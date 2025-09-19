"""
OCR Text Extractor for Schematic Images
Extracts component labels, values, and designations using EasyOCR
"""
import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
import re
import math

logger = logging.getLogger(__name__)

class SchematicTextExtractor:
    """Extracts and parses text from schematic images using OCR"""
    
    def __init__(self):
        """Initialize the OCR text extractor"""
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if CUDA available
            self.ocr_available = True
            logger.info("✅ EasyOCR initialized successfully")
        except ImportError:
            logger.error("❌ EasyOCR not installed. Run: pip install easyocr")
            self.reader = None
            self.ocr_available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize EasyOCR: {e}")
            self.reader = None
            self.ocr_available = False
    
    def extract_component_labels(self, image_path: str, symbol_detections: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Extract text labels and associate them with detected symbols
        
        Args:
            image_path: Path to schematic image
            symbol_detections: List of detected symbols from symbol detector
            
        Returns:
            Enhanced detections with text information
        """
        if not self.ocr_available:
            logger.warning("⚠️ OCR not available, returning original detections")
            return symbol_detections or []
        
        try:
            logger.info(f"🔍 Extracting text from {image_path}")
            
            # Extract all text from image
            all_text_results = self._extract_all_text(image_path)
            
            if not all_text_results:
                logger.warning("⚠️ No text extracted from image")
                return symbol_detections or []
            
            logger.info(f"📝 Found {len(all_text_results)} text elements")
            
            # If no symbol detections provided, return parsed text only
            if not symbol_detections:
                return self._process_standalone_text(all_text_results)
            
            # Associate text with symbol detections
            enhanced_detections = self._associate_text_with_symbols(
                symbol_detections, all_text_results
            )
            
            return enhanced_detections
            
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {e}")
            return symbol_detections or []
    
    def _extract_all_text(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract all text from the image using EasyOCR"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"❌ Could not load image: {image_path}")
                return []
            
            # Run OCR
            results = self.reader.readtext(image)
            
            # Process OCR results
            text_elements = []
            for i, (bbox, text, confidence) in enumerate(results):
                # Calculate center point of text
                bbox_array = np.array(bbox)
                center_x = np.mean(bbox_array[:, 0])
                center_y = np.mean(bbox_array[:, 1])
                
                # Calculate text dimensions
                width = np.max(bbox_array[:, 0]) - np.min(bbox_array[:, 0])
                height = np.max(bbox_array[:, 1]) - np.min(bbox_array[:, 1])
                
                text_element = {
                    'id': f'text_{i}',
                    'text': text.strip(),
                    'confidence': confidence,
                    'bbox': bbox,
                    'center': [center_x, center_y],
                    'dimensions': [width, height],
                    'parsed_info': self._parse_component_text(text.strip())
                }
                
                text_elements.append(text_element)
                
                logger.debug(f"  📝 Text {i}: '{text}' at ({center_x:.1f}, {center_y:.1f}) "
                           f"conf={confidence:.3f}")
            
            # Save debug visualization
            self._visualize_text_extraction(image_path, text_elements)
            
            return text_elements
            
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return []
    
    def _associate_text_with_symbols(self, symbols: List[Dict], text_elements: List[Dict]) -> List[Dict]:
        """Associate text elements with detected symbols based on proximity"""
        enhanced_symbols = []
        
        for symbol in symbols:
            symbol_center = symbol['center']
            
            # Find closest text elements
            nearby_text = self._find_nearby_text(symbol_center, text_elements)
            
            # Create enhanced symbol with text information
            enhanced_symbol = {
                **symbol,
                'associated_text': nearby_text,
                'designation': None,
                'value': None,
                'unit': None,
                'tolerance': None
            }
            
            # Extract component information from associated text
            if nearby_text:
                component_info = self._extract_component_info_from_text(nearby_text)
                enhanced_symbol.update(component_info)
            
            enhanced_symbols.append(enhanced_symbol)
        
        return enhanced_symbols
    
    def _find_nearby_text(self, symbol_center: List[float], 
                         text_elements: List[Dict], 
                         max_distance: float = 150) -> List[Dict]:
        """Find text elements near a symbol center"""
        nearby_text = []
        
        for text_element in text_elements:
            text_center = text_element['center']
            
            # Calculate distance between symbol and text
            distance = math.sqrt(
                (symbol_center[0] - text_center[0])**2 + 
                (symbol_center[1] - text_center[1])**2
            )
            
            if distance <= max_distance:
                text_with_distance = {
                    **text_element,
                    'distance_to_symbol': distance
                }
                nearby_text.append(text_with_distance)
        
        # Sort by distance (closest first)
        nearby_text.sort(key=lambda x: x['distance_to_symbol'])
        
        return nearby_text[:3]  # Return up to 3 closest text elements
    
    def _parse_component_text(self, text: str) -> Dict[str, Any]:
        """Parse component information from text string"""
        text = text.strip().replace(' ', '')  # Remove spaces for easier parsing
        
        parsing_result = {
            'original_text': text,
            'type': 'unknown',
            'designation': None,
            'value': None,
            'unit': None,
            'multiplier': None,
            'tolerance': None
        }
        
        # Component designation patterns (R1, C2, U3, etc.)
        designation_pattern = r'^([RCLUDQXYZKWFJ]\d+)(?:[^\d]|$)'
        designation_match = re.search(designation_pattern, text, re.IGNORECASE)
        
        if designation_match:
            parsing_result['designation'] = designation_match.group(1).upper()
            parsing_result['type'] = 'designation'
            
            # Map designation prefix to component type
            prefix = designation_match.group(1)[0].upper()
            component_type_map = {
                'R': 'resistor', 'C': 'capacitor', 'L': 'inductor',
                'D': 'diode', 'Q': 'transistor', 'U': 'ic',
                'X': 'crystal', 'Y': 'crystal', 'Z': 'zener',
                'K': 'relay', 'W': 'wire', 'F': 'fuse', 'J': 'connector'
            }
            parsing_result['component_type'] = component_type_map.get(prefix, 'unknown')
        
        # Component value patterns
        value_patterns = {
            'resistance': r'(\d+(?:\.\d+)?)\s*([kmgKMG]?)(?:Ω|ohm|ohms|R)(?:\s|$)',
            'capacitance': r'(\d+(?:\.\d+)?)\s*([μuUnNpPmMfF]?)F(?:\s|$)',
            'inductance': r'(\d+(?:\.\d+)?)\s*([μuUnNmMhH]?)H(?:\s|$)',
            'voltage': r'(\d+(?:\.\d+)?)\s*([kKmM]?)V(?:\s|$)',
            'current': r'(\d+(?:\.\d+)?)\s*([kKmMμuUaA]?)A(?:\s|$)',
            'frequency': r'(\d+(?:\.\d+)?)\s*([kKmMgGhH]?)Hz(?:\s|$)'
        }
        
        for value_type, pattern in value_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit_prefix = match.group(2).lower() if match.group(2) else ''
                
                # Convert to base units with multipliers
                multipliers = {
                    'g': 1e9, 'm': 1e6, 'k': 1e3,
                    'u': 1e-6, 'μ': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15
                }
                
                multiplier = multipliers.get(unit_prefix, 1.0)
                base_value = value * multiplier
                
                parsing_result.update({
                    'type': 'value',
                    'value': value,
                    'unit': value_type,
                    'multiplier': unit_prefix,
                    'base_value': base_value,
                    'formatted_value': f"{value}{unit_prefix}{value_type[0].upper()}"
                })
                break
        
        # Tolerance pattern (±5%, 1%, etc.)
        tolerance_pattern = r'[±]?(\d+(?:\.\d+)?)\s*%'
        tolerance_match = re.search(tolerance_pattern, text)
        if tolerance_match:
            parsing_result['tolerance'] = float(tolerance_match.group(1))
        
        return parsing_result
    
    def _extract_component_info_from_text(self, text_elements: List[Dict]) -> Dict[str, Any]:
        """Extract component information from associated text elements"""
        component_info = {
            'designation': None,
            'value': None,
            'unit': None,
            'tolerance': None,
            'text_confidence': 0.0
        }
        
        designations = []
        values = []
        tolerances = []
        
        for text_elem in text_elements:
            parsed = text_elem['parsed_info']
            confidence = text_elem['confidence']
            
            if parsed['type'] == 'designation' and parsed['designation']:
                designations.append((parsed['designation'], confidence))
            
            if parsed['type'] == 'value' and parsed['value']:
                values.append({
                    'value': parsed['value'],
                    'unit': parsed['unit'],
                    'formatted': parsed.get('formatted_value'),
                    'confidence': confidence
                })
            
            if parsed['tolerance'] is not None:
                tolerances.append((parsed['tolerance'], confidence))
        
        # Select best designation (highest confidence)
        if designations:
            component_info['designation'] = max(designations, key=lambda x: x[1])[0]
        
        # Select best value (highest confidence)
        if values:
            best_value = max(values, key=lambda x: x['confidence'])
            component_info['value'] = best_value['formatted'] or best_value['value']
            component_info['unit'] = best_value['unit']
        
        # Select best tolerance (highest confidence)
        if tolerances:
            component_info['tolerance'] = f"±{max(tolerances, key=lambda x: x[1])[0]}%"
        
        # Calculate average text confidence
        if text_elements:
            avg_confidence = sum(elem['confidence'] for elem in text_elements) / len(text_elements)
            component_info['text_confidence'] = avg_confidence
        
        return component_info
    
    def _process_standalone_text(self, text_elements: List[Dict]) -> List[Dict]:
        """Process text elements when no symbol detections are available"""
        processed_text = []
        
        for text_elem in text_elements:
            parsed = text_elem['parsed_info']
            
            if parsed['type'] in ['designation', 'value']:
                processed_element = {
                    'id': text_elem['id'],
                    'type': 'text_detection',
                    'text': text_elem['text'],
                    'confidence': text_elem['confidence'],
                    'bbox': text_elem['bbox'],
                    'center': text_elem['center'],
                    'parsed_info': parsed
                }
                processed_text.append(processed_element)
        
        return processed_text
    
    def _visualize_text_extraction(self, image_path: str, text_elements: List[Dict]):
        """Create debug visualization of text extraction"""
        try:
            image = cv2.imread(image_path)
            
            for text_elem in text_elements:
                bbox = text_elem['bbox']
                text = text_elem['text']
                confidence = text_elem['confidence']
                
                # Draw bounding box
                bbox_points = np.array(bbox, dtype=np.int32)
                cv2.polylines(image, [bbox_points], True, (0, 255, 0), 2)
                
                # Add text label
                label = f"{text} ({confidence:.2f})"
                label_pos = (int(bbox_points[0][0]), int(bbox_points[0][1] - 10))
                cv2.putText(image, label, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 1)
            
            cv2.imwrite("debug_08_text_extraction.png", image)
            logger.info("💾 Saved text extraction debug image: debug_08_text_extraction.png")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not save text visualization: {e}")

# Test function
if __name__ == "__main__":
    extractor = SchematicTextExtractor()
    results = extractor.extract_component_labels("test_schematic.png")
    print(f"Extracted {len(results)} text elements")
    for result in results:
        print(f"  - {result}")
