"""
Operational Amplifier Educational Demo - Medium-Low Complexity Scenario
Demonstrates educational content delivery with clear explanations and practical examples
"""
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

@dataclass
class OpAmpApplication:
    """Operational amplifier application parameters"""
    circuit_type: str = "Non-inverting amplifier"
    gain_requirement: float = 10.0
    bandwidth_requirement: float = 100000.0  # Hz
    input_impedance: str = "High"
    output_impedance: str = "Low"

class OpAmpEducationalDemo:
    """Educational content scenario focused on clear concept explanation and learning"""
    
    def __init__(self):
        self.common_opamps = self._load_common_opamps()
        
    async def process_educational_query(self, query: str, application: OpAmpApplication = None) -> Dict[str, Any]:
        """
        Process operational amplifier educational query with comprehensive explanations
        
        Expected query: "Explain gain-bandwidth product in op-amp design"
        """
        if application is None:
            application = OpAmpApplication()
            
        logger.info(f"Processing op-amp educational query: {query}")
        
        # Determine the educational focus from query
        educational_focus = self._determine_educational_focus(query)
        
        if "gain" in query.lower() and "bandwidth" in query.lower():
            content = self._explain_gain_bandwidth_product()
        elif "stability" in query.lower() or "compensation" in query.lower():
            content = self._explain_stability_and_compensation()
        elif "noise" in query.lower():
            content = self._explain_noise_analysis()
        elif "offset" in query.lower():
            content = self._explain_offset_voltage()
        else:
            # Default comprehensive op-amp overview
            content = self._provide_comprehensive_overview()
        
        # Add practical design examples
        design_examples = self._generate_design_examples(application)
        
        # Include common mistakes and solutions
        common_pitfalls = self._identify_common_pitfalls()
        
        # Provide learning resources
        learning_resources = self._compile_learning_resources()
        
        return {
            "scenario": "Operational Amplifier Educational Analysis",
            "complexity_level": "Medium-Low",
            "target_model": "gpt_4o",
            "educational_content": {
                "topic_overview": educational_focus,
                "core_concepts": content,
                "practical_examples": design_examples,
                "common_pitfalls": common_pitfalls,
                "design_guidelines": self._generate_design_guidelines(),
                "learning_resources": learning_resources,
                "interactive_exercises": self._suggest_interactive_exercises()
            },
            "value_proposition": {
                "learning_acceleration": "Complex concepts explained with practical context",
                "mistake_prevention": "Common pitfalls identified before they occur",
                "practical_application": "Theory connected to real-world design scenarios",
                "progressive_learning": "Concepts build from basic to advanced systematically"
            }
        }
    
    def _explain_gain_bandwidth_product(self) -> Dict[str, Any]:
        """Comprehensive explanation of gain-bandwidth product concept"""
        
        return {
            "definition": {
                "concept": "Gain-Bandwidth Product (GBW) is the frequency at which the open-loop gain of an operational amplifier equals unity (1 or 0dB)",
                "mathematical_relationship": "GBW = Gain × Bandwidth = constant (for frequencies above the dominant pole)",
                "units": "Hz or MHz",
                "symbol": "GBW or ft"
            },
            "fundamental_principle": {
                "explanation": "Due to the single-pole rolloff characteristic of most op-amps, the product of gain and bandwidth remains constant",
                "mathematical_expression": "A(f) = GBW / f, where A(f) is gain at frequency f",
                "physical_meaning": "Higher gain circuits have proportionally lower bandwidth"
            },
            "practical_implications": {
                "design_trade_offs": [
                    "High gain (100x) → Low bandwidth (GBW/100)",
                    "Unity gain (1x) → Maximum bandwidth (= GBW)", 
                    "Low gain (10x) → Higher bandwidth (GBW/10)"
                ],
                "frequency_response": "Gain rolls off at -20dB/decade above the -3dB frequency"
            },
            "design_examples": [
                {
                    "application": "Audio Preamplifier",
                    "opamp": "LM358 (GBW = 1MHz)",
                    "required_gain": "40dB (100x)",
                    "resulting_bandwidth": "1MHz / 100 = 10kHz",
                    "analysis": "Adequate for audio frequencies (20Hz-20kHz)",
                    "design_notes": "Roll-off starts at 10kHz, -3dB point well above audio range"
                },
                {
                    "application": "Video Amplifier", 
                    "opamp": "LM318 (GBW = 15MHz)",
                    "required_gain": "20dB (10x)",
                    "resulting_bandwidth": "15MHz / 10 = 1.5MHz",
                    "analysis": "Suitable for video applications requiring ~6MHz bandwidth",
                    "design_notes": "Higher GBW op-amp needed for video frequencies"
                },
                {
                    "application": "Buffer Amplifier",
                    "opamp": "OPA602 (GBW = 20MHz)",
                    "required_gain": "0dB (1x)",
                    "resulting_bandwidth": "20MHz / 1 = 20MHz",
                    "analysis": "Maximum bandwidth achieved at unity gain",
                    "design_notes": "Ideal for high-frequency signal buffering"
                }
            ],
            "calculation_methodology": {
                "step_1": "Identify required gain: A_req = Vout/Vin",
                "step_2": "Find op-amp GBW from datasheet: typically in MHz",
                "step_3": "Calculate bandwidth: BW = GBW / A_req",
                "step_4": "Verify BW meets application requirements",
                "verification": "Ensure -3dB frequency > highest signal frequency"
            }
        }
    
    def _explain_stability_and_compensation(self) -> Dict[str, Any]:
        """Explain op-amp stability and compensation techniques"""
        
        return {
            "stability_fundamentals": {
                "definition": "Stability refers to an amplifier's ability to remain stable (not oscillate) under all operating conditions",
                "barkhausen_criterion": "Oscillation occurs when loop gain = 1 and phase shift = 180°",
                "phase_margin": "Amount of additional phase shift needed to reach instability threshold",
                "gain_margin": "Amount of additional gain needed to reach instability threshold"
            },
            "compensation_techniques": {
                "internal_compensation": {
                    "description": "Built-in compensation network within the op-amp",
                    "characteristics": "Single dominant pole, unity-gain stable",
                    "examples": ["LM741", "LM358", "TL071"],
                    "pros": "Simple to use, stable at all gains ≥1",
                    "cons": "Limited bandwidth, not optimized for specific applications"
                },
                "external_compensation": {
                    "description": "External components added to optimize stability",
                    "techniques": [
                        "Feedback capacitor (Cf) - Miller compensation",
                        "Input lag network - phase lead compensation", 
                        "Output snubber - high-frequency stability"
                    ],
                    "design_approach": "Tailor compensation for specific gain and bandwidth requirements"
                }
            },
            "practical_stability_guidelines": [
                "Maintain phase margin > 45° for good stability",
                "Keep gain margin > 6dB for robust design",
                "Minimize parasitic capacitances in high-gain circuits",
                "Use ground planes and proper layout for HF stability",
                "Add small capacitor (1-10pF) across feedback resistor if needed"
            ],
            "measurement_techniques": {
                "bode_plots": "Measure gain and phase vs frequency to assess stability",
                "step_response": "Look for overshoot and ringing in transient response",
                "load_testing": "Verify stability with various load impedances",
                "temperature_testing": "Ensure stability across operating temperature range"
            }
        }
    
    def _explain_noise_analysis(self) -> Dict[str, Any]:
        """Explain op-amp noise analysis and optimization"""
        
        return {
            "noise_sources": {
                "input_voltage_noise": {
                    "symbol": "en",
                    "units": "nV/√Hz",
                    "description": "Intrinsic voltage noise of the input stage",
                    "typical_values": "1-100 nV/√Hz depending on op-amp type"
                },
                "input_current_noise": {
                    "symbol": "in",
                    "units": "pA/√Hz",
                    "description": "Shot noise from input bias currents",
                    "typical_values": "0.1-100 pA/√Hz depending on input stage"
                },
                "thermal_noise": {
                    "description": "Johnson noise from resistors",
                    "formula": "en_R = √(4kTR × BW)",
                    "mitigation": "Use lower resistance values where possible"
                }
            },
            "noise_optimization_strategies": {
                "op_amp_selection": [
                    "Low en for low-impedance sources (< 1kΩ)",
                    "Low in for high-impedance sources (> 100kΩ)",
                    "Balanced en and in for moderate impedances"
                ],
                "circuit_design": [
                    "Minimize source resistance where possible",
                    "Use non-inverting configuration for higher input impedance",
                    "Match source impedances for differential inputs",
                    "Minimize bandwidth to required value only"
                ]
            },
            "noise_calculation_example": {
                "scenario": "Low-noise preamplifier design",
                "source_resistance": "1kΩ",
                "opamp_specs": {
                    "en": "4 nV/√Hz",
                    "in": "0.5 pA/√Hz"
                },
                "bandwidth": "10kHz",
                "calculations": {
                    "thermal_noise": "√(4 × 1.38e-23 × 300 × 1000) × √10000 = 0.4 µV",
                    "voltage_noise": "4e-9 × √10000 = 0.4 µV",
                    "current_noise": "0.5e-12 × 1000 × √10000 = 0.05 µV",
                    "total_noise": "√(0.4² + 0.4² + 0.05²) = 0.57 µV"
                }
            }
        }
    
    def _generate_design_examples(self, application: OpAmpApplication) -> List[Dict[str, Any]]:
        """Generate practical design examples based on application"""
        
        examples = []
        
        if application.circuit_type == "Non-inverting amplifier":
            examples.append({
                "circuit_name": "Non-Inverting Amplifier",
                "schematic_description": "Op-amp with feedback from output to inverting input",
                "gain_formula": "A = 1 + (Rf/Ri)",
                "input_impedance": "Very high (op-amp input impedance)",
                "output_impedance": "Very low (op-amp output impedance)",
                "design_procedure": [
                    "Calculate required feedback ratio: Rf/Ri = (Gain - 1)",
                    "Choose Ri value (typically 1kΩ - 10kΩ)",
                    "Calculate Rf = Ri × (Gain - 1)", 
                    "Verify bandwidth: BW = GBW / Gain",
                    "Check stability with chosen component values"
                ],
                "practical_example": {
                    "target_gain": f"{application.gain_requirement}x",
                    "ri_chosen": "1kΩ",
                    "rf_calculated": f"{(application.gain_requirement - 1) * 1000:.0f}Ω",
                    "standard_rf": f"{self._find_standard_resistor((application.gain_requirement - 1) * 1000)}Ω",
                    "actual_gain": f"{1 + self._find_standard_resistor((application.gain_requirement - 1) * 1000)/1000:.2f}x"
                }
            })
        
        # Add inverting amplifier example
        examples.append({
            "circuit_name": "Inverting Amplifier", 
            "schematic_description": "Input connected to inverting input through Ri, feedback from output",
            "gain_formula": "A = -Rf/Ri",
            "input_impedance": "Ri (input resistance)",
            "output_impedance": "Very low (op-amp output impedance)",
            "design_procedure": [
                "Choose input resistance Ri (affects input impedance)",
                "Calculate feedback resistance: Rf = |Gain| × Ri",
                "Verify bandwidth and stability",
                "Consider input bias current effects"
            ],
            "practical_example": {
                "target_gain": f"-{application.gain_requirement}x",
                "ri_chosen": "10kΩ",
                "rf_calculated": f"{application.gain_requirement * 10000:.0f}Ω",
                "input_impedance": "10kΩ",
                "notes": "Lower input impedance than non-inverting configuration"
            }
        })
        
        return examples
    
    def _identify_common_pitfalls(self) -> List[Dict[str, Any]]:
        """Identify common op-amp design mistakes and solutions"""
        
        return [
            {
                "pitfall": "Ignoring Gain-Bandwidth Limitations",
                "description": "Designing for high gain without considering bandwidth impact", 
                "consequences": ["Unexpected frequency response rolloff", "Reduced signal bandwidth", "Phase shifts in AC applications"],
                "solution": "Always verify BW = GBW/Gain meets requirements",
                "prevention": "Check op-amp GBW specification early in design"
            },
            {
                "pitfall": "Inadequate Power Supply Decoupling",
                "description": "Insufficient or improperly placed bypass capacitors",
                "consequences": ["Oscillation", "Power supply noise coupling", "Reduced PSRR performance"],
                "solution": "Use 0.1µF ceramic + 10µF tantalum close to op-amp pins",
                "prevention": "Follow manufacturer's PCB layout guidelines"
            },
            {
                "pitfall": "Input Bias Current Effects",
                "description": "Not accounting for input bias currents in high-impedance circuits",
                "consequences": ["DC offset voltages", "Drift with temperature", "Reduced accuracy"],
                "solution": "Use bias current compensation resistor or FET-input op-amps",
                "prevention": "Calculate worst-case offset: Vos = Ib × Rs"
            },
            {
                "pitfall": "Slew Rate Limitations",
                "description": "Exceeding op-amp slew rate capability",
                "consequences": ["Signal distortion", "Reduced bandwidth", "Non-linear behavior"],
                "solution": "Verify SR > 2π × f × Vpk for sinusoidal signals",
                "prevention": "Check slew rate specification for large signal swings"
            },
            {
                "pitfall": "Phase Margin Issues",
                "description": "Insufficient phase margin causing instability",
                "consequences": ["Oscillation", "Overshoot and ringing", "Poor transient response"],
                "solution": "Add compensation capacitor across feedback resistor",
                "prevention": "Maintain phase margin > 45° in closed-loop design"
            }
        ]
    
    def _generate_design_guidelines(self) -> Dict[str, List[str]]:
        """Generate comprehensive op-amp design guidelines"""
        
        return {
            "component_selection": [
                "Choose GBW at least 10× required bandwidth for good phase margin",
                "Select slew rate > 2π × fmax × Vout_max",
                "Consider input bias current for high-impedance applications",
                "Verify common-mode input range includes signal levels"
            ],
            "circuit_design": [
                "Keep feedback loop physically short to minimize parasitic capacitance",
                "Use non-inverting configuration for high input impedance",
                "Include bias current compensation in high-impedance circuits",
                "Consider input protection for robust design"
            ],
            "pcb_layout": [
                "Place bypass capacitors close to power supply pins",
                "Use ground plane for stable reference",
                "Keep input traces short and shielded if necessary",
                "Separate analog and digital ground systems"
            ],
            "testing_validation": [
                "Measure frequency response to verify bandwidth",
                "Test with maximum expected signal levels",
                "Verify stability across temperature range",
                "Check performance with intended load impedance"
            ]
        }
    
    def _compile_learning_resources(self) -> Dict[str, List[str]]:
        """Compile comprehensive learning resources for op-amp design"""
        
        return {
            "textbooks": [
                "The Art of Electronics - Horowitz & Hill (Chapter 4: Operational Amplifiers)",
                "Op Amps for Everyone - Texas Instruments (Free PDF)",
                "Design with Operational Amplifiers - Franco",
                "Analog Circuit Design - Sansen"
            ],
            "application_notes": [
                "AN-31: Op Amp Circuit Collection - National Semiconductor",
                "SLOA011: Understanding Operational Amplifier Parameters - TI", 
                "AN-20: An Applications Guide for Op Amps - National",
                "SLOA024: Fully-Differential Amplifiers - Texas Instruments"
            ],
            "online_resources": [
                "Analog Devices Circuit Design Tools and Calculators",
                "Texas Instruments Precision Labs - Op Amp Series",
                "MIT OpenCourseWare: Circuits and Electronics",
                "All About Circuits - Operational Amplifier Tutorial"
            ],
            "simulation_tools": [
                "SPICE simulation exercises with LTSpice (free)",
                "Analog Devices ADIsimPE Circuit Simulator",
                "Texas Instruments TINA Circuit Simulator", 
                "Multisim Educational Edition for interactive learning"
            ],
            "hands_on_learning": [
                "Build breadboard circuits with common op-amps (LM741, LM358)",
                "Use oscilloscope to measure frequency response",
                "Experiment with different feedback configurations",
                "Measure noise performance with spectrum analyzer"
            ]
        }
    
    def _suggest_interactive_exercises(self) -> List[Dict[str, Any]]:
        """Suggest hands-on exercises for reinforced learning"""
        
        return [
            {
                "exercise": "GBW Measurement Lab",
                "objective": "Measure gain-bandwidth product of common op-amps",
                "components": ["LM741", "LM358", "TL071", "Function generator", "Oscilloscope"],
                "procedure": [
                    "Build non-inverting amplifier with gain = 10",
                    "Sweep frequency from 100Hz to 1MHz",
                    "Record gain vs frequency", 
                    "Calculate GBW from -3dB frequency",
                    "Compare with datasheet specifications"
                ],
                "learning_outcomes": "Understand practical GBW limitations and measurement techniques"
            },
            {
                "exercise": "Stability Investigation",
                "objective": "Observe stability effects of different compensation methods",
                "components": ["High-speed op-amp", "Various capacitors", "Square wave generator"],
                "procedure": [
                    "Build unity-gain buffer without compensation",
                    "Observe step response for overshoot/ringing",
                    "Add small feedback capacitor (1-10pF)",
                    "Compare step responses",
                    "Measure phase margin if possible"
                ],
                "learning_outcomes": "Practical understanding of stability and compensation effects"
            },
            {
                "exercise": "Noise Measurement Workshop",
                "objective": "Measure and compare noise performance of different op-amps",
                "components": ["Low-noise op-amp", "General-purpose op-amp", "Spectrum analyzer", "Low-noise resistors"],
                "procedure": [
                    "Build identical gain circuits with different op-amps",
                    "Measure output noise with spectrum analyzer",
                    "Calculate input-referred noise",
                    "Compare with theoretical calculations",
                    "Investigate effect of source resistance"
                ],
                "learning_outcomes": "Practical noise analysis and measurement skills"
            }
        ]
    
    def _determine_educational_focus(self, query: str) -> str:
        """Determine the main educational focus from the query"""
        query_lower = query.lower()
        
        if "gain" in query_lower and "bandwidth" in query_lower:
            return "Gain-Bandwidth Product Analysis"
        elif "stability" in query_lower:
            return "Stability and Compensation"
        elif "noise" in query_lower:
            return "Noise Analysis and Optimization"
        elif "offset" in query_lower:
            return "Input Offset and Bias Effects"
        else:
            return "Comprehensive Op-Amp Design Fundamentals"
    
    def _load_common_opamps(self) -> Dict[str, Dict]:
        """Load specifications for common operational amplifiers"""
        
        return {
            "LM741": {
                "gbw": 1.0e6,  # Hz
                "slew_rate": 0.5e6,  # V/s
                "input_bias_current": 80e-9,  # A
                "input_offset_voltage": 1e-3  # V
            },
            "LM358": {
                "gbw": 1.0e6,
                "slew_rate": 0.3e6, 
                "input_bias_current": 45e-9,
                "input_offset_voltage": 2e-3
            },
            "TL071": {
                "gbw": 3.0e6,
                "slew_rate": 13e6,
                "input_bias_current": 65e-12,
                "input_offset_voltage": 3e-3
            }
        }
    
    def _find_standard_resistor(self, target_value: float) -> float:
        """Find closest standard resistor value"""
        # E12 series standard values
        e12_values = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
        
        # Find appropriate decade
        decade = 10 ** int(math.log10(target_value))
        normalized = target_value / decade
        
        # Find closest E12 value
        closest = min(e12_values, key=lambda x: abs(x - normalized))
        
        return closest * decade
