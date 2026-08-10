"""MCP server configuration for Meta Ads API."""

from mcp.server.fastmcp import FastMCP
import argparse
import os
import sys
import json
from typing import Dict, Any, Optional
from .auth import login as login_auth
from .resources import list_resources, get_resource
from .utils import logger

# Initialize FastMCP server
mcp_server = FastMCP("meta-ads")

# Register resource URIs
mcp_server.resource(uri="meta-ads://resources")(list_resources)
mcp_server.resource(uri="meta-ads://images/{resource_id}")(get_resource)


class StreamableHTTPHandler:
    """Handles stateless Streamable HTTP requests for Meta Ads MCP"""
    
    def __init__(self):
        """Initialize handler with no session storage - all auth per request"""
        logger.debug("StreamableHTTPHandler initialized for stateless operation")
        
    def handle_request(self, request_headers: Dict[str, str], request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle individual request with authentication
        
        Args:
            request_headers: HTTP request headers
            request_body: JSON-RPC request body
            
        Returns:
            JSON response with auth status and any tool results
        """
        try:
            # Extract authentication configuration from headers
            auth_config = self.get_auth_config_from_headers(request_headers)
            logger.debug(f"Auth method detected: {auth_config['auth_method']}")
            
            # Handle based on auth method
            if auth_config['auth_method'] == 'bearer':
                return self.handle_bearer_request(auth_config, request_body)
            elif auth_config['auth_method'] == 'custom_meta_app':
                return self.handle_custom_app_request(auth_config, request_body)
            else:
                return self.handle_unauthenticated_request(request_body)
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                },
                'id': request_body.get('id')
            }
    
    def get_auth_config_from_headers(self, request_headers: Dict[str, str]) -> Dict[str, Any]:
        """Extract authentication configuration from HTTP headers
        
        Args:
            request_headers: HTTP request headers
            
        Returns:
            Dictionary with auth method and relevant credentials
        """
        # Security validation - only allow safe headers
        ALLOWED_VIA_HEADERS = {
            'bearer_token': True,          # ✅ Primary method - Meta access token
            'meta_app_id': True,           # ✅ Fallback only - triggers OAuth complexity
            'meta_app_secret': False,      # ❌ Server environment only
            'meta_access_token': False,    # ❌ Use the Authorization header instead
        }

        # PRIMARY: Check for Bearer token in Authorization header (handles 90%+ of cases)
        auth_header = request_headers.get('Authorization') or request_headers.get('authorization')
        if auth_header and auth_header.lower().startswith('bearer '):
            token = auth_header[7:].strip()
            logger.info("Bearer authentication detected (primary path)")
            return {
                'auth_method': 'bearer',
                'bearer_token': token,
                'requires_oauth': False  # Simple token-based auth
            }
        
        # FALLBACK: Custom Meta app (minority of users)
        meta_app_id = request_headers.get('X-META-APP-ID') or request_headers.get('x-meta-app-id')
        if meta_app_id:
            logger.debug("Custom Meta app authentication detected (fallback path)")
            return {
                'auth_method': 'custom_meta_app',
                'meta_app_id': meta_app_id,
                'requires_oauth': True  # Complex OAuth flow required
            }
        
        # No authentication provided
        logger.warning("No authentication method detected in headers")
        return {
            'auth_method': 'none',
            'requires_oauth': False
        }
    
    def handle_bearer_request(self, auth_config: Dict[str, Any], request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with Bearer token (primary path)
        
        Args:
            auth_config: Authentication configuration from headers
            request_body: JSON-RPC request body
            
        Returns:
            JSON response ready for tool execution
        """
        logger.debug("Processing Bearer authenticated request")
        token = auth_config['bearer_token']
        
        # Token is ready to use immediately for API calls
        # TODO: In next phases, this will execute the actual tool call
        return {
            'jsonrpc': '2.0',
            'result': {
                'status': 'ready',
                'auth_method': 'bearer',
                'message': 'Authentication successful with Bearer token',
                'token_source': 'bearer_header'
            },
            'id': request_body.get('id')
        }
    
    def handle_custom_app_request(self, auth_config: Dict[str, Any], request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with custom Meta app (fallback path)
        
        Args:
            auth_config: Authentication configuration from headers
            request_body: JSON-RPC request body
            
        Returns:
            JSON response indicating OAuth flow is required
        """
        logger.debug("Processing custom Meta app request (OAuth required)")
        
        # This may require OAuth flow initiation
        # Each request is independent - no session state
        return {
            'jsonrpc': '2.0',
            'result': {
                'status': 'oauth_required',
                'auth_method': 'custom_meta_app',
                'meta_app_id': auth_config['meta_app_id'],
                'message': 'OAuth flow required for custom Meta app authentication',
                'next_steps': 'Use get_login_link tool to initiate OAuth flow'
            },
            'id': request_body.get('id')
        }
    
    def handle_unauthenticated_request(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with no authentication
        
        Args:
            request_body: JSON-RPC request body
            
        Returns:
            JSON error response requesting authentication
        """
        logger.warning("Unauthenticated request received")
        
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': -32600,
                'message': 'Authentication required',
                'data': {
                    'supported_methods': [
                        'Authorization: Bearer <token> (recommended)',
                        'X-META-APP-ID: Custom Meta app OAuth (advanced users)'
                    ],
                    'documentation': 'https://github.com/pipeboard-co/meta-ads-mcp'
                }
            },
            'id': request_body.get('id')
        }


