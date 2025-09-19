"""
8 Major Hardware Engineering Domains with scope and expertise areas
"""

HARDWARE_DOMAINS = {
    "power_electronics": {
        "scope": ["Buck/boost converters", "LDOs", "switching regulators", "power management ICs"],
        "expertise_areas": ["Efficiency optimization", "thermal management", "ripple analysis", "EMI considerations"],
        "keywords": [
            "power", "voltage regulator", "buck", "boost", "switching", "LDO", "linear regulator",
            "SMPS", "power management", "PMIC", "efficiency", "ripple", "inductor", "capacitor",
            "power supply", "DC-DC", "AC-DC", "converter", "regulator", "power stage"
        ],
        "complexity_weight": 1.2
    },
    "analog_rf": {
        "scope": ["Op-amps", "filters", "signal conditioning", "RF circuits", "mixed-signal design"],
        "expertise_areas": ["Frequency response analysis", "noise characterization", "bandwidth optimization"],
        "keywords": [
            "analog", "op-amp", "operational amplifier", "filter", "active filter", "passive filter",
            "RF", "radio frequency", "mixer", "amplifier", "VGA", "PGA", "ADC", "DAC",
            "signal conditioning", "instrumentation amplifier", "comparator", "reference"
        ],
        "complexity_weight": 1.3
    },
    "digital_design": {
        "scope": ["Microcontrollers", "FPGAs", "logic circuits", "digital signal processing"],
        "expertise_areas": ["Timing analysis", "resource utilization", "power consumption optimization"],
        "keywords": [
            "digital", "microcontroller", "MCU", "FPGA", "logic", "gate", "flip-flop", "counter",
            "state machine", "DSP", "digital signal processing", "VHDL", "Verilog", "timing",
            "clock", "reset", "GPIO", "peripheral", "interrupt", "memory", "CPU"
        ],
        "complexity_weight": 1.1
    },
    "embedded_hardware": {
        "scope": ["MCU selection", "peripheral interfaces", "system integration", "real-time constraints"],
        "expertise_areas": ["Hardware-software co-design", "interrupt handling", "communication protocols"],
        "keywords": [
            "embedded", "microcontroller", "MCU", "peripheral", "interface", "communication",
            "UART", "SPI", "I2C", "CAN", "USB", "Ethernet", "WiFi", "Bluetooth", "real-time",
            "RTOS", "interrupt", "DMA", "timer", "PWM", "system integration"
        ],
        "complexity_weight": 1.0
    },
    "automotive": {
        "scope": ["AEC-Q100 qualified components", "ISO 26262 functional safety", "EMC compliance"],
        "expertise_areas": ["Temperature cycling", "vibration resistance", "functional safety requirements"],
        "keywords": [
            "automotive", "AEC-Q100", "ISO 26262", "functional safety", "ASIL", "ECU",
            "CAN bus", "LIN", "FlexRay", "temperature cycling", "vibration", "EMC", "EMI",
            "automotive grade", "under hood", "passenger compartment", "engine compartment"
        ],
        "complexity_weight": 1.4
    },
    "industrial": {
        "scope": ["Motor drives", "industrial sensors", "PLC interfaces", "industrial communication protocols"],
        "expertise_areas": ["Noise immunity", "temperature range requirements", "reliability standards"],
        "keywords": [
            "industrial", "motor drive", "PLC", "sensor", "actuator", "industrial automation",
            "Modbus", "Profibus", "EtherCAT", "4-20mA", "isolated", "isolation", "galvanic isolation",
            "noise immunity", "industrial grade", "temperature range", "reliability"
        ],
        "complexity_weight": 1.2
    },
    "medical": {
        "scope": ["IEC 60601 compliance", "biocompatibility", "patient safety isolation"],
        "expertise_areas": ["Leakage current limits", "isolation requirements", "sterilization compatibility"],
        "keywords": [
            "medical", "IEC 60601", "biocompatibility", "patient safety", "isolation", "leakage current",
            "medical grade", "sterilization", "biomedical", "healthcare", "diagnostic", "therapeutic",
            "patient applied part", "defibrillation", "medical electrical equipment"
        ],
        "complexity_weight": 1.5
    },
    "consumer": {
        "scope": ["Cost optimization", "miniaturization", "battery life extension", "user experience"],
        "expertise_areas": ["Power efficiency", "form factor constraints", "manufacturing scalability"],
        "keywords": [
            "consumer", "battery", "portable", "mobile", "wearable", "IoT", "cost", "low power",
            "miniaturization", "form factor", "user experience", "UI", "touch", "display",
            "wireless", "charging", "energy harvesting", "mass production"
        ],
        "complexity_weight": 0.8
    }
}
