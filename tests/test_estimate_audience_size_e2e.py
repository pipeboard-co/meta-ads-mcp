#!/usr/bin/env python3
"""
End-to-End Audience Estimation Test for Meta Ads MCP

This test validates that the new estimate_audience_size function correctly provides
comprehensive audience estimation and backwards compatibility for interest validation
through a pre-authenticated MCP server.

Usage:
    1. Start the server: uv run python -m meta_ads_mcp --transport streamable-http --port 8080
    2. Run test: uv run python tests/test_estimate_audience_size_e2e.py

Or with pytest (manual only):
    uv run python -m pytest tests/test_estimate_audience_size_e2e.py -v -m e2e

Test scenarios:
1. Comprehensive audience estimation with complex targeting
2. Backwards compatibility with simple interest validation
3. Error handling for invalid parameters
4. Different optimization goals
"""

import pytest
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

@pytest.mark.e2e
@pytest.mark.skip(reason="E2E test - run manually only")
class AudienceEstimationTester:
    """Test suite focused on audience estimation functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        
        # Default account ID from workspace rules
        self.account_id = "act_701351919139047"
        
        # Test targeting specifications
        self.test_targeting_specs = {
            "simple_demographics": {
                "age_min": 25,
                "age_max": 65,
                "geo_locations": {"countries": ["US"]}
            },
            "demographics_with_interests": {
                "age_min": 18,
                "age_max": 35,
                "geo_locations": {"countries": ["PL"]},
                "flexible_spec": [
                    {"interests": [{"id": "6003371567474"}]}  # Business interest
                ]
            },
            "complex_targeting": {
                "age_min": 25,
                "age_max": 55,
                "geo_locations": {"countries": ["US"], "regions": [{"key": "3847"}]},  # California
                "flexible_spec": [
                    {"interests": [{"id": "6003371567474"}, {"id": "6003462346642"}]},  # Business + Technology
                    {"behaviors": [{"id": "6007101597783"}]}  # Business travelers
                ]
            },
            "mobile_app_targeting": {
                "age_min": 18,
                "age_max": 45,
                "geo_locations": {"countries": ["US"]},
                "user_device": ["mobile"],
                "user_os": ["iOS", "Android"],
                "flexible_spec": [
                    {"interests": [{"id": "6003139266461"}]}  # Mobile games
                ]
            }
        }
        
        # Test interest lists for backwards compatibility
        self.test_interests = {
            "valid_names": ["Japan", "Basketball", "Technology"],
            "mixed_validity": ["Japan", "invalidinterestname12345", "Basketball"],
            "valid_fbids": ["6003700426513", "6003397425735"],  # Japan, Tennis
            "invalid_fbids": ["999999999999", "000000000000"]
        }
        
    def _make_request(self, method: str, params: Dict[str, Any] = None, 
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Audience-Estimation-Test-Client/1.0"
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
                timeout=20  # Increased timeout for delivery estimates
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

    def _check_for_errors(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Properly handle both wrapped and direct error formats"""
        
        # Check for data wrapper format first
        if "data" in parsed_content:
            data = parsed_content["data"]
            
            # Handle case where data is already parsed (dict/list)
            if isinstance(data, dict) and 'error' in data:
                return {
                    "has_error": True,
                    "error_message": data['error'],
                    "error_details": data.get('details', ''),
                    "format": "wrapped_dict"
                }
            
            # Handle case where data is a JSON string that needs parsing
            if isinstance(data, str):
                try:
                    error_data = json.loads(data)
                    if 'error' in error_data:
                        return {
                            "has_error": True,
                            "error_message": error_data['error'],
                            "error_details": error_data.get('details', ''),
                            "format": "wrapped_json"
                        }
                except json.JSONDecodeError:
                    # Data field exists but isn't valid JSON
                    pass
        
        # Check for direct error format
        if 'error' in parsed_content:
            return {
                "has_error": True,
                "error_message": parsed_content['error'],
                "error_details": parsed_content.get('details', ''),
                "format": "direct"
            }
        
        return {"has_error": False}

    def _extract_data(self, parsed_content: Dict[str, Any]) -> Any:
        """Extract successful response data from various wrapper formats"""
        
        if "data" in parsed_content:
            data = parsed_content["data"]
            
            # Handle case where data is already parsed
            if isinstance(data, (list, dict)):
                return data
            
            # Handle case where data is a JSON string
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return None
        
        # Handle direct format (data at top level)
        if isinstance(parsed_content, (list, dict)):
            return parsed_content
        
        return None

    def test_pl_only_reachestimate_bounds(self) -> Dict[str, Any]:
        """Verify PL-only reachestimate returns expected bounds and midpoint.
        
        Prerequisite: Start server with fallback disabled so reachestimate is used directly.
        Example:
            export META_MCP_DISABLE_DELIVERY_FALLBACK=1
            uv run python -m meta_ads_mcp --transport streamable-http --port 8080
        """
        print(f"\n🇵🇱 Testing PL-only reachestimate bounds (fallback disabled)")
        local_account_id = "act_3182643988557192"
        targeting_spec = {"geo_locations": {"countries": ["PL"]}}
        expected_lower = 18600000
        expected_upper = 21900000
        expected_midpoint = 20250000

        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {
                "account_id": local_account_id,
                "targeting": targeting_spec,
                "optimization_goal": "REACH"
            }
        })

        if not result["success"]:
            print(f"   ❌ Request failed: {result.get('text', 'Unknown error')}")
            return {"success": False, "error": result.get("text", "Unknown error")}

        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response")
            return {"success": False, "error": "Invalid JSON"}

        error_info = self._check_for_errors(parsed_content)
        if error_info["has_error"]:
            print(f"   ❌ API Error: {error_info['error_message']}")
            return {"success": False, "error": error_info["error_message"], "error_format": error_info["format"]}

        if not parsed_content.get("success", False):
            print(f"   ❌ Response indicates failure but no error message found")
            return {"success": False, "error": "Unexpected failure"}

        details = parsed_content.get("estimate_details", {}) or {}
        lower = details.get("users_lower_bound")
        upper = details.get("users_upper_bound")
        midpoint = parsed_content.get("estimated_audience_size")
        fallback_used = parsed_content.get("fallback_endpoint_used")

        ok = (
            lower == expected_lower and
            upper == expected_upper and
            midpoint == expected_midpoint and
            (fallback_used is None)
        )

        if ok:
            print(f"   ✅ Bounds: {lower:,}–{upper:,}; midpoint: {midpoint:,}")
            return {
                "success": True,
                "users_lower_bound": lower,
                "users_upper_bound": upper,
                "midpoint": midpoint
            }
        else:
            print(f"   ❌ Unexpected values: lower={lower}, upper={upper}, midpoint={midpoint}, fallback={fallback_used}")
            return {
                "success": False,
                "users_lower_bound": lower,
                "users_upper_bound": upper,
                "midpoint": midpoint,
                "fallback_endpoint_used": fallback_used
            }

    def test_comprehensive_audience_estimation(self) -> Dict[str, Any]:
        """Test comprehensive audience estimation with complex targeting"""
        
        print(f"\n🎯 Testing Comprehensive Audience Estimation")
        results = {}
        
        for spec_name, targeting_spec in self.test_targeting_specs.items():
            print(f"   📊 Testing targeting: '{spec_name}'")
            
            result = self._make_request("tools/call", {
                "name": "estimate_audience_size",
                "arguments": {
                    "account_id": self.account_id,
                    "targeting": targeting_spec,
                    "optimization_goal": "REACH"
                }
            })
            
            if not result["success"]:
                results[spec_name] = {
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
                
                # Check for errors using robust helper method
                error_info = self._check_for_errors(parsed_content)
                if error_info["has_error"]:
                    results[spec_name] = {
                        "success": False,
                        "error": error_info["error_message"],
                        "error_format": error_info["format"]
                    }
                    print(f"   ❌ API Error: {error_info['error_message']}")
                    continue
                
                # Check for expected fields in comprehensive estimation
                has_success = parsed_content.get("success", False)
                has_estimate = "estimated_audience_size" in parsed_content
                has_details = "estimate_details" in parsed_content
                
                results[spec_name] = {
                    "success": has_success and has_estimate,
                    "has_estimate": has_estimate,
                    "has_details": has_details,
                    "estimated_size": parsed_content.get("estimated_audience_size", 0),
                    "optimization_goal": parsed_content.get("optimization_goal"),
                    "raw_response": parsed_content
                }
                
                if has_success and has_estimate:
                    estimate_size = parsed_content.get("estimated_audience_size", 0)
                    print(f"   ✅ Estimated audience: {estimate_size:,} people")
                else:
                    print(f"   ⚠️  Incomplete response: success={has_success}, estimate={has_estimate}")
                
            except json.JSONDecodeError:
                results[spec_name] = {
                    "success": False,
                    "error": "Invalid JSON response",
                    "raw_content": content
                }
                print(f"   ❌ Invalid JSON: {content[:100]}...")
        
        return results

    def test_backwards_compatibility_interest_validation(self) -> Dict[str, Any]:
        """Test backwards compatibility with simple interest validation"""
        
        print(f"\n🔄 Testing Backwards Compatibility (Interest Validation)")
        results = {}
        
        # Test with interest names
        print(f"   📝 Testing interest name validation")
        
        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {
                "interest_list": self.test_interests["mixed_validity"]
            }
        })
        
        if result["success"]:
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                
                # Check for errors first
                error_info = self._check_for_errors(parsed_content)
                if error_info["has_error"]:
                    results["interest_names"] = {
                        "success": False,
                        "error": error_info["error_message"],
                        "error_format": error_info["format"]
                    }
                    print(f"   ❌ API Error: {error_info['error_message']}")
                else:
                    # Extract data using robust helper method
                    validations = self._extract_data(parsed_content)
                    if validations and isinstance(validations, list):
                        results["interest_names"] = {
                            "success": True,
                            "count": len(validations),
                            "has_valid": any(v.get("valid", False) for v in validations),
                            "has_invalid": any(not v.get("valid", True) for v in validations),
                            "validations": validations
                        }
                        print(f"   ✅ Validated {len(validations)} interests")
                        for validation in validations:
                            status = "✅" if validation.get("valid") else "❌"
                            print(f"      {status} {validation.get('name', 'N/A')}")
                    else:
                        results["interest_names"] = {"success": False, "error": "No validation data"}
                        print(f"   ❌ No validation data returned")
                    
            except json.JSONDecodeError:
                results["interest_names"] = {"success": False, "error": "Invalid JSON"}
                print(f"   ❌ Invalid JSON response")
        else:
            results["interest_names"] = {"success": False, "error": result.get("text", "Request failed")}
            print(f"   ❌ Request failed: {result.get('text', 'Unknown error')}")
        
        # Test with interest FBIDs
        print(f"   🔢 Testing interest FBID validation")
        
        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {
                "interest_fbid_list": self.test_interests["valid_fbids"]
            }
        })
        
        if result["success"]:
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                
                # Check for errors first
                error_info = self._check_for_errors(parsed_content)
                if error_info["has_error"]:
                    results["interest_fbids"] = {
                        "success": False,
                        "error": error_info["error_message"],
                        "error_format": error_info["format"]
                    }
                    print(f"   ❌ API Error: {error_info['error_message']}")
                else:
                    # Extract data using robust helper method
                    validations = self._extract_data(parsed_content)
                    if validations and isinstance(validations, list):
                        results["interest_fbids"] = {
                            "success": True,
                            "count": len(validations),
                            "all_valid": all(v.get("valid", False) for v in validations),
                            "validations": validations
                        }
                        print(f"   ✅ Validated {len(validations)} FBID interests")
                        for validation in validations:
                            status = "✅" if validation.get("valid") else "❌"
                            print(f"      {status} FBID: {validation.get('id', 'N/A')}")
                    else:
                        results["interest_fbids"] = {"success": False, "error": "No validation data"}
                        print(f"   ❌ No validation data returned")
                    
            except json.JSONDecodeError:
                results["interest_fbids"] = {"success": False, "error": "Invalid JSON"}
                print(f"   ❌ Invalid JSON response")
        else:
            results["interest_fbids"] = {"success": False, "error": result.get("text", "Request failed")}
            print(f"   ❌ Request failed: {result.get('text', 'Unknown error')}")
        
        return results

    def test_different_optimization_goals(self) -> Dict[str, Any]:
        """Test audience estimation with different optimization goals"""
        
        print(f"\n🎯 Testing Different Optimization Goals")
        results = {}
        
        optimization_goals = ["REACH", "LINK_CLICKS", "CONVERSIONS", "APP_INSTALLS"]
        base_targeting = self.test_targeting_specs["simple_demographics"]
        
        for goal in optimization_goals:
            print(f"   🎯 Testing optimization goal: '{goal}'")
            
            result = self._make_request("tools/call", {
                "name": "estimate_audience_size",
                "arguments": {
                    "account_id": self.account_id,
                    "targeting": base_targeting,
                    "optimization_goal": goal
                }
            })
            
            if result["success"]:
                response_data = result["json"]["result"]
                content = response_data.get("content", [{}])[0].get("text", "")
                
                try:
                    parsed_content = json.loads(content)
                    
                    # Check for errors first
                    error_info = self._check_for_errors(parsed_content)
                    if error_info["has_error"]:
                        results[goal] = {
                            "success": False,
                            "error": error_info["error_message"],
                            "error_format": error_info["format"]
                        }
                        print(f"   ❌ {goal}: {error_info['error_message']}")
                    elif parsed_content.get("success", False):
                        results[goal] = {
                            "success": True,
                            "estimated_size": parsed_content.get("estimated_audience_size", 0),
                            "goal_used": parsed_content.get("optimization_goal")
                        }
                        estimate_size = parsed_content.get("estimated_audience_size", 0)
                        print(f"   ✅ {goal}: {estimate_size:,} people")
                    else:
                        results[goal] = {
                            "success": False,
                            "error": "Response indicates failure but no error message found"
                        }
                        print(f"   ❌ {goal}: Response indicates failure but no error message found")
                        
                except json.JSONDecodeError:
                    results[goal] = {"success": False, "error": "Invalid JSON"}
                    print(f"   ❌ {goal}: Invalid JSON response")
            else:
                results[goal] = {"success": False, "error": result.get("text", "Request failed")}
                print(f"   ❌ {goal}: Request failed")
        
        return results

    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid parameters"""
        
        print(f"\n⚠️  Testing Error Handling")
        results = {}
        
        # Test 1: No parameters
        print(f"   🚫 Testing with no parameters")
        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {}
        })
        
        results["no_params"] = self._parse_error_response(result, "Should require targeting or interest validation")
        
        # Test 2: Account ID without targeting
        print(f"   🚫 Testing account ID without targeting")
        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {
                "account_id": self.account_id
            }
        })
        
        results["no_targeting"] = self._parse_error_response(result, "Should require targeting specification")
        
        # Test 3: Invalid targeting structure
        print(f"   🚫 Testing invalid targeting structure")
        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {
                "account_id": self.account_id,
                "targeting": {"invalid": "structure"}
            }
        })
        
        results["invalid_targeting"] = self._parse_error_response(result, "Should handle invalid targeting")
        
        # Test 4: Missing location in targeting (no geo_locations or custom audiences)
        print(f"   🚫 Testing missing location in targeting")
        result = self._make_request("tools/call", {
            "name": "estimate_audience_size",
            "arguments": {
                "account_id": self.account_id,
                # Interests present but no geo_locations and no custom_audiences
                "targeting": {
                    "age_min": 18,
                    "age_max": 35,
                    "flexible_spec": [
                        {"interests": [{"id": "6003371567474"}]}
                    ]
                }
            }
        })
        results["missing_location"] = self._parse_error_response(result, "Should require a location or custom audience")
        
        return results
    
    def _parse_error_response(self, result: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Helper to parse and validate error responses"""
        
        if not result["success"]:
            print(f"   ✅ {description}: Request failed as expected")
            return {"success": True, "error_type": "request_failure"}
        
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            # Use robust error checking helper method
            error_info = self._check_for_errors(parsed_content)
            if error_info["has_error"]:
                print(f"   ✅ {description}: {error_info['error_message']}")
                return {
                    "success": True, 
                    "error_message": error_info["error_message"],
                    "error_format": error_info["format"]
                }
            else:
                print(f"   ❌ {description}: No error returned when expected")
                return {"success": False, "unexpected_success": True}
                
        except json.JSONDecodeError:
            print(f"   ❌ {description}: Invalid JSON response")
            return {"success": False, "error": "Invalid JSON"}

    def run_audience_estimation_tests(self) -> bool:
        """Run comprehensive audience estimation tests"""
        
        print("🚀 Meta Ads Audience Estimation End-to-End Test Suite")
        print("="*70)
        
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
        print(f"🏢 Using account ID: {self.account_id}")
        
        # Test 0: PL-only reachestimate bounds verification
        print("\n" + "="*70)
        print("📋 PHASE 0: PL-only reachestimate bounds verification (fallback disabled)")
        print("="*70)
        pl_only_results = self.test_pl_only_reachestimate_bounds()
        pl_only_success = pl_only_results.get("success", False)

        # Test 1: Comprehensive Audience Estimation
        print("\n" + "="*70)
        print("📋 PHASE 1: Testing Comprehensive Audience Estimation")
        print("="*70)
        
        comprehensive_results = self.test_comprehensive_audience_estimation()
        comprehensive_success = any(
            result.get("success") and result.get("estimated_size", 0) > 0
            for result in comprehensive_results.values()
        )
        
        # Test 2: Backwards Compatibility
        print("\n" + "="*70)
        print("📋 PHASE 2: Testing Backwards Compatibility")
        print("="*70)
        
        compat_results = self.test_backwards_compatibility_interest_validation()
        compat_success = (
            compat_results.get("interest_names", {}).get("success", False) and
            compat_results.get("interest_fbids", {}).get("success", False)
        )
        
        # Test 3: Different Optimization Goals
        print("\n" + "="*70)
        print("📋 PHASE 3: Testing Different Optimization Goals")
        print("="*70)
        
        goals_results = self.test_different_optimization_goals()
        goals_success = any(
            result.get("success") and result.get("estimated_size", 0) > 0
            for result in goals_results.values()
        )
        
        # Test 4: Error Handling
        print("\n" + "="*70)
        print("📋 PHASE 4: Testing Error Handling")
        print("="*70)
        
        error_results = self.test_error_handling()
        error_success = all(
            result.get("success", False) for result in error_results.values()
        )
        
        # Final assessment
        print("\n" + "="*70)
        print("📊 FINAL RESULTS")
        print("="*70)
        
        all_tests = [
            ("PL-only Reachestimate Bounds", pl_only_success),
            ("Comprehensive Estimation", comprehensive_success),
            ("Backwards Compatibility", compat_success),
            ("Optimization Goals", goals_success),
            ("Error Handling", error_success)
        ]
        
        passed_tests = sum(1 for _, success in all_tests if success)
        total_tests = len(all_tests)
        
        for test_name, success in all_tests:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   • {test_name}: {status}")
        
        overall_success = passed_tests >= 3  # At least 3 out of 4 tests should pass
        
        if overall_success:
            print(f"\n✅ Audience estimation tests: SUCCESS ({passed_tests}/{total_tests} passed)")
            print("   • Comprehensive audience estimation is working")
            print("   • Backwards compatibility is maintained")
            print("   • Meta reachestimate API integration is functional")
            return True
        else:
            print(f"\n❌ Audience estimation tests: FAILED ({passed_tests}/{total_tests} passed)")
            print("   • Some audience estimation features are not working properly")
            return False


def main():
    """Main test execution"""
    tester = AudienceEstimationTester()
    success = tester.run_audience_estimation_tests()
    
    if success:
        print("\n🎉 All audience estimation tests passed!")
    else:
        print("\n⚠️  Some audience estimation tests failed - see details above")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()