def login_cli():
    """
    Command-line function to authenticate with Meta
    """
    logger.info("Starting Meta Ads CLI authentication flow")
    print("Starting Meta Ads CLI authentication flow...")
    
    # Call the common login function
    login_auth()


def main():
    """Main entry point for the package"""
    # Log startup information
    logger.info("Meta Ads MCP server starting")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Args: {sys.argv}")
    
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description="Meta Ads MCP Server - Model Context Protocol server for Meta Ads API",
        epilog="For more information, see https://github.com/pipeboard-co/meta-ads-mcp"
    )
    parser.add_argument("--login", action="store_true", help="Authenticate with Meta and store the token")
    parser.add_argument("--app-id", type=str, help="Meta App ID (Client ID) for authentication")
    parser.add_argument("--version", action="store_true", help="Show the version of the package")
    
    # Transport configuration arguments
    parser.add_argument("--transport", type=str, choices=["stdio", "streamable-http"], 
                       default="stdio", 
                       help="Transport method: 'stdio' for MCP clients (default), 'streamable-http' for HTTP API access")
    parser.add_argument("--port", type=int, default=8080, 
                       help="Port for Streamable HTTP transport (default: 8080, only used with --transport streamable-http)")
    parser.add_argument("--host", type=str, default="localhost", 
                       help="Host for Streamable HTTP transport (default: localhost, only used with --transport streamable-http)")
    parser.add_argument("--sse-response", action="store_true", 
                       help="Use SSE response format instead of JSON (default: JSON, only used with --transport streamable-http)")
    
    args = parser.parse_args()
    logger.debug(f"Parsed args: login={args.login}, app_id={args.app_id}, version={args.version}")
    logger.debug(f"Transport args: transport={args.transport}, port={args.port}, host={args.host}, sse_response={args.sse_response}")
    
    # Validate CLI argument combinations
    if args.transport == "stdio" and (args.port != 8080 or args.host != "localhost" or args.sse_response):
        logger.warning("HTTP transport arguments (--port, --host, --sse-response) are ignored when using stdio transport")
        print("Warning: HTTP transport arguments are ignored when using stdio transport")
    
    # Update app ID if provided as environment variable or command line arg
    from .auth import auth_manager, meta_config
    
    # Check environment variable first (early init)
    env_app_id = os.environ.get("META_APP_ID")
    if env_app_id:
        logger.debug(f"Found META_APP_ID in environment: {env_app_id}")
    else:
        logger.warning("META_APP_ID not found in environment variables")
    
    # Command line takes precedence
    if args.app_id:
        logger.info(f"Setting app_id from command line: {args.app_id}")
        auth_manager.app_id = args.app_id
        meta_config.set_app_id(args.app_id)
    elif env_app_id:
        logger.info(f"Setting app_id from environment: {env_app_id}")
        auth_manager.app_id = env_app_id
        meta_config.set_app_id(env_app_id)
    
    # Log the final app ID that will be used
    logger.info(f"Final app_id from meta_config: {meta_config.get_app_id()}")
    logger.info(f"Final app_id from auth_manager: {auth_manager.app_id}")
    logger.info(f"ENV META_APP_ID: {os.environ.get('META_APP_ID')}")
    
    # Show version if requested
    if args.version:
        from meta_ads_mcp import __version__
        logger.info(f"Displaying version: {__version__}")
        print(f"Meta Ads MCP v{__version__}")
        return 0
    
    # Handle login command
    if args.login:
        login_cli()
        return 0
    
    # PIPEBOARD_API_TOKEN used to exchange a Pipeboard API token for the underlying
    # Meta access token via pipeboard.co. That endpoint has been removed, because the
    # token it returned ignored the API token's account/permission scoping. Warn
    # anyone still setting it so the failure is self-explanatory.
    if os.environ.get("PIPEBOARD_API_TOKEN"):
        logger.warning("PIPEBOARD_API_TOKEN is set but is ignored by meta-ads-mcp.")
        print(
            "⚠️  PIPEBOARD_API_TOKEN is set but is ignored by meta-ads-mcp.",
            file=sys.stderr,
        )
        print(
            "   Pipeboard no longer hands out the underlying Meta access token. To authenticate\n"
            "   this server, either:\n"
            "     - create your own app at https://developers.facebook.com/apps/ and set "
            "META_ACCESS_TOKEN, or\n"
            "     - skip running this server and use the hosted MCP at "
            "https://meta-ads.mcp.pipeboard.co/\n"
            "       (which does authenticate with your Pipeboard API token).\n"
            "   Keep the variable set if you use the Pipeboard CLI or the hosted MCP - they\n"
            "   still use it. Only this package ignores it.",
            file=sys.stderr,
        )

    # Transport-specific server initialization and startup
    if args.transport == "streamable-http":
        logger.info(f"Starting MCP server with Streamable HTTP transport on {args.host}:{args.port}")
        logger.info("Mode: Stateless (no session persistence)")
        logger.info(f"Response format: {'SSE' if args.sse_response else 'JSON'}")
        logger.info("Primary auth method: Bearer Token (recommended)")
        logger.info("Fallback auth method: Custom Meta App OAuth (complex setup)")
        
        print(f"Starting Meta Ads MCP server with Streamable HTTP transport")
        print(f"Server will listen on {args.host}:{args.port}")
        print(f"Response format: {'SSE' if args.sse_response else 'JSON'}")
        print("Primary authentication: Bearer Token (via Authorization: Bearer <token> header)")
        print("Fallback authentication: Custom Meta App OAuth (via X-META-APP-ID header)")
        
        # Configure the existing server with streamable HTTP settings
        mcp_server.settings.host = args.host
        mcp_server.settings.port = args.port
        mcp_server.settings.stateless_http = True
        mcp_server.settings.json_response = not args.sse_response
        # Disable DNS rebinding protection. The SDK auto-enables it when the
        # server binds to a loopback host (127.0.0.1 / localhost / ::1) and
        # ships a port-wildcard allowlist (127.0.0.1:*). An upstream nginx
        # with `proxy_set_header Host $host;` strips the port from the Host
        # header before forwarding, so the allowlist does not match and every
        # request is rejected with HTTP 421 (the 1.0.106 production
        # regression). The protection is irrelevant for a loopback-only
        # service that no external client can reach.
        mcp_server.settings.transport_security.enable_dns_rebinding_protection = False

        # Import all tool modules to ensure they are registered
        logger.info("Ensuring all tools are registered for HTTP transport")
        from . import accounts, campaigns, adsets, ads, insights, authentication
        from . import ads_library, budget_schedules, reports, openai_deep_research
        
        # ✅ NEW: Setup HTTP authentication middleware
        logger.info("Setting up HTTP authentication middleware")
        try:
            from .http_auth_integration import setup_fastmcp_http_auth
            
            # Setup the FastMCP HTTP auth integration
            setup_fastmcp_http_auth(mcp_server)
            logger.info("FastMCP HTTP authentication integration setup successful")
            print("✅ FastMCP HTTP authentication integration enabled")
            print("   - Bearer tokens via Authorization: Bearer <token> header")
            print("   - Direct Meta tokens via X-META-ACCESS-TOKEN header")
            
        except Exception as e:
            logger.error(f"Failed to setup FastMCP HTTP authentication integration: {e}")
            print(f"⚠️  FastMCP HTTP authentication integration setup failed: {e}")
            print("   Server will still start but may not support header-based auth")
        
        # Log final server configuration
        logger.info(f"FastMCP server configured with:")
        logger.info(f"  - Host: {mcp_server.settings.host}")
        logger.info(f"  - Port: {mcp_server.settings.port}")
        logger.info(f"  - Stateless HTTP: {mcp_server.settings.stateless_http}")
        logger.info(f"  - JSON Response: {mcp_server.settings.json_response}")
        logger.info(f"  - Streamable HTTP Path: {mcp_server.settings.streamable_http_path}")
        
        # Start the FastMCP server with Streamable HTTP transport
        try:
            logger.info("Starting FastMCP server with Streamable HTTP transport")
            print(f"✅ Server configured successfully")
            print(f"   URL: http://{args.host}:{args.port}{mcp_server.settings.streamable_http_path}")
            print(f"   Mode: {'Stateless' if mcp_server.settings.stateless_http else 'Stateful'}")
            print(f"   Format: {'JSON' if mcp_server.settings.json_response else 'SSE'}")
            mcp_server.run(transport="streamable-http")
        except Exception as e:
            logger.error(f"Error starting Streamable HTTP server: {e}")
            print(f"Error: Failed to start Streamable HTTP server: {e}")
            return 1
    else:
        # Default stdio transport
        logger.info("Starting MCP server with stdio transport")
        mcp_server.run(transport='stdio') 