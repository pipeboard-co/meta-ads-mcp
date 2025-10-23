"""ASGI application entry point for Meta Ads MCP server."""

from meta_ads_mcp.core.server import mcp_server
from meta_ads_mcp.core.http_auth_integration import setup_fastmcp_http_auth

# Enable JSON responses
mcp_server.settings.json_response = True

# Setup HTTP authentication integration
setup_fastmcp_http_auth(mcp_server)

# Get the Starlette app for streamable HTTP (JSON) transport
app = mcp_server.streamable_http_app()

print("✅ Meta Ads MCP Server ASGI app created (JSON/HTTP transport)")

