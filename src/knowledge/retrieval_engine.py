"""
Retrieval Engine for Hardware AI Orchestrator
Orchestrates knowledge retrieval from multiple sources for RAG enhancement
"""
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import re

# ChromaDB imports
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    VECTOR_DEPS_AVAILABLE = True
except ImportError:
    VECTOR_DEPS_AVAILABLE = False

from .component_db import ComponentDatabase
from .standards_db import StandardsDatabase
from .component_models import ComponentSpecification, ComponentCategory
from ..config.domain_definitions import HARDWARE_DOMAINS

logger = logging.getLogger(__name__)

@dataclass
class RetrievalContext:
    """Context information for knowledge retrieval"""
    query: str
    primary_intent: str
    primary_domain: str
    complexity_score: float
    user_expertise: str = "intermediate"
    project_constraints: Optional[Dict[str, Any]] = None

@dataclass
class KnowledgeResult:
    """Consolidated knowledge retrieval result"""
    components: List[Dict[str, Any]]
    standards: List[Dict[str, Any]]
    domain_context: Dict[str, Any]
    retrieval_summary: Dict[str, Any]

class HardwareRetrievalEngine:
    """Orchestrates knowledge retrieval for hardware engineering queries"""
    
    def __init__(self):
        # Initialize knowledge sources
        self.component_db = ComponentDatabase()
        self.standards_db = StandardsDatabase()
        
        # Initialize vector store with ChromaDB
        self.vector_store_available = False
        self.chroma_client = None
        self.components_collection = None
        self.standards_collection = None
        
        if VECTOR_DEPS_AVAILABLE:
            try:
                self._initialize_vector_store()
                self.vector_store_available = True
                logger.info("✅ ChromaDB vector store initialized successfully")
            except Exception as e:
                logger.warning(f"❌ ChromaDB initialization failed: {e}")
                self.vector_store_available = False
        else:
            logger.warning("❌ Vector store not available: ChromaDB dependencies not available. Install with: pip install chromadb sentence-transformers")
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB client and collections"""
        # Initialize ChromaDB client
        self.chroma_client = chromadb.Client(Settings(
            persist_directory="./data/chromadb",
            is_persistent=True
        ))
        
        # Get or create collections
        try:
            self.components_collection = self.chroma_client.get_collection("hardware_components")
        except:
            # Collection doesn't exist, create it
            self._create_and_populate_collections()
        
        try:
            self.standards_collection = self.chroma_client.get_collection("compliance_standards")
        except:
            # Collection doesn't exist, will be created in _create_and_populate_collections
            pass
    
    def _create_and_populate_collections(self):
        """Create and populate ChromaDB collections with existing data"""
        if not VECTOR_DEPS_AVAILABLE:
            return
        
        # Initialize embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create components collection
        self.components_collection = self.chroma_client.get_or_create_collection(
            name="hardware_components",
            metadata={"description": "Hardware component specifications"}
        )
        
        # Create standards collection
        self.standards_collection = self.chroma_client.get_or_create_collection(
            name="compliance_standards",
            metadata={"description": "Compliance and safety standards"}
        )
        
        # Populate components
        components = self.component_db.get_all_components()
        if components:
            self._add_components_to_vector_store(components, model)
        
        # Populate standards
        standards = list(self.standards_db.standards.values()) if hasattr(self.standards_db, 'standards') else []
        if standards:
            self._add_standards_to_vector_store(standards, model)
    
    def _add_components_to_vector_store(self, components: List[ComponentSpecification], model):
        """Add components to ChromaDB vector store"""
        documents = []
        metadatas = []
        ids = []
        
        for comp in components:
            # Create searchable text from component data
            doc_text = f"""
            {comp.name} {comp.manufacturer} {comp.part_number}
            {comp.description} Category: {comp.category}
            {' '.join(comp.key_features)} {' '.join(comp.applications)}
            {' '.join(comp.keywords)} Package: {comp.package_info.package_type if comp.package_info else ''}
            """.strip()
            
            documents.append(doc_text)
            metadatas.append({
                'type': 'component',
                'category': comp.category.value if hasattr(comp.category, 'value') else str(comp.category),
                'manufacturer': comp.manufacturer,
                'automotive_qualified': getattr(comp, 'automotive_grade', None) is not None,
                'compliance_standards': [std.value if hasattr(std, 'value') else str(std) for std in comp.compliance_standards]
            })
            ids.append(f"comp_{comp.component_id}")
        
        if documents:
            # Generate embeddings
            embeddings = model.encode(documents).tolist()
            
            # Add to collection
            self.components_collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ Added {len(documents)} components to vector store")
    
    def _add_standards_to_vector_store(self, standards, model):
        """Add standards to ChromaDB vector store"""
        documents = []
        metadatas = []
        ids = []
        
        for std in standards:
            # Create searchable text from standard data
            doc_text = f"""
            {std.name} {std.standard_id} {std.organization}
            {std.description} {std.scope}
            """.strip()
            
            # Add requirements text
            for req in std.requirements:
                doc_text += f" {req.title} {req.description} {req.acceptance_criteria}"
            
            documents.append(doc_text)
            metadatas.append({
                'type': 'standard',
                'standard_id': std.standard_id,
                'organization': std.organization,
            })
            ids.append(f"std_{std.standard_id}")
        
        if documents:
            # Generate embeddings
            embeddings = model.encode(documents).tolist()
            
            # Add to collection
            self.standards_collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ Added {len(documents)} standards to vector store")
    
    def retrieve_knowledge(self, context: RetrievalContext) -> KnowledgeResult:
        """
        Main retrieval method - orchestrates all knowledge sources
        Returns consolidated knowledge relevant to the query
        """
        logger.info(f"🔍 Retrieving knowledge for intent: {context.primary_intent}, domain: {context.primary_domain}")
        
        # Retrieve components
        components = self._retrieve_components(context)
        
        # Retrieve standards and compliance info
        standards = self._retrieve_standards(context)
        
        # Get domain context
        domain_context = self._get_domain_context(context.primary_domain)
        
        # Create retrieval summary
        retrieval_summary = {
            "total_components": len(components),
            "total_standards": len(standards),
            "retrieval_methods": self._get_retrieval_methods_used(context),
            "confidence": self._calculate_retrieval_confidence(components, standards, context)
        }
        
        logger.info(f"📊 Retrieved {len(components)} components and {len(standards)} standards")
        
        return KnowledgeResult(
            components=components,
            standards=standards,
            domain_context=domain_context,
            retrieval_summary=retrieval_summary
        )
    
    def _retrieve_components(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve relevant components using multiple strategies"""
        components = []
        
        # Strategy 1: Semantic search using ChromaDB (if available)
        if self.vector_store_available and self.components_collection:
            semantic_results = self._semantic_component_search(context)
            components.extend(semantic_results)
        
        # Strategy 2: Intent-based retrieval
        intent_results = self._intent_based_component_retrieval(context)
        components.extend(intent_results)
        
        # Strategy 3: Domain-specific retrieval
        domain_results = self._domain_specific_component_retrieval(context)
        components.extend(domain_results)
        
        # Deduplicate and rank
        unique_components = self._deduplicate_components(components)
        ranked_components = self._rank_components(unique_components, context)
        
        return ranked_components[:10]  # Limit to top 10 for performance
    
    def _semantic_component_search(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Perform semantic search using ChromaDB vector store"""
        if not self.components_collection:
            return []
        
        try:
            # Build metadata filters
            where_filter = {}
            if context.primary_domain == "automotive":
                where_filter["automotive_qualified"] = True
            
            # Search components using ChromaDB
            results = self.components_collection.query(
                query_texts=[context.query],
                n_results=8,
                where=where_filter if where_filter else None
            )
            
            # Process results
            enhanced_results = []
            if results['ids'] and results['ids'][0]:  # Check if we got results
                for i, component_id in enumerate(results['ids'][0]):
                    # Extract component ID from stored ID format
                    comp_id = component_id.replace('comp_', '')
                    component = self.component_db.get_component(comp_id)
                    
                    if component:
                        distance = results['distances'][0][i] if results.get('distances') else 0.5
                        similarity_score = 1.0 - distance  # Convert distance to similarity
                        
                        enhanced_results.append({
                            "component": component.dict(),
                            "similarity_score": similarity_score,
                            "retrieval_method": "semantic_search",
                            "relevance_factors": ["semantic_similarity", "domain_match"]
                        })
            
            return enhanced_results
        
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    def _retrieve_standards(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve relevant compliance standards and requirements"""
        standards = []
        
        # Strategy 1: Semantic search using ChromaDB (if available)
        if self.vector_store_available and self.standards_collection:
            semantic_standards = self._semantic_standards_search(context)
            standards.extend(semantic_standards)
        
        # Strategy 2: Domain-based standards
        domain_standards = self._domain_specific_standards_retrieval(context)
        standards.extend(domain_standards)
        
        # Deduplicate standards
        unique_standards = self._deduplicate_standards(standards)
        
        return unique_standards[:5]  # Limit to top 5 standards
    
    def _semantic_standards_search(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Perform semantic search for standards using ChromaDB"""
        if not self.standards_collection:
            return []
        
        try:
            # Search standards using ChromaDB
            results = self.standards_collection.query(
                query_texts=[context.query],
                n_results=5
            )
            
            # Process results
            enhanced_results = []
            if results['ids'] and results['ids'][0]:  # Check if we got results
                for i, standard_id in enumerate(results['ids'][0]):
                    # Extract standard ID from stored ID format
                    std_id = standard_id.replace('std_', '')
                    
                    # Find the standard in standards_db
                    standard = None
                    if hasattr(self.standards_db, 'standards'):
                        standard = self.standards_db.standards.get(std_id)
                    
                    if standard:
                        distance = results['distances'][0][i] if results.get('distances') else 0.5
                        similarity_score = 1.0 - distance
                        
                        enhanced_results.append({
                            "standard": standard.dict(),
                            "similarity_score": similarity_score,
                            "retrieval_method": "semantic_search",
                            "relevance_factors": ["semantic_similarity"]
                        })
            
            return enhanced_results
        
        except Exception as e:
            logger.error(f"❌ Standards semantic search failed: {e}")
            return []
    
    def _domain_specific_standards_retrieval(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve standards specific to the domain"""
        standards = []
        
        # Get domain-specific standards
        if context.primary_domain == "automotive":
            # Look for AEC-Q100 and ISO 26262
            automotive_standards = ["AEC-Q100", "ISO-26262"]
            for std_id in automotive_standards:
                if hasattr(self.standards_db, 'standards'):
                    standard = self.standards_db.standards.get(std_id)
                    if standard:
                        standards.append({
                            "standard": standard.dict(),
                            "similarity_score": 0.9,
                            "retrieval_method": "domain_specific",
                            "relevance_factors": ["automotive_domain"]
                        })
        
        elif context.primary_domain == "medical":
            # Look for IEC 60601
            medical_standards = ["IEC-60601"]
            for std_id in medical_standards:
                if hasattr(self.standards_db, 'standards'):
                    standard = self.standards_db.standards.get(std_id)
                    if standard:
                        standards.append({
                            "standard": standard.dict(),
                            "similarity_score": 0.9,
                            "retrieval_method": "domain_specific",
                            "relevance_factors": ["medical_domain"]
                        })
        
        return standards
    
    def _intent_based_component_retrieval(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve components based on query intent"""
        results = []
        
        if context.primary_intent == "component_selection":
            # For component selection, focus on popular/recommended components
            categories = self._get_relevant_categories_for_query(context.query)
            for category in categories:
                components = self.component_db.search_by_category(category)
                for comp in components[:3]:  # Top 3 per category
                    results.append({
                        "component": comp.dict(),
                        "similarity_score": 0.7,  # Default score for intent-based
                        "retrieval_method": "intent_based",
                        "relevance_factors": ["category_match", "intent_alignment"]
                    })
        
        elif context.primary_intent == "compliance_checking":
            # Focus on components with relevant compliance standards
            compliance_filters = self._extract_compliance_requirements(context.query)
            if compliance_filters:
                filtered_components = self.component_db.filter_components(
                    compliance=compliance_filters
                )
                for comp in filtered_components[:5]:
                    results.append({
                        "component": comp.dict(),
                        "similarity_score": 0.8,
                        "retrieval_method": "compliance_based",
                        "relevance_factors": ["compliance_match", "standards_alignment"]
                    })
        
        return results
    
    def _domain_specific_component_retrieval(self, context: RetrievalContext) -> List[Dict[str, Any]]:
        """Retrieve components specific to hardware domain"""
        results = []
        
        if context.primary_domain == "automotive":
            # Focus on AEC-Q100 qualified components
            automotive_components = self.component_db.filter_components(
                compliance=["AEC-Q100"]
            )
            for comp in automotive_components[:4]:
                results.append({
                    "component": comp.dict(),
                    "similarity_score": 0.75,
                    "retrieval_method": "domain_specific",
                    "relevance_factors": ["automotive_qualified", "domain_expertise"]
                })
        
        elif context.primary_domain == "medical":
            # Focus on medical-grade components
            medical_components = self.component_db.filter_components(
                compliance=["IEC-60601"]
            )
            for comp in medical_components[:4]:
                results.append({
                    "component": comp.dict(),
                    "similarity_score": 0.75,
                    "retrieval_method": "domain_specific",
                    "relevance_factors": ["medical_qualified", "safety_compliance"]
                })
        
        return results
    
    def _get_relevant_categories_for_query(self, query: str) -> List[ComponentCategory]:
        """Determine relevant component categories from query"""
        query_lower = query.lower()
        categories = []
        
        category_keywords = {
            ComponentCategory.MICROCONTROLLER: ["microcontroller", "mcu", "processor", "cortex", "arm"],
            ComponentCategory.POWER_MANAGEMENT: ["power", "voltage", "regulator", "buck", "boost", "ldo"],
            ComponentCategory.SENSORS: ["sensor", "temperature", "pressure", "accelerometer"],
            ComponentCategory.ANALOG_IC: ["op-amp", "amplifier", "comparator", "reference"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                categories.append(category)
        
        return categories or [ComponentCategory.MICROCONTROLLER]  # Default fallback
    
    def _extract_compliance_requirements(self, query: str) -> List[str]:
        """Extract compliance requirements from query"""
        query_lower = query.lower()
        compliance = []
        
        if "aec-q100" in query_lower or "automotive" in query_lower:
            compliance.append("AEC-Q100")
        if "iso 26262" in query_lower or "functional safety" in query_lower:
            compliance.append("ISO-26262") 
        if "iec 60601" in query_lower or "medical" in query_lower:
            compliance.append("IEC-60601")
        
        return compliance
    
    def _deduplicate_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate components based on component_id"""
        seen_ids = set()
        unique_components = []
        
        for comp_data in components:
            comp_id = comp_data["component"]["component_id"]
            if comp_id not in seen_ids:
                seen_ids.add(comp_id)
                unique_components.append(comp_data)
        
        return unique_components
    
    def _deduplicate_standards(self, standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate standards based on standard_id"""
        seen_ids = set()
        unique_standards = []
        
        for std_data in standards:
            std_id = std_data["standard"]["standard_id"]
            if std_id not in seen_ids:
                seen_ids.add(std_id)
                unique_standards.append(std_data)
        
        return unique_standards
    
    def _rank_components(self, components: List[Dict[str, Any]], context: RetrievalContext) -> List[Dict[str, Any]]:
        """Rank components based on relevance to query context"""
        def ranking_key(comp_data):
            base_score = comp_data.get("similarity_score", 0.5)
            
            # Boost based on retrieval method
            method_boost = {
                "semantic_search": 0.1,
                "compliance_based": 0.08,
                "domain_specific": 0.06,
                "intent_based": 0.04
            }
            boost = method_boost.get(comp_data.get("retrieval_method", ""), 0.0)
            
            # Boost for domain alignment
            if context.primary_domain == "automotive" and "automotive" in str(comp_data.get("relevance_factors", [])):
                boost += 0.05
            
            return base_score + boost
        
        return sorted(components, key=ranking_key, reverse=True)
    
    def _get_domain_context(self, domain: str) -> Dict[str, Any]:
        """Get contextual information about the hardware domain"""
        domain_info = HARDWARE_DOMAINS.get(domain, {})
        
        return {
            "domain": domain,
            "scope": domain_info.get("scope", []),
            "expertise_areas": domain_info.get("expertise_areas", []),
            "complexity_weight": domain_info.get("complexity_weight", 1.0),
            "typical_components": self._get_typical_components_for_domain(domain),
            "key_considerations": self._get_domain_considerations(domain)
        }
    
    def _get_typical_components_for_domain(self, domain: str) -> List[str]:
        """Get typical component types for a domain"""
        domain_components = {
            "automotive": ["Buck controllers", "CAN transceivers", "Automotive MCUs", "Power MOSFETs"],
            "medical": ["Medical-grade power supplies", "Isolation amplifiers", "Low-leakage regulators"],
            "power_electronics": ["Switching controllers", "Power MOSFETs", "Gate drivers", "Current sensors"],
            "analog_rf": ["Op-amps", "Filters", "VCOs", "Mixers"],
            "digital_design": ["Microcontrollers", "FPGAs", "Logic gates", "Clock generators"]
        }
        return domain_components.get(domain, ["General purpose components"])
    
    def _get_domain_considerations(self, domain: str) -> List[str]:
        """Get key engineering considerations for a domain"""
        considerations = {
            "automotive": ["Temperature cycling", "Vibration resistance", "EMC compliance", "Long-term reliability"],
            "medical": ["Patient safety", "Leakage current limits", "Biocompatibility", "Sterilization compatibility"],
            "power_electronics": ["Efficiency optimization", "Thermal management", "EMI suppression", "Transient response"],
            "analog_rf": ["Noise performance", "Frequency response", "Distortion", "Matching requirements"]
        }
        return considerations.get(domain, ["General reliability", "Cost optimization", "Availability"])
    
    def _get_retrieval_methods_used(self, context: RetrievalContext) -> List[str]:
        """Get list of retrieval methods used for this query"""
        methods = ["intent_based", "domain_specific"]
        if self.vector_store_available:
            methods.append("semantic_search")
        if context.primary_intent == "compliance_checking":
            methods.append("compliance_based")
        return methods
    
    def _calculate_retrieval_confidence(self, components: List[Dict], standards: List[Dict], context: RetrievalContext) -> float:
        """Calculate confidence in retrieval results"""
        base_confidence = 0.6
        
        # Boost for having relevant components
        if components:
            component_boost = min(len(components) * 0.05, 0.3)
            base_confidence += component_boost
        
        # Boost for having relevant standards
        if standards:
            standards_boost = min(len(standards) * 0.08, 0.2)
            base_confidence += standards_boost
        
        # Boost for vector search availability
        if self.vector_store_available:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
