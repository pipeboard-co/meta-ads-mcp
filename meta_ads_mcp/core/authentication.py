"""Authentication-specific functionality for Meta Ads API.

Running this package yourself requires a Meta access token of your own. There are
two ways to get one:

1. **Direct token** (simplest)
   - Set META_ACCESS_TOKEN to a token generated from your own Meta app
   - Takes precedence over every other mechanism

2. **Local OAuth flow** (default when META_ACCESS_TOKEN is unset)
   - Requires META_APP_ID for your own Meta app
   - Uses a local callback server on localhost:8080+ for the OAuth redirect
   - Disabled when META_ADS_DISABLE_CALLBACK_SERVER is set

If you would rather not run a Meta app at all, use the hosted MCP at
https://meta-ads.mcp.pipeboard.co/ and authenticate with a Pipeboard API token.
Pipeboard then calls the Meta API on your behalf and the Meta token is never
exposed to the client.

Note: PIPEBOARD_API_TOKEN is no longer supported. It used to exchange a Pipeboard
API token for the underlying Meta access token, which defeated the scoping on that
API token; the endpoint behind it has been removed.

Environment Variables:
- META_ACCESS_TOKEN: Direct Meta token (highest precedence)
- META_APP_ID / META_APP_SECRET: Your own Meta app, for the local OAuth flow
- META_ADS_DISABLE_CALLBACK_SERVER: Disables the local callback server
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

# Only register the login link tool if not explicitly disabled
ENABLE_LOGIN_LINK = not bool(os.environ.get("META_ADS_DISABLE_LOGIN_LINK", ""))


async def get_login_link(access_token: Optional[str] = None) -> str:
    """
    Get a clickable login link for Meta Ads authentication.
    
    NOTE: This method requires your own Facebook app (META_APP_ID). If you would
    rather not run one, use the hosted MCP at https://meta-ads.mcp.pipeboard.co/
    instead, which authenticates with a Pipeboard API token.

    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
    
    Returns:
        A clickable resource link for Meta authentication
    """
    callback_server_disabled = bool(os.environ.get("META_ADS_DISABLE_CALLBACK_SERVER", ""))

    if callback_server_disabled:
        # No local callback server, so the browser-based OAuth flow is unavailable.
        # Point at the two remaining ways to supply a token.
        logger.info("Callback server disabled - cannot run the local OAuth flow")

        return json.dumps({
            "message": "🔐 Authentication Required",
            "reason": "The local callback server is disabled (META_ADS_DISABLE_CALLBACK_SERVER), so the browser OAuth flow cannot run.",
            "options": [
                {
                    "option": "Use the hosted Meta Ads MCP (recommended)",
                    "url": "https://meta-ads.mcp.pipeboard.co/",
                    "how": "Point your MCP client at this URL and authenticate with your Pipeboard API token. Pipeboard calls the Meta API for you, so no Meta token is needed locally."
                },
                {
                    "option": "Bring your own Meta access token",
                    "url": "https://developers.facebook.com/apps/",
                    "how": "Create your own Meta app, generate an access token, and set META_ACCESS_TOKEN before starting the server."
                }
            ],
            "authentication_method": "callback_server_disabled"
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
                    "🔑 Use direct token: Set META_ACCESS_TOKEN environment variable",
                    "🌐 Use the hosted MCP at https://meta-ads.mcp.pipeboard.co/ with your Pipeboard API token",
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