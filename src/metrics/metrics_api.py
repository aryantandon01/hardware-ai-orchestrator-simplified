"""
Comprehensive Metrics Dashboard API
Real-time metrics visualization and reporting
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from .performance_monitor import performance_monitor
from .accuracy_tracker import accuracy_tracker
from .user_feedback import feedback_system
from .model_routing_validator import routing_validator


metrics_router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

@metrics_router.get("/health")
async def metrics_health():
    """Metrics system health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "performance_monitor": "active",
            "accuracy_tracker": "active", 
            "feedback_system": "active",
            "routing_validator": "active"
        }
    }

@metrics_router.get("/performance/summary")
async def get_performance_metrics(hours: int = 24):
    """Get performance metrics summary"""
    return performance_monitor.get_performance_summary(hours)

@metrics_router.get("/accuracy/summary") 
async def get_accuracy_metrics(days: int = 7):
    """Get accuracy validation summary"""
    return accuracy_tracker.get_accuracy_summary(days)

@metrics_router.get("/satisfaction/summary")
async def get_satisfaction_metrics(days: int = 30):
    """Get user satisfaction summary"""
    return feedback_system.get_satisfaction_summary(days)

@metrics_router.get("/routing/summary")
async def get_routing_metrics(days: int = 7):
    """Get model routing accuracy summary"""
    return routing_validator.validate_routing_accuracy(days)

@metrics_router.get("/compliance/report")
async def get_compliance_report():
    """Get comprehensive compliance report against all targets"""
    
    performance_data = performance_monitor.get_performance_summary(24)
    accuracy_data = accuracy_tracker.get_accuracy_summary(7)
    satisfaction_data = feedback_system.get_satisfaction_summary(30)
    routing_data = routing_validator.validate_routing_accuracy(7)
    
    compliance_score = 0
    total_targets = 4
    
    targets_status = {
        "response_time_target": {
            "target": "95% of queries under 5 seconds",
            "current": f"{performance_data.get('under_5s_target_compliance', 0):.1f}%",
            "met": performance_data.get('target_met', False),
            "grade": performance_data.get('performance_grade', 'D')
        },
        "accuracy_target": {
            "target": ">95% technical accuracy",
            "current": f"{accuracy_data.get('avg_accuracy_percent', 0):.1f}%",
            "met": accuracy_data.get('target_met', False),
            "grade": accuracy_data.get('accuracy_grade', 'D')
        },
        "satisfaction_target": {
            "target": ">85% user satisfaction",
            "current": f"{satisfaction_data.get('satisfaction_rate_percent', 0):.1f}%",
            "met": satisfaction_data.get('target_met', False),
            "grade": satisfaction_data.get('satisfaction_grade', 'D')
        },
        "routing_target": {
            "target": ">92% optimal model selection",
            "current": f"{routing_data.get('routing_accuracy_percent', 0):.1f}%",
            "met": routing_data.get('target_met', False),
            "grade": routing_data.get('routing_grade', 'D')
        }
    }
    
    # Calculate overall compliance score
    for target in targets_status.values():
        if target["met"]:
            compliance_score += 1
    
    overall_grade = "A" if compliance_score == 4 else "B" if compliance_score >= 3 else "C" if compliance_score >= 2 else "D"
    
    return {
        "report_generated": datetime.now().isoformat(),
        "overall_compliance_score": f"{(compliance_score/total_targets)*100:.1f}%",
        "overall_grade": overall_grade,
        "targets_met": compliance_score,
        "total_targets": total_targets,
        "detailed_status": targets_status,
        "recommendations": [
            "Focus on performance optimization" if not targets_status["response_time_target"]["met"] else None,
            "Improve accuracy validation processes" if not targets_status["accuracy_target"]["met"] else None,
            "Enhance user experience" if not targets_status["satisfaction_target"]["met"] else None,
            "Optimize model routing logic" if not targets_status["routing_target"]["met"] else None
        ]
    }
