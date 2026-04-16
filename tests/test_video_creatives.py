"""Test that create_ad_creative handles video creatives correctly."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import (
    create_ad_creative,
    _translate_video_customization_rules,
)


def parse_error_result(result: str) -> dict:
    """Parse error result from create_ad_creative, handling decorator wrapping.

    The meta_api_tool decorator has a known quirk where validation errors without
    a 'details' key get wrapped in {"data": "<json_string>"} due to a KeyError
    in the error inspection code. This helper unwraps both formats.
    """
    data = json.loads(result)
    if "data" in data and isinstance(data["data"], str):
        return json.loads(data["data"])
    return data


@pytest.mark.asyncio
async def test_simple_video_creative_uses_video_data():
    """Test that video_id creates a simple creative with object_story_spec.video_data."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Auto-fetch video thumbnail (no thumbnail_url provided)
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_vid_1"},
            # 3) GET creative details
            {"id": "creative_vid_1", "name": "Video Creative", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_987654",
            name="Video Ad",
            link_url="https://example.com/",
            message="Check out this video",
            headline="Watch Now",
            # NOTE: no description here — providing description routes to asset_feed_spec;
            # see test_video_creative_with_description for that path
            call_to_action_type="LEARN_MORE",
            access_token="test_token"
        )

        assert mock_api.call_count == 3

        # First call is the thumbnail auto-fetch
        assert mock_api.call_args_list[0][0][0] == "vid_987654"

        creative_data = mock_api.call_args_list[1][0][2]

        # Should use object_story_spec with video_data, NOT link_data
        assert "object_story_spec" in creative_data
        assert "asset_feed_spec" not in creative_data
        assert "video_data" in creative_data["object_story_spec"]
        assert "link_data" not in creative_data["object_story_spec"]

        video_data = creative_data["object_story_spec"]["video_data"]
        assert video_data["video_id"] == "vid_987654"
        assert video_data["image_url"] == "https://example.com/auto-thumb.jpg"
        assert "link" not in video_data, "link must NOT be in video_data directly"
        assert video_data["message"] == "Check out this video"
        assert video_data["title"] == "Watch Now"
        assert "description" not in video_data
        assert video_data["call_to_action"]["type"] == "LEARN_MORE"
        assert video_data["call_to_action"]["value"]["link"] == "https://example.com/"


