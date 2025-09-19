"""
End-to-End Pipeline Testing for Complete Schematic Processing
"""
import sys
import pathlib
import pytest
import cv2
import numpy as np
import os
import logging
import asyncio

# Add project root to Python path
project_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from src.vision.schematic_processor.integration_handler import EnhancedSchematicProcessor

class TestEndToEndPipeline:
    """Test complete schematic processing pipeline"""
    
    def test_complete_pipeline_with_synthetic_schematic(self):
        """Test the complete pipeline with a synthetic schematic containing symbols and text"""
        # Enable detailed logging
        logging.basicConfig(level=logging.INFO)
        
        # Create comprehensive synthetic schematic
        test_image = self._create_comprehensive_test_schematic()
        test_image_path = "test_complete_schematic.png"
        cv2.imwrite(test_image_path, test_image)
        
        try:
            processor = EnhancedSchematicProcessor()
            
            # Run complete processing pipeline
            result = asyncio.run(processor.process_schematic(test_image_path))
            
            # Validate pipeline results
            self._validate_pipeline_results(result)
            
            print("✅ Complete end-to-end pipeline test passed!")
            
        finally:
            # Cleanup
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
    
    def _create_comprehensive_test_schematic(self) -> np.ndarray:
        """Create a comprehensive synthetic schematic with symbols and text"""
        # Create larger canvas
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Draw resistor symbols (rectangles) with labels
        cv2.rectangle(image, (100, 100), (160, 140), (0, 0, 0), 3)
        cv2.putText(image, "R1", (110, 90), font, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "10kΩ", (110, 170), font, 0.6, (0, 0, 0), 2)
        
        cv2.rectangle(image, (300, 100), (360, 140), (0, 0, 0), 3)
        cv2.putText(image, "R2", (310, 90), font, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "4.7kΩ", (310, 170), font, 0.6, (0, 0, 0), 2)
        
        # Draw capacitor symbols (parallel lines) with labels
        cv2.line(image, (150, 250), (150, 300), (0, 0, 0), 4)
        cv2.line(image, (160, 250), (160, 300), (0, 0, 0), 4)
        cv2.putText(image, "C1", (140, 240), font, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "100μF", (130, 330), font, 0.6, (0, 0, 0), 2)
        
        cv2.line(image, (350, 250), (350, 300), (0, 0, 0), 4)
        cv2.line(image, (360, 250), (360, 300), (0, 0, 0), 4)
        cv2.putText(image, "C2", (340, 240), font, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "22pF", (340, 330), font, 0.6, (0, 0, 0), 2)
        
        # Draw IC symbol (rectangle) with label
        cv2.rectangle(image, (500, 200), (600, 280), (0, 0, 0), 3)
        cv2.putText(image, "U1", (530, 190), font, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "LM358", (520, 310), font, 0.6, (0, 0, 0), 2)
        
        # Draw connection lines
        cv2.line(image, (160, 120), (300, 120), (0, 0, 0), 2)
        cv2.line(image, (155, 140), (155, 250), (0, 0, 0), 2)
        
        # Add voltage source
        cv2.circle(image, (100, 400), 30, (0, 0, 0), 3)
        cv2.putText(image, "V1", (85, 390), font, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "5V", (90, 450), font, 0.6, (0, 0, 0), 2)
        
        # Add ground symbol
        cv2.line(image, (200, 400), (200, 420), (0, 0, 0), 3)
        cv2.line(image, (190, 420), (210, 420), (0, 0, 0), 3)
        cv2.line(image, (195, 425), (205, 425), (0, 0, 0), 3)
        cv2.putText(image, "GND", (185, 440), font, 0.5, (0, 0, 0), 2)
        
        return image
    
    def _validate_pipeline_results(self, result: dict):
        """Validate the complete pipeline results"""
        # Check basic structure
        assert result['status'] == 'success'
        assert 'processing_metadata' in result
        assert 'image_analysis' in result
        assert 'detected_components' in result
        assert 'component_recommendations' in result
        
        # Check processing metadata
        metadata = result['processing_metadata']
        assert 'processing_times' in metadata
        assert 'capabilities_used' in metadata
        assert len(metadata['processing_steps']) >= 4
        
        # Check image analysis
        analysis = result['image_analysis']
        assert analysis['total_components'] > 0
        assert 'text_extraction_quality' in analysis
        assert 'coverage_metrics' in analysis
        
        # Check detected components
        components = result['detected_components']
        assert len(components) > 0
        
        # Validate component structure
        for component in components:
            assert 'id' in component
            assert 'component_type' in component
            assert 'confidence' in component
        
        # Check for OCR-extracted information in at least some components
        components_with_text = sum(1 for c in components 
                                 if c.get('designation') or c.get('value'))
        assert components_with_text > 0, "Expected at least some components to have OCR-extracted text"
        
        print(f"✅ Pipeline validation passed:")
        print(f"  - {analysis['total_components']} components detected")
        print(f"  - {components_with_text} components with text information")
        print(f"  - Processing time: {metadata['processing_times']['total_processing_ms']:.1f}ms")

    def test_complete_pipeline_with_topology_analysis(self):
        """Test complete pipeline including topology analysis"""
        logging.basicConfig(level=logging.INFO)
        
        # Create comprehensive test schematic
        test_image = self._create_advanced_test_schematic()
        test_image_path = "test_topology_schematic.png"
        cv2.imwrite(test_image_path, test_image)
        
        try:
            processor = EnhancedSchematicProcessor()
            result = asyncio.run(processor.process_schematic(test_image_path))
            
            # Validate enhanced results structure
            self._validate_topology_pipeline_results(result)
            
            print("✅ Complete topology pipeline test passed!")
            
        finally:
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def _create_advanced_test_schematic(self) -> np.ndarray:
        """Create schematic with clear connections for topology testing"""
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255
        
        # Draw resistors with connections
        cv2.rectangle(image, (100, 250), (180, 290), (0, 0, 0), 3)  # R1
        cv2.putText(image, "R1", (110, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "10kΩ", (110, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.rectangle(image, (300, 250), (380, 290), (0, 0, 0), 3)  # R2  
        cv2.putText(image, "R2", (310, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "4.7kΩ", (310, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Draw connection lines between components
        cv2.line(image, (180, 270), (300, 270), (0, 0, 0), 3)  # R1 to R2
        cv2.line(image, (50, 270), (100, 270), (0, 0, 0), 3)   # Input to R1
        cv2.line(image, (380, 270), (450, 270), (0, 0, 0), 3)  # R2 to output
        
        # Add voltage source
        cv2.circle(image, (50, 270), 25, (0, 0, 0), 3)
        cv2.putText(image, "V1", (35, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "5V", (40, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Add ground
        cv2.line(image, (450, 270), (450, 300), (0, 0, 0), 3)
        cv2.line(image, (440, 300), (460, 300), (0, 0, 0), 3)
        cv2.putText(image, "GND", (435, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return image

    def _validate_topology_pipeline_results(self, result: dict):
        """Validate pipeline results include topology analysis"""
        # Basic structure validation
        assert result['status'] == 'success'
        assert 'topology_analysis' in result
        assert 'spice_netlist' in result
        assert 'circuit_intelligence' in result
        
        # Topology analysis validation
        topology = result['topology_analysis']
        assert 'connections' in topology
        assert 'nodes' in topology
        assert 'connection_matrix' in topology
        
        # SPICE netlist validation
        netlist = result['spice_netlist']
        assert 'netlist_text' in netlist
        assert 'spice_components' in netlist
        
        # Enhanced capabilities validation
        metadata = result['processing_metadata']
        assert 'topology_analysis' in metadata['processing_steps']
        assert 'netlist_generation' in metadata['processing_steps']
        
        # Print detailed results
        print(f"✅ Topology validation passed:")
        print(f"  - Connections: {len(topology['connections'])}")
        print(f"  - Nodes: {len(topology['nodes'])}")
        print(f"  - SPICE components: {netlist.get('total_spice_components', 0)}")
        print(f"  - Processing time: {metadata['processing_times']['total_processing_ms']:.1f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
