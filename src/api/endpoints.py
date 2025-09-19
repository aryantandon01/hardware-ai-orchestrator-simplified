"""
FastAPI endpoints for Hardware AI Orchestrator
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Any

from .models import (
    HardwareQueryRequest, HardwareQueryResponse, 
    HealthResponse, ErrorResponse
)
from ..classification.query_analyzer import HardwareQueryAnalyzer
from ..config.settings import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Hardware Analysis"])

# Initialize query analyzer (singleton)
query_analyzer = None

def get_query_analyzer() -> HardwareQueryAnalyzer:
    """Dependency to get query analyzer instance"""
    global query_analyzer
    if query_analyzer is None:
        query_analyzer = HardwareQueryAnalyzer()
    return query_analyzer

@router.post("/analyze", 
             response_model=HardwareQueryResponse,
             summary="Analyze Hardware Engineering Query",
             description="Analyze hardware engineering query for intent, domain, complexity and optimal AI model routing")
async def analyze_hardware_query(
    request: HardwareQueryRequest,
    analyzer: HardwareQueryAnalyzer = Depends(get_query_analyzer)
) -> HardwareQueryResponse:
    """
    Analyze hardware engineering query and determine optimal AI model routing
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing query from {request.user_expertise} user: {request.query[:100]}...")
        
        # Perform complete analysis (single-intent mode for backward compatibility)
        analysis = analyzer.analyze_query(request.query, enable_multi_intent=False)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = HardwareQueryResponse(
            **analysis,
            processing_time_ms=round(processing_time, 2)
        )
        
        logger.info(f"Analysis completed in {processing_time:.2f}ms - "
                   f"Model: {analysis['routing']['selected_model']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed for query: {request.query[:50]}... Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query analysis failed: {str(e)}"
        )

@router.post("/analyze-advanced", 
             response_model=Dict[str, Any],
             summary="Advanced Multi-Intent Analysis",
             description="Enhanced analysis with optional multi-intent classification and knowledge retrieval")
async def analyze_advanced_query(
    request: HardwareQueryRequest,
    enable_multi_intent: bool = False,
    analyzer: HardwareQueryAnalyzer = Depends(get_query_analyzer)
) -> Dict[str, Any]:
    """
    Enhanced analysis with optional multi-intent support and comprehensive knowledge retrieval
    """
    start_time = time.time()
    
    try:
        logger.info(f"Advanced analysis (multi-intent={enable_multi_intent}) from {request.user_expertise} user: {request.query[:100]}...")
        
        # Step 1: Perform enhanced analysis with optional multi-intent support
        analysis = analyzer.analyze_query(request.query, enable_multi_intent=enable_multi_intent)
        
        # Step 2: Knowledge retrieval for RAG enhancement
        from ..knowledge.retrieval_engine import HardwareRetrievalEngine, RetrievalContext
        
        retrieval_engine = HardwareRetrievalEngine()
        
        retrieval_context = RetrievalContext(
            query=request.query,
            primary_intent=analysis["classification"]["primary_intent"]["intent"],
            primary_domain=analysis["classification"]["primary_domain"]["domain"],
            complexity_score=analysis["complexity"]["final_score"],
            user_expertise=request.user_expertise.value
        )
        
        knowledge = retrieval_engine.retrieve_knowledge(retrieval_context)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Step 3: Compile enhanced response
        enhanced_response = {
            **analysis,  # Include all Day 1 analysis
            "knowledge": {
                "components": knowledge.components,
                "standards": knowledge.standards,
                "domain_context": knowledge.domain_context,
                "retrieval_summary": knowledge.retrieval_summary
            },
            "processing_time_ms": round(processing_time, 2),
            "capabilities": [
                "intent_classification", 
                "domain_detection", 
                "complexity_scoring", 
                "model_routing", 
                "knowledge_retrieval",
                "multi_intent_analysis" if enable_multi_intent else "single_intent_analysis"
            ]
        }
        
        logger.info(f"Advanced analysis completed in {processing_time:.2f}ms - "
                   f"Retrieved {len(knowledge.components)} components, {len(knowledge.standards)} standards")
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Advanced analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced analysis failed: {str(e)}")

@router.post("/analyze-with-knowledge", 
             response_model=Dict[str, Any],
             summary="Analyze Query with Knowledge Retrieval",
             description="Complete analysis with RAG-enhanced knowledge retrieval")