@pytest.mark.asyncio
async def test_video_creative_with_thumbnail():
    """Test that thumbnail_url is included as image_url in video_data."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"id": "creative_vid_2"},
            {"id": "creative_vid_2", "name": "Video With Thumb", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_111222",
            thumbnail_url="https://example.com/thumb.jpg",
            name="Video With Thumbnail",
            link_url="https://example.com/",
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[0][0][2]
        video_data = creative_data["object_story_spec"]["video_data"]

        assert video_data["image_url"] == "https://example.com/thumb.jpg"
        assert video_data["video_id"] == "vid_111222"
        # link_url should be in call_to_action.value.link with default CTA type
        assert video_data["call_to_action"]["type"] == "LEARN_MORE"
        assert video_data["call_to_action"]["value"]["link"] == "https://example.com/"


@pytest.mark.asyncio
async def test_video_creative_with_instagram_actor_id():
    """Test that video_id + instagram_actor_id routes through asset_feed_spec.

    Meta returns error 1443048 ("object_story_spec ill formed") when instagram_user_id is
    in object_story_spec but ad_formats=["SINGLE_VIDEO"] is absent from asset_feed_spec.
    The fix: video_id + instagram_actor_id always triggers asset_feed_spec so that
    ad_formats=["SINGLE_VIDEO"] is automatically included in the API call.
    """

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"picture": "https://example.com/auto-thumb.jpg"},
            {"id": "creative_vid_3"},
            {"id": "creative_vid_3", "name": "Video IG", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_333444",
            name="Video For Instagram",
            link_url="https://example.com/",
            instagram_actor_id="ig_555666",
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[1][0][2]

        # Must use asset_feed_spec path (not simple video_data-only path) so that
        # ad_formats=["SINGLE_VIDEO"] is present alongside instagram_user_id.
        assert "asset_feed_spec" in creative_data, (
            "video_id + instagram_actor_id must route through asset_feed_spec "
            "to include ad_formats — otherwise Meta returns error 1443048"
        )
        afs = creative_data["asset_feed_spec"]
        assert afs["ad_formats"] == ["SINGLE_VIDEO"], (
            "ad_formats must be SINGLE_VIDEO for video creatives with instagram_actor_id"
        )
        assert "videos" in afs
        assert afs["videos"][0]["video_id"] == "vid_333444"

        # PR-C: video metadata moved from object_story_spec.video_data to asset_feed_spec.
        # instagram_user_id stays in object_story_spec (instagram_actor_id deprecated Jan 2026).
        assert "object_story_spec" in creative_data
        oss = creative_data["object_story_spec"]
        assert "video_data" not in oss
        assert "link_data" not in oss
        assert "instagram_actor_id" not in oss
        assert oss == {"page_id": "123456789", "instagram_user_id": "ig_555666"}


@pytest.mark.asyncio
async def test_video_creative_asset_feed_spec_path():
    """Test video creative with plural params triggers asset_feed_spec with videos array."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"id": "creative_vid_4"},
            {"id": "creative_vid_4", "name": "Video FLEX", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_555666",
            name="Video FLEX Creative",
            link_url="https://example.com/",
            headlines=["Headline A", "Headline B"],
            messages=["Body text 1", "Body text 2"],
            thumbnail_url="https://example.com/thumb.jpg",
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[0][0][2]

        # Should use asset_feed_spec
        assert "asset_feed_spec" in creative_data
        afs = creative_data["asset_feed_spec"]

        # Should have videos array, NOT images array
        assert "videos" in afs
        assert "images" not in afs
        assert afs["videos"] == [{"video_id": "vid_555666", "thumbnail_url": "https://example.com/thumb.jpg"}]

        # Default ad_formats for video should be SINGLE_VIDEO
        assert afs["ad_formats"] == ["SINGLE_VIDEO"]

        # Should have titles and bodies
        assert len(afs["titles"]) == 2
        assert len(afs["bodies"]) == 2

        # PR-C: video metadata moved from object_story_spec.video_data to asset_feed_spec.
        oss = creative_data["object_story_spec"]
        assert "video_data" not in oss
        assert "link_data" not in oss
        assert oss == {"page_id": "123456789"}
        # link relocated from video_data.call_to_action.value.link to asset_feed_spec.link_urls.
        assert afs["link_urls"] == [{"website_url": "https://example.com/"}]


@pytest.mark.asyncio
async def test_video_creative_with_dof_optimization():
    """Test video creative with DEGREES_OF_FREEDOM optimization_type."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Auto-fetch video thumbnail
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_vid_5"},
            # 3) GET creative details
            {"id": "creative_vid_5", "name": "Video DOF", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_777888",
            name="Video DOF Creative",
            link_url="https://example.com/",
            optimization_type="DEGREES_OF_FREEDOM",
            messages=["Text variant 1", "Text variant 2"],
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[1][0][2]
        afs = creative_data["asset_feed_spec"]

        assert afs["optimization_type"] == "DEGREES_OF_FREEDOM"
        assert "videos" in afs
        # Auto-fetched thumbnail should be included in videos array
        assert afs["videos"] == [{"video_id": "vid_777888", "thumbnail_url": "https://example.com/auto-thumb.jpg"}]

        # PR-C: video metadata moved from object_story_spec.video_data to asset_feed_spec.
        # Thumbnail (was video_data.image_url) is now on asset_feed_spec.videos[].
        oss = creative_data["object_story_spec"]
        assert "video_data" not in oss
        assert "link_data" not in oss
        assert oss == {"page_id": "123456789"}
        assert afs["videos"][0]["thumbnail_url"] == "https://example.com/auto-thumb.jpg"


@pytest.mark.asyncio
async def test_video_and_image_hash_mutual_exclusivity():
    """Test that providing both video_id and image_hash returns an error."""

    result = await create_ad_creative(
        account_id="act_123456",
        video_id="vid_123",
        image_hash="hash_456",
        name="Should Fail",
        link_url="https://example.com/",
        access_token="test_token"
    )

    data = parse_error_result(result)
    assert "error" in data
    assert "Only one media source" in data["error"]


@pytest.mark.asyncio
async def test_video_and_image_hashes_mutual_exclusivity():
    """Test that providing both video_id and image_hashes returns an error."""

    result = await create_ad_creative(
        account_id="act_123456",
        video_id="vid_123",
        image_hashes=["hash_1", "hash_2"],
        name="Should Fail",
        link_url="https://example.com/",
        access_token="test_token"
    )

    data = parse_error_result(result)
    assert "error" in data
    assert "Only one media source" in data["error"]


@pytest.mark.asyncio
async def test_thumbnail_without_video_returns_error():
    """Test that providing thumbnail_url without video_id returns an error."""

    result = await create_ad_creative(
        account_id="act_123456",
        image_hash="hash_123",
        thumbnail_url="https://example.com/thumb.jpg",
        name="Should Fail",
        link_url="https://example.com/",
        access_token="test_token"
    )

    data = parse_error_result(result)
    assert "error" in data
    assert "thumbnail_url can only be used with video_id" in data["error"]


@pytest.mark.asyncio
async def test_no_media_returns_error():
    """Test that providing no media source returns an error."""

    result = await create_ad_creative(
        account_id="act_123456",
        name="Should Fail",
        link_url="https://example.com/",
        access_token="test_token"
    )

    data = parse_error_result(result)
    assert "error" in data
    assert "No media provided" in data["error"]


@pytest.mark.asyncio
async def test_video_creative_with_lead_gen():
    """Test video creative with lead generation form ID."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"picture": "https://example.com/auto-thumb.jpg"},
            {"id": "creative_vid_lead"},
            {"id": "creative_vid_lead", "name": "Video Lead Gen", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_leadgen",
            name="Video Lead Gen Creative",
            link_url="https://example.com/",
            call_to_action_type="SIGN_UP",
            lead_gen_form_id="form_12345",
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[1][0][2]
        video_data = creative_data["object_story_spec"]["video_data"]

        assert "link" not in video_data, "link must NOT be in video_data directly"
        assert video_data["call_to_action"]["type"] == "SIGN_UP"
        assert video_data["call_to_action"]["value"]["link"] == "https://example.com/"
        assert video_data["call_to_action"]["value"]["lead_gen_form_id"] == "form_12345"


@pytest.mark.asyncio
async def test_image_creative_still_works():
    """Regression test: existing image creative path should still work unchanged."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            {"id": "creative_img_1"},
            {"id": "creative_img_1", "name": "Image Creative", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            image_hash="hash_abc123",
            name="Image Ad",
            link_url="https://example.com/",
            message="Click here",
            headline="Great Offer",
            call_to_action_type="SHOP_NOW",
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[0][0][2]

        # Should use link_data, NOT video_data
        assert "link_data" in creative_data["object_story_spec"]
        assert "video_data" not in creative_data["object_story_spec"]

        link_data = creative_data["object_story_spec"]["link_data"]
        assert link_data["image_hash"] == "hash_abc123"
        assert link_data["link"] == "https://example.com/"
        assert link_data["message"] == "Click here"

        # instagram_actor_id at top level for image creatives
        assert "instagram_actor_id" not in creative_data


@pytest.mark.asyncio
async def test_video_creative_with_description():
    """Test that video_id + description routes through asset_feed_spec (not video_data).

    Meta API v24 rejects 'description' inside video_data. To support descriptions
    for video ads, we route to asset_feed_spec when video_id + description is given.
    """

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Auto-fetch video thumbnail
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_vid_desc"},
            # 3) GET creative details
            {"id": "creative_vid_desc", "name": "Video With Desc", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_desc_test",
            name="Video With Description",
            link_url="https://example.com/",
            message="Primary text for the ad",
            headline="Watch Now",
            description="The text below the headline in feed placements",
            call_to_action_type="LEARN_MORE",
            access_token="test_token"
        )

        assert mock_api.call_count == 3

        creative_data = mock_api.call_args_list[1][0][2]

        # Should use asset_feed_spec (not simple video_data path), because
        # video_data does not support description
        assert "asset_feed_spec" in creative_data, (
            "video + description should use asset_feed_spec so description is sent to Meta"
        )

        afs = creative_data["asset_feed_spec"]

        # Description should be in asset_feed_spec.descriptions
        assert "descriptions" in afs, "description should appear in asset_feed_spec.descriptions"
        assert afs["descriptions"] == [{"text": "The text below the headline in feed placements"}]

        # Other fields should also be present
        assert afs["bodies"] == [{"text": "Primary text for the ad"}]
        assert afs["titles"] == [{"text": "Watch Now"}]
        assert "videos" in afs
        assert afs["videos"][0]["video_id"] == "vid_desc_test"

        # PR-C: video metadata moved from object_story_spec.video_data to asset_feed_spec.
        # description is carried by asset_feed_spec.descriptions (asserted above).
        oss = creative_data["object_story_spec"]
        assert "video_data" not in oss
        assert "link_data" not in oss
        assert oss == {"page_id": "123456789"}


@pytest.mark.asyncio
async def test_video_creative_description_only():
    """Test that video_id + description alone (no other plural params) still works."""

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Auto-fetch video thumbnail
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_vid_desc2"},
            # 3) GET creative details
            {"id": "creative_vid_desc2", "name": "Video Desc Only", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_desc_only",
            name="Video Description Only",
            link_url="https://example.com/",
            description="Only description, no other plural params",
            access_token="test_token"
        )

        assert mock_api.call_count == 3

        creative_data = mock_api.call_args_list[1][0][2]

        assert "asset_feed_spec" in creative_data
        afs = creative_data["asset_feed_spec"]
        assert afs["descriptions"] == [{"text": "Only description, no other plural params"}]
        assert "videos" in afs


@pytest.mark.asyncio
async def test_video_creative_instagram_actor_id_with_explicit_ad_formats():
    """Test that explicitly passing ad_formats with instagram_actor_id + video_id also works.

    The caller can still explicitly pass ad_formats=["SINGLE_VIDEO"]; it should be
    respected (not overridden) when both instagram_actor_id and video_id are present.
    """

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Auto-fetch video thumbnail
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_vid_ig_fmt"},
            # 3) GET creative details
            {"id": "creative_vid_ig_fmt", "name": "Video IG Explicit Fmt", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_explicit_fmt",
            name="Video IG Explicit Format",
            link_url="https://example.com/",
            instagram_actor_id="ig_777888",
            ad_formats=["SINGLE_VIDEO"],
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[1][0][2]

        # Must route through asset_feed_spec with explicit ad_formats respected
        assert "asset_feed_spec" in creative_data
        afs = creative_data["asset_feed_spec"]
        assert afs["ad_formats"] == ["SINGLE_VIDEO"]
        assert "videos" in afs
        assert afs["videos"][0]["video_id"] == "vid_explicit_fmt"
        assert creative_data["object_story_spec"]["instagram_user_id"] == "ig_777888"


@pytest.mark.asyncio
async def test_video_creative_without_instagram_actor_id_uses_simple_path():
    """Regression: video_id without instagram_actor_id still uses simple object_story_spec path.

    Only video_id + instagram_actor_id together triggers asset_feed_spec routing.
    A plain video creative (no instagram_actor_id) should still use the simple path.
    """

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Auto-fetch video thumbnail
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_vid_simple"},
            # 3) GET creative details
            {"id": "creative_vid_simple", "name": "Simple Video", "status": "ACTIVE"}
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            video_id="vid_simple_only",
            name="Simple Video No IG",
            link_url="https://example.com/",
            # No instagram_actor_id — should stay on simple path
            access_token="test_token"
        )

        creative_data = mock_api.call_args_list[1][0][2]

        # Without instagram_actor_id, should use simple object_story_spec path (no asset_feed_spec)
        assert "asset_feed_spec" not in creative_data
        assert "object_story_spec" in creative_data
        assert "video_data" in creative_data["object_story_spec"]
        assert "instagram_user_id" not in creative_data["object_story_spec"]


@pytest.mark.asyncio
async def test_videos_array_does_not_trigger_thumbnail_fetch_with_none():
    """Regression: when only videos=[...] is passed (no singular video_id, no thumbnail_url),
    the singular-video thumbnail auto-fetch must NOT call Meta with video_id=None.

    Previously the guard was `if is_video and not thumbnail_url`, where
    `is_video = bool(video_id or videos)`. That meant the videos=[...] path also
    triggered the singular-video thumbnail fetch — which then called
    make_api_request(None, ...) and Meta returned a generic error logged as
    "Could not auto-fetch thumbnail for video None".

    The fix tightens the guard to `if video_id and not thumbnail_url`, so the
    singular-video fetch only runs when video_id is actually set.

    Note: the videos[] branch DOES auto-fetch per-entry thumbnails (each call uses
    the actual entry's video_id, never None). This regression test specifically
    asserts that no call is ever made with `None` as the first positional arg.
    """

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page"
        }

        mock_api.side_effect = [
            # 1) Per-video thumbnail auto-fetch (videos[] branch) — uses real vid_id
            {"picture": "https://example.com/auto-thumb.jpg"},
            # 2) POST create creative
            {"id": "creative_videos_arr"},
            # 3) GET creative details
            {"id": "creative_videos_arr", "name": "Videos Array Creative", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            videos=[{"video_id": "vid_videos_arr"}],  # plural form, no thumbnail_url
            name="Videos Array Test",
            link_url="https://example.com/",
            access_token="test_token",
        )

        # Critically, none of the calls should have been made with None as the
        # first positional argument (which is what the buggy guard produced).
        for call in mock_api.call_args_list:
            assert call.args[0] is not None, (
                f"make_api_request was called with None as the first arg "
                f"(args={call.args!r}); the singular-video thumbnail auto-fetch "
                f"should be skipped when only videos=[...] is provided"
            )


# ---------------------------------------------------------------------------
# Unit tests for _translate_video_customization_rules (videos[] path)
# ---------------------------------------------------------------------------

def test_translate_video_rules_placement_groups_format():
    """placement_groups + customization_spec.video_ids translates to Meta API format.

    Expected Meta format:
      - rule has customization_spec.publisher_platforms and facebook/instagram_positions
      - rule has video_label: {"name": "..."} at the rule level
      - rule has NO `placement_groups` key
      - videos_array entries get `adlabels` assigned matching their rule
    """
    videos_array = [
        {"video_id": "vidA"},
        {"video_id": "vidB"},
    ]
    rules = [
        {
            "placement_groups": ["FEED"],
            "customization_spec": {"video_ids": ["vidA"]},
        },
        {
            "placement_groups": ["STORY"],
            "customization_spec": {"video_ids": ["vidB"]},
        },
    ]

    translated, updated_videos = _translate_video_customization_rules(rules, videos_array)

    # Both rules translated
    assert len(translated) == 2

    # FEED rule
    feed_rule = translated[0]
    assert "placement_groups" not in feed_rule
    feed_cspec = feed_rule["customization_spec"]
    assert "facebook" in feed_cspec["publisher_platforms"]
    assert "instagram" in feed_cspec["publisher_platforms"]
    assert "feed" in feed_cspec["facebook_positions"]
    assert feed_rule["video_label"] == {"name": "PBOARD_VID_0"}

    # STORY rule
    story_rule = translated[1]
    assert "placement_groups" not in story_rule
    story_cspec = story_rule["customization_spec"]
    assert "story" in story_cspec["facebook_positions"]
    assert "story" in story_cspec["instagram_positions"]
    assert story_rule["video_label"] == {"name": "PBOARD_VID_1"}

    # videos_array gets adlabels
    assert len(updated_videos) == 2
    assert updated_videos[0]["video_id"] == "vidA"
    assert updated_videos[0]["adlabels"] == [{"name": "PBOARD_VID_0"}]
    assert updated_videos[1]["video_id"] == "vidB"
    assert updated_videos[1]["adlabels"] == [{"name": "PBOARD_VID_1"}]


def test_translate_video_rules_passthrough_raw_format():
    """Rules already in Meta API format (no placement_groups) pass through unchanged."""
    videos_array = [
        {"video_id": "vidA", "adlabels": [{"name": "labelfb"}]},
    ]
    raw_rules = [
        {
            "customization_spec": {
                "publisher_platforms": ["facebook"],
                "facebook_positions": ["feed"],
            },
            "video_label": {"name": "labelfb"},
        },
    ]

    translated, updated_videos = _translate_video_customization_rules(raw_rules, videos_array)

    # Rules passed through unchanged
    assert translated == raw_rules
    # videos_array passed through unchanged
    assert updated_videos == videos_array


def test_translate_video_rules_preserves_existing_adlabels():
    """If videos_array entries already have adlabels, do not override them."""
    # User-supplied labels via videos[{"label": "my_label"}]
    videos_array = [
        {"video_id": "vidA", "adlabels": [{"name": "user_label"}]},
    ]
    rules = [
        {
            "placement_groups": ["FEED"],
            "customization_spec": {"video_ids": ["vidA"]},
        },
    ]

    translated, updated_videos = _translate_video_customization_rules(rules, videos_array)

    # video_label at rule level uses auto-generated name
    assert translated[0]["video_label"] == {"name": "PBOARD_VID_0"}
    # ...but the existing adlabels on the video are preserved (not overridden)
    assert updated_videos[0]["adlabels"] == [{"name": "user_label"}]


def test_translate_video_rules_string_video_label_coerced():
    """Caller passes customization_spec.video_label: 'str' — coerce to {"name": 'str'}.

    This handles TEST 3 from matt's test cases: string video_label inside
    customization_spec should be lifted to the rule level as an object.
    """
    videos_array = [
        {"video_id": "vidA", "adlabels": [{"name": "vert"}]},
    ]
    rules = [
        {
            "placement_groups": ["STORY"],
            "customization_spec": {"video_label": "vert"},
        },
    ]

    translated, updated_videos = _translate_video_customization_rules(rules, videos_array)

    assert len(translated) == 1
    rule = translated[0]
    assert "placement_groups" not in rule
    # video_label coerced from string to object, hoisted to rule level
    assert rule["video_label"] == {"name": "vert"}
    # customization_spec does not carry video_label (it's moved to rule level)
    assert "video_label" not in rule["customization_spec"]
    # videos_array untouched because we didn't generate any labels
    assert updated_videos == videos_array


@pytest.mark.asyncio
async def test_create_ad_creative_videos_with_placement_rules_sends_correct_payload():
    """End-to-end: videos[] + asset_customization_rules with placement_groups.

    Mirrors matt's TEST 6 payload. The resulting Meta API payload must have:
      - asset_feed_spec.videos with adlabels
      - asset_feed_spec.asset_customization_rules in Meta format
        (publisher_platforms, facebook/instagram_positions, video_label)
      - NO `placement_groups` key anywhere
      - NO raw `video_ids` inside customization_spec in the outgoing rules
    """
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }

        mock_api.side_effect = [
            # 1) Per-video thumbnail auto-fetch for vidA (videos[] branch)
            {"picture": "https://example.com/vidA-thumb.jpg"},
            # 2) Per-video thumbnail auto-fetch for vidB
            {"picture": "https://example.com/vidB-thumb.jpg"},
            # 3) POST create creative
            {"id": "creative_vid_rules"},
            # 4) GET creative details
            {"id": "creative_vid_rules", "name": "Video Placement Rules", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            videos=[
                {"video_id": "vidA"},
                {"video_id": "vidB"},
            ],
            asset_customization_rules=[
                {
                    "placement_groups": ["FEED"],
                    "customization_spec": {"video_ids": ["vidA"]},
                },
                {
                    "placement_groups": ["STORY"],
                    "customization_spec": {"video_ids": ["vidB"]},
                },
            ],
            name="Video Placement Rules",
            link_url="https://example.com/",
            message="Check it out",
            headline="Watch Now",
            call_to_action_type="LEARN_MORE",
            access_token="test_token",
        )

        # 2 thumbnail auto-fetches + POST + GET details = 4 calls
        assert mock_api.call_count == 4
        # POST is the 3rd call (after the two thumbnail GETs)
        creative_data = mock_api.call_args_list[2][0][2]

        assert "asset_feed_spec" in creative_data
        afs = creative_data["asset_feed_spec"]

        # videos[] entries must have adlabels
        assert "videos" in afs
        videos_out = afs["videos"]
        assert len(videos_out) == 2
        assert videos_out[0]["video_id"] == "vidA"
        assert videos_out[0]["adlabels"] == [{"name": "PBOARD_VID_0"}]
        assert videos_out[1]["video_id"] == "vidB"
        assert videos_out[1]["adlabels"] == [{"name": "PBOARD_VID_1"}]

        # Rules must be in Meta API format
        assert "asset_customization_rules" in afs
        rules_out = afs["asset_customization_rules"]
        assert len(rules_out) == 2

        # No user-facing placement_groups anywhere in outgoing payload
        for r in rules_out:
            assert "placement_groups" not in r, (
                f"placement_groups must not ship to Meta: {r!r}"
            )
            # video_ids inside customization_spec should have been converted to
            # video_label at the rule level; raw video_ids must not ship to Meta
            cspec = r.get("customization_spec", {})
            assert "video_ids" not in cspec, (
                f"customization_spec.video_ids must not ship to Meta: {r!r}"
            )

        # FEED rule has feed positions and video_label
        feed_rule = rules_out[0]
        assert "feed" in feed_rule["customization_spec"]["facebook_positions"]
        assert feed_rule["video_label"] == {"name": "PBOARD_VID_0"}

        # STORY rule has story positions and video_label
        story_rule = rules_out[1]
        assert "story" in story_rule["customization_spec"]["facebook_positions"]
        assert "story" in story_rule["customization_spec"]["instagram_positions"]
        assert story_rule["video_label"] == {"name": "PBOARD_VID_1"}


# ---------------------------------------------------------------------------
# Per-video thumbnail auto-fetch in the videos=[...] branch (PR-B)
# ---------------------------------------------------------------------------
# Meta API v24 requires a thumbnail (image_hash or image_url) for each entry
# in asset_feed_spec.videos[]. Without it, creates fail with error 1443226
# ("Please specify one of image_hash or image_url in the video_data field
# of object_story_spec"). These tests cover the per-entry auto-fetch the
# videos[] path performs in parallel.


@pytest.mark.asyncio
async def test_videos_array_auto_fetches_missing_thumbnails():
    """When entries in videos=[...] have no thumbnail_url, fetch each one in parallel
    via {video_id}?fields=picture,thumbnails and apply the result to the entry.

    Expected calls: 2 thumbnail GETs (one per video) + 1 POST creative + 1 GET details = 4.
    """
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }

        mock_api.side_effect = [
            # 1) Thumbnail fetch for "a"
            {"picture": "https://example.com/picA.jpg",
             "thumbnails": {"data": [{"uri": "https://example.com/thumbA.jpg"}]}},
            # 2) Thumbnail fetch for "b"
            {"picture": "https://example.com/picB.jpg",
             "thumbnails": {"data": [{"uri": "https://example.com/thumbB.jpg"}]}},
            # 3) POST create creative
            {"id": "creative_auto_thumb"},
            # 4) GET creative details
            {"id": "creative_auto_thumb", "name": "Auto Thumb", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            videos=[{"video_id": "a"}, {"video_id": "b"}],
            name="Auto Thumb",
            link_url="https://example.com/",
            message="hi",
            headline="hi",
            call_to_action_type="LEARN_MORE",
            access_token="test_token",
        )

        assert mock_api.call_count == 4, (
            f"Expected 4 calls (2 thumb GETs + POST + GET details), got "
            f"{mock_api.call_count}: {[c.args[0] for c in mock_api.call_args_list]}"
        )

        # First two calls are the thumbnail GETs.
        thumb_call_a = mock_api.call_args_list[0]
        thumb_call_b = mock_api.call_args_list[1]
        # First positional arg is the video_id (endpoint path).
        ids_fetched = {thumb_call_a.args[0], thumb_call_b.args[0]}
        assert ids_fetched == {"a", "b"}
        # Both thumbnail GETs should request picture,thumbnails.
        for c in (thumb_call_a, thumb_call_b):
            params = c.args[2]
            assert params.get("fields") == "picture,thumbnails"

        # POST is the 3rd call. asset_feed_spec.videos must carry the fetched URIs.
        creative_data = mock_api.call_args_list[2][0][2]
        afs = creative_data["asset_feed_spec"]
        videos_out = afs["videos"]
        assert len(videos_out) == 2
        by_id = {v["video_id"]: v for v in videos_out}
        assert by_id["a"]["thumbnail_url"] == "https://example.com/thumbA.jpg"
        assert by_id["b"]["thumbnail_url"] == "https://example.com/thumbB.jpg"


@pytest.mark.asyncio
async def test_videos_array_uses_provided_thumbnails_without_fetch():
    """When every videos[] entry already has a thumbnail_url, no auto-fetch should
    happen. Only POST + GET details = 2 calls.
    """
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }

        mock_api.side_effect = [
            {"id": "creative_provided_thumb"},
            {"id": "creative_provided_thumb", "name": "Provided", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            videos=[
                {"video_id": "a", "thumbnail_url": "https://x"},
                {"video_id": "b", "thumbnail_url": "https://y"},
            ],
            name="Provided Thumb",
            link_url="https://example.com/",
            message="hi",
            headline="hi",
            call_to_action_type="LEARN_MORE",
            access_token="test_token",
        )

        assert mock_api.call_count == 2, (
            f"Expected 2 calls (POST + GET details), got {mock_api.call_count}: "
            f"{[c.args[0] for c in mock_api.call_args_list]}"
        )

        # First call is the POST. Both provided thumbnail_urls preserved verbatim.
        creative_data = mock_api.call_args_list[0][0][2]
        afs = creative_data["asset_feed_spec"]
        by_id = {v["video_id"]: v for v in afs["videos"]}
        assert by_id["a"]["thumbnail_url"] == "https://x"
        assert by_id["b"]["thumbnail_url"] == "https://y"


@pytest.mark.asyncio
async def test_video_thumbnail_fetch_prefers_thumbnails_uri_over_picture():
    """`_fetch_video_thumbnail` must prefer the pre-generated thumbnails.data[0].uri
    over the `picture` field, since `picture` can be a small placeholder while
    thumbnails carries the actual generated frame.
    """
    from meta_ads_mcp.core.ads import _fetch_video_thumbnail

    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api:
        mock_api.return_value = {
            "picture": "https://example.com/placeholder-picture.jpg",
            "thumbnails": {
                "data": [
                    {"uri": "https://example.com/preferred-thumb.jpg"},
                    {"uri": "https://example.com/another-thumb.jpg"},
                ]
            },
        }

        result = await _fetch_video_thumbnail("vid_123", "test_token")

        assert result == "https://example.com/preferred-thumb.jpg"
        # Sanity: it should have asked for both fields.
        params = mock_api.call_args.args[2]
        assert params.get("fields") == "picture,thumbnails"


@pytest.mark.asyncio
async def test_videos_array_proceeds_when_thumbnail_fetch_fails():
    """If the thumbnail fetch returns nothing usable (empty/None), the videos[]
    path should still proceed. The entry simply ships without a thumbnail_url —
    Meta will return its own actionable error if it actually needs one.
    """
    with patch('meta_ads_mcp.core.ads.make_api_request') as mock_api, \
         patch('meta_ads_mcp.core.ads._discover_pages_for_account') as mock_discover:

        mock_discover.return_value = {
            "success": True,
            "page_id": "123456789",
            "page_name": "Test Page",
        }

        mock_api.side_effect = [
            # 1) Thumbnail fetch: API returned an empty dict (no picture, no thumbnails)
            {},
            # 2) POST create creative
            {"id": "creative_fail_thumb"},
            # 3) GET creative details
            {"id": "creative_fail_thumb", "name": "Fail Thumb", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            videos=[{"video_id": "vid_no_thumb"}],
            name="Fail Thumb",
            link_url="https://example.com/",
            message="hi",
            headline="hi",
            call_to_action_type="LEARN_MORE",
            access_token="test_token",
        )

        assert mock_api.call_count == 3
        creative_data = mock_api.call_args_list[1][0][2]
        afs = creative_data["asset_feed_spec"]
        videos_out = afs["videos"]
        assert len(videos_out) == 1
        # No thumbnail_url on the entry — graceful degradation.
        assert "thumbnail_url" not in videos_out[0]
        assert videos_out[0]["video_id"] == "vid_no_thumb"
