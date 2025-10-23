#!/usr/bin/env python3
"""
Run Meta Ads MCP using FastMCP's native streamable HTTP transport.
This supports SSE (Server-Sent Events) which Cursor expects.
"""

import os
import uvicorn

# Set environment variables
os.environ.setdefault("META_APP_ID", "665587869862344")
os.environ.setdefault("META_APP_SECRET", "2eebb6109153f476f9df8625d673917e")
os.environ.setdefault("POSTGRES_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

from meta_ads_mcp.core.server import mcp_server
from meta_ads_mcp.core.http_auth_integration import setup_fastmcp_http_auth

print("=" * 70)
print("🚀 Meta Ads MCP - FastMCP Native HTTP (SSE)")
print("=" * 70)
print("  URL: http://0.0.0.0:8080/mcp")
print("  SSE: http://0.0.0.0:8080/sse")
print("  Auth: PAT tokens via Authorization: Bearer <token>")
print("  Health: http://0.0.0.0:8080/health")
print("=" * 70)

# Setup HTTP authentication integration
setup_fastmcp_http_auth(mcp_server)

# Enable JSON responses for HTTP transport
mcp_server.settings.json_response = True

# Get FastMCP's streamable HTTP app
app = mcp_server.streamable_http_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

