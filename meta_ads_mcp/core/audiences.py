"""Custom audience tools for Meta Ads API."""

import hashlib
import json
import re
from typing import List, Optional, Dict, Any

from .api import meta_api_tool, make_api_request
from .server import mcp_server


def _normalize_and_hash_email(email: str) -> str:
    """Normalize an email address and return its SHA-256 hex digest.

    Args:
        email: Raw email string (may have surrounding whitespace or spaces around @).

    Returns:
        Lowercase, whitespace-stripped SHA-256 hex digest of the email.
    """
    normalized = re.sub(r"\s+", "", email.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


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
        "fields": "id,name,subtype,approximate_count_lower_bound,approximate_count_upper_bound,data_source,delivery_status"
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
    customer_file_source: Optional[str] = None,
) -> str:
    """
    Create a custom audience for a Meta Ads account.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        name: Audience name
        subtype: Audience subtype. Valid values: ENGAGEMENT, CUSTOM, WEBSITE, VIDEO.
                 Note: IG_BUSINESS was removed in v25.0. Use ENGAGEMENT with an IG
                 engagement rule instead (see rule examples below).
        access_token: Meta API access token (optional - will use cached token if not provided)
        description: Optional audience description
        rule: Optional rule dict defining audience membership criteria.
        customer_file_source: Required for CUSTOM subtype. Valid values:
                              USER_PROVIDED_ONLY, PARTNER_PROVIDED_ONLY, BOTH_USER_AND_PARTNER_PROVIDED

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

    valid_subtypes = {"ENGAGEMENT", "CUSTOM", "WEBSITE", "VIDEO"}
    if subtype not in valid_subtypes:
        return json.dumps(
            {"error": f"Invalid subtype '{subtype}'. Valid: ENGAGEMENT, CUSTOM, WEBSITE, VIDEO. Note: IG_BUSINESS was removed in v25.0 — use ENGAGEMENT with an IG engagement rule instead."},
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

    if customer_file_source is not None:
        params["customer_file_source"] = customer_file_source

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


@mcp_server.tool()
@meta_api_tool
async def add_users_to_custom_audience(
    audience_id: str,
    emails: List[str],
    access_token: Optional[str] = None,
    already_hashed: bool = False,
) -> str:
    """
    Add users to an existing custom audience via a list of email addresses.

    Emails are normalized (lowercased, whitespace stripped) and SHA-256 hashed
    before upload unless already_hashed=True.

    Args:
        audience_id: ID of the custom audience to populate (e.g. "6933647088203")
        emails: List of email addresses to add. Accepts raw or pre-hashed emails.
        access_token: Meta API access token (optional - will use cached token if not provided)
        already_hashed: Set to True if emails are already SHA-256 hashed. Default: False.

    Returns:
        JSON response from Meta API with num_received, num_invalid_skipped, and
        invalid_entry_samples fields.
    """
    if not audience_id:
        return json.dumps({"error": "audience_id is required"}, indent=2)

    if not emails:
        return json.dumps({"error": "emails list must not be empty"}, indent=2)

    if not all(isinstance(e, str) for e in emails):
        return json.dumps({"error": "all entries in emails must be strings"}, indent=2)

    if already_hashed:
        invalid = [e for e in emails if len(e) != 64 or not all(c in "0123456789abcdef" for c in e)]
        if invalid:
            return json.dumps(
                {"error": f"already_hashed=True requires 64-char lowercase hex SHA-256 strings; invalid: {invalid[:3]}"},
                indent=2,
            )
        hashed = [[e] for e in emails]
    else:
        hashed = [[_normalize_and_hash_email(e)] for e in emails]

    endpoint = f"{audience_id}/users"
    params: Dict[str, Any] = {
        "payload": {
            "schema": ["EMAIL_SHA256"],
            "data": hashed,
        }
    }

    data = await make_api_request(endpoint, access_token, params, method="POST")

    return json.dumps(data, indent=2)
