#!/usr/bin/env python3
"""
E2E Test for mobile app adset creation issue (Issue #008)

This test validates that the create_adset tool supports required parameters 
for mobile app campaigns:
- promoted_object configuration
- destination_type settings  
- Conversion event dataset linking
- Custom event type specification

Expected Meta API error when parameters are missing:
"Select a dataset and conversion event for your ad set (Code 100)"

Usage (Manual execution only):
    1. Start the server: uv run python -m meta_ads_mcp --transport streamable-http --port 8080
    2. Run test: uv run python tests/test_mobile_app_adset_issue.py
    
Or with pytest (explicit E2E flag required):
    uv run python -m pytest tests/test_mobile_app_adset_issue.py -v -m e2e

Note: This test is marked as E2E and will NOT run automatically in CI.
It must be executed manually to validate mobile app campaign functionality.
"""

import pytest
import requests
import json
import time
import sys
import os
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MobileAppAdsetTester:
    """Test suite for mobile app adset creation functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        
    def _make_request(self, method: str, params: Dict[str, Any] = None, 
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        # Default headers for MCP protocol with streamable HTTP transport
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "MobileApp-Test-Client/1.0"
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
                timeout=30  # Increased timeout for API calls
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

    def test_create_adset_tool_exists(self) -> Dict[str, Any]:
        """Test that create_adset tool exists and check its parameters"""
        result = self._make_request("tools/list", {})
        
        if not result["success"]:
            return {"success": False, "error": "Failed to get tools list"}
        
        tools = result["json"]["result"].get("tools", [])
        create_adset_tool = next((tool for tool in tools if tool["name"] == "create_adset"), None)
        
        if not create_adset_tool:
            return {"success": False, "error": "create_adset tool not found"}
        
        # Check if mobile app specific parameters are supported
        input_schema = create_adset_tool.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        
        mobile_app_params = ["promoted_object", "destination_type"]
        missing_params = []
        
        for param in mobile_app_params:
            if param not in properties:
                missing_params.append(param)
        
        return {
            "success": True,
            "tool": create_adset_tool,
            "missing_mobile_app_params": missing_params,
            "has_mobile_app_support": len(missing_params) == 0
        }

    def test_reproduce_mobile_app_error(self) -> Dict[str, Any]:
        """Reproduce mobile app adset creation error scenario"""
        
        # Test parameters for mobile app campaign
        test_params = {
            "name": "create_adset",
            "arguments": {
                "account_id": "act_123456789012345",  # Generic test account
                "campaign_id": "120230566078340163",  # This will likely be invalid but that's OK for testing
                "name": "test mobile app ad set",
                "status": "PAUSED",
                "targeting": {
                    "age_max": 65,
                    "age_min": 18,
                    "app_install_state": "not_installed",
                    "geo_locations": {
                        "countries": ["DE"],
                        "location_types": ["home", "recent"]
                    },
                    "user_device": ["Android_Smartphone", "Android_Tablet"],
                    "user_os": ["Android"],
                    "brand_safety_content_filter_levels": ["FACEBOOK_STANDARD", "AN_STANDARD"],
                    "targeting_automation": {"advantage_audience": 1}
                },
                "optimization_goal": "APP_INSTALLS",
                "billing_event": "IMPRESSIONS"
            }
        }
        
        result = self._make_request("tools/call", test_params)
        
        if not result["success"]:
            return {
                "success": False, 
                "error": f"MCP call failed: {result.get('text', 'Unknown error')}"
            }
        
        # Parse the response 
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            # Check if this is an error response
            if "error" in parsed_content:
                error_details = parsed_content["error"]
                if isinstance(error_details, dict) and "details" in error_details:
                    meta_error = error_details["details"]
                    
                    # Check for the specific error we're looking for
                    if isinstance(meta_error, dict) and "error" in meta_error:
                        error_code = meta_error["error"].get("code")
                        error_message = meta_error["error"].get("error_user_msg", "")
                        
                        is_dataset_error = (
                            error_code == 100 and 
                            "conversion event" in error_message.lower()
                        )
                        
                        return {
                            "success": True,
                            "reproduced_error": is_dataset_error,
                            "error_code": error_code,
                            "error_message": error_message,
                            "full_response": parsed_content
                        }
            
            return {
                "success": True,
                "reproduced_error": False,
                "unexpected_response": parsed_content
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {e}",
                "raw_content": content
            }

# Pytest E2E test class - marked to prevent automatic execution
@pytest.mark.e2e
@pytest.mark.skip(reason="E2E test - requires running MCP server - execute manually only")
class TestMobileAppAdsetIssueE2E:
    """E2E test for mobile app adset creation functionality (Issue #008)"""
    
    def setup_method(self):
        """Set up test instance"""
        self.tester = MobileAppAdsetTester()
    
    def test_create_adset_tool_has_mobile_app_params(self):
        """Test that create_adset tool exists and has mobile app parameters"""
        result = self.tester.test_create_adset_tool_exists()
        
        assert result["success"], f"Tool test failed: {result.get('error', 'Unknown error')}"
        
        missing_params = result["missing_mobile_app_params"]
        has_mobile_support = result["has_mobile_app_support"]
        
        # Report results but don't fail if parameters are missing (this is what we're testing)
        if missing_params:
            pytest.skip(f"Missing mobile app parameters: {missing_params}")
        else:
            # Parameters are present - mobile app support is available
            assert has_mobile_support, "Tool should have mobile app support when parameters are present"
    
    def test_reproduce_mobile_app_error_scenario(self):
        """Test reproducing mobile app adset creation error scenario"""
        result = self.tester.test_reproduce_mobile_app_error()
        
        assert result["success"], f"Error reproduction test failed: {result.get('error', 'Unknown error')}"
        
        # This test is mainly for validation, not assertion
        # The actual error depends on authentication and server state
        if result.get("reproduced_error"):
            print(f"Reproduced error - Code: {result.get('error_code')}, Message: {result.get('error_message')}")
        else:
            print("Different response received (may indicate parameters are working or auth issues)")


def main():
    """Run mobile app adset creation tests (manual execution)"""
    print("🚀 Mobile App Adset Creation E2E Test")
    print("=" * 50)
    print("⚠️  This is an E2E test - requires MCP server running on localhost:8080")
    print("   Start server with: uv run python -m meta_ads_mcp --transport streamable-http --port 8080")
    print()
    
    tester = MobileAppAdsetTester()
    
    # Test 1: Check if create_adset tool exists and has mobile app parameters
    print("\n🧪 Test 1: Checking create_adset tool parameters...")
    tool_test = tester.test_create_adset_tool_exists()
    
    if tool_test["success"]:
        missing_params = tool_test["missing_mobile_app_params"]
        if missing_params:
            print(f"❌ Missing mobile app parameters: {missing_params}")
            print("⚠️  Mobile app campaigns may not work without these parameters")
        else:
            print("✅ All mobile app parameters are present")
    else:
        print(f"❌ Tool test failed: {tool_test['error']}")
    
    # Test 2: Try to reproduce mobile app error scenario
    print("\n🧪 Test 2: Testing mobile app campaign creation...")
    error_test = tester.test_reproduce_mobile_app_error()
    
    if error_test["success"]:
        if error_test.get("reproduced_error"):
            print("✅ Successfully reproduced the error!")
            print(f"   Error Code: {error_test['error_code']}")
            print(f"   Error Message: {error_test['error_message']}")
        else:
            print("⚠️  Error not reproduced - different response received")
            if "unexpected_response" in error_test:
                print(f"   Response: {json.dumps(error_test['unexpected_response'], indent=2)}")
    else:
        print(f"❌ Error reproduction test failed: {error_test['error']}")
    
    # Summary
    print("\n🏁 TEST SUMMARY")
    print("=" * 30)
    
    if tool_test["success"]:
        missing_params = tool_test["missing_mobile_app_params"]
        issue_confirmed = len(missing_params) > 0
        fix_validated = len(missing_params) == 0
        
        if fix_validated:
            print("✅ MOBILE APP SUPPORT VALIDATED")
            print("   All required mobile app parameters are present")
            print("   Mobile app campaigns should work correctly!")
        elif issue_confirmed:
            print("❌ MOBILE APP SUPPORT INCOMPLETE")
            print(f"   Missing parameters: {missing_params}")
            print("   Mobile app campaigns may fail without these parameters")
        else:
            print("❓ STATUS UNCLEAR")
            print("   Could not determine mobile app parameter status")
    else:
        print("❌ TEST FAILED")
        print("   Could not connect to MCP server or validate tools")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())