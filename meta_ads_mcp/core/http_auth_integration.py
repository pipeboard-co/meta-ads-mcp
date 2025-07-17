"""
FastMCP HTTP Authentication Integration for Meta Ads MCP

This module provides direct integration with FastMCP to inject authentication
from HTTP headers into the tool execution context.
"""

import asyncio
import contextvars
from typing import Optional
from .utils import logger
import json

# Use context variables instead of thread-local storage for better async support
_auth_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('auth_token', default=None)
_pipeboard_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('pipeboard_token', default=None)

class FastMCPAuthIntegration:
    """Direct integration with FastMCP for HTTP authentication"""
    
    @staticmethod
    def set_auth_token(token: str) -> None:
        """Set authentication token for the current context
        
        Args:
            token: Access token to use for this request
        """
        _auth_token.set(token)
    
    @staticmethod
    def get_auth_token() -> Optional[str]:
        """Get authentication token for the current context
        
        Returns:
            Access token if set, None otherwise
        """
        return _auth_token.get(None)
    
    @staticmethod
    def set_pipeboard_token(token: str) -> None:
        """Set Pipeboard token for the current context
        
        Args:
            token: Pipeboard API token to use for this request
        """
        _pipeboard_token.set(token)
    
    @staticmethod
    def get_pipeboard_token() -> Optional[str]:
        """Get Pipeboard token for the current context
        
        Returns:
            Pipeboard token if set, None otherwise
        """
        return _pipeboard_token.get(None)
    
    @staticmethod
    def clear_auth_token() -> None:
        """Clear authentication token for the current context"""
        _auth_token.set(None)
    
    @staticmethod
    def clear_pipeboard_token() -> None:
        """Clear Pipeboard token for the current context"""
        _pipeboard_token.set(None)
    
    @staticmethod
    def extract_token_from_headers(headers: dict) -> Optional[str]:
        """Extract token from HTTP headers
        
        Args:
            headers: HTTP request headers
            
        Returns:
            Token if found, None otherwise
        """
        # Check for Bearer token in Authorization header (primary method)
        auth_header = headers.get('Authorization') or headers.get('authorization')
        if auth_header and auth_header.lower().startswith('bearer '):
            token = auth_header[7:].strip()
            logger.debug("Found Bearer token in Authorization header")
            return token
        
        # Check for direct Meta access token
        meta_token = headers.get('X-META-ACCESS-TOKEN') or headers.get('x-meta-access-token')
        if meta_token:
            return meta_token
        
        # Check for Pipeboard token (legacy support, to be removed)
        pipeboard_token = headers.get('X-PIPEBOARD-API-TOKEN') or headers.get('x-pipeboard-api-token')
        if pipeboard_token:
            logger.debug("Found Pipeboard token in legacy headers")
            return pipeboard_token
        
        return None
    
    @staticmethod
    def extract_pipeboard_token_from_headers(headers: dict) -> Optional[str]:
        """Extract Pipeboard token from HTTP headers
        
        Args:
            headers: HTTP request headers
            
        Returns:
            Pipeboard token if found, None otherwise
        """
        # Check for Pipeboard token in X-Pipeboard-Token header (duplication API pattern)
        pipeboard_token = headers.get('X-Pipeboard-Token') or headers.get('x-pipeboard-token')
        if pipeboard_token:
            logger.debug("Found Pipeboard token in X-Pipeboard-Token header")
            return pipeboard_token
        
        # Check for legacy Pipeboard token header
        legacy_token = headers.get('X-PIPEBOARD-API-TOKEN') or headers.get('x-pipeboard-api-token')
        if legacy_token:
            logger.debug("Found Pipeboard token in legacy X-PIPEBOARD-API-TOKEN header")
            return legacy_token
        
        return None

def patch_fastmcp_server(mcp_server):
    """Patch FastMCP server to inject authentication from HTTP headers
    
    Args:
        mcp_server: FastMCP server instance to patch
    """
    logger.info("Patching FastMCP server for HTTP authentication")
    
    # Store the original run method
    original_run = mcp_server.run
    
    def patched_run(transport="stdio", **kwargs):
        """Enhanced run method that sets up HTTP auth integration"""
        logger.debug(f"Starting FastMCP with transport: {transport}")
        
        if transport == "streamable-http":
            logger.debug("Setting up HTTP authentication for streamable-http transport")
            setup_http_auth_patching()
        
        # Call the original run method
        return original_run(transport=transport, **kwargs)
    
    # Replace the run method
    mcp_server.run = patched_run
    logger.info("FastMCP server patching complete")

def setup_http_auth_patching():
    """Setup HTTP authentication patching for auth system"""
    logger.info("Setting up HTTP authentication patching")
    
    # Import and patch the auth system
    from . import auth
    from . import api
    from . import authentication
    
    # Store the original function
    original_get_current_access_token = auth.get_current_access_token
    
    async def get_current_access_token_with_http_support() -> Optional[str]:
        """Enhanced get_current_access_token that checks HTTP context first"""
        
        # Check for context-scoped token first
        context_token = FastMCPAuthIntegration.get_auth_token()
        if context_token:
            return context_token
        
        # Fall back to original implementation
        return await original_get_current_access_token()
    
    # Replace the function in all modules that imported it
    auth.get_current_access_token = get_current_access_token_with_http_support
    api.get_current_access_token = get_current_access_token_with_http_support
    authentication.get_current_access_token = get_current_access_token_with_http_support
    
    logger.info("Auth system patching complete - patched in auth, api, and authentication modules")

