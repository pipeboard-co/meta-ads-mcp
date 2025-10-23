#!/usr/bin/env python3
"""
Test PAT authentication with the backend MCP server
"""
import requests
import json

# Backend MCP server URL
MCP_SERVER_URL = "http://localhost:8080"

def test_pat_auth(pat_token: str):
    """Test PAT authentication by calling tools/list"""
    
    print(f"\n{'='*60}")
    print("Testing PAT Authentication with Backend MCP Server")
    print(f"{'='*60}\n")
    
    print(f"🔑 Using PAT Token: {pat_token[:15]}...")
    print(f"🌐 MCP Server URL: {MCP_SERVER_URL}")
    
    headers = {
        "Authorization": f"Bearer {pat_token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # MCP tools/list request
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    print(f"\n📤 Sending Request:")
    print(f"   Method: POST")
    print(f"   Endpoint: {MCP_SERVER_URL}/mcp/")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"\n📥 Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Authentication Successful!")
            data = response.json()
            
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"\n📋 Available Tools ({len(tools)}):")
                for i, tool in enumerate(tools[:5], 1):  # Show first 5
                    print(f"   {i}. {tool.get('name', 'Unknown')}")
                    print(f"      {tool.get('description', '')[:60]}...")
                if len(tools) > 5:
                    print(f"   ... and {len(tools) - 5} more tools")
            else:
                print(f"\n   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Authentication Failed!")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to MCP server")
        print(f"   Make sure the server is running at {MCP_SERVER_URL}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_pat_auth.py <PAT_TOKEN>")
        print("\nGet a PAT token from http://localhost:3000/tokens")
        print("Copy the full token (starts with 'mcp_') and paste it here")
        sys.exit(1)
    
    pat_token = sys.argv[1]
    test_pat_auth(pat_token)
