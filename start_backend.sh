#!/bin/bash
export META_APP_ID=665587869862344
export META_APP_SECRET=2eebb6109153f476f9df8625d673917e
export POSTGRES_URL="postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

cd /Users/naveengarhwal/meta-ads-mcp-1

# Initialize database
python3 << 'PYEOF'
from meta_ads_mcp.core.db import init_db
init_db()
print("✅ Database initialized")
PYEOF

# Start MCP server using uvicorn directly
python3 -c "
from meta_ads_mcp.core.server import mcp_server
from meta_ads_mcp.core.http_auth_integration import setup_fastmcp_http_auth
import uvicorn

# Setup HTTP authentication
setup_fastmcp_http_auth(mcp_server)

# Get the Starlette app
app = mcp_server.sse_app()

print('🚀 Starting Meta Ads MCP Server on http://0.0.0.0:8080/mcp')
uvicorn.run(app, host='0.0.0.0', port=8080)
"
