"""Core API functionality for Meta Ads API."""

from typing import Any, Dict, Optional, Callable
import json
import httpx
import asyncio
import functools
import os
from . import auth
from .auth import needs_authentication, auth_manager, start_callback_server, shutdown_callback_server
from .utils import logger

# Constants
META_GRAPH_API_VERSION = "v22.0"
META_GRAPH_API_BASE = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}"
USER_AGENT = "meta-ads-mcp/1.0"

# Log key environment and configuration at startup
logger.info("Core API module initialized")
logger.info(f"Graph API Version: {META_GRAPH_API_VERSION}")
logger.info(f"META_APP_ID env var present: {'Yes' if os.environ.get('META_APP_ID') else 'No'}")

class GraphAPIError(Exception):
    """Exception raised for errors from the Graph API."""
    def __init__(self, error_data: Dict[str, Any]):
        self.error_data = error_data
        self.message = error_data.get('message', 'Unknown Graph API error')
        super().__init__(self.message)
        
        # Log error details
        logger.error(f"Graph API Error: {self.message}")
        logger.debug(f"Error details: {error_data}")
        
        # Check if this is an auth error
        if "code" in error_data and error_data["code"] in [190, 102, 4]:
            # Common auth error codes
            logger.warning(f"Auth error detected (code: {error_data['code']}). Invalidating token.")
            auth_manager.invalidate_token()


