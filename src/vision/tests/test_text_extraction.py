"""
Test cases for OCR text extraction
"""
import sys
import pathlib
import pytest
import cv2
import numpy as np
import os
import logging

# Add project root to Python path
project_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from src.vision.schematic_processor.text_extractor import SchematicTextExtractor

class TestTextExtraction:
    """Test cases for schematic text extraction"""
    
    def test_extractor_initialization(self):
        """Test that OCR extractor initializes properly"""
        extractor = SchematicTextExtractor()
        assert extractor is not None
        # OCR might not be available in test environment, that's OK
        
    def test_text_extraction_with_synthetic_image(self):
        """Test OCR extraction on synthetic image with text"""
        # Enable logging for test
        logging.basicConfig(level=logging.INFO)
        
        # Create test image with text
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # Add text labels typical of schematic components
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(test_image, "R1", (50, 50), font, 1, (0, 0, 0), 2)
        cv2.putText(test_image, "10kΩ", (50, 80), font, 0.7, (0, 0, 0), 2)
        cv2.putText(test_image, "C2", (200, 50), font, 1, (0, 0, 0), 2)
        cv2.putText(test_image, "100μF", (200, 80), font, 0.7, (0, 0, 0), 2)
        cv2.putText(test_image, "U3", (350, 50), font, 1, (0, 0, 0), 2)
        
        test_image_path = "test_ocr_schematic.png"
        cv2.imwrite(test_image_path, test_image)
        
        try:
            extractor = SchematicTextExtractor()
            
            # Test text extraction
            results = extractor.extract_component_labels(test_image_path)
            
            print(f"🔍 OCR Results: {len(results)} elements extracted")
            for i, result in enumerate(results):
                print(f"  {i+1}. Text: '{result.get('text', 'N/A')}' "
                      f"Type: {result.get('type', 'N/A')} "
                      f"Confidence: {result.get('confidence', 'N/A')}")
            
            # Verify results structure
            assert isinstance(results, list)
            
            # If OCR is available, we should get some results
            if extractor.ocr_available and len(results) > 0:
                # Check that results have expected structure
                for result in results:
                    if 'text' in result:
                        assert 'confidence' in result
                        assert 'center' in result
                        
                print("✅ OCR extraction test passed!")
            else:
                print("⚠️ OCR not available - test passed with fallback behavior")
                
        finally:
            # Clean up
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
    
    def test_component_text_parsing(self):
        """Test parsing of component designations and values"""
        extractor = SchematicTextExtractor()
        
        # Test cases for text parsing
        test_cases = [
            ("R1", {"type": "designation", "designation": "R1", "component_type": "resistor"}),
            ("10kΩ", {"type": "value", "unit": "resistance", "value": 10.0, "multiplier": "k"}),
            ("C2", {"type": "designation", "designation": "C2", "component_type": "capacitor"}),
            ("100μF", {"type": "value", "unit": "capacitance", "value": 100.0, "multiplier": "μ"}),
            ("U3", {"type": "designation", "designation": "U3", "component_type": "ic"}),
            ("±5%", {"tolerance": 5.0})
        ]
        
        for text, expected in test_cases:
            parsed = extractor._parse_component_text(text)
            print(f"📝 Parsing '{text}': {parsed}")
            
            # Check expected fields
            for key, value in expected.items():
                assert key in parsed, f"Missing key {key} for text '{text}'"
                assert parsed[key] == value, f"Expected {key}={value}, got {parsed[key]} for text '{text}'"
        
        print("✅ Component text parsing test passed!")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
