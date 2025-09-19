"""
Model-specific routing criteria and rules
"""
from typing import Dict, List, Set

class ModelRoutingRules:
    """Encapsulates routing rules for each AI model"""
    
    CLAUDE_SONNET_4 = {
        "name": "claude-sonnet-4",
        "complexity_threshold": 0.8,
        "optimal_intents": {
            "compliance_checking", "design_validation", "signal_integrity", 
            "thermal_analysis"
        },
        "optimal_domains": {"automotive", "medical", "analog_rf", "power_electronics"},
        "key_indicators": [
            "AEC-Q100", "ISO 26262", "IEC 60601", "safety-critical", "compliance",
            "functional safety", "ASIL", "medical grade", "automotive grade"
        ],
        "description": "Complex hardware analysis requiring deep domain expertise"
    }
    
    GROK_2 = {
        "name": "grok-2", 
        "complexity_range": (0.6, 0.8),
        "optimal_intents": {
            "component_selection", "cost_optimization", "lifecycle_management"
        },
        "optimal_domains": {"embedded_hardware", "consumer", "industrial"},
        "key_indicators": [
            "compare", "alternative", "cost", "price", "selection", "recommendation",
            "trade-off", "evaluation", "sourcing", "supplier"
        ],
        "description": "Component selection and trade-off analysis"
    }
    
    GPT_4O = {
        "name": "gpt-4o",
        "complexity_range": (0.4, 0.7),
        "optimal_intents": {
            "educational_content", "circuit_analysis", "troubleshooting"
        },
        "optimal_domains": {"digital_design", "embedded_hardware", "analog_rf"},
        "key_indicators": [
            "explain", "how does", "what is", "principle", "concept", "theory",
            "learning", "tutorial", "guide", "understanding"
        ],
        "description": "General hardware engineering knowledge and education"
    }
    
    GPT_4O_MINI = {
        "name": "gpt-4o-mini",
        "complexity_threshold": 0.4,  # Below this threshold
        "optimal_intents": {"educational_content"},
        "optimal_domains": set(),  # Works for any domain for simple queries
        "key_indicators": [
            "specification", "datasheet", "parameter", "value", "lookup",
            "what is the", "pin", "package", "voltage", "current", "simple"
        ],
        "description": "Simple specification lookups and basic information retrieval"
    }

    @classmethod
    def get_all_models(cls) -> Dict[str, Dict]:
        """Get all model configurations"""
        return {
            "claude_sonnet_4": cls.CLAUDE_SONNET_4,
            "grok_2": cls.GROK_2, 
            "gpt_4o": cls.GPT_4O,
            "gpt_4o_mini": cls.GPT_4O_MINI
        }
