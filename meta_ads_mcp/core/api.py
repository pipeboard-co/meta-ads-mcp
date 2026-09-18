"""Core API functionality for Meta Ads API."""

from typing import Any, Dict, Optional, Callable
import json
import hmac
import hashlib
import httpx
import asyncio
import functools
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import re
from . import auth
from .auth import needs_authentication, auth_manager, start_callback_server, shutdown_callback_server
from .utils import logger


# Query-string params that must never leak to the caller in error payloads.
# access_token is the operator credential; appsecret_proof is derived from
# the app secret + access token via HMAC and is similarly sensitive.
# See GHSA-9gw6-46qc-99vr.
_SENSITIVE_QUERY_PARAMS = frozenset(
    {
        "access_token",
        "appsecret_proof",
        "client_secret",
        "authorization",
        "api_key",
    }
)
_SENSITIVE_KEYS = _SENSITIVE_QUERY_PARAMS | frozenset(
    {
        "cookie",
        "cookies",
        "set_cookie",
        "password",
        "refresh_token",
        "session_token",
    }
)
_BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_RAW_QUERY_SECRET_RE = re.compile(
    r"(?i)(\b(?:access_token|appsecret_proof|client_secret|authorization|api_key)=)"
    r"([^&\s#\"'<>]+)"
)
_ENCODED_QUERY_SECRET_RE = re.compile(
    r"(?i)((?:access_token|appsecret_proof|client_secret|authorization|api_key)%3d)"
    r"(.+?)(?=%26|$)"
)


class _SecretValues(tuple):
    """Iterable sentinels whose representation can never disclose a secret."""

    def __new__(cls, values=()):
        return super().__new__(
            cls,
            (str(value) for value in values if isinstance(value, str) and value),
        )

    def __repr__(self) -> str:
        return f"<redacted-secret-values count={len(self)}>"


def _is_sensitive_key(key: Any) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return (
        normalized in _SENSITIVE_KEYS
        or normalized.endswith("_access_token")
        or normalized.endswith("_client_secret")
        or normalized.endswith("_password")
    )


def _sanitize_string(value: str, secrets: tuple[str, ...]) -> str:
    sanitized = value
    for secret in secrets:
        if secret:
            sanitized = sanitized.replace(secret, "REDACTED")
    sanitized = _BEARER_RE.sub("Bearer REDACTED", sanitized)
    sanitized = _RAW_QUERY_SECRET_RE.sub(r"\1REDACTED", sanitized)
    sanitized = _ENCODED_QUERY_SECRET_RE.sub(r"\1REDACTED", sanitized)
    if "://" in sanitized and "?" in sanitized:
        sanitized = _redact_url(sanitized)
    return sanitized


def _opaque_cursor(paging: Dict[str, Any], secrets: tuple[str, ...]) -> str | None:
    cursors = paging.get("cursors")
    cursor = cursors.get("after") if isinstance(cursors, dict) else None
    if not isinstance(cursor, str) or not cursor:
        return None
    cursor = _sanitize_string(cursor, secrets)
    if "://" in cursor or "?" in cursor or "&" in cursor:
        return None
    return cursor


def _sanitize_mcp_payload(value: Any, secrets=()) -> Any:
    """Recursively sanitize one value before it crosses the MCP boundary.

    Provider pagination URLs are replaced with an opaque cursor envelope.  The
    caller must pass only credentials already available to the process; they
    are used as sentinels and are never retained in the returned object.
    """

    known_secrets = _SecretValues(secrets)
    if isinstance(value, dict):
        paging = value.get("paging")
        data = value.get("data")
        if isinstance(data, list) and isinstance(paging, dict):
            cursor = _opaque_cursor(paging, known_secrets)
            normalized = {
                "items": _sanitize_mcp_payload(data, known_secrets),
                "next_cursor": cursor,
                "has_more": bool(paging.get("next") and cursor),
            }
            for key, nested in value.items():
                if key not in {"data", "paging"}:
                    normalized[key] = _sanitize_mcp_payload(nested, known_secrets)
            return normalized
        return {
            key: (
                "REDACTED"
                if _is_sensitive_key(key)
                else _sanitize_mcp_payload(nested, known_secrets)
            )
            for key, nested in value.items()
        }
    if isinstance(value, list):
        return [_sanitize_mcp_payload(item, known_secrets) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_mcp_payload(item, known_secrets) for item in value)
    if isinstance(value, str):
        return _sanitize_string(value, known_secrets)
    return value


