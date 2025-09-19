"""
Enhanced Schematic Symbol Detector with Comprehensive Debugging
"""
import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SchematicSymbolDetector:
    """Enhanced schematic symbol detector with fallback and debugging capabilities"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize detector with YOLO model and fallback capabilities"""
        self.component_classes = [
            'resistor', 'capacitor', 'inductor', 'diode', 
            'transistor', 'op_amp', 'voltage_source', 'ground',
            'switch', 'fuse', 'transformer', 'connector'
        ]
        
        # Initialize YOLO model
        try:
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')  # Use nano model for speed
            logger.info("✅ YOLOv8 model loaded successfully")
        except ImportError:
            logger.error("❌ Ultralytics not installed")
            self.model = None
        except Exception as e:
            logger.error(f"❌ YOLO model loading failed: {e}")
            self.model = None
    
    def detect_symbols(self, image_path: str, confidence_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Main detection method with YOLO + enhanced fallback
        """
        logger.info(f"🔍 Analyzing schematic: {image_path}")
        
        # Try YOLO detection first
        if self.model:
            try:
                results = self.model(image_path, conf=confidence_threshold)
                detections = self._process_yolo_results(results)
                
                if detections:
                    logger.info(f"✅ YOLOv8 found {len(detections)} detections")
                    return detections
                else:
                    logger.info("⚠️ No YOLOv8 detections, using enhanced fallback")
                    
            except Exception as e:
                logger.error(f"❌ YOLO detection failed: {e}")
        
        # Use enhanced fallback detection with comprehensive debugging
        return self._enhanced_fallback_detection(image_path)
    
    def _process_yolo_results(self, results) -> List[Dict[str, Any]]:
        """Process YOLO detection results"""
        detections = []
        
        for result in results:
            if result.boxes is not None:
                for i, box in enumerate(result.boxes):
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    
                    # Map to component type
                    component_type = self._map_class_to_component(cls_id)
                    
                    detection = {
                        'id': f'yolo_{i}',
                        'component_type': component_type,
                        'confidence': confidence,
                        'bbox': xyxy,
                        'center': [(xyxy[0] + xyxy[2]) / 2, (xyxy[1] + xyxy[3]) / 2],
                        'dimensions': [xyxy[2] - xyxy[0], xyxy[3] - xyxy[1]],
                        'detection_method': 'yolo'
                    }
                    detections.append(detection)
        
        return detections
    
    def _enhanced_fallback_detection(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Enhanced fallback detection with comprehensive debugging
        """
        logger.info("🔄 Starting enhanced fallback detection with debugging...")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"❌ Could not load image: {image_path}")
                return []
            
            logger.info(f"📊 Original image shape: {image.shape}")
            
            # Step 1: Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.imwrite("debug_01_grayscale.png", gray)
            logger.info("💾 Saved debug_01_grayscale.png")
            
            # Step 2: Try multiple preprocessing approaches
            detections_by_method = {}
            
            # Method 1: Simple binary threshold
            _, binary_simple = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            cv2.imwrite("debug_02_binary_simple.png", binary_simple)
            detections_by_method['simple'] = self._find_contours_and_detect(
                binary_simple, image, "simple"
            )
            
            # Method 2: Adaptive threshold (Gaussian)
            binary_adaptive = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
            )
            cv2.imwrite("debug_03_binary_adaptive.png", binary_adaptive)
            detections_by_method['adaptive'] = self._find_contours_and_detect(
                binary_adaptive, image, "adaptive"
            )
            
            # Method 3: Otsu's threshold
            _, binary_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            cv2.imwrite("debug_04_binary_otsu.png", binary_otsu)
            detections_by_method['otsu'] = self._find_contours_and_detect(
                binary_otsu, image, "otsu"
            )
            
            # Method 4: Morphological operations + threshold
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            _, binary_morph = cv2.threshold(morph, 127, 255, cv2.THRESH_BINARY_INV)
            cv2.imwrite("debug_05_binary_morph.png", binary_morph)
            detections_by_method['morph'] = self._find_contours_and_detect(
                binary_morph, image, "morph"
            )
            
            # Select best method (most detections)
            best_method = max(detections_by_method.keys(), 
                            key=lambda k: len(detections_by_method[k]))
            best_detections = detections_by_method[best_method]
            
            logger.info(f"🏆 Best method: {best_method} with {len(best_detections)} detections")
            
            # Log results summary
            for method, detections in detections_by_method.items():
                logger.info(f"  📊 {method}: {len(detections)} detections")
            
            return best_detections
            
        except Exception as e:
            logger.error(f"❌ Enhanced fallback detection failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _find_contours_and_detect(self, binary_image: np.ndarray, 
                                  original_image: np.ndarray, 
                                  method_name: str) -> List[Dict[str, Any]]:
        """Find contours and create detections with debugging"""
        
        # Find contours
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logger.info(f"🔍 Method {method_name}: Found {len(contours)} raw contours")
        
        # Create debug image with contours
        debug_contours = original_image.copy()
        cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
        cv2.imwrite(f"debug_06_contours_{method_name}.png", debug_contours)
        
        detections = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Very permissive threshold for debugging
            if area > 10:  # Accept small contours for debugging
                x, y, w, h = cv2.boundingRect(contour)
                
                # Additional shape analysis
                perimeter = cv2.arcLength(contour, True)
                aspect_ratio = float(w) / h if h != 0 else 0
                extent = area / (w * h) if (w * h) != 0 else 0
                
                detection = {
                    'id': f'{method_name}_{i}',
                    'component_type': self._classify_shape(area, aspect_ratio, extent),
                    'confidence': 0.5,
                    'bbox': [x, y, x+w, y+h],
                    'center': [x+w/2, y+h/2],
                    'dimensions': [w, h],
                    'area': area,
                    'perimeter': perimeter,
                    'aspect_ratio': aspect_ratio,
                    'extent': extent,
                    'detection_method': f'fallback_{method_name}'
                }
                detections.append(detection)
                
                logger.info(f"  ✅ {method_name}_{i}: area={area:.1f}, bbox=[{x},{y},{x+w},{y+h}]")
        
        return detections
    
    def _classify_shape(self, area: float, aspect_ratio: float, extent: float) -> str:
        """Basic shape classification for fallback detection"""
        if 0.8 <= aspect_ratio <= 1.2:  # Roughly square
            if area > 1000:
                return "large_component"
            else:
                return "small_component"
        elif aspect_ratio > 2:  # Long and thin
            return "linear_component"
        else:
            return "unknown_component"
    
    def _map_class_to_component(self, cls_id: int) -> str:
        """Map YOLO class ID to component type"""
        # Simple mapping for demo - in production, use trained electronics model
        generic_mappings = {
            0: 'unknown_component',
            1: 'connector',
            2: 'resistor',
            3: 'capacitor',
            4: 'transistor',
            5: 'diode'
        }
        return generic_mappings.get(cls_id, 'unknown_component')
    
    def visualize_detections(self, image_path: str, detections: List[Dict], 
                           save_path: str = "debug_07_final_detections.png"):
        """Create visualization of all detections"""
        image = cv2.imread(image_path)
        
        for detection in detections:
            bbox = detection['bbox']
            component_type = detection['component_type']
            confidence = detection['confidence']
            method = detection.get('detection_method', 'unknown')
            
            # Draw bounding box
            color = (0, 255, 0) if 'yolo' in method else (255, 0, 0)
            cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), 
                         (int(bbox[2]), int(bbox[3])), color, 2)
            
            # Add label with method info
            label = f"{component_type} ({method}) {confidence:.2f}"
            cv2.putText(image, label, (int(bbox[0]), int(bbox[1]-10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        cv2.imwrite(save_path, image)
        logger.info(f"💾 Saved final detection visualization: {save_path}")
        
        return image
