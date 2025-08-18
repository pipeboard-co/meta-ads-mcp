"""Budget Schedule-related functionality for Meta Ads API."""

import json
from typing import Optional, Dict, Any

from .api import meta_api_tool, make_api_request
from .server import mcp_server
# Assuming no other specific dependencies from adsets.py are needed for this single function.
# If other utilities from adsets.py (like get_ad_accounts) were needed, they'd be imported here.

@mcp_server.tool()
@meta_api_tool
async def create_budget_schedule(
    campaign_id: str,
    budget_value: int,
    budget_value_type: str,
    time_start: int,
    time_end: int,
    access_token: Optional[str] = None
) -> str:
    """
    Create a budget schedule for a Meta Ads campaign.

    Allows scheduling budget increases based on anticipated high-demand periods.
    The times should be provided as Unix timestamps.
    
    Args:
        campaign_id: Meta Ads campaign ID.
        budget_value: Amount of budget increase. Interpreted based on budget_value_type.
        budget_value_type: Type of budget value - "ABSOLUTE" or "MULTIPLIER".
        time_start: Unix timestamp for when the high demand period should start.
        time_end: Unix timestamp for when the high demand period should end.
        access_token: Meta API access token (optional - will use cached token if not provided).
        
    Returns:
        A JSON string containing the ID of the created budget schedule or an error message.
    """
    if not campaign_id:
        return json.dumps({"error": "Campaign ID is required"}, indent=2)
    if budget_value is None: # Check for None explicitly
        return json.dumps({"error": "Budget value is required"}, indent=2)
    if not budget_value_type:
        return json.dumps({"error": "Budget value type is required"}, indent=2)
    if budget_value_type not in ["ABSOLUTE", "MULTIPLIER"]:
        return json.dumps({"error": "Invalid budget_value_type. Must be ABSOLUTE or MULTIPLIER"}, indent=2)
    if time_start is None: # Check for None explicitly to allow 0
        return json.dumps({"error": "Time start is required"}, indent=2)
    if time_end is None: # Check for None explicitly to allow 0
        return json.dumps({"error": "Time end is required"}, indent=2)

    endpoint = f"{campaign_id}/budget_schedules"

    params = {
        "budget_value": budget_value,
        "budget_value_type": budget_value_type,
        "time_start": time_start,
        "time_end": time_end,
    }

    try:
        data = await make_api_request(endpoint, access_token, params, method="POST")
        return json.dumps(data, indent=2)
    except Exception as e:
        error_msg = str(e)
        # Include details about the error and the parameters sent for easier debugging
        return json.dumps({
            "error": "Failed to create budget schedule",
            "details": error_msg,
            "campaign_id": campaign_id,
            "params_sent": params
        }, indent=2) 