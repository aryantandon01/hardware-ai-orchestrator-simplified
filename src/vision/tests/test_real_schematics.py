"""
Testing with Real Schematic Images
"""
import sys
import pathlib
import pytest
import requests
import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

# Add project root to Python path
project_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from src.vision.schematic_processor.integration_handler import EnhancedSchematicProcessor

class TestRealSchematics:
    """Test with real or realistic schematic images"""
    
    def test_with_realistic_schematic(self):
        """Test with a more realistic hand-drawn style schematic"""
        # Create realistic schematic image
        realistic_schematic = self._create_realistic_schematic()
        test_path = "realistic_schematic.png"
        realistic_schematic.save(test_path)
        
        try:
            processor = EnhancedSchematicProcessor()
            result = asyncio.run(processor.process_schematic(test_path))
            
            # Validate results
            assert result['status'] == 'success'
            components = result['detected_components']
            
            print(f"🔍 Realistic schematic analysis:")
            print(f"  - Total components: {len(components)}")
            
            # Print detailed component information
            for i, comp in enumerate(components):
                designation = comp.get('designation', 'N/A')
                value = comp.get('value', 'N/A')
                comp_type = comp.get('component_type', 'unknown')
                confidence = comp.get('confidence', 0.0)
                
                print(f"  Component {i+1}: {designation} ({comp_type}) = {value} "
                      f"[conf: {confidence:.2f}]")
            
            # Check text extraction quality
            text_quality = result['image_analysis']['text_extraction_quality']
            print(f"  - Text quality: {text_quality['overall_quality']:.2f}")
            print(f"  - Text coverage: {text_quality['text_coverage']:.2f}")
            
            print("✅ Realistic schematic test completed successfully!")
            
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)
    
    def _create_realistic_schematic(self) -> Image:
        """Create a more realistic-looking schematic using PIL"""
        # Create white background
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a better font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw more realistic circuit elements
        
        # Resistor 1 (zigzag pattern)
        self._draw_resistor(draw, (100, 150), "R1", "10kΩ")
        
        # Resistor 2
        self._draw_resistor(draw, (300, 150), "R2", "4.7kΩ")
        
        # Capacitors
        self._draw_capacitor(draw, (150, 250), "C1", "100μF")
        self._draw_capacitor(draw, (350, 250), "C2", "22pF")
        
        # Op-amp
        self._draw_op_amp(draw, (500, 200), "U1", "LM358")
        
        # Voltage source
        self._draw_voltage_source(draw, (100, 350), "V1", "5V")
        
        # Ground
        self._draw_ground(draw, (200, 380))
        
        # Connection wires
        draw.line([(160, 150), (300, 150)], fill='black', width=2)
        draw.line([(150, 180), (150, 250)], fill='black', width=2)
        draw.line([(350, 180), (350, 250)], fill='black', width=2)
        
        return img
    
    def _draw_resistor(self, draw, pos, label, value):
        """Draw a resistor symbol with label and value"""
        x, y = pos
        # Draw resistor body (rectangle)
        draw.rectangle([(x, y-10), (x+60, y+10)], outline='black', width=2)
        
        # Add zigzag pattern
        points = [(x, y), (x+10, y-8), (x+20, y+8), (x+30, y-8), 
                 (x+40, y+8), (x+50, y-8), (x+60, y)]
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill='black', width=2)
        
        # Add label and value
        draw.text((x+15, y-30), label, fill='black')
        draw.text((x+10, y+20), value, fill='black')
    
    def _draw_capacitor(self, draw, pos, label, value):
        """Draw a capacitor symbol with label and value"""
        x, y = pos
        # Draw two parallel lines
        draw.line([(x-5, y-20), (x-5, y+20)], fill='black', width=3)
        draw.line([(x+5, y-20), (x+5, y+20)], fill='black', width=3)
        
        # Connection lines
        draw.line([(x-25, y), (x-5, y)], fill='black', width=2)
        draw.line([(x+5, y), (x+25, y)], fill='black', width=2)
        
        # Add label and value
        draw.text((x-10, y-40), label, fill='black')
        draw.text((x-15, y+30), value, fill='black')
    
    def _draw_op_amp(self, draw, pos, label, value):
        """Draw an op-amp symbol with label and value"""
        x, y = pos
        # Draw triangle
        points = [(x, y), (x+60, y-30), (x+60, y+30), (x, y)]
        draw.polygon(points, outline='black', width=2)
        
        # Add + and - symbols
        draw.text((x+5, y-15), "+", fill='black')
        draw.text((x+5, y+5), "-", fill='black')
        
        # Add label and value
        draw.text((x+15, y-50), label, fill='black')
        draw.text((x+10, y+40), value, fill='black')
    
    def _draw_voltage_source(self, draw, pos, label, value):
        """Draw a voltage source symbol with label and value"""
        x, y = pos
        # Draw circle
        draw.ellipse([(x-20, y-20), (x+20, y+20)], outline='black', width=2)
        
        # Add + and - symbols
        draw.text((x-5, y-10), "+", fill='black')
        draw.text((x-5, y+5), "-", fill='black')
        
        # Add label and value
        draw.text((x-10, y-40), label, fill='black')
        draw.text((x-5, y+30), value, fill='black')
    
    def _draw_ground(self, draw, pos):
        """Draw a ground symbol"""
        x, y = pos
        # Draw ground lines
        draw.line([(x, y), (x, y+15)], fill='black', width=3)
        draw.line([(x-10, y+15), (x+10, y+15)], fill='black', width=3)
        draw.line([(x-7, y+20), (x+7, y+20)], fill='black', width=2)
        draw.line([(x-4, y+25), (x+4, y+25)], fill='black', width=1)
        
        draw.text((x-15, y+30), "GND", fill='black')

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
