"""Authentication related functionality for Meta Ads API."""

from typing import Any, Dict, Optional
import time
import platform
import pathlib
import os
import webbrowser
import asyncio
import json
from .utils import logger
import requests

# Import from the new callback server module
from .callback_server import (
    start_callback_server,
    shutdown_callback_server,
    token_container,
    callback_server_port
)

# Import the new Pipeboard authentication
from .pipeboard_auth import pipeboard_auth_manager

# Auth constants
# Scope includes pages_show_list and pages_read_engagement to fix issue #16
# where get_account_pages failed for regular users due to missing page permissions
AUTH_SCOPE = "business_management,public_profile,pages_show_list,pages_read_engagement"
AUTH_REDIRECT_URI = "http://localhost:8888/callback"
AUTH_RESPONSE_TYPE = "token"

# Log important configuration information
logger.info("Authentication module initialized")
logger.info(f"Auth scope: {AUTH_SCOPE}")
logger.info(f"Default redirect URI: {AUTH_REDIRECT_URI}")

# Global flag for authentication state
needs_authentication = False

# Meta configuration singleton
class MetaConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            logger.debug("Creating new MetaConfig instance")
            cls._instance = super(MetaConfig, cls).__new__(cls)
            cls._instance.app_id = os.environ.get("META_APP_ID", "779761636818489")
            logger.info(f"MetaConfig initialized with app_id from env/default: {cls._instance.app_id}")
        return cls._instance
    
    def set_app_id(self, app_id):
        """Set the Meta App ID for API calls"""
        logger.info(f"Setting Meta App ID: {app_id}")
        self.app_id = app_id
        # Also update environment variable for modules that might read directly from it
        os.environ["META_APP_ID"] = app_id
        logger.debug(f"Updated META_APP_ID environment variable: {os.environ.get('META_APP_ID')}")
    
    def get_app_id(self):
        """Get the current Meta App ID"""
        # Check if we have one set
        if hasattr(self, 'app_id') and self.app_id:
            logger.debug(f"Using app_id from instance: {self.app_id}")
            return self.app_id
        
        # If not, try environment variable
        env_app_id = os.environ.get("META_APP_ID", "")
        if env_app_id:
            logger.debug(f"Using app_id from environment: {env_app_id}")
            # Update our instance for future use
            self.app_id = env_app_id
            return env_app_id
        
        logger.warning("No app_id found in instance or environment variables")
        return ""
    
    def is_configured(self):
        """Check if the Meta configuration is complete"""
        app_id = self.get_app_id()
        configured = bool(app_id)
        logger.debug(f"MetaConfig.is_configured() = {configured} (app_id: {app_id})")
        return configured

# Create singleton instance
meta_config = MetaConfig()

