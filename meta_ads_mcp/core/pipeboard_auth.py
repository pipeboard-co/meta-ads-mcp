"""Authentication with Meta Ads API via pipeboard.co."""

import os
import json
import time
import requests
from pathlib import Path
import platform
from typing import Optional, Dict, Any
from .utils import logger

# Enable more detailed logging
import logging
logger.setLevel(logging.DEBUG)

# Base URL for pipeboard API
PIPEBOARD_API_BASE = "https://pipeboard.co/api"

# Debug message about API base URL
logger.info(f"Pipeboard API base URL: {PIPEBOARD_API_BASE}")

class TokenInfo:
    """Stores token information including expiration"""
    def __init__(self, access_token: str, expires_at: Optional[str] = None, token_type: Optional[str] = None):
        self.access_token = access_token
        self.expires_at = expires_at
        self.token_type = token_type
        self.created_at = int(time.time())
        logger.debug(f"TokenInfo created. Expires at: {expires_at if expires_at else 'Not specified'}")
    
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expires_at:
            logger.debug("No expiration date set for token, assuming not expired")
            return False  # If no expiration is set, assume it's not expired
        
        # Parse ISO 8601 date format to timestamp
        try:
            # Convert the expires_at string to a timestamp
            # Format is like "2023-12-31T23:59:59.999Z" or "2023-12-31T23:59:59.999+00:00"
            from datetime import datetime
            
            # Remove the Z suffix if present and handle +00:00 format
            expires_at_str = self.expires_at
            if expires_at_str.endswith('Z'):
                expires_at_str = expires_at_str[:-1]  # Remove Z
                
            # Handle microseconds if present
            if '.' in expires_at_str:
                datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
            else:
                datetime_format = "%Y-%m-%dT%H:%M:%S"
                
            # Handle timezone offset
            timezone_offset = "+00:00"
            if "+" in expires_at_str:
                expires_at_str, timezone_offset = expires_at_str.split("+")
                timezone_offset = "+" + timezone_offset
            
            # Parse the datetime without timezone info
            expires_datetime = datetime.strptime(expires_at_str, datetime_format)
            
            # Convert to timestamp (assume UTC)
            expires_timestamp = expires_datetime.timestamp()
            current_time = time.time()
            
            # Check if token is expired and log result
            is_expired = current_time > expires_timestamp
            time_diff = expires_timestamp - current_time
            if is_expired:
                logger.debug(f"Token is expired! Current time: {datetime.fromtimestamp(current_time)}, " 
                             f"Expires at: {datetime.fromtimestamp(expires_timestamp)}, "
                             f"Expired {abs(time_diff):.0f} seconds ago")
            else:
                logger.debug(f"Token is still valid. Expires at: {datetime.fromtimestamp(expires_timestamp)}, "
                             f"Time remaining: {time_diff:.0f} seconds")
            
            return is_expired
        except Exception as e:
            logger.error(f"Error parsing expiration date: {e}")
            # Log the actual value to help diagnose format issues
            logger.error(f"Invalid expires_at value: '{self.expires_at}'")
            # Log detailed error information
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False  # If we can't parse the date, assume it's not expired
    
    def serialize(self) -> Dict[str, Any]:
        """Convert to a dictionary for storage"""
        return {
            "access_token": self.access_token,
            "expires_at": self.expires_at,
            "token_type": self.token_type,
            "created_at": self.created_at
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'TokenInfo':
        """Create from a stored dictionary"""
        logger.debug(f"Deserializing token data with keys: {', '.join(data.keys())}")
        if 'expires_at' in data:
            logger.debug(f"Token expires_at from cache: {data['expires_at']}")
        
        token = cls(
            access_token=data.get("access_token", ""),
            expires_at=data.get("expires_at"),
            token_type=data.get("token_type")
        )
        token.created_at = data.get("created_at", int(time.time()))
        return token


class PipeboardAuthManager:
    """Manages authentication with Meta APIs via pipeboard.co"""
    def __init__(self):
        self.api_token = os.environ.get("PIPEBOARD_API_TOKEN", "")
        logger.debug(f"PipeboardAuthManager initialized with API token: {self.api_token[:5]}..." if self.api_token else "No API token")
        if self.api_token:
            logger.info("Pipeboard authentication enabled. Will use pipeboard.co for Meta authentication.")
        else:
            logger.info("Pipeboard authentication not enabled. Set PIPEBOARD_API_TOKEN environment variable to enable.")
        self.token_info = None
        # Note: Token caching is disabled to always fetch fresh tokens from Pipeboard
    
    def _get_token_cache_path(self) -> Path:
        """Get the platform-specific path for token cache file"""
        if platform.system() == "Windows":
            base_path = Path(os.environ.get("APPDATA", ""))
        elif platform.system() == "Darwin":  # macOS
            base_path = Path.home() / "Library" / "Application Support"
        else:  # Assume Linux/Unix
            base_path = Path.home() / ".config"
        
        # Create directory if it doesn't exist
        cache_dir = base_path / "meta-ads-mcp"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_path = cache_dir / "pipeboard_token_cache.json"
        logger.debug(f"Token cache path: {cache_path}")
        return cache_path
    
    def _load_cached_token(self) -> bool:
        """Load token from cache if available"""
        cache_path = self._get_token_cache_path()
        
        if not cache_path.exists():
            logger.debug(f"Token cache file not found at {cache_path}")
            return False
        
        try:
            with open(cache_path, "r") as f:
                logger.debug(f"Reading token cache from {cache_path}")
                data = json.load(f)
                
                # Validate the cached data structure
                required_fields = ["access_token"]
                if not all(field in data for field in required_fields):
                    logger.warning("Cached token data is missing required fields")
                    return False
                
                # Check if the token looks valid (basic format check)
                if not data.get("access_token") or len(data["access_token"]) < 20:
                    logger.warning("Cached token appears malformed")
                    return False
                
                self.token_info = TokenInfo.deserialize(data)
                
                # Log token details (partial token for security)
                masked_token = self.token_info.access_token[:10] + "..." + self.token_info.access_token[-5:] if self.token_info.access_token else "None"
                logger.debug(f"Loaded token: {masked_token}")
                
                # Check if token is expired
                if self.token_info.is_expired():
                    logger.info("Cached token is expired, removing cache file")
                    # Remove the expired cache file
                    try:
                        cache_path.unlink()
                        logger.info(f"Removed expired token cache: {cache_path}")
                    except Exception as e:
                        logger.warning(f"Could not remove expired cache file: {e}")
                    self.token_info = None
                    return False
                
                # Additional validation: check if token is too old (more than 60 days)
                current_time = int(time.time())
                if self.token_info.created_at and (current_time - self.token_info.created_at) > (60 * 24 * 3600):
                    logger.warning("Cached token is too old (more than 60 days), removing cache file")
                    try:
                        cache_path.unlink()
                        logger.info(f"Removed old token cache: {cache_path}")
                    except Exception as e:
                        logger.warning(f"Could not remove old cache file: {e}")
                    self.token_info = None
                    return False
                
                logger.info(f"Loaded cached token (expires at {self.token_info.expires_at})")
                return True
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing token cache file: {e}")
            logger.debug("Token cache file might be corrupted, trying to read raw content")
            try:
                with open(cache_path, "r") as f:
                    raw_content = f.read()
                logger.debug(f"Raw cache file content (first 100 chars): {raw_content[:100]}")
            except Exception as e2:
                logger.error(f"Could not read raw cache file: {e2}")
            # If there's any error reading the cache, try to remove the corrupted file
            try:
                cache_path.unlink()
                logger.info(f"Removed corrupted token cache: {cache_path}")
            except Exception as cleanup_error:
                logger.warning(f"Could not remove corrupted cache file: {cleanup_error}")
            return False
        except Exception as e:
            logger.error(f"Error loading cached token: {e}")
            # If there's any error reading the cache, try to remove the corrupted file
            try:
                cache_path.unlink()
                logger.info(f"Removed corrupted token cache: {cache_path}")
            except Exception as cleanup_error:
                logger.warning(f"Could not remove corrupted cache file: {cleanup_error}")
            return False
    
    def _save_token_to_cache(self) -> None:
        """Save token to cache file"""
        if not self.token_info:
            logger.debug("No token to save to cache")
            return
        
        cache_path = self._get_token_cache_path()
        
        try:
            token_data = self.token_info.serialize()
            logger.debug(f"Saving token to cache. Expires at: {token_data.get('expires_at')}")
            
            with open(cache_path, "w") as f:
                json.dump(token_data, f)
            logger.info(f"Token cached at: {cache_path}")
        except Exception as e:
            logger.error(f"Error saving token to cache: {e}")
    
    def initiate_auth_flow(self) -> Dict[str, str]:
        """
        Initiate the Meta OAuth flow via pipeboard.co
        
        Returns:
            Dict with loginUrl and status info
        """
        if not self.api_token:
            logger.error("No PIPEBOARD_API_TOKEN environment variable set")
            raise ValueError("No PIPEBOARD_API_TOKEN environment variable set")
            
        # Exactly match the format used in meta_auth_test.sh
        url = f"{PIPEBOARD_API_BASE}/meta/auth?api_token={self.api_token}"
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initiating auth flow with POST request to {url}")
        
        try:
            # Make the POST request exactly as in the working meta_auth_test.sh script
            response = requests.post(url, headers=headers)
            logger.info(f"Auth flow response status: {response.status_code}")
            
            # Better error handling
            if response.status_code != 200:
                logger.error(f"Auth flow error: HTTP {response.status_code}")
                error_text = response.text if response.text else "No response content"
                logger.error(f"Response content: {error_text}")
                if response.status_code == 404:
                    raise ValueError(f"Pipeboard API endpoint not found. Check if the server is running at {PIPEBOARD_API_BASE}")
                elif response.status_code == 401:
                    raise ValueError(f"Unauthorized: Invalid API token. Check your PIPEBOARD_API_TOKEN.")
                
                response.raise_for_status()
            
            # Parse the response    
            try:
                data = response.json()
                logger.info(f"Received response keys: {', '.join(data.keys())}")
            except json.JSONDecodeError:
                logger.error(f"Could not parse JSON response: {response.text}")
                raise ValueError(f"Invalid JSON response from auth endpoint: {response.text[:100]}")
            
            # Log auth flow response (without sensitive information)
            if 'loginUrl' in data:
                logger.info(f"Auth flow initiated successfully with login URL: {data['loginUrl'][:30]}...")
            else:
                logger.warning(f"Auth flow response missing loginUrl field. Response keys: {', '.join(data.keys())}")
            
            return data
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Pipeboard: {e}")
            logger.debug(f"Attempting to connect to: {PIPEBOARD_API_BASE}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout connecting to Pipeboard: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating auth flow: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initiating auth flow: {e}")
            raise
    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get the current access token, refreshing if necessary or if forced
        
        Args:
            force_refresh: Force token refresh even if cached token exists
            
        Returns:
            Access token if available, None otherwise
        """
        # First check if API token is configured
        if not self.api_token:
            logger.error("TOKEN VALIDATION FAILED: No Pipeboard API token configured")
            logger.error("Please set PIPEBOARD_API_TOKEN environment variable")
            return None
            
        logger.info("Getting fresh token from Pipeboard (caching disabled)")
        
        # If force refresh or no token/expired token, get a new one from Pipeboard
        try:
            # Make a request to get the token, using the same URL format as initiate_auth_flow
            url = f"{PIPEBOARD_API_BASE}/meta/token?api_token={self.api_token}"
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.info(f"Requesting token from {url}")
            
            # Add timeout for better error messages
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.Timeout:
                logger.error("TOKEN VALIDATION FAILED: Timeout while connecting to Pipeboard API")
                logger.error(f"Could not connect to {PIPEBOARD_API_BASE} within 10 seconds")
                return None
            except requests.exceptions.ConnectionError:
                logger.error("TOKEN VALIDATION FAILED: Connection error with Pipeboard API")
                logger.error(f"Could not connect to {PIPEBOARD_API_BASE} - check if service is running")
                return None
                
            logger.info(f"Token request response status: {response.status_code}")
            
            # Better error handling with response content
            if response.status_code != 200:
                logger.error(f"TOKEN VALIDATION FAILED: HTTP error {response.status_code}")
                error_text = response.text if response.text else "No response content"
                logger.error(f"Response content: {error_text}")
                
                # Add more specific error messages for common status codes
                if response.status_code == 401:
                    logger.error("Authentication failed: Invalid Pipeboard API token")
                elif response.status_code == 404:
                    logger.error("Endpoint not found: Check if Pipeboard API service is running correctly")
                elif response.status_code == 400:
                    logger.error("Bad request: The request to Pipeboard API was malformed")
                    
                response.raise_for_status()
                
            try:
                data = response.json()
                logger.info(f"Received token response with keys: {', '.join(data.keys())}")
            except json.JSONDecodeError:
                logger.error("TOKEN VALIDATION FAILED: Invalid JSON response from Pipeboard API")
                logger.error(f"Response content (first 100 chars): {response.text[:100]}")
                return None
            
            # Validate response data
            if "access_token" not in data:
                logger.error("TOKEN VALIDATION FAILED: No access_token in Pipeboard API response")
                logger.error(f"Response keys: {', '.join(data.keys())}")
                if "error" in data:
                    logger.error(f"Error details: {data['error']}")
                else:
                    logger.error("No error information available in response")
                return None
                
            # Create new token info
            self.token_info = TokenInfo(
                access_token=data.get("access_token"),
                expires_at=data.get("expires_at"),
                token_type=data.get("token_type", "bearer")
            )
            
            # Note: Token caching is disabled
            
            masked_token = self.token_info.access_token[:10] + "..." + self.token_info.access_token[-5:] if self.token_info.access_token else "None"
            logger.info(f"Successfully retrieved access token: {masked_token}")
            return self.token_info.access_token
        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
            response_text = e.response.text if hasattr(e, 'response') and e.response else "No response"
            
            if status_code == 401:
                logger.error(f"Unauthorized: Check your PIPEBOARD_API_TOKEN. Response: {response_text}")
            elif status_code == 404:
                logger.error(f"No token available: You might need to complete authorization first. Response: {response_text}")
                # Return None so caller can handle the auth flow
                return None
            else:
                logger.error(f"Error getting access token (status {status_code}): {e}")
                logger.error(f"Response content: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting access token: {e}")
            return None
        
    def invalidate_token(self) -> None:
        """Invalidate the current token, usually because it has expired or is invalid"""
        if self.token_info:
            logger.info(f"Invalidating token: {self.token_info.access_token[:10]}...")
            self.token_info = None
            
            # Remove the cached token file
            try:
                cache_path = self._get_token_cache_path()
                if cache_path.exists():
                    os.remove(cache_path)
                    logger.info(f"Removed cached token file: {cache_path}")
                else:
                    logger.debug(f"No token cache file to remove: {cache_path}")
            except Exception as e:
                logger.error(f"Error removing cached token file: {e}")
        else:
            logger.debug("No token to invalidate")

    def test_token_validity(self) -> bool:
        """
        Test if the current token is valid with the Meta Graph API
        
        Returns:
            True if valid, False otherwise
        """
        if not self.token_info or not self.token_info.access_token:
            logger.debug("No token to test")
            logger.error("TOKEN VALIDATION FAILED: Missing token to test")
            return False
            
        # Log token details for debugging (partial token for security)
        masked_token = self.token_info.access_token[:5] + "..." + self.token_info.access_token[-5:] if self.token_info.access_token else "None"
        token_type = self.token_info.token_type if hasattr(self.token_info, 'token_type') and self.token_info.token_type else "bearer"
        logger.debug(f"Testing token validity (token: {masked_token}, type: {token_type})")
            
        try:
            # Make a simple request to the /me endpoint to test the token
            META_GRAPH_API_VERSION = "v22.0"
            url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/me"
            headers = {"Authorization": f"Bearer {self.token_info.access_token}"}
            
            logger.debug(f"Testing token validity with request to {url}")
            
            # Add timeout and better error handling
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.Timeout:
                logger.error("TOKEN VALIDATION FAILED: Timeout while connecting to Meta API")
                logger.error("The Graph API did not respond within 10 seconds")
                return False
            except requests.exceptions.ConnectionError:
                logger.error("TOKEN VALIDATION FAILED: Connection error with Meta API")
                logger.error("Could not establish connection to Graph API - check network connectivity")
                return False
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Token is valid. User ID: {data.get('id')}")
                # Add more useful user information for debugging
                user_info = f"User ID: {data.get('id')}"
                if 'name' in data:
                    user_info += f", Name: {data.get('name')}"
                logger.info(f"Meta API token validated successfully ({user_info})")
                return True
            else:
                logger.error(f"TOKEN VALIDATION FAILED: API returned status {response.status_code}")
                
                # Try to parse the error response for more detailed information
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_obj = error_data.get('error', {})
                        error_code = error_obj.get('code', 'unknown')
                        error_message = error_obj.get('message', 'Unknown error')
                        logger.error(f"Meta API error: Code {error_code} - {error_message}")
                        
                        # Add specific guidance for common error codes
                        if error_code == 190:
                            logger.error("Error indicates the token is invalid or has expired")
                        elif error_code == 4:
                            logger.error("Error indicates rate limiting - too many requests")
                        elif error_code == 200:
                            logger.error("Error indicates API permissions or configuration issue")
                    else:
                        logger.error(f"No error object in response: {error_data}")
                except json.JSONDecodeError:
                    logger.error(f"Could not parse error response: {response.text[:200]}")
                
                return False
        except Exception as e:
            logger.error(f"TOKEN VALIDATION FAILED: Unexpected error: {str(e)}")
            
            # Add stack trace for debugging complex issues
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
            return False


# Create singleton instance
pipeboard_auth_manager = PipeboardAuthManager() 