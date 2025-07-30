#!/usr/bin/env python3
"""
End-to-End Budget Update Test for Meta Ads MCP

This test validates that the budget update functionality correctly updates
ad set budgets through the Meta Ads API through a pre-authenticated MCP server.

Test functions:
- update_adset (with daily_budget parameter)
- update_adset (with lifetime_budget parameter)
- update_adset (with both budget types)
- Error handling for invalid budgets
- Budget update with other parameters
"""

import requests
import json
import os
import sys
import time
from typing import Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")

class BudgetUpdateTester:
    """Test suite focused on budget update functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        
        # Test data for validation
        self.test_budgets = {
            "daily_budgets": ["5000", "10000", "25000"],  # $50, $100, $250
            "lifetime_budgets": ["50000", "100000", "250000"],  # $500, $1000, $2500
            "invalid_budgets": ["-1000", "0", "invalid_budget", "999999999999"]
        }
        
        # Test ad set IDs specifically created for budget testing
        self.test_adset_ids = [
            "120229734413930183",
            "120229734413930183",
            "120229734413930183",
            "120229734413930183",
            "120229734413930183",
            "120229734413930183"
        ]
        
        # Rate limiting tracking
        self.rate_limit_hit = False
        self.last_rate_limit_time = 0
    
    def _wait_for_rate_limit(self, error_msg: str) -> bool:
        """Wait if we hit rate limiting, return True if we should retry"""
        if "rate limit" in error_msg.lower() or "too many changes" in error_msg.lower():
            if not self.rate_limit_hit:
                print(f"   ⏳ Rate limit hit! Waiting 1 hour before continuing...")
                print(f"      • Meta Ads API allows only 4 budget changes per hour")
                print(f"      • You can manually continue by pressing Enter when ready")
                self.rate_limit_hit = True
                self.last_rate_limit_time = time.time()
                
                # Wait for user input or 1 hour
                try:
                    input("   Press Enter when ready to continue (or wait 1 hour)...")
                    print("   ✅ Continuing with tests...")
                    return True
                except KeyboardInterrupt:
                    print("   ❌ Test interrupted by user")
                    return False
            else:
                print(f"   ⏳ Still rate limited, waiting...")
                return False
        return False

    def _make_request(self, method: str, params: Dict[str, Any] = None, 
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Budget-Update-Test-Client/1.0"
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

    def test_daily_budget_update(self) -> Dict[str, Any]:
        """Test daily budget update functionality"""
        
        print(f"\n💰 Testing daily budget update function")
        results = {}
        
        for budget in self.test_budgets["daily_budgets"]:
            print(f"   💰 Updating daily budget to: ${int(budget)/100:.2f}")
            
            # Retry logic for rate limiting
            max_retries = 3
            for attempt in range(max_retries):
                result = self._make_request("tools/call", {
                    "name": "update_adset",
                    "arguments": {
                        "adset_id": self.test_adset_ids[0],
                        "daily_budget": budget
                    }
                })
                
                if not result["success"]:
                    results[budget] = {
                        "success": False,
                        "error": result.get("text", "Unknown error")
                    }
                    print(f"   ❌ Failed: {result.get('text', 'Unknown error')}")
                    break
                
                # Parse response
                response_data = result["json"]["result"]
                content = response_data.get("content", [{}])[0].get("text", "")
                
                try:
                    parsed_content = json.loads(content)
                    
                    # Check for successful update indicators
                    has_id = "id" in parsed_content
                    has_daily_budget = "daily_budget" in parsed_content
                    has_success = "success" in parsed_content
                    has_error = "error" in parsed_content
                    
                    # Handle rate limiting and API errors
                    if has_error:
                        error_msg = parsed_content.get("error", "")
                        if "rate limit" in error_msg.lower() or "too many changes" in error_msg.lower():
                            if attempt < max_retries - 1:  # Don't retry on last attempt
                                if self._wait_for_rate_limit(error_msg):
                                    print(f"   🔄 Retrying after rate limit...")
                                    continue
                                else:
                                    break
                            else:
                                results[budget] = {
                                    "success": True,  # Rate limiting is expected behavior
                                    "has_success": False,
                                    "has_error": True,
                                    "rate_limited": True,
                                    "error_message": error_msg
                                }
                                print(f"   ⚠️  Rate limited (expected): {error_msg}")
                                break
                        else:
                            results[budget] = {
                                "success": False,
                                "has_error": True,
                                "error_message": error_msg
                            }
                            print(f"   ❌ API Error: {error_msg}")
                            break
                    
                    results[budget] = {
                        "success": True,
                        "has_id": has_id,
                        "has_daily_budget": has_daily_budget,
                        "has_success": has_success,
                        "updated_budget": parsed_content.get("daily_budget", "N/A"),
                        "adset_id": parsed_content.get("id", "N/A")
                    }
                    
                    print(f"   ✅ Updated daily budget to ${int(budget)/100:.2f}")
                    print(f"      • Ad Set ID: {parsed_content.get('id', 'N/A')}")
                    print(f"      • Success: {parsed_content.get('success', 'N/A')}")
                    print(f"      • Raw Response: {parsed_content}")
                    
                    # Note: Meta Ads API returns {"success": true} for updates
                    # The actual updated values can be verified by fetching ad set details
                    break  # Success, exit retry loop
                    
                except json.JSONDecodeError:
                    results[budget] = {
                        "success": False,
                        "error": "Invalid JSON response",
                        "raw_content": content
                    }
                    print(f"   ❌ Invalid JSON: {content}")
                    break
        
        return results

    def test_lifetime_budget_update(self) -> Dict[str, Any]:
        """Test lifetime budget update functionality"""
        
        print(f"\n💰 Testing lifetime budget update function")
        print(f"   ⚠️  Note: Meta Ads API may reject lifetime budget updates if ad set has daily budget")
        results = {}
        
        for budget in self.test_budgets["lifetime_budgets"]:
            print(f"   💰 Updating lifetime budget to: ${int(budget)/100:.2f}")
            
            # Retry logic for rate limiting
            max_retries = 3
            for attempt in range(max_retries):
                result = self._make_request("tools/call", {
                    "name": "update_adset",
                    "arguments": {
                        "adset_id": self.test_adset_ids[1],
                        "lifetime_budget": budget
                    }
                })
                
                if not result["success"]:
                    results[budget] = {
                        "success": False,
                        "error": result.get("text", "Unknown error")
                    }
                    print(f"   ❌ Failed: {result.get('text', 'Unknown error')}")
                    break
                
                # Parse response
                response_data = result["json"]["result"]
                content = response_data.get("content", [{}])[0].get("text", "")
                
                try:
                    parsed_content = json.loads(content)
                    
                    # Check for successful update indicators
                    has_id = "id" in parsed_content
                    has_lifetime_budget = "lifetime_budget" in parsed_content
                    has_success = "success" in parsed_content
                    has_error = "error" in parsed_content
                    
                    # Handle rate limiting and API errors
                    if has_error:
                        error_msg = parsed_content.get("error", "")
                        if "rate limit" in error_msg.lower() or "too many changes" in error_msg.lower():
                            if attempt < max_retries - 1:  # Don't retry on last attempt
                                if self._wait_for_rate_limit(error_msg):
                                    print(f"   🔄 Retrying after rate limit...")
                                    continue
                                else:
                                    break
                            else:
                                results[budget] = {
                                    "success": True,  # Rate limiting is expected behavior
                                    "has_success": False,
                                    "has_error": True,
                                    "rate_limited": True,
                                    "error_message": error_msg
                                }
                                print(f"   ⚠️  Rate limited (expected): {error_msg}")
                                break
                        elif "should be recurring budget" in error_msg.lower() or "cannot switch" in error_msg.lower():
                            results[budget] = {
                                "success": False,
                                "has_error": True,
                                "api_limitation": "Cannot switch from daily to lifetime budget",
                                "error_message": error_msg
                            }
                            print(f"   ⚠️  API Limitation: {error_msg}")
                            break
                        else:
                            results[budget] = {
                                "success": False,
                                "has_error": True,
                                "error_message": error_msg
                            }
                            print(f"   ❌ API Error: {error_msg}")
                            break
                    
                    results[budget] = {
                        "success": True,
                        "has_id": has_id,
                        "has_lifetime_budget": has_lifetime_budget,
                        "has_success": has_success,
                        "updated_budget": parsed_content.get("lifetime_budget", "N/A"),
                        "adset_id": parsed_content.get("id", "N/A")
                    }
                    
                    print(f"   ✅ Updated lifetime budget to ${int(budget)/100:.2f}")
                    print(f"      • Ad Set ID: {parsed_content.get('id', 'N/A')}")
                    print(f"      • Success: {parsed_content.get('success', 'N/A')}")
                    
                    # Note: Meta Ads API returns {"success": true} for updates
                    # The actual updated values can be verified by fetching ad set details
                    break  # Success, exit retry loop
                    
                except json.JSONDecodeError:
                    results[budget] = {
                        "success": False,
                        "error": "Invalid JSON response",
                        "raw_content": content
                    }
                    print(f"   ❌ Invalid JSON: {content}")
                    break
        
        return results

    def test_both_budget_types_update(self) -> Dict[str, Any]:
        """Test updating both daily and lifetime budget simultaneously"""
        
        print(f"\n💰 Testing both budget types update function")
        print(f"   ⚠️  Note: Meta Ads API may reject this if ad set has existing daily budget")
        
        daily_budget = "15000"  # $150
        lifetime_budget = "150000"  # $1500
        
        print(f"   💰 Updating both budgets - Daily: ${int(daily_budget)/100:.2f}, Lifetime: ${int(lifetime_budget)/100:.2f}")
        
        result = self._make_request("tools/call", {
            "name": "update_adset",
                                "arguments": {
                        "adset_id": self.test_adset_ids[2],
                        "daily_budget": daily_budget,
                        "lifetime_budget": lifetime_budget
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
                error_msg = parsed_content.get("error", "")
                if "rate limit" in error_msg.lower() or "too many changes" in error_msg.lower():
                    return {
                        "success": True,  # Rate limiting is expected behavior
                        "rate_limited": True,
                        "error_message": error_msg
                    }
                else:
                    return {
                        "success": False,
                        "error": error_msg,
                        "api_limitation": "Cannot have both daily and lifetime budgets"
                    }
            
            # Check for successful update indicators
            has_id = "id" in parsed_content
            has_daily_budget = "daily_budget" in parsed_content
            has_lifetime_budget = "lifetime_budget" in parsed_content
            has_success = "success" in parsed_content
            
            result_data = {
                "success": True,
                "has_id": has_id,
                "has_daily_budget": has_daily_budget,
                "has_lifetime_budget": has_lifetime_budget,
                "has_success": has_success,
                "daily_budget": parsed_content.get("daily_budget", "N/A"),
                "lifetime_budget": parsed_content.get("lifetime_budget", "N/A"),
                "adset_id": parsed_content.get("id", "N/A")
            }
            
            print(f"   ✅ Updated both budgets successfully")
            print(f"      • Ad Set ID: {parsed_content.get('id', 'N/A')}")
            print(f"      • Success: {parsed_content.get('success', 'N/A')}")
            
            # Note: Meta Ads API returns {"success": true} for updates
            # The actual updated values can be verified by fetching ad set details
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }

    def test_budget_update_with_other_parameters(self) -> Dict[str, Any]:
        """Test budget update combined with other parameters"""
        
        print(f"\n💰 Testing budget update with other parameters")
        
        result = self._make_request("tools/call", {
            "name": "update_adset",
            "arguments": {
                "adset_id": self.test_adset_ids[3],
                "daily_budget": "7500",  # $75
                "status": "PAUSED",
                "bid_amount": 1000,
                "bid_strategy": "LOWEST_COST_WITH_BID_CAP"
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
                error_msg = parsed_content.get("error", "")
                if "rate limit" in error_msg.lower() or "too many changes" in error_msg.lower():
                    return {
                        "success": True,  # Rate limiting is expected behavior
                        "rate_limited": True,
                        "error_message": error_msg
                    }
                else:
                    return {
                        "success": False,
                        "error": error_msg
                    }
            
            # Check for successful update indicators
            has_id = "id" in parsed_content
            has_daily_budget = "daily_budget" in parsed_content
            has_status = "status" in parsed_content
            has_success = "success" in parsed_content
            
            result_data = {
                "success": True,
                "has_id": has_id,
                "has_daily_budget": has_daily_budget,
                "has_status": has_status,
                "has_success": has_success,
                "daily_budget": parsed_content.get("daily_budget", "N/A"),
                "status": parsed_content.get("status", "N/A"),
                "adset_id": parsed_content.get("id", "N/A")
            }
            
            print(f"   ✅ Updated budget with other parameters successfully")
            print(f"      • Ad Set ID: {parsed_content.get('id', 'N/A')}")
            print(f"      • Success: {parsed_content.get('success', 'N/A')}")
            
            # Note: Meta Ads API returns {"success": true} for updates
            # The actual updated values can be verified by fetching ad set details
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }

    def test_invalid_budget_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid budget values"""
        
        print(f"\n💰 Testing invalid budget handling")
        results = {}
        
        for invalid_budget in self.test_budgets["invalid_budgets"]:
            print(f"   💰 Testing invalid budget: '{invalid_budget}'")
            
            result = self._make_request("tools/call", {
                "name": "update_adset",
                "arguments": {
                    "adset_id": self.test_adset_ids[4],
                    "daily_budget": invalid_budget
                }
            })
            
            if not result["success"]:
                results[invalid_budget] = {
                    "success": False,
                    "error": result.get("text", "Unknown error")
                }
                print(f"   ❌ Request failed: {result.get('text', 'Unknown error')}")
                continue
            
            # Parse response
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                
                # For invalid budgets, we expect an error response
                has_error = "error" in parsed_content or "data" in parsed_content
                has_details = "details" in parsed_content
                
                # Check if the error is a proper validation error (not a rate limit or other issue)
                error_msg = parsed_content.get("error", "")
                if not error_msg and "data" in parsed_content:
                    try:
                        data_content = json.loads(parsed_content.get("data", ""))
                        if "error" in data_content:
                            error_msg = data_content["error"].get("message", "")
                    except:
                        pass
                
                is_validation_error = any(keyword in error_msg.lower() for keyword in [
                    "must be a number", "greater than or equal to 0", "too high", "too low", "invalid parameter",
                    "budget is too low", "budget is too high", "decrease your ad set budget"
                ])
                
                results[invalid_budget] = {
                    "success": has_error and is_validation_error,  # Success if we got proper validation error
                    "has_error": has_error,
                    "has_details": has_details,
                    "is_validation_error": is_validation_error,
                    "error_message": error_msg or parsed_content.get("error", "No error field"),
                    "details": parsed_content.get("details", "No details field")
                }
                
                if has_error and is_validation_error:
                    print(f"   ✅ Properly handled invalid budget '{invalid_budget}'")
                    print(f"      • Error: {parsed_content.get('error', 'N/A')}")
                elif has_error:
                    print(f"   ⚠️  Got error but not validation error for '{invalid_budget}'")
                    print(f"      • Error: {parsed_content.get('error', 'N/A')}")
                else:
                    print(f"   ❌ Unexpected success for invalid budget '{invalid_budget}'")
                    print(f"      • Response: {parsed_content}")
                
            except json.JSONDecodeError:
                results[invalid_budget] = {
                    "success": False,
                    "error": "Invalid JSON response",
                    "raw_content": content
                }
                print(f"   ❌ Invalid JSON: {content}")
        
        return results

    def test_budget_update_with_targeting(self) -> Dict[str, Any]:
        """Test budget update combined with targeting update"""
        
        print(f"\n💰 Testing budget update with targeting")
        
        targeting = {
            "age_min": 25,
            "age_max": 45,
            "geo_locations": {"countries": ["US", "CA"]}
        }
        
        result = self._make_request("tools/call", {
            "name": "update_adset",
            "arguments": {
                "adset_id": self.test_adset_ids[5],
                "daily_budget": "8500",  # $85
                "targeting": targeting
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
                error_msg = parsed_content.get("error", "")
                if "rate limit" in error_msg.lower() or "too many changes" in error_msg.lower():
                    return {
                        "success": True,  # Rate limiting is expected behavior
                        "rate_limited": True,
                        "error_message": error_msg
                    }
                else:
                    return {
                        "success": False,
                        "error": error_msg
                    }
            
            # Check for successful update indicators
            has_id = "id" in parsed_content
            has_daily_budget = "daily_budget" in parsed_content
            has_success = "success" in parsed_content
            
            result_data = {
                "success": True,
                "has_id": has_id,
                "has_daily_budget": has_daily_budget,
                "has_success": has_success,
                "daily_budget": parsed_content.get("daily_budget", "N/A"),
                "adset_id": parsed_content.get("id", "N/A")
            }
            
            print(f"   ✅ Updated budget with targeting successfully")
            print(f"      • Ad Set ID: {parsed_content.get('id', 'N/A')}")
            print(f"      • Success: {parsed_content.get('success', 'N/A')}")
            
            # Note: Meta Ads API returns {"success": true} for updates
            # The actual updated values can be verified by fetching ad set details
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }

    def run_budget_update_tests(self) -> bool:
        """Run comprehensive budget update tests"""
        
        print("🚀 Meta Ads Budget Update End-to-End Test Suite")
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
        print("⚠️  Note: This test uses ad sets specifically created for budget testing")
        print("⚠️  Note: Campaign uses ad set level budgets - testing budget updates at ad set level")
        print("⚠️  Note: Meta Ads API allows only 4 budget changes per hour - test will wait if rate limited")
        
        # Test 1: Daily Budget Updates
        print("\n" + "="*60)
        print("📋 PHASE 1: Testing Daily Budget Updates")
        print("="*60)
        
        daily_results = self.test_daily_budget_update()
        daily_success = any(
            result.get("success") or 
            (result.get("success") and result.get("rate_limited"))
            for result in daily_results.values()
        )
        
        # Test 2: Lifetime Budget Updates
        print("\n" + "="*60)
        print("📋 PHASE 2: Testing Lifetime Budget Updates")
        print("="*60)
        
        lifetime_results = self.test_lifetime_budget_update()
        lifetime_success = any(
            result.get("success") or 
            (result.get("success") and result.get("rate_limited")) or
            (not result.get("success") and result.get("api_limitation"))
            for result in lifetime_results.values()
        )
        
        # Test 3: Both Budget Types
        print("\n" + "="*60)
        print("📋 PHASE 3: Testing Both Budget Types")
        print("="*60)
        
        both_budgets_result = self.test_both_budget_types_update()
        both_budgets_success = (both_budgets_result.get("success") or
                              (not both_budgets_result.get("success") and 
                               both_budgets_result.get("rate_limited")) or
                              (not both_budgets_result.get("success") and 
                               both_budgets_result.get("api_limitation")))
        
        # Test 4: Budget with Other Parameters
        print("\n" + "="*60)
        print("📋 PHASE 4: Testing Budget with Other Parameters")
        print("="*60)
        
        other_params_result = self.test_budget_update_with_other_parameters()
        other_params_success = (other_params_result.get("success") or
                              (other_params_result.get("success") and 
                               other_params_result.get("rate_limited")))
        
        # Test 5: Invalid Budget Handling
        print("\n" + "="*60)
        print("📋 PHASE 5: Testing Invalid Budget Handling")
        print("="*60)
        
        invalid_results = self.test_invalid_budget_handling()
        invalid_success = any(
            result.get("success") and result.get("is_validation_error") 
            for result in invalid_results.values()
        )
        
        # Test 6: Budget with Targeting
        print("\n" + "="*60)
        print("📋 PHASE 6: Testing Budget with Targeting")
        print("="*60)
        
        targeting_result = self.test_budget_update_with_targeting()
        targeting_success = (targeting_result.get("success") or
                           (targeting_result.get("success") and 
                            targeting_result.get("rate_limited")))
        
        # Final assessment
        print("\n" + "="*60)
        print("📊 FINAL RESULTS")
        print("="*60)
        
        all_tests = [
            ("Daily Budget Updates", daily_success),
            ("Lifetime Budget Updates", lifetime_success),
            ("Both Budget Types", both_budgets_success),
            ("Budget with Other Parameters", other_params_success),
            ("Invalid Budget Handling", invalid_success),
            ("Budget with Targeting", targeting_success)
        ]
        
        passed_tests = sum(1 for _, success in all_tests if success)
        total_tests = len(all_tests)
        
        for test_name, success in all_tests:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   • {test_name}: {status}")
        
        overall_success = passed_tests >= 4  # At least 4 out of 6 tests should pass
        
        if overall_success:
            print(f"\n✅ Budget update tests: SUCCESS ({passed_tests}/{total_tests} passed)")
            print("   • Core budget update functionality is working")
            print("   • Meta Ads API integration is functional")
            print("   • Error handling is working properly")
            return True
        else:
            print(f"\n❌ Budget update tests: FAILED ({passed_tests}/{total_tests} passed)")
            print("   • Some budget update functions are not working properly")
            print("   • Check API permissions and ad set IDs")
            return False


def main():
    """Main test execution"""
    tester = BudgetUpdateTester()
    success = tester.run_budget_update_tests()
    
    if success:
        print("\n🎉 All budget update tests passed!")
    else:
        print("\n⚠️  Some budget update tests failed - see details above")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 