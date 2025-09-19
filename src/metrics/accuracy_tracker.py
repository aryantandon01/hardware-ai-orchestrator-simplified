"""
Technical Accuracy Validation System
Target: >95% accuracy for component specifications
"""

import json
import sqlite3
from pathlib import Path  # ← ADD THIS LINE
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import statistics

@dataclass
class AccuracyResult:
    """Individual accuracy measurement"""
    timestamp: datetime
    query_id: str
    component_type: str
    predicted_specs: Dict[str, Any]
    verified_specs: Dict[str, Any]
    accuracy_score: float
    validation_method: str
    validator_id: Optional[str] = None

class AccuracyTracker:
    """System for tracking and validating technical accuracy"""
    
    def __init__(self, db_path: str = "metrics/accuracy.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Component specification databases (APIs/datasets)
        self.validation_sources = {
            "digikey": "https://api.digikey.com/v1/",
            "mouser": "https://api.mouser.com/api/v1/",
            "manufacturer_datasheets": "internal_db",
            "expert_validation": "manual"
        }
    
    def _init_database(self):
        """Initialize accuracy tracking database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accuracy_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query_id TEXT NOT NULL,
                component_type TEXT NOT NULL,
                predicted_specs TEXT NOT NULL,
                verified_specs TEXT NOT NULL,
                accuracy_score REAL NOT NULL,
                validation_method TEXT NOT NULL,
                validator_id TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    async def validate_component_accuracy(self, 
                                        query_id: str,
                                        component_type: str,
                                        predicted_specs: Dict[str, Any],
                                        validation_method: str = "auto") -> AccuracyResult:
        """Validate component specification accuracy"""
        
        if validation_method == "auto":
            verified_specs = await self._auto_validate_specs(component_type, predicted_specs)
        elif validation_method == "datasheet":
            verified_specs = await self._datasheet_validate(component_type, predicted_specs)
        else:
            verified_specs = predicted_specs  # Fallback
        
        # Calculate accuracy score
        accuracy_score = self._calculate_accuracy_score(predicted_specs, verified_specs)
        
        result = AccuracyResult(
            timestamp=datetime.now(),
            query_id=query_id,
            component_type=component_type,
            predicted_specs=predicted_specs,
            verified_specs=verified_specs,
            accuracy_score=accuracy_score,
            validation_method=validation_method
        )
        
        self._store_accuracy_result(result)
        return result
    
    async def _auto_validate_specs(self, component_type: str, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically validate against component databases"""
        # This would integrate with actual component databases
        # For now, return mock validation
        return {
            **specs,
            "validation_source": "auto_db",
            "confidence": 0.85
        }
    
    async def _datasheet_validate(self, component_type: str, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against manufacturer datasheets"""
        # Mock datasheet validation
        return {
            **specs,
            "validation_source": "datasheet",
            "confidence": 0.95
        }
    
    def _calculate_accuracy_score(self, predicted: Dict[str, Any], verified: Dict[str, Any]) -> float:
        """Calculate accuracy score between predicted and verified specs"""
        if not predicted or not verified:
            return 0.0
        
        common_keys = set(predicted.keys()) & set(verified.keys())
        if not common_keys:
            return 0.0
        
        correct_count = 0
        for key in common_keys:
            if key in ['validation_source', 'confidence']:
                continue
                
            pred_val = str(predicted[key]).lower()
            ver_val = str(verified[key]).lower()
            
            # Fuzzy matching for specifications
            if pred_val == ver_val:
                correct_count += 1
            elif self._fuzzy_match(pred_val, ver_val):
                correct_count += 0.8  # Partial credit
        
        return (correct_count / len(common_keys)) * 100
    
    def _fuzzy_match(self, val1: str, val2: str) -> bool:
        """Fuzzy matching for component specifications"""
        # Simple fuzzy matching - could be enhanced with ML
        val1_clean = ''.join(c for c in val1 if c.isalnum()).lower()
        val2_clean = ''.join(c for c in val2 if c.isalnum()).lower()
        
        if len(val1_clean) == 0 or len(val2_clean) == 0:
            return False
        
        # Simple substring matching
        return val1_clean in val2_clean or val2_clean in val1_clean
    
    def _store_accuracy_result(self, result: AccuracyResult):
        """Store accuracy result in database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO accuracy_results 
            (timestamp, query_id, component_type, predicted_specs, verified_specs,
             accuracy_score, validation_method, validator_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            result.query_id,
            result.component_type,
            json.dumps(result.predicted_specs),
            json.dumps(result.verified_specs),
            result.accuracy_score,
            result.validation_method,
            result.validator_id
        ))
        conn.commit()
        conn.close()
    
    def get_accuracy_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get accuracy summary for specified period"""
        since = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT accuracy_score, component_type, validation_method
            FROM accuracy_results 
            WHERE timestamp > ?
        """, (since.isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"error": "No validation data available"}
        
        scores = [r[0] for r in results]
        avg_accuracy = statistics.mean(scores)
        
        # Component type breakdown
        type_accuracy = {}
        for score, comp_type, _ in results:
            if comp_type not in type_accuracy:
                type_accuracy[comp_type] = []
            type_accuracy[comp_type].append(score)
        
        type_summary = {
            comp_type: {
                "avg_accuracy": statistics.mean(scores),
                "count": len(scores)
            }
            for comp_type, scores in type_accuracy.items()
        }
        
        return {
            "period_days": days,
            "total_validations": len(results),
            "avg_accuracy_percent": round(avg_accuracy, 2),
            "target_accuracy": 95.0,
            "target_met": avg_accuracy >= 95.0,
            "accuracy_grade": "A" if avg_accuracy >= 95 else "B" if avg_accuracy >= 90 else "C",
            "component_type_breakdown": type_summary
        }

# Global instance
accuracy_tracker = AccuracyTracker()
