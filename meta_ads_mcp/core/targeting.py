"""Targeting search functionality for Meta Ads API."""

import json
from typing import Optional, List, Dict, Any
from .api import meta_api_tool, make_api_request
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def search_interests(access_token: str = None, query: str = None, limit: int = 25) -> str:
    """
    Search for interest targeting options by keyword.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        query: Search term for interests (e.g., "baseball", "cooking", "travel")
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
async def get_interest_suggestions(access_token: str = None, interest_list: List[str] = None, limit: int = 25) -> str:
    """
    Get interest suggestions based on existing interests.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)  
        interest_list: List of interest names to get suggestions for (e.g., ["Basketball", "Soccer"])
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
async def validate_interests(access_token: str = None, interest_list: List[str] = None, 
                           interest_fbid_list: List[str] = None) -> str:
    """
    Validate interest names or IDs for targeting.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        interest_list: List of interest names to validate (e.g., ["Japan", "Basketball"])
        interest_fbid_list: List of interest IDs to validate (e.g., ["6003700426513"])
    
    Returns:
        JSON string with validation results showing valid status and audience_size for each interest
    """
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


@mcp_server.tool()
@meta_api_tool
async def search_behaviors(access_token: str = None, limit: int = 50) -> str:
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
async def search_demographics(access_token: str = None, demographic_class: str = "demographics", limit: int = 50) -> str:
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
async def search_geo_locations(access_token: str = None, query: str = None, 
                             location_types: List[str] = None, limit: int = 25) -> str:
    """
    Search for geographic targeting locations.
    
    Args:
        access_token: Meta API access token (optional - will use cached token if not provided)
        query: Search term for locations (e.g., "New York", "California", "Japan")
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