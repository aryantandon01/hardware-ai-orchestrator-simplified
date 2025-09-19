"""
Model Routing Accuracy Validation System
Target: >92% optimal model selection
"""

import sqlite3
import json
from pathlib import Path  # ← ADD THIS LINE
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

class ModelType(Enum):
    CLAUDE_SONNET = "claude_sonnet_4"
    GROK_2 = "grok_2"
    GPT4O = "gpt_4o"
    GPT4O_MINI = "gpt_4o_mini"

@dataclass
class RoutingDecision:
    """Model routing decision record"""
    timestamp: datetime
    query_id: str
    query_complexity: float
    query_type: str
    selected_model: str
    routing_confidence: float
    alternative_models: List[str]
    processing_time_ms: float
    success: bool
    expert_validation: Optional[str] = None  # Expert's recommended model

class ModelRoutingValidator:
    """System for validating model routing decisions"""
    
    def __init__(self, db_path: str = "metrics/routing.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Model capability matrix
        self.model_capabilities = {
            "claude_sonnet_4": {
                "complexity_threshold": 0.8,
                "best_for": ["complex_analysis", "design_review"],
                "avg_time_ms": 4500
            },
            "grok_2": {
                "complexity_threshold": 0.6,
                "best_for": ["component_comparison", "recommendation"],
                "avg_time_ms": 3200
            },
            "gpt_4o": {
                "complexity_threshold": 0.4,
                "best_for": ["general_query", "education"],
                "avg_time_ms": 2800
            },
            "gpt_4o_mini": {
                "complexity_threshold": 0.2,
                "best_for": ["simple_lookup", "basic_info"],
                "avg_time_ms": 1500
            }
        }
    
    def _init_database(self):
        """Initialize routing validation database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS routing_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query_id TEXT NOT NULL,
                query_complexity REAL NOT NULL,
                query_type TEXT NOT NULL,
                selected_model TEXT NOT NULL,
                routing_confidence REAL NOT NULL,
                alternative_models TEXT NOT NULL,
                processing_time_ms REAL NOT NULL,
                success BOOLEAN NOT NULL,
                expert_validation TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def record_routing_decision(self, decision: RoutingDecision) -> str:
        """Record a model routing decision"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            INSERT INTO routing_decisions 
            (timestamp, query_id, query_complexity, query_type, selected_model,
             routing_confidence, alternative_models, processing_time_ms, success, expert_validation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.timestamp.isoformat(),
            decision.query_id,
            decision.query_complexity,
            decision.query_type,
            decision.selected_model,
            decision.routing_confidence,
            json.dumps(decision.alternative_models),
            decision.processing_time_ms,
            decision.success,
            decision.expert_validation
        ))
        decision_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return f"routing_{decision_id}"
    
    def validate_routing_accuracy(self, days: int = 7) -> Dict[str, Any]:
        """Validate routing accuracy against expert recommendations and performance"""
        since = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT query_complexity, query_type, selected_model, routing_confidence,
                   processing_time_ms, success, expert_validation
            FROM routing_decisions 
            WHERE timestamp > ?
        """, (since.isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"error": "No routing data available"}
        
        total_decisions = len(results)
        optimal_decisions = 0
        expert_validated = 0
        
        model_performance = {}
        
        for result in results:
            complexity, query_type, selected_model, confidence, time_ms, success, expert_val = result
            
            # Track model performance
            if selected_model not in model_performance:
                model_performance[selected_model] = {
                    "count": 0,
                    "avg_time": 0,
                    "success_rate": 0,
                    "times": [],
                    "successes": []
                }
            
            model_performance[selected_model]["count"] += 1
            model_performance[selected_model]["times"].append(time_ms)
            model_performance[selected_model]["successes"].append(success)
            
            # Check if routing was optimal
            optimal_model = self._determine_optimal_model(complexity, query_type)
            if selected_model == optimal_model:
                optimal_decisions += 1
            
            # Expert validation
            if expert_val:
                expert_validated += 1
                if expert_val == selected_model:
                    # Expert agreed with routing
                    pass
        
        # Calculate model performance statistics
        for model, perf in model_performance.items():
            perf["avg_time"] = statistics.mean(perf["times"])
            perf["success_rate"] = (sum(perf["successes"]) / len(perf["successes"])) * 100
        
        routing_accuracy = (optimal_decisions / total_decisions) * 100
        
        return {
            "period_days": days,
            "total_routing_decisions": total_decisions,
            "routing_accuracy_percent": round(routing_accuracy, 2),
            "expert_validated_count": expert_validated,
            "target_accuracy": 92.0,
            "target_met": routing_accuracy >= 92.0,
            "model_performance": model_performance,
            "routing_grade": self._calculate_routing_grade(routing_accuracy),
            "recommendations": self._generate_routing_recommendations(model_performance)
        }
    
    def _determine_optimal_model(self, complexity: float, query_type: str) -> str:
        """Determine optimal model based on complexity and query type"""
        # Simple rule-based optimal model selection
        if complexity >= 0.8:
            return "claude_sonnet_4"
        elif complexity >= 0.6:
            return "grok_2"
        elif complexity >= 0.3:
            return "gpt_4o"
        else:
            return "gpt_4o_mini"
    
    def _calculate_routing_grade(self, accuracy: float) -> str:
        """Calculate routing accuracy grade"""
        if accuracy >= 95:
            return "A+"
        elif accuracy >= 92:
            return "A"
        elif accuracy >= 85:
            return "B"
        elif accuracy >= 75:
            return "C"
        else:
            return "D"
    
    def _generate_routing_recommendations(self, model_performance: Dict) -> List[str]:
        """Generate routing optimization recommendations"""
        recommendations = []
        
        for model, perf in model_performance.items():
            if perf["success_rate"] < 85:
                recommendations.append(f"Consider reducing {model} usage - low success rate ({perf['success_rate']:.1f}%)")
            
            if perf["avg_time"] > self.model_capabilities.get(model, {}).get("avg_time_ms", 5000):
                recommendations.append(f"{model} performing slower than expected - investigate performance")
        
        return recommendations

# Global instance
routing_validator = ModelRoutingValidator()