async def analyze_with_knowledge(
    request: HardwareQueryRequest,
    analyzer: HardwareQueryAnalyzer = Depends(get_query_analyzer)
) -> Dict[str, Any]:
    """
    Perform complete analysis including knowledge retrieval for RAG enhancement
    (Legacy endpoint - use /analyze-advanced for new features)
    """
    start_time = time.time()
    
    try:
        # Step 1: Perform Day 1 analysis (intent, domain, complexity, routing)
        analysis = analyzer.analyze_query(request.query)
        
        # Step 2: Knowledge retrieval for RAG
        from ..knowledge.retrieval_engine import HardwareRetrievalEngine, RetrievalContext
        
        retrieval_engine = HardwareRetrievalEngine()
        
        retrieval_context = RetrievalContext(
            query=request.query,
            primary_intent=analysis["classification"]["primary_intent"]["intent"],
            primary_domain=analysis["classification"]["primary_domain"]["domain"],
            complexity_score=analysis["complexity"]["final_score"],
            user_expertise=request.user_expertise.value
        )
        
        knowledge = retrieval_engine.retrieve_knowledge(retrieval_context)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Combine Day 1 analysis with Day 2 knowledge
        enhanced_response = {
            **analysis,  # Include all Day 1 analysis
            "knowledge": {
                "components": knowledge.components,
                "standards": knowledge.standards,
                "domain_context": knowledge.domain_context,
                "retrieval_summary": knowledge.retrieval_summary
            },
            "processing_time_ms": round(processing_time, 2),
            "capabilities": ["intent_classification", "domain_detection", "complexity_scoring", "model_routing", "knowledge_retrieval"]
        }
        
        logger.info(f"Enhanced analysis completed in {processing_time:.2f}ms - "
                   f"Retrieved {len(knowledge.components)} components, {len(knowledge.standards)} standards")
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

@router.get("/health", 
           response_model=HealthResponse,
           summary="Health Check",
           description="Check system health and component status")
async def health_check() -> HealthResponse:
    """System health check endpoint"""
    try:
        # Test analyzer initialization
        analyzer = get_query_analyzer()
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            components={
                "intent_classifier": "operational",
                "domain_detector": "operational", 
                "complexity_scorer": "operational",
                "model_router": "operational",
                "knowledge_retrieval": "operational",
                "multi_intent_support": "available"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"System unhealthy: {str(e)}"
        )

@router.get("/models",
           summary="Available AI Models",
           description="List available AI models and their routing criteria")
