"""
SPICE Netlist Generation from Detected Circuit Topology
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .connection_detector import Connection, Node

logger = logging.getLogger(__name__)

@dataclass
class SPICEComponent:
    """Represents a SPICE component with its parameters"""
    name: str
    component_type: str
    nodes: List[str]
    value: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class NetlistGenerator:
    """Generates SPICE netlists from circuit topology analysis"""
    
    def __init__(self):
        self.component_counter = {}  # Track component naming
    
    def generate_spice_netlist(self, components, connections, nodes):
        """
        Generate SPICE netlist from detected components and topology
        """
        try:
            netlist_lines = []
            netlist_lines.append("* Generated SPICE Netlist")
            netlist_lines.append("* Hardware AI Orchestrator")
            netlist_lines.append("")
            
            spice_components = []
            
            # Process each component
            for comp in components:  # ✅ Use 'comp' not 'component'
                try:
                    designation = comp.get('designation', f"COMP{len(spice_components)+1}")
                    component_type = comp.get('component_type', 'unknown')
                    value = comp.get('value', '1')
                    
                    # Convert to SPICE format
                    if component_type.lower() == 'resistor':
                        spice_line = f"R{designation} N1 N2 {value}"
                    elif component_type.lower() == 'capacitor':
                        spice_line = f"C{designation} N1 N2 {value}"
                    elif component_type.lower() == 'inductor':
                        spice_line = f"L{designation} N1 N2 {value}"
                    else:
                        spice_line = f"X{designation} N1 N2 {component_type}"
                    
                    netlist_lines.append(spice_line)
                    spice_components.append({
                        'designation': designation,
                        'type': component_type,
                        'value': value,
                        'spice_line': spice_line
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process component {comp}: {e}")
                    continue
            
            # Add analysis commands
            netlist_lines.append("")
            netlist_lines.append(".op")
            netlist_lines.append(".end")
            
            netlist_text = "\n".join(netlist_lines)
            
            return {
                'netlist': netlist_text,
                'components': spice_components,
                'node_mapping': {},
                'analysis_commands': ['.op'],
                'metadata': {
                    'generation_success': True,
                    'total_components': len(spice_components)
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Netlist generation failed: {e}")
            return {
                'netlist': '',
                'components': [],
                'node_mapping': {},
                'analysis_commands': [],
                'metadata': {
                    'generation_success': False,
                    'error': str(e)
                }
            }

    
    def _convert_components_to_spice(self, detected_components: List[Dict], 
                                   nodes: List[Node]) -> List[SPICEComponent]:
        """Convert detected components to SPICE format"""
        spice_components = []
        
        for component in detected_components:
            comp_type = component.get('component_type', 'unknown')
            comp_id = component['id']
            designation = component.get('designation', '')
            value = component.get('value', '')
            
            # Generate SPICE component
            spice_comp = self._create_spice_component(
                comp_type, comp_id, designation, value, nodes
            )
            
            if spice_comp:
                spice_components.append(spice_comp)
        
        return spice_components
    
    def _create_spice_component(self, comp_type: str, comp_id: str, 
                              designation: str, value: str, 
                              nodes: List[Node]) -> Optional[SPICEComponent]:
        """Create SPICE component from detected component"""
        
        # Find nodes connected to this component
        connected_nodes = [
            node.node_id for node in nodes 
            if comp_id in node.connected_components
        ]
        
        # Generate SPICE name
        spice_name = self._generate_spice_name(comp_type, designation)
        
        # Component-specific SPICE generation
        if comp_type == 'resistor':
            return SPICEComponent(
                name=spice_name,
                component_type='R',
                nodes=connected_nodes[:2],  # Resistors have 2 nodes
                value=self._parse_resistance_value(value),
                parameters={'tolerance': component.get('tolerance')}
            )
            
        elif comp_type == 'capacitor':
            return SPICEComponent(
                name=spice_name,
                component_type='C',
                nodes=connected_nodes[:2],  # Capacitors have 2 nodes
                value=self._parse_capacitance_value(value),
                parameters={'voltage_rating': self._estimate_voltage_rating(value)}
            )
            
        elif comp_type == 'inductor':
            return SPICEComponent(
                name=spice_name,
                component_type='L',
                nodes=connected_nodes[:2],  # Inductors have 2 nodes
                value=self._parse_inductance_value(value)
            )
            
        elif comp_type == 'voltage_source':
            return SPICEComponent(
                name=spice_name,
                component_type='V',
                nodes=connected_nodes[:2],  # Voltage sources have 2 nodes
                value=self._parse_voltage_value(value),
                parameters={'type': 'DC'}
            )
            
        elif comp_type == 'diode':
            return SPICEComponent(
                name=spice_name,
                component_type='D',
                nodes=connected_nodes[:2],  # Diodes have 2 nodes
                model='1N4148',  # Default diode model
                parameters={'area': 1}
            )
            
        elif comp_type in ['transistor', 'op_amp']:
            # Multi-terminal devices - more complex
            return SPICEComponent(
                name=spice_name,
                component_type='Q' if comp_type == 'transistor' else 'X',
                nodes=connected_nodes,  # Use all connected nodes
                model=self._get_default_model(comp_type, designation),
                parameters={'type': comp_type}
            )
        
        # Default/unknown component
        return SPICEComponent(
            name=spice_name,
            component_type='R',  # Default to resistor
            nodes=connected_nodes[:2],
            value='1k',  # Default value
            parameters={'note': f'Unknown component type: {comp_type}'}
        )
    
    def _generate_spice_name(self, comp_type: str, designation: str) -> str:
        """Generate appropriate SPICE component name"""
        if designation and len(designation) > 1:
            # Use designation if available (R1, C2, etc.)
            return designation.upper()
        
        # Generate name based on type
        type_prefixes = {
            'resistor': 'R',
            'capacitor': 'C',
            'inductor': 'L',
            'voltage_source': 'V',
            'current_source': 'I',
            'diode': 'D',
            'transistor': 'Q',
            'op_amp': 'U'
        }
        
        prefix = type_prefixes.get(comp_type, 'X')
        
        # Get counter for this type
        if prefix not in self.component_counter:
            self.component_counter[prefix] = 1
        else:
            self.component_counter[prefix] += 1
        
        return f"{prefix}{self.component_counter[prefix]}"
    
    def _parse_resistance_value(self, value_str: str) -> str:
        """Parse resistance value to SPICE format"""
        if not value_str:
            return '1k'  # Default
        
        # Handle common formats: "10k", "10kΩ", "10000", etc.
        value_str = value_str.replace('Ω', '').replace('ohm', '').replace(' ', '').lower()
        
        # Convert multipliers
        if 'k' in value_str:
            return value_str  # SPICE understands 'k'
        elif 'm' in value_str and 'meg' not in value_str:
            return value_str.replace('m', 'meg')  # SPICE uses 'meg' for million
        elif 'g' in value_str:
            return value_str.replace('g', 'g')  # SPICE understands 'g'
        
        return value_str if value_str else '1k'
    
    def _parse_capacitance_value(self, value_str: str) -> str:
        """Parse capacitance value to SPICE format"""
        if not value_str:
            return '1n'  # Default
        
        value_str = value_str.replace('F', '').replace(' ', '').lower()
        
        # SPICE capacitance multipliers
        multiplier_map = {
            'μ': 'u',  # Micro
            'u': 'u',  # Micro  
            'n': 'n',  # Nano
            'p': 'p',  # Pico
            'f': 'f'   # Femto
        }
        
        for old, new in multiplier_map.items():
            value_str = value_str.replace(old, new)
        
        return value_str if value_str else '1n'
    
    def _parse_inductance_value(self, value_str: str) -> str:
        """Parse inductance value to SPICE format"""
        if not value_str:
            return '1u'  # Default
        
        value_str = value_str.replace('H', '').replace(' ', '').lower()
        
        # Convert multipliers similar to capacitance
        multiplier_map = {
            'μ': 'u',
            'u': 'u',
            'm': 'm',
            'n': 'n'
        }
        
        for old, new in multiplier_map.items():
            value_str = value_str.replace(old, new)
        
        return value_str if value_str else '1u'
    
    def _parse_voltage_value(self, value_str: str) -> str:
        """Parse voltage value to SPICE format"""
        if not value_str:
            return '5'  # Default 5V
        
        # Remove 'V' and spaces
        value_str = value_str.replace('V', '').replace(' ', '').lower()
        
        # Handle multipliers
        if 'k' in value_str:
            return value_str  # SPICE understands 'k'
        elif 'm' in value_str:
            return value_str.replace('m', 'm')
        
        return value_str if value_str else '5'
    
    def _estimate_voltage_rating(self, value_str: str) -> str:
        """Estimate voltage rating for capacitors"""
        # Simple heuristic based on capacitance value
        if not value_str:
            return '16V'
        
        if 'μ' in value_str or 'u' in value_str:
            # Larger capacitors usually lower voltage
            return '16V'
        elif 'n' in value_str:
            # Smaller capacitors can handle higher voltage
            return '50V'
        elif 'p' in value_str:
            # Very small capacitors, high voltage
            return '100V'
        
        return '25V'  # Default
    
    def _get_default_model(self, comp_type: str, designation: str) -> str:
        """Get default SPICE model for complex components"""
        if comp_type == 'transistor':
            return '2N2222'  # Default NPN transistor
        elif comp_type == 'op_amp':
            if 'lm358' in designation.lower():
                return 'LM358'
            else:
                return 'UA741'  # Default op-amp
        
        return 'DEFAULT'
    
    def _build_node_mapping(self, nodes: List[Node], 
                          connections: List[Connection]) -> Dict[str, int]:
        """Build mapping from node IDs to SPICE node numbers"""
        node_mapping = {}
        
        # Reserve node 0 for ground
        node_mapping['gnd'] = 0
        node_mapping['ground'] = 0
        
        # Assign numbers to other nodes
        node_number = 1
        for node in nodes:
            if node.node_id not in node_mapping:
                node_mapping[node.node_id] = node_number
                node_number += 1
        
        return node_mapping
    
    def _generate_netlist_text(self, spice_components: List[SPICEComponent], 
                             node_mapping: Dict[str, int]) -> List[str]:
        """Generate SPICE netlist text lines"""
        netlist_lines = []
        
        for component in spice_components:
            line_parts = [component.name]
            
            # Add nodes
            for node_id in component.nodes:
                node_number = node_mapping.get(node_id, 0)
                line_parts.append(str(node_number))
            
            # Add value or model
            if component.model:
                line_parts.append(component.model)
            elif component.value:
                line_parts.append(component.value)
            
            # Add parameters if any
            if component.parameters:
                for param, value in component.parameters.items():
                    if param not in ['tolerance', 'voltage_rating', 'note', 'type']:
                        line_parts.append(f"{param}={value}")
            
            netlist_lines.append(' '.join(line_parts))
        
        return netlist_lines
    
    def _generate_analysis_commands(self, spice_components: List[SPICEComponent]) -> List[str]:
        """Generate appropriate SPICE analysis commands"""
        commands = []
        
        # Basic operating point analysis
        commands.append('.op')
        
        # DC sweep if voltage sources present
        voltage_sources = [c for c in spice_components if c.component_type == 'V']
        if voltage_sources:
            # Simple DC analysis
            commands.append('.dc V1 0 10 0.1')
        
        # AC analysis if reactive components present
        reactive_components = [c for c in spice_components 
                             if c.component_type in ['C', 'L']]
        if reactive_components:
            commands.append('.ac dec 10 1 1meg')
        
        # Transient analysis for circuits with time-varying elements
        commands.append('.tran 1n 1u')
        
        return commands
    
    def _assemble_complete_netlist(self, netlist_lines: List[str], 
                                 analysis_commands: List[str],
                                 spice_components: List[SPICEComponent]) -> str:
        """Assemble complete SPICE netlist with headers and analysis"""
        lines = []
        
        # Title
        lines.append('* SPICE Netlist Generated by Hardware AI Orchestrator')
        lines.append('* Generated from schematic analysis')
        lines.append('')
        
        # Component lines
        lines.append('* Circuit Components')
        lines.extend(netlist_lines)
        lines.append('')
        
        # Analysis commands
        lines.append('* Analysis Commands')
        lines.extend(analysis_commands)
        lines.append('')
        
        # Control commands
        lines.append('* Control Commands')
        lines.append('.control')
        lines.append('run')
        lines.append('print all')
        lines.append('.endc')
        lines.append('')
        
        # End
        lines.append('.end')
        
        return '\n'.join(lines)
