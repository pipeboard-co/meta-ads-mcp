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
"""

import json
import asyncio
import os
from .api import meta_api_tool
from .auth import start_callback_server, shutdown_callback_server, auth_manager, get_current_access_token
from .server import mcp_server
from .utils import logger, META_APP_SECRET
from .pipeboard_auth import pipeboard_auth_manager


@mcp_server.tool()
async def get_login_link(access_token: str = None) -> str:
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
                    "message": "Manual token provided",
                    "token_status": "Provided token",
                    "authentication_method": "manual_token"
                }, indent=2)
            
            # Check if Pipeboard token is working
            token = pipeboard_auth_manager.get_access_token()
            if token:
                return json.dumps({
                    "message": "Already authenticated via Pipeboard",
                    "token_status": "Valid Pipeboard token",
                    "authentication_method": "pipeboard_token"
                }, indent=2)
            
            # Start Pipeboard auth flow
            auth_data = pipeboard_auth_manager.initiate_auth_flow()
            login_url = auth_data.get('loginUrl')
            
            if login_url:
                return json.dumps({
                    "login_url": login_url,
                    "markdown_link": f"[Click here to authenticate with Meta Ads via Pipeboard]({login_url})",
                    "message": "IMPORTANT: Please use the Markdown link format in your response to allow the user to click it.",
                    "instructions_for_llm": "You must present this link as clickable Markdown to the user using the markdown_link format provided.",
                    "authentication_method": "pipeboard_oauth",
                    "note": "After authenticating, the token will be automatically retrieved from Pipeboard."
                }, indent=2)
            else:
                return json.dumps({
                    "error": "No login URL received from Pipeboard",
                    "authentication_method": "pipeboard_oauth_failed"
                }, indent=2)
                
        except Exception as e:
            logger.error(f"Error initiating Pipeboard auth flow: {e}")
            return json.dumps({
                "error": f"Failed to initiate Pipeboard authentication: {str(e)}",
                "message": "Please check your PIPEBOARD_API_TOKEN environment variable.",
                "authentication_method": "pipeboard"
            }, indent=2)
    elif callback_server_disabled:
        # Production OAuth flow - use Pipeboard OAuth endpoints directly
        logger.info("Production OAuth flow - using Pipeboard OAuth endpoints")
        
        return json.dumps({
            "authorization_endpoint": "https://pipeboard.co/oauth/authorize", 
            "token_endpoint": "https://pipeboard.co/oauth/token",
            "registration_endpoint": "https://pipeboard.co/oauth/register",
            "discovery_endpoint": "/.well-known/oauth-authorization-server",
            "message": "Production OAuth flow - use dynamic client registration",
            "instructions": "MCP clients should use the OAuth discovery endpoint to get authorization URLs",
            "authentication_method": "production_oauth",
            "note": "For manual authentication, clients need to register with Pipeboard OAuth service first"
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
                "message": "Already authenticated",
                "token_status": token_status,
                "token_preview": cached_token[:10] + "...",
                "created_at": auth_manager.token_info.created_at if hasattr(auth_manager, "token_info") else None,
                "expires_in": auth_manager.token_info.expires_in if hasattr(auth_manager, "token_info") else None,
                "authentication_method": "meta_oauth"
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
                "error": "Callback server disabled",
                "message": str(e),
                "suggestion": "Use Pipeboard authentication (set PIPEBOARD_API_TOKEN) or provide a direct access token",
                "authentication_method": "meta_oauth_disabled"
            }, indent=2)
        
        # Check if we can exchange for long-lived tokens
        token_exchange_supported = bool(META_APP_SECRET)
        token_duration = "60 days" if token_exchange_supported else "1-2 hours"
        
        # Return a special format that helps the LLM format the response properly
        response = {
            "login_url": login_url,
            "token_status": token_status,
            "server_status": f"Callback server running on port {port}",
            "markdown_link": f"[Click here to authenticate with Meta Ads]({login_url})",
            "message": "IMPORTANT: Please use the Markdown link format in your response to allow the user to click it.",
            "instructions_for_llm": "You must present this link as clickable Markdown to the user using the markdown_link format provided.",
            "token_exchange": "enabled" if token_exchange_supported else "disabled",
            "token_duration": token_duration,
            "authentication_method": "meta_oauth",
            "token_exchange_message": f"Your authentication token will be valid for approximately {token_duration}." + 
                                    (" Long-lived token exchange is enabled." if token_exchange_supported else 
                                    " For direct Meta authentication, long-lived tokens require META_APP_SECRET. Consider using Pipeboard authentication instead (60-day tokens by default)."),
            "note": "After authenticating, the token will be automatically saved."
        }
        
        # Wait a moment to ensure the server is fully started
        await asyncio.sleep(1)
        
        return json.dumps(response, indent=2) 