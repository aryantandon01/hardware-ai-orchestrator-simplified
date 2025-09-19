"""
Vector Store Manager for hardware knowledge base
Handles semantic search and embedding storage using ChromaDB
"""
import os
import logging
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    SentenceTransformer = None

from .component_models import ComponentSpecification
from .component_db import ComponentDatabase
from .standards_db import StandardsDatabase

logger = logging.getLogger(__name__)

class HardwareVectorStore:
    """Manages vector storage and semantic search for hardware knowledge"""
    
    def __init__(self, persist_directory: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2"):
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB dependencies not available. Install with: "
                "pip install chromadb sentence-transformers"
            )
        
        self.persist_directory = persist_directory or "./data/chromadb"
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize ChromaDB client
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Initialize collections
        self.components_collection = self._get_or_create_collection("hardware_components")
        self.standards_collection = self._get_or_create_collection("compliance_standards")
        
        logger.info(f"Vector store initialized with model {model_name}")
        logger.info(f"Embedding dimension: {self.embedding_dimension}")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            collection = self.client.get_collection(name=name)
            logger.info(f"Loaded existing collection '{name}' with {collection.count()} items")
        except ValueError:
            collection = self.client.create_collection(name=name)
            logger.info(f"Created new collection '{name}'")
        return collection
    
    def add_component(self, component: ComponentSpecification) -> None:
        """Add a single component to the vector store"""
        # Create searchable text representation
        searchable_text = self._component_to_searchable_text(component)
        
        # Generate embedding
        embedding = self.embedding_model.encode([searchable_text])[0].tolist()
        
        # Prepare metadata
        metadata = {
            "component_id": component.component_id,
            "name": component.name,
            "manufacturer": component.manufacturer,
            "category": component.category.value,
            "subcategory": component.subcategory or "",
            "voltage_min": component.electrical_specs.operating_voltage_min,
            "voltage_max": component.electrical_specs.operating_voltage_max,
            "temp_min": component.thermal_specs.operating_temp_min,
            "temp_max": component.thermal_specs.operating_temp_max,
            "compliance_standards": ",".join([std.value for std in component.compliance_standards]),
            "automotive_grade": component.automotive_grade or "",
            "price_1k": component.pricing.price_1k if component.pricing else None,
            "package_type": component.package_info.package_type,
            "applications": ",".join(component.applications[:3])  # Limit for metadata
        }
        
        # Add to collection
        self.components_collection.add(
            ids=[component.component_id],
            embeddings=[embedding],
            documents=[searchable_text],
            metadatas=[metadata]
        )
    
    def add_components_batch(self, components: List[ComponentSpecification]) -> None:
        """Add multiple components to vector store efficiently"""
        if not components:
            return
        
        searchable_texts = [self._component_to_searchable_text(comp) for comp in components]
        embeddings = self.embedding_model.encode(searchable_texts).tolist()
        
        ids = [comp.component_id for comp in components]
        metadatas = [self._component_to_metadata(comp) for comp in components]
        
        self.components_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=searchable_texts,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(components)} components to vector store")
    
    def _component_to_searchable_text(self, component: ComponentSpecification) -> str:
        """Convert component to searchable text representation"""
        parts = [
            f"Component: {component.name}",
            f"Manufacturer: {component.manufacturer}",
            f"Category: {component.category.value}",
        ]
        
        if component.subcategory:
            parts.append(f"Subcategory: {component.subcategory}")
        
        if component.description:
            parts.append(f"Description: {component.description}")
        
        # Electrical specifications
        elec = component.electrical_specs
        parts.append(f"Operating voltage: {elec.operating_voltage_min}V to {elec.operating_voltage_max}V")
        
        if elec.supply_current_typical:
            parts.append(f"Current consumption: {elec.supply_current_typical}mA")
        
        # Thermal specifications
        thermal = component.thermal_specs
        parts.append(f"Temperature range: {thermal.operating_temp_min}°C to {thermal.operating_temp_max}°C")
        
        # Features and applications
        if component.key_features:
            parts.append(f"Features: {', '.join(component.key_features[:5])}")
        
        if component.applications:
            parts.append(f"Applications: {', '.join(component.applications[:5])}")
        
        # Compliance
        if component.compliance_standards:
            standards = [std.value for std in component.compliance_standards]
            parts.append(f"Compliance: {', '.join(standards)}")
        
        # Keywords
        if component.keywords:
            parts.append(f"Keywords: {', '.join(component.keywords[:10])}")
        
        return " | ".join(parts)
    
    def _component_to_metadata(self, component: ComponentSpecification) -> Dict[str, Any]:
        """Convert component to metadata dictionary"""
        return {
            "component_id": component.component_id,
            "name": component.name,
            "manufacturer": component.manufacturer,
            "category": component.category.value,
            "subcategory": component.subcategory or "",
            "voltage_min": component.electrical_specs.operating_voltage_min,
            "voltage_max": component.electrical_specs.operating_voltage_max,
            "temp_min": component.thermal_specs.operating_temp_min,
            "temp_max": component.thermal_specs.operating_temp_max,
            "compliance": ",".join([std.value for std in component.compliance_standards]),
            "automotive_grade": component.automotive_grade or "",
            "package_type": component.package_info.package_type,
            "price_1k": component.pricing.price_1k if component.pricing else 0.0
        }
    
    def search_components(self, 
                         query: str, 
                         n_results: int = 5,
                         filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for components using semantic similarity"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Prepare where clause for filtering
        where_clause = {}
        if filters:
            if "category" in filters:
                where_clause["category"] = filters["category"]
            if "manufacturer" in filters:
                where_clause["manufacturer"] = filters["manufacturer"]
            if "automotive_grade" in filters and filters["automotive_grade"]:
                where_clause["automotive_grade"] = {"$ne": ""}
        
        # Query ChromaDB
        results = self.components_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:  # Check if results exist
            for i, component_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "component_id": component_id,
                    "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": results["metadatas"][0][i],
                    "searchable_text": results["documents"][0][i]
                })
        
        return formatted_results
    
    def search_with_constraints(self,
                               query: str,
                               voltage_range: Optional[Tuple[float, float]] = None,
                               temp_range: Optional[Tuple[float, float]] = None,
                               compliance_required: Optional[List[str]] = None,
                               n_results: int = 5) -> List[Dict[str, Any]]:
        """Search with hardware-specific constraints"""
        # Get initial semantic search results (broader search)
        initial_results = self.search_components(query, n_results=n_results*2)
        
        # Apply additional filtering
        filtered_results = []
        for result in initial_results:
            metadata = result["metadata"]
            
            # Voltage range check
            if voltage_range:
                min_volt, max_volt = voltage_range
                if not (metadata["voltage_min"] >= min_volt and metadata["voltage_max"] <= max_volt):
                    continue
            
            # Temperature range check
            if temp_range:
                min_temp, max_temp = temp_range
                if not (metadata["temp_min"] >= min_temp and metadata["temp_max"] <= max_temp):
                    continue
            
            # Compliance check
            if compliance_required:
                component_compliance = metadata.get("compliance", "").split(",")
                if not any(req in component_compliance for req in compliance_required):
                    continue
            
            filtered_results.append(result)
            
            if len(filtered_results) >= n_results:
                break
        
        return filtered_results
    
    def get_similar_components(self, component_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find components similar to a given component"""
        # Get the component's document
        try:
            component_data = self.components_collection.get(ids=[component_id])
            if not component_data["documents"]:
                return []
            
            # Use the component's document as query
            component_text = component_data["documents"][0]
            return self.search_components(component_text, n_results=n_results+1)[1:]  # Exclude self
            
        except Exception as e:
            logger.error(f"Error finding similar components: {e}")
            return []
    
    def populate_from_database(self, component_db: ComponentDatabase) -> None:
        """Populate vector store from component database"""
        components = component_db.get_all_components()
        if components:
            self.add_components_batch(components)
            logger.info(f"Populated vector store with {len(components)} components from database")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collections"""
        return {
            "components_count": self.components_collection.count(),
            "standards_count": self.standards_collection.count(),
            "embedding_model": self.model_name,
            "embedding_dimension": self.embedding_dimension
        }
