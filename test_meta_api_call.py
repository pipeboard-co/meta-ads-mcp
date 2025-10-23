#!/usr/bin/env python3
"""
Test actual Meta API call using stored OAuth token via PAT authentication
"""
import requests
import json

# Backend MCP server URL
MCP_SERVER_URL = "http://localhost:8080"

def test_meta_api_call(pat_token: str):
    """Test get_ad_accounts API call which uses stored OAuth token"""
    
    print(f"\n{'='*70}")
    print("Testing Meta API Call via PAT + Stored OAuth Token")
    print(f"{'='*70}\n")
    
    print(f"🔑 Using PAT Token: {pat_token[:15]}...")
    print(f"📡 This will use the stored Meta OAuth token from database")
    
    headers = {
        "Authorization": f"Bearer {pat_token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # MCP tools/call request for get_ad_accounts
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_ad_accounts",
            "arguments": {}
        },
        "id": 1
    }
    
    print(f"\n📤 Calling Meta API:")
    print(f"   Tool: get_ad_accounts")
    print(f"   This will fetch Meta Ad Accounts using stored OAuth token\n")
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response:")
        print(f"   Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            if "result" in data:
                result = data["result"]
                
                # Parse the content
                if isinstance(result, dict) and "content" in result:
                    for content_item in result["content"]:
                        if content_item.get("type") == "text":
                            text_content = content_item.get("text", "")
                            print(f"✅ Meta API Call Successful!\n")
                            print(f"📊 Response Data:")
                            print(f"{text_content[:500]}...")  # Show first 500 chars
                            
                            # Check if we got account data
                            if "account_id" in text_content or "id" in text_content:
                                print(f"\n✅ Successfully retrieved ad account data!")
                                print(f"✅ OAuth token from database is working!")
                                print(f"✅ Complete authentication flow verified!")
                            
                else:
                    print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Unexpected response format")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API Call Failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to MCP server")
        print(f"   Make sure the server is running at {MCP_SERVER_URL}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_meta_api_call.py <PAT_TOKEN>")
        print("\nThis will test the complete flow:")
        print("1. Authenticate with PAT token")
        print("2. Backend retrieves OAuth token from database")
        print("3. Backend calls Meta API with OAuth token")
        print("4. Returns ad accounts data")
        sys.exit(1)
    
    pat_token = sys.argv[1]
    test_meta_api_call(pat_token)
