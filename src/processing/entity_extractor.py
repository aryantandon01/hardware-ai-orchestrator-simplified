# src/processing/entity_extractor.py
from typing import Any, Dict

class HardwareEntityExtractor:
    """Extract hardware-specific entities from natural language queries"""
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        entities = {
            "voltage_ranges": self._extract_voltages(query),
            "current_requirements": self._extract_currents(query), 
            "temperature_specs": self._extract_temperatures(query),
            "power_requirements": self._extract_power(query),
            "compliance_standards": self._extract_standards(query),
            "package_constraints": self._extract_packages(query)
        }
        return entities
