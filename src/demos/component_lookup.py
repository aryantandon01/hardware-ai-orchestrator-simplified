"""
Component Specification Lookup Demo - Low Complexity Scenario  
Demonstrates fast factual information retrieval and tabular data presentation
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LookupRequest:
    """Component lookup request parameters"""
    part_number: str
    manufacturer: Optional[str] = None
    include_alternatives: bool = True
    include_pricing: bool = True
    include_availability: bool = False

class ComponentLookupDemo:
    """Simple, fast component specification lookup scenario"""
    
    def __init__(self):
        self.component_database = self._initialize_component_database()
        
    async def process_lookup_query(self, query: str, request: LookupRequest = None) -> Dict[str, Any]:
        """
        Process component specification lookup query with fast retrieval
        
        Expected query: "What are LM317 specifications?" or "STM32F103 datasheet"
        """
        # Extract part number from query if not provided in request
        if request is None:
            part_number = self._extract_part_number_from_query(query)
            request = LookupRequest(part_number=part_number)
        
        logger.info(f"Processing component lookup: {request.part_number}")
        
        # Step 1: Primary component lookup
        component_spec = self._lookup_component_specifications(request.part_number)
        
        if not component_spec:
            return self._handle_component_not_found(request.part_number, query)
        
        # Step 2: Format specifications for presentation
        formatted_specs = self._format_specifications(component_spec)
        
        # Step 3: Get pricing information if requested
        pricing_info = {}
        if request.include_pricing:
            pricing_info = self._get_pricing_information(request.part_number)
        
        # Step 4: Find alternative components if requested
        alternatives = []
        if request.include_alternatives:
            alternatives = self._find_alternative_components(component_spec)
        
        # Step 5: Get availability information if requested
        availability_info = {}
        if request.include_availability:
            availability_info = self._get_availability_information(request.part_number)
        
        return {
            "scenario": "Component Specification Lookup",
            "complexity_level": "Low",
            "target_model": "gpt_4o_mini",
            "lookup_results": {
                "component_identification": {
                    "part_number": component_spec["part_number"],
                    "manufacturer": component_spec["manufacturer"],
                    "description": component_spec["description"],
                    "category": component_spec["category"]
                },
                "key_specifications": formatted_specs,
                "pricing_information": pricing_info,
                "alternative_components": alternatives,
                "availability_status": availability_info,
                "documentation_links": self._get_documentation_links(component_spec),
                "package_information": self._get_package_information(component_spec)
            },
            "value_proposition": {
                "instant_access": "Immediate specification retrieval without manual datasheet searching",
                "time_savings": "Reduces lookup time from minutes to seconds",
                "comprehensive_data": "All key specifications in standardized format",
                "alternative_awareness": "Automatic suggestion of equivalent components"
            }
        }
    
    def _lookup_component_specifications(self, part_number: str) -> Optional[Dict[str, Any]]:
        """Lookup component specifications from database"""
        
        # Normalize part number (remove spaces, convert to uppercase)
        normalized_pn = part_number.upper().replace(" ", "").replace("-", "")
        
        # Direct lookup
        if normalized_pn in self.component_database:
            return self.component_database[normalized_pn]
        
        # Fuzzy matching for common variations
        for db_pn, spec in self.component_database.items():
            if self._fuzzy_match(normalized_pn, db_pn):
                return spec
        
        return None
    
    def _format_specifications(self, component_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Format component specifications for clear presentation"""
        
        category = component_spec.get("category", "").lower()
        
        if category == "voltage_regulator":
            return self._format_regulator_specs(component_spec)
        elif category == "microcontroller":
            return self._format_mcu_specs(component_spec)
        elif category == "operational_amplifier":
            return self._format_opamp_specs(component_spec)
        elif category == "power_management":
            return self._format_power_management_specs(component_spec)
        else:
            return self._format_generic_specs(component_spec)
    
    def _format_regulator_specs(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Format voltage regulator specifications"""
        
        return {
            "electrical_characteristics": {
                "Input Voltage Range": spec.get("input_voltage_range", "N/A"),
                "Output Voltage Range": spec.get("output_voltage_range", "N/A"),
                "Maximum Output Current": spec.get("max_output_current", "N/A"),
                "Dropout Voltage": spec.get("dropout_voltage", "N/A"),
                "Line Regulation": spec.get("line_regulation", "N/A"),
                "Load Regulation": spec.get("load_regulation", "N/A"),
                "Quiescent Current": spec.get("quiescent_current", "N/A")
            },
            "thermal_characteristics": {
                "Operating Temperature Range": spec.get("operating_temp_range", "N/A"),
                "Thermal Resistance (θJA)": spec.get("thermal_resistance_ja", "N/A"),
                "Maximum Junction Temperature": spec.get("max_junction_temp", "N/A")
            },
            "performance_specs": {
                "PSRR (Power Supply Rejection Ratio)": spec.get("psrr", "N/A"),
                "Output Noise": spec.get("output_noise", "N/A"),
                "Transient Response": spec.get("transient_response", "N/A")
            }
        }
    
    def _format_mcu_specs(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Format microcontroller specifications"""
        
        return {
            "processor_core": {
                "Architecture": spec.get("architecture", "N/A"),
                "Core": spec.get("core", "N/A"),
                "Maximum Frequency": spec.get("max_frequency", "N/A"),
                "Performance": spec.get("performance_rating", "N/A")
            },
            "memory_specifications": {
                "Flash Memory": spec.get("flash_memory", "N/A"),
                "RAM": spec.get("ram_memory", "N/A"),
                "EEPROM": spec.get("eeprom_memory", "N/A"),
                "External Memory Interface": spec.get("external_memory", "N/A")
            },
            "peripheral_interfaces": {
                "GPIO Pins": spec.get("gpio_count", "N/A"),
                "Analog Inputs (ADC)": spec.get("adc_channels", "N/A"),
                "PWM Channels": spec.get("pwm_channels", "N/A"),
                "Communication Interfaces": spec.get("communication_interfaces", [])
            },
            "power_specifications": {
                "Operating Voltage": spec.get("operating_voltage", "N/A"),
                "Current Consumption (Active)": spec.get("active_current", "N/A"),
                "Current Consumption (Sleep)": spec.get("sleep_current", "N/A"),
                "Power-Down Modes": spec.get("power_modes", [])
            }
        }
    
    def _format_opamp_specs(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Format operational amplifier specifications"""
        
        return {
            "dc_characteristics": {
                "Input Offset Voltage": spec.get("input_offset_voltage", "N/A"),
                "Input Bias Current": spec.get("input_bias_current", "N/A"),
                "Input Offset Current": spec.get("input_offset_current", "N/A"),
                "Common-Mode Rejection Ratio": spec.get("cmrr", "N/A"),
                "Power Supply Rejection Ratio": spec.get("psrr", "N/A")
            },
            "ac_characteristics": {
                "Gain-Bandwidth Product": spec.get("gbw", "N/A"),
                "Slew Rate": spec.get("slew_rate", "N/A"),
                "Phase Margin": spec.get("phase_margin", "N/A"),
                "Unity-Gain Bandwidth": spec.get("unity_gain_bw", "N/A")
            },
            "noise_characteristics": {
                "Input Voltage Noise": spec.get("input_voltage_noise", "N/A"),
                "Input Current Noise": spec.get("input_current_noise", "N/A"),
                "Noise Figure": spec.get("noise_figure", "N/A")
            }
        }
    
    def _get_pricing_information(self, part_number: str) -> Dict[str, Any]:
        """Get pricing information across different volume tiers"""
        
        # Sample pricing data (in a real system, this would query a pricing API)
        pricing_data = {
            "LM317T": {
                "currency": "USD",
                "pricing_tiers": {
                    "1": {"price": 0.85, "moq": 1},
                    "10": {"price": 0.75, "moq": 10},
                    "100": {"price": 0.65, "moq": 100},
                    "1000": {"price": 0.52, "moq": 1000}
                },
                "price_breaks": [1, 10, 100, 1000, 5000],
                "last_updated": "2025-09-15"
            },
            "STM32F103C8T6": {
                "currency": "USD", 
                "pricing_tiers": {
                    "1": {"price": 3.10, "moq": 1},
                    "10": {"price": 2.85, "moq": 10},
                    "100": {"price": 2.65, "moq": 100},
                    "1000": {"price": 2.25, "moq": 1000}
                },
                "price_breaks": [1, 10, 100, 1000, 10000],
                "last_updated": "2025-09-15"
            }
        }
        
        return pricing_data.get(part_number, {
            "note": "Pricing information not available",
            "recommendation": "Contact distributor for current pricing"
        })
    
    def _find_alternative_components(self, component_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find alternative/equivalent components"""
        
        category = component_spec.get("category", "").lower()
        part_number = component_spec.get("part_number", "")
        
        alternatives = []
        
        if part_number == "LM317T":
            alternatives = [
                {
                    "part_number": "LM1117-ADJ",
                    "manufacturer": "Texas Instruments",
                    "description": "Low-dropout adjustable regulator",
                    "key_differences": ["Lower dropout voltage (1.2V vs 2V)", "SOT-223 package available"],
                    "compatibility": "Pin-compatible replacement with improved dropout",
                    "cost_comparison": "Similar pricing",
                    "availability": "Good"
                },
                {
                    "part_number": "AMS1117-ADJ", 
                    "manufacturer": "Advanced Monolithic Systems",
                    "description": "Low-cost adjustable LDO regulator",
                    "key_differences": ["Lower cost", "SOT-223 package", "Similar performance"],
                    "compatibility": "Functional equivalent", 
                    "cost_comparison": "~30% lower cost",
                    "availability": "Excellent"
                }
            ]
        elif part_number == "STM32F103C8T6":
            alternatives = [
                {
                    "part_number": "STM32F103CBT6",
                    "manufacturer": "STMicroelectronics", 
                    "description": "Same family with more Flash memory",
                    "key_differences": ["128KB Flash (vs 64KB)", "Same pin configuration"],
                    "compatibility": "Pin-compatible upgrade",
                    "cost_comparison": "~20% higher cost",
                    "availability": "Good"
                },
                {
                    "part_number": "GD32F103C8T6",
                    "manufacturer": "GigaDevice",
                    "description": "Compatible alternative with enhanced features",
                    "key_differences": ["Higher max frequency (108MHz)", "Additional peripherals"],
                    "compatibility": "Code-compatible alternative",
                    "cost_comparison": "~15% lower cost", 
                    "availability": "Good"
                }
            ]
        
        return alternatives
    
    def _get_availability_information(self, part_number: str) -> Dict[str, Any]:
        """Get current availability and lead time information"""
        
        # Sample availability data (would query distributor APIs in real system)
        availability_data = {
            "LM317T": {
                "stock_level": "In Stock",
                "quantity_available": "25,000+",
                "lead_time": "Same day shipping",
                "distributors": [
                    {"name": "Digi-Key", "stock": "15K+", "price": "$0.85"},
                    {"name": "Mouser", "stock": "10K+", "price": "$0.87"},
                    {"name": "Arrow", "stock": "5K+", "price": "$0.83"}
                ],
                "manufacturer_status": "Active",
                "lifecycle_status": "Production"
            },
            "STM32F103C8T6": {
                "stock_level": "Limited Stock",
                "quantity_available": "500",
                "lead_time": "12-16 weeks",
                "distributors": [
                    {"name": "Digi-Key", "stock": "200", "price": "$3.10"},
                    {"name": "Mouser", "stock": "300", "price": "$3.15"},
                    {"name": "Arrow", "stock": "0", "price": "N/A"}
                ],
                "manufacturer_status": "Active",
                "lifecycle_status": "Production - allocation"
            }
        }
        
        return availability_data.get(part_number, {
            "note": "Availability information not available",
            "recommendation": "Check with distributors for current stock levels"
        })
    
    def _get_documentation_links(self, component_spec: Dict[str, Any]) -> Dict[str, str]:
        """Get links to component documentation"""
        
        part_number = component_spec.get("part_number", "")
        manufacturer = component_spec.get("manufacturer", "")
        
        # Sample documentation links (would be dynamically generated in real system)
        doc_links = {
            "datasheet": f"https://www.example.com/datasheets/{part_number}.pdf",
            "application_notes": f"https://www.example.com/appnotes/{part_number}/",
            "reference_designs": f"https://www.example.com/reference/{part_number}/",
            "development_tools": f"https://www.example.com/tools/{part_number}/",
            "community_forums": f"https://forum.example.com/components/{part_number}/"
        }
        
        return doc_links
    
    def _get_package_information(self, component_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get component package and physical information"""
        
        return {
            "available_packages": component_spec.get("packages", []),
            "recommended_package": component_spec.get("recommended_package", "N/A"),
            "package_dimensions": component_spec.get("package_dimensions", {}),
            "thermal_considerations": component_spec.get("thermal_package_info", ""),
            "assembly_notes": component_spec.get("assembly_notes", "")
        }
    
    def _handle_component_not_found(self, part_number: str, query: str) -> Dict[str, Any]:
        """Handle cases where component is not found in database"""
        
        # Suggest similar components or search strategies
        suggestions = self._generate_search_suggestions(part_number)
        
        return {
            "scenario": "Component Specification Lookup",
            "complexity_level": "Low",
            "target_model": "gpt_4o_mini",
            "lookup_results": {
                "status": "Component Not Found",
                "searched_part": part_number,
                "original_query": query,
                "suggestions": {
                    "similar_components": suggestions,
                    "search_tips": [
                        "Verify part number spelling and format",
                        "Check if part number includes package suffix",
                        "Try manufacturer-specific part number format",
                        "Search by component function or category"
                    ],
                    "alternative_searches": [
                        f"Search for '{part_number}' without package suffix",
                        f"Look up manufacturer '{self._extract_manufacturer(part_number)}' products",
                        "Browse by component category"
                    ]
                },
                "next_steps": [
                    "Verify part number with manufacturer datasheet",
                    "Check distributor websites for exact part number",
                    "Contact technical support for assistance"
                ]
            }
        }
    
    def _initialize_component_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize component specification database with sample data"""
        
        return {
            "LM317T": {
                "part_number": "LM317T",
                "manufacturer": "Texas Instruments",
                "description": "Adjustable 3-Terminal Positive Voltage Regulator",
                "category": "voltage_regulator",
                "input_voltage_range": "3V to 40V",
                "output_voltage_range": "1.25V to 37V (adjustable)",
                "max_output_current": "1.5A",
                "dropout_voltage": "2V typical",
                "line_regulation": "0.01% typical", 
                "load_regulation": "0.1% typical",
                "quiescent_current": "3.5mA typical",
                "operating_temp_range": "-55°C to +150°C",
                "thermal_resistance_ja": "50°C/W",
                "packages": ["TO-220", "TO-263", "SOT-223"],
                "recommended_package": "TO-220 for high current applications"
            },
            "STM32F103C8T6": {
                "part_number": "STM32F103C8T6",
                "manufacturer": "STMicroelectronics", 
                "description": "32-bit ARM Cortex-M3 Microcontroller",
                "category": "microcontroller",
                "architecture": "ARM Cortex-M3",
                "core": "32-bit RISC",
                "max_frequency": "72MHz",
                "flash_memory": "64KB",
                "ram_memory": "20KB",
                "eeprom_memory": "None (Flash emulation)",
                "gpio_count": "37",
                "adc_channels": "10 × 12-bit",
                "pwm_channels": "Multiple timers",
                "communication_interfaces": ["2× I2C", "3× USART", "2× SPI", "1× CAN", "1× USB"],
                "operating_voltage": "2.0V to 3.6V",
                "active_current": "36mA @ 72MHz",
                "sleep_current": "2µA (Standby mode)",
                "packages": ["LQFP48", "VFQFPN48"],
                "operating_temp_range": "-40°C to +85°C"
            },
            "LM741": {
                "part_number": "LM741",
                "manufacturer": "Texas Instruments",
                "description": "General Purpose Operational Amplifier",
                "category": "operational_amplifier",
                "input_offset_voltage": "1mV typical",
                "input_bias_current": "80nA typical",
                "input_offset_current": "20nA typical", 
                "cmrr": "90dB typical",
                "psrr": "77dB typical",
                "gbw": "1MHz typical",
                "slew_rate": "0.5V/µs typical",
                "input_voltage_noise": "20nV/√Hz @ 1kHz",
                "packages": ["DIP-8", "SOIC-8", "TO-99"],
                "operating_temp_range": "0°C to +70°C (commercial)"
            }
        }
    
    def _extract_part_number_from_query(self, query: str) -> str:
        """Extract part number from natural language query"""
        
        # Common part number patterns
        import re
        
        # Look for alphanumeric patterns that could be part numbers
        patterns = [
            r'\b[A-Z]{2,}\d+[A-Z]*\d*[A-Z]*\b',  # LM317T, STM32F103C8T6
            r'\b\d+[A-Z]+\d*[A-Z]*\b',            # 741, 555
            r'\b[A-Z]+\d+[A-Z]*\b'                # LM741, TL071
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query.upper())
            if matches:
                return matches[0]
        
        # If no pattern match, try to extract the most likely candidate
        words = query.upper().replace("?", "").split()
        for word in words:
            if len(word) > 3 and any(c.isdigit() for c in word) and any(c.isalpha() for c in word):
                return word
        
        return "UNKNOWN"
    
    def _fuzzy_match(self, query_pn: str, db_pn: str) -> bool:
        """Perform fuzzy matching for part number variations"""
        
        # Remove common suffixes and prefixes for matching
        query_clean = query_pn.replace("T", "").replace("-", "")
        db_clean = db_pn.replace("T", "").replace("-", "")
        
        return query_clean == db_clean or query_pn in db_pn or db_pn in query_pn
    
    def _generate_search_suggestions(self, part_number: str) -> List[str]:
        """Generate search suggestions for unknown components"""
        
        suggestions = []
        
        # Extract base part number
        base = part_number[:6] if len(part_number) > 6 else part_number
        
        # Generate variations
        suggestions.append(f"Try searching for base part: {base}")
        suggestions.append(f"Search without package suffix")
        suggestions.append(f"Look for manufacturer prefix variations")
        
        return suggestions
    
    def _extract_manufacturer(self, part_number: str) -> str:
        """Extract likely manufacturer from part number prefix"""
        
        manufacturer_prefixes = {
            "LM": "Texas Instruments / National Semiconductor",
            "STM32": "STMicroelectronics", 
            "TL": "Texas Instruments",
            "AD": "Analog Devices",
            "MAX": "Maxim Integrated"
        }
        
        for prefix, mfg in manufacturer_prefixes.items():
            if part_number.startswith(prefix):
                return mfg
        
        return "Unknown"
    
    def _format_generic_specs(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Format generic component specifications"""
        
        formatted = {}
        
        # Group specifications by type
        electrical_keys = ["voltage", "current", "power", "frequency", "impedance"]
        thermal_keys = ["temperature", "thermal", "junction"]
        mechanical_keys = ["package", "dimensions", "weight"]
        
        for key, value in spec.items():
            if any(ek in key.lower() for ek in electrical_keys):
                if "electrical" not in formatted:
                    formatted["electrical"] = {}
                formatted["electrical"][key] = value
            elif any(tk in key.lower() for tk in thermal_keys):
                if "thermal" not in formatted:
                    formatted["thermal"] = {}
                formatted["thermal"][key] = value
            elif any(mk in key.lower() for mk in mechanical_keys):
                if "mechanical" not in formatted:
                    formatted["mechanical"] = {}
                formatted["mechanical"][key] = value
            else:
                if "general" not in formatted:
                    formatted["general"] = {}
                formatted["general"][key] = value
        
        return formatted
