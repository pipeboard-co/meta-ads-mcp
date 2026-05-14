"""Tests for object_story_id support in create_ad_creative and bulk_create_ad_creatives."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.ads import (
    create_ad_creative,
    _translate_video_customization_rules_for_existing_post,
    _ALL_ENHANCEMENT_KEYS,
)


# ---------------------------------------------------------------------------
# Unit tests for _translate_video_customization_rules_for_existing_post
# ---------------------------------------------------------------------------

def test_translate_video_rules_story_placement():
    """Translates STORY placement_groups to Meta API positions."""
    rules = [
        {
            "placement_groups": ["STORY"],
            "customization_spec": {"video_ids": ["vid123"]},
        }
    ]
    translated, videos = _translate_video_customization_rules_for_existing_post(rules)

    assert len(videos) == 1
    assert videos[0]["video_id"] == "vid123"
    assert videos[0]["adlabels"] == [{"name": "PBOARD_VID_0"}]

    assert len(translated) == 1
    cspec = translated[0]["customization_spec"]
    assert "facebook" in cspec["publisher_platforms"]
    assert "instagram" in cspec["publisher_platforms"]
    assert "story" in cspec["facebook_positions"]
    assert "story" in cspec["instagram_positions"]
    assert translated[0]["video_label"] == {"name": "PBOARD_VID_0"}


def test_translate_video_rules_no_placement_groups_passthrough():
    """Rules without placement_groups are passed through unchanged."""
    raw_rules = [
        {
            "customization_spec": {"publisher_platforms": ["instagram"]},
            "video_label": {"name": "my_label"},
        }
    ]
    translated, videos = _translate_video_customization_rules_for_existing_post(raw_rules)
    assert translated == raw_rules
    assert videos == []


def test_translate_video_rules_multiple_placements():
    """Multiple placement groups merge into one customization_spec."""
    rules = [
        {
            "placement_groups": ["STORY", "FEED"],
            "customization_spec": {"video_ids": ["vid_abc"]},
        }
    ]
    translated, videos = _translate_video_customization_rules_for_existing_post(rules)

    cspec = translated[0]["customization_spec"]
    assert "facebook" in cspec["publisher_platforms"]
    assert "instagram" in cspec["publisher_platforms"]
    # STORY adds story positions; FEED adds feed/stream positions
    assert "story" in cspec.get("facebook_positions", [])
    assert "feed" in cspec.get("facebook_positions", [])


def test_translate_video_rules_empty():
    """Empty rules list returns empty results."""
    translated, videos = _translate_video_customization_rules_for_existing_post([])
    assert translated == []
    assert videos == []


# ---------------------------------------------------------------------------
# create_ad_creative: object_story_id basic path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_simple():
    """object_story_id passed directly to Meta API without object_story_spec."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_1"},
            {"id": "creative_osi_1", "name": "OSI Creative", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            access_token="test_token",
        )

        parsed = json.loads(result)
        assert parsed["success"] is True

        create_call = mock_api.call_args_list[0]
        creative_data = create_call[0][2]

        assert creative_data["object_story_id"] == "124965744226834_3888007311337206"
        assert "object_story_spec" not in creative_data
        assert "asset_feed_spec" not in creative_data


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_with_cta():
    """object_story_id + call_to_action_type uses top-level call_to_action."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_2"},
            {"id": "creative_osi_2", "name": "OSI Creative CTA", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            call_to_action_type="SEE_MENU",
            link_url="https://kfc.rs/meni/dinein",
            access_token="test_token",
        )

        parsed = json.loads(result)
        assert parsed["success"] is True

        creative_data = mock_api.call_args_list[0][0][2]

        assert creative_data["object_story_id"] == "124965744226834_3888007311337206"
        assert "call_to_action" in creative_data
        assert creative_data["call_to_action"]["type"] == "SEE_MENU"
        assert creative_data["call_to_action"]["value"]["link"] == "https://kfc.rs/meni/dinein"


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_with_asset_customization():
    """object_story_id + asset_customization_rules builds asset_feed_spec with videos."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_3"},
            {"id": "creative_osi_3", "name": "OSI + Story video", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            asset_customization_rules=[
                {
                    "placement_groups": ["STORY"],
                    "customization_spec": {"video_ids": ["890310874031162"]},
                }
            ],
            call_to_action_type="SEE_MENU",
            link_url="https://kfc.rs/meni/dinein",
            access_token="test_token",
        )

        parsed = json.loads(result)
        assert parsed["success"] is True

        creative_data = mock_api.call_args_list[0][0][2]

        assert creative_data["object_story_id"] == "124965744226834_3888007311337206"
        assert "asset_feed_spec" in creative_data

        afs = creative_data["asset_feed_spec"]
        assert len(afs["videos"]) == 1
        assert afs["videos"][0]["video_id"] == "890310874031162"
        assert afs["link_urls"] == [{"website_url": "https://kfc.rs/meni/dinein"}]
        assert afs["call_to_action_types"] == ["SEE_MENU"]

        rules = afs["asset_customization_rules"]
        assert len(rules) == 1
        assert "story" in rules[0]["customization_spec"].get("facebook_positions", [])
        assert "video_label" in rules[0]


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_translates_instagram_actor_id():
    """object_story_id + instagram_actor_id must translate to top-level
    instagram_user_id (Meta deprecated instagram_actor_id at POST
    /act_ID/adcreatives in Jan 2026; sending the old name returns error 100).
    """
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_ig"},
            {"id": "creative_osi_ig", "name": "OSI + IG", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            instagram_actor_id="17841476585143410",
            call_to_action_type="SHOP_NOW",
            link_url="https://example.com/",
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]

        # Deprecated field name must NOT appear anywhere on the request.
        assert "instagram_actor_id" not in creative_data
        # New field name must appear at the top level (object_story_id path has
        # no object_story_spec to nest it under).
        assert creative_data["instagram_user_id"] == "17841476585143410"
        # object_story_id still passed through unchanged.
        assert creative_data["object_story_id"] == "124965744226834_3888007311337206"


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_with_asset_customization_translates_instagram_actor_id():
    """object_story_id + asset_customization_rules + instagram_actor_id —
    even when asset_feed_spec is built, the deprecated field must still be
    translated to instagram_user_id at the top level.
    """
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_ig_acr"},
            {"id": "creative_osi_ig_acr", "status": "ACTIVE"},
        ]

        await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            asset_customization_rules=[
                {
                    "placement_groups": ["STORY"],
                    "customization_spec": {"video_ids": ["890310874031162"]},
                }
            ],
            instagram_actor_id="17841476585143410",
            call_to_action_type="SHOP_NOW",
            link_url="https://example.com/",
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        assert "instagram_actor_id" not in creative_data
        assert creative_data["instagram_user_id"] == "17841476585143410"
        assert "asset_feed_spec" in creative_data


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_invalid_instagram_error_no_longer_blames_scope():
    """When Meta returns 'Param instagram_actor_id must be a valid Instagram
    account id' for the object_story_id path, the error enhancement must not
    falsely claim the token is missing the instagram_basic permission.
    """
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.return_value = {
            "error": {
                "details": {
                    "error": {
                        "code": 100,
                        "message": "Param instagram_actor_id must be a valid Instagram account id",
                    }
                }
            }
        }

        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            instagram_actor_id="17841476585143410",
            call_to_action_type="SHOP_NOW",
            link_url="https://example.com/",
            access_token="test_token",
        )

        # The meta_api_tool decorator wraps error responses without a "details"
        # key as {"data": "<json_string>"} — unwrap both shapes.
        parsed = json.loads(result)
        if "data" in parsed and isinstance(parsed["data"], str):
            parsed = json.loads(parsed["data"])
        # The misleading instagram_basic explanation must be gone.
        explanation = parsed.get("explanation", "")
        assert "instagram_basic" not in explanation
        # And the fix advice must no longer tell the user to reconnect their
        # Facebook account — that does not actually resolve this Meta error.
        fix = parsed.get("fix", "")
        assert "Reconnect" not in fix
        # The new guidance should point to get_instagram_accounts.
        assert "get_instagram_accounts" in fix


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_no_media_required():
    """object_story_id bypasses the image_hash/video_id requirement."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_4"},
            {"id": "creative_osi_4", "name": "OSI no media check", "status": "ACTIVE"},
        ]

        # Should NOT return an error about missing media
        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            access_token="test_token",
        )

        parsed = json.loads(result)
        assert "error" not in parsed or parsed.get("success") is True


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_no_page_required():
    """object_story_id bypasses page_id discovery."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, \
         patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:
        mock_api.side_effect = [
            {"id": "creative_osi_5"},
            {"id": "creative_osi_5", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            access_token="test_token",
        )

        # Page discovery should NOT be called
        mock_discover.assert_not_called()

        parsed = json.loads(result)
        assert parsed.get("success") is True


# ---------------------------------------------------------------------------
# create_ad_creative: disable_all_enhancements
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_ad_creative_disable_all_enhancements():
    """disable_all_enhancements=True sets every individual enhancement key to OPT_OUT."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, \
         patch("meta_ads_mcp.core.ads._discover_pages_for_account") as mock_discover:
        mock_discover.return_value = {"success": True, "page_id": "111", "page_name": "Test"}
        mock_api.side_effect = [
            {"id": "creative_dae_1"},
            {"id": "creative_dae_1", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            image_hash="test_hash",
            link_url="https://example.com",
            disable_all_enhancements=True,
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        dof = creative_data.get("degrees_of_freedom_spec", {})
        cfs = dof.get("creative_features_spec", {})
        # Every individual key should be OPT_OUT — "standard_enhancements" is deprecated
        for key in _ALL_ENHANCEMENT_KEYS:
            assert cfs.get(key) == {"enroll_status": "OPT_OUT"}, f"Expected {key} OPT_OUT"
        assert "standard_enhancements" not in cfs, "deprecated key must not be sent"
        # contextual_multi_ads should also be disabled
        assert creative_data.get("contextual_multi_ads") == {"enroll_status": "OPT_OUT"}


@pytest.mark.asyncio
async def test_create_ad_creative_object_story_id_with_disable_enhancements():
    """object_story_id + disable_all_enhancements works together."""
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api:
        mock_api.side_effect = [
            {"id": "creative_osi_dae"},
            {"id": "creative_osi_dae", "status": "ACTIVE"},
        ]

        result = await create_ad_creative(
            account_id="act_123456",
            object_story_id="124965744226834_3888007311337206",
            call_to_action_type="SEE_MENU",
            link_url="https://kfc.rs/meni/dinein",
            disable_all_enhancements=True,
            access_token="test_token",
        )

        creative_data = mock_api.call_args_list[0][0][2]
        assert creative_data["object_story_id"] == "124965744226834_3888007311337206"
        dof = creative_data.get("degrees_of_freedom_spec", {})
        cfs = dof.get("creative_features_spec", {})
        for key in _ALL_ENHANCEMENT_KEYS:
            assert cfs.get(key) == {"enroll_status": "OPT_OUT"}, f"Expected {key} OPT_OUT"
        assert "standard_enhancements" not in cfs
        assert creative_data.get("contextual_multi_ads") == {"enroll_status": "OPT_OUT"}