class TokenInfo:
    """Stores token information including expiration"""
    def __init__(self, access_token: str, expires_in: Optional[int] = None, user_id: Optional[str] = None):
        self.access_token = access_token
        self.expires_in = expires_in
        self.user_id = user_id
        self.created_at = int(time.time())
        logger.debug(f"TokenInfo created. Expires in: {expires_in if expires_in else 'Not specified'}")
    
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expires_in:
            return False  # If no expiration is set, assume it's not expired
        
        current_time = int(time.time())
        return current_time > (self.created_at + self.expires_in)
    
    def serialize(self) -> Dict[str, Any]:
        """Convert to a dictionary for storage"""
        return {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "user_id": self.user_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'TokenInfo':
        """Create from a stored dictionary"""
        token = cls(
            access_token=data.get("access_token", ""),
            expires_in=data.get("expires_in"),
            user_id=data.get("user_id")
        )
        token.created_at = data.get("created_at", int(time.time()))
        return token


class AuthManager:
    """Manages authentication with Meta APIs"""
    def __init__(self, app_id: str, redirect_uri: str = AUTH_REDIRECT_URI):
        self.app_id = app_id
        self.redirect_uri = redirect_uri
        self.token_info = None
        # Check for Pipeboard token first
        self.use_pipeboard = bool(os.environ.get("PIPEBOARD_API_TOKEN", ""))
        if not self.use_pipeboard:
            self._load_cached_token()
    
    def _get_token_cache_path(self) -> pathlib.Path:
        """Get the platform-specific path for token cache file"""
        if platform.system() == "Windows":
            base_path = pathlib.Path(os.environ.get("APPDATA", ""))
        elif platform.system() == "Darwin":  # macOS
            base_path = pathlib.Path.home() / "Library" / "Application Support"
        else:  # Assume Linux/Unix
            base_path = pathlib.Path.home() / ".config"
        
        # Create directory if it doesn't exist
        cache_dir = base_path / "meta-ads-mcp"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        return cache_dir / "token_cache.json"
    
    def _load_cached_token(self) -> bool:
        """Load token from cache if available"""
        cache_path = self._get_token_cache_path()
        
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
                
                # Validate the cached data structure
                required_fields = ["access_token", "created_at"]
                if not all(field in data for field in required_fields):
                    logger.warning("Cached token data is missing required fields")
                    return False
                
                # Check if the token looks valid (basic format check)
                if not data.get("access_token") or len(data["access_token"]) < 20:
                    logger.warning("Cached token appears malformed")
                    return False
                
                self.token_info = TokenInfo.deserialize(data)
                
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
                
                logger.info(f"Loaded cached token (expires in {(self.token_info.created_at + self.token_info.expires_in) - int(time.time())} seconds)")
                return True
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
            return
        
        cache_path = self._get_token_cache_path()
        
        try:
            with open(cache_path, "w") as f:
                json.dump(self.token_info.serialize(), f)
            logger.info(f"Token cached at: {cache_path}")
        except Exception as e:
            logger.error(f"Error saving token to cache: {e}")
    
    def get_auth_url(self) -> str:
        """Generate the Facebook OAuth URL for desktop app flow"""
        return (
            f"https://www.facebook.com/v22.0/dialog/oauth?"
            f"client_id={self.app_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope={AUTH_SCOPE}&"
            f"response_type={AUTH_RESPONSE_TYPE}"
        )
    
    def authenticate(self, force_refresh: bool = False) -> Optional[str]:
        """
        Authenticate with Meta APIs
        
        Args:
            force_refresh: Force token refresh even if cached token exists
            
        Returns:
            Access token if successful, None otherwise
        """
        # If Pipeboard auth is available, use that instead
        if self.use_pipeboard:
            logger.info("Using Pipeboard authentication")
            return pipeboard_auth_manager.get_access_token(force_refresh=force_refresh)
        
        # Otherwise, use the original OAuth flow
        # Check if we already have a valid token
        if not force_refresh and self.token_info and not self.token_info.is_expired():
            return self.token_info.access_token
        
        # Start the callback server if not already running
        try:
            port = start_callback_server()
            
            # Update redirect URI with the actual port
            self.redirect_uri = f"http://localhost:{port}/callback"
            
            # Generate the auth URL
            auth_url = self.get_auth_url()
            
            # Open browser with auth URL
            logger.info(f"Opening browser with URL: {auth_url}")
            webbrowser.open(auth_url)
            
            # We don't wait for the token here anymore
            # The token will be processed by the callback server
            # Just return None to indicate we've started the flow
            return None
        except Exception as e:
            logger.error(f"Failed to start callback server: {e}")
            logger.info("Callback server disabled. OAuth authentication flow cannot be used.")
            return None
    
    def get_access_token(self) -> Optional[str]:
        """
        Get the current access token, refreshing if necessary
        
        Returns:
            Access token if available, None otherwise
        """
        # If using Pipeboard, always delegate to the Pipeboard auth manager
        if self.use_pipeboard:
            return pipeboard_auth_manager.get_access_token()
            
        if not self.token_info or self.token_info.is_expired():
            return None
        
        return self.token_info.access_token
        
    def invalidate_token(self) -> None:
        """Invalidate the current token, usually because it has expired or is invalid"""
        # If using Pipeboard, delegate to the Pipeboard auth manager
        if self.use_pipeboard:
            pipeboard_auth_manager.invalidate_token()
            return
            
        if self.token_info:
            logger.info(f"Invalidating token: {self.token_info.access_token[:10]}...")
            self.token_info = None
            
            # Signal that authentication is needed
            global needs_authentication
            needs_authentication = True
            
            # Remove the cached token file
            try:
                cache_path = self._get_token_cache_path()
                if cache_path.exists():
                    os.remove(cache_path)
                    logger.info(f"Removed cached token file: {cache_path}")
            except Exception as e:
                logger.error(f"Error removing cached token file: {e}")
    
    def clear_token(self) -> None:
        """Alias for invalidate_token for consistency with other APIs"""
        self.invalidate_token()


def process_token_response(token_container):
    """Process the token response from Facebook."""
    global needs_authentication, auth_manager
    
    if token_container and token_container.get('token'):
        logger.info("Processing token response from Facebook OAuth")
        
        # Exchange the short-lived token for a long-lived token
        short_lived_token = token_container['token']
        long_lived_token_info = exchange_token_for_long_lived(short_lived_token)
        
        if long_lived_token_info:
            logger.info(f"Successfully exchanged for long-lived token (expires in {long_lived_token_info.expires_in} seconds)")
            
            try:
                auth_manager.token_info = long_lived_token_info
                logger.info(f"Long-lived token info set in auth_manager, expires in {long_lived_token_info.expires_in} seconds")
            except NameError:
                logger.error("auth_manager not defined when trying to process token")
                
            try:
                logger.info("Attempting to save long-lived token to cache")
                auth_manager._save_token_to_cache()
                logger.info(f"Long-lived token successfully saved to cache at {auth_manager._get_token_cache_path()}")
            except Exception as e:
                logger.error(f"Error saving token to cache: {e}")
                
            needs_authentication = False
            return True
        else:
            # Fall back to the short-lived token if exchange fails
            logger.warning("Failed to exchange for long-lived token, using short-lived token instead")
            token_info = TokenInfo(
                access_token=short_lived_token,
                expires_in=token_container.get('expires_in', 0)
            )
            
            try:
                auth_manager.token_info = token_info
                logger.info(f"Short-lived token info set in auth_manager, expires in {token_info.expires_in} seconds")
            except NameError:
                logger.error("auth_manager not defined when trying to process token")
                
            try:
                logger.info("Attempting to save token to cache")
                auth_manager._save_token_to_cache()
                logger.info(f"Token successfully saved to cache at {auth_manager._get_token_cache_path()}")
            except Exception as e:
                logger.error(f"Error saving token to cache: {e}")
                
            needs_authentication = False
            return True
    else:
        logger.warning("Received empty token in process_token_response")
        needs_authentication = True
        return False


def exchange_token_for_long_lived(short_lived_token):
    """
    Exchange a short-lived token for a long-lived token (60 days validity).
    
    Args:
        short_lived_token: The short-lived access token received from OAuth flow
        
    Returns:
        TokenInfo object with the long-lived token, or None if exchange failed
    """
    logger.info("Attempting to exchange short-lived token for long-lived token")
    
    try:
        # Get the app ID from the configuration
        app_id = meta_config.get_app_id()
        
        # Get the app secret - this should be securely stored
        app_secret = os.environ.get("META_APP_SECRET", "")
        
        if not app_id or not app_secret:
            logger.error("Missing app_id or app_secret for token exchange")
            return None
            
        # Make the API request to exchange the token
        url = "https://graph.facebook.com/v22.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_lived_token
        }
        
        logger.debug(f"Making token exchange request to {url}")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Token exchange response: {data}")
            
            # Create TokenInfo from the response
            # The response includes access_token and expires_in (in seconds)
            new_token = data.get("access_token")
            expires_in = data.get("expires_in")
            
            if new_token:
                logger.info(f"Received long-lived token, expires in {expires_in} seconds (~{expires_in//86400} days)")
                return TokenInfo(
                    access_token=new_token,
                    expires_in=expires_in
                )
            else:
                logger.error("No access_token in exchange response")
                return None
        else:
            logger.error(f"Token exchange failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error exchanging token: {e}")
        return None


