"""Custom audience tools for Meta Ads API."""

import json
from typing import Optional, Dict, Any
from .api import meta_api_tool, make_api_request
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def get_custom_audiences(account_id: str, access_token: Optional[str] = None) -> str:
    """
    Get custom audiences for a Meta Ads account.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
    """
    if not account_id:
        return json.dumps({"error": "account_id is required"}, indent=2)

    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    endpoint = f"{account_id}/customaudiences"
    params = {
        "fields": "id,name,subtype,approximate_count,data_source,delivery_status"
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
    rule: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a custom audience for a Meta Ads account.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Audience name
        subtype: Audience subtype. Valid values: ENGAGEMENT, CUSTOM, WEBSITE, VIDEO, IG_BUSINESS
        access_token: Meta API access token (optional - will use cached token if not provided)
        description: Optional audience description
        rule: Optional rule dict defining audience membership criteria.

    rule examples:
      IG engagers (30 days): {"inclusions": {"operator": "or", "rules": [{"event_sources": [{"id": "<ig_user_id>", "type": "ig_business"}], "retention_seconds": 2592000, "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": "ig_business_profile_all"}]}}]}}
      Video viewers (60 days): {"inclusions": {"operator": "or", "rules": [{"event_sources": [{"id": "<video_id>", "type": "video"}], "retention_seconds": 5184000, "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": "video_watched"}]}}]}}
    """
    if not account_id:
        return json.dumps({"error": "account_id is required"}, indent=2)

    if not name:
        return json.dumps({"error": "name is required"}, indent=2)

    if not subtype:
        return json.dumps({"error": "subtype is required"}, indent=2)

    valid_subtypes = {"ENGAGEMENT", "CUSTOM", "WEBSITE", "VIDEO", "IG_BUSINESS"}
    if subtype not in valid_subtypes:
        return json.dumps(
            {"error": f"Invalid subtype '{subtype}'. Valid: ENGAGEMENT, CUSTOM, WEBSITE, VIDEO, IG_BUSINESS"},
            indent=2,
        )

    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    endpoint = f"{account_id}/customaudiences"
    params: Dict[str, Any] = {
        "name": name,
        "subtype": subtype,
    }

    if description is not None:
        params["description"] = description

    if rule is not None:
        params["rule"] = rule

    data = await make_api_request(endpoint, access_token, params, method="POST")

    return json.dumps(data, indent=2)


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
    Create a lookalike audience based on an existing custom audience.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Audience name
        origin_audience_id: ID of the source custom audience to base the lookalike on
        country: Two-letter country code for the lookalike audience (e.g. 'GR', 'US')
        access_token: Meta API access token (optional - will use cached token if not provided)
        ratio: Similarity ratio between 0.01 (most similar, 1%) and 0.20 (broadest, 20%). Default: 0.01
    """
    if not account_id:
        return json.dumps({"error": "account_id is required"}, indent=2)

    if not name:
        return json.dumps({"error": "name is required"}, indent=2)

    if not origin_audience_id:
        return json.dumps({"error": "origin_audience_id is required"}, indent=2)

    if not country:
        return json.dumps({"error": "country is required"}, indent=2)

    if not (0.01 <= ratio <= 0.20):
        return json.dumps(
            {"error": f"ratio must be between 0.01 and 0.20, got {ratio}"},
            indent=2,
        )

    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    lookalike_spec = {"type": "custom_ratio", "country": country, "ratio": ratio}

    endpoint = f"{account_id}/customaudiences"
    params: Dict[str, Any] = {
        "name": name,
        "subtype": "LOOKALIKE",
        "origin_audience_id": origin_audience_id,
        "lookalike_spec": lookalike_spec,
    }

    data = await make_api_request(endpoint, access_token, params, method="POST")

    return json.dumps(data, indent=2)
