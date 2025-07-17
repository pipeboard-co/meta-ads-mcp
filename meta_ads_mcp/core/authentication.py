"""Authentication-specific functionality for Meta Ads API."""

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
    
    if using_pipeboard:
        # Handle Pipeboard authentication
        # Check if we have a cached token
        cached_token = pipeboard_auth_manager.get_access_token()
        token_status = "No token" if not cached_token else "Valid token"
        
        # If we already have a valid token and none was provided, just return success
        if cached_token and not access_token:
            logger.info("get_login_link called with existing valid Pipeboard token")
            return json.dumps({
                "message": "Already authenticated with Pipeboard",
                "token_status": token_status,
                "token_preview": cached_token[:10] + "..." if cached_token else None,
                "authentication_method": "pipeboard"
            }, indent=2)
        
        # Initiate the auth flow via Pipeboard
        try:
            auth_data = pipeboard_auth_manager.initiate_auth_flow()
            login_url = auth_data.get("loginUrl")
            
            # Return a special format that helps the LLM format the response properly
            response = {
                "login_url": login_url,
                "token_status": token_status,
                "markdown_link": f"[Click here to authenticate with Meta Ads via Pipeboard]({login_url})",
                "message": "IMPORTANT: Please use the Markdown link format in your response to allow the user to click it.",
                "instructions_for_llm": "You must present this link as clickable Markdown to the user using the markdown_link format provided.",
                "authentication_method": "pipeboard",
                "token_duration": "Approximately 60 days",
                "note": "After authenticating, the token will be automatically saved."
            }
            
            return json.dumps(response, indent=2)
        except Exception as e:
            logger.error(f"Error initiating Pipeboard auth flow: {e}")
            return json.dumps({
                "error": f"Failed to initiate Pipeboard authentication: {str(e)}",
                "message": "Please check your PIPEBOARD_API_TOKEN environment variable.",
                "authentication_method": "pipeboard"
            }, indent=2)
    else:
        # Original Meta authentication flow
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