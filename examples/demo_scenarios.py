"""
Demo scenarios from the assignment - test queries for validation
"""

DEMO_SCENARIOS = {
    "scenario_1_buck_converter": {
        "description": "Automotive Buck Converter Design (High Complexity → Claude Sonnet 4)",
        "query": "I need to design a buck converter for automotive ECU application, 12V to 5V conversion at 3A output current. It must be AEC-Q100 qualified and meet ISO 26262 ASIL-B requirements for functional safety. Need thermal analysis for -40°C to +125°C temperature range and EMC compliance for automotive standards.",
        "expected_model": "claude_sonnet_4",
        "expected_complexity": ">= 0.8",
        "expected_intent": "compliance_checking",
        "expected_domain": "automotive"
    },
    
    "scenario_2_mcu_selection": {
        "description": "IoT Microcontroller Selection (Medium Complexity → Grok-2)",
        "query": "Compare ARM Cortex-M4 microcontrollers for IoT application requiring ultra-low power consumption, integrated WiFi connectivity, and cost optimization for 10K volume production. Need trade-off analysis between STM32, ESP32, and Nordic nRF series.",
        "expected_model": "grok_2",
        "expected_complexity": "0.6-0.8",
        "expected_intent": "component_selection", 
        "expected_domain": "embedded_hardware"
    },
    
    "scenario_3_opamp_analysis": {
        "description": "Op-Amp Circuit Analysis (Medium-Low Complexity → GPT-4o)",
        "query": "Explain the gain-bandwidth product limitations in operational amplifier circuits. How does it affect circuit design and what are the trade-offs between gain and frequency response? Provide practical design examples.",
        "expected_model": "gpt_4o",
        "expected_complexity": "0.4-0.7",
        "expected_intent": "educational_content",
        "expected_domain": "analog_rf"
    },
    
    "scenario_4_spec_lookup": {
        "description": "Component Specification Lookup (Low Complexity → GPT-4o-mini)",
        "query": "What are the key specifications of LM317 voltage regulator? Show operating voltage range, output current, and package options.",
        "expected_model": "gpt_4o_mini", 
        "expected_complexity": "< 0.4",
        "expected_intent": "educational_content",
        "expected_domain": "power_electronics"
    }
}

# Additional test queries for comprehensive validation
ADDITIONAL_TEST_QUERIES = [
    # Intent Classification Tests
    {
        "query": "Calculate thermal resistance for heat sink in 50W power amplifier design",
        "expected_intent": "thermal_analysis",
        "expected_domain": "power_electronics"
    },
    {
        "query": "Debug oscilloscope measurement showing signal integrity issues on high-speed digital bus",
        "expected_intent": "troubleshooting", 
        "expected_domain": "digital_design"
    },
    {
        "query": "Verify IEC 60601 leakage current compliance for medical device power supply",
        "expected_intent": "compliance_checking",
        "expected_domain": "medical"
    },
    
    # Domain Detection Tests
    {
        "query": "Industrial PLC interface design with galvanic isolation and noise immunity",
        "expected_domain": "industrial"
    },
    {
        "query": "Consumer wearable device battery optimization for extended runtime",
        "expected_domain": "consumer"
    },
    {
        "query": "RF mixer design for 2.4GHz frequency conversion with low phase noise",
        "expected_domain": "analog_rf"
    }
]
