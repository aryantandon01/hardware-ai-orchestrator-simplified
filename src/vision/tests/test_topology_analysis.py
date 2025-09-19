"""
Test Advanced Topology Analysis Features
"""
import sys
import pathlib
import pytest
import cv2
import numpy as np
import os

# Add project root to Python path
project_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

class TestTopologyAnalysis:
    """Test topology analysis features"""
    
    def test_connection_detector_initialization(self):
        """Test that connection detector initializes properly"""
        try:
            from src.vision.topology.connection_detector import AdvancedConnectionDetector
            detector = AdvancedConnectionDetector()
            assert detector is not None
            assert detector.connection_confidence_threshold == 0.6
            print("✅ Connection detector initialized successfully")
        except ImportError:
            pytest.skip("Topology modules not yet implemented")
    
    def test_basic_connection_detection(self):
        """Test connection detection with simple synthetic image"""
        try:
            from src.vision.topology.connection_detector import AdvancedConnectionDetector
            
            # Create simple test image with lines
            test_image = np.ones((400, 600, 3), dtype=np.uint8) * 255
            
            # Draw horizontal and vertical lines (connections)
            cv2.line(test_image, (100, 200), (300, 200), (0, 0, 0), 3)  # Horizontal
            cv2.line(test_image, (400, 100), (400, 300), (0, 0, 0), 3)  # Vertical
            
            # Draw some component rectangles
            cv2.rectangle(test_image, (80, 180), (120, 220), (0, 0, 0), 2)
            cv2.rectangle(test_image, (280, 180), (320, 220), (0, 0, 0), 2)
            
            test_path = "test_connections.png"
            cv2.imwrite(test_path, test_image)
            
            # Mock component data
            mock_components = [
                {'id': 'comp1', 'bbox': [80, 180, 120, 220], 'component_type': 'resistor'},
                {'id': 'comp2', 'bbox': [280, 180, 320, 220], 'component_type': 'capacitor'}
            ]
            
            try:
                detector = AdvancedConnectionDetector()
                result = detector.detect_connections(test_path, mock_components)
                
                # Validate results structure
                assert 'connections' in result
                assert 'nodes' in result
                assert 'topology_analysis' in result
                
                connections = result['connections']
                print(f"🔍 Detected {len(connections)} connections")
                
                # Should detect at least the horizontal line
                assert len(connections) > 0, "Should detect at least one connection"
                
                print("✅ Basic connection detection working")
                
            finally:
                if os.path.exists(test_path):
                    os.remove(test_path)
                    
        except ImportError:
            pytest.skip("Connection detector not yet implemented")
    
    def test_netlist_generation(self):
        """Test SPICE netlist generation"""
        try:
            from src.vision.topology.netlist_generator import NetlistGenerator
            
            # Mock data for netlist generation
            mock_components = [
                {
                    'id': 'R1', 
                    'component_type': 'resistor', 
                    'designation': 'R1', 
                    'value': '10k'
                },
                {
                    'id': 'C1', 
                    'component_type': 'capacitor', 
                    'designation': 'C1', 
                    'value': '100μF'
                }
            ]
            
            mock_connections = []  # Simplified for basic test
            mock_nodes = [
                type('Node', (), {'node_id': 'node1', 'connected_components': ['R1', 'C1']})()
            ]
            
            generator = NetlistGenerator()
            result = generator.generate_spice_netlist(mock_components, mock_connections, mock_nodes)
            
            # Validate netlist structure
            assert 'netlist' in result
            assert 'components' in result
            assert 'metadata' in result
            
            netlist_text = result['netlist']
            print(f"📝 Generated netlist length: {len(netlist_text)} characters")
            
            # Check for basic SPICE elements
            assert 'R1' in netlist_text or len(result['components']) > 0
            assert '.end' in netlist_text
            
            print("✅ SPICE netlist generation working")
            
        except ImportError:
            pytest.skip("Netlist generator not yet implemented")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
