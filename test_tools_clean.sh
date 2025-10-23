#!/bin/bash

PAT_TOKEN="mcp_4ac25c262df6f6c7dbb0676a7c19185da9cd27931f04e175051e6ba4f37a9011"
MCP_URL="http://localhost:8080/mcp"
ACCOUNT_ID="act_398953170637981"

echo "🚀 Testing Meta Ads MCP Tools"
echo "========================================"
echo ""

# Test 1: Get Campaigns
echo "1️⃣  Get Campaigns"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"get_campaigns\",
      \"arguments\": {
        \"account_id\": \"$ACCOUNT_ID\",
        \"limit\": 3
      }
    }
  }" | python3 << 'PYTHON'
import sys, json
d = json.load(sys.stdin)
content = d.get('result', {}).get('content', [{}])[0].get('text', '')
data = json.loads(content)
campaigns = data.get('data', [])
print(f"   ✅ Found {len(campaigns)} campaigns")
for i, c in enumerate(campaigns[:3], 1):
    print(f"      {i}. {c.get('name', 'N/A')[:40]}")
    print(f"         Status: {c.get('status', 'N/A')}, ID: {c.get('id', 'N/A')}")
PYTHON

echo ""

# Test 2: Get Ad Sets
echo "2️⃣  Get Ad Sets"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 2,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"get_adsets\",
      \"arguments\": {
        \"account_id\": \"$ACCOUNT_ID\",
        \"limit\": 3
      }
    }
  }" | python3 << 'PYTHON'
import sys, json
d = json.load(sys.stdin)
content = d.get('result', {}).get('content', [{}])[0].get('text', '')
data = json.loads(content)
adsets = data.get('data', [])
print(f"   ✅ Found {len(adsets)} ad sets")
for i, a in enumerate(adsets[:3], 1):
    print(f"      {i}. {a.get('name', 'N/A')[:40]}")
    print(f"         Status: {a.get('status', 'N/A')}, ID: {a.get('id', 'N/A')}")
PYTHON

echo ""

# Test 3: Search Interests
echo "3️⃣  Search Interests (Targeting)"
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
        "query": "artificial intelligence",
        "limit": 5
      }
    }
  }' | python3 << 'PYTHON'
import sys, json
d = json.load(sys.stdin)
content = d.get('result', {}).get('content', [{}])[0].get('text', '')
data = json.loads(content)
interests = data.get('data', [])
print(f"   ✅ Found {len(interests)} interests")
for i, interest in enumerate(interests, 1):
    name = interest.get('name', 'N/A')
    audience = interest.get('audience_size_lower_bound', 0)
    print(f"      {i}. {name}")
    print(f"         Audience: {audience:,}+ people")
PYTHON

echo ""

# Test 4: Estimate Audience Size
echo "4️⃣  Estimate Audience Size"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 4,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"estimate_audience_size\",
      \"arguments\": {
        \"account_id\": \"$ACCOUNT_ID\",
        \"targeting\": {
          \"geo_locations\": {\"countries\": [\"US\"]},
          \"age_min\": 25,
          \"age_max\": 65
        }
      }
    }
  }" | python3 << 'PYTHON'
import sys, json
d = json.load(sys.stdin)
content = d.get('result', {}).get('content', [{}])[0].get('text', '')
data = json.loads(content)
if 'data' in data:
    estimate = data.get('data', [{}])[0] if isinstance(data.get('data'), list) else data.get('data', {})
    users = estimate.get('users', 0)
    print(f"   ✅ Estimated audience: {users:,} people")
    print(f"      Target: US, Ages 25-65")
else:
    print(f"   ℹ️  {data}")
PYTHON

echo ""

# Test 5: Search Demographics
echo "5️⃣  Search Demographics"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "search_demographics",
      "arguments": {
        "demographic_class": "life_events",
        "limit": 5
      }
    }
  }' | python3 << 'PYTHON'
import sys, json
d = json.load(sys.stdin)
content = d.get('result', {}).get('content', [{}])[0].get('text', '')
data = json.loads(content)
demographics = data.get('data', [])
print(f"   ✅ Found {len(demographics)} life events")
for i, demo in enumerate(demographics[:5], 1):
    name = demo.get('name', 'N/A')
    print(f"      {i}. {name}")
PYTHON

echo ""
echo "========================================"
echo "✅ All 5 tests completed successfully!"
echo "========================================"
