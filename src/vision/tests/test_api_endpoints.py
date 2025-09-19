"""
Test API Endpoints for Schematic Processing
"""
import sys
import pathlib
import pytest
import asyncio
from fastapi.testclient import TestClient
from PIL import Image
import io

# Add project root to Python path
project_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from src.main import app

class TestSchematicAPI:
    """Test schematic processing API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/api/v1/schematic/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "status" in data
        assert data["status"] == "healthy"
        
        print(f"✅ Health check passed: {data['service']}")
    
    def test_capabilities_endpoint(self):
        """Test the capabilities endpoint"""
        response = self.client.get("/api/v1/schematic/capabilities")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "features" in data
        assert "supported_file_formats" in data
        
        # Verify key capabilities
        features = data["features"]
        assert "symbol_detection" in features
        assert "text_extraction" in features
        assert "enhanced_analysis" in features
        
        print(f"✅ Capabilities endpoint working:")
        print(f"  - Service: {data['service']}")
        print(f"  - Features: {len(features)} capabilities")
        print(f"  - Formats: {data['supported_file_formats']}")
    
    def test_analyze_endpoint_with_image(self):
        """Test the analyze endpoint with a test image"""
        # Create a simple test image
        test_image = self._create_test_image()
        
        # Convert to bytes for upload
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Test the analyze endpoint
        response = self.client.post(
            "/api/v1/schematic/analyze",
            files={"file": ("test_schematic.png", img_byte_arr, "image/png")}
        )
        
        print(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            assert "status" in data
            assert "processing_metadata" in data
            assert "image_analysis" in data
            assert "detected_components" in data
            
            # Print results summary
            analysis = data["image_analysis"]
            components = data["detected_components"]
            
            print(f"✅ API analysis successful:")
            print(f"  - Status: {data['status']}")
            print(f"  - Components detected: {analysis['total_components']}")
            print(f"  - Processing time: {data['processing_metadata']['processing_times']['total_processing_ms']:.1f}ms")
            
            # Print component details
            for i, comp in enumerate(components[:3]):  # Show first 3
                designation = comp.get('designation', 'N/A')
                comp_type = comp.get('component_type', 'unknown')
                confidence = comp.get('confidence', 0.0)
                print(f"  - Component {i+1}: {designation} ({comp_type}) [conf: {confidence:.2f}]")
        else:
            print(f"❌ API test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            pytest.fail(f"API endpoint failed with status {response.status_code}")
    
    def test_analyze_endpoint_validation(self):
        """Test file validation on analyze endpoint"""
        # Test with invalid file type
        response = self.client.post(
            "/api/v1/schematic/analyze",
            files={"file": ("test.txt", b"invalid file content", "text/plain")}
        )
        
        print(f"📊 Validation Response Status: {response.status_code}")
        print(f"📊 Validation Response Content: {response.text}")
        
        assert response.status_code == 400
        
        try:
            data = response.json()
            # ✅ FIXED: Check if 'detail' key exists before accessing
            if 'detail' in data:
                assert "Unsupported file type" in data["detail"]
            elif 'error' in data:
                assert "Unsupported file type" in data["error"]
            else:
                # Print actual response structure for debugging
                print(f"Unexpected response structure: {data}")
                pytest.fail("Expected error message not found in response")
        except Exception as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response.text}")
            pytest.fail(f"Could not parse error response: {e}")
            
        print("✅ File validation working correctly")

    
    def _create_test_image(self) -> Image:
        """Create a simple test image for API testing"""
        img = Image.new('RGB', (400, 300), 'white')
        from PIL import ImageDraw
        
        draw = ImageDraw.Draw(img)
        
        # Simple resistor symbol
        draw.rectangle([(100, 100), (160, 120)], outline='black', width=2)
        draw.text((110, 80), "R1", fill='black')
        draw.text((110, 130), "10kΩ", fill='black')
        
        # Simple capacitor symbol
        draw.line([(200, 100), (200, 120)], fill='black', width=3)
        draw.line([(210, 100), (210, 120)], fill='black', width=3)
        draw.text((190, 80), "C1", fill='black')
        draw.text((185, 130), "100μF", fill='black')
        
        return img

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
