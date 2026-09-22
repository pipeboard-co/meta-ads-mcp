"""Callback server for Meta Ads API authentication."""

import threading
import socket
import time
import logging
import secrets
import webbrowser
import os
from html import escape as html_escape
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

from .utils import logger

# Global token container for communication between threads
token_container = {"token": None, "expires_in": None, "user_id": None}

# Global variables for server thread and state
callback_server_thread = None
callback_server_lock = threading.Lock()
callback_server_running = False
callback_server_port = None
callback_server_instance = None
server_shutdown_timer = None

# Timeout in seconds before shutting down the callback server
CALLBACK_SERVER_TIMEOUT = 180  # 3 minutes timeout

# Maximum number of characters of an OAuth error echoed back to the browser
MAX_ERROR_DISPLAY_LENGTH = 200


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Print path for debugging
            print(f"Callback server received request: {self.path}")
            
            if self.path.startswith("/callback"):
                self._handle_oauth_callback()
            else:
                # If no matching path, return a 404 error
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _send_html(self, html: str, csp: str = "default-src 'none'") -> None:
        """Send an HTML response with hardening headers."""
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", csp)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _handle_oauth_callback(self):
        """Handle OAuth callback after user authorization"""
        # Check if we're being redirected from Facebook with an authorization code
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        
        # Check for code parameter
        code = params.get('code', [None])[0]
        state = params.get('state', [None])[0]
        error = params.get('error', [None])[0]
        
        # Anything reaching this endpoint is attacker-controllable, so the error
        # is HTML-escaped (and truncated) before it is echoed back to the browser.
        csp = "default-src 'none'"
        
        if error:
            # User denied access or other error occurred
            safe_error = html_escape(error[:MAX_ERROR_DISPLAY_LENGTH])
            html = f"""
            <html>
            <head><title>Authorization Failed</title></head>
            <body>
                <h1>Authorization Failed</h1>
                <p>Error: {safe_error}</p>
                <p>The authorization was cancelled or failed. You can close this window.</p>
            </body>
            </html>
            """
            logger.error(f"OAuth authorization failed: {error}")
        elif code:
            # Success case - we have the authorization code
            logger.info(f"Received authorization code: {code[:10]}...")
            
            # Store the authorization code temporarily
            # The auth module will exchange this for an access token
            token_container.update({
                "auth_code": code,
                "state": state,
                "timestamp": time.monotonic()
            })
            
            # The success page needs its own inline script, so allow just that
            # one script via a per-response nonce rather than loosening the CSP.
            nonce = secrets.token_urlsafe(16)
            csp = f"default-src 'none'; script-src 'nonce-{nonce}'"
            html = f"""
            <html>
            <head><title>Authorization Successful</title></head>
            <body>
                <h1>✅ Authorization Successful!</h1>
                <p>You have successfully authorized the Meta Ads MCP application.</p>
                <p>You can now close this window and return to your application.</p>
                <script nonce="{nonce}">
                    // Try to close the window automatically after 2 seconds
                    setTimeout(function() {{
                        window.close();
                    }}, 2000);
                </script>
            </body>
            </html>
            """
            logger.info("OAuth authorization successful")
        else:
            # No code or error - something unexpected happened
            html = """
            <html>
            <head><title>Unexpected Response</title></head>
            <body>
                <h1>Unexpected Response</h1>
                <p>No authorization code or error received. Please try again.</p>
            </body>
            </html>
            """
            logger.warning("OAuth callback received without code or error")
        
        self._send_html(html, csp)
    
    # Silence server logs
    def log_message(self, format, *args):
        return


def shutdown_callback_server():
    """
    Shutdown the callback server if it's running
    """
    global callback_server_thread, callback_server_running, callback_server_port, callback_server_instance, server_shutdown_timer
    
    with callback_server_lock:
        if not callback_server_running:
            print("Callback server is not running")
            return
        
        if server_shutdown_timer is not None:
            server_shutdown_timer.cancel()
            server_shutdown_timer = None
        
        try:
            if callback_server_instance:
                print("Shutting down callback server...")
                callback_server_instance.shutdown()
                callback_server_instance.server_close()
                print("Callback server shut down successfully")
            
            if callback_server_thread and callback_server_thread.is_alive():
                callback_server_thread.join(timeout=5)
                if callback_server_thread.is_alive():
                    print("Warning: Callback server thread did not shut down cleanly")
        except Exception as e:
            print(f"Error during callback server shutdown: {e}")
        finally:
            callback_server_running = False
            callback_server_thread = None
            callback_server_port = None
            callback_server_instance = None


def start_callback_server() -> int:
    """
    Start the callback server and return the port number it's running on.
    
    Returns:
        int: Port number the server is listening on
        
    Raises:
        Exception: If the server fails to start
    """
    global callback_server_thread, callback_server_running, callback_server_port, callback_server_instance, server_shutdown_timer
    
    # Check if callback server is disabled
    if os.environ.get("META_ADS_DISABLE_CALLBACK_SERVER"):
        raise Exception("Callback server is disabled via META_ADS_DISABLE_CALLBACK_SERVER environment variable")
    
    with callback_server_lock:
        if callback_server_running:
            print(f"Callback server already running on port {callback_server_port}")
            return callback_server_port
        
        # Find an available port
        port = 8080
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Test if port is available
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                break
            except OSError:
                port += 1
        else:
            raise Exception(f"Could not find an available port after {max_attempts} attempts")
        
        callback_server_port = port
        
        # Start the server in a separate thread
        callback_server_thread = threading.Thread(target=server_thread, daemon=True)
        callback_server_thread.start()
        
        # Wait a moment for the server to start
        time.sleep(0.5)
        
        if not callback_server_running:
            raise Exception("Failed to start callback server")
        
        # Set up automatic shutdown timer
        def auto_shutdown():
            print(f"Callback server auto-shutdown after {CALLBACK_SERVER_TIMEOUT} seconds")
            shutdown_callback_server()
        
        server_shutdown_timer = threading.Timer(CALLBACK_SERVER_TIMEOUT, auto_shutdown)
        server_shutdown_timer.start()
        
        print(f"Callback server started on http://localhost:{port}")
        return port


def server_thread():
    """Thread function to run the callback server"""
    global callback_server_running, callback_server_instance
    
    try:
        callback_server_instance = HTTPServer(('localhost', callback_server_port), CallbackHandler)
        callback_server_running = True
        print(f"Callback server thread started on port {callback_server_port}")
        callback_server_instance.serve_forever()
    except Exception as e:
        print(f"Callback server error: {e}")
        callback_server_running = False
    finally:
        print("Callback server thread finished")
        callback_server_running = False 