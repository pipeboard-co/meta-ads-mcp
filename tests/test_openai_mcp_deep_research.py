#!/usr/bin/env python3
"""
OpenAI MCP Deep Research Integration Tests

This test suite validates the OpenAI MCP specification compliance:
- search tool: Returns list of IDs based on query
- fetch tool: Returns complete record data by ID
- ChatGPT Deep Research compatibility
- Integration with existing authentication

Usage:
    1. Start the server: python -m meta_ads_mcp --transport streamable-http --port 8080
    2. Run tests: python -m pytest tests/test_openai_mcp_deep_research.py -v

Or run directly:
    python tests/test_openai_mcp_deep_research.py
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, Optional, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")
    print("   Install with: pip install python-dotenv")

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OpenAIMCPTester:
    """Test suite for OpenAI MCP Deep Research compatibility"""
    
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
            "User-Agent": "OpenAI-MCP-Test-Client/1.0"
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

    def test_search_tool_exists(self, auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Test that the search tool is available in tools list"""
        result = self._make_request("tools/list", {}, auth_headers)
        
        if not result["success"]:
            return {"success": False, "error": "Failed to get tools list"}
        
        tools = result["json"]["result"].get("tools", [])
        search_tool = next((tool for tool in tools if tool["name"] == "search"), None)
        
        return {
            "success": search_tool is not None,
            "tool": search_tool,
            "all_tools": [tool["name"] for tool in tools]
        }

    def test_fetch_tool_exists(self, auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Test that the fetch tool is available in tools list"""
        result = self._make_request("tools/list", {}, auth_headers)
        
        if not result["success"]:
            return {"success": False, "error": "Failed to get tools list"}
        
        tools = result["json"]["result"].get("tools", [])
        fetch_tool = next((tool for tool in tools if tool["name"] == "fetch"), None)
        
        return {
            "success": fetch_tool is not None,
            "tool": fetch_tool,
            "all_tools": [tool["name"] for tool in tools]
        }

    def test_search_tool_call(self, query: str, auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Test calling the search tool with a query"""
        result = self._make_request("tools/call", {
            "name": "search",
            "arguments": {"query": query}
        }, auth_headers)
        
        if not result["success"]:
            return {"success": False, "error": result.get("text", "Unknown error")}
        
        # Parse the tool response
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            ids = parsed_content.get("ids", [])
            
            return {
                "success": True,
                "ids": ids,
                "raw_content": content,
                "id_count": len(ids)
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Search tool did not return valid JSON",
                "raw_content": content
            }

    def test_fetch_tool_call(self, record_id: str, auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Test calling the fetch tool with an ID"""
        result = self._make_request("tools/call", {
            "name": "fetch",
            "arguments": {"id": record_id}
        }, auth_headers)
        
        if not result["success"]:
            return {"success": False, "error": result.get("text", "Unknown error")}
        
        # Parse the tool response
        response_data = result["json"]["result"]
        content = response_data.get("content", [{}])[0].get("text", "")
        
        try:
            parsed_content = json.loads(content)
            
            return {
                "success": True,
                "record": parsed_content,
                "raw_content": content,
                "has_required_fields": all(field in parsed_content for field in ["id", "title", "text"])
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Fetch tool did not return valid JSON",
                "raw_content": content
            }

    def test_search_fetch_workflow(self, auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Test the complete search->fetch workflow that ChatGPT Deep Research expects"""
        
        # Step 1: Search for something that will return account IDs
        search_result = self.test_search_tool_call("Yves", auth_headers)
        
        if not search_result["success"]:
            return {
                "success": False,
                "step": "search",
                "error": search_result.get("error", "Search failed")
            }
        
        if not search_result["ids"]:
            return {
                "success": False,
                "step": "search",
                "error": "Search returned no IDs"
            }
        
        # Step 2: Fetch the first ID
        first_id = search_result["ids"][0]
        fetch_result = self.test_fetch_tool_call(first_id, auth_headers)
        
        if not fetch_result["success"]:
            return {
                "success": False,
                "step": "fetch",
                "error": fetch_result.get("error", "Fetch failed"),
                "searched_id": first_id
            }
        
        return {
            "success": True,
            "search_ids": search_result["ids"],
            "fetched_record": fetch_result["record"],
            "workflow_complete": True
        }

    def test_openai_specification_compliance(self, auth_headers: Dict[str, str] = None) -> Dict[str, bool]:
        """Test compliance with OpenAI's MCP specification for Deep Research"""
        results = {}
        
        print("\n🧪 Testing OpenAI MCP Specification Compliance")
        print("="*55)
        
        # Test 1: Both required tools exist
        print("🔍 Checking required tools exist")
        search_exists = self.test_search_tool_exists(auth_headers)
        fetch_exists = self.test_fetch_tool_exists(auth_headers)
        
        results["search_tool_exists"] = search_exists["success"]
        results["fetch_tool_exists"] = fetch_exists["success"]
        
        if not search_exists["success"]:
            print("❌ Search tool not found")
            print(f"   Available tools: {search_exists.get('all_tools', [])}")
            return results
        
        if not fetch_exists["success"]:
            print("❌ Fetch tool not found")
            print(f"   Available tools: {fetch_exists.get('all_tools', [])}")
            return results
        
        print("✅ Both search and fetch tools found")
        
        # Test 2: Search tool returns proper format
        print("\n🔍 Testing search tool format")
        search_result = self.test_search_tool_call("Yves", auth_headers)
        results["search_format_valid"] = search_result["success"]
        
        if not search_result["success"]:
            print(f"❌ Search tool failed: {search_result.get('error', 'Unknown error')}")
            return results
        
        print(f"✅ Search tool returns valid format with {search_result['id_count']} IDs")
        
        # Test 3: Fetch tool returns proper format
        if search_result["ids"]:
            print("\n🔍 Testing fetch tool format")
            first_id = search_result["ids"][0]
            fetch_result = self.test_fetch_tool_call(first_id, auth_headers)
            results["fetch_format_valid"] = fetch_result["success"]
            results["fetch_has_required_fields"] = fetch_result.get("has_required_fields", False)
            
            if not fetch_result["success"]:
                print(f"❌ Fetch tool failed: {fetch_result.get('error', 'Unknown error')}")
                return results
            
            print("✅ Fetch tool returns valid format")
            
            if fetch_result["has_required_fields"]:
                print("✅ Fetch response includes required fields (id, title, text)")
            else:
                print("⚠️  Fetch response missing some required fields")
        else:
            print("⚠️  Cannot test fetch tool - no IDs returned by search")
            results["fetch_format_valid"] = False
            results["fetch_has_required_fields"] = False
        
        # Test 4: Complete workflow
        print("\n🔍 Testing complete search->fetch workflow")
        workflow_result = self.test_search_fetch_workflow(auth_headers)
        results["workflow_complete"] = workflow_result["success"]
        
        if workflow_result["success"]:
            print("✅ Complete workflow successful")
        else:
            print(f"❌ Workflow failed at {workflow_result.get('step', 'unknown')} step")
            print(f"   Error: {workflow_result.get('error', 'Unknown error')}")
        
        return results

    def test_page_search_functionality(self, auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Test that the search function includes page searching when query mentions pages"""
        print("\n🔍 Testing page search functionality")
        
        # Test 1: Search with page-related query that matches an account name
        page_search_result = self.test_search_tool_call("Injury Payouts pages", auth_headers)
        
        if not page_search_result["success"]:
            return {
                "success": False,
                "error": f"Page search failed: {page_search_result.get('error', 'Unknown error')}"
            }
        
        # Check if page records are included in results
        page_ids = [id for id in page_search_result["ids"] if id.startswith("page:")]
        
        result = {
            "success": True,
            "page_search_works": len(page_ids) > 0,
            "page_ids_found": len(page_ids),
            "total_ids": len(page_search_result["ids"]),
            "page_ids": page_ids
        }
        
        if len(page_ids) > 0:
            print(f"✅ Page search working - found {len(page_ids)} page records")
            
            # Test 2: Fetch a page record
            first_page_id = page_ids[0]
            fetch_result = self.test_fetch_tool_call(first_page_id, auth_headers)
            
            if fetch_result["success"]:
                print(f"✅ Page fetch working - retrieved page record: {first_page_id}")
                result["page_fetch_works"] = True
                result["fetched_page_data"] = fetch_result.get("record", {})
            else:
                print(f"❌ Page fetch failed: {fetch_result.get('error', 'Unknown error')}")
                result["page_fetch_works"] = False
        else:
            print("⚠️  No page records found in search results")
            result["page_fetch_works"] = False
        
        return result

    def run_openai_compliance_test_suite(self) -> bool:
        """Run complete OpenAI MCP compliance test suite"""
        print("🚀 OpenAI MCP Deep Research Compliance Test Suite")
        print("="*60)
        
        # Check server availability first
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            server_running = response.status_code in [200, 404]
        except:
            server_running = False
        
        if not server_running:
            print("❌ Server is not running at", self.base_url)
            print("   Please start the server with:")
            print("   python -m meta_ads_mcp --transport streamable-http --port 8080")
            return False
        
        print("✅ Server is running")
        
        # Test with no authentication (server handles auth implicitly)
        auth_scenarios = [
            {
                "name": "No Authentication",
                "headers": None
            }
        ]
        
        all_results = {}
        
        for scenario in auth_scenarios:
            print(f"\n📋 Testing with: {scenario['name']}")
            print("-" * 40)
            
            results = self.test_openai_specification_compliance(scenario["headers"])
            
            # Add page search test
            page_results = self.test_page_search_functionality(scenario["headers"])
            results["page_search_functionality"] = page_results.get("page_search_works", False)
            results["page_fetch_functionality"] = page_results.get("page_fetch_works", False)
            
            all_results[scenario["name"]] = results
        
        # Summary
        print("\n🏁 OPENAI MCP COMPLIANCE TEST RESULTS")
        print("="*40)
        
        overall_success = True
        for scenario_name, results in all_results.items():
            scenario_success = all(results.values()) if results else False
            status = "✅ COMPLIANT" if scenario_success else "❌ NON-COMPLIANT"
            print(f"{scenario_name}: {status}")
            
            if not scenario_success and results:
                for test_name, test_result in results.items():
                    if not test_result:
                        print(f"   ❌ {test_name}")
            
            if not scenario_success:
                overall_success = False
        
        print(f"\n📊 Overall OpenAI MCP Compliance: {'✅ COMPLIANT' if overall_success else '❌ NON-COMPLIANT'}")
        
        if overall_success:
            print("\n🎉 Server is fully compatible with OpenAI's MCP specification!")
            print("   • ChatGPT Deep Research: Ready")
            print("   • Search tool: Compliant (includes page search)")
            print("   • Fetch tool: Compliant")
            print("   • Workflow: Complete")
            print("   • Page Search: Enhanced")
        else:
            print("\n⚠️  Server needs updates for OpenAI MCP compliance")
            print("   See failed tests above for required changes")
        
        return overall_success


def main():
    """Main test execution"""
    tester = OpenAIMCPTester()
    success = tester.run_openai_compliance_test_suite()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 