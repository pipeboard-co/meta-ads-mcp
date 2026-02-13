"""Campaign-related functionality for Meta Ads API."""

import json
from typing import List, Optional, Dict, Any, Union
from .api import meta_api_tool, make_api_request
from .accounts import get_ad_accounts
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def get_campaigns(
    account_id: str, 
    access_token: Optional[str] = None, 
    limit: int = 10, 
    status_filter: str = "", 
    objective_filter: Union[str, List[str]] = "", 
    after: str = ""
) -> str:
    """
    Get campaigns for a Meta Ads account with optional filtering.
    
    Note: By default, the Meta API returns a subset of available fields. 
    Other fields like 'effective_status', 'special_ad_categories', 
    'lifetime_budget', 'spend_cap', 'budget_remaining', 'promoted_object', 
    'source_campaign_id', etc., might be available but require specifying them
    in the API call (currently not exposed by this tool's parameters).
    
    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
        limit: Maximum number of campaigns to return (default: 10)
        status_filter: Filter by effective status (e.g., 'ACTIVE', 'PAUSED', 'ARCHIVED').
                       Maps to the 'effective_status' API parameter, which expects an array
                       (this function handles the required JSON formatting). Leave empty for all statuses.
        objective_filter: Filter by campaign objective(s). Can be a single objective string or a list of objectives.
                         Valid objectives: 'OUTCOME_AWARENESS', 'OUTCOME_TRAFFIC', 'OUTCOME_ENGAGEMENT',
                         'OUTCOME_LEADS', 'OUTCOME_SALES', 'OUTCOME_APP_PROMOTION'.
                         Examples: 'OUTCOME_LEADS' or ['OUTCOME_LEADS', 'OUTCOME_SALES'].
                         Leave empty for all objectives.
        after: Pagination cursor to get the next set of results
    """
    # Require explicit account_id
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)
    
    endpoint = f"{account_id}/campaigns"
    params = {
        "fields": "id,name,objective,status,daily_budget,lifetime_budget,buying_type,start_time,stop_time,created_time,updated_time,bid_strategy",
        "limit": limit
    }
    
    # Build filtering array for complex filtering
    filters = []
    
    if status_filter:
        # API expects an array, encode it as a JSON string
        params["effective_status"] = json.dumps([status_filter])
    
    # Handle objective filtering - supports both single string and list of objectives
    if objective_filter:
        # Convert single string to list for consistent handling
        objectives = [objective_filter] if isinstance(objective_filter, str) else objective_filter
        
        # Filter out empty strings
        objectives = [obj for obj in objectives if obj]
        
        if objectives:
            filters.append({
                "field": "objective",
                "operator": "IN",
                "value": objectives
            })
    
    # Add filtering parameter if we have filters
    if filters:
        params["filtering"] = json.dumps(filters)
    
    if after:
        params["after"] = after
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_campaign_details(campaign_id: str, access_token: Optional[str] = None) -> str:
    """
    Get detailed information about a specific campaign.

    Note: This function requests a specific set of fields ('id,name,objective,status,...'). 
    The Meta API offers many other fields for campaigns (e.g., 'effective_status', 'source_campaign_id', etc.) 
    that could be added to the 'fields' parameter in the code if needed.
    
    Args:
        campaign_id: Meta Ads campaign ID
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not campaign_id:
        return json.dumps({"error": "No campaign ID provided"}, indent=2)
    
    endpoint = f"{campaign_id}"
    params = {
        "fields": "id,name,objective,status,daily_budget,lifetime_budget,buying_type,start_time,stop_time,created_time,updated_time,bid_strategy,special_ad_categories,special_ad_category_country,budget_remaining,configured_status"
    }
    
    data = await make_api_request(endpoint, access_token, params)
    
    return json.dumps(data, indent=2) 