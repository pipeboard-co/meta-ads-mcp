"""Duplication functionality for Meta Ads API."""

import json
import logging
import os
import httpx
from typing import Optional, Dict, Any, List, Union
from .server import mcp_server
from .api import meta_api_tool
from . import auth
from .http_auth_integration import FastMCPAuthIntegration

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised on 429 so FastMCP sets isError: true in the MCP response."""
    pass


# Only register the duplication functions if the environment variable is set
ENABLE_DUPLICATION = bool(os.environ.get("META_ADS_ENABLE_DUPLICATION", ""))

if ENABLE_DUPLICATION:
    @mcp_server.tool()
    @meta_api_tool
    async def duplicate_campaign(
        campaign_id: str,
        access_token: Optional[str] = None,
        name_suffix: Optional[str] = " - Copy",
        include_ad_sets: bool = True,
        include_ads: bool = True,
        include_creatives: bool = True,
        copy_schedule: bool = False,
        new_daily_budget: Optional[float] = None,
        new_status: Optional[str] = "PAUSED",
        pb_token: Optional[str] = None
    ) -> str:
        """
        Duplicate a Meta Ads campaign with all its ad sets and ads.

        Recommended: Use this to run robust experiments.

        Args:
            campaign_id: Meta Ads campaign ID to duplicate
            name_suffix: Suffix to add to the duplicated campaign name
            include_ad_sets: Whether to duplicate ad sets within the campaign
            include_ads: Whether to duplicate ads within ad sets
            include_creatives: Whether to duplicate ad creatives
            copy_schedule: Whether to copy the campaign schedule
            new_daily_budget: Override the daily budget for the new campaign
            new_status: Status for the new campaign (ACTIVE or PAUSED)
        """
        return await _forward_duplication_request(
            "campaign",
            campaign_id,
            access_token,
            {
                "name_suffix": name_suffix,
                "include_ad_sets": include_ad_sets,
                "include_ads": include_ads,
                "include_creatives": include_creatives,
                "copy_schedule": copy_schedule,
                "new_daily_budget": new_daily_budget,
                "new_status": new_status,
                "pb_token": pb_token
            }
        )

    @mcp_server.tool()
    @meta_api_tool
    async def duplicate_adset(
        adset_id: str,
        access_token: Optional[str] = None,
        target_campaign_id: Optional[str] = None,
        name_suffix: Optional[str] = " - Copy",
        include_ads: bool = True,
        include_creatives: bool = True,
        new_daily_budget: Optional[float] = None,
        new_targeting: Optional[Dict[str, Any]] = None,
        new_status: Optional[str] = "PAUSED",
        pb_token: Optional[str] = None
    ) -> str:
        """
        Duplicate a Meta Ads ad set with its ads.

        Recommended: Use this to run robust experiments.

        Args:
            adset_id: Meta Ads ad set ID to duplicate
            target_campaign_id: Campaign ID to move the duplicated ad set to (optional)
            name_suffix: Suffix to add to the duplicated ad set name
            include_ads: Whether to duplicate ads within the ad set
            include_creatives: Whether to duplicate ad creatives
            new_daily_budget: Override the daily budget for the new ad set
            new_targeting: Override targeting settings for the new ad set
            new_status: Status for the new ad set (ACTIVE or PAUSED)
        """
        return await _forward_duplication_request(
            "adset",
            adset_id,
            access_token,
            {
                "target_campaign_id": target_campaign_id,
                "name_suffix": name_suffix,
                "include_ads": include_ads,
                "include_creatives": include_creatives,
                "new_daily_budget": new_daily_budget,
                "new_targeting": new_targeting,
                "new_status": new_status,
                "pb_token": pb_token
            }
        )

    @mcp_server.tool()
    @meta_api_tool
    async def duplicate_ad(
        ad_id: str,
        access_token: Optional[str] = None,
        target_adset_id: Optional[str] = None,
        name_suffix: Optional[str] = " - Copy",
        duplicate_creative: bool = True,
        new_creative_name: Optional[str] = None,
        new_status: Optional[str] = "PAUSED",
        pb_token: Optional[str] = None
    ) -> str:
        """
        Duplicate a Meta Ads ad.

        Recommended: Use this to run robust experiments.

        Args:
            ad_id: Meta Ads ad ID to duplicate
            target_adset_id: Ad set ID to move the duplicated ad to (optional)
            name_suffix: Suffix to add to the duplicated ad name
            duplicate_creative: Whether to duplicate the ad creative
            new_creative_name: Override name for the duplicated creative
            new_status: Status for the new ad (ACTIVE or PAUSED)
        """
        return await _forward_duplication_request(
            "ad",
            ad_id,
            access_token,
            {
                "target_adset_id": target_adset_id,
                "name_suffix": name_suffix,
                "duplicate_creative": duplicate_creative,
                "new_creative_name": new_creative_name,
                "new_status": new_status,
                "pb_token": pb_token
            }
        )

    @mcp_server.tool()
    @meta_api_tool
    async def duplicate_creative(
        creative_id: str,
        access_token: Optional[str] = None,
        name_suffix: Optional[str] = " - Copy",
        new_primary_text: Optional[str] = None,
        new_headline: Optional[str] = None,
        new_description: Optional[str] = None,
        new_cta_type: Optional[str] = None,
        new_destination_url: Optional[str] = None,
        pb_token: Optional[str] = None
    ) -> str:
        """
        Duplicate a Meta Ads creative.

        Recommended: Use this to run robust experiments.

        Args:
            creative_id: Meta Ads creative ID to duplicate
            name_suffix: Suffix to add to the duplicated creative name
            new_primary_text: Override the primary text for the new creative
            new_headline: Override the headline for the new creative
            new_description: Override the description for the new creative
            new_cta_type: Override the call-to-action type for the new creative
            new_destination_url: Override the destination URL for the new creative
        """
        return await _forward_duplication_request(
            "creative",
            creative_id,
            access_token,
            {
                "name_suffix": name_suffix,
                "new_primary_text": new_primary_text,
                "new_headline": new_headline,
                "new_description": new_description,
                "new_cta_type": new_cta_type,
                "new_destination_url": new_destination_url,
                "pb_token": pb_token
            }
        )


async def _forward_duplication_request(resource_type: str, resource_id: str, access_token: str, options: Dict[str, Any]) -> str:
    """
    Forward duplication request to the cloud-hosted MCP API using dual-header authentication.
    
    This implements the dual-header authentication pattern for MCP server callbacks:
    - Authorization: Bearer <facebook_token> - Facebook access token for Meta API calls
    - X-Pipeboard-Token: <pipeboard_token> - Pipeboard API token for authentication
    
    Args:
        resource_type: Type of resource to duplicate (campaign, adset, ad, creative)
        resource_id: ID of the resource to duplicate
        access_token: Meta API access token (optional, will use context if not provided)
        options: Duplication options
    """
    try:
        # Get tokens from the request context that were set by the HTTP auth middleware
        # In the dual-header authentication pattern:
        # - Pipeboard token comes from X-Pipeboard-Token header (for authentication)
        # - Facebook token comes from Authorization header (for Meta API calls)

        # Get tokens from context set by AuthInjectionMiddleware
        pipeboard_token = FastMCPAuthIntegration.get_pipeboard_token()
        token_source = "contextvar" if pipeboard_token else None
        facebook_token = FastMCPAuthIntegration.get_auth_token()

        # Fallback: proxy injects pb_token into arguments when ContextVar
        # is unreachable (Starlette BaseHTTPMiddleware -> FastMCP dispatch breaks it)
        if not pipeboard_token:
            pipeboard_token = options.pop('pb_token', None)
            if pipeboard_token:
                token_source = "injected_argument"
                logger.info("Using pipeboard_token from injected argument (ContextVar fallback)")
        else:
            # Remove pb_token from options so it is not sent to the API
            options.pop('pb_token', None)

        # Use provided access_token parameter if no Facebook token found in context
        if not facebook_token:
            facebook_token = access_token if access_token else await auth.get_current_access_token()

        logger.info(
            "Duplication auth: pipeboard=%s, facebook=%s, source=%s",
            "set" if pipeboard_token else "MISSING",
            "set" if facebook_token else "MISSING",
            token_source or "none"
        )

        # Validate we have both required tokens
        if not pipeboard_token:
            return json.dumps({
                "error": "authentication_required",
                "message": "Pipeboard API token not found",
                "details": {
                    "required": "Valid Pipeboard token via X-Pipeboard-Token header",
                    "received_headers": "Check that the MCP server is forwarding the X-Pipeboard-Token header"
                }
            }, indent=2)
            
        if not facebook_token:
            return json.dumps({
                "error": "authentication_required",
                "message": "Meta Ads access token not found",
                "details": {
                    "required": "Valid Meta access token from authenticated session",
                    "check": "Ensure Facebook account is connected and token is valid"
                }
            }, indent=2)

        # Construct the API endpoint.
        # PIPEBOARD_API_BASE_URL allows overriding for local e2e testing.
        base_url = os.environ.get("PIPEBOARD_API_BASE_URL", "https://mcp.pipeboard.co")
        endpoint = f"{base_url}/api/meta/duplicate/{resource_type}/{resource_id}"
        
        # Prepare the dual-header authentication as per API documentation
        headers = {
            "Authorization": f"Bearer {facebook_token}",  # Facebook token for Meta API
            "X-Pipeboard-Token": pipeboard_token,         # Pipeboard token for auth
            "Content-Type": "application/json",
            "User-Agent": "meta-ads-mcp/1.0"
        }
        
        # Remove None values from options
        clean_options = {k: v for k, v in options.items() if v is not None}
        
        # Make the request to the cloud service
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=clean_options
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.dumps(result, indent=2)
            elif response.status_code == 400:
                # Validation failed
                try:
                    error_data = response.json()
                    return json.dumps({
                        "success": False,
                        "error": "validation_failed",
                        "errors": error_data.get("errors", [response.text]),
                        "warnings": error_data.get("warnings", [])
                    }, indent=2)
                except:
                    return json.dumps({
                        "success": False,
                        "error": "validation_failed",
                        "errors": [response.text],
                        "warnings": []
                    }, indent=2)
            elif response.status_code == 401:
                return json.dumps({
                    "success": False,
                    "error": "authentication_error",
                    "message": "Invalid or expired API token"
                }, indent=2)
            elif response.status_code == 402:
                try:
                    error_data = response.json()
                    return json.dumps({
                        "success": False,
                        "error": "subscription_required",
                        "message": error_data.get("message", "This feature is not available in your current plan"),
                        "upgrade_url": error_data.get("upgrade_url", "https://pipeboard.co/upgrade"),
                        "suggestion": error_data.get("suggestion", "Please upgrade your account to access this feature")
                    }, indent=2)
                except:
                    return json.dumps({
                        "success": False,
                        "error": "subscription_required",
                        "message": "This feature is not available in your current plan",
                        "upgrade_url": "https://pipeboard.co/upgrade",
                        "suggestion": "Please upgrade your account to access this feature"
                    }, indent=2)
            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    # Check if this is a premium feature error
                    if error_data.get("error") == "premium_feature":
                        return json.dumps({
                            "success": False,
                            "error": "premium_feature_required",
                            "message": error_data.get("message", "This is a premium feature that requires subscription"),
                            "details": error_data.get("details", {
                                "upgrade_url": "https://pipeboard.co/upgrade",
                                "suggestion": "Please upgrade your account to access this feature"
                            })
                        }, indent=2)
                    else:
                        # Default to facebook connection required
                        return json.dumps({
                            "success": False,
                            "error": "facebook_connection_required",
                            "message": error_data.get("message", "You need to connect your Facebook account first"),
                            "details": error_data.get("details", {
                                "login_flow_url": "/connections",
                                "auth_flow_url": "/api/meta/auth"
                            })
                        }, indent=2)
                except:
                    return json.dumps({
                        "success": False,
                        "error": "facebook_connection_required",
                        "message": "You need to connect your Facebook account first",
                        "details": {
                            "login_flow_url": "/connections",
                            "auth_flow_url": "/api/meta/auth"
                        }
                    }, indent=2)
            elif response.status_code == 404:
                return json.dumps({
                    "success": False,
                    "error": "resource_not_found",
                    "message": f"{resource_type.title()} not found or access denied",
                    "suggestion": f"Verify the {resource_type} ID and your Facebook account permissions"
                }, indent=2)
            elif response.status_code == 429:
                # Raise so FastMCP sets isError: true in MCP response,
                # enabling the Next.js proxy to detect and retry.
                raise RateLimitError(json.dumps({
                    "error": "rate_limit_exceeded",
                    "message": "Meta API rate limit exceeded",
                    "details": {
                        "suggestion": "Please wait before retrying",
                        "retry_after": response.headers.get("Retry-After", "60")
                    }
                }, indent=2))
            elif response.status_code == 502:
                try:
                    error_data = response.json()
                    return json.dumps({
                        "success": False,
                        "error": "meta_api_error",
                        "message": error_data.get("message", "Facebook API error"),
                        "recoverable": True,
                        "suggestion": "Please wait 5 minutes before retrying"
                    }, indent=2)
                except:
                    return json.dumps({
                        "success": False,
                        "error": "meta_api_error",
                        "message": "Facebook API error",
                        "recoverable": True,
                        "suggestion": "Please wait 5 minutes before retrying"
                    }, indent=2)
            else:
                error_detail = response.text
                error_json = None
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message", error_detail)
                except:
                    pass

                result = {
                    "error": error_json.get("error", "duplication_failed") if error_json else "duplication_failed",
                    "message": error_json.get("message", f"Failed to duplicate {resource_type}") if error_json else f"Failed to duplicate {resource_type}",
                    "details": {
                        "status_code": response.status_code,
                        "error_detail": error_detail,
                        "resource_type": resource_type,
                        "resource_id": resource_id
                    }
                }

                # Forward structured error fields from the API response
                if error_json:
                    for field in ("suggestion", "error_subcode", "error_user_title",
                                  "error_user_msg", "raw_code", "raw_type", "recoverable"):
                        if error_json.get(field) is not None:
                            result[field] = error_json[field]

                return json.dumps(result, indent=2)
    
    except httpx.TimeoutException:
        return json.dumps({
            "error": "request_timeout",
            "message": "Request to duplication service timed out",
            "details": {
                "suggestion": "Please try again later",
                "timeout": "120 seconds"
            }
        }, indent=2)
    
    except httpx.RequestError as e:
        return json.dumps({
            "error": "network_error", 
            "message": "Failed to connect to duplication service",
            "details": {
                "error": str(e),
                "suggestion": "Check your internet connection and try again"
            }
        }, indent=2)
    
    except RateLimitError:
        raise  # Let FastMCP handle this to set isError: true

    except Exception as e:
        return json.dumps({
            "error": "unexpected_error",
            "message": f"Unexpected error during {resource_type} duplication",
            "details": {
                "error": str(e),
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        }, indent=2)


def _get_estimated_components(resource_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Get estimated components that would be duplicated."""
    if resource_type == "campaign":
        components = {"campaigns": 1}
        if options.get("include_ad_sets", True):
            components["ad_sets"] = "3-5 (estimated)"
        if options.get("include_ads", True):
            components["ads"] = "5-15 (estimated)"
        if options.get("include_creatives", True):
            components["creatives"] = "5-15 (estimated)"
        return components
    elif resource_type == "adset":
        components = {"ad_sets": 1}
        if options.get("include_ads", True):
            components["ads"] = "2-5 (estimated)"
        if options.get("include_creatives", True):
            components["creatives"] = "2-5 (estimated)"
        return components
    elif resource_type == "ad":
        components = {"ads": 1}
        if options.get("duplicate_creative", True):
            components["creatives"] = 1
        return components
    elif resource_type == "creative":
        return {"creatives": 1}
    
    return {} 