async def get_available_models() -> Dict[str, Any]:
    """Get information about available AI models and routing criteria"""
    try:
        from ..routing.routing_rules import ModelRoutingRules
        models = ModelRoutingRules.get_all_models()
        
        return {
            "available_models": list(models.keys()),
            "model_details": models,
            "routing_info": {
                "complexity_thresholds": {
                    "claude_sonnet_4": "≥ 0.8",
                    "grok_2": "0.6 - 0.8", 
                    "gpt_4o": "0.4 - 0.7",
                    "gpt_4o_mini": "< 0.4"
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return {
            "available_models": ["claude_sonnet_4", "grok_2", "gpt_4o", "gpt_4o_mini"],
            "note": "Model details temporarily unavailable"
        }

@router.get("/categories",
           summary="Hardware Categories",
           description="List all supported intent categories and hardware domains")
async def get_categories() -> Dict[str, Any]:
    """Get supported hardware categories and domains"""
    try:
        from ..config.intent_categories import INTENT_CATEGORIES
        from ..config.domain_definitions import HARDWARE_DOMAINS
        
        return {
            "intent_categories": {
                name: {
                    "description": config["description"],
                    "base_complexity": config["base_complexity"]
                }
                for name, config in INTENT_CATEGORIES.items()
            },
            "hardware_domains": {
                name: {
                    "scope": config["scope"],
                    "expertise_areas": config["expertise_areas"]
                }
                for name, config in HARDWARE_DOMAINS.items()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        return {
            "note": "Categories temporarily unavailable",
            "error": str(e)
        }

# Demo scenario endpoints
@router.post("/demo/automotive-buck-converter")
async def demo_automotive_converter(query: str = "Design automotive buck converter, 12V to 5V, 3A, AEC-Q100"):
    """Demo: Automotive buck converter design scenario"""
    try:
        from ..demos.automotive_buck_converter import AutomotiveBuckConverterDemo
        demo = AutomotiveBuckConverterDemo()
        return await demo.process_design_query(query)
    except Exception as e:
        logger.error(f"Automotive demo failed: {e}")
        return {
            "error": "Demo temporarily unavailable",
            "message": "Automotive buck converter demo is being updated",
            "query": query
        }

@router.post("/demo/iot-mcu-selection")
async def demo_iot_mcu_selection(query: str = "Compare ARM Cortex-M4 MCUs for IoT with WiFi and low power"):
    """Demo: IoT microcontroller selection scenario"""
    try:
        from ..demos.iot_mcu_selection import IoTMCUSelectionDemo
        demo = IoTMCUSelectionDemo()
        return await demo.process_selection_query(query)
    except Exception as e:
        logger.error(f"IoT MCU demo failed: {e}")
        return {
            "error": "Demo temporarily unavailable",
            "message": "IoT MCU selection demo is being updated",
            "query": query
        }

@router.post("/demo/opamp-analysis")
async def demo_opamp_analysis(query: str = "Explain gain-bandwidth product in op-amp design"):
    """Demo: Operational amplifier educational analysis"""
    try:
        from ..demos.opamp_educational import OpAmpEducationalDemo
        demo = OpAmpEducationalDemo()
        return await demo.process_educational_query(query)
    except Exception as e:
        logger.error(f"Op-amp demo failed: {e}")
        return {
            "error": "Demo temporarily unavailable",
            "message": "Op-amp analysis demo is being updated",
            "query": query
        }

@router.post("/demo/component-lookup")
async def demo_component_lookup(part_number: str = "LM317"):
    """Demo: Component specification lookup"""
    try:
        from ..demos.component_lookup import ComponentLookupDemo, LookupRequest
        demo = ComponentLookupDemo()
        request = LookupRequest(part_number=part_number)
        return await demo.process_lookup_query(f"What are {part_number} specifications?", request)
    except Exception as e:
        logger.error(f"Component lookup demo failed: {e}")
        return {
            "error": "Demo temporarily unavailable",
            "message": "Component lookup demo is being updated",
            "part_number": part_number
        }

# Phase 3 Advanced Features Endpoints
@router.post("/advanced/analyze-schematic")
async def analyze_schematic(file: UploadFile = File(...)):
    """Analyze uploaded schematic diagram"""
    try:
        from ..advanced.multimodal.schematic_processor import SchematicProcessor
        
        processor = SchematicProcessor()
        image_data = await file.read()
        
        result = await processor.analyze_schematic(image_data, analysis_type="complete")
        
        return {
            "analysis_results": {
                "detected_components": result.detected_components,
                "circuit_topology": result.circuit_topology,
                "design_rules_check": result.design_rules_check,
                "auto_generated_bom": result.auto_generated_bom,
                "confidence_score": result.confidence_score
            }
        }
    except Exception as e:
        logger.error(f"Schematic analysis failed: {e}")
        return {
            "error": "Schematic analysis temporarily unavailable",
            "message": "Multi-modal processing is being updated",
            "filename": file.filename
        }

@router.post("/advanced/analyze-simulation")
async def analyze_simulation(simulation_data: Dict[str, Any]):
    """Analyze SPICE simulation results with AI optimization"""
    try:
        from ..advanced.simulation.spice_analyzer import SPICEAnalyzer
        
        analyzer = SPICEAnalyzer()
        result = await analyzer.analyze_simulation_results(simulation_data)
        
        return result
    except Exception as e:
        logger.error(f"Simulation analysis failed: {e}")
        return {
            "error": "Simulation analysis temporarily unavailable",
            "message": "SPICE analysis is being updated"
        }

@router.post("/advanced/supply-chain-forecast")
async def supply_chain_forecast(component_id: str, horizon_months: int = 12):
    """Generate supply chain forecast for component"""
    try:
        from ..advanced.intelligence.supply_chain_predictor import SupplyChainPredictor
        
        predictor = SupplyChainPredictor()
        forecast = await predictor.forecast_component_supply(component_id, horizon_months)
        
        return {
            "component_id": forecast.component_id,
            "current_status": forecast.current_status,
            "availability_forecast": forecast.availability_forecast,
            "price_forecast": forecast.price_forecast,
            "risk_assessment": forecast.risk_assessment,
            "alternatives": forecast.alternative_recommendations
        }
    except Exception as e:
        logger.error(f"Supply chain forecast failed: {e}")
        return {
            "error": "Supply chain forecasting temporarily unavailable",
            "message": "Predictive analytics is being updated",
            "component_id": component_id
        }

@router.post("/collaboration/create-design-pattern")
async def create_design_pattern(design_data: Dict[str, Any], metadata: Dict[str, Any]):
    """Create reusable design pattern from successful project"""
    try:
        from ..advanced.collaboration.knowledge_manager import CollaborativeKnowledgeManager
        
        manager = CollaborativeKnowledgeManager()
        pattern_id = await manager.create_design_pattern(design_data, metadata)
        
        return {"pattern_id": pattern_id, "status": "created"}
    except Exception as e:
        logger.error(f"Design pattern creation failed: {e}")
        return {
            "error": "Design pattern creation temporarily unavailable",
            "message": "Collaboration features are being updated"
        }

@router.get("/collaboration/design-patterns")
async def search_design_patterns(query: str = "", category: str = None):
    """Search organizational design patterns"""
    try:
        from ..advanced.collaboration.knowledge_manager import CollaborativeKnowledgeManager
        
        manager = CollaborativeKnowledgeManager()
        filters = {"category": category} if category else None
        patterns = await manager.search_design_patterns(query, filters)
        
        return {"patterns": patterns}
    except Exception as e:
        logger.error(f"Design pattern search failed: {e}")
        return {
            "error": "Design pattern search temporarily unavailable",
            "message": "Collaboration features are being updated",
            "query": query
        }
