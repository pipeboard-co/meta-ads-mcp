"""Test that create_ad_creative handles video creatives correctly."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative


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
            description="Amazing content",
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
        assert video_data["description"] == "Amazing content"
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
    """Test that instagram_actor_id goes inside video_data for simple video creatives."""

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
        video_data = creative_data["object_story_spec"]["video_data"]

        # For simple video creatives, instagram_actor_id should be inside video_data
        assert video_data["instagram_actor_id"] == "ig_555666"
        # And NOT at the top level
        assert "instagram_actor_id" not in creative_data


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

        # object_story_spec should use video_data anchor without "link"
        assert "video_data" in creative_data["object_story_spec"]
        assert creative_data["object_story_spec"]["video_data"]["video_id"] == "vid_555666"
        assert "link" not in creative_data["object_story_spec"]["video_data"]


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

        # video_data anchor should have image_url and not "link"
        assert creative_data["object_story_spec"]["video_data"]["image_url"] == "https://example.com/auto-thumb.jpg"
        assert "link" not in creative_data["object_story_spec"]["video_data"]


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
