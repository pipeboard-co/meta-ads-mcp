"""Adds Library-related functionality for Meta Ads API."""

import json
import os
from typing import Optional, List, Dict, Any
from .api import meta_api_tool, make_api_request
from .server import mcp_server


# Only register the search_ads_archive function if the environment variable is NOT set
DISABLE_ADS_LIBRARY = bool(os.environ.get("META_ADS_DISABLE_ADS_LIBRARY", ""))

if not DISABLE_ADS_LIBRARY:
    @mcp_server.tool()
    @meta_api_tool
    async def search_ads_archive(
        search_terms: str,
        ad_reached_countries: List[str],
        access_token: Optional[str] = None,
        ad_type: str = "ALL",
        limit: int = 25,  # Default limit, adjust as needed
        fields: str = "ad_creation_time,ad_creative_body,ad_creative_link_caption,ad_creative_link_description,ad_creative_link_title,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,currency,demographic_distribution,funding_entity,impressions,page_id,page_name,publisher_platform,region_distribution,spend"
    ) -> str:
        """
        Search the Facebook Ads Library archive.

        Args:
            search_terms: The search query for ads.
            ad_reached_countries: List of country codes (e.g., ["US", "GB"]).
            access_token: Meta API access token (optional - will use cached token if not provided).
            ad_type: Type of ads to search for (e.g., POLITICAL_AND_ISSUE_ADS, HOUSING_ADS, ALL).
            limit: Maximum number of ads to return.
            fields: Comma-separated string of fields to retrieve for each ad.

        Example Usage via curl equivalent:
            curl -G \\
            -d "search_terms='california'" \\
            -d "ad_type=POLITICAL_AND_ISSUE_ADS" \\
            -d "ad_reached_countries=['US']" \\
            -d "fields=ad_snapshot_url,spend" \\
            -d "access_token=<ACCESS_TOKEN>" \\
            "https://graph.facebook.com/<API_VERSION>/ads_archive"
        """
        if not access_token:
            # Attempt to get token implicitly if not provided - meta_api_tool handles this
            pass

        if not search_terms:
            return json.dumps({"error": "search_terms parameter is required"}, indent=2)

        if not ad_reached_countries:
            return json.dumps({"error": "ad_reached_countries parameter is required"}, indent=2)

        endpoint = "ads_archive"
        params = {
            "search_terms": search_terms,
            "ad_type": ad_type,
            "ad_reached_countries": json.dumps(ad_reached_countries), # API expects a JSON array string
            "limit": limit,
            "fields": fields,
        }

        try:
            data = await make_api_request(endpoint, access_token, params, method="GET")
            return json.dumps(data, indent=2)
        except Exception as e:
            error_msg = str(e)
            # Consider logging the full error for debugging
            # print(f"Error calling Ads Library API: {error_msg}")
            return json.dumps({
                "error": "Failed to search ads archive",
                "details": error_msg,
                "params_sent": {k: v for k, v in params.items() if k != 'access_token'} # Avoid logging token
            }, indent=2) 