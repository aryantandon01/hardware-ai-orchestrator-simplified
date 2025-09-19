"""
Hardware Domain Detection
Identifies queries within 8 major hardware engineering domains
"""
from typing import Dict, List, Tuple
import re
from ..config.domain_definitions import HARDWARE_DOMAINS

class HardwareDomainDetector:
    def __init__(self):
        self.domains = HARDWARE_DOMAINS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient domain matching"""
        self.patterns = {}
        for domain, config in self.domains.items():
            keywords = config["keywords"]
            pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            self.patterns[domain] = re.compile(pattern, re.IGNORECASE)
    
    def detect_domains(self, query: str) -> Dict[str, float]:
        """
        Detect hardware domains in query
        Returns confidence scores for each domain
        """
        domain_scores = {}
        
        for domain, pattern in self.patterns.items():
            matches = pattern.findall(query)
            keyword_count = len(matches)
            
            if keyword_count > 0:
                # Base score from keyword density
                base_score = min(keyword_count * 0.3, 1.0)
                
                # Apply domain complexity weight
                complexity_weight = self.domains[domain]["complexity_weight"]
                final_score = base_score * (complexity_weight / 1.5)  # Normalize
                
                domain_scores[domain] = min(final_score, 1.0)
        
        return domain_scores
    
    def get_primary_domain(self, query: str) -> Tuple[str, float]:
        """Get the highest-confidence domain classification"""
        domain_scores = self.detect_domains(query)
        
        if not domain_scores:
            return "embedded_hardware", 0.5  # Default fallback
        
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])
        return primary_domain
    
    def get_domain_info(self, domain: str) -> Dict:
        """Get complete domain information"""
        return self.domains.get(domain, {})
