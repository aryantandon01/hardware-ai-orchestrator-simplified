"""
Main FastAPI Application - Hardware AI Orchestrator
Enhanced with Multi-Modal Schematic Processing Capabilities
"""
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import uvicorn
import os
from typing import Optional


from .api.endpoints import router
from .config.settings import settings


# Add to your existing API endpoints (src/api/endpoints.py or main.py)

from src.metrics.performance_monitor import performance_monitor
from src.metrics.accuracy_tracker import accuracy_tracker
from src.metrics.user_feedback import feedback_system, UserFeedback
from src.metrics.model_routing_validator import routing_validator, RoutingDecision
# from src.metrics.dashboard.metrics_api import metrics_router
from datetime import datetime
import uuid

# Import schematic router with graceful fallback
try:
    from .vision.schematic_processor.integration_handler import schematic_router, EnhancedSchematicProcessor
    SCHEMATIC_AVAILABLE = True
    logging.info("✅ Schematic processing module loaded successfully")
except ImportError as e:
    schematic_router = None
    EnhancedSchematicProcessor = None
    SCHEMATIC_AVAILABLE = False
    logging.warning(f"⚠️ Schematic processing not available: {e}")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI app with enhanced metadata
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🚀 AI Orchestration System for Hardware Engineering
    
    **Core Capabilities:**
    - Intelligent AI model routing based on query complexity
    - RAG-enhanced knowledge retrieval with vector search
    - Multi-domain expertise (automotive, medical, IoT, digital design)
    - Advanced query analysis with intent classification
    
    **Advanced Features:**
    - Multi-modal schematic understanding and analysis
    - Component detection and recommendation
    - Design compliance checking
    - Supply chain intelligence (planned)
    
    **API Endpoints:**
    - `/api/v1/analyze` - Natural language hardware queries
    - `/api/v1/schematic/analyze` - Schematic image analysis
    - `/docs` - Interactive API documentation
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Hardware AI Orchestrator",
        "url": "https://github.com/your-repo/hardware-ai-orchestrator"
    }
)


# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)


# Request timing and ID middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and request ID to response headers"""
    import uuid
    
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Add request ID to request state for logging
    request.state.request_id = request_id
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    response.headers["X-Request-ID"] = request_id
    
    return response


# Include existing API router
app.include_router(router)


# ✅ CRITICAL FIX: Include schematic router WITHOUT additional prefix
# The schematic_router already has prefix="/api/v1/schematic" defined internally
if SCHEMATIC_AVAILABLE and schematic_router:
    app.include_router(
        schematic_router,  # No prefix here - router already defines its own
        tags=["schematic-processing"]
    )
    logger.info("🔍 Schematic processing endpoints enabled at /api/v1/schematic/*")
else:
    logger.warning("⚠️ Schematic processing endpoints not available")


# Enhanced root endpoint
@app.get("/", 
         summary="Hardware AI Orchestrator Root", 
         description="System information and available endpoints")
