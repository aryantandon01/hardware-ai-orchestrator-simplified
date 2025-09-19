"""
Query Analyzer - Orchestrates all classification components
"""
from typing import Dict, Any
import logging
from .intent_classifier import HardwareIntentClassifier
from .domain_detector import HardwareDomainDetector
from .complexity_scorer import HardwareComplexityScorer
from ..routing.model_router import ModelRouter
from ..routing.fallback_handler import FallbackHandler

logger = logging.getLogger(__name__)

class HardwareQueryAnalyzer:
    """Main orchestrator for hardware query analysis and routing"""
    
    def __init__(self):
        self.intent_classifier = HardwareIntentClassifier()
        self.domain_detector = HardwareDomainDetector()
        self.complexity_scorer = HardwareComplexityScorer()
        self.model_router = ModelRouter()
        self.fallback_handler = FallbackHandler()
    
    def analyze_query(self, query: str, enable_multi_intent: bool = False) -> Dict[str, Any]:
        """
        Complete analysis of hardware engineering query with optional multi-intent support
        Returns classification, complexity, and routing decision
        """
        try:
            logger.info(f"Analyzing query: {query[:100]}...")
            
            # Step 1: Intent Classification (Enhanced)
            if enable_multi_intent:
                # Use enhanced multi-intent classification
                intent_analysis = self.intent_classifier.classify_multiple_intents(query)
                active_intents = intent_analysis.get("primary_intents", {})
                
                # Extract primary intent from multi-intent analysis
                if active_intents:
                    primary_intent = max(active_intents, key=active_intents.get)
                    intent_confidence = active_intents[primary_intent]
                else:
                    # Fallback to single intent if no active intents found
                    primary_intent, intent_confidence = self.intent_classifier.get_primary_intent(query)
                
                # Use multi-intent analysis as all_intents
                all_intents = intent_analysis
                intent_combination = intent_analysis.get("intent_combination", "single_intent")
            else:
                # Use existing single-intent classification
                primary_intent, intent_confidence = self.intent_classifier.get_primary_intent(query)
                all_intents = self.intent_classifier.classify_intent(query)
                intent_combination = "single_intent"
            
            # Step 2: Domain Detection  
            primary_domain, domain_confidence = self.domain_detector.get_primary_domain(query)
            all_domains = self.domain_detector.detect_domains(query)
            
            # Step 3: Complexity Scoring
            complexity_analysis = self.complexity_scorer.calculate_complexity(
                query, primary_domain, primary_intent
            )
            
            # Step 4: Model Routing
            routing_decision = self.model_router.select_model(
                complexity_analysis["final_score"],
                primary_intent,
                primary_domain, 
                query
            )
            
            # Compile complete analysis
            analysis = {
                "query": query,
                "classification": {
                    "primary_intent": {
                        "intent": primary_intent,
                        "confidence": intent_confidence,
                        "description": self.intent_classifier.get_intent_description(primary_intent)
                    },
                    "all_intents": all_intents,
                    "primary_domain": {
                        "domain": primary_domain,
                        "confidence": domain_confidence,
                        "info": self.domain_detector.get_domain_info(primary_domain)
                    },
                    "all_domains": all_domains
                },
                "complexity": complexity_analysis,
                "routing": routing_decision,
                "analysis_metadata": {
                    "timestamp": self._get_timestamp(),
                    "version": "1.0.0",
                    "multi_intent_enabled": enable_multi_intent,
                    "intent_combination": intent_combination if enable_multi_intent else "single_intent"
                }
            }
            
            logger.info(f"Analysis complete - Intent: {primary_intent}, Domain: {primary_domain}, "
                       f"Complexity: {complexity_analysis['final_score']:.3f}, "
                       f"Model: {routing_decision['selected_model']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return self._handle_analysis_failure(query, e)

    def _handle_analysis_failure(self, query: str, error: Exception) -> Dict[str, Any]:
        """Handle analysis failures with graceful fallback"""
        fallback_routing = self.fallback_handler.handle_routing_failure(query, 0.5, error)
        
        return {
            "query": query,
            "classification": {
                "primary_intent": {"intent": "educational_content", "confidence": 0.3},
                "primary_domain": {"domain": "embedded_hardware", "confidence": 0.3}
            },
            "complexity": {"final_score": 0.5, "factor_scores": {}},
            "routing": fallback_routing,
            "error": str(error),
            "is_fallback": True
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis metadata"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