def _assert_no_secret(value: Any, secrets=()) -> None:
    """Fail closed if a known secret or credential-shaped value remains."""

    secrets = _SecretValues(secrets)
    serialized = json.dumps(value, default=str, ensure_ascii=False)
    for secret in secrets:
        if isinstance(secret, str) and secret and secret in serialized:
            raise McpToolError("unsafe_output_blocked")
    for match in _BEARER_RE.finditer(serialized):
        if not match.group(0).upper().endswith("REDACTED"):
            raise McpToolError("unsafe_output_blocked")
    raw_match = _RAW_QUERY_SECRET_RE.search(serialized)
    if raw_match and raw_match.group(2).upper() != "REDACTED":
        raise McpToolError("unsafe_output_blocked")
    encoded_match = _ENCODED_QUERY_SECRET_RE.search(serialized)
    if encoded_match and encoded_match.group(2).upper() != "REDACTED":
        raise McpToolError("unsafe_output_blocked")


def _redact_url(url: str) -> str:
    """Strip sensitive query params (access_token, appsecret_proof) from a URL.

    Used to scrub Graph API URLs before they are returned to MCP callers in
    error responses.
    """
    if not url:
        return url
    try:
        parts = urlsplit(url)
        if not parts.query:
            return url
        scrubbed = [
            (k, "REDACTED" if k.lower() in _SENSITIVE_QUERY_PARAMS else v)
            for k, v in parse_qsl(parts.query, keep_blank_values=True)
        ]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(scrubbed), parts.fragment))
    except Exception:
        # Be conservative: if parsing fails, drop the query string entirely.
        return url.split("?", 1)[0]

class McpToolError(Exception):
    """Base class for MCP tool errors that must set isError: true.

    Subclasses should be raised (not returned) from tool handlers.
    meta_api_tool re-raises these so FastMCP sees them and sets
    isError: true in the JSON-RPC response, which triggers the usage
    credit refund in the Next.js proxy.
    """
    pass


def ensure_act_prefix(account_id: str) -> str:
    """Ensure account_id has the 'act_' prefix required by Meta's Graph API."""
    if account_id and not account_id.startswith("act_"):
        return f"act_{account_id}"
    return account_id


# Constants
META_GRAPH_API_VERSION = "v24.0"
META_GRAPH_API_BASE = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}"
USER_AGENT = "meta-ads-mcp/1.0"

# Log key environment and configuration at startup
logger.info("Core API module initialized")
logger.info(f"Graph API Version: {META_GRAPH_API_VERSION}")
logger.info(f"META_APP_ID env var present: {'Yes' if os.environ.get('META_APP_ID') else 'No'}")
logger.info(f"META_APP_SECRET env var present (appsecret_proof will be {'enabled' if os.environ.get('META_APP_SECRET') else 'disabled'})")

def _is_account_disabled_error(error_code: Any, error_subcode: Any) -> bool:
    """Return True when a Graph error indicates the ad account / action is
    blocked by Meta policy rather than the token being invalid.

    Currently covers:
      - code 368: "The action attempted has been deemed abusive or is otherwise
        disallowed." Token is still valid; the specific action was rejected.
      - code 190 + subcode 459: user has been checkpointed by Facebook
        security. Token is not expired; the user must clear the checkpoint on
        Facebook before further calls succeed. Telling them to reconnect on
        Pipeboard does not unblock them.

    Other code 190 subcodes (458, 460, 463, 464, 467) are genuine session /
    credential errors — keep the existing invalidate-token behavior for those.
    """
    if error_code == 368:
        return True
    if error_code == 190 and error_subcode == 459:
        return True
    return False


