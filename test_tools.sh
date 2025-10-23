#!/bin/bash

PAT_TOKEN="mcp_4ac25c262df6f6c7dbb0676a7c19185da9cd27931f04e175051e6ba4f37a9011"
MCP_URL="http://localhost:8080/mcp"

echo "================================"
echo "Testing Meta Ads MCP Tools"
echo "================================"
echo ""

# Test 1: Get Account Info
echo "📋 Test 1: Get Account Info"
echo "----------------------------"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_account_info",
      "arguments": {
        "account_id": "act_1288134801884591"
      }
    }
  }' | python3 -c "import sys, json; d = json.load(sys.stdin); content = d.get('result', {}).get('content', [{}])[0].get('text', ''); data = json.loads(content); print(json.dumps(data, indent=2)[:500])"

echo ""
echo ""

# Test 2: Get Campaigns
echo "📊 Test 2: Get Campaigns"
echo "----------------------------"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_campaigns",
      "arguments": {
        "account_id": "act_1288134801884591",
        "limit": 3
      }
    }
  }' | python3 -c "import sys, json; d = json.load(sys.stdin); content = d.get('result', {}).get('content', [{}])[0].get('text', ''); data = json.loads(content); campaigns = data.get('data', []); print(f'Found {len(campaigns)} campaigns'); [print(f\"  - {c.get('name', 'N/A')} (ID: {c.get('id', 'N/A')})\") for c in campaigns[:3]]"

echo ""
echo ""

# Test 3: Search Interests
echo "🎯 Test 3: Search Interests (Targeting)"
echo "----------------------------"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "search_interests",
      "arguments": {
        "query": "technology",
        "limit": 5
      }
    }
  }' | python3 -c "import sys, json; d = json.load(sys.stdin); content = d.get('result', {}).get('content', [{}])[0].get('text', ''); data = json.loads(content); interests = data.get('data', []); print(f'Found {len(interests)} interests'); [print(f\"  - {i.get('name', 'N/A')} (Audience: {i.get('audience_size_lower_bound', 0):,}+)\") for i in interests[:5]]"

echo ""
echo ""

# Test 4: Get Account Pages
echo "📄 Test 4: Get Account Pages"
echo "----------------------------"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_account_pages",
      "arguments": {
        "account_id": "act_1288134801884591"
      }
    }
  }' | python3 -c "import sys, json; d = json.load(sys.stdin); content = d.get('result', {}).get('content', [{}])[0].get('text', ''); data = json.loads(content); pages = data.get('pages', []); print(f'Found {len(pages)} pages'); [print(f\"  - {p.get('name', 'N/A')} (ID: {p.get('id', 'N/A')})\") for p in pages[:3]]"

echo ""
echo ""

# Test 5: Search Geo Locations
echo "🌍 Test 5: Search Geo Locations"
echo "----------------------------"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "search_geo_locations",
      "arguments": {
        "query": "California",
        "limit": 3
      }
    }
  }' | python3 -c "import sys, json; d = json.load(sys.stdin); content = d.get('result', {}).get('content', [{}])[0].get('text', ''); data = json.loads(content); locations = data.get('data', []); print(f'Found {len(locations)} locations'); [print(f\"  - {loc.get('name', 'N/A')} ({loc.get('type', 'N/A')}, Key: {loc.get('key', 'N/A')})\") for loc in locations[:3]]"

echo ""
echo ""
echo "================================"
echo "✅ All Tests Complete!"
echo "================================"
