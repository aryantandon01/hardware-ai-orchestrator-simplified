"""
Hardware Query Intent Classification
Recognizes 12 distinct hardware engineering intent categories
"""
from typing import Dict, List, Tuple, Any
import re
from ..config.intent_categories import INTENT_CATEGORIES

class HardwareIntentClassifier:
    def __init__(self):
        self.intent_categories = INTENT_CATEGORIES
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        self.patterns = {}
        for intent, config in self.intent_categories.items():
            # Create regex pattern from keywords
            keywords = config["keywords"]
            pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            self.patterns[intent] = re.compile(pattern, re.IGNORECASE)
    
    def classify_intent(self, query: str) -> Dict[str, float]:
        """
        Classify query intent across all 12 categories
        Returns confidence scores for each intent
        """
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, pattern in self.patterns.items():
            # Count keyword matches
            matches = pattern.findall(query)
            keyword_count = len(matches)
            
            # Calculate base score from keyword density
            base_score = min(keyword_count * 0.2, 1.0)
            
            # Boost score for complexity indicators
            complexity_indicators = self.intent_categories[intent]["complexity_indicators"]
            for indicator in complexity_indicators:
                if indicator in query_lower:
                    base_score += 0.1
            
            # Apply base complexity modifier
            base_complexity = self.intent_categories[intent]["base_complexity"]
            final_score = base_score * base_complexity
            
            intent_scores[intent] = min(final_score, 1.0)
        
        return intent_scores
    
    def classify_multiple_intents(self, query: str) -> Dict[str, Any]:
        """Enhanced intent classifier supporting multiple concurrent intents"""
        intents = self.classify_intent(query)
        
        # Identify queries with multiple intents
        active_intents = {k: v for k, v in intents.items() if v > 0.4}
        
        return {
            "primary_intents": active_intents,
            "intent_combination": self._detect_intent_patterns(active_intents)
        }
    
    def _detect_intent_patterns(self, active_intents: Dict[str, float]) -> str:
        """Detect common multi-intent patterns in hardware queries"""
        # Component selection + Compliance checking
        if ("component_selection" in active_intents and 
            "compliance_checking" in active_intents):
            return "component_selection_and_compliance"
        
        # Circuit analysis + Thermal analysis  
        if ("circuit_analysis" in active_intents and 
            "thermal_analysis" in active_intents):
            return "circuit_analysis_and_thermal"
        
        # Component selection + Cost optimization
        if ("component_selection" in active_intents and 
            "cost_optimization" in active_intents):
            return "component_selection_and_cost"
        
        # Design validation + Compliance checking
        if ("design_validation" in active_intents and 
            "compliance_checking" in active_intents):
            return "design_validation_and_compliance"
        
        # Default: multiple intents without specific pattern
        if len(active_intents) > 1:
            return "multiple_intents"
        
        return "single_intent"
    
    def get_primary_intent(self, query: str) -> Tuple[str, float]:
        """Get the highest-confidence intent classification"""
        intent_scores = self.classify_intent(query)
        
        if not intent_scores:
            return "educational_content", 0.3  # Default fallback
        
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        return primary_intent
    
    def get_intent_description(self, intent: str) -> str:
        """Get human-readable description of an intent category"""
        return self.intent_categories.get(intent, {}).get("description", "Unknown intent")
