"""
Hardware Complexity Scoring Algorithm
Evaluates queries on 6 technical complexity factors, produces 0.0-1.0 scores
"""
from typing import Dict, List
import re
from ..config.complexity_weights import COMPLEXITY_FACTORS

class HardwareComplexityScorer:
    def __init__(self):
        self.factors = COMPLEXITY_FACTORS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each complexity factor"""
        self.patterns = {}
        
        # Technical keywords density pattern
        tech_keywords = self.factors["technical_keywords_density"]["high_complexity_keywords"]
        self.patterns["technical"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in tech_keywords) + r')\b', 
            re.IGNORECASE
        )
        
        # Design constraints pattern
        constraint_keywords = self.factors["design_constraint_count"]["constraint_keywords"]
        self.patterns["constraints"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in constraint_keywords) + r')\b',
            re.IGNORECASE
        )
        
        # Calculation complexity pattern
        calc_keywords = self.factors["calculation_complexity"]["calculation_keywords"]
        self.patterns["calculations"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in calc_keywords) + r')\b',
            re.IGNORECASE
        )
        
        # Standards involvement pattern
        standards_keywords = self.factors["standards_involvement"]["standards_keywords"]
        self.patterns["standards"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in standards_keywords) + r')\b',
            re.IGNORECASE
        )
        
        # Multi-domain integration pattern
        integration_keywords = self.factors["multi_domain_integration"]["integration_keywords"]
        self.patterns["integration"] = re.compile(
            r'\b(' + '|'.join(re.escape(kw) for kw in integration_keywords) + r')\b',
            re.IGNORECASE
        )
    
    def calculate_complexity(self, query: str, domain: str = None, intent: str = None) -> Dict[str, float]:
        """
        Calculate complexity score based on 6 factors - ENHANCED for automotive
        Returns detailed breakdown and final score
        """
        query_lower = query.lower()
        factor_scores = {}
        
        # Debug output to track scoring
        print(f"🔍 Debug - Query: {query[:50]}...")
        print(f"🔍 Debug - Domain: {domain}")
        
        # 1. Technical Keywords Density (30% weight)
        tech_matches = len(self.patterns["technical"].findall(query))
        tech_density = min(tech_matches * 0.2, 1.0)
        factor_scores["technical_keywords_density"] = tech_density
        print(f"🔍 Debug - Tech matches: {tech_matches}, Score: {tech_density}")
        
        # 2. Design Constraint Count (15% weight)
        constraint_matches = len(self.patterns["constraints"].findall(query))
        constraint_score = min(constraint_matches * 0.25, 1.0)
        factor_scores["design_constraint_count"] = constraint_score
        print(f"🔍 Debug - Constraint matches: {constraint_matches}, Score: {constraint_score}")
        
        # 3. Domain Specificity (25% weight) - ENHANCED
        high_spec_domains = self.factors["domain_specificity"]["high_specificity_domains"]
        if domain and any(d.lower() in domain.lower() for d in high_spec_domains):
            domain_score = 1.0  # ← Boosted from 0.8
            print(f"🔍 Debug - High-spec domain matched: {domain}")
        elif domain:
            domain_score = 0.6  # ← Boosted from 0.5
        else:
            domain_score = 0.3
        factor_scores["domain_specificity"] = domain_score
        
        # 4. Calculation Complexity (15% weight)
        calc_matches = len(self.patterns["calculations"].findall(query))
        calc_score = min(calc_matches * 0.3, 1.0)
        factor_scores["calculation_complexity"] = calc_score
        
        # 5. Standards Involvement (15% weight) - ENHANCED
        standards_matches = len(self.patterns["standards"].findall(query))
        # Special boost for critical automotive standards
        if any(std in query.upper() for std in ["AEC-Q100", "ISO 26262", "ASIL"]):
            standards_score = min(standards_matches * 0.6, 1.0)  # ← Boosted multiplier
            print(f"🔍 Debug - Critical automotive standard found!")
        else:
            standards_score = min(standards_matches * 0.4, 1.0)
        factor_scores["standards_involvement"] = standards_score
        print(f"🔍 Debug - Standards matches: {standards_matches}, Score: {standards_score}")
        
        # 6. Multi-Domain Integration (5% weight)
        integration_matches = len(self.patterns["integration"].findall(query))
        integration_score = min(integration_matches * 0.5, 1.0)
        factor_scores["multi_domain_integration"] = integration_score
        
        # Calculate weighted final score
        final_score = 0.0
        for factor, score in factor_scores.items():
            weight = self.factors[factor]["weight"]
            final_score += score * weight
            print(f"🔍 Debug - {factor}: {score:.3f} × {weight:.3f} = {score * weight:.3f}")
        
        # Add query length complexity (longer queries often more complex)
        word_count = len(query.split())
        length_bonus = min(word_count / 50, 0.1)  # Max 0.1 bonus
        final_score += length_bonus
        
        # Automotive-specific complexity bonus - NEW
        automotive_bonus = 0.0
        if domain and "automotive" in domain.lower():
            automotive_indicators = ["buck converter", "AEC-Q100", "automotive", "grade", "qualification", 
                                "12V", "5V", "3A", "converter", "design"]
            automotive_matches = sum(1 for indicator in automotive_indicators if indicator.lower() in query.lower())
            automotive_bonus = min(automotive_matches * 0.04, 0.15)  # Up to 15% bonus
            final_score += automotive_bonus
            print(f"🔍 Debug - Automotive bonus: {automotive_matches} matches = +{automotive_bonus:.3f}")
        
        # Ensure score is between 0.0 and 1.0
        final_score = max(0.0, min(final_score, 1.0))
        
        print(f"🔍 Debug - Final complexity score: {final_score:.3f}")
        print("=" * 50)
        
        return {
            "factor_scores": factor_scores,
            "final_score": final_score,
            "word_count": word_count,
            "length_bonus": length_bonus,
            "automotive_bonus": automotive_bonus
        }

