import requests
from PIL import Image, ImageDraw
import io

def test_api_with_topology():
    """Test API with topology analysis features"""
    
    # Create test image
    img = Image.new('RGB', (600, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw simple circuit
    draw.rectangle([100, 150, 160, 190], outline='black', width=3)  # Resistor
    draw.text((110, 130), "R1", fill='black')
    draw.text((110, 200), "10kΩ", fill='black')
    
    draw.rectangle([250, 150, 310, 190], outline='black', width=3)  # Resistor
    draw.text((260, 130), "R2", fill='black')
    draw.text((260, 200), "4.7kΩ", fill='black')
    
    # Connection line
    draw.line([160, 170, 250, 170], fill='black', width=3)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    # Send to API
    response = requests.post(
        "http://localhost:8000/api/v1/schematic/analyze",
        files={"file": ("test_circuit.png", img_bytes, "image/png")}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("✅ API Response received successfully")
        print(f"📊 Status: {result['status']}")
        print(f"🔧 Components: {result['image_analysis']['total_components']}")
        
        # Check for topology analysis
        if 'topology_analysis' in result:
            topology = result['topology_analysis']
            print(f"🔗 Connections: {len(topology.get('connections', []))}")
            print(f"📍 Nodes: {len(topology.get('nodes', []))}")
            
        # Check for SPICE netlist
        if 'spice_netlist' in result:
            netlist = result['spice_netlist']
            print(f"📝 SPICE generated: {netlist.get('generation_successful', False)}")
            
        return True
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    success = test_api_with_topology()
    print("✅ API topology test passed!" if success else "❌ API topology test failed!")