async def make_api_request(
    endpoint: str,
    access_token: str,
    params: Optional[Dict[str, Any]] = None,
    method: str = "GET"
) -> Dict[str, Any]:
    """
    Make a request to the Meta Graph API.
    
    Args:
        endpoint: API endpoint path (without base URL)
        access_token: Meta API access token
        params: Additional query parameters
        method: HTTP method (GET, POST, DELETE)
    
    Returns:
        API response as a dictionary
    """
    # Validate access token before proceeding
    if not access_token:
        logger.error("API request attempted with blank access token")
        return {
            "error": {
                "message": "Authentication Required",
                "details": "A valid access token is required to access the Meta API",
                "action_required": "Please authenticate first"
            }
        }
        
    url = f"{META_GRAPH_API_BASE}/{endpoint}"
    
    headers = {
        "User-Agent": USER_AGENT,
    }
    
    request_params = params or {}
    request_params["access_token"] = access_token
    
    # Logging the request (masking token for security)
    masked_params = {k: "***TOKEN***" if k == "access_token" else v for k, v in request_params.items()}
    logger.debug(f"API Request: {method} {url}")
    logger.debug(f"Request params: {masked_params}")
    
    # Check for app_id in params
    app_id = auth_manager.app_id
    logger.debug(f"Current app_id from auth_manager: {app_id}")
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                # For GET, JSON-encode dict/list params (e.g., targeting_spec) to proper strings
                encoded_params = {}
                for key, value in request_params.items():
                    if isinstance(value, (dict, list)):
                        encoded_params[key] = json.dumps(value)
                    else:
                        encoded_params[key] = value
                response = await client.get(url, params=encoded_params, headers=headers, timeout=30.0)
            elif method == "POST":
                # For Meta API, POST requests need data, not JSON
                if 'targeting' in request_params and isinstance(request_params['targeting'], dict):
                    # Convert targeting dict to string for the API
                    request_params['targeting'] = json.dumps(request_params['targeting'])
                
                # Convert lists and dicts to JSON strings    
                for key, value in request_params.items():
                    if isinstance(value, (list, dict)):
                        request_params[key] = json.dumps(value)
                
                logger.debug(f"POST params (prepared): {masked_params}")
                response = await client.post(url, data=request_params, headers=headers, timeout=30.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request_params, headers=headers, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            logger.debug(f"API Response status: {response.status_code}")
            
            # Ensure the response is JSON and return it as a dictionary
            try:
                return response.json()
            except json.JSONDecodeError:
                # If not JSON, return text content in a structured format
                return {
                    "text_response": response.text,
                    "status_code": response.status_code
                }
        
        except httpx.HTTPStatusError as e:
            error_info = {}
            try:
                error_info = e.response.json()
            except:
                error_info = {"status_code": e.response.status_code, "text": e.response.text}
            
            logger.error(f"HTTP Error: {e.response.status_code} - {error_info}")
            
            # Check for authentication errors
            if e.response.status_code == 401 or e.response.status_code == 403:
                logger.warning("Detected authentication error (401/403)")
                auth_manager.invalidate_token()
            elif "error" in error_info:
                error_obj = error_info.get("error", {})
                # Check for specific FB API errors related to auth
                if isinstance(error_obj, dict) and error_obj.get("code") in [190, 102, 4, 200, 10]:
                    logger.warning(f"Detected Facebook API auth error: {error_obj.get('code')}")
                    # Log more details about app ID related errors
                    if error_obj.get("code") == 200 and "Provide valid app ID" in error_obj.get("message", ""):
                        logger.error("Meta API authentication configuration issue")
                        logger.error(f"Current app_id: {app_id}")
                        # Provide a clearer error message without the confusing "Provide valid app ID" message
                        return {
                            "error": {
                                "message": "Meta API authentication configuration issue. Please check your app credentials.",
                                "original_error": error_obj.get("message"),
                                "code": error_obj.get("code")
                            }
                        }
                    auth_manager.invalidate_token()
            
            # Include full details for technical users
            full_response = {
                "headers": dict(e.response.headers),
                "status_code": e.response.status_code,
                "url": str(e.response.url),
                "reason": getattr(e.response, "reason_phrase", "Unknown reason"),
                "request_method": e.request.method,
                "request_url": str(e.request.url)
            }
            
            # Return a properly structured error object
            return {
                "error": {
                    "message": f"HTTP Error: {e.response.status_code}",
                    "details": error_info,
                    "full_response": full_response
                }
            }
        
        except Exception as e:
            logger.error(f"Request Error: {str(e)}")
            return {"error": {"message": str(e)}}


# Generic wrapper for all Meta API tools
def meta_api_tool(func):
    """Decorator for Meta API tools that handles authentication and error handling."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Log function call
            logger.debug(f"Function call: {func.__name__}")
            logger.debug(f"Args: {args}")
            # Log kwargs without sensitive info
            safe_kwargs = {k: ('***TOKEN***' if k == 'access_token' else v) for k, v in kwargs.items()}
            logger.debug(f"Kwargs: {safe_kwargs}")
            
            # Log app ID information
            app_id = auth_manager.app_id
            logger.debug(f"Current app_id: {app_id}")
            logger.debug(f"META_APP_ID env var: {os.environ.get('META_APP_ID')}")
            
            # If access_token is not in kwargs or not kwargs['access_token'], try to get it from auth_manager
            if 'access_token' not in kwargs or not kwargs['access_token']:
                try:
                    access_token = await auth.get_current_access_token()
                    if access_token:
                        kwargs['access_token'] = access_token
                        logger.debug("Using access token from auth_manager")
                    else:
                        logger.warning("No access token available from auth_manager")
                        # Add more details about why token might be missing
                        if (auth_manager.app_id == "YOUR_META_APP_ID" or not auth_manager.app_id) and not auth_manager.use_pipeboard:
                            logger.error("TOKEN VALIDATION FAILED: No valid app_id configured")
                            logger.error("Please set META_APP_ID environment variable or configure in your code")
                        elif auth_manager.use_pipeboard:
                            logger.error("TOKEN VALIDATION FAILED: Pipeboard authentication enabled but no valid token available")
                            logger.error("Complete authentication via Pipeboard service or check PIPEBOARD_API_TOKEN")
                        else:
                            logger.error("Check logs above for detailed token validation failures")
                except Exception as e:
                    logger.error(f"Error getting access token: {str(e)}")
                    # Add stack trace for better debugging
                    import traceback
                    logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Final validation - if we still don't have a valid token, return authentication required
            if 'access_token' not in kwargs or not kwargs['access_token']:
                logger.warning("No access token available, authentication needed")
                
                # Add more specific troubleshooting information
                auth_url = auth_manager.get_auth_url()
                app_id = auth_manager.app_id
                using_pipeboard = auth_manager.use_pipeboard
                
                logger.error("TOKEN VALIDATION SUMMARY:")
                logger.error(f"- Current app_id: '{app_id}'")
                logger.error(f"- Environment META_APP_ID: '{os.environ.get('META_APP_ID', 'Not set')}'")
                logger.error(f"- Pipeboard API token configured: {'Yes' if os.environ.get('PIPEBOARD_API_TOKEN') else 'No'}")
                logger.error(f"- Using Pipeboard authentication: {'Yes' if using_pipeboard else 'No'}")
                
                # Check for common configuration issues - but only if not using Pipeboard
                if not using_pipeboard and (app_id == "YOUR_META_APP_ID" or not app_id):
                    logger.error("ISSUE DETECTED: No valid Meta App ID configured")
                    logger.error("ACTION REQUIRED: Set META_APP_ID environment variable with a valid App ID")
                elif using_pipeboard:
                    logger.error("ISSUE DETECTED: Pipeboard authentication configured but no valid token available")
                    logger.error("ACTION REQUIRED: Complete authentication via Pipeboard service")
                
                # Provide different guidance based on authentication method
                if using_pipeboard:
                    return json.dumps({
                        "error": {
                            "message": "Pipeboard Authentication Required",
                            "details": {
                                "description": "Your Pipeboard API token is invalid or has expired",
                                "action_required": "Update your Pipeboard token",
                                "setup_url": "https://pipeboard.co/setup",
                                "token_url": "https://pipeboard.co/api-tokens",
                                "configuration_status": {
                                    "app_id_configured": bool(app_id) and app_id != "YOUR_META_APP_ID",
                                    "pipeboard_enabled": True,
                                },
                                "troubleshooting": "Go to https://pipeboard.co/setup to verify your account setup, then visit https://pipeboard.co/api-tokens to obtain a new API token",
                                "setup_link": "[Verify your Pipeboard account setup](https://pipeboard.co/setup)",
                                "token_link": "[Get a new Pipeboard API token](https://pipeboard.co/api-tokens)"
                            }
                        }
                    }, indent=2)
                else:
                    return json.dumps({
                        "error": {
                            "message": "Authentication Required",
                            "details": {
                                "description": "You need to authenticate with the Meta API before using this tool",
                                "action_required": "Please authenticate first",
                                "auth_url": auth_url,
                                "configuration_status": {
                                    "app_id_configured": bool(app_id) and app_id != "YOUR_META_APP_ID",
                                    "pipeboard_enabled": False,
                                },
                                "troubleshooting": "Check logs for TOKEN VALIDATION FAILED messages",
                                "markdown_link": f"[Click here to authenticate with Meta Ads API]({auth_url})"
                            }
                        }
                    }, indent=2)
                
            # Call the original function
            result = await func(*args, **kwargs)
            
            # If the result is a string (JSON), try to parse it to check for errors
            if isinstance(result, str):
                try:
                    result_dict = json.loads(result)
                    if "error" in result_dict:
                        logger.error(f"Error in API response: {result_dict['error']}")
                        # If this is an app ID error, log more details
                        if isinstance(result_dict.get("details", {}).get("error", {}), dict):
                            error_obj = result_dict["details"]["error"]
                            if error_obj.get("code") == 200 and "Provide valid app ID" in error_obj.get("message", ""):
                                logger.error("Meta API authentication configuration issue")
                                logger.error(f"Current app_id: {app_id}")
                                # Replace the confusing error with a more user-friendly one
                                return json.dumps({
                                    "error": {
                                        "message": "Meta API Configuration Issue",
                                        "details": {
                                            "description": "Your Meta API app is not properly configured",
                                            "action_required": "Check your META_APP_ID environment variable",
                                            "current_app_id": app_id,
                                            "original_error": error_obj.get("message")
                                        }
                                    }
                                }, indent=2)
                except Exception:
                    # Not JSON or other parsing error, wrap it in a dictionary
                    return json.dumps({"data": result}, indent=2)
            
            # If result is already a dictionary, ensure it's properly serialized
            if isinstance(result, dict):
                return json.dumps(result, indent=2)
            
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2)
    
    return wrapper 