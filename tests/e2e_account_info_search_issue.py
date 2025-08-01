#!/usr/bin/env python3
"""
E2E Test for Account Info Search Issue

This test reproduces the issue reported by a user where get_account_info
cannot find account ID 414174661097171, while get_ad_accounts can see it.

Usage:
    1. Start the server: uv run python -m meta_ads_mcp --transport streamable-http --port 8080
    2. Run test: uv run python tests/e2e_account_info_search_issue.py

Or with pytest (manual only):
    uv run python -m pytest tests/e2e_account_info_search_issue.py -v -m e2e
"""

import pytest
import requests
import json
from typing import Dict, Any

@pytest.mark.e2e
@pytest.mark.skip(reason="E2E test - run manually only")
class TestAccountInfoSearchIssue:
    """E2E test for account info search issue"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        self.target_account_id = "414174661097171"
    
    def test_get_ad_accounts_can_see_target_account(self):
        """Verify get_ad_accounts can see account 414174661097171"""
        print(f"\n🔍 Testing if get_ad_accounts can see account {self.target_account_id}")
        
        params = {
            "name": "get_ad_accounts",
            "arguments": {}
        }
        
        result = self._make_request("tools/call", params)
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"Request failed: {result.get('error', 'Unknown error')}",
                "status_code": result["status_code"]
            }
        
        try:
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            parsed_content = json.loads(content)
            
            # Check for errors first
            error_info = self._check_for_errors(parsed_content)
            if error_info["has_error"]:
                return {
                    "success": False,
                    "error": f"get_ad_accounts returned error: {error_info['error_message']}",
                    "error_format": error_info["format"]
                }
            
            # Extract accounts data
            accounts = []
            if "data" in parsed_content:
                data = parsed_content["data"]
                
                # Handle case where data is already parsed (list/dict)
                if isinstance(data, list):
                    accounts = data
                elif isinstance(data, dict) and "data" in data:
                    accounts = data["data"]
                
                # Handle case where data is a JSON string that needs parsing
                elif isinstance(data, str):
                    try:
                        parsed_data = json.loads(data)
                        if isinstance(parsed_data, list):
                            accounts = parsed_data
                        elif isinstance(parsed_data, dict) and "data" in parsed_data:
                            accounts = parsed_data["data"]
                    except json.JSONDecodeError:
                        pass
            elif isinstance(parsed_content, list):
                accounts = parsed_content
            
            # Search for target account
            found_account = None
            for account in accounts:
                if isinstance(account, dict):
                    account_id = account.get("id", "").replace("act_", "")
                    if account_id == self.target_account_id:
                        found_account = account
                        break
            
            result_data = {
                "success": True,
                "total_accounts": len(accounts),
                "target_account_found": found_account is not None,
                "found_account_details": found_account if found_account else None,
                "all_account_ids": [
                    acc.get("id", "").replace("act_", "") 
                    for acc in accounts 
                    if isinstance(acc, dict) and acc.get("id")
                ]
            }
            
            print(f"✅ get_ad_accounts results:")
            print(f"   Total accounts found: {result_data['total_accounts']}")
            print(f"   Target account {self.target_account_id} found: {result_data['target_account_found']}")
            if found_account:
                print(f"   Account details: {found_account}")
            
            return result_data
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Could not parse get_ad_accounts response: {str(e)}",
                "raw_content": content
            }
    
    def test_get_account_info_cannot_find_target_account(self):
        """Verify get_account_info cannot find account 414174661097171"""
        print(f"\n🔍 Testing if get_account_info can find account {self.target_account_id}")
        
        params = {
            "name": "get_account_info",
            "arguments": {
                "account_id": self.target_account_id
            }
        }
        
        result = self._make_request("tools/call", params)
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"Request failed: {result.get('error', 'Unknown error')}",
                "status_code": result["status_code"]
            }
        
        try:
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            parsed_content = json.loads(content)
            
            # Check for errors
            error_info = self._check_for_errors(parsed_content)
            
            result_data = {
                "success": True,
                "has_error": error_info["has_error"],
                "error_message": error_info.get("error_message", ""),
                "error_format": error_info.get("format", ""),
                "raw_response": parsed_content
            }
            
            print(f"✅ get_account_info results:")
            print(f"   Has error: {result_data['has_error']}")
            if result_data['has_error']:
                print(f"   Error message: {result_data['error_message']}")
                print(f"   Error format: {result_data['error_format']}")
            else:
                print(f"   Unexpected success: {parsed_content}")
            
            return result_data
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Could not parse get_account_info response: {str(e)}",
                "raw_content": content
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
    
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "E2E-Test-Client/1.0"
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
            
            return {
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else None,
                "text": response.text,
                "success": response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "json": None,
                "text": str(e),
                "success": False,
                "error": str(e)
            }

def run_validation():
    """Run the validation tests"""
    print("🚀 Starting Account Info Search Issue Validation")
    print(f"Target Account ID: 414174661097171")
    print("="*60)
    
    test_instance = TestAccountInfoSearchIssue()
    
    # Test 1: Check if get_ad_accounts can see the account
    accounts_result = test_instance.test_get_ad_accounts_can_see_target_account()
    
    # Test 2: Check if get_account_info can find the account
    account_info_result = test_instance.test_get_account_info_cannot_find_target_account()
    
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    
    if accounts_result["success"]:
        print(f"✅ get_ad_accounts: Found {accounts_result['total_accounts']} total accounts")
        if accounts_result["target_account_found"]:
            print(f"✅ get_ad_accounts: Target account 414174661097171 IS visible")
        else:
            print(f"❌ get_ad_accounts: Target account 414174661097171 is NOT visible")
            print(f"   Available account IDs: {accounts_result.get('all_account_ids', [])}")
    else:
        print(f"❌ get_ad_accounts: Failed - {accounts_result['error']}")
    
    if account_info_result["success"]:
        if account_info_result["has_error"]:
            print(f"❌ get_account_info: Cannot find account (Error: {account_info_result['error_message']})")
        else:
            print(f"✅ get_account_info: Successfully found account")
    else:
        print(f"❌ get_account_info: Test failed - {account_info_result['error']}")
    
    # Determine if issue is confirmed
    issue_confirmed = (
        accounts_result.get("success", False) and
        accounts_result.get("target_account_found", False) and
        account_info_result.get("success", False) and
        account_info_result.get("has_error", False)
    )
    
    print("\n" + "="*60)
    if issue_confirmed:
        print("🐛 ISSUE CONFIRMED:")
        print("   - get_ad_accounts CAN see the account")
        print("   - get_account_info CANNOT find the account")
        print("   - This validates the user's complaint")
    else:
        print("🤔 ISSUE NOT CONFIRMED:")
        print("   - The behavior may be different than reported")
        print("   - Check individual test results above")
    print("="*60)

if __name__ == "__main__":
    run_validation()