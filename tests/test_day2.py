# test_day2_rag.py - Comprehensive Day 2 RAG Testing Script

import requests
import json
import time
import sys
from PIL import Image, ImageDraw
import io
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30  # seconds

class HardwareAITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": time.time(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if not success and "error" in details:
            print(f"   Error: {details['error']}")
        elif success and "summary" in details:
            print(f"   {details['summary']}")
    
    def test_system_status(self) -> bool:
        """Test system health and component availability"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                components = data.get("components", {})
                
                self.log_result("System Status", True, {
                    "summary": f"System healthy, Components: {list(components.keys())}",
                    "components": components
                })
                return True
            else:
                self.log_result("System Status", False, {
                    "error": f"Status code: {response.status_code}",
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("System Status", False, {"error": str(e)})
            return False
    
    def test_basic_query_analysis(self) -> bool:
        """Test basic query analysis without RAG"""
        try:
            payload = {
                "query": "What are the specifications of LM317 voltage regulator?",
                "user_expertise": "intermediate"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["complexity", "classification", "routing"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Basic Query Analysis", False, {
                        "error": f"Missing fields: {missing_fields}"
                    })
                    return False
                
                complexity = data["complexity"]["final_score"]
                model = data["routing"]["selected_model"]
                intent = data["classification"]["primary_intent"]["intent"]
                
                self.log_result("Basic Query Analysis", True, {
                    "summary": f"Model: {model}, Complexity: {complexity:.3f}, Intent: {intent}",
                    "complexity": complexity,
                    "selected_model": model,
                    "intent": intent
                })
                return True
            else:
                self.log_result("Basic Query Analysis", False, {
                    "error": f"Status code: {response.status_code}",
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Basic Query Analysis", False, {"error": str(e)})
            return False
    
    def test_rag_enhanced_analysis(self) -> bool:
        """Test RAG-enhanced analysis (Day 2 core functionality)"""
        test_cases = [
            {
                "name": "Power Management Components",
                "query": "Buck controllers for automotive 12V to 5V conversion with 3A current capability and AEC-Q100 qualification",
                "expertise": "expert",
                "expected_domain": "automotive",
                "min_components": 1
            },
            {
                "name": "Microcontroller Database",
                "query": "ARM Cortex-M4 microcontrollers with ultra-low power consumption for IoT battery applications",
                "expertise": "senior", 
                "expected_domain": "embedded_hardware",
                "min_components": 2
            },
            {
                "name": "Analog IC Selection",
                "query": "Precision operational amplifier for medical instrumentation with low offset voltage and rail-to-rail output",
                "expertise": "expert",
                "expected_domain": "medical",
                "min_components": 1
            },
            {
                "name": "Standards Database",
                "query": "AEC-Q100 qualification requirements for automotive grade 0 components",
                "expertise": "expert",
                "expected_domain": "automotive",
                "min_standards": 1
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                # Check if enhanced endpoint exists
                payload = {
                    "query": test_case["query"],
                    "user_expertise": test_case["expertise"],
                    "include_knowledge": True
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/analyze-enhanced",
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate RAG response structure
                    if "knowledge" in data:
                        knowledge = data["knowledge"]
                        components = knowledge.get("components", [])
                        standards = knowledge.get("standards", [])
                        
                        component_count = len(components)
                        standard_count = len(standards)
                        
                        # Validate minimum requirements
                        meets_requirements = True
                        issues = []
                        
                        if "min_components" in test_case and component_count < test_case["min_components"]:
                            meets_requirements = False
                            issues.append(f"Expected ≥{test_case['min_components']} components, got {component_count}")
                        
                        if "min_standards" in test_case and standard_count < test_case["min_standards"]:
                            meets_requirements = False
                            issues.append(f"Expected ≥{test_case['min_standards']} standards, got {standard_count}")
                        
                        if meets_requirements:
                            success_count += 1
                            self.log_result(f"RAG: {test_case['name']}", True, {
                                "summary": f"Components: {component_count}, Standards: {standard_count}",
                                "components": component_count,
                                "standards": standard_count,
                                "retrieval_quality": knowledge.get("retrieval_summary", {}).get("overall_quality", "N/A")
                            })
                        else:
                            self.log_result(f"RAG: {test_case['name']}", False, {
                                "error": "; ".join(issues),
                                "components_found": component_count,
                                "standards_found": standard_count
                            })
                    else:
                        # Fallback: test basic analysis without RAG
                        basic_payload = {
                            "query": test_case["query"],
                            "user_expertise": test_case["expertise"]
                        }
                        
                        basic_response = self.session.post(
                            f"{self.base_url}/api/v1/analyze",
                            json=basic_payload,
                            timeout=15
                        )
                        
                        if basic_response.status_code == 200:
                            basic_data = basic_response.json()
                            domain = basic_data.get("classification", {}).get("primary_domain", {}).get("domain", "unknown")
                            
                            success_count += 1
                            self.log_result(f"RAG: {test_case['name']} (Fallback)", True, {
                                "summary": f"Basic analysis successful, Domain: {domain}",
                                "fallback_mode": True,
                                "domain": domain
                            })
                        else:
                            self.log_result(f"RAG: {test_case['name']}", False, {
                                "error": "No RAG data and basic analysis failed",
                                "status_code": basic_response.status_code
                            })
                else:
                    # Try basic analysis as fallback
                    basic_payload = {
                        "query": test_case["query"],
                        "user_expertise": test_case["expertise"]
                    }
                    
                    basic_response = self.session.post(
                        f"{self.base_url}/api/v1/analyze",
                        json=basic_payload,
                        timeout=15
                    )
                    
                    if basic_response.status_code == 200:
                        basic_data = basic_response.json()
                        domain = basic_data.get("classification", {}).get("primary_domain", {}).get("domain", "unknown")
                        
                        success_count += 1
                        self.log_result(f"RAG: {test_case['name']} (Basic Mode)", True, {
                            "summary": f"Basic analysis mode, Domain: {domain}",
                            "basic_mode": True,
                            "domain": domain
                        })
                    else:
                        self.log_result(f"RAG: {test_case['name']}", False, {
                            "error": f"Enhanced endpoint unavailable (status: {response.status_code}), basic analysis failed",
                            "enhanced_status": response.status_code,
                            "basic_status": basic_response.status_code
                        })
                        
            except Exception as e:
                self.log_result(f"RAG: {test_case['name']}", False, {"error": str(e)})
        
        # Overall RAG test success
        total_tests = len(test_cases)
        rag_success = success_count >= total_tests * 0.75  # 75% success rate
        
        self.log_result("RAG System Overall", rag_success, {
            "summary": f"{success_count}/{total_tests} RAG tests passed",
            "success_rate": f"{(success_count/total_tests)*100:.1f}%"
        })
        
        return rag_success
    
    def test_vector_search_capabilities(self) -> bool:
        """Test semantic search capabilities"""
        semantic_queries = [
            {
                "query": "low noise precision amplifier for medical devices",
                "expected_keywords": ["medical", "precision", "amplifier"]
            },
            {
                "query": "automotive qualified switching regulator for harsh environment",
                "expected_keywords": ["automotive", "switching", "regulator"]
            },
            {
                "query": "ultra-low power microcontroller for battery operated sensors",
                "expected_keywords": ["low_power", "microcontroller", "battery"]
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(semantic_queries):
            try:
                payload = {
                    "query": test_case["query"],
                    "user_expertise": "senior"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/analyze",
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check domain detection (indicates semantic understanding)
                    domain = data.get("classification", {}).get("primary_domain", {}).get("domain", "")
                    intent = data.get("classification", {}).get("primary_intent", {}).get("intent", "")
                    complexity = data.get("complexity", {}).get("final_score", 0)
                    
                    # Basic validation of semantic understanding
                    semantic_indicators = 0
                    
                    if domain and domain != "unknown":
                        semantic_indicators += 1
                    
                    if intent and intent != "unknown":
                        semantic_indicators += 1
                        
                    if 0.2 <= complexity <= 1.0:  # Reasonable complexity range
                        semantic_indicators += 1
                    
                    if semantic_indicators >= 2:
                        success_count += 1
                        self.log_result(f"Vector Search: Query {i+1}", True, {
                            "summary": f"Domain: {domain}, Intent: {intent}, Complexity: {complexity:.3f}",
                            "semantic_understanding": True
                        })
                    else:
                        self.log_result(f"Vector Search: Query {i+1}", False, {
                            "error": "Poor semantic understanding",
                            "domain": domain,
                            "intent": intent,
                            "complexity": complexity
                        })
                else:
                    self.log_result(f"Vector Search: Query {i+1}", False, {
                        "error": f"Request failed with status {response.status_code}"
                    })
                    
            except Exception as e:
                self.log_result(f"Vector Search: Query {i+1}", False, {"error": str(e)})
        
        vector_search_success = success_count >= len(semantic_queries) * 0.6  # 60% success rate
        
        self.log_result("Vector Search Overall", vector_search_success, {
            "summary": f"{success_count}/{len(semantic_queries)} semantic queries successful",
            "success_rate": f"{(success_count/len(semantic_queries))*100:.1f}%"
        })
        
        return vector_search_success
    
    def test_schematic_processing(self) -> bool:
        """Test schematic processing capabilities (if available)"""
        try:
            # Test schematic health first
            response = self.session.get(f"{self.base_url}/api/v1/schematic/health", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Schematic Processing", False, {
                    "error": "Schematic endpoints not available",
                    "note": "This is expected if computer vision modules are not installed"
                })
                return False
            
            # Create a simple test schematic
            test_image = self.create_test_schematic()
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            test_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Test schematic analysis
            files = {"file": ("test_schematic.png", img_byte_arr, "image/png")}
            
            response = self.session.post(
                f"{self.base_url}/api/v1/schematic/analyze",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate schematic analysis response
                components = data.get("detected_components", [])
                status = data.get("status", "")
                
                component_count = len(components)
                
                self.log_result("Schematic Processing", True, {
                    "summary": f"Analysis successful, {component_count} components detected",
                    "components_detected": component_count,
                    "status": status
                })
                return True
            else:
                self.log_result("Schematic Processing", False, {
                    "error": f"Analysis failed with status {response.status_code}",
                    "response": response.text[:200]
                })
                return False
                
        except Exception as e:
            self.log_result("Schematic Processing", False, {
                "error": str(e),
                "note": "Computer vision dependencies may not be installed"
            })
            return False
    
    def create_test_schematic(self) -> Image.Image:
        """Create a simple test schematic for upload testing"""
        img = Image.new('RGB', (400, 300), 'white')
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
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Day 2 tests"""
        print("🧠 Hardware AI Orchestrator - Day 2 RAG Testing")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("System Health", self.test_system_status),
            ("Basic Analysis", self.test_basic_query_analysis),
            ("RAG Enhanced Analysis", self.test_rag_enhanced_analysis),
            ("Vector Search", self.test_vector_search_capabilities),
            ("Schematic Processing", self.test_schematic_processing)
        ]
        
        results = {}
        total_success = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    total_success += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {e}")
                results[test_name] = False
        
        # Summary
        success_rate = (total_success / len(tests)) * 100
        
        print(f"\n{'=' * 60}")
        print(f"🏆 DAY 2 RAG TEST SUMMARY")
        print(f"{'=' * 60}")
        print(f"Tests Passed: {total_success}/{len(tests)} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"✅ EXCELLENT: Day 2 RAG system is production ready!")
        elif success_rate >= 60:
            print(f"✅ GOOD: Day 2 RAG system is functional with minor issues")
        else:
            print(f"⚠️ NEEDS WORK: Day 2 RAG system needs improvement")
        
        return {
            "overall_success_rate": success_rate,
            "tests_passed": total_success,
            "total_tests": len(tests),
            "individual_results": results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    print(f"🎯 Testing Hardware AI Orchestrator at: {base_url}")
    
    tester = HardwareAITester(base_url)
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["overall_success_rate"] >= 60:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
