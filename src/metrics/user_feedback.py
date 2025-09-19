"""
User Satisfaction and Feedback System
Target: >85% user satisfaction rating
"""

import sqlite3
import json
from pathlib import Path  # ← ADD THIS LINE
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics

class SatisfactionRating(Enum):
    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5

@dataclass
class UserFeedback:
    """Individual user feedback entry"""
    timestamp: datetime
    query_id: str
    user_id: str
    satisfaction_rating: int  # 1-5 scale
    relevance_score: int     # 1-5 scale
    accuracy_perceived: int  # 1-5 scale
    speed_satisfaction: int  # 1-5 scale
    comments: Optional[str] = None
    feature_used: Optional[str] = None

class UserFeedbackSystem:
    """System for collecting and analyzing user feedback"""
    
    def __init__(self, db_path: str = "metrics/feedback.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                satisfaction_rating INTEGER NOT NULL,
                relevance_score INTEGER NOT NULL,
                accuracy_perceived INTEGER NOT NULL,
                speed_satisfaction INTEGER NOT NULL,
                comments TEXT,
                feature_used TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def submit_feedback(self, feedback: UserFeedback) -> str:
        """Submit user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            INSERT INTO user_feedback 
            (timestamp, query_id, user_id, satisfaction_rating, relevance_score,
             accuracy_perceived, speed_satisfaction, comments, feature_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.timestamp.isoformat(),
            feedback.query_id,
            feedback.user_id,
            feedback.satisfaction_rating,
            feedback.relevance_score,
            feedback.accuracy_perceived,
            feedback.speed_satisfaction,
            feedback.comments,
            feedback.feature_used
        ))
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return f"feedback_{feedback_id}"
    
    def get_satisfaction_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get user satisfaction summary"""
        since = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT satisfaction_rating, relevance_score, accuracy_perceived, 
                   speed_satisfaction, feature_used
            FROM user_feedback 
            WHERE timestamp > ?
        """, (since.isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"error": "No feedback data available"}
        
        # Calculate metrics
        satisfaction_scores = [r[0] for r in results]
        relevance_scores = [r[1] for r in results]
        accuracy_scores = [r[2] for r in results]
        speed_scores = [r[3] for r in results]
        
        avg_satisfaction = statistics.mean(satisfaction_scores)
        satisfied_users = len([s for s in satisfaction_scores if s >= 4])
        satisfaction_rate = (satisfied_users / len(satisfaction_scores)) * 100
        
        # Feature breakdown
        feature_satisfaction = {}
        for result in results:
            feature = result[4] or "general"
            if feature not in feature_satisfaction:
                feature_satisfaction[feature] = []
            feature_satisfaction[feature].append(result[0])
        
        feature_summary = {
            feature: {
                "avg_satisfaction": statistics.mean(scores),
                "count": len(scores)
            }
            for feature, scores in feature_satisfaction.items()
        }
        
        return {
            "period_days": days,
            "total_feedback": len(results),
            "avg_satisfaction_score": round(avg_satisfaction, 2),
            "satisfaction_rate_percent": round(satisfaction_rate, 2),
            "target_satisfaction": 85.0,
            "target_met": satisfaction_rate >= 85.0,
            "detailed_scores": {
                "relevance": round(statistics.mean(relevance_scores), 2),
                "perceived_accuracy": round(statistics.mean(accuracy_scores), 2),
                "speed_satisfaction": round(statistics.mean(speed_scores), 2)
            },
            "feature_breakdown": feature_summary,
            "satisfaction_grade": self._calculate_satisfaction_grade(satisfaction_rate)
        }
    
    def _calculate_satisfaction_grade(self, satisfaction_rate: float) -> str:
        """Calculate satisfaction grade"""
        if satisfaction_rate >= 95:
            return "A+"
        elif satisfaction_rate >= 85:
            return "A"
        elif satisfaction_rate >= 75:
            return "B"
        elif satisfaction_rate >= 65:
            return "C"
        else:
            return "D"

# Global instance
feedback_system = UserFeedbackSystem()
