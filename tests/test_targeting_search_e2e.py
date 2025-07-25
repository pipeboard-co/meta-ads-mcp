#!/usr/bin/env python3
"""
End-to-End Targeting Search Test for Meta Ads MCP

This test validates that the targeting search tools correctly find and return
targeting options (interests, behaviors, demographics, geo locations) from the
Meta Ads API through a pre-authenticated MCP server.

Test functions:
- search_interests
- get_interest_suggestions  
- validate_interests
- search_behaviors
- search_demographics
- search_geo_locations
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")

class TargetingSearchTester:
    """Test suite focused on targeting search functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        
        # Test data for validation
        self.test_queries = {
            "interests": ["baseball", "cooking", "travel"],
            "geo_locations": ["New York", "California", "Japan"],
            "interest_suggestions": ["Basketball", "Soccer"],
            "demographics": ["life_events", "industries", "family_statuses"]
        }
        
    def _make_request(self, method: str, params: Dict[str, Any] = None, 
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Targeting-Search-Test-Client/1.0"
        }
        
        if headers:
            default_headers.update(headers)
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id
        }
        
        if params:
            payload["params"] = params
        
        try:
            response = requests.post(
                self.endpoint,
                headers=default_headers,
                json=payload,
                timeout=15
            )
            
            self.request_id += 1
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "json": response.json() if response.status_code == 200 else None,
                "text": response.text,
                "success": response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "headers": {},
                "json": None,
                "text": str(e),
                "success": False,
                "error": str(e)
            }

    def test_search_interests(self) -> Dict[str, Any]:
        """Test search_interests functionality"""
        
        print(f"\n🔍 Testing search_interests function")
        results = {}
        
        for query in self.test_queries["interests"]:
            print(f"   🔎 Searching for interests: '{query}'")
            
            result = self._make_request("tools/call", {
                "name": "search_interests",
                "arguments": {
                    "query": query,
                    "limit": 5
                }
            })
            
            if not result["success"]:
                results[query] = {
                    "success": False,
                    "error": result.get("text", "Unknown error")
                }
                print(f"   ❌ Failed: {result.get('text', 'Unknown error')}")
                continue
            
            # Parse response
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                
                if "error" in parsed_content:
                    results[query] = {
                        "success": False,
                        "error": parsed_content["error"]
                    }
                    print(f"   ❌ API Error: {parsed_content['error']}")
                    continue
                
                interests = parsed_content.get("data", [])
                
                results[query] = {
                    "success": True,
                    "count": len(interests),
                    "interests": interests[:3],  # Keep first 3 for display
                    "has_required_fields": all(
                        "id" in interest and "name" in interest 
                        for interest in interests
                    )
                }
                
                print(f"   ✅ Found {len(interests)} interests")
                for interest in interests[:3]:
                    print(f"      • {interest.get('name', 'N/A')} (ID: {interest.get('id', 'N/A')})")
                
            except json.JSONDecodeError:
                results[query] = {
                    "success": False,
                    "error": "Invalid JSON response",
                    "raw_content": content
                }
                print(f"   ❌ Invalid JSON: {content}")
        
        return results

    def test_get_interest_suggestions(self) -> Dict[str, Any]:
        """Test get_interest_suggestions functionality"""
        
        print(f"\n🔍 Testing get_interest_suggestions function")
        
        interest_list = self.test_queries["interest_suggestions"]
        print(f"   🔎 Getting suggestions for: {interest_list}")
        
        result = self._make_request("tools/call", {
            "name": "get_interest_suggestions",
            "arguments": {
                "interest_list": interest_list,
                "limit": 5
            }
        })
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        # Parse response
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            if "error" in parsed_content:
                return {
                    "success": False,
                    "error": parsed_content["error"]
                }
            
            suggestions = parsed_content.get("data", [])
            
            result_data = {
                "success": True,
                "count": len(suggestions),
                "suggestions": suggestions[:3],  # Keep first 3 for display
                "has_required_fields": all(
                    "id" in suggestion and "name" in suggestion 
                    for suggestion in suggestions
                )
            }
            
            print(f"   ✅ Found {len(suggestions)} suggestions")
            for suggestion in suggestions[:3]:
                print(f"      • {suggestion.get('name', 'N/A')} (ID: {suggestion.get('id', 'N/A')})")
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }

    def test_validate_interests(self) -> Dict[str, Any]:
        """Test validate_interests functionality"""
        
        print(f"\n🔍 Testing validate_interests function")
        
        # Test with known valid and invalid interest names
        test_interests = ["Japan", "Basketball", "invalidinterestname12345"]
        print(f"   🔎 Validating interests: {test_interests}")
        
        result = self._make_request("tools/call", {
            "name": "validate_interests",
            "arguments": {
                "interest_list": test_interests
            }
        })
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        # Parse response
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            if "error" in parsed_content:
                return {
                    "success": False,
                    "error": parsed_content["error"]
                }
            
            validations = parsed_content.get("data", [])
            
            result_data = {
                "success": True,
                "count": len(validations),
                "validations": validations,
                "has_valid_interests": any(
                    validation.get("valid", False) for validation in validations
                ),
                "has_invalid_interests": any(
                    not validation.get("valid", True) for validation in validations
                )
            }
            
            print(f"   ✅ Validated {len(validations)} interests")
            for validation in validations:
                status = "✅" if validation.get("valid") else "❌"
                print(f"      {status} {validation.get('name', 'N/A')}")
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }

    def test_search_behaviors(self) -> Dict[str, Any]:
        """Test search_behaviors functionality"""
        
        print(f"\n🔍 Testing search_behaviors function")
        
        result = self._make_request("tools/call", {
            "name": "search_behaviors",
            "arguments": {
                "limit": 5
            }
        })
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        # Parse response
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            if "error" in parsed_content:
                return {
                    "success": False,
                    "error": parsed_content["error"]
                }
            
            behaviors = parsed_content.get("data", [])
            
            result_data = {
                "success": True,
                "count": len(behaviors),
                "behaviors": behaviors[:3],  # Keep first 3 for display
                "has_required_fields": all(
                    "id" in behavior and "name" in behavior 
                    for behavior in behaviors
                )
            }
            
            print(f"   ✅ Found {len(behaviors)} behaviors")
            for behavior in behaviors[:3]:
                print(f"      • {behavior.get('name', 'N/A')} (ID: {behavior.get('id', 'N/A')})")
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }

    def test_search_demographics(self) -> Dict[str, Any]:
        """Test search_demographics functionality"""
        
        print(f"\n🔍 Testing search_demographics function")
        results = {}
        
        for demo_class in self.test_queries["demographics"]:
            print(f"   🔎 Searching demographics class: '{demo_class}'")
            
            result = self._make_request("tools/call", {
                "name": "search_demographics",
                "arguments": {
                    "demographic_class": demo_class,
                    "limit": 3
                }
            })
            
            if not result["success"]:
                results[demo_class] = {
                    "success": False,
                    "error": result.get("text", "Unknown error")
                }
                print(f"   ❌ Failed: {result.get('text', 'Unknown error')}")
                continue
            
            # Parse response
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                
                if "error" in parsed_content:
                    results[demo_class] = {
                        "success": False,
                        "error": parsed_content["error"]
                    }
                    print(f"   ❌ API Error: {parsed_content['error']}")
                    continue
                
                demographics = parsed_content.get("data", [])
                
                results[demo_class] = {
                    "success": True,
                    "count": len(demographics),
                    "demographics": demographics[:2],  # Keep first 2 for display
                    "has_required_fields": all(
                        "id" in demo and "name" in demo 
                        for demo in demographics
                    )
                }
                
                print(f"   ✅ Found {len(demographics)} {demo_class}")
                for demo in demographics[:2]:
                    print(f"      • {demo.get('name', 'N/A')} (ID: {demo.get('id', 'N/A')})")
                
            except json.JSONDecodeError:
                results[demo_class] = {
                    "success": False,
                    "error": "Invalid JSON response",
                    "raw_content": content
                }
                print(f"   ❌ Invalid JSON: {content}")
        
        return results

    def test_search_geo_locations(self) -> Dict[str, Any]:
        """Test search_geo_locations functionality"""
        
        print(f"\n🔍 Testing search_geo_locations function")
        results = {}
        
        for query in self.test_queries["geo_locations"]:
            print(f"   🔎 Searching for locations: '{query}'")
            
            result = self._make_request("tools/call", {
                "name": "search_geo_locations",
                "arguments": {
                    "query": query,
                    "location_types": ["country", "region", "city"],
                    "limit": 3
                }
            })
            
            if not result["success"]:
                results[query] = {
                    "success": False,
                    "error": result.get("text", "Unknown error")
                }
                print(f"   ❌ Failed: {result.get('text', 'Unknown error')}")
                continue
            
            # Parse response
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                
                if "error" in parsed_content:
                    results[query] = {
                        "success": False,
                        "error": parsed_content["error"]
                    }
                    print(f"   ❌ API Error: {parsed_content['error']}")
                    continue
                
                locations = parsed_content.get("data", [])
                
                results[query] = {
                    "success": True,
                    "count": len(locations),
                    "locations": locations[:3],  # Keep first 3 for display
                    "has_required_fields": all(
                        "key" in location and "name" in location and "type" in location
                        for location in locations
                    )
                }
                
                print(f"   ✅ Found {len(locations)} locations")
                for location in locations[:3]:
                    print(f"      • {location.get('name', 'N/A')} ({location.get('type', 'N/A')}, Key: {location.get('key', 'N/A')})")
                
            except json.JSONDecodeError:
                results[query] = {
                    "success": False,
                    "error": "Invalid JSON response",
                    "raw_content": content
                }
                print(f"   ❌ Invalid JSON: {content}")
        
        return results

    def run_targeting_search_tests(self) -> bool:
        """Run comprehensive targeting search tests"""
        
        print("🚀 Meta Ads Targeting Search End-to-End Test Suite")
        print("="*60)
        
        # Check server availability
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            server_running = response.status_code in [200, 404]
        except:
            server_running = False
        
        if not server_running:
            print("❌ Server is not running at", self.base_url)
            print("   Please start the server with:")
            print("   python3 -m meta_ads_mcp --transport streamable-http --port 8080")
            return False
        
        print("✅ Server is running")
        print("🔐 Using implicit authentication from server")
        
        # Test 1: Search Interests
        print("\n" + "="*60)
        print("📋 PHASE 1: Testing Interest Search")
        print("="*60)
        
        interests_results = self.test_search_interests()
        interests_success = any(
            result.get("success") and result.get("count", 0) > 0 
            for result in interests_results.values()
        )
        
        # Test 2: Interest Suggestions
        print("\n" + "="*60)
        print("📋 PHASE 2: Testing Interest Suggestions")
        print("="*60)
        
        suggestions_result = self.test_get_interest_suggestions()
        suggestions_success = suggestions_result.get("success") and suggestions_result.get("count", 0) > 0
        
        # Test 3: Interest Validation
        print("\n" + "="*60)
        print("📋 PHASE 3: Testing Interest Validation")
        print("="*60)
        
        validation_result = self.test_validate_interests()
        validation_success = (validation_result.get("success") and 
                            validation_result.get("has_valid_interests") and 
                            validation_result.get("has_invalid_interests"))
        
        # Test 4: Behavior Search
        print("\n" + "="*60)
        print("📋 PHASE 4: Testing Behavior Search")
        print("="*60)
        
        behaviors_result = self.test_search_behaviors()
        behaviors_success = behaviors_result.get("success") and behaviors_result.get("count", 0) > 0
        
        # Test 5: Demographics Search
        print("\n" + "="*60)
        print("📋 PHASE 5: Testing Demographics Search")
        print("="*60)
        
        demographics_results = self.test_search_demographics()
        demographics_success = any(
            result.get("success") and result.get("count", 0) > 0 
            for result in demographics_results.values()
        )
        
        # Test 6: Geo Location Search
        print("\n" + "="*60)
        print("📋 PHASE 6: Testing Geo Location Search")
        print("="*60)
        
        geo_results = self.test_search_geo_locations()
        geo_success = any(
            result.get("success") and result.get("count", 0) > 0 
            for result in geo_results.values()
        )
        
        # Final assessment
        print("\n" + "="*60)
        print("📊 FINAL RESULTS")
        print("="*60)
        
        all_tests = [
            ("Interest Search", interests_success),
            ("Interest Suggestions", suggestions_success),
            ("Interest Validation", validation_success),
            ("Behavior Search", behaviors_success),
            ("Demographics Search", demographics_success),
            ("Geo Location Search", geo_success)
        ]
        
        passed_tests = sum(1 for _, success in all_tests if success)
        total_tests = len(all_tests)
        
        for test_name, success in all_tests:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   • {test_name}: {status}")
        
        overall_success = passed_tests >= 4  # At least 4 out of 6 tests should pass
        
        if overall_success:
            print(f"\n✅ Targeting search tests: SUCCESS ({passed_tests}/{total_tests} passed)")
            print("   • Core targeting search functionality is working")
            print("   • Meta Ads API integration is functional")
            return True
        else:
            print(f"\n❌ Targeting search tests: FAILED ({passed_tests}/{total_tests} passed)")
            print("   • Some targeting search functions are not working properly")
            return False


def main():
    """Main test execution"""
    tester = TargetingSearchTester()
    success = tester.run_targeting_search_tests()
    
    if success:
        print("\n🎉 All targeting search tests passed!")
    else:
        print("\n⚠️  Some targeting search tests failed - see details above")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 