async def root():
    """Enhanced root endpoint with comprehensive system information"""
    endpoints = {
        "analyze": {
            "url": "/api/v1/analyze",
            "method": "POST",
            "description": "Natural language hardware engineering queries with AI routing"
        },
        "health": {
            "url": "/api/v1/health", 
            "method": "GET",
            "description": "System health check"
        }
    }
    
    # Add schematic endpoints if available
    if SCHEMATIC_AVAILABLE:
        endpoints["schematic_analyze"] = {
            "url": "/api/v1/schematic/analyze",
            "method": "POST", 
            "description": "Multi-modal schematic image analysis and component detection"
        }
        endpoints["schematic_health"] = {
            "url": "/api/v1/schematic/health",
            "method": "GET",
            "description": "Schematic processing service health check"
        }
        endpoints["schematic_capabilities"] = {
            "url": "/api/v1/schematic/capabilities",
            "method": "GET",
            "description": "Schematic processing capabilities and features"
        }
    
    return {
        "message": "🚀 Hardware AI Orchestrator",
        "version": settings.app_version,
        "status": "operational",
        "capabilities": {
            "ai_routing": "✅ Enabled",
            "knowledge_retrieval": "✅ Enabled", 
            "vector_search": "✅ Enabled",
            "schematic_processing": "✅ Enabled" if SCHEMATIC_AVAILABLE else "⚠️ Unavailable"
        },
        "endpoints": endpoints,
        "documentation": {
            "interactive_docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Enhanced system status endpoint
@app.get("/api/v1/status", 
         summary="System Status", 
         description="Detailed system status and feature availability")
async def system_status():
    """Comprehensive system status endpoint"""
    try:
        # Test core components
        from .analysis.query_analyzer import HardwareQueryAnalyzer
        from .routing.model_router import ModelRouter
        
        core_status = "healthy"
        query_analyzer = HardwareQueryAnalyzer()
        model_router = ModelRouter()
        
    except Exception as e:
        core_status = "degraded"
        logger.error(f"Core component check failed: {e}")
    
    # Test knowledge retrieval
    try:
        from .knowledge.retrieval_engine import HardwareRetrievalEngine
        retrieval_engine = HardwareRetrievalEngine()
        knowledge_status = "healthy"
    except Exception as e:
        knowledge_status = "degraded"
        logger.error(f"Knowledge retrieval check failed: {e}")
    
    # Test schematic processing
    schematic_status = "healthy" if SCHEMATIC_AVAILABLE else "unavailable"
    
    return {
        "timestamp": time.time(),
        "system": {
            "status": core_status,
            "uptime": "operational",
            "version": settings.app_version
        },
        "components": {
            "core_ai_pipeline": core_status,
            "knowledge_retrieval": knowledge_status,
            "schematic_processing": schematic_status,
            "vector_database": "healthy" if knowledge_status == "healthy" else "unknown"
        },
        "features": {
            "intelligent_routing": True,
            "rag_enhancement": True,
            "multi_modal_processing": SCHEMATIC_AVAILABLE,
            "predictive_intelligence": False,  # Future feature
            "collaborative_features": False   # Future feature
        }
    }


# Enhanced global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Enhanced global exception handler with detailed logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"🚨 Unhandled exception [Request ID: {request_id}] "
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Error: {str(exc)}"
    )
    
    # Don't expose internal errors in production
    error_detail = str(exc) if settings.debug else "An internal error occurred"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": error_detail,
            "request_id": request_id,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


# HTTP exception handler for better error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced HTTP exception handler"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 Hardware AI Orchestrator starting up...")
    logger.info(f"📊 Version: {settings.app_version}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🔍 Schematic processing: {'Enabled' if SCHEMATIC_AVAILABLE else 'Disabled'}")
    
    # Initialize components
    try:
        from .knowledge.retrieval_engine import HardwareRetrievalEngine
        retrieval_engine = HardwareRetrievalEngine()
        logger.info("✅ Knowledge retrieval engine initialized")
    except Exception as e:
        logger.warning(f"⚠️ Knowledge retrieval initialization failed: {e}")
    
    # Log available routes for debugging
    logger.info("🔗 Available API routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"  {route.methods} {route.path}")
    
    logger.info("✅ Hardware AI Orchestrator startup complete")


# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🛑 Hardware AI Orchestrator shutting down...")
    # Add cleanup tasks here if needed
    logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    # Enhanced development server configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"🌐 Starting server at http://{host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True,
        reload_dirs=["src"] if settings.debug else None
    )

@schematic_router.post("/analyze")
async def analyze_schematic(file: UploadFile = File(...)):
    """Enhanced schematic analysis with comprehensive metrics tracking"""
    import time
    import tempfile
    import asyncio
    from pathlib import Path
    from fastapi import HTTPException
    from fastapi.encoders import jsonable_encoder
    
    # Import your metrics modules (add these at the top of your file)
    from src.metrics.performance_monitor import performance_monitor
    from src.metrics.accuracy_tracker import accuracy_tracker
    from src.vision.schematic_processor.integration_handler import EnhancedSchematicProcessor
    
    # Generate unique query ID
    query_id = f"query_{int(time.time() * 1000)}"
    temp_file_path = None
    
    # Start performance monitoring
    performance_monitor.start_measurement(query_id, "schematic_analysis")
    
    try:
        # File validation with metrics tracking
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        if not file.filename.lower().endswith(allowed_extensions):
            performance_monitor.complete_measurement(
                query_id, 
                success=False, 
                error_type="InvalidFileType"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        file_content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            tmp_file.write(file_content)
            temp_file_path = tmp_file.name
        
        # Processing with detailed checkpoints
        processor = EnhancedSchematicProcessor()
        
        # Checkpoint: Starting symbol detection
        performance_monitor.checkpoint(query_id, "symbol_detection_start")
        
        # Process schematic - this calls your existing process_schematic method
        result = await processor.process_schematic(temp_file_path)
        
        # Checkpoint: Processing complete
        performance_monitor.checkpoint(query_id, "processing_complete")
        
        # Calculate complexity score from results (you can enhance this logic)
        complexity_score = calculate_complexity_score(result)
        
        # Complete performance measurement
        perf_metric = performance_monitor.complete_measurement(
            query_id,
            success=True,
            complexity_score=complexity_score
        )
        
        # Add comprehensive metrics metadata to response
        result["metrics"] = {
            "query_id": query_id,
            "processing_time_ms": round(perf_metric.total_time_ms, 2),
            "performance_grade": calculate_performance_grade(perf_metric.total_time_ms),
            "complexity_score": complexity_score,
            "timestamp": perf_metric.timestamp.isoformat(),
            "checkpoints": {
                "symbol_detection_ms": perf_metric.symbol_detection_ms,
                "ocr_extraction_ms": perf_metric.ocr_extraction_ms,
                "topology_analysis_ms": perf_metric.topology_analysis_ms,
                "recommendations_ms": perf_metric.recommendations_ms
            }
        }
        
        # Async accuracy validation (doesn't block response)
        asyncio.create_task(
            validate_component_accuracy_async(
                query_id,
                result.get("detected_components", []),
                complexity_score
            )
        )
        
        # Ensure JSON serialization safety
        safe_result = jsonable_encoder(result)
        
        return safe_result
    
    except Exception as e:
        # Record failed measurement with detailed error info
        performance_monitor.complete_measurement(
            query_id,
            success=False,
            error_type=type(e).__name__
        )
        
        logger.error(f"❌ Schematic analysis failed for query {query_id}: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Processing failed: {str(e)}",
                "query_id": query_id,
                "timestamp": time.time()
            }
        )
    
    finally:
        # Robust cleanup
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")


def calculate_complexity_score(result: dict) -> float:
    """Calculate query complexity score based on analysis results"""
    try:
        component_count = len(result.get("detected_components", []))
        topology_connections = len(result.get("topology_analysis", {}).get("connections", []))
        has_spice = result.get("spice_netlist", {}).get("generation_successful", False)
        
        # Simple complexity scoring (you can enhance this)
        base_score = min(component_count / 20.0, 1.0)  # Normalize by expected max components
        topology_bonus = min(topology_connections / 10.0, 0.3)  # Up to 30% bonus for topology
        spice_bonus = 0.2 if has_spice else 0  # 20% bonus if SPICE generated
        
        return min(base_score + topology_bonus + spice_bonus, 1.0)
    except Exception:
        return 0.5  # Default complexity if calculation fails


def calculate_performance_grade(processing_time_ms: float) -> str:
    """Calculate performance grade based on processing time"""
    if processing_time_ms < 2000:
        return "A+"
    elif processing_time_ms < 3000:
        return "A"
    elif processing_time_ms < 5000:
        return "B"
    elif processing_time_ms < 8000:
        return "C"
    else:
        return "D"


async def validate_component_accuracy_async(query_id: str, components: list, complexity: float):
    """Async validation of component accuracy (runs in background)"""
    try:
        if not components:
            return
        
        # Sample validation for first few components
        for i, component in enumerate(components[:5]):  # Limit to first 5 for performance
            await accuracy_tracker.validate_component_accuracy(
                query_id=f"{query_id}_comp_{i}",
                component_type=component.get("component_type", "unknown"),
                predicted_specs={
                    "designation": component.get("designation"),
                    "value": component.get("value"),
                    "confidence": component.get("confidence", 0.0)
                },
                validation_method="auto"
            )
    except Exception as e:
        logger.warning(f"Background accuracy validation failed for {query_id}: {e}")


@schematic_router.post("/feedback")
async def submit_user_feedback(
    query_id: str,
    satisfaction_rating: int,
    relevance_score: int,
    accuracy_perceived: int,
    speed_satisfaction: int,
    user_id: str = "anonymous",
    comments: Optional[str] = None,
    feature_used: Optional[str] = None
):
    """Submit user feedback for analysis quality"""
    
    feedback = UserFeedback(
        timestamp=datetime.now(),
        query_id=query_id,
        user_id=user_id,
        satisfaction_rating=satisfaction_rating,
        relevance_score=relevance_score,
        accuracy_perceived=accuracy_perceived,
        speed_satisfaction=speed_satisfaction,
        comments=comments,
        feature_used=feature_used
    )
    
    feedback_id = feedback_system.submit_feedback(feedback)
    
    return {
        "status": "success",
        "feedback_id": feedback_id,
        "message": "Thank you for your feedback!"
    }

@schematic_router.get("/metrics/dashboard")
async def get_metrics_dashboard():
    """Get comprehensive metrics dashboard"""
    
    # Gather all metrics
    performance_summary = performance_monitor.get_performance_summary(24)
    accuracy_summary = accuracy_tracker.get_accuracy_summary(7)
    satisfaction_summary = feedback_system.get_satisfaction_summary(30)
    routing_summary = routing_validator.validate_routing_accuracy(7)
    
    return {
        "dashboard_generated": datetime.now().isoformat(),
        "performance": performance_summary,
        "accuracy": accuracy_summary,
        "user_satisfaction": satisfaction_summary,
        "model_routing": routing_summary,
        "compliance_status": {
            "performance_target_met": performance_summary.get("target_met", False),
            "accuracy_target_met": accuracy_summary.get("target_met", False),
            "satisfaction_target_met": satisfaction_summary.get("target_met", False),
            "routing_target_met": routing_summary.get("target_met", False)
        }
    }
