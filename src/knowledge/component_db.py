"""
Hardware Component Database Manager
Manages the component specification database with search and retrieval capabilities
"""
import json
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

from .component_models import ComponentSpecification, ComponentCategory
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ComponentDatabase:
    """Manages hardware component specifications database"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join("src", "data", "components")
        self.components: Dict[str, ComponentSpecification] = {}
        self.category_index: Dict[ComponentCategory, List[str]] = {}
        self.manufacturer_index: Dict[str, List[str]] = {}
        self.keyword_index: Dict[str, List[str]] = {}
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the component database from JSON files"""
        try:
            self._load_components_from_files()
            self._build_indexes()
            logger.info(f"Loaded {len(self.components)} components from database")
        except Exception as e:
            logger.error(f"Failed to initialize component database: {e}")
            self._create_sample_data()
    
    def _load_components_from_files(self):
        """Load components from JSON files in data directory"""
        data_path = Path(self.data_path)
        if not data_path.exists():
            logger.warning(f"Component data path {data_path} does not exist")
            return
        
        for json_file in data_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    components_data = json.load(f)
                
                for comp_data in components_data.get('components', []):
                    component = ComponentSpecification(**comp_data)
                    self.components[component.component_id] = component
                    
            except Exception as e:
                logger.error(f"Error loading components from {json_file}: {e}")
    
    def _build_indexes(self):
        """Build search indexes for efficient retrieval"""
        self.category_index.clear()
        self.manufacturer_index.clear()
        self.keyword_index.clear()
        
        for comp_id, component in self.components.items():
            # Category index
            if component.category not in self.category_index:
                self.category_index[component.category] = []
            self.category_index[component.category].append(comp_id)
            
            # Manufacturer index
            if component.manufacturer not in self.manufacturer_index:
                self.manufacturer_index[component.manufacturer] = []
            self.manufacturer_index[component.manufacturer].append(comp_id)
            
            # Keyword index
            all_keywords = component.keywords + [component.name.lower(), component.part_number.lower()]
            if component.subcategory:
                all_keywords.append(component.subcategory.lower())
            
            for keyword in all_keywords:
                keyword = keyword.lower().strip()
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                if comp_id not in self.keyword_index[keyword]:
                    self.keyword_index[keyword].append(comp_id)
    
    def _create_sample_data(self):
        """Create sample component data for testing"""
        sample_components = self._get_sample_components()
        for component in sample_components:
            self.components[component.component_id] = component
        self._build_indexes()
        logger.info(f"Created {len(sample_components)} sample components")
    
    def _get_sample_components(self) -> List[ComponentSpecification]:
        """Generate sample component data"""
        from .component_models import (
            ElectricalSpecification, ThermalSpecification, 
            PackageInfo, PricingInfo, ComplianceStandard
        )
        
        return [
            # STM32F103 Microcontroller
            ComponentSpecification(
                component_id="MCU_STM32F103C8T6",
                name="STM32F103C8T6",
                manufacturer="STMicroelectronics",
                part_number="STM32F103C8T6",
                category=ComponentCategory.MICROCONTROLLER,
                subcategory="ARM Cortex-M3",
                electrical_specs=ElectricalSpecification(
                    operating_voltage_min=2.0,
                    operating_voltage_max=3.6,
                    supply_current_typical=36.0,
                    supply_current_max=50.0
                ),
                thermal_specs=ThermalSpecification(
                    operating_temp_min=-40.0,
                    operating_temp_max=85.0,
                    storage_temp_min=-65.0,
                    storage_temp_max=150.0
                ),
                package_info=PackageInfo(
                    package_type="LQFP",
                    pin_count=48,
                    package_size="7x7",
                    pitch=0.5
                ),
                compliance_standards=[ComplianceStandard.ROHS, ComplianceStandard.REACH],
                pricing=PricingInfo(
                    price_1k=2.50,
                    price_10k=1.80,
                    price_100k=1.25,
                    lead_time_weeks=12
                ),
                description="32-bit ARM Cortex-M3 microcontroller with 64KB Flash, 20KB RAM",
                key_features=[
                    "ARM Cortex-M3 core",
                    "64KB Flash memory",
                    "20KB SRAM",
                    "2x12-bit ADC",
                    "7 timers",
                    "9 communication interfaces"
                ],
                applications=[
                    "Industrial automation",
                    "Consumer electronics",
                    "Motor control",
                    "IoT devices"
                ],
                keywords=["stm32", "cortex-m3", "microcontroller", "32-bit", "arm"]
            ),
            
            # LM317 Voltage Regulator
            ComponentSpecification(
                component_id="REG_LM317T",
                name="LM317T",
                manufacturer="Texas Instruments",
                part_number="LM317T",
                category=ComponentCategory.POWER_MANAGEMENT,
                subcategory="Linear Voltage Regulator",
                electrical_specs=ElectricalSpecification(
                    operating_voltage_min=3.0,
                    operating_voltage_max=40.0,
                    output_current_max=1500.0,
                    line_regulation=0.01,
                    load_regulation=0.1,
                    efficiency_typical=65.0
                ),
                thermal_specs=ThermalSpecification(
                    operating_temp_min=-55.0,
                    operating_temp_max=150.0,
                    thermal_resistance_jc=5.0,
                    power_dissipation_max=20.0
                ),
                package_info=PackageInfo(
                    package_type="TO-220",
                    pin_count=3,
                    package_size="10.16x4.57",
                    height_max=4.7
                ),
                compliance_standards=[ComplianceStandard.ROHS],
                pricing=PricingInfo(
                    price_1k=0.85,
                    price_10k=0.65,
                    price_100k=0.45,
                    lead_time_weeks=8
                ),
                description="Adjustable 3-Terminal Positive Voltage Regulator",
                key_features=[
                    "Adjustable output voltage 1.25V to 37V",
                    "1.5A output current capability",
                    "Internal thermal overload protection",
                    "Internal short circuit current limiting"
                ],
                applications=[
                    "Power supplies",
                    "Battery chargers",
                    "Voltage references",
                    "Current regulators"
                ],
                keywords=["lm317", "voltage regulator", "adjustable", "linear", "power"]
            ),
            
            # Buck Converter Controller (Automotive Grade)
            ComponentSpecification(
                component_id="CTRL_TPS54560_AEC",
                name="TPS54560-Q1",
                manufacturer="Texas Instruments",
                part_number="TPS54560DDAR",
                category=ComponentCategory.POWER_MANAGEMENT,
                subcategory="Buck Controller",
                electrical_specs=ElectricalSpecification(
                    operating_voltage_min=4.5,
                    operating_voltage_max=60.0,
                    supply_current_typical=1.8,
                    output_current_max=5000.0,
                    efficiency_typical=95.0
                ),
                thermal_specs=ThermalSpecification(
                    operating_temp_min=-40.0,
                    operating_temp_max=125.0,
                    thermal_resistance_ja=26.0,
                    power_dissipation_max=2.4
                ),
                package_info=PackageInfo(
                    package_type="HSOP",
                    pin_count=8,
                    package_size="3.9x4.9",
                    pitch=1.27
                ),
                compliance_standards=[
                    ComplianceStandard.AEC_Q100,
                    ComplianceStandard.ROHS,
                    ComplianceStandard.REACH
                ],
                automotive_grade="1",  # AEC-Q100 Grade 1
                pricing=PricingInfo(
                    price_1k=3.25,
                    price_10k=2.85,
                    price_100k=2.15,
                    lead_time_weeks=16
                ),
                description="60V, 5A Synchronous Step-Down SWIFT Converter",
                key_features=[
                    "4.5V to 60V input voltage range",
                    "5A continuous output current",
                    "Integrated high-side and low-side MOSFETs",
                    "Automotive qualified AEC-Q100"
                ],
                applications=[
                    "Automotive ECUs",
                    "Industrial automation",
                    "Telecom infrastructure",
                    "Point-of-load conversion"
                ],
                keywords=["buck converter", "automotive", "aec-q100", "switching", "60v"]
            )
        ]
    
    def get_component(self, component_id: str) -> Optional[ComponentSpecification]:
        """Get component by ID"""
        return self.components.get(component_id)
    
    def search_by_category(self, category: ComponentCategory) -> List[ComponentSpecification]:
        """Search components by category"""
        component_ids = self.category_index.get(category, [])
        return [self.components[comp_id] for comp_id in component_ids]
    
    def search_by_manufacturer(self, manufacturer: str) -> List[ComponentSpecification]:
        """Search components by manufacturer"""
        component_ids = self.manufacturer_index.get(manufacturer, [])
        return [self.components[comp_id] for comp_id in component_ids]
    
    def search_by_keywords(self, keywords: List[str]) -> List[ComponentSpecification]:
        """Search components by keywords"""
        matching_ids = set()
        
        for keyword in keywords:
            keyword = keyword.lower().strip()
            if keyword in self.keyword_index:
                if not matching_ids:
                    matching_ids = set(self.keyword_index[keyword])
                else:
                    matching_ids &= set(self.keyword_index[keyword])
        
        return [self.components[comp_id] for comp_id in matching_ids]
    
    def filter_components(self, 
                         category: Optional[ComponentCategory] = None,
                         manufacturer: Optional[str] = None,
                         voltage_min: Optional[float] = None,
                         voltage_max: Optional[float] = None,
                         temp_min: Optional[float] = None,
                         temp_max: Optional[float] = None,
                         compliance: Optional[List[str]] = None) -> List[ComponentSpecification]:
        """Filter components by multiple criteria"""
        results = list(self.components.values())
        
        if category:
            results = [c for c in results if c.category == category]
        
        if manufacturer:
            results = [c for c in results if c.manufacturer.lower() == manufacturer.lower()]
        
        if voltage_min is not None:
            results = [c for c in results if c.electrical_specs.operating_voltage_min >= voltage_min]
        
        if voltage_max is not None:
            results = [c for c in results if c.electrical_specs.operating_voltage_max <= voltage_max]
        
        if temp_min is not None:
            results = [c for c in results if c.thermal_specs.operating_temp_min >= temp_min]
        
        if temp_max is not None:
            results = [c for c in results if c.thermal_specs.operating_temp_max <= temp_max]
        
        if compliance:
            results = [c for c in results if any(std.value in compliance for std in c.compliance_standards)]
        
        return results
    
    def get_all_components(self) -> List[ComponentSpecification]:
        """Get all components"""
        return list(self.components.values())
    
    def get_component_count(self) -> int:
        """Get total component count"""
        return len(self.components)
    
    def get_categories(self) -> List[ComponentCategory]:
        """Get all available categories"""
        return list(self.category_index.keys())
    
    def get_manufacturers(self) -> List[str]:
        """Get all available manufacturers"""
        return list(self.manufacturer_index.keys())
