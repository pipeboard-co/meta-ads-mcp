#!/usr/bin/env python3
"""
Focused Account Search Test for Meta Ads MCP

This test validates that the search tool correctly finds and returns
account data for known test accounts.

Expected test accounts:
- act_4891437610982483 (Yves Junqueira)
- act_701351919139047 (Injury Payouts)
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

class AccountSearchTester:
    """Test suite focused on account search functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp/"
        self.request_id = 1
        
        # Expected test data
        self.expected_accounts = [
            {
                "id": "act_4891437610982483", 
                "name": "Yves Junqueira",
                "account_id": "4891437610982483"
            },
            {
                "id": "act_701351919139047", 
                "name": "Injury Payouts", 
                "account_id": "701351919139047"
            }
        ]
        
    def _make_request(self, method: str, params: Dict[str, Any] = None, 
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "Account-Search-Test-Client/1.0"
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
                timeout=10
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

    def test_search_accounts(self) -> Dict[str, Any]:
        """Test searching for accounts with various queries"""
        
        queries_to_test = [
            "accounts",
            "ad accounts", 
            "meta accounts",
            "Yves",
            "Injury Payouts"
        ]
        
        results = {}
        
        for query in queries_to_test:
            print(f"\n🔍 Testing search query: '{query}'")
            
            result = self._make_request("tools/call", {
                "name": "search",
                "arguments": {"query": query}
            })
            
            if not result["success"]:
                results[query] = {
                    "success": False, 
                    "error": result.get("text", "Unknown error")
                }
                print(f"❌ Search failed: {result.get('text', 'Unknown error')}")
                continue
            
            # Parse the tool response
            response_data = result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            
            try:
                parsed_content = json.loads(content)
                ids = parsed_content.get("ids", [])
                
                # Check for expected account IDs
                expected_account_ids = [f"account:{acc['id']}" for acc in self.expected_accounts]
                found_account_ids = [id for id in ids if id.startswith("account:")]
                
                results[query] = {
                    "success": True,
                    "ids": ids,
                    "account_ids": found_account_ids,
                    "found_expected_accounts": len([id for id in expected_account_ids if id in found_account_ids]),
                    "total_expected": len(expected_account_ids),
                    "raw_content": parsed_content
                }
                
                print(f"✅ Found {len(found_account_ids)} account IDs: {found_account_ids}")
                print(f"📊 Expected accounts found: {results[query]['found_expected_accounts']}/{results[query]['total_expected']}")
                print(f"🔍 Raw response: {json.dumps(parsed_content, indent=2)}")
                
            except json.JSONDecodeError:
                results[query] = {
                    "success": False,
                    "error": "Search tool did not return valid JSON",
                    "raw_content": content
                }
                print(f"❌ Invalid JSON response: {content}")
        
        return results

    def test_fetch_account(self, account_id: str) -> Dict[str, Any]:
        """Test fetching a specific account by ID"""
        
        print(f"\n🔍 Testing fetch for account: {account_id}")
        
        result = self._make_request("tools/call", {
            "name": "fetch",
            "arguments": {"id": account_id}
        })
        
        if not result["success"]:
            return {
                "success": False, 
                "error": result.get("text", "Unknown error")
            }
        
        # Parse the tool response
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            # Validate required fields for OpenAI MCP compliance
            required_fields = ["id", "title", "text"]
            has_required_fields = all(field in parsed_content for field in required_fields)
            
            result_data = {
                "success": True,
                "record": parsed_content,
                "has_required_fields": has_required_fields,
                "missing_fields": [field for field in required_fields if field not in parsed_content]
            }
            
            if has_required_fields:
                print(f"✅ Successfully fetched account with all required fields")
                print(f"   Title: {parsed_content.get('title', 'N/A')}")
                print(f"   ID: {parsed_content.get('id', 'N/A')}")
            else:
                print(f"⚠️  Account fetched but missing required fields: {result_data['missing_fields']}")
            
            return result_data
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Fetch tool did not return valid JSON",
                "raw_content": content
            }

    def run_account_search_tests(self) -> bool:
        """Run comprehensive account search tests"""
        
        print("🚀 Meta Ads Account Search Test Suite")
        print("="*50)
        
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
        
        # Test 0: First try get_ad_accounts to see if we can get raw data
        print("\n" + "="*50)
        print("📋 PHASE 0: Testing Direct Account Access")
        print("="*50)
        
        account_result = self._make_request("tools/call", {
            "name": "get_ad_accounts",
            "arguments": {
                "user_id": "me",
                "parameters": json.dumps({"limit": 5})
            }
        })
        
        if account_result["success"]:
            response_data = account_result["json"]["result"]
            content = response_data.get("content", [{}])[0].get("text", "")
            try:
                account_data = json.loads(content)
                print(f"✅ get_ad_accounts returned: {json.dumps(account_data, indent=2)}")
            except:
                print(f"⚠️  get_ad_accounts raw response: {content}")
        else:
            print(f"❌ get_ad_accounts failed: {account_result.get('text', 'Unknown error')}")

        # Test 1: Search for accounts
        print("\n" + "="*50)
        print("📋 PHASE 1: Testing Account Search")
        print("="*50)
        
        search_results = self.test_search_accounts()
        
        # Find the best search result that returned accounts
        best_search = None
        for query, result in search_results.items():
            if result.get("success") and result.get("account_ids"):
                best_search = result
                break
        
        if not best_search:
            print("\n❌ No search queries returned account IDs")
            print("📊 Search Results Summary:")
            for query, result in search_results.items():
                if result.get("success"):
                    print(f"   '{query}': {len(result.get('ids', []))} total IDs, {len(result.get('account_ids', []))} account IDs")
                else:
                    print(f"   '{query}': FAILED - {result.get('error', 'Unknown error')}")
            return False
        
        print(f"\n✅ Found accounts in search results")
        account_ids = best_search["account_ids"]
        print(f"📋 Account IDs found: {account_ids}")
        
        # Test 2: Fetch account details
        print("\n" + "="*50)
        print("📋 PHASE 2: Testing Account Fetch")
        print("="*50)
        
        fetch_success = True
        for account_id in account_ids[:2]:  # Test first 2 accounts
            fetch_result = self.test_fetch_account(account_id)
            if not fetch_result["success"]:
                print(f"❌ Failed to fetch {account_id}: {fetch_result.get('error', 'Unknown error')}")
                fetch_success = False
            elif not fetch_result["has_required_fields"]:
                print(f"⚠️  {account_id} missing required fields: {fetch_result['missing_fields']}")
                fetch_success = False
        
        # Final assessment
        print("\n" + "="*50)
        print("📊 FINAL RESULTS")
        print("="*50)
        
        if fetch_success and account_ids:
            print("✅ Account search and fetch workflow: SUCCESS")
            print(f"   • Found {len(account_ids)} accounts")
            print(f"   • All fetched accounts have required fields")
            print(f"   • OpenAI MCP compliance: PASSED")
            return True
        else:
            print("❌ Account search and fetch workflow: FAILED")
            if not account_ids:
                print("   • Issue: No account IDs returned by search")
            if not fetch_success:
                print("   • Issue: Some accounts failed to fetch or missing required fields")
            return False


def main():
    """Main test execution"""
    tester = AccountSearchTester()
    success = tester.run_account_search_tests()
    
    if success:
        print("\n🎉 All account search tests passed!")
    else:
        print("\n⚠️  Some account search tests failed - see details above")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 