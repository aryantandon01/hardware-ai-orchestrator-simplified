"""
Advanced Connection Detection for Circuit Topology Analysis
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Connection:
    """Represents a connection between components"""
    start_point: Tuple[int, int]
    end_point: Tuple[int, int]
    path: List[Tuple[int, int]]
    connection_type: str  # 'wire', 'trace', 'bus'
    confidence: float
    connected_components: List[str]  # Component IDs

@dataclass
class Node:
    """Represents an electrical node (connection point)"""
    position: Tuple[int, int]
    node_id: str
    connected_components: List[str]
    connection_count: int

class AdvancedConnectionDetector:
    """Detects and analyzes electrical connections in schematics"""
    
    def __init__(self):
        self.connections = []
        self.nodes = []
        self.connection_confidence_threshold = 0.6
    
    def detect_connections(self, image_path: str, detected_components: List[Dict]) -> Dict[str, Any]:
        """
        Detect all electrical connections in the schematic
        
        Args:
            image_path: Path to schematic image
            detected_components: List of detected components with bboxes
            
        Returns:
            Dictionary containing connections, nodes, and topology info
        """
        logger.info("🔍 Starting advanced connection detection...")
        
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Step 1: Detect line segments (wires/traces)
            line_segments = self._detect_line_segments(image)
            logger.info(f"📏 Detected {len(line_segments)} line segments")
            
            # Step 2: Filter and classify connections
            electrical_connections = self._classify_line_segments(line_segments, image)
            logger.info(f"⚡ Identified {len(electrical_connections)} electrical connections")
            
            # Step 3: Find component connection points
            component_pins = self._extract_component_pins(detected_components, image)
            logger.info(f"📌 Found {len(component_pins)} component connection points")
            
            # Step 4: Build connection network
            connections = self._build_connection_network(
                electrical_connections, component_pins, detected_components
            )
            
            # Step 5: Identify electrical nodes
            nodes = self._identify_electrical_nodes(connections, component_pins)
            
            # Step 6: Analyze topology
            topology_analysis = self._analyze_circuit_topology(connections, nodes, detected_components)
            
            result = {
                'connections': connections,
                'nodes': nodes,
                'topology_analysis': topology_analysis,
                'component_pins': component_pins,
                'connection_matrix': self._build_connection_matrix(connections, detected_components)
            }
            
            logger.info("✅ Connection detection completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Connection detection failed: {e}")
            return {'connections': [], 'nodes': [], 'topology_analysis': {}}
    
    def _detect_line_segments(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect line segments using advanced Hough transform"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Advanced preprocessing for line detection
        # 1. Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 2. Adaptive thresholding
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
        
        # 3. Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 4. Edge detection
        edges = cv2.Canny(cleaned, 50, 150, apertureSize=3)
        
        # 5. Probabilistic Hough Line Transform
        lines = cv2.HoughLinesP(
            edges, 
            rho=1, 
            theta=np.pi/180, 
            threshold=50,
            minLineLength=20, 
            maxLineGap=5
        )
        
        # 6. Filter and merge nearby lines
        if lines is not None:
            merged_lines = self._merge_nearby_lines(lines.reshape(-1, 4))
            return merged_lines
        
        return []
    
    def _merge_nearby_lines(self, lines: np.ndarray, distance_threshold: float = 10) -> List[Tuple[int, int, int, int]]:
        """Merge nearby parallel lines to reduce noise"""
        if len(lines) == 0:
            return []
        
        merged = []
        used = set()
        
        for i, line1 in enumerate(lines):
            if i in used:
                continue
                
            x1, y1, x2, y2 = line1
            merged_line = line1.copy()
            used.add(i)
            
            for j, line2 in enumerate(lines[i+1:], i+1):
                if j in used:
                    continue
                    
                x3, y3, x4, y4 = line2
                
                # Check if lines are nearby and roughly parallel
                dist1 = np.sqrt((x1-x3)**2 + (y1-y3)**2)
                dist2 = np.sqrt((x2-x4)**2 + (y2-y4)**2)
                
                if dist1 < distance_threshold and dist2 < distance_threshold:
                    # Merge lines by extending endpoints
                    merged_line = [
                        min(x1, x3), min(y1, y3),
                        max(x2, x4), max(y2, y4)
                    ]
                    used.add(j)
            
            merged.append(tuple(merged_line))
        
        return merged
    
    def _classify_line_segments(self, line_segments: List[Tuple], image: np.ndarray) -> List[Dict]:
        """Classify line segments as wires, traces, or other elements"""
        classified_connections = []
        
        for i, (x1, y1, x2, y2) in enumerate(line_segments):
            # Calculate line properties
            length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            angle = np.arctan2(y2-y1, x2-x1) * 180 / np.pi
            
            # Analyze line thickness and continuity
            thickness = self._estimate_line_thickness(image, (x1, y1, x2, y2))
            continuity = self._check_line_continuity(image, (x1, y1, x2, y2))
            
            # Classification logic
            connection_type = 'wire'  # Default
            confidence = 0.7  # Base confidence
            
            # Horizontal/vertical lines are more likely to be wires
            if abs(angle) < 15 or abs(angle - 90) < 15 or abs(angle - 180) < 15:
                confidence += 0.2
            
            # Longer lines are more likely to be intentional connections
            if length > 30:
                confidence += 0.1
            
            # Thin, continuous lines are likely wires
            if thickness <= 3 and continuity > 0.8:
                connection_type = 'wire'
                confidence += 0.1
            
            classified_connections.append({
                'id': f'conn_{i}',
                'start_point': (x1, y1),
                'end_point': (x2, y2),
                'connection_type': connection_type,
                'confidence': min(confidence, 1.0),
                'properties': {
                    'length': length,
                    'angle': angle,
                    'thickness': thickness,
                    'continuity': continuity
                }
            })
        
        return classified_connections
    
    def _estimate_line_thickness(self, image: np.ndarray, line: Tuple[int, int, int, int]) -> float:
        """Estimate the thickness of a line segment"""
        x1, y1, x2, y2 = line
        
        # Sample points along the line
        num_samples = max(3, int(np.sqrt((x2-x1)**2 + (y2-y1)**2) / 10))
        
        thicknesses = []
        for i in range(num_samples):
            t = i / (num_samples - 1) if num_samples > 1 else 0
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            
            # Check perpendicular line thickness at this point
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                thickness = self._measure_perpendicular_thickness(image, (x, y), line)
                thicknesses.append(thickness)
        
        return np.mean(thicknesses) if thicknesses else 1.0
    
    def _measure_perpendicular_thickness(self, image: np.ndarray, point: Tuple[int, int], 
                                       line: Tuple[int, int, int, int]) -> float:
        """Measure line thickness perpendicular to line direction at given point"""
        x, y = point
        x1, y1, x2, y2 = line
        
        # Calculate perpendicular direction
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return 1.0
        
        # Normalize and rotate 90 degrees
        perp_dx = -dy / length
        perp_dy = dx / length
        
        # Sample along perpendicular direction
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        thickness = 0
        for dist in range(1, 20):  # Sample up to 20 pixels away
            for direction in [-1, 1]:
                sample_x = int(x + direction * dist * perp_dx)
                sample_y = int(y + direction * dist * perp_dy)
                
                if (0 <= sample_x < gray.shape[1] and 0 <= sample_y < gray.shape[0]):
                    if gray[sample_y, sample_x] < 128:  # Dark pixel (part of line)
                        thickness = max(thickness, dist)
                    else:
                        break
        
        return thickness * 2  # Both directions
    
    def _check_line_continuity(self, image: np.ndarray, line: Tuple[int, int, int, int]) -> float:
        """Check how continuous a line is (0.0 = broken, 1.0 = solid)"""
        x1, y1, x2, y2 = line
        
        # Sample points along the line
        num_samples = max(5, int(np.sqrt((x2-x1)**2 + (y2-y1)**2) / 5))
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        dark_pixels = 0
        
        for i in range(num_samples):
            t = i / (num_samples - 1) if num_samples > 1 else 0
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            
            if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
                if gray[y, x] < 128:  # Dark pixel
                    dark_pixels += 1
        
        return dark_pixels / num_samples if num_samples > 0 else 0.0
    
    def _extract_component_pins(self, detected_components: List[Dict], image: np.ndarray) -> List[Dict]:
        """Extract connection points (pins) from detected components"""
        component_pins = []
        
        for component in detected_components:
            bbox = component['bbox']
            comp_id = component['id']
            comp_type = component.get('component_type', 'unknown')
            
            # Extract pins based on component type
            pins = self._get_component_pin_locations(bbox, comp_type, image)
            
            for pin_idx, pin_pos in enumerate(pins):
                component_pins.append({
                    'pin_id': f'{comp_id}_pin_{pin_idx}',
                    'component_id': comp_id,
                    'position': pin_pos,
                    'pin_number': pin_idx + 1,
                    'component_type': comp_type
                })
        
        return component_pins
    
    def _get_component_pin_locations(self, bbox: List[float], comp_type: str, 
                                   image: np.ndarray) -> List[Tuple[int, int]]:
        """Determine pin locations based on component type and bbox"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        pins = []
        
        if comp_type in ['resistor', 'inductor']:
            # Two pins on opposite ends
            pins = [
                (int(x1), int(center_y)),  # Left pin
                (int(x2), int(center_y))   # Right pin
            ]
        elif comp_type == 'capacitor':
            # Two pins on opposite sides
            pins = [
                (int(x1), int(center_y)),  # Left pin
                (int(x2), int(center_y))   # Right pin
            ]
        elif comp_type in ['transistor', 'op_amp', 'ic']:
            # Multiple pins - estimate based on component size
            width = x2 - x1
            height = y2 - y1
            
            if width > height:  # Horizontal orientation
                # Pins on top and bottom
                num_pins = max(2, int(width / 20))  # Estimate pin count
                for i in range(num_pins):
                    pin_x = x1 + (i + 1) * width / (num_pins + 1)
                    pins.extend([
                        (int(pin_x), int(y1)),  # Top pin
                        (int(pin_x), int(y2))   # Bottom pin
                    ])
            else:  # Vertical orientation
                # Pins on left and right
                num_pins = max(2, int(height / 20))
                for i in range(num_pins):
                    pin_y = y1 + (i + 1) * height / (num_pins + 1)
                    pins.extend([
                        (int(x1), int(pin_y)),  # Left pin
                        (int(x2), int(pin_y))   # Right pin
                    ])
        elif comp_type == 'voltage_source':
            # Two pins
            pins = [
                (int(center_x), int(y1)),  # Top pin
                (int(center_x), int(y2))   # Bottom pin
            ]
        elif comp_type == 'ground':
            # Single pin
            pins = [(int(center_x), int(y1))]  # Top pin
        else:
            # Default: assume 2 pins
            pins = [
                (int(x1), int(center_y)),
                (int(x2), int(center_y))
            ]
        
        return pins
    
    def _build_connection_network(self, electrical_connections: List[Dict], 
                                component_pins: List[Dict], 
                                detected_components: List[Dict]) -> List[Connection]:
        """Build network of connections between components"""
        connections = []
        proximity_threshold = 25  # pixels
        
        for conn in electrical_connections:
            start_point = conn['start_point']
            end_point = conn['end_point']
            
            # Find components connected by this connection
            connected_components = []
            
            # Check start point proximity to component pins
            for pin in component_pins:
                pin_pos = pin['position']
                dist_start = np.sqrt((start_point[0] - pin_pos[0])**2 + 
                                   (start_point[1] - pin_pos[1])**2)
                dist_end = np.sqrt((end_point[0] - pin_pos[0])**2 + 
                                 (end_point[1] - pin_pos[1])**2)
                
                if dist_start < proximity_threshold or dist_end < proximity_threshold:
                    connected_components.append(pin['component_id'])
            
            # Remove duplicates
            connected_components = list(set(connected_components))
            
            if len(connected_components) >= 1:  # Valid connection
                connections.append(Connection(
                    start_point=start_point,
                    end_point=end_point,
                    path=[start_point, end_point],
                    connection_type=conn['connection_type'],
                    confidence=conn['confidence'],
                    connected_components=connected_components
                ))
        
        return connections
    
    def _identify_electrical_nodes(self, connections: List[Connection], 
                                 component_pins: List[Dict]) -> List[Node]:
        """Identify electrical nodes (equipotential points)"""
        nodes = []
        processed_pins = set()
        node_counter = 0
        
        # Group connected pins into nodes
        for pin in component_pins:
            if pin['pin_id'] in processed_pins:
                continue
            
            # Find all pins connected to this pin
            connected_pins = self._find_connected_pins(pin, connections, component_pins)
            
            if connected_pins:
                # Create node from connected pins
                node_id = f"node_{node_counter}"
                node_counter += 1
                
                # Calculate average position
                positions = [p['position'] for p in connected_pins]
                avg_x = sum(pos[0] for pos in positions) / len(positions)
                avg_y = sum(pos[1] for pos in positions) / len(positions)
                
                # Get connected components
                connected_component_ids = list(set(
                    pin['component_id'] for pin in connected_pins
                ))
                
                nodes.append(Node(
                    position=(int(avg_x), int(avg_y)),
                    node_id=node_id,
                    connected_components=connected_component_ids,
                    connection_count=len(connected_pins)
                ))
                
                # Mark pins as processed
                for pin in connected_pins:
                    processed_pins.add(pin['pin_id'])
        
        return nodes
    
    def _find_connected_pins(self, start_pin: Dict, connections: List[Connection], 
                           all_pins: List[Dict]) -> List[Dict]:
        """Find all pins electrically connected to the given pin"""
        connected_pins = [start_pin]
        processed = {start_pin['pin_id']}
        queue = [start_pin]
        
        while queue:
            current_pin = queue.pop(0)
            
            # Find connections involving this pin's component
            for connection in connections:
                if current_pin['component_id'] in connection.connected_components:
                    # Find other components in this connection
                    for comp_id in connection.connected_components:
                        if comp_id != current_pin['component_id']:
                            # Find pins of the connected component
                            for pin in all_pins:
                                if (pin['component_id'] == comp_id and 
                                    pin['pin_id'] not in processed):
                                    
                                    connected_pins.append(pin)
                                    processed.add(pin['pin_id'])
                                    queue.append(pin)
        
        return connected_pins
    
    def _analyze_circuit_topology(self, connections: List[Connection], 
                                nodes: List[Node], 
                                detected_components: List[Dict]) -> Dict[str, Any]:
        """Analyze overall circuit topology"""
        analysis = {
            'total_connections': len(connections),
            'total_nodes': len(nodes),
            'total_components': len(detected_components),
            'connectivity_matrix': self._build_connectivity_matrix(connections, detected_components),
            'circuit_complexity': self._calculate_circuit_complexity(connections, nodes, detected_components),
            'potential_issues': self._identify_potential_issues(connections, nodes, detected_components)
        }
        
        return analysis
    
    def _build_connectivity_matrix(self, connections: List[Connection], 
                                 components: List[Dict]) -> List[List[int]]:
        """Build adjacency matrix showing component connectivity"""
        n_components = len(components)
        matrix = [[0 for _ in range(n_components)] for _ in range(n_components)]
        
        # Create component ID to index mapping
        comp_id_to_idx = {comp['id']: idx for idx, comp in enumerate(components)}
        
        # Fill matrix based on connections
        for connection in connections:
            connected_comps = connection.connected_components
            
            # Mark all pairs as connected
            for i, comp_id_1 in enumerate(connected_comps):
                for comp_id_2 in connected_comps[i+1:]:
                    if comp_id_1 in comp_id_to_idx and comp_id_2 in comp_id_to_idx:
                        idx1 = comp_id_to_idx[comp_id_1]
                        idx2 = comp_id_to_idx[comp_id_2]
                        matrix[idx1][idx2] = 1
                        matrix[idx2][idx1] = 1  # Symmetric
        
        return matrix
    
    def _build_connection_matrix(self, connections: List[Connection], 
                               components: List[Dict]) -> Dict[str, Any]:
        """Build comprehensive connection matrix with metadata"""
        connectivity_matrix = self._build_connectivity_matrix(connections, components)
        
        return {
            'adjacency_matrix': connectivity_matrix,
            'component_ids': [comp['id'] for comp in components],
            'connection_strengths': self._calculate_connection_strengths(connections),
            'isolated_components': self._find_isolated_components(connectivity_matrix, components)
        }
    
    def _calculate_connection_strengths(self, connections: List[Connection]) -> Dict[str, float]:
        """Calculate connection strength between component pairs"""
        strengths = {}
        
        for connection in connections:
            connected_comps = connection.connected_components
            for i, comp1 in enumerate(connected_comps):
                for comp2 in connected_comps[i+1:]:
                    pair_key = f"{comp1}-{comp2}"
                    reverse_key = f"{comp2}-{comp1}"
                    
                    strength = connection.confidence
                    
                    # Use higher strength if already exists
                    existing_strength = strengths.get(pair_key, strengths.get(reverse_key, 0))
                    strengths[pair_key] = max(strength, existing_strength)
        
        return strengths
    
    def _find_isolated_components(self, connectivity_matrix: List[List[int]], 
                                components: List[Dict]) -> List[str]:
        """Find components with no connections"""
        isolated = []
        
        for i, row in enumerate(connectivity_matrix):
            if sum(row) == 0:  # No connections
                isolated.append(components[i]['id'])
        
        return isolated
    
    def _calculate_circuit_complexity(self, connections: List[Connection], 
                                   nodes: List[Node], 
                                   components: List[Dict]) -> Dict[str, float]:
        """Calculate various circuit complexity metrics"""
        n_components = len(components)
        n_connections = len(connections)
        n_nodes = len(nodes)
        
        # Basic complexity metrics
        complexity = {
            'component_density': n_connections / max(n_components, 1),
            'node_complexity': n_nodes / max(n_components, 1),
            'connection_ratio': n_connections / max(n_components - 1, 1),  # Normalized by minimum spanning tree
            'average_node_degree': sum(node.connection_count for node in nodes) / max(n_nodes, 1)
        }
        
        return complexity
    
    def _identify_potential_issues(self, connections: List[Connection], 
                                 nodes: List[Node], 
                                 components: List[Dict]) -> List[Dict[str, str]]:
        """Identify potential circuit design issues"""
        issues = []
        
        # Check for isolated components
        connectivity_matrix = self._build_connectivity_matrix(connections, components)
        isolated_components = self._find_isolated_components(connectivity_matrix, components)
        
        if isolated_components:
            issues.append({
                'type': 'isolation',
                'severity': 'warning',
                'message': f"Found {len(isolated_components)} isolated components: {', '.join(isolated_components)}"
            })
        
        # Check for high-degree nodes (potential shorts or bus connections)
        high_degree_nodes = [node for node in nodes if node.connection_count > 4]
        if high_degree_nodes:
            issues.append({
                'type': 'high_connectivity',
                'severity': 'info',
                'message': f"Found {len(high_degree_nodes)} nodes with high connectivity (>4 connections)"
            })
        
        # Check for very short connections (potential noise)
        short_connections = [
            conn for conn in connections 
            if np.sqrt((conn.end_point[0] - conn.start_point[0])**2 + 
                      (conn.end_point[1] - conn.start_point[1])**2) < 10
        ]
        
        if short_connections:
            issues.append({
                'type': 'short_connections',
                'severity': 'info',
                'message': f"Found {len(short_connections)} very short connections (possible noise)"
            })
        
        return issues
