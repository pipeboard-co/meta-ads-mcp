"""Audience management tools for Meta Ads API."""

import json
from typing import Optional
from .api import meta_api_tool, make_api_request
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def get_custom_audiences(
    account_id: str,
    access_token: Optional[str] = None,
    limit: int = 20,
) -> str:
    """
    List all custom audiences for a Meta Ads account.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
        limit: Maximum number of audiences to return (default: 20)
    """
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)

    endpoint = f"{account_id}/customaudiences"
    params = {
        "fields": "id,name,subtype,approximate_count,data_source,delivery_status,lookalike_spec",
        "limit": limit,
    }

    data = await make_api_request(endpoint, access_token, params)
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_custom_audience(
    account_id: str,
    name: str,
    subtype: str,
    access_token: Optional[str] = None,
    description: Optional[str] = None,
    rule: Optional[str] = None,
    retention_days: int = 30,
) -> str:
    """
    Create a custom audience for a Meta Ads account.

    For video-viewer audiences (Month 2 retargeting), use:
        subtype="VIDEO_VIEWS"
        rule=JSON string specifying video IDs and threshold (see Meta docs)

    For IG engager audiences, use:
        subtype="ENGAGEMENT"
        rule=JSON string specifying page/IG object and engagement type

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Audience name
        subtype: Audience type. Common values: VIDEO_VIEWS, ENGAGEMENT, CUSTOM
        access_token: Meta API access token (optional - will use cached token if not provided)
        description: Optional description
        rule: JSON string with audience rule spec (required for VIDEO_VIEWS / ENGAGEMENT)
        retention_days: How many days to retain audience members (default: 30)
    """
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    if not name:
        return json.dumps({"error": "No audience name provided"}, indent=2)
    if not subtype:
        return json.dumps({"error": "No subtype provided"}, indent=2)

    endpoint = f"{account_id}/customaudiences"
    params = {
        "name": name,
        "subtype": subtype,
        "retention_days": retention_days,
    }
    if description:
        params["description"] = description
    if rule:
        params["rule"] = rule

    try:
        data = await make_api_request(endpoint, access_token, params, method="POST")
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": "Failed to create custom audience", "details": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_lookalike_audience(
    account_id: str,
    name: str,
    origin_audience_id: str,
    country: str,
    access_token: Optional[str] = None,
    ratio: float = 0.01,
) -> str:
    """
    Create a lookalike audience from an existing custom audience seed.

    For Month 2: seed = video-viewer custom audience from Month 1.
    For Month 3: seed = email customer list audience (if IG-based saturates).

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Lookalike audience name
        origin_audience_id: ID of the source custom audience to model from
        country: 2-letter country code for the lookalike (e.g. "GR")
        access_token: Meta API access token (optional - will use cached token if not provided)
        ratio: Lookalike size as fraction of country population (0.01 = 1%, default)
    """
    if not account_id:
        return json.dumps({"error": "No account ID provided"}, indent=2)
    if not origin_audience_id:
        return json.dumps({"error": "No origin_audience_id provided"}, indent=2)

    endpoint = f"{account_id}/customaudiences"
    lookalike_spec = json.dumps({
        "country": country,
        "ratio": ratio,
        "type": "similarity",
    })
    params = {
        "name": name,
        "subtype": "LOOKALIKE",
        "origin_audience_id": origin_audience_id,
        "lookalike_spec": lookalike_spec,
    }

    try:
        data = await make_api_request(endpoint, access_token, params, method="POST")
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": "Failed to create lookalike audience", "details": str(e)}, indent=2)
