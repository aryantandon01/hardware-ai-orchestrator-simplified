"""
Intelligent Model Router
Routes queries to optimal AI model based on complexity, intent, and domain
"""
from typing import Dict, List, Tuple, Optional
import re
from .routing_rules import ModelRoutingRules
from ..config.complexity_weights import COMPLEXITY_THRESHOLDS

class ModelRouter:
    def __init__(self):
        self.models = ModelRoutingRules.get_all_models()
        self.thresholds = COMPLEXITY_THRESHOLDS
        self._compile_indicator_patterns()
    
    def _compile_indicator_patterns(self):
        """Compile regex patterns for key indicators"""
        self.indicator_patterns = {}
        for model_name, config in self.models.items():
            indicators = config.get("key_indicators", [])
            if indicators:
                pattern = r'\b(' + '|'.join(re.escape(ind) for ind in indicators) + r')\b'
                self.indicator_patterns[model_name] = re.compile(pattern, re.IGNORECASE)
    
    def select_model(self, 
                    complexity_score: float,
                    primary_intent: str, 
                    primary_domain: str,
                    query: str) -> Dict[str, any]:
        """
        Select optimal AI model based on query characteristics
        Returns model selection with confidence and reasoning
        """
        model_scores = {}
        
        # Score each model based on multiple factors
        for model_name, config in self.models.items():
            score = 0.0
            reasons = []
            
            # 1. Complexity Score Matching (40% weight)
            complexity_match = self._calculate_complexity_match(complexity_score, config)
            score += complexity_match * 0.6
            if complexity_match > 0.5:
                reasons.append(f"Complexity match: {complexity_match:.2f}")
            
            # 2. Intent Alignment (25% weight) 
            intent_match = self._calculate_intent_match(primary_intent, config)
            score += intent_match * 0.2
            if intent_match > 0.5:
                reasons.append(f"Intent alignment: {intent_match:.2f}")
            
            # 3. Domain Specialization (20% weight)
            domain_match = self._calculate_domain_match(primary_domain, config)
            score += domain_match * 0.15
            if domain_match > 0.5:
                reasons.append(f"Domain specialization: {domain_match:.2f}")
            
            # 4. Key Indicator Presence (15% weight)
            indicator_match = self._calculate_indicator_match(query, model_name, config)
            score += indicator_match * 0.05
            if indicator_match > 0.5:
                reasons.append(f"Key indicators present: {indicator_match:.2f}")
            
            model_scores[model_name] = {
                "score": score,
                "reasons": reasons,
                "config": config
            }
        
        # Select highest scoring model
        best_model = max(model_scores.items(), key=lambda x: x[1]["score"])
        selected_model, selection_data = best_model
        
        # Fallback logic for edge cases
        if selection_data["score"] < 0.3:
            selected_model = self._apply_fallback_logic(complexity_score)
            selection_data["reasons"].append("Applied fallback logic due to low confidence")
        
        return {
            "selected_model": selected_model,
            "confidence": selection_data["score"],
            "reasoning": selection_data["reasons"],
            "all_scores": {k: v["score"] for k, v in model_scores.items()},
            "complexity_score": complexity_score
        }
    
    def _calculate_complexity_match(self, complexity: float, config: Dict) -> float:
        """Calculate complexity match with STRICT thresholds per assignment requirements"""
        if "complexity_threshold" in config:
            threshold = config["complexity_threshold"]
            if config["name"] == "claude-sonnet-4":
                # Claude: ONLY for complexity >= 0.8, zero score otherwise
                return 1.0 if complexity >= threshold else 0.0
            else:
                # GPT-4o-mini: ONLY for complexity < 0.4, zero score otherwise  
                return 1.0 if complexity < threshold else 0.0
        
        elif "complexity_range" in config:
            # Models with range (Grok-2, GPT-4o): STRICT range enforcement
            min_c, max_c = config["complexity_range"]
            return 1.0 if min_c <= complexity <= max_c else 0.0
        
        return 0.0  # No partial credit for anything outside thresholds
    
    def _calculate_intent_match(self, intent: str, config: Dict) -> float:
        """Calculate intent alignment with model's optimal intents"""
        optimal_intents = config.get("optimal_intents", set())
        if not optimal_intents:
            return 0.5  # Neutral if no specific intents
        
        return 1.0 if intent in optimal_intents else 0.2
    
    def _calculate_domain_match(self, domain: str, config: Dict) -> float:
        """Calculate domain specialization match"""
        optimal_domains = config.get("optimal_domains", set())
        if not optimal_domains:
            return 0.5  # Neutral if no domain specialization
        
        return 1.0 if domain in optimal_domains else 0.3
    
    def _calculate_indicator_match(self, query: str, model_name: str, config: Dict) -> float:
        """Calculate key indicator presence"""
        if model_name not in self.indicator_patterns:
            return 0.5  # Neutral if no indicators defined
        
        pattern = self.indicator_patterns[model_name]
        matches = len(pattern.findall(query))
        return min(matches * 0.3, 1.0)
    
    def _apply_fallback_logic(self, complexity: float) -> str:
        """Apply fallback routing logic for edge cases"""
        if complexity >= 0.8:
            return "claude_sonnet_4"
        elif complexity >= 0.6:
            return "gpt_4o"  # Fallback if Grok-2 not available
        elif complexity >= 0.4:
            return "gpt_4o"
        else:
            return "gpt_4o_mini"
