"""Authentication-specific functionality for Meta Ads API.

The Meta Ads MCP server supports two authentication modes:

1. **Development/Local Mode** (default)
   - Uses local callback server on localhost:8080+ for OAuth redirect
   - Requires META_ADS_DISABLE_CALLBACK_SERVER to NOT be set
   - Best for local development and testing

2. **Production Mode**
   - Uses META_ACCESS_TOKEN for direct token authentication
   - Or uses META_REDIRECT_URI for public OAuth redirect endpoint
   - Best for server deployments

Environment Variables:
- META_APP_ID: Your Meta App ID (required)
- META_APP_SECRET: Your Meta App Secret (required for token exchange)
- META_ACCESS_TOKEN: Direct Meta token (optional, for non-interactive auth)
- META_REDIRECT_URI: Custom OAuth redirect URI (optional, for production OAuth)
- META_ADS_DISABLE_CALLBACK_SERVER: Disables local server (optional)
- META_ADS_DISABLE_LOGIN_LINK: Hard-disables the get_login_link tool (optional)
"""

import json
from typing import Optional
import asyncio
import os
from .api import meta_api_tool
from . import auth
from .auth import start_callback_server, shutdown_callback_server, auth_manager
from .server import mcp_server
from .utils import logger, META_APP_SECRET

# Only register the login link tool if not explicitly disabled
ENABLE_LOGIN_LINK = not bool(os.environ.get("META_ADS_DISABLE_LOGIN_LINK", ""))


async def get_login_link(access_token: Optional[str] = None) -> str:
    """
    Get a clickable login link for Meta Ads authentication.
    
    This tool generates an OAuth URL for authenticating with Meta Ads API.
    For local development, it starts a callback server automatically.
    For production, set META_REDIRECT_URI to your custom redirect endpoint.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
    
    Returns:
        A clickable resource link for Meta authentication
    """
    callback_server_disabled = bool(os.environ.get("META_ADS_DISABLE_CALLBACK_SERVER", ""))
    
    if callback_server_disabled:
        # Production mode - provide instructions for manual OAuth
        logger.info("Production OAuth mode - callback server disabled")
        
        # Check if META_REDIRECT_URI is set
        redirect_uri = os.environ.get("META_REDIRECT_URI")
        if redirect_uri:
            # Generate auth URL with custom redirect URI
            auth_manager.redirect_uri = redirect_uri
            login_url = auth_manager.get_auth_url()
            
            return json.dumps({
                "message": "🔐 Authentication Required",
                "instructions": "Use the link below to authenticate with Meta Ads.",
                "login_url": login_url,
                "markdown_link": f"[🚀 Authenticate with Meta Ads]({login_url})",
                "what_to_do": "Click the link to complete OAuth. After authorization, exchange the code at your redirect URI for an access token.",
                "redirect_uri": redirect_uri,
                "authentication_method": "production_oauth_with_redirect",
                "next_steps": "After receiving the authorization code at your redirect URI, exchange it for an access token using the Meta Graph API."
            }, indent=2)
        else:
            return json.dumps({
                "message": "⚠️ Production Authentication Setup Required",
                "error": "Callback server is disabled but no META_REDIRECT_URI is configured",
                "solutions": [
                    "🔧 Set META_REDIRECT_URI environment variable to your OAuth redirect endpoint",
                    "🔑 Or provide a direct META_ACCESS_TOKEN environment variable",
                    "💻 Or enable callback server by unsetting META_ADS_DISABLE_CALLBACK_SERVER for local development"
                ],
                "authentication_method": "production_oauth_missing_config"
            }, indent=2)
    else:
        # Local development mode with callback server
        # Check if we have a cached token
        cached_token = auth_manager.get_access_token()
        token_status = "No token" if not cached_token else "Valid token"
        
        # If we already have a valid token and none was provided, just return success
        if cached_token and not access_token:
            logger.info("get_login_link called with existing valid token")
            return json.dumps({
                "message": "✅ Already Authenticated", 
                "status": "You're successfully authenticated with Meta Ads!",
                "token_info": f"Token preview: {cached_token[:10]}...",
                "created_at": auth_manager.token_info.created_at if hasattr(auth_manager, "token_info") else None,
                "expires_in": auth_manager.token_info.expires_in if hasattr(auth_manager, "token_info") else None,
                "authentication_method": "meta_oauth",
                "ready_to_use": "You can now use all Meta Ads MCP tools and commands."
            }, indent=2)
        
        # IMPORTANT: Start the callback server first by calling our helper function
        # This ensures the server is ready before we provide the URL to the user
        logger.info("Starting callback server for authentication")
        try:
            port = start_callback_server()
            logger.info(f"Callback server started on port {port}")
            
            # Generate direct login URL
            auth_manager.redirect_uri = f"http://localhost:{port}/callback"  # Ensure port is set correctly
            logger.info(f"Setting redirect URI to {auth_manager.redirect_uri}")
            login_url = auth_manager.get_auth_url()
            logger.info(f"Generated login URL: {login_url}")
        except Exception as e:
            logger.error(f"Failed to start callback server: {e}")
            return json.dumps({
                "message": "❌ Local Authentication Unavailable",
                "error": "Cannot start local callback server for authentication",
                "reason": str(e),
                "solutions": [
                    "🔑 Use direct token: Set META_ACCESS_TOKEN environment variable", 
                    "🔧 Check if another service is using the required ports",
                    "🌐 Or set META_REDIRECT_URI for production OAuth"
                ],
                "authentication_method": "meta_oauth_disabled"
            }, indent=2)
        
    # Check if we can exchange for long-lived tokens
    token_exchange_supported = bool(META_APP_SECRET)
    token_duration = "60 days" if token_exchange_supported else "1-2 hours"
    
    # Return a special format that helps the LLM format the response properly
    response = {
        "message": "🔗 Click to Authenticate",
        "login_url": login_url,
        "markdown_link": f"[🚀 Authenticate with Meta Ads]({login_url})",
        "instructions": "Click the link above to authenticate with Meta Ads.",
        "server_info": f"Local callback server running on port {port}",
        "token_duration": f"Your token will be valid for approximately {token_duration}",
        "authentication_method": "meta_oauth",
        "what_happens_next": "After clicking, you'll be redirected to Meta's authentication page. Once completed, your token will be automatically saved.",
        "security_note": "This uses a secure local callback server for development purposes."
    }
    
    # Wait a moment to ensure the server is fully started
    await asyncio.sleep(1)
    
    return json.dumps(response, indent=2)

# Conditionally register as MCP tool only when enabled
if ENABLE_LOGIN_LINK:
    get_login_link = mcp_server.tool()(get_login_link)
