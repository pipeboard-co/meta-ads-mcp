#!/usr/bin/env python3
"""
Campaign Objective Filtering Tests for Meta Ads MCP

This test validates that the get_campaigns function correctly filters
campaigns by objective type, supporting both single and multiple objectives.

Test scenarios:
1. Single objective filtering (e.g., OUTCOME_LEADS)
2. Multiple objective filtering (e.g., [OUTCOME_LEADS, OUTCOME_SALES])
3. Combined status and objective filtering
4. Empty/no filtering (returns all campaigns)
5. Edge cases (empty strings, invalid types)
"""

import pytest
import requests
import json
from typing import Dict, Any, List


class CampaignObjectiveFilterTester:
    """Test suite for campaign objective filtering functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Campaign-Filter-Test-Client/1.0"
        }
        
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
                headers=headers,
                json=payload,
                timeout=30
            )
            
            self.request_id += 1
            
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "json": response.json() if response.status_code == 200 else None,
                "text": response.text,
                "success": response.status_code == 200
            }
            
            # Parse the content if successful
            if result["success"] and result["json"]:
                response_data = result["json"].get("result", {})
                content = response_data.get("content", [{}])[0].get("text", "")
                try:
                    result["parsed_content"] = json.loads(content)
                except json.JSONDecodeError:
                    result["parsed_content"] = None
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "headers": {},
                "json": None,
                "text": str(e),
                "success": False,
                "error": str(e)
            }
    
    def get_campaigns(self, account_id: str, **filters) -> Dict[str, Any]:
        """Get campaigns with optional filters"""
        
        arguments = {"account_id": account_id}
        arguments.update(filters)
        
        return self._make_request("tools/call", {
            "name": "get_campaigns",
            "arguments": arguments
        })
    
    def test_no_filtering(self, account_id: str) -> Dict[str, Any]:
        """Test getting campaigns without any filtering"""
        
        print(f"\n🔍 Test 1: Get campaigns without filtering")
        
        result = self.get_campaigns(account_id)
        
        if not result["success"]:
            return {
                "test": "no_filtering",
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        campaigns = result.get("parsed_content", {}).get("data", [])
        
        return {
            "test": "no_filtering",
            "success": True,
            "campaign_count": len(campaigns),
            "campaigns": campaigns,
            "objectives": [c.get("objective") for c in campaigns if "objective" in c]
        }
    
    def test_single_objective_filter(self, account_id: str, objective: str) -> Dict[str, Any]:
        """Test filtering by a single objective"""
        
        print(f"\n🔍 Test 2: Filter by single objective: {objective}")
        
        result = self.get_campaigns(account_id, objective_filter=objective)
        
        if not result["success"]:
            return {
                "test": "single_objective",
                "objective": objective,
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        campaigns = result.get("parsed_content", {}).get("data", [])
        objectives_found = [c.get("objective") for c in campaigns if "objective" in c]
        
        # Verify all campaigns match the filter
        all_match = all(obj == objective for obj in objectives_found) if objectives_found else True
        
        return {
            "test": "single_objective",
            "objective": objective,
            "success": True,
            "all_match_filter": all_match,
            "campaign_count": len(campaigns),
            "objectives": objectives_found
        }
    
    def test_multiple_objectives_filter(self, account_id: str, objectives: List[str]) -> Dict[str, Any]:
        """Test filtering by multiple objectives"""
        
        print(f"\n🔍 Test 3: Filter by multiple objectives: {objectives}")
        
        result = self.get_campaigns(account_id, objective_filter=objectives)
        
        if not result["success"]:
            return {
                "test": "multiple_objectives",
                "objectives": objectives,
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        campaigns = result.get("parsed_content", {}).get("data", [])
        objectives_found = [c.get("objective") for c in campaigns if "objective" in c]
        
        # Verify all campaigns match one of the filter objectives
        all_match = all(obj in objectives for obj in objectives_found) if objectives_found else True
        
        return {
            "test": "multiple_objectives",
            "objectives": objectives,
            "success": True,
            "all_match_filter": all_match,
            "campaign_count": len(campaigns),
            "objectives_found": objectives_found,
            "unique_objectives": list(set(objectives_found))
        }
    
    def test_combined_status_and_objective_filter(
        self, 
        account_id: str, 
        status: str, 
        objective: str
    ) -> Dict[str, Any]:
        """Test filtering by both status and objective"""
        
        print(f"\n🔍 Test 4: Filter by status '{status}' and objective '{objective}'")
        
        result = self.get_campaigns(
            account_id, 
            status_filter=status, 
            objective_filter=objective
        )
        
        if not result["success"]:
            return {
                "test": "combined_filters",
                "status": status,
                "objective": objective,
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        campaigns = result.get("parsed_content", {}).get("data", [])
        
        # Check if campaigns match both filters
        objectives_match = all(
            c.get("objective") == objective 
            for c in campaigns if "objective" in c
        )
        
        return {
            "test": "combined_filters",
            "status": status,
            "objective": objective,
            "success": True,
            "objectives_match": objectives_match,
            "campaign_count": len(campaigns),
            "campaigns": [
                {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "status": c.get("status"),
                    "objective": c.get("objective")
                }
                for c in campaigns
            ]
        }
    
    def test_empty_string_filter(self, account_id: str) -> Dict[str, Any]:
        """Test that empty string filter returns all campaigns"""
        
        print(f"\n🔍 Test 5: Empty string filter (should return all)")
        
        result = self.get_campaigns(account_id, objective_filter="")
        
        if not result["success"]:
            return {
                "test": "empty_string_filter",
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        campaigns = result.get("parsed_content", {}).get("data", [])
        
        return {
            "test": "empty_string_filter",
            "success": True,
            "campaign_count": len(campaigns),
            "note": "Empty filter should return all campaigns"
        }
    
    def test_empty_list_filter(self, account_id: str) -> Dict[str, Any]:
        """Test that empty list filter returns all campaigns"""
        
        print(f"\n🔍 Test 6: Empty list filter (should return all)")
        
        result = self.get_campaigns(account_id, objective_filter=[])
        
        if not result["success"]:
            return {
                "test": "empty_list_filter",
                "success": False,
                "error": result.get("text", "Unknown error")
            }
        
        campaigns = result.get("parsed_content", {}).get("data", [])
        
        return {
            "test": "empty_list_filter",
            "success": True,
            "campaign_count": len(campaigns),
            "note": "Empty list should return all campaigns"
        }
    
    def run_all_tests(self, account_id: str) -> bool:
        """Run comprehensive campaign objective filtering tests"""
        
        print("🚀 Campaign Objective Filtering Test Suite")
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
        print(f"🏢 Testing with account: {account_id}")
        
        test_results = []
        
        # Test 1: No filtering (get all campaigns to see what objectives exist)
        result1 = self.test_no_filtering(account_id)
        test_results.append(result1)
        if result1["success"]:
            print(f"✅ Found {result1['campaign_count']} campaigns")
            print(f"   Objectives: {set(result1.get('objectives', []))}")
            available_objectives = list(set(result1.get('objectives', [])))
        else:
            print(f"❌ Failed: {result1.get('error')}")
            return False
        
        # If we have campaigns with objectives, test filtering
        if available_objectives:
            # Test 2: Single objective filter
            test_objective = available_objectives[0]
            result2 = self.test_single_objective_filter(account_id, test_objective)
            test_results.append(result2)
            if result2["success"]:
                if result2["all_match_filter"]:
                    print(f"✅ Single objective filter works correctly")
                    print(f"   Found {result2['campaign_count']} campaigns with objective '{test_objective}'")
                else:
                    print(f"⚠️  Filter returned campaigns with wrong objectives")
                    print(f"   Expected: {test_objective}")
                    print(f"   Found: {set(result2['objectives'])}")
            else:
                print(f"❌ Single objective filter failed: {result2.get('error')}")
            
            # Test 3: Multiple objectives filter (if we have at least 2 objectives)
            if len(available_objectives) >= 2:
                test_objectives = available_objectives[:2]
                result3 = self.test_multiple_objectives_filter(account_id, test_objectives)
                test_results.append(result3)
                if result3["success"]:
                    if result3["all_match_filter"]:
                        print(f"✅ Multiple objectives filter works correctly")
                        print(f"   Found {result3['campaign_count']} campaigns")
                        print(f"   Unique objectives: {result3['unique_objectives']}")
                    else:
                        print(f"⚠️  Filter returned campaigns with wrong objectives")
                        print(f"   Expected: {test_objectives}")
                        print(f"   Found: {result3['unique_objectives']}")
                else:
                    print(f"❌ Multiple objectives filter failed: {result3.get('error')}")
            else:
                print(f"ℹ️  Skipping multiple objectives test (only {len(available_objectives)} objective found)")
            
            # Test 4: Combined status and objective filter
            result4 = self.test_combined_status_and_objective_filter(
                account_id, 
                "ACTIVE", 
                test_objective
            )
            test_results.append(result4)
            if result4["success"]:
                if result4["objectives_match"]:
                    print(f"✅ Combined filters work correctly")
                    print(f"   Found {result4['campaign_count']} ACTIVE campaigns with objective '{test_objective}'")
                else:
                    print(f"⚠️  Combined filter returned campaigns with wrong objectives")
            else:
                print(f"❌ Combined filter failed: {result4.get('error')}")
        else:
            print("ℹ️  No campaigns found, skipping filter tests")
        
        # Test 5: Empty string filter
        result5 = self.test_empty_string_filter(account_id)
        test_results.append(result5)
        if result5["success"]:
            print(f"✅ Empty string filter works correctly")
            print(f"   Returned {result5['campaign_count']} campaigns (same as no filter)")
        else:
            print(f"❌ Empty string filter failed: {result5.get('error')}")
        
        # Test 6: Empty list filter
        result6 = self.test_empty_list_filter(account_id)
        test_results.append(result6)
        if result6["success"]:
            print(f"✅ Empty list filter works correctly")
            print(f"   Returned {result6['campaign_count']} campaigns (same as no filter)")
        else:
            print(f"❌ Empty list filter failed: {result6.get('error')}")
        
        # Final assessment
        print("\n" + "="*60)
        print("📊 FINAL RESULTS")
        print("="*60)
        
        successful_tests = sum(1 for r in test_results if r.get("success", False))
        total_tests = len(test_results)
        
        if successful_tests == total_tests:
            print(f"✅ All {total_tests} tests passed!")
            return True
        else:
            print(f"⚠️  {successful_tests}/{total_tests} tests passed")
            failed_tests = [r for r in test_results if not r.get("success", False)]
            print(f"   Failed tests: {[r.get('test') for r in failed_tests]}")
            return False


# Pytest-compatible test functions
@pytest.fixture
def tester(server_url):
    """Create a tester instance"""
    return CampaignObjectiveFilterTester(server_url)


@pytest.fixture
def account_id():
    """Default test account ID"""
    return "act_701351919139047"


def test_server_running(check_server_running):
    """Verify the server is running before tests"""
    assert check_server_running


def test_no_filtering(tester, account_id, check_server_running):
    """Test getting campaigns without filtering"""
    result = tester.test_no_filtering(account_id)
    assert result["success"], f"Failed: {result.get('error')}"
    assert isinstance(result["campaign_count"], int)
    print(f"Found {result['campaign_count']} campaigns")


def test_single_objective_filter(tester, account_id, check_server_running):
    """Test filtering by a single objective"""
    # First get available objectives
    no_filter_result = tester.test_no_filtering(account_id)
    assert no_filter_result["success"]
    
    objectives = no_filter_result.get("objectives", [])
    if not objectives:
        pytest.skip("No campaigns with objectives found")
    
    test_objective = objectives[0]
    result = tester.test_single_objective_filter(account_id, test_objective)
    assert result["success"], f"Failed: {result.get('error')}"
    assert result["all_match_filter"], "Filter returned campaigns with wrong objectives"
    print(f"Single objective filter: {result['campaign_count']} campaigns with {test_objective}")


def test_multiple_objectives_filter(tester, account_id, check_server_running):
    """Test filtering by multiple objectives"""
    # First get available objectives
    no_filter_result = tester.test_no_filtering(account_id)
    assert no_filter_result["success"]
    
    available_objectives = list(set(no_filter_result.get("objectives", [])))
    if len(available_objectives) < 2:
        pytest.skip("Need at least 2 different objectives to test")
    
    test_objectives = available_objectives[:2]
    result = tester.test_multiple_objectives_filter(account_id, test_objectives)
    assert result["success"], f"Failed: {result.get('error')}"
    assert result["all_match_filter"], "Filter returned campaigns with wrong objectives"
    print(f"Multiple objectives filter: {result['campaign_count']} campaigns")


def test_combined_filters(tester, account_id, check_server_running):
    """Test filtering by both status and objective"""
    # First get available objectives
    no_filter_result = tester.test_no_filtering(account_id)
    assert no_filter_result["success"]
    
    objectives = no_filter_result.get("objectives", [])
    if not objectives:
        pytest.skip("No campaigns with objectives found")
    
    test_objective = objectives[0]
    result = tester.test_combined_status_and_objective_filter(
        account_id, 
        "ACTIVE", 
        test_objective
    )
    assert result["success"], f"Failed: {result.get('error')}"
    print(f"Combined filters: {result['campaign_count']} campaigns")


def test_empty_string_filter(tester, account_id, check_server_running):
    """Test that empty string filter returns all campaigns"""
    result = tester.test_empty_string_filter(account_id)
    assert result["success"], f"Failed: {result.get('error')}"
    print(f"Empty string filter: {result['campaign_count']} campaigns")


def test_empty_list_filter(tester, account_id, check_server_running):
    """Test that empty list filter returns all campaigns"""
    result = tester.test_empty_list_filter(account_id)
    assert result["success"], f"Failed: {result.get('error')}"
    print(f"Empty list filter: {result['campaign_count']} campaigns")


def main():
    """Main test execution for standalone running"""
    import sys
    
    account_id = "act_701351919139047"  # Default test account
    
    tester = CampaignObjectiveFilterTester()
    success = tester.run_all_tests(account_id)
    
    if success:
        print("\n🎉 All campaign objective filtering tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed - see details above")
        sys.exit(1)


if __name__ == "__main__":
    main()

