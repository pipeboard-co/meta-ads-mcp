#!/usr/bin/env python3
"""Start the Meta Ads MCP server with HTTP auth integration."""

import os

# Set environment variables
os.environ.setdefault("META_APP_ID", "665587869862344")
os.environ.setdefault("META_APP_SECRET", "2eebb6109153f476f9df8625d673917e")
os.environ.setdefault("POSTGRES_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

from meta_ads_mcp.core.server import mcp_server
from meta_ads_mcp.core.http_auth_integration import setup_fastmcp_http_auth

# Enable JSON responses
mcp_server.settings.json_response = True

# Setup HTTP authentication
setup_fastmcp_http_auth(mcp_server)

print("🚀 Meta Ads MCP Server Starting")
print("   Transport: streamable-http (JSON)")
print("   Auth: PAT tokens via Authorization header")

# Start the server - FastMCP will use default port from environment or 8000
mcp_server.run(transport="streamable-http")
