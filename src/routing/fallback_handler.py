"""
Fallback mechanisms for edge cases and error handling
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FallbackHandler:
    """Handles edge cases and provides fallback routing strategies"""
    
    def __init__(self):
        self.fallback_priority = [
            "gpt_4o",      # Most reliable fallback
            "gpt_4o_mini", # Fast and cost-effective
            "claude_sonnet_4",  # High-quality but expensive
            "grok_2"       # Least priority due to potential availability
        ]
    
    def handle_routing_failure(self, 
                             query: str, 
                             complexity: float, 
                             error: Exception) -> Dict[str, any]:
        """Handle cases where primary routing fails"""
        logger.warning(f"Routing failure for query: {query[:50]}... Error: {error}")
        
        # Simple complexity-based fallback
        if complexity >= 0.7:
            fallback_model = "claude_sonnet_4"
            reason = "High complexity query, using premium model"
        elif complexity <= 0.3:
            fallback_model = "gpt_4o_mini"
            reason = "Simple query, using efficient model"
        else:
            fallback_model = "gpt_4o"
            reason = "Medium complexity, using reliable model"
        
        return {
            "selected_model": fallback_model,
            "confidence": 0.5,  # Medium confidence for fallback
            "reasoning": [reason, f"Fallback due to: {str(error)}"],
            "is_fallback": True
        }
    
    def handle_model_unavailable(self, 
                                unavailable_model: str, 
                                original_selection: Dict) -> str:
        """Handle cases where selected model is unavailable"""
        logger.warning(f"Model {unavailable_model} unavailable, selecting alternative")
        
        complexity = original_selection.get("complexity_score", 0.5)
        
        # Remove unavailable model from priority list
        available_models = [m for m in self.fallback_priority if m != unavailable_model]
        
        # Select based on complexity and availability
        if complexity >= 0.8 and "claude_sonnet_4" in available_models:
            return "claude_sonnet_4"
        elif complexity >= 0.4 and "gpt_4o" in available_models:
            return "gpt_4o"
        else:
            return available_models[0] if available_models else "gpt_4o_mini"
