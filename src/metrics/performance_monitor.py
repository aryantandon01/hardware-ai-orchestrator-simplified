"""
Performance Monitoring System for Hardware AI Orchestrator
Target: <5 seconds for 95% of queries, comprehensive timing analysis
"""

import time
import asyncio
import statistics
import json
import sqlite3
from pathlib import Path  # ← ADD THIS LINE
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: datetime
    query_id: str
    query_type: str
    total_time_ms: float
    symbol_detection_ms: float
    ocr_extraction_ms: float
    topology_analysis_ms: float
    recommendations_ms: float
    model_routing_time_ms: float
    user_id: Optional[str] = None
    complexity_score: Optional[float] = None
    success: bool = True
    error_type: Optional[str] = None

class PerformanceMonitor:
    """Real-time performance monitoring and analysis"""
    
    def __init__(self, db_path: str = "metrics/performance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self.current_measurements = {}
        
    def _init_database(self):
        """Initialize performance metrics database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query_id TEXT NOT NULL,
                query_type TEXT NOT NULL,
                total_time_ms REAL NOT NULL,
                symbol_detection_ms REAL,
                ocr_extraction_ms REAL,
                topology_analysis_ms REAL,
                recommendations_ms REAL,
                model_routing_time_ms REAL,
                user_id TEXT,
                complexity_score REAL,
                success BOOLEAN NOT NULL,
                error_type TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def start_measurement(self, query_id: str, query_type: str = "schematic_analysis") -> str:
        """Start performance measurement for a query"""
        self.current_measurements[query_id] = {
            'start_time': time.time(),
            'query_type': query_type,
            'checkpoints': {}
        }
        return query_id
    
    def checkpoint(self, query_id: str, checkpoint_name: str):
        """Record a performance checkpoint"""
        if query_id in self.current_measurements:
            current_time = time.time()
            start_time = self.current_measurements[query_id]['start_time']
            self.current_measurements[query_id]['checkpoints'][checkpoint_name] = {
                'time_ms': (current_time - start_time) * 1000,
                'timestamp': current_time
            }
    
    def complete_measurement(self, query_id: str, success: bool = True, 
                           error_type: Optional[str] = None,
                           user_id: Optional[str] = None,
                           complexity_score: Optional[float] = None) -> PerformanceMetric:
        """Complete measurement and store results"""
        if query_id not in self.current_measurements:
            raise ValueError(f"No measurement started for query_id: {query_id}")
        
        measurement = self.current_measurements[query_id]
        end_time = time.time()
        total_time_ms = (end_time - measurement['start_time']) * 1000
        
        # Calculate individual stage times
        checkpoints = measurement['checkpoints']
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            query_id=query_id,
            query_type=measurement['query_type'],
            total_time_ms=total_time_ms,
            symbol_detection_ms=checkpoints.get('symbol_detection', {}).get('time_ms', 0),
            ocr_extraction_ms=checkpoints.get('ocr_extraction', {}).get('time_ms', 0),
            topology_analysis_ms=checkpoints.get('topology_analysis', {}).get('time_ms', 0),
            recommendations_ms=checkpoints.get('recommendations', {}).get('time_ms', 0),
            model_routing_time_ms=checkpoints.get('model_routing', {}).get('time_ms', 0),
            user_id=user_id,
            complexity_score=complexity_score,
            success=success,
            error_type=error_type
        )
        
        # Store in database
        self._store_metric(metric)
        
        # Clean up
        del self.current_measurements[query_id]
        
        return metric
    
    def _store_metric(self, metric: PerformanceMetric):
        """Store performance metric in database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO performance_metrics 
            (timestamp, query_id, query_type, total_time_ms, symbol_detection_ms,
             ocr_extraction_ms, topology_analysis_ms, recommendations_ms,
             model_routing_time_ms, user_id, complexity_score, success, error_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric.timestamp.isoformat(),
            metric.query_id,
            metric.query_type,
            metric.total_time_ms,
            metric.symbol_detection_ms,
            metric.ocr_extraction_ms,
            metric.topology_analysis_ms,
            metric.recommendations_ms,
            metric.model_routing_time_ms,
            metric.user_id,
            metric.complexity_score,
            metric.success,
            metric.error_type
        ))
        conn.commit()
        conn.close()
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        since = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT total_time_ms, success, query_type 
            FROM performance_metrics 
            WHERE timestamp > ? AND success = 1
        """, (since.isoformat(),))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"error": "No data available for specified period"}
        
        response_times = [r[0] for r in results]
        
        # Calculate key metrics
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        success_rate = len([r for r in results if r[1]]) / len(results) * 100
        
        # Target compliance
        under_5s_count = len([t for t in response_times if t < 5000])
        under_5s_percentage = (under_5s_count / len(response_times)) * 100
        
        return {
            "period_hours": hours,
            "total_queries": len(results),
            "avg_response_time_ms": round(avg_response_time, 2),
            "p95_response_time_ms": round(p95_response_time, 2),
            "success_rate_percent": round(success_rate, 2),
            "under_5s_target_compliance": round(under_5s_percentage, 2),
            "target_met": under_5s_percentage >= 95.0,
            "performance_grade": self._calculate_performance_grade(avg_response_time, under_5s_percentage)
        }
    
    def _calculate_performance_grade(self, avg_time: float, compliance: float) -> str:
        """Calculate overall performance grade"""
        if avg_time < 2000 and compliance >= 98:
            return "A+"
        elif avg_time < 3000 and compliance >= 95:
            return "A"
        elif avg_time < 4000 and compliance >= 90:
            return "B"
        elif avg_time < 5000 and compliance >= 85:
            return "C"
        else:
            return "D"

# Global instance
performance_monitor = PerformanceMonitor()
