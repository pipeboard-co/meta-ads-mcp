"""Callback server for Meta Ads API authentication and confirmations."""

import threading
import socket
import asyncio
import json
import logging
import webbrowser
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from typing import Dict, Any, Optional

from .utils import logger

# Global token container for communication between threads
token_container = {"token": None, "expires_in": None, "user_id": None}

# Global container for update confirmations
update_confirmation = {"approved": False}

# Global variables for server thread and state
callback_server_thread = None
callback_server_lock = threading.Lock()
callback_server_running = False
callback_server_port = None
callback_server_instance = None
server_shutdown_timer = None

# Timeout in seconds before shutting down the callback server
CALLBACK_SERVER_TIMEOUT = 180  # 3 minutes timeout


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Print path for debugging
            print(f"Callback server received request: {self.path}")
            
            if self.path.startswith("/callback"):
                self._handle_oauth_callback()
            elif self.path.startswith("/token"):
                self._handle_token()
            elif self.path.startswith("/confirm-update"):
                self._handle_update_confirmation()
            elif self.path.startswith("/update-confirm"):
                self._handle_update_execution()
            elif self.path.startswith("/verify-update"):
                self._handle_update_verification()
            elif self.path.startswith("/api/adset"):
                self._handle_adset_api()
            elif self.path.startswith("/api/ad"):
                self._handle_ad_api()
            else:
                # If no matching path, return a 404 error
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _handle_oauth_callback(self):
        """Handle the OAuth callback from Meta"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        callback_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .success { 
                    color: #4CAF50;
                    font-size: 24px;
                    margin-bottom: 20px;
                }
                .info {
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="success">Authentication Successful!</div>
            <div class="info">
                <p>Your Meta Ads API token has been received.</p>
                <p>You can now close this window and return to the application.</p>
            </div>
            <button class="button" onclick="window.close()">Close Window</button>
            
            <script>
            // Function to parse URL parameters including fragments
            function parseURL(url) {
                var params = {};
                var parser = document.createElement('a');
                parser.href = url;
                
                // Parse fragment parameters
                var fragment = parser.hash.substring(1);
                var fragmentParams = fragment.split('&');
                
                for (var i = 0; i < fragmentParams.length; i++) {
                    var pair = fragmentParams[i].split('=');
                    params[pair[0]] = decodeURIComponent(pair[1]);
                }
                
                return params;
            }
            
            // Parse the URL to get the access token
            var params = parseURL(window.location.href);
            var token = params['access_token'];
            var expires_in = params['expires_in'];
            
            // Send the token to the server
            if (token) {
                // Create XMLHttpRequest object
                var xhr = new XMLHttpRequest();
                
                // Configure it to make a GET request to the /token endpoint
                xhr.open('GET', '/token?token=' + encodeURIComponent(token) + 
                              '&expires_in=' + encodeURIComponent(expires_in), true);
                
                // Set up a handler for when the request is complete
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        console.log('Token successfully sent to server');
                    } else {
                        console.error('Failed to send token to server');
                    }
                };
                
                // Send the request
                xhr.send();
            } else {
                console.error('No token found in URL');
                document.body.innerHTML += '<div style="color: red; margin-top: 20px;">Error: No authentication token found. Please try again.</div>';
            }
            </script>
        </body>
        </html>
        """
        self.wfile.write(callback_html.encode())
    
    def _handle_token(self):
        """Handle the token received from the callback"""
        # Extract token from query params
        query = parse_qs(urlparse(self.path).query)
        token_container["token"] = query.get("token", [""])[0]
        
        if "expires_in" in query:
            try:
                token_container["expires_in"] = int(query.get("expires_in", ["0"])[0])
            except ValueError:
                token_container["expires_in"] = None
        
        # Send success response
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Token received")

        # The actual token processing is now handled by the auth module
        # that imports this module and accesses token_container
    
    def _handle_update_confirmation(self):
        """Handle the update confirmation page"""
        # Extract query parameters
        query = parse_qs(urlparse(self.path).query)
        adset_id = query.get("adset_id", [""])[0]
        ad_id = query.get("ad_id", [""])[0]
        token = query.get("token", [""])[0]
        changes = query.get("changes", ["{}"])[0]
        
        # Determine what type of object we're updating
        object_id = ad_id if ad_id else adset_id
        object_type = "Ad" if ad_id else "Ad Set"
        
        try:
            changes_dict = json.loads(changes)
        except json.JSONDecodeError:
            changes_dict = {}
        
        # Return confirmation page
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # Create a properly escaped JSON string for JavaScript
        escaped_changes = json.dumps(changes).replace("'", "\\'").replace('"', '\\"')
        
        html = """
        <html>
        <head>
            <title>Confirm """ + object_type + """ Update</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; max-width: 1000px; margin: 0 auto; }
                .warning { color: #d73a49; margin: 20px 0; padding: 15px; border-left: 4px solid #d73a49; background-color: #fff8f8; }
                .changes { background: #f6f8fa; padding: 15px; border-radius: 6px; }
                .buttons { margin-top: 20px; }
                button { padding: 10px 20px; margin-right: 10px; border-radius: 6px; cursor: pointer; }
                .approve { background: #2ea44f; color: white; border: none; }
                .cancel { background: #d73a49; color: white; border: none; }
                .diff-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                .diff-table td { padding: 8px; border: 1px solid #ddd; }
                .diff-table .header { background: #f1f8ff; font-weight: bold; }
                .status { padding: 15px; margin-top: 20px; border-radius: 6px; display: none; }
                .success { background-color: #e6ffed; border: 1px solid #2ea44f; color: #22863a; }
                .error { background-color: #ffeef0; border: 1px solid #d73a49; color: #d73a49; }
                pre { white-space: pre-wrap; word-break: break-all; }
            </style>
        </head>
        <body>
            <h1>Confirm """ + object_type + """ Update</h1>
            <p>You are about to update """ + object_type + """: <strong>""" + object_id + """</strong></p>
            
            <div class="warning">
                <p><strong>Warning:</strong> This action will directly update your """ + object_type.lower() + """ in Meta Ads. Please review the changes carefully before approving.</p>
            </div>
            
            <div class="changes">
                <h3>Changes to apply:</h3>
                <table class="diff-table">
                    <tr class="header">
                        <td>Field</td>
                        <td>New Value</td>
                        <td>Description</td>
                    </tr>
                    """
        
        # Generate table rows for each change
        for k, v in changes_dict.items():
            description = ""
            if k == "frequency_control_specs" and isinstance(v, list) and len(v) > 0:
                spec = v[0]
                if all(key in spec for key in ["event", "interval_days", "max_frequency"]):
                    description = f"Cap to {spec['max_frequency']} {spec['event'].lower()} per {spec['interval_days']} days"
            
            # Special handling for targeting_automation
            elif k == "targeting" and isinstance(v, dict) and "targeting_automation" in v:
                targeting_auto = v.get("targeting_automation", {})
                if "advantage_audience" in targeting_auto:
                    audience_value = targeting_auto["advantage_audience"]
                    description = f"Set Advantage+ audience to {'ON' if audience_value == 1 else 'OFF'}"
                    if audience_value == 1:
                        description += " (may be restricted for Special Ad Categories)"
            
            # Format the value for display
            display_value = json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v)
            
            html += f"""
                    <tr>
                        <td>{k}</td>
                        <td><pre>{display_value}</pre></td>
                        <td>{description}</td>
                    </tr>
                    """
        
        html += """
                </table>
            </div>
            
            <div class="buttons">
                <button class="approve" onclick="approveChanges()">Approve Changes</button>
                <button class="cancel" onclick="cancelChanges()">Cancel</button>
            </div>
            
            <div id="status" class="status"></div>

            <script>
                // Get the approve button
                const approveBtn = document.querySelector('.approve');
                const cancelBtn = document.querySelector('.cancel');
                const statusDiv = document.querySelector('.status');
                
                let debugMode = false;
                // Function to log debug messages
                function debugLog(...args) {
                    if (debugMode) {
                        console.log(...args);
                    }
                }
                
                // Add event listeners to buttons
                approveBtn.addEventListener('click', approveChanges);
                cancelBtn.addEventListener('click', cancelChanges);
                
                function showStatus(message, isError = false) {
                    statusDiv.textContent = message;
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'status ' + (isError ? 'error' : 'success');
                }
                
                function approveChanges() {
                    // Disable buttons to prevent double-submission
                    const buttons = [approveBtn, cancelBtn];
                    buttons.forEach(button => button.disabled = true);
                    
                    showStatus('Approving changes...');
                    
                    // Determine which object type we're updating
                    const isAd = Boolean('""" + ad_id + """'); 
                    const objectType = isAd ? 'ad' : 'adset';
                    const objectId = '""" + object_id + """';
                    
                    // Create parameters
                    const params = new URLSearchParams({
                        action: 'approve',
                        token: '""" + token + """',
                        changes: '""" + escaped_changes + """'
                    });
                    
                    // Add the appropriate ID parameter based on object type
                    if (isAd) {
                        params.append('ad_id', objectId);
                    } else {
                        params.append('adset_id', objectId);
                    }
                    
                    debugLog("Sending update request with params", {
                        objectType,
                        objectId,
                        changes: JSON.parse('""" + escaped_changes + """')
                    });
                    
                    fetch('/update-confirm?' + params)
                    .then(response => response.json())
                    .then(data => {
                        debugLog("Update response data", data);
                        buttons.forEach(button => button.disabled = false);
                        
                        // Handle result
                        if (data.status === 'error') {
                            let errorMessage = data.error || 'Unknown error';
                            const originalErrorDetails = data.api_error || {};
                            
                            showStatus('Error: ' + errorMessage, true);
                            
                            // Create a detailed error object for the verification page
                            const fullErrorData = {
                                message: errorMessage,
                                details: data.errorDetails || [],
                                apiError: originalErrorDetails || data.apiError || {},
                                fullResponse: data.fullResponse || {}
                            };
                            
                            debugLog("Redirecting with error message", errorMessage);
                            debugLog("Full error data", fullErrorData);
                            
                            // Encode the stringified error object
                            const encodedErrorData = encodeURIComponent(JSON.stringify(fullErrorData));
                            
                            // Redirect to verification page with detailed error information
                            const errorParams = new URLSearchParams({
                                token: '""" + token + """',
                                error: errorMessage,
                                errorData: encodedErrorData
                            });
                            
                            // Add the appropriate ID parameter based on object type
                            if (isAd) {
                                errorParams.append('ad_id', objectId);
                            } else {
                                errorParams.append('adset_id', objectId);
                            }
                            
                            window.location.href = '/verify-update?' + errorParams;
                        } else {
                            showStatus('Changes approved and will be applied shortly!');
                            setTimeout(() => {
                                const verifyParams = new URLSearchParams({
                                    token: '""" + token + """'
                                });
                                
                                // Add the appropriate ID parameter based on object type
                                if (isAd) {
                                    verifyParams.append('ad_id', objectId);
                                } else {
                                    verifyParams.append('adset_id', objectId);
                                }
                                
                                window.location.href = '/verify-update?' + verifyParams;
                            }, 3000);
                        }
                    })
                    .catch(error => {
                        debugLog("Fetch error", error);
                        showStatus('Error applying changes: ' + error, true);
                        buttons.forEach(button => button.disabled = false);
                    });
                }
                
                function cancelChanges() {
                    showStatus("Cancelling update...");
                    
                    // Determine which object type we're updating
                    const isAd = Boolean('""" + ad_id + """'); 
                    const objectId = '""" + object_id + """';
                    
                    // Create parameters
                    const params = new URLSearchParams({
                        action: 'cancel'
                    });
                    
                    // Add the appropriate ID parameter based on object type
                    if (isAd) {
                        params.append('ad_id', objectId);
                    } else {
                        params.append('adset_id', objectId);
                    }
                    
                    fetch('/update-confirm?' + params)
                    .then(() => {
                        showStatus('Update cancelled.');
                        setTimeout(() => window.close(), 2000);
                    });
                }
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def _handle_update_execution(self):
        """Handle the update execution after user confirmation"""
        # Handle update confirmation response
        query = parse_qs(urlparse(self.path).query)
        action = query.get("action", [""])[0]
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        if action == "approve":
            adset_id = query.get("adset_id", [""])[0]
            ad_id = query.get("ad_id", [""])[0]
            token = query.get("token", [""])[0]
            changes = query.get("changes", ["{}"])[0]
            
            # Determine what type of object we're updating
            object_id = ad_id if ad_id else adset_id
            object_type = "ad" if ad_id else "adset"
            
            # Store the approval in the global variable for the main thread to process
            update_confirmation.clear()
            update_confirmation.update({
                "approved": True,
                "object_id": object_id,
                "object_type": object_type,
                "token": token,
                "changes": changes
            })
            
            # Process the update asynchronously
            result = asyncio.run(self._perform_update(object_id, token, changes))
            self.wfile.write(json.dumps(result).encode())
        else:
            # Store the cancellation
            update_confirmation.clear()
            update_confirmation.update({"approved": False})
            self.wfile.write(json.dumps({"status": "cancelled"}).encode())
    
    async def _perform_update(self, object_id, token, changes):
        """Perform the actual update of the adset or ad"""
        from .api import make_api_request
        
        try:
            # Handle potential multiple encoding of JSON
            decoded_changes = changes
            # Try multiple decode attempts to handle various encoding scenarios
            for _ in range(3):  # Try up to 3 levels of decoding
                try:
                    # Try to parse as JSON
                    changes_obj = json.loads(decoded_changes)
                    # If we got a string back, we need to decode again
                    if isinstance(changes_obj, str):
                        decoded_changes = changes_obj
                        continue
                    else:
                        # We have a dictionary, break the loop
                        changes_dict = changes_obj
                        break
                except json.JSONDecodeError:
                    # Try unescaping first
                    import html
                    decoded_changes = html.unescape(decoded_changes)
                    try:
                        changes_dict = json.loads(decoded_changes)
                        break
                    except:
                        # Failed to parse, will try again in the next iteration
                        pass
            else:
                # If we got here, we couldn't parse the JSON
                return {"status": "error", "error": f"Failed to decode changes JSON: {changes}"}
            
            endpoint = f"{object_id}"
            
            # Create API parameters properly
            api_params = {}
            
            # Add each change parameter
            for key, value in changes_dict.items():
                api_params[key] = value
                
            # Add the access token
            api_params["access_token"] = token
            
            # Log what we're about to send
            object_type = "ad set" if object_id.startswith("23") else "ad"  # Simple heuristic based on ID prefix
            logger.info(f"Sending update to Meta API for {object_type} {object_id}")
            logger.info(f"Parameters: {json.dumps(api_params)}")
            
            # Make the API request to update the object
            result = await make_api_request(endpoint, token, api_params, method="POST")
            
            # Log the result
            logger.info(f"Meta API update result: {json.dumps(result) if isinstance(result, dict) else result}")
            
            # Handle various result formats
            if result is None:
                logger.error("Empty response from Meta API")
                return {"status": "error", "error": "Empty response from Meta API"}
                
            # Check if the result contains an error
            if isinstance(result, dict) and 'error' in result:
                # Extract detailed error message from Meta API
                error_obj = result['error']
                error_msg = error_obj.get('message', 'Unknown API error')
                detailed_error = ""
                
                # Check for more detailed error messages
                if 'error_user_msg' in error_obj and error_obj['error_user_msg']:
                    detailed_error = error_obj['error_user_msg']
                    logger.error(f"Meta API user-facing error message: {detailed_error}")
                
                # Extract error data if available
                error_specs = []
                if 'error_data' in error_obj and isinstance(error_obj['error_data'], str):
                    try:
                        error_data = json.loads(error_obj['error_data'])
                        if 'blame_field_specs' in error_data and error_data['blame_field_specs']:
                            blame_specs = error_data['blame_field_specs']
                            if isinstance(blame_specs, list) and blame_specs:
                                if isinstance(blame_specs[0], list):
                                    error_specs = [msg for msg in blame_specs[0] if msg]
                                else:
                                    error_specs = [str(spec) for spec in blame_specs if spec]
                            
                            if error_specs:
                                logger.error(f"Meta API blame field specs: {'; '.join(error_specs)}")
                    except Exception as e:
                        logger.error(f"Error parsing error_data: {e}")
                
                # Construct most descriptive error message
                if detailed_error:
                    error_msg = detailed_error
                elif error_specs:
                    error_msg = "; ".join(error_specs)
                
                # Log the detailed error information
                logger.error(f"Meta API error: {error_msg}")
                logger.error(f"Full error object: {json.dumps(error_obj)}")
                
                return {
                    "status": "error", 
                    "error": error_msg, 
                    "api_error": result['error'],
                    "detailed_errors": error_specs,
                    "full_response": result
                }
            
            # Handle string results (which might be error messages)
            if isinstance(result, str):
                try:
                    # Try to parse as JSON
                    result_obj = json.loads(result)
                    if isinstance(result_obj, dict) and 'error' in result_obj:
                        return {"status": "error", "error": result_obj['error'].get('message', 'Unknown API error')}
                except:
                    # If not parseable as JSON, return as error message
                    return {"status": "error", "error": result}
            
            # If we got here, assume success
            return {"status": "approved", "api_result": result}
        except Exception as e:
            # Log the exception for debugging
            logger.error(f"Error in perform_update: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}
    
    def _handle_update_verification(self):
        """Handle the verification page for updates"""
        query = parse_qs(urlparse(self.path).query)
        adset_id = query.get("adset_id", [""])[0]
        ad_id = query.get("ad_id", [""])[0]
        object_id = query.get("object_id", [""])[0] 
        
        # For backward compatibility - use object_id if available, otherwise check for adset_id or ad_id
        if not object_id:
            object_id = ad_id if ad_id else adset_id
            
        object_type = query.get("object_type", [""])[0]
        if not object_type:
            object_type = "Ad" if ad_id else "Ad Set"
            
        token = query.get("token", [""])[0]
        error_message = query.get("error", [""])[0]
        error_data_encoded = query.get("errorData", [""])[0]
        
        # Respond with verification page
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verification - """ + object_type + """ Update</title>
            <meta charset="utf-8">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    max-width: 1000px; 
                    margin: 0 auto;
                    line-height: 1.6;
                }
                .header { 
                    margin-bottom: 20px; 
                    padding-bottom: 10px; 
                    border-bottom: 1px solid #ccc; 
                }
                .success { 
                    color: #2ea44f; 
                    background-color: #e6ffed; 
                    padding: 15px; 
                    border-radius: 6px; 
                    margin: 20px 0; 
                }
                .error { 
                    color: #d73a49; 
                    background-color: #ffeef0; 
                    padding: 15px; 
                    border-radius: 6px; 
                    margin: 20px 0; 
                }
                .details { 
                    background: #f6f8fa; 
                    padding: 15px; 
                    border-radius: 6px; 
                    margin: 20px 0; 
                }
                .btn {
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #0366d6;
                    color: white;
                    border-radius: 6px;
                    text-decoration: none;
                    margin-top: 20px;
                }
                pre {
                    white-space: pre-wrap;
                    word-break: break-word;
                    background: #f8f8f8;
                    padding: 10px;
                    border-radius: 4px;
                    overflow: auto;
                }
                #currentDetails {
                    display: none;
                    margin-top: 20px;
                }
                .toggle-btn {
                    background-color: #f1f8ff;
                    border: 1px solid #c8e1ff;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 20px;
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>""" + object_type + """ Update Verification</h1>
                <p>Object ID: <strong>""" + object_id + """</strong></p>
            </div>
        """
        
        # If there's an error message, display it
        if error_message:
            html += """
            <div class="error">
                <h3>❌ Update Failed</h3>
                <p><strong>Error:</strong> """ + error_message + """</p>
            """
            
            # If there's detailed error data, decode and display it
            if error_data_encoded:
                try:
                    error_data = json.loads(urllib.parse.unquote(error_data_encoded))
                    html += """
                    <div class="details">
                        <h4>Error Details:</h4>
                        <pre>""" + json.dumps(error_data, indent=2) + """</pre>
                    </div>
                    """
                except:
                    pass
            
            html += """</div>"""
        else:
            # No error, display success message
            html += """
            <div class="success">
                <h3>✅ Update Successful</h3>
                <p>Your """ + object_type.lower() + """ has been updated successfully.</p>
            </div>
            """
        
        # Add JavaScript to fetch the current details of the ad/adset
        html += """
        <button class="toggle-btn" id="toggleDetails">Show Current Details</button>
        <div id="currentDetails">
            <h3>Current """ + object_type + """ Details:</h3>
            <pre id="detailsJson">Loading...</pre>
        </div>
        
        <a href="#" class="btn" onclick="window.close()">Close Window</a>
        
        <script>
            document.getElementById('toggleDetails').addEventListener('click', function() {
                const detailsDiv = document.getElementById('currentDetails');
                const toggleBtn = document.getElementById('toggleDetails');
                
                if (detailsDiv.style.display === 'block') {
                    detailsDiv.style.display = 'none';
                    toggleBtn.textContent = 'Show Current Details';
                } else {
                    detailsDiv.style.display = 'block';
                    toggleBtn.textContent = 'Hide Current Details';
                    
                    // Fetch current details if not already loaded
                    if (document.getElementById('detailsJson').textContent === 'Loading...') {
                        fetchCurrentDetails();
                    }
                }
            });
            
            function fetchCurrentDetails() {
                const objectId = '""" + object_id + """';
                const objectType = '""" + object_type.lower() + """';
                const endpoint = objectType === 'ad' ? 
                    `/api/ad?ad_id=${objectId}&token=""" + token + """` : 
                    `/api/adset?adset_id=${objectId}&token=""" + token + """`;
                
                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('detailsJson').textContent = JSON.stringify(data, null, 2);
                    })
                    .catch(error => {
                        document.getElementById('detailsJson').textContent = `Error fetching details: ${error}`;
                    });
            }
        </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode('utf-8'))
    
    def _handle_adset_api(self):
        """Handle API requests for adset data"""
        # Parse query parameters
        query = parse_qs(urlparse(self.path).query)
        adset_id = query.get("adset_id", [""])[0]
        token = query.get("token", [""])[0]
        
        from .api import make_api_request
        
        # Call the Graph API directly
        async def get_adset_data():
            try:
                endpoint = f"{adset_id}"
                params = {
                    "fields": "id,name,campaign_id,status,daily_budget,lifetime_budget,targeting,bid_amount,bid_strategy,optimization_goal,billing_event,start_time,end_time,created_time,updated_time,attribution_spec,destination_type,promoted_object,pacing_type,budget_remaining,frequency_control_specs"
                }
                
                result = await make_api_request(endpoint, token, params)
                
                # Check if result is a string (possibly an error message)
                if isinstance(result, str):
                    try:
                        # Try to parse as JSON
                        parsed_result = json.loads(result)
                        return parsed_result
                    except json.JSONDecodeError:
                        # Return error object if can't parse as JSON
                        return {"error": {"message": result}}
                        
                # If the result is None, return an error object
                if result is None:
                    return {"error": {"message": "Empty response from API"}}
                    
                return result
            except Exception as e:
                logger.error(f"Error in get_adset_data: {str(e)}")
                return {"error": {"message": f"Error fetching ad set data: {str(e)}"}}
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_adset_data())
        loop.close()
        
        # Return the result
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
    
    def _handle_ad_api(self):
        """Handle API requests for ad data"""
        # Parse query parameters
        query = parse_qs(urlparse(self.path).query)
        ad_id = query.get("ad_id", [""])[0]
        token = query.get("token", [""])[0]
        
        from .api import make_api_request
        
        # Call the Graph API directly
        async def get_ad_data():
            endpoint = f"{ad_id}"
            params = {
                "fields": "id,name,adset_id,campaign_id,status,creative,created_time,updated_time,bid_amount,conversion_domain,tracking_specs,preview_shareable_link"
            }
            return await make_api_request(endpoint, token, params)
        
        # Run the async function to get data
        result = asyncio.run(get_ad_data())
        
        # Send the response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        if isinstance(result, dict):
            self.wfile.write(json.dumps(result, indent=2).encode())
        else:
            self.wfile.write(json.dumps({"error": "Failed to get ad data"}, indent=2).encode())
    
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
        
        print(f"Shutting down callback server on port {callback_server_port}")
        
        # Shutdown the server if it exists
        if callback_server_instance:
            try:
                callback_server_instance.shutdown()
                callback_server_instance = None
                callback_server_running = False
                print("Callback server has been shut down")
            except Exception as e:
                print(f"Error shutting down callback server: {e}")
        else:
            print("No server instance to shut down")

def start_callback_server() -> int:
    """
    Start the callback server if it's not already running
    
    Returns:
        Port number the server is running on
    
    Raises:
        Exception: If callback server is disabled via META_ADS_DISABLE_CALLBACK_SERVER environment variable
    """
    # Check if callback server is disabled via environment variable
    if os.environ.get("META_ADS_DISABLE_CALLBACK_SERVER"):
        logger.info("Callback server disabled via META_ADS_DISABLE_CALLBACK_SERVER environment variable")
        print("Callback server is disabled. OAuth authentication flow cannot be used.")
        raise Exception("Callback server disabled via META_ADS_DISABLE_CALLBACK_SERVER environment variable. Use alternative authentication methods.")
    
    global callback_server_thread, callback_server_running, callback_server_port, callback_server_instance, server_shutdown_timer
    
    with callback_server_lock:
        if callback_server_running:
            print(f"Callback server already running on port {callback_server_port}")
            
            # Reset the shutdown timer if one exists
            if server_shutdown_timer is not None:
                server_shutdown_timer.cancel()
            
            server_shutdown_timer = threading.Timer(CALLBACK_SERVER_TIMEOUT, shutdown_callback_server)
            server_shutdown_timer.daemon = True
            server_shutdown_timer.start()
            print(f"Reset server shutdown timer to {CALLBACK_SERVER_TIMEOUT} seconds")
            
            return callback_server_port
        
        # Find an available port
        port = 8888
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    break
            except OSError:
                port += 1
                if attempt == max_attempts - 1:
                    raise Exception(f"Could not find an available port after {max_attempts} attempts")
        
        callback_server_port = port
        
        try:
            # Create and start server in a daemon thread
            server = HTTPServer(('localhost', port), CallbackHandler)
            callback_server_instance = server
            print(f"Callback server starting on port {port}")
            
            # Create a simple flag to signal when the server is ready
            server_ready = threading.Event()
            
            def server_thread():
                try:
                    # Signal that the server thread has started
                    server_ready.set()
                    print(f"Callback server is now ready on port {port}")
                    # Start serving HTTP requests
                    server.serve_forever()
                except Exception as e:
                    print(f"Server error: {e}")
                finally:
                    with callback_server_lock:
                        global callback_server_running
                        callback_server_running = False
            
            callback_server_thread = threading.Thread(target=server_thread)
            callback_server_thread.daemon = True
            callback_server_thread.start()
            
            # Wait for server to be ready (up to 5 seconds)
            if not server_ready.wait(timeout=5):
                print("Warning: Timeout waiting for server to start, but continuing anyway")
            
            callback_server_running = True
            
            # Set a timer to shutdown the server after CALLBACK_SERVER_TIMEOUT seconds
            if server_shutdown_timer is not None:
                server_shutdown_timer.cancel()
            
            server_shutdown_timer = threading.Timer(CALLBACK_SERVER_TIMEOUT, shutdown_callback_server)
            server_shutdown_timer.daemon = True
            server_shutdown_timer.start()
            print(f"Server will automatically shut down after {CALLBACK_SERVER_TIMEOUT} seconds of inactivity")
            
            # Verify the server is actually accepting connections
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect(('localhost', port))
                print(f"Confirmed server is accepting connections on port {port}")
            except Exception as e:
                print(f"Warning: Could not verify server connection: {e}")
                
            return port
            
        except Exception as e:
            print(f"Error starting callback server: {e}")
            # Try again with a different port in case of bind issues
            if "address already in use" in str(e).lower():
                print("Port may be in use, trying a different port...")
                return start_callback_server()  # Recursive call with a new port
            raise e 