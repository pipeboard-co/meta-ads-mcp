"""Targeting search functionality for Meta Ads API."""

import json
from typing import Optional, List, Dict, Any
import os
from .api import meta_api_tool, make_api_request
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def search_interests(query: str, access_token: Optional[str] = None, limit: int = 25) -> str:
    """
    Search for interest targeting options by keyword.
    
    Args:
        query: Search term for interests (e.g., "baseball", "cooking", "travel")
        access_token: Meta API access token (optional - will use cached token if not provided)
        limit: Maximum number of results to return (default: 25)
    
    Returns:
        JSON string containing interest data with id, name, audience_size, and path fields
    """
    if not query:
        return json.dumps({"error": "No search query provided"}, indent=2)
    
    endpoint = "search"
    params = {
        "type": "adinterest",
        "q": query,
        "limit": limit
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_interest_suggestions(interest_list: List[str], access_token: Optional[str] = None, limit: int = 25) -> str:
    """
    Get interest suggestions based on existing interests.
    
    Args:
        interest_list: List of interest names to get suggestions for (e.g., ["Basketball", "Soccer"])
        access_token: Meta API access token (optional - will use cached token if not provided)  
        limit: Maximum number of suggestions to return (default: 25)
    
    Returns:
        JSON string containing suggested interests with id, name, audience_size, and description fields
    """
    if not interest_list:
        return json.dumps({"error": "No interest list provided"}, indent=2)
    
    endpoint = "search"
    params = {
        "type": "adinterestsuggestion", 
        "interest_list": json.dumps(interest_list),
        "limit": limit
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def estimate_audience_size(
    access_token: Optional[str] = None,
    account_id: Optional[str] = None,
    targeting: Optional[Dict[str, Any]] = None,
    optimization_goal: str = "REACH",
    # Backwards compatibility for simple interest validation
    interest_list: Optional[List[str]] = None,
    interest_fbid_list: Optional[List[str]] = None
) -> str:
    """
    Estimate audience size for targeting specifications using Meta's delivery_estimate API.
    
    This function provides comprehensive audience estimation for complex targeting combinations
    including demographics, geography, interests, and behaviors. It also maintains backwards
    compatibility for simple interest validation.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        account_id: Meta Ads account ID (format: act_XXXXXXXXX) - required for comprehensive estimation
        targeting: Complete targeting specification including demographics, geography, interests, etc.
                  Example: {
                      "age_min": 25,
                      "age_max": 65,
                      "geo_locations": {"countries": ["PL"]},
                      "flexible_spec": [
                          {"interests": [{"id": "6003371567474"}]},
                          {"interests": [{"id": "6003462346642"}]}
                      ]
                  }
        optimization_goal: Optimization goal for estimation (default: "REACH"). 
                          Options: "REACH", "LINK_CLICKS", "IMPRESSIONS", "CONVERSIONS", etc.
        interest_list: [DEPRECATED - for backwards compatibility] List of interest names to validate
        interest_fbid_list: [DEPRECATED - for backwards compatibility] List of interest IDs to validate
    
    Returns:
        JSON string with audience estimation results including estimated_audience_size,
        reach_estimate, and targeting validation
    """
    # Handle backwards compatibility - simple interest validation
    # Check if we're in backwards compatibility mode (interest params provided OR no comprehensive params)
    is_backwards_compatible_call = (interest_list or interest_fbid_list) or (not account_id and not targeting)
    
    if is_backwards_compatible_call and not targeting:
        if not interest_list and not interest_fbid_list:
            return json.dumps({"error": "No interest list or FBID list provided"}, indent=2)
        
        endpoint = "search"
        params = {
            "type": "adinterestvalid"
        }
        
        if interest_list:
            params["interest_list"] = json.dumps(interest_list)
        
        if interest_fbid_list:
            params["interest_fbid_list"] = json.dumps(interest_fbid_list)
        
        data = await make_api_request(endpoint, access_token, params)
        
        return json.dumps(data, indent=2)
    
    # Comprehensive audience estimation using delivery_estimate API
    if not account_id:
        return json.dumps({
            "error": "account_id is required for comprehensive audience estimation",
            "details": "For simple interest validation, use interest_list or interest_fbid_list parameters"
        }, indent=2)
    
    if not targeting:
        return json.dumps({
            "error": "targeting specification is required for comprehensive audience estimation",
            "example": {
                "age_min": 25,
                "age_max": 65,
                "geo_locations": {"countries": ["US"]},
                "flexible_spec": [
                    {"interests": [{"id": "6003371567474"}]}
                ]
            }
        }, indent=2)
    
    # Preflight validation: require at least one location OR a custom audience
    def _has_location_or_custom_audience(t: Dict[str, Any]) -> bool:
        if not isinstance(t, dict):
            return False
        geo = t.get("geo_locations") or {}
        if isinstance(geo, dict):
            for key in [
                "countries",
                "regions",
                "cities",
                "zips",
                "geo_markets",
                "country_groups"
            ]:
                val = geo.get(key)
                if isinstance(val, list) and len(val) > 0:
                    return True
        # Top-level custom audiences
        ca = t.get("custom_audiences")
        if isinstance(ca, list) and len(ca) > 0:
            return True
        # Custom audiences within flexible_spec
        flex = t.get("flexible_spec")
        if isinstance(flex, list):
            for spec in flex:
                if isinstance(spec, dict):
                    ca_spec = spec.get("custom_audiences")
                    if isinstance(ca_spec, list) and len(ca_spec) > 0:
                        return True
        return False

    if not _has_location_or_custom_audience(targeting):
        return json.dumps({
            "error": "Missing target audience location",
            "details": "Select at least one location in targeting.geo_locations or include a custom audience.",
            "action_required": "Add geo_locations with countries/regions/cities/zips or include custom_audiences.",
            "example": {
                "geo_locations": {"countries": ["US"]},
                "age_min": 25,
                "age_max": 65
            }
        }, indent=2)
    
    # Build reach estimate request (using correct Meta API endpoint)
    endpoint = f"{account_id}/reachestimate"
    params = {
        "targeting_spec": targeting
    }
    
    # Note: reachestimate endpoint doesn't support optimization_goal or objective parameters
    
    try:
        data = await make_api_request(endpoint, access_token, params, method="GET")
        
        # Surface Graph API errors directly for better diagnostics.
        # If reachestimate fails, optionally attempt a fallback using delivery_estimate.
        if isinstance(data, dict) and "error" in data:
            # Special handling for Missing Target Audience Location error (subcode 1885364)
            try:
                err_wrapper = data.get("error", {})
                details_obj = err_wrapper.get("details", {})
                raw_err = details_obj.get("error", {}) if isinstance(details_obj, dict) else {}
                if (
                    isinstance(raw_err, dict) and (
                        raw_err.get("error_subcode") == 1885364 or
                        raw_err.get("error_user_title") == "Missing Target Audience Location"
                    )
                ):
                    return json.dumps({
                        "error": "Missing target audience location",
                        "details": raw_err.get("error_user_msg") or "Select at least one location, or choose a custom audience.",
                        "endpoint_used": f"{account_id}/reachestimate",
                        "action_required": "Add geo_locations with at least one of countries/regions/cities/zips or include custom_audiences.",
                        "blame_field_specs": raw_err.get("error_data", {}).get("blame_field_specs") if isinstance(raw_err.get("error_data"), dict) else None
                    }, indent=2)
            except Exception:
                pass
            # Allow disabling fallback via environment variable
            # Default: fallback disabled unless explicitly enabled by setting DISABLE flag to "0"
            disable_fallback = os.environ.get("META_MCP_DISABLE_DELIVERY_FALLBACK", "1") == "1"
            if disable_fallback:
                return json.dumps({
                    "error": "Graph API returned an error for reachestimate",
                    "details": data.get("error"),
                    "endpoint_used": f"{account_id}/reachestimate",
                    "request_params": {
                        "has_targeting_spec": bool(targeting),
                    },
                    "note": "delivery_estimate fallback disabled via META_MCP_DISABLE_DELIVERY_FALLBACK"
                }, indent=2)

            # Try fallback to delivery_estimate endpoint
            try:
                fallback_endpoint = f"{account_id}/delivery_estimate"
                fallback_params = {
                    "targeting_spec": json.dumps(targeting),
                    # Some API versions accept optimization_goal here
                    "optimization_goal": optimization_goal
                }
                fallback_data = await make_api_request(fallback_endpoint, access_token, fallback_params, method="GET")
                
                # If fallback returns usable data, format similarly
                if isinstance(fallback_data, dict) and "data" in fallback_data and len(fallback_data["data"]) > 0:
                    estimate_data = fallback_data["data"][0]
                    formatted_response = {
                        "success": True,
                        "account_id": account_id,
                        "targeting": targeting,
                        "optimization_goal": optimization_goal,
                        "estimated_audience_size": estimate_data.get("estimate_mau", 0),
                        "estimate_details": {
                            "monthly_active_users": estimate_data.get("estimate_mau", 0),
                            "daily_outcomes_curve": estimate_data.get("estimate_dau", []),
                            "bid_estimate": estimate_data.get("bid_estimates", {}),
                            "unsupported_targeting": estimate_data.get("unsupported_targeting", [])
                        },
                        "raw_response": fallback_data,
                        "fallback_endpoint_used": "delivery_estimate"
                    }
                    return json.dumps(formatted_response, indent=2)
                
                # Fallback returned but not in expected format
                return json.dumps({
                    "error": "Graph API returned an error for reachestimate; delivery_estimate fallback did not return usable data",
                    "reachestimate_error": data.get("error"),
                    "fallback_endpoint_used": "delivery_estimate",
                    "fallback_raw_response": fallback_data,
                    "endpoint_used": f"{account_id}/reachestimate",
                    "request_params": {
                        "has_targeting_spec": bool(targeting)
                    }
                }, indent=2)
            except Exception as _fallback_exc:
                return json.dumps({
                    "error": "Graph API returned an error for reachestimate; delivery_estimate fallback also failed",
                    "reachestimate_error": data.get("error"),
                    "fallback_endpoint_used": "delivery_estimate",
                    "fallback_exception": str(_fallback_exc),
                    "endpoint_used": f"{account_id}/reachestimate",
                    "request_params": {
                        "has_targeting_spec": bool(targeting)
                    }
                }, indent=2)

        # Format the response for easier consumption
        if "data" in data:
            response_data = data["data"]
            # Case 1: delivery_estimate-like list structure
            if isinstance(response_data, list) and len(response_data) > 0:
                estimate_data = response_data[0]
                formatted_response = {
                    "success": True,
                    "account_id": account_id,
                    "targeting": targeting,
                    "optimization_goal": optimization_goal,
                    "estimated_audience_size": estimate_data.get("estimate_mau", 0),
                    "estimate_details": {
                        "monthly_active_users": estimate_data.get("estimate_mau", 0),
                        "daily_outcomes_curve": estimate_data.get("estimate_dau", []),
                        "bid_estimate": estimate_data.get("bid_estimates", {}),
                        "unsupported_targeting": estimate_data.get("unsupported_targeting", [])
                    },
                    "raw_response": data
                }
                return json.dumps(formatted_response, indent=2)
            # Case 1b: explicit handling for empty list responses
            if isinstance(response_data, list) and len(response_data) == 0:
                return json.dumps({
                    "error": "No estimation data returned from Meta API",
                    "raw_response": data,
                    "debug_info": {
                        "response_keys": list(data.keys()) if isinstance(data, dict) else "not_a_dict",
                        "response_type": str(type(data)),
                        "endpoint_used": f"{account_id}/reachestimate"
                    }
                }, indent=2)
            # Case 2: reachestimate dict structure with bounds
            if isinstance(response_data, dict):
                lower = response_data.get("users_lower_bound", response_data.get("estimate_mau_lower_bound"))
                upper = response_data.get("users_upper_bound", response_data.get("estimate_mau_upper_bound"))
                estimate_ready = response_data.get("estimate_ready")
                midpoint = None
                try:
                    if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
                        midpoint = int((lower + upper) / 2)
                except Exception:
                    midpoint = None
                formatted_response = {
                    "success": True,
                    "account_id": account_id,
                    "targeting": targeting,
                    "optimization_goal": optimization_goal,
                    "estimated_audience_size": midpoint if midpoint is not None else 0,
                    "estimate_details": {
                        "users_lower_bound": lower,
                        "users_upper_bound": upper,
                        "estimate_ready": estimate_ready
                    },
                    "raw_response": data
                }
                return json.dumps(formatted_response, indent=2)
        else:
            return json.dumps({
                "error": "No estimation data returned from Meta API",
                "raw_response": data,
                "debug_info": {
                    "response_keys": list(data.keys()) if isinstance(data, dict) else "not_a_dict",
                    "response_type": str(type(data)),
                    "endpoint_used": f"{account_id}/reachestimate"
                }
            }, indent=2)
    
    except Exception as e:
        # Try fallback to delivery_estimate first when an exception occurs (unless disabled)
        # Default: fallback disabled unless explicitly enabled by setting DISABLE flag to "0"
        disable_fallback = os.environ.get("META_MCP_DISABLE_DELIVERY_FALLBACK", "1") == "1"
        if not disable_fallback:
            try:
                fallback_endpoint = f"{account_id}/delivery_estimate"
                fallback_params = {
                "targeting_spec": json.dumps(targeting) if isinstance(targeting, dict) else targeting,
                "optimization_goal": optimization_goal
            }
                fallback_data = await make_api_request(fallback_endpoint, access_token, fallback_params, method="GET")
            
                if isinstance(fallback_data, dict) and "data" in fallback_data and len(fallback_data["data"]) > 0:
                    estimate_data = fallback_data["data"][0]
                    formatted_response = {
                        "success": True,
                        "account_id": account_id,
                        "targeting": targeting,
                        "optimization_goal": optimization_goal,
                        "estimated_audience_size": estimate_data.get("estimate_mau", 0),
                        "estimate_details": {
                            "monthly_active_users": estimate_data.get("estimate_mau", 0),
                            "daily_outcomes_curve": estimate_data.get("estimate_dau", []),
                            "bid_estimate": estimate_data.get("bid_estimates", {}),
                            "unsupported_targeting": estimate_data.get("unsupported_targeting", [])
                        },
                        "raw_response": fallback_data,
                        "fallback_endpoint_used": "delivery_estimate"
                    }
                    return json.dumps(formatted_response, indent=2)
            except Exception as _fallback_exc:
                # If fallback also fails, proceed to detailed error handling below
                pass

        # Check if this is the specific Business Manager system user permission error
        error_str = str(e)
        if "100" in error_str and "33" in error_str:
            # Try to provide fallback estimation using individual interests if available
            interests_found = []
            if targeting and "interests" in targeting:
                interests_found.extend([interest.get("id") for interest in targeting["interests"] if interest.get("id")])
            elif targeting and "flexible_spec" in targeting:
                for spec in targeting["flexible_spec"]:
                    if "interests" in spec:
                        interests_found.extend([interest.get("id") for interest in spec["interests"] if interest.get("id")])
            
            if interests_found:
                # Attempt to get individual interest data as fallback
                try:
                    fallback_result = await estimate_audience_size(
                        access_token=access_token,
                        interest_fbid_list=interests_found
                    )
                    fallback_data = json.loads(fallback_result)
                    
                    return json.dumps({
                        "comprehensive_targeting_failed": True,
                        "error_code": "100-33",
                        "fallback_used": True,
                        "details": {
                            "issue": "reachestimate endpoint returned error - possibly due to targeting parameters or account limitations",
                            "solution": "Individual interest validation used as fallback - comprehensive targeting may have specific requirements",
                            "endpoint_used": f"{account_id}/reachestimate"
                        },
                        "individual_interest_data": fallback_data,
                        "note": "Individual interest audience sizes provided as fallback. Comprehensive targeting via reachestimate endpoint failed."
                    }, indent=2)
                except:
                    pass
            
            return json.dumps({
                "error": "reachestimate endpoint returned error (previously was incorrectly using delivery_estimate)",
                "error_code": "100-33", 
                "details": {
                    "issue": "The endpoint returned an error, possibly due to targeting parameters or account limitations",
                    "endpoint_used": f"{account_id}/reachestimate",
                    "previous_issue": "Code was previously using non-existent delivery_estimate endpoint - now fixed",
                    "available_alternative": "Use interest_list or interest_fbid_list parameters for individual interest validation"
                },
                "raw_error": error_str
            }, indent=2)
        else:
            return json.dumps({
                "error": f"Failed to get audience estimation from reachestimate endpoint: {str(e)}",
                "details": "Check targeting parameters and account permissions",
                "error_type": "general_api_error",
                "endpoint_used": f"{account_id}/reachestimate"
            }, indent=2)


@mcp_server.tool()
@meta_api_tool
async def search_behaviors(access_token: Optional[str] = None, limit: int = 50) -> str:
    """
    Get all available behavior targeting options.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        limit: Maximum number of results to return (default: 50)
    
    Returns:
        JSON string containing behavior targeting options with id, name, audience_size bounds, path, and description
    """
    endpoint = "search"
    params = {
        "type": "adTargetingCategory",
        "class": "behaviors",
        "limit": limit
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def search_demographics(access_token: Optional[str] = None, demographic_class: str = "demographics", limit: int = 50) -> str:
    """
    Get demographic targeting options.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        demographic_class: Type of demographics to retrieve. Options: 'demographics', 'life_events', 
                          'industries', 'income', 'family_statuses', 'user_device', 'user_os' (default: 'demographics')
        limit: Maximum number of results to return (default: 50)
    
    Returns:
        JSON string containing demographic targeting options with id, name, audience_size bounds, path, and description
    """
    endpoint = "search"
    params = {
        "type": "adTargetingCategory",
        "class": demographic_class,
        "limit": limit
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def search_geo_locations(query: str, access_token: Optional[str] = None, 
                             location_types: Optional[List[str]] = None, limit: int = 25) -> str:
    """
    Search for geographic targeting locations.
    
    Args:
        query: Search term for locations (e.g., "New York", "California", "Japan")
        access_token: Meta API access token (optional - will use cached token if not provided)
        location_types: Types of locations to search. Options: ['country', 'region', 'city', 'zip', 
                       'geo_market', 'electoral_district']. If not specified, searches all types.
        limit: Maximum number of results to return (default: 25)
    
    Returns:
        JSON string containing location data with key, name, type, and geographic hierarchy information
    """
    if not query:
        return json.dumps({"error": "No search query provided"}, indent=2)
    
    endpoint = "search"
    params = {
        "type": "adgeolocation",
        "q": query,
        "limit": limit
    }
    
    if location_types:
        params["location_types"] = json.dumps(location_types)
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2) 