# Global instance for easy access
fastmcp_auth = FastMCPAuthIntegration()

# Forward declaration of setup_starlette_middleware
def setup_starlette_middleware(app):
    pass

def setup_fastmcp_http_auth(mcp_server):
    """Setup HTTP authentication integration with FastMCP
    
    Args:
        mcp_server: FastMCP server instance to configure
    """
    logger.info("Setting up FastMCP HTTP authentication integration")
    
    # 1. Patch FastMCP's run method to ensure our get_current_access_token patch is applied
    # This remains crucial for the token to be picked up by tool calls.
    patch_fastmcp_server(mcp_server) # This patches mcp_server.run
    
    # 2. Patch the methods that provide the Starlette app instance
    # This ensures our middleware is added to the app Uvicorn will actually serve.

    app_provider_methods = []
    if mcp_server.settings.json_response:
        if hasattr(mcp_server, "streamable_http_app") and callable(mcp_server.streamable_http_app):
            app_provider_methods.append("streamable_http_app")
        else:
            logger.warning("mcp_server.streamable_http_app not found or not callable, cannot patch for JSON responses.")
    else: # SSE
        if hasattr(mcp_server, "sse_app") and callable(mcp_server.sse_app):
            app_provider_methods.append("sse_app")
        else:
            logger.warning("mcp_server.sse_app not found or not callable, cannot patch for SSE responses.")

    if not app_provider_methods:
        logger.error("No suitable app provider method (streamable_http_app or sse_app) found on mcp_server. Cannot add HTTP Auth middleware.")
        # Fallback or error handling might be needed here if this is critical
    
    for method_name in app_provider_methods:
        original_app_provider_method = getattr(mcp_server, method_name)
        
        def new_patched_app_provider_method(*args, **kwargs):
            # Call the original method to get/create the Starlette app
            app = original_app_provider_method(*args, **kwargs)
            if app:
                logger.debug(f"Original {method_name} returned app: {type(app)}. Adding AuthInjectionMiddleware.")
                # Now, add our middleware to this specific app instance
                setup_starlette_middleware(app) 
            else:
                logger.error(f"Original {method_name} returned None or a non-app object.")
            return app
            
        setattr(mcp_server, method_name, new_patched_app_provider_method)
        logger.debug(f"Patched mcp_server.{method_name} to inject AuthInjectionMiddleware.")

    # The old setup_request_middleware call is no longer needed here,
    # as middleware addition is now handled by patching the app provider methods.
    # try:
    #     setup_request_middleware(mcp_server) 
    # except Exception as e:
    #     logger.warning(f"Could not setup request middleware: {e}")

    logger.info("FastMCP HTTP authentication integration setup attempt complete.")

# Remove the old setup_request_middleware function as its logic is integrated above
# def setup_request_middleware(mcp_server): ... (delete this function)

# --- AuthInjectionMiddleware definition ---
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import json # Ensure json is imported if not already at the top

class AuthInjectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"HTTP Auth Middleware: Processing request to {request.url.path}")
        logger.debug(f"HTTP Auth Middleware: Request headers: {list(request.headers.keys())}")
        
        # Extract both types of tokens for dual-header authentication
        auth_token = FastMCPAuthIntegration.extract_token_from_headers(dict(request.headers))
        pipeboard_token = FastMCPAuthIntegration.extract_pipeboard_token_from_headers(dict(request.headers))
        
        if auth_token:
            logger.debug(f"HTTP Auth Middleware: Extracted auth token: {auth_token[:10]}...")
            logger.debug("Injecting auth token into request context")
            FastMCPAuthIntegration.set_auth_token(auth_token)
        
        if pipeboard_token:
            logger.debug(f"HTTP Auth Middleware: Extracted Pipeboard token: {pipeboard_token[:10]}...")
            logger.debug("Injecting Pipeboard token into request context")
            FastMCPAuthIntegration.set_pipeboard_token(pipeboard_token)
        
        if not auth_token and not pipeboard_token:
            logger.warning("HTTP Auth Middleware: No authentication tokens found in headers")
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Clear tokens that were set for this request
            if auth_token:
                FastMCPAuthIntegration.clear_auth_token()
            if pipeboard_token:
                FastMCPAuthIntegration.clear_pipeboard_token()

def setup_starlette_middleware(app):
    """Add AuthInjectionMiddleware to the Starlette app if not already present.
    
    Args:
        app: Starlette app instance
    """
    if not app:
        logger.error("Cannot setup Starlette middleware, app is None.")
        return

    # Check if our specific middleware class is already in the stack
    already_added = False
    # Starlette's app.middleware is a list of Middleware objects.
    # app.user_middleware contains middleware added by app.add_middleware()
    for middleware_item in app.user_middleware:
        if middleware_item.cls == AuthInjectionMiddleware:
            already_added = True
            break
            
    if not already_added:
        try:
            app.add_middleware(AuthInjectionMiddleware)
            logger.info("AuthInjectionMiddleware added to Starlette app successfully.")
        except Exception as e:
            logger.error(f"Failed to add AuthInjectionMiddleware to Starlette app: {e}", exc_info=True)
    else:
        logger.debug("AuthInjectionMiddleware already present in Starlette app's middleware stack.") 