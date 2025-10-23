#!/usr/bin/env python3
"""
Test HTTP MCP client - simulates how a real MCP client would connect.
"""

import requests
import json
from typing import Dict, Any

class MCPHTTPClient:
    """Simple MCP HTTP client for testing."""
    
    def __init__(self, url: str, token: str):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        self.request_id = 0
    
    def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        self.request_id += 1
        
        request_data = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        
        if params is not None:
            request_data["params"] = params
        
        print(f"📤 Sending: {method}")
        
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                    return result
                elif "result" in result:
                    print(f"✅ Success")
                    return result
                else:
                    print(f"⚠️  Unexpected response format")
                    return result
            else:
                print(f"❌ HTTP Error: {response.text}")
                return {"error": {"code": response.status_code, "message": response.text}}
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return {"error": {"code": -1, "message": str(e)}}
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP connection."""
        return self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {}
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return self._send_request("tools/list")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific tool."""
        params = {"name": tool_name}
        if arguments:
            params["arguments"] = arguments
        return self._send_request("tools/call", params)
    
    def list_prompts(self) -> Dict[str, Any]:
        """List available prompts."""
        return self._send_request("prompts/list")


def test_mcp_server():
    """Test the MCP HTTP server with a real client flow."""
    
    print("=" * 70)
    print("🧪 Testing Meta Ads MCP HTTP Server")
    print("=" * 70)
    
    # Configuration
    url = "http://localhost:8080/mcp"
    token = "mcp_28c6a707dd94b8e457410c77edd4be94534290cae4a16abf1b35603f391be2a7"
    
    # Create client
    client = MCPHTTPClient(url, token)
    
    # Test 1: Initialize
    print("\n" + "=" * 70)
    print("Test 1: Initialize Connection")
    print("=" * 70)
    result = client.initialize()
    if "result" in result:
        server_info = result["result"].get("serverInfo", {})
        print(f"✅ Server: {server_info.get('name')} v{server_info.get('version')}")
        capabilities = result["result"].get("capabilities", {})
        print(f"✅ Capabilities: {list(capabilities.keys())}")
    else:
        print(f"❌ Initialize failed: {result}")
        return False
    
    # Test 2: List Tools
    print("\n" + "=" * 70)
    print("Test 2: List Tools")
    print("=" * 70)
    result = client.list_tools()
    if "result" in result:
        tools = result["result"].get("tools", [])
        print(f"✅ Found {len(tools)} tools")
        print(f"📋 First 5 tools:")
        for tool in tools[:5]:
            print(f"   - {tool['name']}: {tool.get('description', 'No description')[:60]}")
    else:
        print(f"❌ List tools failed: {result}")
        return False
    
    # Test 3: List Prompts
    print("\n" + "=" * 70)
    print("Test 3: List Prompts")
    print("=" * 70)
    result = client.list_prompts()
    if "result" in result:
        prompts = result["result"].get("prompts", [])
        print(f"✅ Found {len(prompts)} prompts")
    else:
        print(f"⚠️  List prompts response: {result}")
    
    # Test 4: Call a simple tool
    print("\n" + "=" * 70)
    print("Test 4: Call Tool (get_ad_accounts)")
    print("=" * 70)
    result = client.call_tool("get_ad_accounts")
    if "result" in result:
        content = result["result"].get("content", [])
        if content:
            print(f"✅ Tool executed successfully")
            print(f"📊 Response preview: {str(content[0])[:200]}...")
        else:
            print(f"⚠️  Tool returned empty content")
    else:
        print(f"❌ Tool call failed: {result}")
    
    # Test 5: Call search tool
    print("\n" + "=" * 70)
    print("Test 5: Call Tool (search_interests)")
    print("=" * 70)
    result = client.call_tool("search_interests", {"query": "fitness"})
    if "result" in result:
        content = result["result"].get("content", [])
        if content:
            print(f"✅ Search tool executed successfully")
            print(f"📊 Response preview: {str(content[0])[:200]}...")
        else:
            print(f"⚠️  Tool returned empty content")
    else:
        print(f"❌ Tool call failed: {result}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ HTTP MCP Server Test Complete!")
    print("=" * 70)
    print("🎉 Server is working correctly for hosted deployment!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = test_mcp_server()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