class GraphAPIError(Exception):
    """Exception raised for errors from the Graph API."""
    def __init__(self, error_data: Dict[str, Any]):
        self.error_data = error_data
        self.message = error_data.get('message', 'Unknown Graph API error')
        super().__init__(self.message)

        # Log error details
        logger.error(f"Graph API Error: {self.message}")
        logger.debug(f"Error details: {error_data}")

        code = error_data.get("code")
        subcode = error_data.get("error_subcode")

        # Check if this is an auth error (code 4 is rate limiting, NOT auth)
        if code in [190, 102]:
            if _is_account_disabled_error(code, subcode):
                logger.warning(
                    f"Account/action policy block (code={code}, subcode={subcode}). "
                    f"Token is still valid — NOT invalidating."
                )
            else:
                logger.warning(f"Auth error detected (code: {code}). Invalidating token.")
                auth_manager.invalidate_token()
        elif code == 368:
            logger.warning(
                f"Action disallowed (code=368, subcode={subcode}). "
                f"Token is still valid — NOT invalidating."
            )
        elif code == 4:
            logger.warning(f"Rate limit error detected (code: 4, subcode: {error_data.get('error_subcode', 'N/A')}). Token is still valid — NOT invalidating.")


def _log_meta_rate_limit_headers(headers: dict, endpoint: str) -> None:
    """Log Meta's rate limit headers for observability (X-App-Usage, X-Business-Use-Case-Usage)."""
    app_usage = headers.get("x-app-usage")
    biz_usage = headers.get("x-business-use-case-usage")
    ad_account_usage = headers.get("x-ad-account-usage")

    if app_usage or biz_usage or ad_account_usage:
        usage_data = {}
        if app_usage:
            try:
                usage_data["app_usage"] = json.loads(app_usage)
            except (json.JSONDecodeError, TypeError):
                usage_data["app_usage_raw"] = str(app_usage)
        if biz_usage:
            try:
                usage_data["business_use_case_usage"] = json.loads(biz_usage)
            except (json.JSONDecodeError, TypeError):
                usage_data["business_use_case_usage_raw"] = str(biz_usage)
        if ad_account_usage:
            try:
                usage_data["ad_account_usage"] = json.loads(ad_account_usage)
            except (json.JSONDecodeError, TypeError):
                usage_data["ad_account_usage_raw"] = str(ad_account_usage)

        # Warn at high usage levels (any field >= 80%)
        is_high = False
        for key, val in usage_data.items():
            if isinstance(val, dict):
                for metric, pct in val.items():
                    if isinstance(pct, (int, float)) and pct >= 80:
                        is_high = True
                        break

        log_fn = logger.warning if is_high else logger.info
        log_fn(f"meta_rate_limit_usage endpoint={endpoint} {json.dumps(usage_data)}")


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
    
    # Shallow-copy the caller's params: this function injects credentials
    # (access_token, appsecret_proof) and JSON-stringifies dict/list values
    # below. Mutating the caller's dict leaked the access token into tool
    # responses that echo their params back (e.g. update_ad_creative's
    # attempted_updates on error 1815573).
    request_params = dict(params) if params else {}
    request_params["access_token"] = access_token

    # Add appsecret_proof when META_APP_SECRET is configured.
    # Required for system user tokens and recommended by Meta for all
    # server-to-server API calls to verify token authenticity.
    # See: https://developers.facebook.com/docs/graph-api/securing-requests/
    app_secret = os.environ.get("META_APP_SECRET", "")
    if app_secret and access_token:
        request_params["appsecret_proof"] = hmac.new(
            app_secret.encode("utf-8"),
            access_token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    # Logging the request (masking token for security)
    masked_params = {k: "***MASKED***" if k in ("access_token", "appsecret_proof") else v for k, v in request_params.items()}
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
            elif method == "PUT":
                # PUT for updates that Meta requires via PUT (e.g., creative_features_spec).
                # Meta expects access_token as a query param, not in the body.
                query_params = {}
                body_params = {}
                for key, value in request_params.items():
                    if key in ("access_token", "appsecret_proof"):
                        query_params[key] = value
                    elif isinstance(value, (list, dict)):
                        body_params[key] = json.dumps(value)
                    else:
                        body_params[key] = value
                response = await client.put(url, params=query_params, data=body_params, headers=headers, timeout=30.0)
            elif method == "DELETE":
                response = await client.delete(url, params=request_params, headers=headers, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            logger.debug(f"API Response status: {response.status_code}")

            # Log Meta rate limit headers for observability
            _log_meta_rate_limit_headers(response.headers, endpoint)

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

            # Log Meta rate limit headers even on errors
            _log_meta_rate_limit_headers(e.response.headers, endpoint)

            # Check for rate limit errors vs authentication errors.
            # Code 4 is a rate limit (NOT auth) — do NOT invalidate token.
            error_code = None
            error_subcode = None
            is_account_disabled = False
            if "error" in error_info:
                error_obj = error_info.get("error", {})
                if isinstance(error_obj, dict):
                    error_code = error_obj.get("code")
                    error_subcode = error_obj.get("error_subcode")

                if error_code == 4:
                    # Application-level rate limit — token is still valid
                    logger.warning(
                        f"Facebook API rate limit (code=4, subcode={error_subcode}, "
                        f"msg={error_obj.get('error_user_msg', error_obj.get('message', 'N/A'))}). "
                        f"Token is still valid — NOT invalidating."
                    )
                elif _is_account_disabled_error(error_code, error_subcode):
                    # Policy-side block (account or action). Token is still
                    # valid; surface a distinct flag so callers can branch
                    # without treating this as a stale-token reconnect.
                    is_account_disabled = True
                    logger.warning(
                        f"Account/action policy block (code={error_code}, subcode={error_subcode}). "
                        f"Token is still valid — NOT invalidating."
                    )
                elif error_code in [190, 102, 200, 10]:
                    logger.warning(f"Detected Facebook API auth error: {error_code}")
                    if error_code == 200 and "Provide valid app ID" in error_obj.get("message", ""):
                        logger.error("Meta API authentication configuration issue")
                        logger.error(f"Current app_id: {app_id}")
                        return {
                            "error": {
                                "message": "Meta API authentication configuration issue. Please check your app credentials.",
                                "original_error": error_obj.get("message"),
                                "code": error_code
                            }
                        }
                    auth_manager.invalidate_token()
                elif e.response.status_code in [401, 403]:
                    logger.warning(f"Detected authentication error ({e.response.status_code})")
                    auth_manager.invalidate_token()
            elif e.response.status_code in [401, 403]:
                logger.warning(f"Detected authentication error ({e.response.status_code})")
                auth_manager.invalidate_token()

            # Include full details for technical users. URLs are scrubbed of
            # access_token/appsecret_proof — see GHSA-9gw6-46qc-99vr.
            full_response = {
                "headers": dict(e.response.headers),
                "status_code": e.response.status_code,
                "url": _redact_url(str(e.response.url)),
                "reason": getattr(e.response, "reason_phrase", "Unknown reason"),
                "request_method": e.request.method,
                "request_url": _redact_url(str(e.request.url))
            }

            # Return a properly structured error object
            error_payload: Dict[str, Any] = {
                "message": f"HTTP Error: {e.response.status_code}",
                "details": error_info,
                "full_response": full_response,
            }
            if is_account_disabled:
                error_payload["is_account_disabled"] = True
                if error_code is not None:
                    error_payload["error_code"] = error_code
                if error_subcode is not None:
                    error_payload["error_subcode"] = error_subcode
            return {"error": error_payload}
        
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
            logger.debug("Positional arg count: %d", len(args))
            # Log kwargs without sensitive info
            safe_kwargs = {
                k: ("***REDACTED***" if _is_sensitive_key(k) else v)
                for k, v in kwargs.items()
            }
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
                        if auth_manager.app_id == "YOUR_META_APP_ID" or not auth_manager.app_id:
                            logger.error("TOKEN VALIDATION FAILED: No valid app_id configured")
                            logger.error("Please set META_APP_ID environment variable or configure in your code")
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

                logger.error("TOKEN VALIDATION SUMMARY:")
                logger.error(f"- Current app_id: '{app_id}'")
                logger.error(f"- Environment META_APP_ID: '{os.environ.get('META_APP_ID', 'Not set')}'")
                logger.error(f"- META_ACCESS_TOKEN set: {'Yes' if os.environ.get('META_ACCESS_TOKEN') else 'No'}")

                if app_id == "YOUR_META_APP_ID" or not app_id:
                    logger.error("ISSUE DETECTED: No valid Meta App ID configured")
                    logger.error("ACTION REQUIRED: Set META_APP_ID environment variable with a valid App ID")

                if os.environ.get("PIPEBOARD_API_TOKEN"):
                    logger.error(
                        "NOTE: PIPEBOARD_API_TOKEN is set but is ignored by this package. "
                        "Use META_ACCESS_TOKEN, or the hosted MCP at "
                        "https://meta-ads.mcp.pipeboard.co/ which does accept it. "
                        "The Pipeboard CLI also still uses it, so leave it set if you use that."
                    )

                return json.dumps({
                    "error": {
                        "message": "Authentication Required",
                        "details": {
                            "description": "You need to authenticate with the Meta API before using this tool",
                            "action_required": "Please authenticate first",
                            "auth_url": auth_url,
                            "configuration_status": {
                                "app_id_configured": bool(app_id) and app_id != "YOUR_META_APP_ID",
                            },
                            "options": [
                                {
                                    "option": "Use the hosted Meta Ads MCP (no Meta app needed)",
                                    "url": "https://meta-ads.mcp.pipeboard.co/",
                                    "how": "Point your MCP client at this URL and authenticate with your Pipeboard API token."
                                },
                                {
                                    "option": "Bring your own Meta access token",
                                    "url": "https://developers.facebook.com/apps/",
                                    "how": "Create your own Meta app, generate an access token, and set META_ACCESS_TOKEN."
                                }
                            ],
                            "troubleshooting": "Check logs for TOKEN VALIDATION FAILED messages",
                            "markdown_link": f"[Click here to authenticate with Meta Ads API]({auth_url})"
                        }
                    }
                }, indent=2)
                
            # Call the original function
            result = await func(*args, **kwargs)
            known_secrets = tuple(
                secret
                for secret in (
                    kwargs.get("access_token"),
                    os.environ.get("META_ACCESS_TOKEN"),
                    os.environ.get("META_APP_SECRET"),
                )
                if isinstance(secret, str) and secret
            )
            
            # If the result is a string (JSON), try to parse it to check for errors
            if isinstance(result, str):
                try:
                    result_dict = json.loads(result)
                    if "error" in result_dict:
                        logger.error(
                            "Error in API response: %s",
                            _sanitize_mcp_payload(result_dict["error"], known_secrets),
                        )
                        # If this is an app ID error, log more details
                        if isinstance(result_dict.get("details", {}).get("error", {}), dict):
                            error_obj = result_dict["details"]["error"]
                            if error_obj.get("code") == 200 and "Provide valid app ID" in error_obj.get("message", ""):
                                logger.error("Meta API authentication configuration issue")
                                logger.error(f"Current app_id: {app_id}")
                                # Replace the confusing error with a more user-friendly one
                                result_dict = {
                                    "error": {
                                        "message": "Meta API Configuration Issue",
                                        "details": {
                                            "description": "Your Meta API app is not properly configured",
                                            "action_required": "Check your META_APP_ID environment variable",
                                            "current_app_id": app_id,
                                            "original_error": error_obj.get("message")
                                        }
                                    }
                                }
                    result = result_dict
                except Exception:
                    # Not JSON or other parsing error, wrap it in a dictionary
                    result = {"data": result}
            
            sanitized = _sanitize_mcp_payload(result, known_secrets)
            _assert_no_secret(sanitized, known_secrets)
            if isinstance(sanitized, (dict, list, tuple)):
                return json.dumps(sanitized, indent=2)
            return sanitized
        except McpToolError:
            raise  # Let FastMCP set isError: true and refund the usage credit
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2)

    return wrapper
