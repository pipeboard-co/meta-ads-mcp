"""Instagram Insights and publishing functionality for Meta Graph API."""

import json
from typing import Optional, List
from .api import meta_api_tool, make_api_request
from .server import mcp_server


@mcp_server.tool()
@meta_api_tool
async def list_media(
    ig_user_id: str,
    access_token: Optional[str] = None,
    limit: int = 20,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> str:
    """List media objects for an Instagram Business Account.

    NOTE: ig_user_id is the Instagram Business Account ID (numeric). Do NOT pass
    an ad account ID starting with 'act_' — that will fail.

    Args:
        ig_user_id: Numeric Instagram Business Account ID.
        access_token: Meta API access token.
        limit: Maximum number of media items to return (default 20).
        since: Start of date range (YYYY-MM-DD or Unix timestamp). Optional.
        until: End of date range (YYYY-MM-DD or Unix timestamp). Optional.

    Returns:
        JSON string with media list including id, media_type, media_product_type,
        timestamp, permalink, caption, like_count, comments_count, thumbnail_url.
        Note: like_count may be omitted by the API for some media types or accounts
        with professional dashboard enabled. For Reel view counts use
        get_media_insights with metrics=["views"].
    """
    if not ig_user_id:
        return json.dumps({"error": "ig_user_id is required"}, indent=2)

    params = {
        "fields": "id,media_type,media_product_type,timestamp,permalink,caption,like_count,comments_count,thumbnail_url",
        "limit": limit,
    }
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    data = await make_api_request(f"{ig_user_id}/media", access_token, params)
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_media_insights(
    media_id: str,
    access_token: Optional[str] = None,
    metrics: Optional[List[str]] = None,
) -> str:
    """Get insights for a specific Instagram media object.

    Supported metrics by media type (Graph API v25.0+):
        IMAGE:    impressions, reach, saved, total_interactions
        VIDEO:    impressions, reach, saved, total_interactions
        REELS:    reach, impressions, saved, shares, views, total_interactions
        CAROUSEL: impressions, reach, saved, total_interactions

    Note: plays and ig_reels_aggregated_all_plays_count were removed in v22.0.
    Use views for Reels play counts.

    Note: The IG API uses the 'metric' parameter (singular), not 'metrics'.

    Args:
        media_id: ID of the Instagram media object.
        access_token: Meta API access token.
        metrics: List of metric names to retrieve. Defaults to
                 ["reach", "impressions", "saved", "shares", "plays",
                  "total_interactions"] when None or empty.

    Returns:
        JSON string with metric data for the media object.
    """
    if not media_id:
        return json.dumps({"error": "media_id is required"}, indent=2)

    default_metrics = ["reach", "impressions", "saved", "shares", "views", "total_interactions"]
    metrics_to_use = metrics if metrics else default_metrics

    params = {"metric": ",".join(metrics_to_use)}
    data = await make_api_request(f"{media_id}/insights", access_token, params)
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_ig_account_insights(
    ig_user_id: str,
    metrics: List[str],
    access_token: Optional[str] = None,
    period: str = "day",
    since: Optional[str] = None,
    until: Optional[str] = None,
    metric_type: Optional[str] = None,
) -> str:
    """Get insights for an Instagram Business Account.

    Note: 'follower_count' metric only works with period=day. Max lookback
    30 days for most metrics.

    Valid periods: day, week, days_28, month, lifetime.

    As of Graph API v25.0, some metrics require metric_type to be specified
    (e.g. metric_type='total_value'). Pass metric_type when the API returns
    a requirement error for the requested metrics.

    Args:
        ig_user_id: Numeric Instagram Business Account ID.
        metrics: List of metric names to retrieve (required, must not be empty).
        access_token: Meta API access token.
        period: Aggregation period — one of day, week, days_28, month, lifetime.
        since: Start of date range (YYYY-MM-DD or Unix timestamp). Optional.
        until: End of date range (YYYY-MM-DD or Unix timestamp). Optional.
        metric_type: Optional metric type qualifier required by v25.0 for certain
                     metrics (e.g. 'total_value'). Omitted if not provided.

    Returns:
        JSON string with account-level insight data.
    """
    if not ig_user_id:
        return json.dumps({"error": "ig_user_id is required"}, indent=2)

    if not metrics:
        return json.dumps({"error": "metrics must not be empty"}, indent=2)

    valid_periods = {"day", "week", "days_28", "month", "lifetime"}
    if period not in valid_periods:
        return json.dumps(
            {"error": f"Invalid period '{period}'. Valid: day, week, days_28, month, lifetime"},
            indent=2,
        )

    if "follower_count" in metrics and period != "day":
        return json.dumps(
            {"error": f"follower_count metric only works with period='day', got '{period}'"},
            indent=2,
        )

    params = {
        "metric": ",".join(metrics),
        "period": period,
    }
    if since is not None:
        params["since"] = since
    if until is not None:
        params["until"] = until
    if metric_type is not None:
        params["metric_type"] = metric_type

    data = await make_api_request(f"{ig_user_id}/insights", access_token, params)
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_story_insights(
    story_id: str,
    access_token: Optional[str] = None,
    metrics: Optional[List[str]] = None,
) -> str:
    """Get insights for an Instagram Story.

    Note: Story insights are only available ~72h after posting (24h story
    lifetime + 48h after expiry before metrics stabilise).

    Args:
        story_id: ID of the Instagram Story media object.
        access_token: Meta API access token.
        metrics: List of metric names to retrieve. Defaults to
                 ["impressions", "reach", "replies", "taps_forward",
                  "taps_back", "exits"] when None or empty.

    Returns:
        JSON string with story insight data.
    """
    if not story_id:
        return json.dumps({"error": "story_id is required"}, indent=2)

    default_metrics = ["impressions", "reach", "replies", "taps_forward", "taps_back", "exits"]
    metrics_to_use = metrics if metrics else default_metrics

    params = {"metric": ",".join(metrics_to_use)}
    data = await make_api_request(f"{story_id}/insights", access_token, params)
    return json.dumps(data, indent=2)


@mcp_server.tool()
@meta_api_tool
async def publish_media(
    ig_user_id: str,
    media_url: str,
    media_type: str,
    access_token: Optional[str] = None,
    caption: Optional[str] = None,
) -> str:
    """Publish a media object to an Instagram Business Account (two-step process).

    Step 1 creates a media container; Step 2 publishes it. If Step 1 fails,
    the error is returned immediately without attempting Step 2.

    Note: 50 posts/day rate limit applies. Media URL must be publicly accessible.

    Valid media_type values: IMAGE, VIDEO, REELS, STORIES.

    Args:
        ig_user_id: Numeric Instagram Business Account ID.
        media_url: Publicly accessible URL of the media to publish.
        media_type: One of IMAGE, VIDEO, REELS, STORIES.
        access_token: Meta API access token.
        caption: Optional caption text for the post.

    Returns:
        JSON string with the published media ID on success, or an error dict.
    """
    if not ig_user_id:
        return json.dumps({"error": "ig_user_id is required"}, indent=2)

    if not media_url.startswith("http://") and not media_url.startswith("https://"):
        return json.dumps({"error": "media_url must start with http:// or https://"}, indent=2)

    valid_media_types = {"IMAGE", "VIDEO", "REELS", "STORIES"}
    if media_type not in valid_media_types:
        return json.dumps(
            {"error": f"Invalid media_type '{media_type}'. Valid: IMAGE, VIDEO, REELS, STORIES"},
            indent=2,
        )

    # Step 1 — Create media container
    step1_params = {"caption": caption} if caption else {}
    if media_type == "IMAGE":
        step1_params["image_url"] = media_url
    else:  # VIDEO, REELS, STORIES
        step1_params["video_url"] = media_url
        step1_params["media_type"] = media_type

    step1_data = await make_api_request(
        f"{ig_user_id}/media", access_token, step1_params, method="POST"
    )

    if "error" in step1_data:
        return json.dumps(step1_data, indent=2)

    creation_id = step1_data.get("id")
    if not creation_id:
        return json.dumps(
            {"error": "Step 1 succeeded but no creation_id returned", "step1_response": step1_data},
            indent=2,
        )

    # Step 2 — Publish the container
    step2_params = {"creation_id": creation_id}
    step2_data = await make_api_request(
        f"{ig_user_id}/media_publish", access_token, step2_params, method="POST"
    )

    if "error" in step2_data:
        return json.dumps(
            {"error": "Publishing failed", "creation_id": creation_id, "details": step2_data},
            indent=2,
        )

    return json.dumps(step2_data, indent=2)
