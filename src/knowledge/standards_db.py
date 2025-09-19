"""
Hardware Standards Database
Manages compliance standards and certification requirements
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field
import logging

# Import ComplianceStandard enum from component_models
# from .component_models import ComplianceStandard

logger = logging.getLogger(__name__)

class StandardRequirement(BaseModel):
    """Individual standard requirement"""
    requirement_id: str
    title: str
    description: str
    test_conditions: Optional[str] = None
    acceptance_criteria: str
    applicable_components: List[str] = Field(default_factory=list)

class ComplianceStandardDoc(BaseModel):
    """Complete compliance standard definition"""
    standard_id: str
    name: str
    organization: str
    version: str
    description: str
    scope: str
    applicable_domains: List[str] = Field(default_factory=list)
    requirements: List[StandardRequirement] = Field(default_factory=list)
    test_methods: List[str] = Field(default_factory=list)
    certification_process: Optional[str] = None
    validity_period: Optional[str] = None

class StandardsDatabase:
    """Manages hardware compliance standards database"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join("src", "data", "standards")
        self.standards: Dict[str, ComplianceStandardDoc] = {}  # Fixed: Use ComplianceStandardDoc
        self.domain_index: Dict[str, List[str]] = {}
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize standards database"""
        try:
            self._load_standards_from_files()
            self._build_indexes()
            logger.info(f"Loaded {len(self.standards)} compliance standards")
        except Exception as e:
            logger.error(f"Failed to initialize standards database: {e}")
            self._create_sample_standards()
    
    def _load_standards_from_files(self):
        """Load standards from JSON files"""
        data_path = Path(self.data_path)
        if not data_path.exists():
            logger.warning(f"Standards data path {data_path} does not exist")
            return
        
        for json_file in data_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    standards_data = json.load(f)
                
                # Fixed: Use ComplianceStandardDoc instead of ComplianceStandard
                standard = ComplianceStandardDoc(**standards_data)
                self.standards[standard.standard_id] = standard
                    
            except Exception as e:
                logger.error(f"Error loading standard from {json_file}: {e}")
    
    def _build_indexes(self):
        """Build search indexes"""
        self.domain_index.clear()
        
        for std_id, standard in self.standards.items():
            for domain in standard.applicable_domains:
                if domain not in self.domain_index:
                    self.domain_index[domain] = []
                self.domain_index[domain].append(std_id)
    
    def _create_sample_standards(self):
        """Create sample standards data"""
        sample_standards = [
            # AEC-Q100 Standard - Fixed: Use ComplianceStandardDoc
            ComplianceStandardDoc(
                standard_id="AEC_Q100",
                name="AEC-Q100",
                organization="Automotive Electronics Council",
                version="Rev-H",
                description="Failure Mechanism Based Stress Test Qualification for Integrated Circuits",
                scope="Automotive integrated circuits qualification",
                applicable_domains=["automotive", "power_electronics", "analog_ic"],
                requirements=[
                    StandardRequirement(
                        requirement_id="AEC_Q100_001",
                        title="Temperature Cycling",
                        description="Components must survive temperature cycling stress test",
                        test_conditions="1000 cycles, -40°C to +150°C for Grade 0",
                        acceptance_criteria="Zero failures allowed"
                    ),
                    StandardRequirement(
                        requirement_id="AEC_Q100_002", 
                        title="High Temperature Operating Life",
                        description="Extended operation at maximum temperature",
                        test_conditions="1000 hours at maximum operating temperature",
                        acceptance_criteria="Parametric drift within specification limits"
                    ),
                    StandardRequirement(
                        requirement_id="AEC_Q100_003",
                        title="Humidity Resistance",
                        description="Resistance to humidity and temperature stress",
                        test_conditions="1000 hours at 85°C/85%RH",
                        acceptance_criteria="No corrosion or parameter degradation"
                    )
                ],
                test_methods=[
                    "JESD22-A104 (Temperature Cycling)",
                    "JESD22-A108 (Temperature, Humidity, Bias Life)",
                    "JESD22-A113 (Preconditioning)"
                ],
                certification_process="Third-party qualification laboratory testing required"
            ),
            
            # ISO 26262 Standard - Fixed: Use ComplianceStandardDoc
            ComplianceStandardDoc(
                standard_id="ISO_26262",
                name="ISO 26262",
                organization="International Organization for Standardization",
                version="2018",
                description="Road Vehicles - Functional Safety",
                scope="Functional safety for automotive electronic systems",
                applicable_domains=["automotive", "safety_systems"],
                requirements=[
                    StandardRequirement(
                        requirement_id="ISO_26262_ASIL_A",
                        title="ASIL A Requirements",
                        description="Automotive Safety Integrity Level A requirements",
                        acceptance_criteria="Single point fault metric ≥ 90%"
                    ),
                    StandardRequirement(
                        requirement_id="ISO_26262_ASIL_B",
                        title="ASIL B Requirements", 
                        description="Automotive Safety Integrity Level B requirements",
                        acceptance_criteria="Single point fault metric ≥ 90%, Latent fault metric ≥ 60%"
                    ),
                    StandardRequirement(
                        requirement_id="ISO_26262_ASIL_C",
                        title="ASIL C Requirements",
                        description="Automotive Safety Integrity Level C requirements", 
                        acceptance_criteria="Single point fault metric ≥ 99%, Latent fault metric ≥ 80%"
                    ),
                    StandardRequirement(
                        requirement_id="ISO_26262_ASIL_D",
                        title="ASIL D Requirements",
                        description="Automotive Safety Integrity Level D requirements",
                        acceptance_criteria="Single point fault metric ≥ 99%, Latent fault metric ≥ 90%"
                    )
                ],
                test_methods=[
                    "Hazard Analysis and Risk Assessment (HARA)",
                    "Fault Tree Analysis (FTA)",
                    "Failure Mode and Effects Analysis (FMEA)"
                ]
            ),
            
            # IEC 60601 Standard - Fixed: Use ComplianceStandardDoc
            ComplianceStandardDoc(
                standard_id="IEC_60601",
                name="IEC 60601-1",
                organization="International Electrotechnical Commission",
                version="3.1",
                description="Medical Electrical Equipment - General Requirements for Basic Safety and Essential Performance",
                scope="Medical electrical equipment safety requirements",
                applicable_domains=["medical", "power_electronics"],
                requirements=[
                    StandardRequirement(
                        requirement_id="IEC_60601_001",
                        title="Patient Applied Parts Isolation",
                        description="Electrical isolation requirements for patient contact",
                        test_conditions="4000VAC test voltage for Type BF applied parts",
                        acceptance_criteria="No breakdown or flashover"
                    ),
                    StandardRequirement(
                        requirement_id="IEC_60601_002",
                        title="Leakage Current Limits",
                        description="Maximum allowable leakage current limits",
                        acceptance_criteria="Patient leakage current ≤ 10μA normal, ≤ 50μA fault condition"
                    ),
                    StandardRequirement(
                        requirement_id="IEC_60601_003",
                        title="EMC Requirements",
                        description="Electromagnetic compatibility for medical devices",
                        test_conditions="IEC 60601-1-2 EMC standard compliance",
                        acceptance_criteria="Essential performance maintained during EMC testing"
                    )
                ],
                test_methods=[
                    "Dielectric strength testing",
                    "Leakage current measurement", 
                    "EMC testing per IEC 60601-1-2"
                ]
            )
        ]
        
        for standard in sample_standards:
            self.standards[standard.standard_id] = standard
        
        self._build_indexes()
        logger.info(f"Created {len(sample_standards)} sample standards")
    
    def get_standard(self, standard_id: str) -> Optional[ComplianceStandardDoc]:
        """Get standard by ID"""
        return self.standards.get(standard_id)
    
    def get_standards_by_domain(self, domain: str) -> List[ComplianceStandardDoc]:
        """Get standards applicable to domain"""
        standard_ids = self.domain_index.get(domain, [])
        return [self.standards[std_id] for std_id in standard_ids]
    
    def search_requirements(self, query: str) -> List[StandardRequirement]:
        """Search for requirements containing query text"""
        results = []
        query_lower = query.lower()
        
        for standard in self.standards.values():
            for requirement in standard.requirements:
                if (query_lower in requirement.title.lower() or 
                    query_lower in requirement.description.lower()):
                    results.append(requirement)
        
        return results
    
    def get_all_standards(self) -> List[ComplianceStandardDoc]:
        """Get all standards"""
        return list(self.standards.values())
