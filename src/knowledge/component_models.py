"""
Pydantic models for hardware component specifications
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ComponentCategory(str, Enum):
    """Hardware component categories"""
    MICROCONTROLLER = "microcontroller"
    POWER_MANAGEMENT = "power_management"
    SENSORS = "sensors"
    ANALOG_IC = "analog_ic"
    PASSIVE_COMPONENTS = "passive_components"
    CONNECTORS = "connectors"
    MEMORY = "memory"
    COMMUNICATION = "communication"

class ComplianceStandard(str, Enum):
    """Industry compliance standards"""
    AEC_Q100 = "AEC-Q100"
    ISO_26262 = "ISO 26262"
    IEC_60601 = "IEC 60601"
    ROHS = "RoHS"
    REACH = "REACH"
    FCC = "FCC"
    CE = "CE"

class ThermalSpecification(BaseModel):
    """Thermal characteristics of components"""
    operating_temp_min: float = Field(..., description="Minimum operating temperature (°C)")
    operating_temp_max: float = Field(..., description="Maximum operating temperature (°C)")
    storage_temp_min: Optional[float] = Field(None, description="Minimum storage temperature (°C)")
    storage_temp_max: Optional[float] = Field(None, description="Maximum storage temperature (°C)")
    thermal_resistance_ja: Optional[float] = Field(None, description="Thermal resistance junction-to-ambient (°C/W)")
    thermal_resistance_jc: Optional[float] = Field(None, description="Thermal resistance junction-to-case (°C/W)")
    power_dissipation_max: Optional[float] = Field(None, description="Maximum power dissipation (W)")

class ElectricalSpecification(BaseModel):
    """Electrical characteristics of components"""
    operating_voltage_min: float = Field(..., description="Minimum operating voltage (V)")
    operating_voltage_max: float = Field(..., description="Maximum operating voltage (V)")
    supply_current_typical: Optional[float] = Field(None, description="Typical supply current (mA)")
    supply_current_max: Optional[float] = Field(None, description="Maximum supply current (mA)")
    input_current_max: Optional[float] = Field(None, description="Maximum input current (mA)")
    output_current_max: Optional[float] = Field(None, description="Maximum output current (mA)")
    line_regulation: Optional[float] = Field(None, description="Line regulation (%/V)")
    load_regulation: Optional[float] = Field(None, description="Load regulation (%)")
    efficiency_typical: Optional[float] = Field(None, description="Typical efficiency (%)")

class PackageInfo(BaseModel):
    """Component packaging information"""
    package_type: str = Field(..., description="Package type (e.g., QFN, LQFP, BGA)")
    pin_count: Optional[int] = Field(None, description="Number of pins")
    package_size: Optional[str] = Field(None, description="Package dimensions (mm)")
    pitch: Optional[float] = Field(None, description="Pin pitch (mm)")
    height_max: Optional[float] = Field(None, description="Maximum height (mm)")

class PricingInfo(BaseModel):
    """Component pricing and availability"""
    price_1k: Optional[float] = Field(None, description="Price per unit at 1K quantity (USD)")
    price_10k: Optional[float] = Field(None, description="Price per unit at 10K quantity (USD)")
    price_100k: Optional[float] = Field(None, description="Price per unit at 100K quantity (USD)")
    lead_time_weeks: Optional[int] = Field(None, description="Lead time in weeks")
    availability_status: Optional[str] = Field(None, description="Current availability status")
    lifecycle_status: Optional[str] = Field(None, description="Product lifecycle status")

class ComponentSpecification(BaseModel):
    """Complete hardware component specification"""
    # Basic Information
    component_id: str = Field(..., description="Unique component identifier")
    name: str = Field(..., description="Component name")
    manufacturer: str = Field(..., description="Manufacturer name")
    part_number: str = Field(..., description="Manufacturer part number")
    category: ComponentCategory = Field(..., description="Component category")
    subcategory: Optional[str] = Field(None, description="Component subcategory")
    
    # Technical Specifications
    electrical_specs: ElectricalSpecification
    thermal_specs: ThermalSpecification
    package_info: PackageInfo
    
    # Compliance and Standards
    compliance_standards: List[ComplianceStandard] = Field(default_factory=list)
    automotive_grade: Optional[str] = Field(None, description="AEC-Q100 grade (0, 1, 2, 3)")
    safety_rating: Optional[str] = Field(None, description="Functional safety rating (ASIL, SIL)")
    
    # Commercial Information
    pricing: Optional[PricingInfo] = Field(None)
    
    # Documentation
    datasheet_url: Optional[str] = Field(None, description="Datasheet URL")
    application_notes: List[str] = Field(default_factory=list, description="Application note URLs")
    reference_designs: List[str] = Field(default_factory=list, description="Reference design URLs")
    
    # Additional Metadata
    description: Optional[str] = Field(None, description="Component description")
    key_features: List[str] = Field(default_factory=list, description="Key features list")
    applications: List[str] = Field(default_factory=list, description="Typical applications")
    
    # Search and Classification
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    similar_components: List[str] = Field(default_factory=list, description="Similar component IDs")
