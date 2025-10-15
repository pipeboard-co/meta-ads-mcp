"""Authentication-specific functionality for Meta Ads API.

The Meta Ads MCP server supports three authentication modes:

1. **Development/Local Mode** (default)
   - Uses local callback server on localhost:8080+ for OAuth redirect
   - Requires META_ADS_DISABLE_CALLBACK_SERVER to NOT be set
   - Best for local development and testing

2. **Production with API Token** 
   - Uses PIPEBOARD_API_TOKEN for server-to-server authentication
   - Bypasses OAuth flow entirely
   - Best for server deployments with pre-configured tokens

3. **Production OAuth Flow** (NEW)
   - Uses Pipeboard OAuth endpoints for dynamic client registration
   - Triggered when META_ADS_DISABLE_CALLBACK_SERVER is set but no PIPEBOARD_API_TOKEN
   - Supports MCP clients that implement OAuth 2.0 discovery

Environment Variables:
- PIPEBOARD_API_TOKEN: Enables mode 2 (token-based auth)  
- META_ADS_DISABLE_CALLBACK_SERVER: Disables local server, enables mode 3
- META_ACCESS_TOKEN: Direct Meta token (fallback)
- META_ADS_DISABLE_LOGIN_LINK: Hard-disables the get_login_link tool; returns a disabled message
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
from .pipeboard_auth import pipeboard_auth_manager

# Only register the login link tool if not explicitly disabled
ENABLE_LOGIN_LINK = not bool(os.environ.get("META_ADS_DISABLE_LOGIN_LINK", ""))


async def get_login_link(access_token: Optional[str] = None) -> str:
    """
    Get a clickable login link for Meta Ads authentication.
    
    NOTE: This method should only be used if you're using your own Facebook app.
    If using Pipeboard authentication (recommended), set the PIPEBOARD_API_TOKEN
    environment variable instead (token obtainable via https://pipeboard.co).
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
    
    Returns:
        A clickable resource link for Meta authentication
    """
    # Check if we're using pipeboard authentication
    using_pipeboard = bool(os.environ.get("PIPEBOARD_API_TOKEN", ""))
    callback_server_disabled = bool(os.environ.get("META_ADS_DISABLE_CALLBACK_SERVER", ""))
    
    if using_pipeboard:
        # Pipeboard token-based authentication
        try:
            logger.info("Using Pipeboard token-based authentication")
            
            # If an access token was provided, this is likely a test - return success
            if access_token:
                return json.dumps({
                    "message": "✅ Authentication Token Provided",
                    "status": "Using provided access token for authentication",
                    "token_info": f"Token preview: {access_token[:10]}...",
                    "authentication_method": "manual_token",
                    "ready_to_use": "You can now use all Meta Ads MCP tools and commands."
                }, indent=2)
            
            # Check if Pipeboard token is working
            token = pipeboard_auth_manager.get_access_token()
            if token:
                return json.dumps({
                    "message": "✅ Already Authenticated",
                    "status": "You're successfully authenticated with Meta Ads via Pipeboard!",
                    "token_info": f"Token preview: {token[:10]}...",
                    "authentication_method": "pipeboard_token",
                    "ready_to_use": "You can now use all Meta Ads MCP tools and commands."
                }, indent=2)
            
            # Start Pipeboard auth flow
            auth_data = pipeboard_auth_manager.initiate_auth_flow()
            login_url = auth_data.get('loginUrl')
            
            if login_url:
                return json.dumps({
                    "message": "🔗 Click to Authenticate",
                    "login_url": login_url,
                    "markdown_link": f"[🚀 Authenticate with Meta Ads]({login_url})",
                    "instructions": "Click the link above to complete authentication with Meta Ads.",
                    "authentication_method": "pipeboard_oauth",
                    "what_happens_next": "After clicking, you'll be redirected to Meta's authentication page. Once completed, your token will be automatically saved.",
                    "token_duration": "Your token will be valid for approximately 60 days."
                }, indent=2)
            else:
                return json.dumps({
                    "message": "❌ Authentication Error",
                    "error": "Could not generate authentication URL from Pipeboard",
                    "troubleshooting": [
                        "Check that your PIPEBOARD_API_TOKEN is valid",
                        "Ensure the Pipeboard service is accessible",
                        "Try again in a few moments"
                    ],
                    "authentication_method": "pipeboard_oauth_failed"
                }, indent=2)
                
        except Exception as e:
            logger.error(f"Error initiating Pipeboard auth flow: {e}")
            return json.dumps({
                "message": "❌ Pipeboard Authentication Error",
                "error": f"Failed to initiate Pipeboard authentication: {str(e)}",
                "troubleshooting": [
                    "✅ Check that PIPEBOARD_API_TOKEN environment variable is set correctly",
                    "🌐 Verify that pipeboard.co is accessible from your network",
                    "🔄 Try refreshing your Pipeboard API token",
                    "⏰ Wait a moment and try again"
                ],
                "get_help": "Contact support if the issue persists",
                "authentication_method": "pipeboard_error"
            }, indent=2)
    elif callback_server_disabled:
        # Production OAuth flow - use Pipeboard OAuth endpoints directly
        logger.info("Production OAuth flow - using Pipeboard OAuth endpoints")
        
        return json.dumps({
            "message": "🔐 Authentication Required",
            "instructions": "Please sign in to your Pipeboard account to authenticate with Meta Ads.",
            "sign_in_url": "https://pipeboard.co/auth/signin",
            "markdown_link": "[🚀 Sign in to Pipeboard](https://pipeboard.co/auth/signin)",
            "what_to_do": "Click the link above to sign in to your Pipeboard account and complete authentication.",
            "authentication_method": "production_oauth"
        }, indent=2)
    else:
        # Original Meta authentication flow (development/local)
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
                    "🌐 Use Pipeboard authentication: Set PIPEBOARD_API_TOKEN environment variable",
                    "🔑 Use direct token: Set META_ACCESS_TOKEN environment variable", 
                    "🔧 Check if another service is using the required ports"
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