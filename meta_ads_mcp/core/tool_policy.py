"""Tool-surface policies for the Meta Ads MCP server."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP


READ_ONLY_TOOL_NAMES = frozenset(
    {
        "get_ad_accounts",
        "get_account_info",
        "get_campaigns",
        "get_campaign_details",
        "get_adsets",
        "get_adset_details",
        "get_ads",
        "get_ad_details",
        "get_creative_details",
        "get_ad_creatives",
        "get_ad_image",
        "get_image_by_hash",
        "get_ad_video",
        "compute_image_crops",
        "search_pages_by_name",
        "get_account_pages",
        "get_insights",
        "get_login_link",
        "search_ads_archive",
        "search_interests",
        "get_interest_suggestions",
        "estimate_audience_size",
        "search_behaviors",
        "search_demographics",
        "search_geo_locations",
        "search",
        "fetch",
    }
)


def read_only_mode_enabled() -> bool:
    """Return whether the opt-in read-only server mode is enabled."""
    return os.getenv("META_ADS_MCP_READ_ONLY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def apply_read_only_tool_policy(server: FastMCP, *, enabled: bool) -> set[str]:
    """Remove every non-allowlisted tool when read-only mode is enabled."""
    if not enabled:
        return set()

    registered = {tool.name for tool in server._tool_manager.list_tools()}
    removed = registered - READ_ONLY_TOOL_NAMES
    for name in sorted(removed):
        server.remove_tool(name)
    return removed
