#!/usr/bin/env python3
"""Run the Meta Ads MCP server with proper HTTP configuration."""

import os
import sys
import asyncio

# Set environment variables
os.environ.setdefault("META_APP_ID", "665587869862344")
os.environ.setdefault("META_APP_SECRET", "2eebb6109153f476f9df8625d673917e")
os.environ.setdefault("POSTGRES_URL", "postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

from meta_ads_mcp.core.server import mcp_server
from meta_ads_mcp.core.http_auth_integration import setup_fastmcp_http_auth
import uvicorn

# Enable JSON responses
mcp_server.settings.json_response = True

# Setup HTTP authentication
setup_fastmcp_http_auth(mcp_server)

print("=" * 60)
print("🚀 Meta Ads MCP Remote Server")
print("=" * 60)
print(f"URL: http://0.0.0.0:8080/mcp")
print(f"Transport: HTTP + JSON")
print(f"Auth: PAT tokens via Authorization: Bearer <token>")
print("=" * 60)

# Get the Starlette app
app = mcp_server.streamable_http_app()

# Start the app - need to initialize the session manager first
async def lifespan(app):
    """Initialize FastMCP's session manager."""
    # Get the session manager
    if hasattr(mcp_server, '_session_manager'):
        session_manager = mcp_server._session_manager
        if hasattr(session_manager, 'initialize'):
            await session_manager.initialize()
    yield
    # Cleanup on shutdown
    if hasattr(mcp_server, '_session_manager'):
        session_manager = mcp_server._session_manager
        if hasattr(session_manager, 'cleanup'):
            await session_manager.cleanup()

# Run with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")



