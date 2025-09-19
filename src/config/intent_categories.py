"""
12 Hardware Engineering Intent Categories with keywords and complexity indicators
"""

INTENT_CATEGORIES = {
    "component_selection": {
        "description": "Microcontroller evaluation, power IC comparison, sensor selection criteria",
        "keywords": [
            "microcontroller", "MCU", "power IC", "sensor", "compare", "select", "evaluation", 
            "choice", "recommendation", "alternative", "substitute", "equivalent", "better than",
            "ARM Cortex", "RISC-V", "PIC", "AVR", "ESP32", "STM32", "voltage regulator", "LDO"
        ],
        "complexity_indicators": ["trade-off", "optimization", "performance comparison", "specification"],
        "base_complexity": 0.5
    },
    "circuit_analysis": {
        "description": "Buck converter design optimization, op-amp configuration analysis, filter topology selection",
        "keywords": [
            "circuit", "design", "analysis", "buck converter", "boost", "op-amp", "operational amplifier",
            "filter", "topology", "schematic", "configuration", "optimization", "gain", "frequency response",
            "bandwidth", "stability", "feedback", "compensation", "noise", "distortion"
        ],
        "complexity_indicators": ["mathematical", "calculation", "simulation", "optimization", "analysis"],
        "base_complexity": 0.6
    },
    "thermal_analysis": {
        "description": "Heat sink calculations, power dissipation modeling, thermal resistance analysis",
        "keywords": [
            "thermal", "heat sink", "temperature", "power dissipation", "thermal resistance", 
            "junction temperature", "ambient", "cooling", "thermal management", "heat transfer",
            "thermal pad", "thermal interface", "TIM", "airflow", "convection", "conduction"
        ],
        "complexity_indicators": ["calculation", "modeling", "simulation", "thermal analysis"],
        "base_complexity": 0.7
    },
    "signal_integrity": {
        "description": "Impedance matching, crosstalk mitigation, EMI suppression techniques",
        "keywords": [
            "impedance", "matching", "crosstalk", "EMI", "EMC", "signal integrity", "transmission line",
            "reflection", "ringing", "overshoot", "undershoot", "ground plane", "via", "routing",
            "differential", "single-ended", "noise", "interference", "shielding", "filtering"
        ],
        "complexity_indicators": ["high-frequency", "RF", "transmission line", "electromagnetic"],
        "base_complexity": 0.8
    },
    "compliance_checking": {
        "description": "AEC-Q100 verification, EMC standards adherence, safety regulation compliance",
        "keywords": [
            "compliance", "AEC-Q100", "ISO 26262", "IEC 60601", "EMC", "safety", "regulation",
            "standard", "certification", "qualification", "automotive", "medical", "functional safety",
            "ASIL", "SIL", "risk assessment", "hazard analysis", "verification", "validation"
        ],
        "complexity_indicators": ["safety-critical", "certification", "standards", "compliance"],
        "base_complexity": 0.9
    },
    "design_validation": {
        "description": "Design review protocols, margin analysis, worst-case scenario evaluation",
        "keywords": [
            "validation", "verification", "design review", "margin analysis", "worst-case", 
            "Monte Carlo", "sensitivity analysis", "tolerance", "reliability", "MTBF", "MTTF",
            "failure rate", "derating", "stress analysis", "corner analysis", "process variation"
        ],
        "complexity_indicators": ["statistical", "analysis", "modeling", "validation"],
        "base_complexity": 0.8
    },
    "cost_optimization": {
        "description": "BOM cost reduction strategies, alternative component sourcing, volume pricing analysis",
        "keywords": [
            "cost", "BOM", "price", "budget", "optimization", "reduction", "sourcing", "supplier",
            "volume", "quantity", "pricing", "alternative", "cheaper", "lower cost", "value engineering",
            "cost analysis", "total cost", "lifecycle cost", "procurement"
        ],
        "complexity_indicators": ["analysis", "optimization", "trade-off"],
        "base_complexity": 0.4
    },
    "lifecycle_management": {
        "description": "Obsolescence monitoring, long-term availability assessment, migration pathway planning",
        "keywords": [
            "obsolescence", "end-of-life", "EOL", "lifecycle", "availability", "long-term", 
            "migration", "replacement", "upgrade", "roadmap", "future", "sustainability",
            "supply chain", "risk", "continuity", "legacy", "maintenance"
        ],
        "complexity_indicators": ["planning", "strategy", "long-term"],
        "base_complexity": 0.5
    },
    "troubleshooting": {
        "description": "Failure mode analysis, measurement interpretation, debug methodology",
        "keywords": [
            "troubleshooting", "debug", "failure", "problem", "issue", "error", "fault",
            "diagnosis", "root cause", "FMEA", "failure mode", "measurement", "oscilloscope",
            "multimeter", "spectrum analyzer", "logic analyzer", "not working", "broken"
        ],
        "complexity_indicators": ["analysis", "diagnosis", "systematic"],
        "base_complexity": 0.6
    },
    "educational_content": {
        "description": "Circuit principle explanations, component fundamentals, design methodology guidance",
        "keywords": [
            "explain", "how does", "what is", "principle", "fundamental", "basic", "theory",
            "concept", "learning", "tutorial", "guide", "methodology", "approach", "technique",
            "understanding", "clarification", "definition", "example", "demonstration"
        ],
        "complexity_indicators": ["explanation", "fundamental", "concept"],
        "base_complexity": 0.3
    }
}