async def get_current_access_token() -> Optional[str]:
    """Get the current access token from auth manager"""
    # Check for environment variable first - this takes highest precedence
    env_token = os.environ.get("META_ACCESS_TOKEN")
    if env_token:
        logger.debug("Using access token from META_ACCESS_TOKEN environment variable")
        # Basic validation
        if len(env_token) < 20:  # Most Meta tokens are much longer
            logger.error(f"TOKEN VALIDATION FAILED: Token from environment variable appears malformed (length: {len(env_token)})")
            return None
        return env_token
        
    # Use the singleton auth manager
    global auth_manager
    
    # Log the function call and current app ID
    logger.debug("get_current_access_token() called")
    app_id = meta_config.get_app_id()
    logger.debug(f"Current app_id: {app_id}")
    
    # Check if using Pipeboard authentication
    using_pipeboard = auth_manager.use_pipeboard
    
    # Check if app_id is valid - but only if not using Pipeboard authentication
    if not app_id and not using_pipeboard:
        logger.error("TOKEN VALIDATION FAILED: No valid app_id configured")
        logger.error("Please set META_APP_ID environment variable or configure via meta_config.set_app_id()")
        return None
    
    # Attempt to get access token
    try:
        token = auth_manager.get_access_token()
        
        if token:
            # Add basic token validation - check if it looks like a valid token
            if len(token) < 20:  # Most Meta tokens are much longer
                logger.error(f"TOKEN VALIDATION FAILED: Token appears malformed (length: {len(token)})")
                auth_manager.invalidate_token()
                return None
                
            logger.debug(f"Access token found in auth_manager (starts with: {token[:10]}...)")
            return token
        else:
            logger.warning("No valid access token available in auth_manager")
            
            # Check why token might be missing
            if hasattr(auth_manager, 'token_info') and auth_manager.token_info:
                if auth_manager.token_info.is_expired():
                    logger.error("TOKEN VALIDATION FAILED: Token is expired")
                    # Add expiration details
                    if hasattr(auth_manager.token_info, 'expires_in') and auth_manager.token_info.expires_in:
                        expiry_time = auth_manager.token_info.created_at + auth_manager.token_info.expires_in
                        current_time = int(time.time())
                        expired_seconds_ago = current_time - expiry_time
                        logger.error(f"Token expired {expired_seconds_ago} seconds ago")
                elif not auth_manager.token_info.access_token:
                    logger.error("TOKEN VALIDATION FAILED: Token object exists but access_token is empty")
                else:
                    logger.error("TOKEN VALIDATION FAILED: Token exists but was rejected for unknown reason")
            else:
                logger.error("TOKEN VALIDATION FAILED: No token information available")
                
            # Suggest next steps for troubleshooting
            logger.error("To fix: Try re-authenticating or check if your token has been revoked")
            return None
    except Exception as e:
        logger.error(f"Error getting access token: {str(e)}")
        import traceback
        logger.error(f"Token validation stacktrace: {traceback.format_exc()}")
        return None


