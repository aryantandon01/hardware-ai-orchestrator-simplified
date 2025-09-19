"""
Pydantic models for request and response validation
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class UserExpertise(str, Enum):
    """User expertise levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    SENIOR = "senior"
    EXPERT = "expert"

class HardwareQueryRequest(BaseModel):
    """Request model for hardware query analysis"""
    query: str = Field(..., min_length=5, max_length=1000, description="Hardware engineering query")
    user_expertise: UserExpertise = Field(default=UserExpertise.INTERMEDIATE, description="User expertise level")
    project_phase: Optional[str] = Field(default=None, description="Project phase: concept, design, validation, production")
    preferred_domain: Optional[str] = Field(default=None, description="Preferred hardware domain if known")

class IntentClassification(BaseModel):
    """Intent classification results"""
    intent: str
    confidence: float
    description: str

class DomainClassification(BaseModel):
    """Domain classification results"""
    domain: str
    confidence: float
    info: Dict[str, Any]

class ComplexityAnalysis(BaseModel):
    """Complexity analysis results"""
    final_score: float
    factor_scores: Dict[str, float]
    word_count: int
    length_bonus: float

class RoutingDecision(BaseModel):
    """Model routing decision"""
    selected_model: str
    confidence: float
    reasoning: List[str]
    all_scores: Dict[str, float]
    complexity_score: float

class HardwareQueryResponse(BaseModel):
    """Complete response for hardware query analysis"""
    query: str
    classification: Dict[str, Any]
    complexity: ComplexityAnalysis
    routing: RoutingDecision
    analysis_metadata: Dict[str, Any]
    processing_time_ms: Optional[float] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    components: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    query: Optional[str] = None
