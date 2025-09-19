"""
IoT Microcontroller Selection Demo - Medium Complexity Scenario
Demonstrates comparative analysis and trade-off evaluation for embedded applications
"""
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass 
class IoTRequirements:
    """IoT application requirements"""
    architecture: str = "ARM Cortex-M4"
    connectivity: List[str] = None
    power_budget: str = "Ultra-low power"
    memory_requirements: str = "Moderate"
    cost_target: str = "Cost-optimized"
    development_timeline: str = "6 months"
    
    def __post_init__(self):
        if self.connectivity is None:
            self.connectivity = ["WiFi", "Bluetooth"]

class IoTMCUSelectionDemo:
    """Medium-complexity component selection scenario with quantitative trade-off analysis"""
    
    def __init__(self):
        pass
        
    async def process_selection_query(self, query: str, requirements: IoTRequirements = None) -> Dict[str, Any]:
        """
        Process IoT microcontroller selection with comprehensive comparative analysis
        
        Expected query: "Compare ARM Cortex-M4 microcontrollers for IoT with ultra-low power and WiFi"
        """
        if requirements is None:
            requirements = IoTRequirements()
            
        logger.info(f"Processing IoT MCU selection: {query}")
        
        # Step 1: Generate candidate microcontrollers
        candidates = self._generate_mcu_candidates(requirements)
        
        # Step 2: Perform detailed comparison
        comparison_matrix = self._create_comparison_matrix(candidates, requirements)
        
        # Step 3: Power analysis across operating modes
        power_analysis = self._analyze_power_consumption(candidates)
        
        # Step 4: Development ecosystem evaluation
        ecosystem_analysis = self._evaluate_development_ecosystems(candidates)
        
        # Step 5: Cost analysis across volumes
        cost_analysis = self._perform_cost_analysis(candidates)
        
        # Step 6: Generate recommendation
        recommendation = self._generate_recommendation(candidates, requirements, comparison_matrix)
        
        return {
            "scenario": "IoT Microcontroller Selection",
            "complexity_level": "Medium", 
            "target_model": "grok_2",
            "selection_analysis": {
                "requirements_summary": {
                    "architecture": requirements.architecture,
                    "connectivity": requirements.connectivity,
                    "power_target": requirements.power_budget,
                    "cost_objective": requirements.cost_target
                },
                "candidate_microcontrollers": candidates,
                "comparison_matrix": comparison_matrix,
                "power_analysis": power_analysis,
                "ecosystem_analysis": ecosystem_analysis, 
                "cost_analysis": cost_analysis,
                "recommendation": recommendation
            },
            "value_proposition": {
                "decision_confidence": "Quantitative analysis eliminates guesswork",
                "time_savings": "Reduces evaluation time from weeks to hours",
                "risk_reduction": "Power and cost modeling prevents late-stage surprises", 
                "optimization": "Multi-dimensional trade-off analysis ensures optimal choice"
            }
        }
    
    def _generate_mcu_candidates(self, req: IoTRequirements) -> List[Dict[str, Any]]:
        """Generate candidate microcontrollers based on requirements"""
        
        candidates = [
            {
                "name": "STM32L4R5",
                "manufacturer": "STMicroelectronics",
                "core": "ARM Cortex-M4F @ 120MHz",
                "memory": {
                    "flash": "2MB",
                    "ram": "640KB", 
                    "eeprom": "None (emulated)"
                },
                "connectivity": {
                    "built_in": ["USB", "CAN", "I2C", "SPI", "UART"],
                    "external_required": ["WiFi module", "Bluetooth module"]
                },
                "power_specs": {
                    "stop_mode": "5.2µA",
                    "active_mode": "84µA/MHz",
                    "run_mode_typical": "10.1mA @ 120MHz"
                },
                "package_options": ["LQFP144", "UFBGA169", "LQFP100"],
                "strengths": ["Ultra-low power", "Large memory", "Rich peripherals"],
                "weaknesses": ["No integrated connectivity", "Higher pin count"]
            },
            {
                "name": "ESP32-S3", 
                "manufacturer": "Espressif Systems",
                "core": "Dual Xtensa LX7 @ 240MHz",
                "memory": {
                    "flash": "8MB (external)",
                    "ram": "512KB", 
                    "psram": "8MB (optional)"
                },
                "connectivity": {
                    "built_in": ["WiFi 6", "Bluetooth 5.0", "USB", "I2C", "SPI", "UART"],
                    "external_required": []
                },
                "power_specs": {
                    "deep_sleep": "10µA",
                    "active_mode": "44µA/MHz", 
                    "wifi_active": "120mA typical"
                },
                "package_options": ["QFN56", "QFN32"],
                "strengths": ["Integrated WiFi/Bluetooth", "Low cost", "Rich ecosystem"],
                "weaknesses": ["Higher power consumption", "Non-ARM architecture"]
            },
            {
                "name": "nRF52840",
                "manufacturer": "Nordic Semiconductor", 
                "core": "ARM Cortex-M4F @ 64MHz",
                "memory": {
                    "flash": "1MB",
                    "ram": "256KB",
                    "eeprom": "None"
                },
                "connectivity": {
                    "built_in": ["Bluetooth 5.2", "Thread", "Zigbee", "USB", "I2C", "SPI"],
                    "external_required": ["WiFi module"]
                },
                "power_specs": {
                    "system_off": "1.5µA",
                    "active_mode": "58µA/MHz",
                    "bluetooth_active": "5.5mA"
                },
                "package_options": ["QFN73", "WLCSP"],
                "strengths": ["Excellent power efficiency", "Advanced Bluetooth", "Small form factor"],
                "weaknesses": ["No WiFi", "Limited flash memory", "Higher cost"]
            }
        ]
        
        return candidates
    
    def _create_comparison_matrix(self, candidates: List[Dict], req: IoTRequirements) -> Dict[str, Any]:
        """Create comprehensive comparison matrix with scoring"""
        
        # Define evaluation criteria with weights
        criteria_weights = {
            "power_efficiency": 0.30,
            "connectivity_match": 0.25, 
            "memory_adequacy": 0.15,
            "cost_effectiveness": 0.15,
            "development_ease": 0.10,
            "ecosystem_maturity": 0.05
        }
        
        matrix = {}
        
        for candidate in candidates:
            name = candidate["name"]
            
            # Score each criteria (0-10 scale)
            scores = {
                "power_efficiency": self._score_power_efficiency(candidate),
                "connectivity_match": self._score_connectivity_match(candidate, req),
                "memory_adequacy": self._score_memory_adequacy(candidate),
                "cost_effectiveness": self._score_cost_effectiveness(candidate),
                "development_ease": self._score_development_ease(candidate),
                "ecosystem_maturity": self._score_ecosystem_maturity(candidate)
            }
            
            # Calculate weighted score
            weighted_score = sum(scores[criteria] * weight for criteria, weight in criteria_weights.items())
            
            matrix[name] = {
                "scores": scores,
                "weighted_total": round(weighted_score, 2),
                "ranking_factors": self._get_ranking_factors(candidate, scores)
            }
        
        return {
            "evaluation_criteria": criteria_weights,
            "candidate_scores": matrix,
            "ranking": sorted(matrix.keys(), key=lambda x: matrix[x]["weighted_total"], reverse=True)
        }
    
    def _analyze_power_consumption(self, candidates: List[Dict]) -> Dict[str, Any]:
        """Detailed power consumption analysis across operating modes"""
        
        # Define typical IoT usage pattern
        usage_pattern = {
            "deep_sleep": 0.90,  # 90% of time
            "sensor_reading": 0.05,  # 5% of time  
            "data_processing": 0.03,  # 3% of time
            "wireless_transmission": 0.02  # 2% of time
        }
        
        power_analysis = {}
        
        for candidate in candidates:
            name = candidate["name"]
            power_specs = candidate["power_specs"]
            
            # Calculate average power consumption
            if name == "STM32L4R5":
                avg_power = (
                    usage_pattern["deep_sleep"] * 5.2e-3 +  # mA
                    usage_pattern["sensor_reading"] * 10.1 + 
                    usage_pattern["data_processing"] * 10.1 +
                    usage_pattern["wireless_transmission"] * 25.0  # External module
                )
            elif name == "ESP32-S3":
                avg_power = (
                    usage_pattern["deep_sleep"] * 0.01 +
                    usage_pattern["sensor_reading"] * 20.0 +
                    usage_pattern["data_processing"] * 30.0 +
                    usage_pattern["wireless_transmission"] * 120.0
                )
            elif name == "nRF52840":
                avg_power = (
                    usage_pattern["deep_sleep"] * 1.5e-3 +
                    usage_pattern["sensor_reading"] * 3.7 +
                    usage_pattern["data_processing"] * 3.7 +
                    usage_pattern["wireless_transmission"] * 5.5
                )
            
            # Calculate battery life estimates
            battery_capacities = {"CR2032": 220, "AA": 2800, "18650": 3400}  # mAh
            
            battery_life = {}
            for battery, capacity in battery_capacities.items():
                life_hours = capacity / avg_power
                battery_life[battery] = {
                    "hours": round(life_hours),
                    "days": round(life_hours / 24, 1),
                    "years": round(life_hours / (24 * 365), 2)
                }
            
            power_analysis[name] = {
                "average_power_consumption": f"{avg_power:.2f}mA",
                "power_breakdown": {
                    "sleep_contribution": f"{usage_pattern['deep_sleep'] * avg_power:.3f}mA",
                    "active_contribution": f"{(1-usage_pattern['deep_sleep']) * avg_power:.2f}mA"
                },
                "battery_life_estimates": battery_life,
                "power_optimization_notes": self._get_power_optimization_notes(candidate)
            }
        
        return power_analysis
    
    def _evaluate_development_ecosystems(self, candidates: List[Dict]) -> Dict[str, Any]:
        """Evaluate development ecosystems and toolchain maturity"""
        
        ecosystem_analysis = {}
        
        for candidate in candidates:
            name = candidate["name"]
            
            if name == "STM32L4R5":
                ecosystem_analysis[name] = {
                    "ide_support": ["STM32CubeIDE", "Keil MDK", "IAR EWARM", "VS Code"],
                    "framework_support": ["STM32Cube HAL", "FreeRTOS", "Azure RTOS", "Zephyr"],
                    "community_size": "Large",
                    "documentation_quality": "Excellent", 
                    "code_examples": "Extensive",
                    "third_party_libraries": "Wide selection",
                    "debugging_tools": "ST-Link, J-Link support",
                    "learning_curve": "Medium",
                    "ecosystem_maturity": 9
                }
            elif name == "ESP32-S3":
                ecosystem_analysis[name] = {
                    "ide_support": ["ESP-IDF", "Arduino IDE", "PlatformIO", "VS Code"],
                    "framework_support": ["ESP-IDF", "Arduino", "MicroPython", "Zephyr"],
                    "community_size": "Very Large",
                    "documentation_quality": "Good",
                    "code_examples": "Abundant", 
                    "third_party_libraries": "Excellent for WiFi/IoT",
                    "debugging_tools": "Built-in JTAG, ESP-Prog",
                    "learning_curve": "Low",
                    "ecosystem_maturity": 8
                }
            elif name == "nRF52840":
                ecosystem_analysis[name] = {
                    "ide_support": ["nRF Connect SDK", "Keil MDK", "GCC", "VS Code"],
                    "framework_support": ["nRF Connect SDK", "Zephyr", "FreeRTOS", "Mbed"],
                    "community_size": "Medium",
                    "documentation_quality": "Excellent",
                    "code_examples": "Comprehensive",
                    "third_party_libraries": "Good for Bluetooth/mesh",
                    "debugging_tools": "nRF DK, J-Link support", 
                    "learning_curve": "Medium-High",
                    "ecosystem_maturity": 7
                }
        
        return ecosystem_analysis
    
    def _perform_cost_analysis(self, candidates: List[Dict]) -> Dict[str, Any]:
        """Comprehensive cost analysis across volume tiers"""
        
        cost_analysis = {}
        
        # Define volume tiers and pricing
        volume_pricing = {
            "STM32L4R5": {"1K": 8.50, "10K": 6.80, "100K": 5.20},
            "ESP32-S3": {"1K": 3.20, "10K": 2.85, "100K": 2.40},
            "nRF52840": {"1K": 4.80, "10K": 4.20, "100K": 3.60}
        }
        
        # Additional system costs
        for candidate in candidates:
            name = candidate["name"]
            base_pricing = volume_pricing[name]
            
            # Calculate additional component costs
            additional_costs = self._calculate_additional_costs(candidate)
            
            total_costs = {}
            for volume, base_cost in base_pricing.items():
                total_costs[volume] = base_cost + additional_costs["per_unit"]
            
            cost_analysis[name] = {
                "mcu_pricing": base_pricing,
                "additional_components": additional_costs,
                "total_system_cost": total_costs,
                "development_costs": self._estimate_development_costs(candidate),
                "cost_breakdown": self._generate_cost_breakdown(candidate, base_pricing["1K"])
            }
        
        return cost_analysis
    
    def _generate_recommendation(self, candidates: List[Dict], req: IoTRequirements, comparison: Dict) -> Dict[str, Any]:
        """Generate final recommendation with detailed justification"""
        
        ranking = comparison["ranking"]
        top_choice = ranking[0]
        
        # Find the top candidate details
        top_candidate = next(c for c in candidates if c["name"] == top_choice)
        
        recommendation = {
            "primary_recommendation": {
                "microcontroller": top_choice,
                "manufacturer": top_candidate["manufacturer"],
                "confidence": "High",
                "overall_score": comparison["candidate_scores"][top_choice]["weighted_total"]
            },
            "key_advantages": self._get_key_advantages(top_candidate, comparison),
            "implementation_considerations": self._get_implementation_considerations(top_candidate),
            "alternative_options": {
                "performance_alternative": ranking[1] if len(ranking) > 1 else None,
                "cost_alternative": self._get_cost_alternative(candidates, comparison),
                "power_alternative": self._get_power_alternative(candidates)
            },
            "decision_rationale": self._generate_decision_rationale(top_candidate, req, comparison),
            "next_steps": [
                "Obtain evaluation board and development kit",
                "Validate power consumption with actual application code",
                "Prototype critical connectivity and sensor interfaces", 
                "Verify regulatory compliance for target markets",
                "Establish supplier relationships and pricing agreements"
            ]
        }
        
        return recommendation
    
    # Helper methods for scoring and analysis
    def _score_power_efficiency(self, candidate: Dict) -> int:
        """Score power efficiency (0-10)"""
        power_specs = candidate["power_specs"]
        
        if "system_off" in power_specs:
            sleep_current = float(power_specs["system_off"].replace("µA", ""))
        else:
            sleep_current = float(power_specs["stop_mode"].replace("µA", "")) if "stop_mode" in power_specs else 10.0
            
        # Score based on sleep current (lower is better)
        if sleep_current < 2.0:
            return 10
        elif sleep_current < 5.0:
            return 8
        elif sleep_current < 10.0:
            return 6
        else:
            return 4
    
    def _score_connectivity_match(self, candidate: Dict, req: IoTRequirements) -> int:
        """Score connectivity match to requirements"""
        built_in = candidate["connectivity"]["built_in"]
        required_external = candidate["connectivity"]["external_required"]
        
        # Count matching built-in connectivity
        matches = sum(1 for conn in req.connectivity if any(conn.lower() in bi.lower() for bi in built_in))
        total_required = len(req.connectivity)
        
        # Penalty for external requirements
        external_penalty = len(required_external) * 2
        
        base_score = int((matches / total_required) * 10)
        return max(0, base_score - external_penalty)
    
    def _score_memory_adequacy(self, candidate: Dict) -> int:
        """Score memory adequacy for IoT applications"""
        memory = candidate["memory"]
        flash_mb = float(memory["flash"].replace("MB", ""))
        ram_kb = float(memory["ram"].replace("KB", ""))
        
        # IoT application typically needs 512KB+ flash, 128KB+ RAM
        flash_score = min(10, int(flash_mb * 5))  # 2MB = 10 points
        ram_score = min(10, int(ram_kb / 25.6))   # 256KB = 10 points
        
        return int((flash_score + ram_score) / 2)
    
    def _score_cost_effectiveness(self, candidate: Dict) -> int:
        """Score cost effectiveness (lower cost = higher score)"""
        # Rough cost estimates based on typical market pricing
        cost_estimates = {
            "STM32L4R5": 8.5,
            "ESP32-S3": 3.2, 
            "nRF52840": 4.8
        }
        
        cost = cost_estimates.get(candidate["name"], 5.0)
        
        # Score inversely proportional to cost
        if cost < 3.0:
            return 10
        elif cost < 5.0:
            return 8
        elif cost < 7.0:
            return 6
        else:
            return 4
    
    def _score_development_ease(self, candidate: Dict) -> int:
        """Score development ease and ecosystem"""
        ease_scores = {
            "STM32L4R5": 7,  # Good tools, medium learning curve
            "ESP32-S3": 9,   # Arduino support, easy start
            "nRF52840": 6    # Powerful but steeper curve
        }
        
        return ease_scores.get(candidate["name"], 5)
    
    def _score_ecosystem_maturity(self, candidate: Dict) -> int:
        """Score ecosystem maturity"""
        maturity_scores = {
            "STM32L4R5": 9,  # Very mature ARM ecosystem
            "ESP32-S3": 8,   # Rapid growth, good support
            "nRF52840": 7    # Focused but smaller ecosystem
        }
        
        return maturity_scores.get(candidate["name"], 5)
    
    def _get_ranking_factors(self, candidate: Dict, scores: Dict) -> List[str]:
        """Get key ranking factors for candidate"""
        factors = []
        
        for criteria, score in scores.items():
            if score >= 8:
                factors.append(f"Strong {criteria.replace('_', ' ')}")
        
        return factors
    
    def _get_power_optimization_notes(self, candidate: Dict) -> List[str]:
        """Get power optimization recommendations"""
        name = candidate["name"]
        
        notes = {
            "STM32L4R5": [
                "Use STOP2 mode for lowest power consumption",
                "Optimize peripheral clock gating",
                "Consider external RTC for wake-up timing"
            ],
            "ESP32-S3": [
                "Use deep sleep mode between transmissions",
                "Optimize WiFi connection patterns", 
                "Consider ULP coprocessor for sensor monitoring"
            ],
            "nRF52840": [
                "Leverage System OFF mode for ultra-low power",
                "Use RAM retention selectively",
                "Optimize Bluetooth connection intervals"
            ]
        }
        
        return notes.get(name, [])
    
    def _calculate_additional_costs(self, candidate: Dict) -> Dict[str, Any]:
        """Calculate additional component costs beyond the MCU"""
        name = candidate["name"]
        
        additional_costs = {
            "STM32L4R5": {
                "wifi_module": 2.50,
                "bluetooth_module": 1.80,
                "external_crystal": 0.15,
                "power_management": 0.50,
                "per_unit": 5.45
            },
            "ESP32-S3": {
                "external_flash": 0.80,
                "power_management": 0.30,
                "per_unit": 1.10
            },
            "nRF52840": {
                "wifi_module": 2.50,
                "external_crystal": 0.15,
                "power_management": 0.40,
                "per_unit": 3.05
            }
        }
        
        return additional_costs.get(name, {"per_unit": 0})
    
    def _estimate_development_costs(self, candidate: Dict) -> Dict[str, Any]:
        """Estimate development costs and timeline"""
        name = candidate["name"]
        
        dev_costs = {
            "STM32L4R5": {
                "evaluation_kit": 50,
                "development_tools": 200,
                "estimated_timeline": "4-6 months",
                "engineering_effort": "Medium"
            },
            "ESP32-S3": {
                "evaluation_kit": 25,
                "development_tools": 0,  # Free tools
                "estimated_timeline": "2-4 months", 
                "engineering_effort": "Low"
            },
            "nRF52840": {
                "evaluation_kit": 40,
                "development_tools": 150,
                "estimated_timeline": "5-7 months",
                "engineering_effort": "Medium-High"
            }
        }
        
        return dev_costs.get(name, {})
    
    def _generate_cost_breakdown(self, candidate: Dict, base_cost: float) -> Dict[str, str]:
        """Generate cost breakdown percentages"""
        additional = self._calculate_additional_costs(candidate)["per_unit"]
        total = base_cost + additional
        
        return {
            "mcu_percentage": f"{(base_cost/total)*100:.1f}%",
            "additional_components": f"{(additional/total)*100:.1f}%",
            "total_system_cost": f"${total:.2f}"
        }
    
    def _get_key_advantages(self, candidate: Dict, comparison: Dict) -> List[str]:
        """Get key advantages of recommended choice"""
        name = candidate["name"]
        scores = comparison["candidate_scores"][name]["scores"]
        
        advantages = []
        for criteria, score in scores.items():
            if score >= 8:
                advantages.append(f"Excellent {criteria.replace('_', ' ')}: {score}/10")
        
        return advantages
    
    def _get_implementation_considerations(self, candidate: Dict) -> List[str]:
        """Get implementation considerations for the recommended choice"""
        name = candidate["name"]
        
        considerations = {
            "STM32L4R5": [
                "External WiFi/Bluetooth modules require additional design complexity",
                "Consider antenna design for external wireless modules",
                "Power management design critical for battery operation"
            ],
            "ESP32-S3": [
                "Integrated antenna or external antenna design required",
                "Power supply design critical for WiFi operation",
                "Consider EMC implications of high-speed wireless"
            ],
            "nRF52840": [
                "Excellent for Bluetooth-centric applications",
                "External WiFi module required for dual connectivity",
                "Consider mesh networking capabilities for IoT networks"
            ]
        }
        
        return considerations.get(name, [])
    
    def _get_cost_alternative(self, candidates: List[Dict], comparison: Dict) -> str:
        """Get the most cost-effective alternative"""
        costs = {}
        for candidate in candidates:
            name = candidate["name"]
            # Use rough cost estimates
            cost_estimates = {"STM32L4R5": 8.5, "ESP32-S3": 3.2, "nRF52840": 4.8}
            costs[name] = cost_estimates.get(name, 5.0)
        
        return min(costs.keys(), key=lambda x: costs[x])
    
    def _get_power_alternative(self, candidates: List[Dict]) -> str:
        """Get the most power-efficient alternative"""
        power_scores = {}
        for candidate in candidates:
            power_scores[candidate["name"]] = self._score_power_efficiency(candidate)
        
        return max(power_scores.keys(), key=lambda x: power_scores[x])
    
    def _generate_decision_rationale(self, candidate: Dict, req: IoTRequirements, comparison: Dict) -> List[str]:
        """Generate detailed decision rationale"""
        name = candidate["name"]
        
        rationale = [
            f"Highest overall score ({comparison['candidate_scores'][name]['weighted_total']}/10) based on weighted criteria",
            f"Strong alignment with {req.power_budget} power requirements",
            f"Good connectivity match for {', '.join(req.connectivity)} requirements",
            f"Appropriate memory capacity for {req.memory_requirements} applications",
            f"Development timeline compatible with {req.development_timeline} project schedule"
        ]
        
        return rationale