def login():
    """
    Start the login flow to authenticate with Meta
    """
    print("Starting Meta Ads authentication flow...")
    
    try:
        # Start the callback server first
        try:
            port = start_callback_server()
        except Exception as callback_error:
            print(f"Error: {callback_error}")
            print("Callback server is disabled. Please use alternative authentication methods:")
            print("- Set PIPEBOARD_API_TOKEN environment variable for Pipeboard authentication")
            print("- Or provide a direct META_ACCESS_TOKEN environment variable")
            return
        
        # Get the auth URL and open the browser
        auth_url = auth_manager.get_auth_url()
        print(f"Opening browser with URL: {auth_url}")
        webbrowser.open(auth_url)
        
        # Wait for token to be received
        print("Waiting for authentication to complete...")
        max_wait = 300  # 5 minutes
        wait_interval = 2  # 2 seconds
        
        for _ in range(max_wait // wait_interval):
            if token_container["token"]:
                token = token_container["token"]
                print("Authentication successful!")
                # Verify token works by getting basic user info
                try:
                    from .api import make_api_request
                    result = asyncio.run(make_api_request("me", token, {}))
                    print(f"Authenticated as: {result.get('name', 'Unknown')} (ID: {result.get('id', 'Unknown')})")
                    return
                except Exception as e:
                    print(f"Warning: Could not verify token: {e}")
                    return
            time.sleep(wait_interval)
        
        print("Authentication timed out. Please try again.")
    except Exception as e:
        print(f"Error during authentication: {e}")
        print(f"Direct authentication URL: {auth_manager.get_auth_url()}")
        print("You can manually open this URL in your browser to complete authentication.")

# Initialize auth manager with a placeholder - will be updated at runtime
META_APP_ID = os.environ.get("META_APP_ID", "YOUR_META_APP_ID")

# Create the auth manager
auth_manager = AuthManager(META_APP_ID) 