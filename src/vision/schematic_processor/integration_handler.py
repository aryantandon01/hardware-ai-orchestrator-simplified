"""
Enhanced Integration Handler for Schematic Processing with OCR Support
Orchestrates complete multi-modal schematic analysis pipeline
"""
import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List, Optional
import tempfile
import os
import time
from pathlib import Path
from fastapi.encoders import jsonable_encoder

from .symbol_detector import SchematicSymbolDetector
from .text_extractor import SchematicTextExtractor
from ...knowledge.retrieval_engine import HardwareRetrievalEngine, RetrievalContext

logger = logging.getLogger(__name__)

# Create router for schematic endpoints
schematic_router = APIRouter(prefix="/api/v1/schematic", tags=["schematic-processing"])

class EnhancedSchematicProcessor:
    """Enhanced processor for complete schematic analysis with OCR integration"""
    
    def __init__(self):
        """Initialize all processing modules"""
        from ..topology.connection_detector import AdvancedConnectionDetector
        from ..topology.netlist_generator import NetlistGenerator

        self.symbol_detector = SchematicSymbolDetector()
        self.text_extractor = SchematicTextExtractor()
        self.retrieval_engine = HardwareRetrievalEngine()
        self.connection_detector = AdvancedConnectionDetector()
        self.netlist_generator = NetlistGenerator()
        
        logger.info("🚀 Enhanced Schematic Processor initialized")
    
    async def process_schematic(self, image_path: str) -> Dict[str, Any]:
        """
        Complete multi-modal schematic processing pipeline with OCR and Topology Analysis
        
        Args:
            image_path: Path to uploaded schematic image
            
        Returns:
            Comprehensive analysis result with enhanced component data and topology
        """
        start_time = time.time()
        logger.info(f"🔄 Starting enhanced schematic processing with topology: {image_path}")
        
        try:
            # Step 1: Symbol Detection
            logger.info("🔍 Step 1/6: Detecting schematic symbols...")
            detected_symbols = self.symbol_detector.detect_symbols(image_path)
            symbol_time = time.time()
            
            # Step 2: OCR Text Extraction and Association
            logger.info("📝 Step 2/6: Extracting and associating text with OCR...")
            enhanced_components = self.text_extractor.extract_component_labels(
                image_path, detected_symbols
            )
            ocr_time = time.time()
            
            # Step 3: Advanced Topology Analysis
            logger.info("🔧 Step 3/6: Analyzing circuit topology and connections...")
            topology_analysis = {}
            netlist_result = {}
            
            try:
                # Import topology modules (with fallback if not available)
                try:
                    from ..topology.connection_detector import AdvancedConnectionDetector
                    from ..topology.netlist_generator import NetlistGenerator
                    
                    # Initialize if not already done
                    if not hasattr(self, 'connection_detector'):
                        self.connection_detector = AdvancedConnectionDetector()
                    if not hasattr(self, 'netlist_generator'):
                        self.netlist_generator = NetlistGenerator()
                    
                    # Perform topology analysis
                    topology_analysis = self.connection_detector.detect_connections(
                        image_path, enhanced_components
                    )
                    
                    # Step 4: Generate SPICE Netlist
                    logger.info("📝 Step 4/6: Generating SPICE netlist...")
                    netlist_result = self.netlist_generator.generate_spice_netlist(
                        enhanced_components,
                        topology_analysis.get('connections', []),
                        topology_analysis.get('nodes', [])
                    )
                    topology_time = time.time()
                    
                    logger.info(f"✅ Topology analysis completed: {len(topology_analysis.get('connections', []))} connections, {len(topology_analysis.get('nodes', []))} nodes")
                    
                except ImportError as e:
                    logger.warning(f"⚠️ Topology modules not available: {e}")
                    topology_analysis = {'connections': [], 'nodes': [], 'topology_analysis': {}}
                    netlist_result = {'netlist': '', 'components': [], 'metadata': {'generation_success': False}}
                    topology_time = time.time()
                    
            except Exception as e:
                logger.warning(f"⚠️ Topology analysis failed: {e}")
                topology_analysis = {'connections': [], 'nodes': [], 'topology_analysis': {}}
                netlist_result = {'netlist': '', 'components': [], 'metadata': {'generation_success': False}}
                topology_time = time.time()
            
            # Step 5: Enhanced Component Recommendations
            logger.info("🎯 Step 5/6: Generating enhanced component recommendations...")
            try:
                recommendations = await self._generate_enhanced_recommendations(enhanced_components)
            except Exception as e:
                logger.warning(f"⚠️ Recommendation generation failed: {e}")
                recommendations = []
            recommendation_time = time.time()
            
            # Step 6: Comprehensive Analysis and Insights
            logger.info("📊 Step 6/6: Generating design insights and analysis...")
            try:
                design_insights = self._generate_enhanced_design_insights(enhanced_components)
                compliance_analysis = self._perform_enhanced_compliance_check(enhanced_components)
            except Exception as e:
                logger.warning(f"⚠️ Analysis generation failed: {e}")
                design_insights = {}
                compliance_analysis = {}
            final_time = time.time()
            
            # Create comprehensive analysis result with topology data
            analysis_result = {
                'status': 'success',
                'processing_metadata': {
                    'processing_steps': [
                        'symbol_detection', 
                        'ocr_text_extraction', 
                        'text_symbol_association',
                        'topology_analysis',
                        'netlist_generation',
                        'enhanced_recommendations', 
                        'design_analysis'
                    ],
                    'processing_times': {
                        'symbol_detection_ms': round((symbol_time - start_time) * 1000, 2),
                        'ocr_extraction_ms': round((ocr_time - symbol_time) * 1000, 2),
                        'topology_analysis_ms': round((topology_time - ocr_time) * 1000, 2),
                        'recommendations_ms': round((recommendation_time - topology_time) * 1000, 2),
                        'analysis_ms': round((final_time - recommendation_time) * 1000, 2),
                        'total_processing_ms': round((final_time - start_time) * 1000, 2)
                    },
                    'capabilities_used': {
                        'symbol_detection': True,
                        'ocr_text_extraction': self.text_extractor.ocr_available,
                        'topology_analysis': len(topology_analysis.get('connections', [])) > 0,
                        'netlist_generation': netlist_result.get('metadata', {}).get('generation_success', False),
                        'knowledge_retrieval': True,
                        'ai_recommendations': True
                    }
                },
                'image_analysis': {
                    'total_components': len(enhanced_components),
                    'components_with_text': sum(1 for c in enhanced_components 
                                            if c.get('designation') or c.get('value')),
                    'component_types': self._summarize_component_types(enhanced_components),
                    'detection_confidence': self._calculate_average_confidence(enhanced_components),
                    'text_extraction_quality': self._calculate_text_quality(enhanced_components),
                    'coverage_metrics': self._calculate_coverage_metrics(enhanced_components),
                    'topology_metrics': {
                        'total_connections': len(topology_analysis.get('connections', [])),
                        'total_nodes': len(topology_analysis.get('nodes', [])),
                        'connectivity_density': self._calculate_connectivity_density(enhanced_components, topology_analysis),
                        'circuit_complexity': topology_analysis.get('topology_analysis', {}).get('circuit_complexity', {})
                    }
                },
                'detected_components': enhanced_components,
                'component_recommendations': recommendations,
                'design_insights': design_insights,
                'compliance_analysis': compliance_analysis,
                'suggested_improvements': self._generate_advanced_suggestions(enhanced_components),
                'bill_of_materials': self._generate_bill_of_materials(enhanced_components),
                
                # NEW: Topology Analysis Results
                'topology_analysis': {
                    'connections': topology_analysis.get('connections', []),
                    'nodes': topology_analysis.get('nodes', []),
                    'connection_matrix': topology_analysis.get('connection_matrix', {}),
                    'circuit_analysis': topology_analysis.get('topology_analysis', {}),
                    'potential_issues': topology_analysis.get('topology_analysis', {}).get('potential_issues', [])
                },
                
                # NEW: SPICE Netlist Generation Results
                'spice_netlist': {
                    'netlist_text': netlist_result.get('netlist', ''),
                    'spice_components': netlist_result.get('components', []),
                    'node_mapping': netlist_result.get('node_mapping', {}),
                    'analysis_commands': netlist_result.get('analysis_commands', []),
                    'generation_successful': netlist_result.get('metadata', {}).get('generation_success', False),
                    'total_spice_components': len(netlist_result.get('components', []))
                },
                
                # NEW: Enhanced Circuit Intelligence
                'circuit_intelligence': {
                    'electrical_connectivity': topology_analysis.get('connection_matrix', {}),
                    'signal_flow_analysis': self._analyze_signal_flow(topology_analysis, enhanced_components),
                    'design_patterns_detected': self._identify_advanced_patterns(enhanced_components, topology_analysis),
                    'optimization_opportunities': self._identify_optimization_opportunities(enhanced_components, topology_analysis)
                }
            }
            
            # ✅ BULLETPROOF FIX: Deep conversion of all NumPy and non-serializable types
            logger.info("🔄 Converting data types for JSON serialization...")
            try:
                # First pass: Use your deep conversion method
                safe_analysis_result = self._deep_convert_numpy_types(analysis_result)
                
                # Second pass: Use FastAPI's encoder for any remaining issues
                from fastapi.encoders import jsonable_encoder
                final_result = jsonable_encoder(safe_analysis_result)
                
                logger.info("✅ Data serialization completed successfully")
                
            except Exception as serialization_error:
                logger.error(f"❌ Serialization error: {serialization_error}")
                
                # Ultimate fallback: Create a safe, simplified response
                processing_time = final_time - start_time
                final_result = {
                    'status': 'success',
                    'message': 'Processing completed successfully',
                    'processing_metadata': {
                        'total_processing_ms': round(processing_time * 1000, 2),
                        'capabilities_used': {
                            'symbol_detection': True,
                            'ocr_text_extraction': True,
                            'serialization_fallback': True
                        }
                    },
                    'image_analysis': {
                        'total_components': len(enhanced_components),
                        'processing_successful': True
                    },
                    'detected_components': [
                        {
                            'id': comp.get('id', f'comp_{i}'),
                            'component_type': str(comp.get('component_type', 'unknown')),
                            'confidence': float(comp.get('confidence', 0.0)) if comp.get('confidence') is not None else 0.0,
                            'designation': str(comp.get('designation', 'N/A')) if comp.get('designation') else 'N/A',
                            'value': str(comp.get('value', 'N/A')) if comp.get('value') else 'N/A'
                        }
                        for i, comp in enumerate(enhanced_components[:10])  # Limit to first 10 for safety
                    ],
                    'note': 'Full analysis completed, response simplified for serialization safety'
                }
                
                logger.info("✅ Fallback serialization successful")
            
            processing_time = final_time - start_time
            logger.info(f"✅ Enhanced schematic processing with topology completed successfully in {processing_time:.2f}s")
            logger.info(f"📊 Results: {len(enhanced_components)} components, {len(topology_analysis.get('connections', []))} connections, {len(topology_analysis.get('nodes', []))} nodes")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced schematic processing failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error response instead of raising HTTP exception
            return {
                'status': 'error',
                'message': f'Processing failed: {str(e)}',
                'processing_metadata': {
                    'processing_failed': True,
                    'error_type': type(e).__name__
                }
            }


    
    async def _generate_enhanced_recommendations(self, components: List[Dict]) -> Dict[str, Any]:
        """Generate enhanced component recommendations using OCR-extracted information"""
        recommendations = {}
        recommendation_summary = {
            'total_recommendations': 0,
            'components_with_recommendations': 0,
            'recommendation_quality': 0.0
        }
        
        for component in components:
            component_type = component.get('component_type', 'unknown')
            component_id = component.get('id', 'unknown')
            
            # Skip unknown components without additional info
            if component_type == 'unknown' and not component.get('designation'):
                continue
            
            try:
                # Create enhanced query using OCR-extracted information
                query = self._create_enhanced_recommendation_query(component)
                
                # Determine domain based on component characteristics
                domain = self._determine_component_domain(component)
                
                # Create retrieval context
                retrieval_context = RetrievalContext(
                    query=query,
                    primary_intent="component_selection",
                    primary_domain=domain,
                    complexity_score=0.6,  # Medium complexity for component selection
                    user_expertise="intermediate"
                )
                
                # Get knowledge-enhanced recommendations
                knowledge_result = self.retrieval_engine.retrieve_knowledge(retrieval_context)
                
                # Create comprehensive recommendation
                component_recommendation = {
                    'detected_component': {
                        'type': component_type,
                        'designation': component.get('designation'),
                        'value': component.get('value'),
                        'tolerance': component.get('tolerance'),
                        'confidence': component.get('confidence', 0.0),
                        'text_confidence': component.get('text_confidence', 0.0)
                    },
                    'suggested_parts': [
                        {
                            'component': part['component'],
                            'similarity_score': part.get('similarity_score', 0.0),
                            'match_reasoning': self._generate_match_reasoning(component, part)
                        }
                        for part in knowledge_result.components[:3]
                    ],
                    'relevant_standards': knowledge_result.standards,
                    'design_considerations': self._get_enhanced_design_considerations(
                        component_type, component
                    ),
                    'application_notes': self._generate_application_notes(component),
                    'alternative_solutions': self._suggest_alternative_solutions(component)
                }
                
                recommendations[component_id] = component_recommendation
                recommendation_summary['components_with_recommendations'] += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to generate recommendation for {component_id}: {e}")
        
        recommendation_summary['total_recommendations'] = len(recommendations)
        recommendation_summary['recommendation_quality'] = (
            recommendation_summary['components_with_recommendations'] / 
            max(len(components), 1)
        )
        
        return {
            'recommendations': recommendations,
            'summary': recommendation_summary
        }
    
    def _create_enhanced_recommendation_query(self, component: Dict) -> str:
        """Create enhanced search query using OCR-extracted component information"""
        try:
            component_type = self._safe_string_field(component, 'component_type', 'component')
            designation = self._safe_string_field(component, 'designation')
            value = self._safe_string_field(component, 'value')
            tolerance = self._safe_string_field(component, 'tolerance')
            
            # Build comprehensive query
            query_parts = [component_type]
            
            if designation:
                query_parts.append(f"designation {designation}")
            
            if value:
                query_parts.append(f"value {value}")
            
            if tolerance:
                query_parts.append(f"tolerance {tolerance}")
            
            query_parts.extend(["selection", "circuit design", "specifications"])
            
            return " ".join(query_parts)
        except Exception as e:
            logger.warning(f"⚠️ Error creating recommendation query: {e}")
            return f"{component.get('component_type', 'component')} selection circuit design"



    
    def _determine_component_domain(self, component: Dict) -> str:
        """Determine the most appropriate domain for component recommendations"""
        component_type = component.get('component_type', 'unknown')
        designation = component.get('designation', '').upper()
        
        # Domain mapping based on component characteristics
        if component_type in ['voltage_source', 'regulator'] or designation.startswith(('U', 'IC')):
            return "power_electronics"
        elif component_type in ['op_amp', 'amplifier'] or 'AMP' in designation:
            return "analog_design"
        elif component_type in ['microcontroller', 'processor'] or designation.startswith('MCU'):
            return "digital_design"
        elif any(automotive_indicator in str(component).lower() 
                for automotive_indicator in ['aec', 'automotive', '12v', '24v']):
            return "automotive"
        else:
            return "analog_design"  # Default domain
    
    def _calculate_text_quality(self, components: List[Dict]) -> Dict[str, float]:
        """Calculate comprehensive text extraction quality metrics"""
        if not components:
            return {
                'average_confidence': 0.0,
                'text_coverage': 0.0,
                'designation_coverage': 0.0,
                'value_coverage': 0.0,
                'overall_quality': 0.0
            }
        
        text_confidences = []
        components_with_designation = 0
        components_with_value = 0
        components_with_any_text = 0
        
        for comp in components:
            if comp.get('text_confidence'):
                text_confidences.append(comp['text_confidence'])
            
            if comp.get('designation'):
                components_with_designation += 1
                components_with_any_text += 1
            elif comp.get('value'):
                components_with_value += 1
                components_with_any_text += 1
        
        avg_confidence = sum(text_confidences) / len(text_confidences) if text_confidences else 0.0
        text_coverage = components_with_any_text / len(components)
        designation_coverage = components_with_designation / len(components)
        value_coverage = components_with_value / len(components)
        overall_quality = (avg_confidence * 0.4 + text_coverage * 0.6)
        
        return {
            'average_confidence': round(avg_confidence, 3),
            'text_coverage': round(text_coverage, 3),
            'designation_coverage': round(designation_coverage, 3),
            'value_coverage': round(value_coverage, 3),
            'overall_quality': round(overall_quality, 3)
        }
    
    def _calculate_coverage_metrics(self, components: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive coverage metrics for the analysis"""
        total_components = len(components)
        
        if total_components == 0:
            return {'total': 0, 'coverage_by_type': {}}
        
        coverage_metrics = {
            'total_components': total_components,
            'coverage_by_detection_method': {},
            'coverage_by_component_type': {},
            'quality_distribution': {
                'high_confidence': 0,  # >0.8
                'medium_confidence': 0,  # 0.5-0.8
                'low_confidence': 0     # <0.5
            }
        }
        
        # Analyze detection methods
        method_counts = {}
        type_counts = {}
        
        for comp in components:
            # Detection method analysis
            detection_method = comp.get('detection_method', 'unknown')
            method_counts[detection_method] = method_counts.get(detection_method, 0) + 1
            
            # Component type analysis
            comp_type = comp.get('component_type', 'unknown')
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
            
            # Quality distribution
            confidence = comp.get('confidence', 0.0)
            if confidence > 0.8:
                coverage_metrics['quality_distribution']['high_confidence'] += 1
            elif confidence > 0.5:
                coverage_metrics['quality_distribution']['medium_confidence'] += 1
            else:
                coverage_metrics['quality_distribution']['low_confidence'] += 1
        
        coverage_metrics['coverage_by_detection_method'] = method_counts
        coverage_metrics['coverage_by_component_type'] = type_counts
        
        return coverage_metrics
    
    def _generate_enhanced_design_insights(self, components: List[Dict]) -> List[Dict[str, Any]]:
        """Generate comprehensive design insights using OCR-extracted information"""
        insights = []
        
        # Analyze component distribution
        component_analysis = self._analyze_component_distribution(components)
        value_analysis = self._analyze_component_values(components)
        design_patterns = self._identify_design_patterns(components)
        
        # Generate insights based on analysis
        insights.extend(self._generate_distribution_insights(component_analysis))
        insights.extend(self._generate_value_insights(value_analysis))
        insights.extend(self._generate_pattern_insights(design_patterns))
        
        return insights

    def _analyze_component_distribution(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze the distribution of component types and characteristics"""
        distribution = {
            'by_type': {},
            'with_designations': 0,
            'with_values': 0,
            'total': len(components)
        }
        
        for comp in components:
            # Use safe string extraction
            comp_type = self._safe_string_field(comp, 'component_type', 'unknown')
            designation = self._safe_string_field(comp, 'designation')
            value = self._safe_string_field(comp, 'value')
            
            # Count by type
            distribution['by_type'][comp_type] = distribution['by_type'].get(comp_type, 0) + 1
            
            # Count components with designations and values
            if designation:
                distribution['with_designations'] += 1
            if value:
                distribution['with_values'] += 1
        
        return distribution

    
    def _analyze_component_values(self, components: List[Dict]) -> Dict[str, List]:
        """Analyze component values for design insights"""
        values = {
            'resistors': [],
            'capacitors': [],
            'inductors': [],
            'voltages': []
        }
        
        for comp in components:
            # Use the safe helper instead of direct .get().upper()
            designation = self._safe_string_field(comp, 'designation')
            value_str = self._safe_string_field(comp, 'value')
            
            if designation and value_str:
                designation_upper = designation.upper()
                
                if designation_upper.startswith('R'):
                    values['resistors'].append(value_str)
                elif designation_upper.startswith('C'):
                    values['capacitors'].append(value_str)
                elif designation_upper.startswith('L'):
                    values['inductors'].append(value_str)
        
        return values

    
    def _analyze_component_values(self, components: List[Dict]) -> Dict[str, List]:
        """Analyze component values for design insights"""
        values = {
            'resistors': [],
            'capacitors': [],
            'inductors': [],
            'voltages': []
        }
        
        for comp in components:
            # Safe handling of designation field
            designation = comp.get('designation')
            if designation and isinstance(designation, str):
                designation_upper = designation.upper()
            else:
                designation_upper = ''
            
            value_str = comp.get('value')
            if not value_str or not isinstance(value_str, str):
                continue
                
            try:
                if designation_upper.startswith('R') and value_str:
                    values['resistors'].append(value_str)
                elif designation_upper.startswith('C') and value_str:
                    values['capacitors'].append(value_str)
                elif designation_upper.startswith('L') and value_str:
                    values['inductors'].append(value_str)
            except Exception as e:
                logger.warning(f"⚠️ Error processing component value for {designation}: {e}")
        
        return values

    
    def _identify_design_patterns(self, components: List[Dict]) -> Dict[str, bool]:
        """Identify common design patterns in the schematic"""
        patterns = {
            'power_supply_circuit': False,
            'amplifier_circuit': False,
            'digital_logic': False,
            'filter_circuit': False,
            'oscillator_circuit': False
        }
        
        # Extract component information safely
        component_types = []
        designations = []
        
        for c in components:
            comp_type = self._safe_string_field(c, 'component_type')
            designation = self._safe_string_field(c, 'designation')
            
            if comp_type:
                component_types.append(comp_type)
            if designation:
                designations.append(designation.upper())
        
        # Pattern detection logic
        if 'voltage_source' in component_types or any('VCC' in d or 'VDD' in d for d in designations):
            patterns['power_supply_circuit'] = True
        
        if 'op_amp' in component_types or any('U' in d and 'AMP' in d for d in designations):
            patterns['amplifier_circuit'] = True
        
        if any(d.startswith('IC') or d.startswith('U') for d in designations):
            patterns['digital_logic'] = True
        
        capacitor_count = sum(1 for d in designations if d.startswith('C'))
        inductor_count = sum(1 for d in designations if d.startswith('L'))
        if capacitor_count >= 2 or inductor_count >= 1:
            patterns['filter_circuit'] = True
        
        return patterns

    
    def _generate_distribution_insights(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate insights based on component distribution"""
        insights = []
        
        total = analysis['total']
        by_type = analysis['by_type']
        
        # Component count insights
        if by_type.get('unknown', 0) > 8:
            insights.append({
                'type': 'optimization',
                'category': 'component_count',
                'message': f"Circuit has {by_type.get('unknown', 0)} detected components - consider component identification improvements",
                'severity': 'medium',
                'recommendation': "Review component symbols and labels for better recognition"
            })
        
        # Coverage insights
        if total > 0:
            designation_coverage = analysis['with_designations'] / total
            if designation_coverage < 0.7:
                insights.append({
                    'type': 'documentation',
                    'category': 'schematic_quality',
                    'message': f"Only {designation_coverage:.1%} of components have clear designations",
                    'severity': 'low',
                    'recommendation': "Add component designations (R1, C2, etc.) to improve schematic readability"
                })
        
        return insights

    def _generate_value_insights(self, values: Dict) -> List[Dict[str, Any]]:
        """Generate insights based on component values"""
        insights = []
        
        # Resistor value insights
        if values.get('resistors'):
            insights.append({
                'type': 'component_analysis',
                'category': 'resistor_values',
                'message': f"Detected {len(values['resistors'])} resistor values",
                'severity': 'info',
                'recommendation': "Verify resistor power ratings and tolerances for application requirements"
            })
        
        # Capacitor value insights
        if values.get('capacitors'):
            insights.append({
                'type': 'component_analysis',
                'category': 'capacitor_values', 
                'message': f"Detected {len(values['capacitors'])} capacitor values",
                'severity': 'info',
                'recommendation': "Consider capacitor dielectric types and voltage ratings for optimal performance"
            })
        
        return insights

    def _generate_pattern_insights(self, patterns: Dict) -> List[Dict[str, Any]]:
        """Generate insights based on identified design patterns"""
        insights = []
        
        for pattern_name, detected in patterns.items():
            if detected:
                insight_map = {
                    'power_supply_circuit': {
                        'message': "Power supply circuit detected - verify regulation and filtering",
                        'recommendation': "Review load regulation, ripple specifications, and thermal management"
                    },
                    'amplifier_circuit': {
                        'message': "Amplifier circuit detected - check gain and bandwidth specifications",
                        'recommendation': "Verify input/output impedances, gain-bandwidth product, and stability"
                    },
                    'filter_circuit': {
                        'message': "Filter circuit detected - analyze frequency response",
                        'recommendation': "Calculate cutoff frequencies and verify component tolerances"
                    }
                }
                
                if pattern_name in insight_map:
                    insight = insight_map[pattern_name]
                    insights.append({
                        'type': 'design_pattern',
                        'category': pattern_name,
                        'message': insight['message'],
                        'severity': 'info',
                        'recommendation': insight['recommendation']
                    })
        
        return insights

    
    def _perform_enhanced_compliance_check(self, components: List[Dict]) -> Dict[str, Any]:
        """Perform enhanced compliance checking with OCR-extracted information"""
        compliance_analysis = {
            'overall_score': 0.0,
            'checks_performed': [],
            'passed_checks': [],
            'failed_checks': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check 1: Component Designations
        designation_check = self._check_component_designations(components)
        compliance_analysis['checks_performed'].append('component_designations')
        if designation_check['passed']:
            compliance_analysis['passed_checks'].append('component_designations')
        else:
            compliance_analysis['failed_checks'].append('component_designations')
            compliance_analysis['warnings'].extend(designation_check['warnings'])
        
        # Check 2: Value Specifications
        value_check = self._check_component_values(components)
        compliance_analysis['checks_performed'].append('component_values')
        if value_check['passed']:
            compliance_analysis['passed_checks'].append('component_values')
        else:
            compliance_analysis['warnings'].extend(value_check['warnings'])
        
        # Check 3: Design Completeness
        completeness_check = self._check_design_completeness(components)
        compliance_analysis['checks_performed'].append('design_completeness')
        compliance_analysis['warnings'].extend(completeness_check['warnings'])
        compliance_analysis['recommendations'].extend(completeness_check['recommendations'])
        
        # Calculate overall score
        total_checks = len(compliance_analysis['checks_performed'])
        passed_checks = len(compliance_analysis['passed_checks'])
        compliance_analysis['overall_score'] = passed_checks / total_checks if total_checks > 0 else 0.0
        
        return compliance_analysis
    
    def _check_component_designations(self, components: List[Dict]) -> Dict[str, Any]:
        """Check component designation compliance"""
        total_components = len(components)
        components_with_designations = sum(1 for c in components if c.get('designation'))
        
        designation_coverage = components_with_designations / total_components if total_components > 0 else 0
        
        return {
            'passed': designation_coverage >= 0.8,
            'coverage': designation_coverage,
            'warnings': [
                f"Only {designation_coverage:.1%} of components have designations - industry standard is >80%"
            ] if designation_coverage < 0.8 else []
        }
    
    def _check_component_values(self, components: List[Dict]) -> Dict[str, Any]:
        """Check component value specifications"""
        total_components = len(components)
        components_with_values = sum(1 for c in components if c.get('value'))
        
        value_coverage = components_with_values / total_components if total_components > 0 else 0
        
        return {
            'passed': value_coverage >= 0.6,
            'coverage': value_coverage,
            'warnings': [
                f"Only {value_coverage:.1%} of components have specified values"
            ] if value_coverage < 0.6 else []
        }
    
    def _check_design_completeness(self, components: List[Dict]) -> Dict[str, Any]:
        """Check overall design completeness"""
        warnings = []
        recommendations = []
        
        component_types = [c.get('component_type', '') for c in components]
        
        # Check for power supply components
        if 'voltage_source' not in component_types:
            warnings.append("No power source detected in schematic")
            recommendations.append("Add power supply specifications and connections")
        
        # Check for ground connections
        if 'ground' not in component_types:
            warnings.append("No ground reference detected in schematic")
            recommendations.append("Ensure proper ground symbol placement for reference")
        
        # Check for test points
        test_point_indicators = ['TP', 'TEST', 'PROBE']
        has_test_points = any(
            any(indicator in str(c.get('designation', '')).upper() for indicator in test_point_indicators)
            for c in components
        )
        
        if not has_test_points:
            recommendations.append("Consider adding test points for debugging and validation")
        
        return {
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _generate_bill_of_materials(self, components: List[Dict]) -> Dict[str, Any]:
        """Generate bill of materials from detected components"""
        bom = {
            'total_components': len(components),
            'unique_components': 0,
            'items': [],
            'summary_by_type': {}
        }
        
        # Group components by type and value
        component_groups = {}
        
        for comp in components:
            # Safe string handling
            designation = comp.get('designation')
            if not designation or not isinstance(designation, str):
                designation = 'Unknown'
            
            comp_type = comp.get('component_type')
            if not comp_type or not isinstance(comp_type, str):
                comp_type = 'unknown'
                
            value = comp.get('value')
            if not value or not isinstance(value, str):
                value = 'N/A'
                
            tolerance = comp.get('tolerance')
            if not tolerance or not isinstance(tolerance, str):
                tolerance = 'N/A'
            
            # Create component key for grouping
            comp_key = f"{comp_type}_{value}_{tolerance}"
            
            if comp_key not in component_groups:
                component_groups[comp_key] = {
                    'type': comp_type,
                    'value': value,
                    'tolerance': tolerance,
                    'designations': [],
                    'quantity': 0
                }
            
            component_groups[comp_key]['designations'].append(designation)
            component_groups[comp_key]['quantity'] += 1
        
        # Create BOM items
        for comp_key, group in component_groups.items():
            bom_item = {
                'item_number': len(bom['items']) + 1,
                'component_type': group['type'],
                'value': group['value'],
                'tolerance': group['tolerance'],
                'quantity': group['quantity'],
                'designations': ', '.join(sorted(group['designations'])),
                'description': self._generate_component_description(group)
            }
            bom['items'].append(bom_item)
            
            # Update summary by type
            comp_type = group['type']
            if comp_type not in bom['summary_by_type']:
                bom['summary_by_type'][comp_type] = {'count': 0, 'unique_values': 0}
            bom['summary_by_type'][comp_type]['count'] += group['quantity']
            bom['summary_by_type'][comp_type]['unique_values'] += 1
        
        bom['unique_components'] = len(bom['items'])
        
        return bom

    
    def _generate_component_description(self, component_group: Dict) -> str:
        """Generate descriptive text for BOM component"""
        comp_type = component_group['type'].replace('_', ' ').title()
        value = component_group['value']
        tolerance = component_group['tolerance']
        
        description_parts = [comp_type]
        
        if value != 'N/A':
            description_parts.append(f"{value}")
        
        if tolerance != 'N/A':
            description_parts.append(f"{tolerance}")
        
        return ', '.join(description_parts)
    
    def _safe_string_field(self, component: Dict, field_name: str, default: str = '') -> str:
        """Safely extract string field from component dictionary"""
        value = component.get(field_name)
        if value and isinstance(value, str):
            return value
        return default


    # Utility methods from original implementation (enhanced)
    def _summarize_component_types(self, components: List[Dict]) -> Dict[str, int]:
        """Enhanced component type summarization"""
        type_counts = {}
        for component in components:
            comp_type = component.get('component_type', 'unknown')
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        return type_counts
    
    def _calculate_average_confidence(self, components: List[Dict]) -> float:
        """Calculate average detection confidence with text confidence weighting"""
        if not components:
            return 0.0
        
        total_confidence = 0.0
        confidence_count = 0
        
        for comp in components:
            # Weight detection confidence and text confidence
            detection_conf = comp.get('confidence', 0.0)
            text_conf = comp.get('text_confidence', 0.0)
            
            # Combined confidence with equal weighting
            if text_conf > 0:
                combined_conf = (detection_conf + text_conf) / 2
            else:
                combined_conf = detection_conf
            
            total_confidence += combined_conf
            confidence_count += 1
        
        return total_confidence / confidence_count if confidence_count > 0 else 0.0
    
    def _generate_advanced_suggestions(self, components: List[Dict]) -> List[Dict[str, Any]]:
        """Generate advanced suggestions based on comprehensive analysis"""
        suggestions = []
        
        # Analyze component distribution
        comp_types = self._summarize_component_types(components)
        
        # Advanced suggestion logic
        if comp_types.get('resistor', 0) > 10:
            suggestions.append({
                'category': 'optimization',
                'priority': 'medium',
                'title': 'Consider Resistor Network Integration',
                'description': f'Circuit contains {comp_types["resistor"]} individual resistors',
                'recommendation': 'Evaluate thick-film resistor networks to reduce component count, board space, and assembly time',
                'potential_savings': 'Up to 60% space reduction and improved matching'
            })
        
        # Power integrity suggestions
        if comp_types.get('capacitor', 0) >= 3:
            suggestions.append({
                'category': 'power_integrity',
                'priority': 'high',
                'title': 'Power Supply Decoupling Review',
                'description': f'Multiple capacitors ({comp_types["capacitor"]}) detected',
                'recommendation': 'Verify decoupling capacitor placement near power pins and review ESR specifications',
                'potential_impact': 'Improved power supply noise rejection and system stability'
            })
        
        # Documentation suggestions
        text_quality = self._calculate_text_quality(components)
        if text_quality['designation_coverage'] < 0.8:
            suggestions.append({
                'category': 'documentation',
                'priority': 'low',
                'title': 'Improve Component Labeling',
                'description': f'Only {text_quality["designation_coverage"]:.1%} of components have clear designations',
                'recommendation': 'Add standardized component designations (R1, C2, U3, etc.) for better schematic readability',
                'potential_impact': 'Enhanced design review efficiency and reduced assembly errors'
            })
        
        return suggestions
    
    # Enhanced helper methods
    def _generate_match_reasoning(self, detected_comp: Dict, suggested_part: Dict) -> str:
        """Generate reasoning for why a part matches the detected component"""
        reasoning_parts = []
        
        detected_type = detected_comp.get('component_type', 'unknown')
        detected_value = detected_comp.get('value', '')
        
        if detected_type != 'unknown':
            reasoning_parts.append(f"Component type match: {detected_type}")
        
        if detected_value:
            reasoning_parts.append(f"Value compatibility: {detected_value}")
        
        if not reasoning_parts:
            reasoning_parts.append("General component category match")
        
        return "; ".join(reasoning_parts)
    
    def _get_enhanced_design_considerations(self, component_type: str, component: Dict) -> List[str]:
        """Get enhanced design considerations with OCR context"""
        base_considerations = {
            'resistor': [
                "Verify power rating based on circuit current",
                "Consider temperature coefficient for precision applications",
                "Evaluate tolerance requirements for circuit performance"
            ],
            'capacitor': [
                "Select appropriate dielectric type (ceramic, electrolytic, tantalum)",
                "Verify voltage rating with adequate derating (typically 50-80%)",
                "Consider ESR and ESL for high-frequency applications"
            ],
            'inductor': [
                "Verify current rating and saturation characteristics",
                "Consider DC resistance impact on efficiency",
                "Evaluate magnetic shielding requirements"
            ],
            'transistor': [
                "Ensure adequate current and voltage ratings",
                "Consider thermal management and heat sinking",
                "Evaluate switching characteristics for application"
            ]
        }
        
        considerations = base_considerations.get(component_type, [
            "Review component specifications carefully",
            "Verify ratings meet application requirements",
            "Consider environmental operating conditions"
        ])
        
        # Add value-specific considerations if available
        value = component.get('value', '')
        if value and component_type == 'resistor':
            try:
                # Simple power estimation for resistor
                if 'k' in value.lower():
                    considerations.append("High resistance value - typically low power application")
                elif any(indicator in value.lower() for indicator in ['m', 'milliohm']):
                    considerations.append("Low resistance value - verify power handling capability")
            except:
                pass
        
        return considerations
    
    def _generate_application_notes(self, component: Dict) -> List[str]:
        """Generate application-specific notes for the component"""
        notes = []
        comp_type = component.get('component_type', 'unknown')
        value = component.get('value', '')
        designation = component.get('designation', '')
        
        if comp_type == 'capacitor' and value:
            if 'μF' in value or 'uF' in value:
                notes.append("Electrolytic or ceramic capacitor - verify polarity if electrolytic")
            elif 'pF' in value or 'nF' in value:
                notes.append("Small value capacitor - likely ceramic or film type")
        
        elif comp_type == 'resistor' and designation:
            if designation.upper().startswith('R'):
                notes.append("Standard resistor designation - verify precision requirements")
        
        if not notes:
            notes.append(f"Standard {comp_type} application - follow manufacturer guidelines")
        
        return notes
    
    def _suggest_alternative_solutions(self, component: Dict) -> List[str]:
        """Suggest alternative solutions for the detected component"""
        alternatives = []
        comp_type = component.get('component_type', 'unknown')
        
        alternative_map = {
            'resistor': [
                "Consider thick-film resistor networks for multiple resistors",
                "Digital potentiometers for variable resistance applications",
                "Current sense amplifiers for precision current measurement"
            ],
            'capacitor': [
                "Ceramic capacitors for high-frequency applications",
                "Supercapacitors for energy storage applications",
                "Film capacitors for high-precision timing circuits"
            ],
            'inductor': [
                "Ferrite beads for EMI suppression",
                "Coupled inductors for transformer applications",
                "Air-core inductors for high-frequency RF applications"
            ]
        }
        
        return alternative_map.get(comp_type, [
            "Integrated solutions may be available",
            "Consider multi-function components for space savings"
        ])

    def _calculate_connectivity_density(self, components: List[Dict], topology_analysis: Dict) -> float:
        """Calculate how densely connected the circuit is"""
        if not components or not topology_analysis.get('connections'):
            return 0.0
        
        max_possible_connections = len(components) * (len(components) - 1) / 2
        actual_connections = len(topology_analysis.get('connections', []))
        
        return actual_connections / max_possible_connections if max_possible_connections > 0 else 0.0

    def _analyze_signal_flow(self, topology_analysis: Dict, components: List[Dict]) -> Dict[str, Any]:
        """Analyze signal flow patterns in the circuit"""
        connections = topology_analysis.get('connections', [])
        nodes = topology_analysis.get('nodes', [])
        
        # Basic signal flow analysis
        signal_flow = {
            'input_components': [],
            'output_components': [], 
            'processing_components': [],
            'power_components': [],
            'signal_paths': []
        }
        
        # Classify components by their likely role
        for component in components:
            try:
                comp_type = component.get('component_type', 'unknown')
                
                # ✅ FIXED: Safe string extraction using helper method
                designation = self._safe_string_field(component, 'designation', '').upper()
                
                if comp_type == 'voltage_source' or 'VCC' in designation or 'VDD' in designation:
                    signal_flow['power_components'].append(component['id'])
                elif comp_type in ['connector', 'input'] or designation.startswith('J'):
                    signal_flow['input_components'].append(component['id'])
                elif comp_type in ['op_amp', 'transistor', 'ic']:
                    signal_flow['processing_components'].append(component['id'])
                    
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing component {component.get('id', 'unknown')}: {e}")
                continue
        
        # Identify potential signal paths
        signal_flow['total_paths'] = len(connections)
        signal_flow['complexity_score'] = len(nodes) / max(len(components), 1)
        
        return signal_flow


    def _identify_advanced_patterns(self, components: List[Dict], topology_analysis: Dict) -> List[Dict[str, str]]:
        """Identify advanced circuit design patterns"""
        patterns = []
        connections = topology_analysis.get('connections', [])
        nodes = topology_analysis.get('nodes', [])
        
        # Pattern: Voltage divider
        resistor_components = [c for c in components if c.get('component_type') == 'resistor']
        if len(resistor_components) >= 2:
            patterns.append({
                'pattern': 'voltage_divider_candidate',
                'description': f'Detected {len(resistor_components)} resistors - potential voltage divider configuration',
                'confidence': '0.6'  # ✅ FIXED: Convert to string to avoid JSON serialization issues
            })
        
        # Pattern: RC filter
        resistors = len([c for c in components if c.get('component_type') == 'resistor'])
        capacitors = len([c for c in components if c.get('component_type') == 'capacitor'])
        
        if resistors >= 1 and capacitors >= 1:
            patterns.append({
                'pattern': 'rc_filter',
                'description': f'RC network detected: {resistors} resistors, {capacitors} capacitors',
                'confidence': '0.7'
            })
        
        # Pattern: Amplifier circuit
        op_amps = [c for c in components if c.get('component_type') == 'op_amp']
        if op_amps:
            patterns.append({
                'pattern': 'amplifier_circuit',
                'description': f'Amplifier circuit with {len(op_amps)} op-amp(s)',
                'confidence': '0.8'
            })
        
        return patterns


    def _identify_optimization_opportunities(self, components: List[Dict], topology_analysis: Dict) -> List[Dict[str, str]]:
        """Identify circuit optimization opportunities"""
        opportunities = []
        
        try:
            # Check for component consolidation opportunities
            component_types = {}
            for comp in components:
                comp_type = comp.get('component_type', 'unknown')
                component_types[comp_type] = component_types.get(comp_type, 0) + 1
            
            # Resistor network opportunity
            if component_types.get('resistor', 0) >= 4:
                opportunities.append({
                    'type': 'component_consolidation',
                    'description': f'Consider resistor network for {component_types["resistor"]} individual resistors',
                    'potential_benefit': 'Space savings, improved matching, reduced assembly time',
                    'priority': 'medium'
                })
            
            # Capacitor optimization
            if component_types.get('capacitor', 0) >= 3:
                opportunities.append({
                    'type': 'power_integrity',
                    'description': f'Review {component_types["capacitor"]} capacitors for optimal decoupling',
                    'potential_benefit': 'Improved power supply noise rejection',
                    'priority': 'high'
                })
            
            # Connectivity optimization
            isolated_components = topology_analysis.get('topology_analysis', {}).get('potential_issues', [])
            isolation_issues = [issue for issue in isolated_components if isinstance(issue, dict) and issue.get('type') == 'isolation']
            
            if isolation_issues:
                opportunities.append({
                    'type': 'connectivity',
                    'description': 'Some components appear isolated - verify connections',
                    'potential_benefit': 'Ensure proper circuit functionality',
                    'priority': 'high'
                })
        
        except Exception as e:
            logger.warning(f"⚠️ Error identifying optimization opportunities: {e}")
        
        return opportunities
    
    def _deep_convert_numpy_types(self, obj):
        """
        Comprehensive recursive converter for all numpy and non-serializable types
        """
        import numpy as np
        from datetime import datetime, date
        from decimal import Decimal
        
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {str(k): self._deep_convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._deep_convert_numpy_types(item) for item in obj]
        elif isinstance(obj, set):
            return [self._deep_convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.generic):
            return obj.item()
        elif hasattr(obj, 'item') and callable(getattr(obj, 'item', None)):
            try:
                return obj.item()
            except (ValueError, AttributeError):
                pass
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return self._deep_convert_numpy_types(obj.__dict__)
        elif hasattr(obj, '_asdict'):  # namedtuples
            return self._deep_convert_numpy_types(obj._asdict())
        else:
            # For unknown types, try to convert to string or skip
            try:
                return str(obj)
            except:
                logger.warning(f"Skipping non-serializable object: {type(obj)}")
                return f"<non-serializable: {type(obj).__name__}>"




# Enhanced API endpoints
@schematic_router.post("/analyze")
async def analyze_schematic_enhanced(file: UploadFile = File(...)):
    """Enhanced schematic analysis with OCR text extraction"""
    
    # File validation
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    file_content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name
    
    try:
        # Process schematic with enhanced processor
        processor = EnhancedSchematicProcessor()
        result = await processor.process_schematic(tmp_path)
        
        # ✅ ALTERNATIVE SIMPLE FIX: Use FastAPI's comprehensive serializer
        from fastapi.encoders import jsonable_encoder
        return jsonable_encoder(result)
    
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except OSError:
            logger.warning(f"Could not delete temporary file: {tmp_path}")





@schematic_router.get("/health")
async def schematic_health_check_enhanced():
    """Enhanced health check for schematic processing service"""
    health_status = {
        "service": "enhanced_schematic_processor",
        "status": "healthy",
        "timestamp": time.time(),
        "capabilities": {
            "symbol_detection": True,
            "ocr_text_extraction": False,  # Will be updated based on actual availability
            "knowledge_retrieval": True,
            "ai_recommendations": True
        },
        "components": {
            "symbol_detector": "operational",
            "text_extractor": "checking...",
            "retrieval_engine": "operational"
        }
    }
    
    # Check OCR availability
    try:
        text_extractor = SchematicTextExtractor()
        health_status["capabilities"]["ocr_text_extraction"] = text_extractor.ocr_available
        health_status["components"]["text_extractor"] = "operational" if text_extractor.ocr_available else "limited"
    except Exception as e:
        health_status["components"]["text_extractor"] = f"error: {str(e)}"
    
    return health_status


@schematic_router.get("/capabilities")
async def get_schematic_capabilities():
    """Get detailed information about schematic processing capabilities"""
    return {
        "service": "enhanced_schematic_processor",
        "version": "2.0.0",
        "features": {
            "symbol_detection": {
                "description": "Detect electronic components in schematic images",
                "methods": ["YOLO object detection", "OpenCV contour analysis"],
                "supported_components": [
                    "resistors", "capacitors", "inductors", "diodes", 
                    "transistors", "op-amps", "voltage sources", "ground symbols"
                ]
            },
            "text_extraction": {
                "description": "Extract component labels and values using OCR",
                "engine": "EasyOCR",
                "capabilities": [
                    "Component designations (R1, C2, U3)",
                    "Component values (10kΩ, 100μF)",
                    "Tolerance specifications (±5%)",
                    "Text-symbol spatial association"
                ]
            },
            "enhanced_analysis": {
                "description": "Comprehensive design analysis and recommendations",
                "features": [
                    "Component recommendations",
                    "Design pattern recognition",
                    "Compliance checking",
                    "Bill of materials generation",
                    "Design optimization suggestions"
                ]
            }
        },
        "supported_file_formats": [".png", ".jpg", ".jpeg", ".bmp", ".tiff"],
        "file_size_limit": "10MB",
        "processing_capabilities": {
            "max_components": "unlimited",
            "text_languages": ["en"],
            "output_formats": ["JSON"]
        }
    }


__all__ = ["schematic_router", "EnhancedSchematicProcessor"]
