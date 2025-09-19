import sys
import pathlib
import pytest
import os

# Add project root to Python path - this fixes the import issue
project_root = pathlib.Path(__file__).resolve().parents[3]  # Go up 3 levels to reach project root
sys.path.insert(0, str(project_root))

# Now this import will work
from src.vision.schematic_processor.symbol_detector import SchematicSymbolDetector

class TestSymbolDetector:
    """Test cases for schematic symbol detection"""
    
    def test_detector_initialization(self):
        """Test that detector initializes properly"""
        detector = SchematicSymbolDetector()
        assert detector is not None
        assert len(detector.component_classes) > 0
    
    def test_fallback_detection(self):
        """Test enhanced fallback detection with comprehensive debugging"""
        import cv2
        import numpy as np
        import logging
        
        # Enable verbose logging
        logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Create enhanced test image with various shapes
        test_image = np.ones((400, 400, 3), dtype=np.uint8) * 255
        
        # Draw filled rectangles
        cv2.rectangle(test_image, (50, 50), (150, 150), (0, 0, 0), -1)
        cv2.rectangle(test_image, (200, 200), (300, 300), (0, 0, 0), -1)
        
        # Draw thick outlines
        cv2.rectangle(test_image, (320, 50), (380, 150), (0, 0, 0), 8)
        
        # Draw circles
        cv2.circle(test_image, (100, 300), 30, (0, 0, 0), -1)
        cv2.circle(test_image, (300, 100), 25, (0, 0, 0), -1)
        
        # Draw lines (components)
        cv2.line(test_image, (50, 250), (150, 250), (0, 0, 0), 5)
        cv2.line(test_image, (250, 50), (250, 150), (0, 0, 0), 5)
        
        test_image_path = "test_schematic_enhanced.png"
        cv2.imwrite(test_image_path, test_image)
        
        try:
            detector = SchematicSymbolDetector()
            detections = detector.detect_symbols(test_image_path)
            
            # Create visualization
            detector.visualize_detections(test_image_path, detections)
            
            print(f"🔍 Total detections found: {len(detections)}")
            
            # Print detailed results
            for i, detection in enumerate(detections):
                print(f"  Detection {i+1}: {detection['component_type']} "
                    f"(method: {detection['detection_method']}) "
                    f"at {detection['center']} "
                    f"area: {detection.get('area', 'N/A')}")
            
            # Assertions
            assert isinstance(detections, list)
            assert len(detections) > 0, f"Expected detections but got {len(detections)}"
            
            # Verify required fields
            for detection in detections:
                required_fields = ['id', 'component_type', 'confidence', 'bbox', 'center']
                for field in required_fields:
                    assert field in detection, f"Missing field {field} in detection"
            
            print(f"✅ Test passed with {len(detections)} detections!")
            
        finally:
            # Clean up test file
            import os
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

if __name__ == "__main__":
    # Run tests when file is executed directly
    pytest.main([__file__, "-v"])
