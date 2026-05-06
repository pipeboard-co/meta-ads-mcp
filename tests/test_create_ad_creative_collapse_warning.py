"""Tests for create_ad_creative readback-based collapse detection."""

import pytest
import json
from unittest.mock import patch
from meta_ads_mcp.core.ads import create_ad_creative


def _mock_page_discovery():
    return patch(
        "meta_ads_mcp.core.ads._discover_pages_for_account",
        return_value={"success": True, "page_id": "p", "page_name": "T"},
    )


@pytest.mark.asyncio
async def test_warning_when_asset_feed_spec_missing_on_readback():
    collapsed_readback = {
        "id": "c1",
        "object_story_spec": {"page_id": "p", "link_data": {"image_hash": "h1", "link": "https://ex.com"}},
    }
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, _mock_page_discovery():
        mock_api.side_effect = [{"id": "c1"}, collapsed_readback]
        result_json = await create_ad_creative(
            account_id="act_1",
            page_id="p",
            link_url="https://ex.com",
            image_hashes=["h1", "h2"],
            asset_customization_rules=[
                {"placement_groups": ["FEED"], "customization_spec": {"image_hashes": ["h1"]}},
                {"placement_groups": ["STORY"], "customization_spec": {"image_hashes": ["h2"]}},
            ],
            headline="Hi",
            description="Desc",
            message="Msg",
            call_to_action_type="SHOP_NOW",
            access_token="tok",
        )
        result = json.loads(result_json)
        posted = mock_api.call_args_list[0][0][2]
        assert len(posted["asset_feed_spec"]["images"]) == 2
        assert posted["asset_feed_spec"]["asset_customization_rules"]
        warning = result.get("warning")
        assert warning is not None
        warn_text = warning if isinstance(warning, str) else " ".join(warning)
        assert "silently rewrote" in warn_text
        assert "is_dynamic_creative" in warn_text


@pytest.mark.asyncio
async def test_no_warning_when_asset_feed_spec_preserved():
    preserved_readback = {
        "id": "c2",
        "object_story_spec": {"page_id": "p"},
        "asset_feed_spec": {
            "images": [{"hash": "h1"}, {"hash": "h2"}],
            "asset_customization_rules": [{"customization_spec": {"publisher_platforms": ["facebook"]}}],
            "optimization_type": "PLACEMENT",
        },
    }
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, _mock_page_discovery():
        mock_api.side_effect = [{"id": "c2"}, preserved_readback]
        result_json = await create_ad_creative(
            account_id="act_1",
            page_id="p",
            link_url="https://ex.com",
            image_hashes=["h1", "h2"],
            asset_customization_rules=[
                {"placement_groups": ["FEED"], "customization_spec": {"image_hashes": ["h1"]}},
                {"placement_groups": ["STORY"], "customization_spec": {"image_hashes": ["h2"]}},
            ],
            headline="Hi",
            description="Desc",
            message="Msg",
            access_token="tok",
        )
        result = json.loads(result_json)
        warning = result.get("warning")
        warn_text = "" if warning is None else (warning if isinstance(warning, str) else " ".join(warning))
        assert "silently rewrote" not in warn_text


@pytest.mark.asyncio
async def test_dof_downgrade_warning_revised():
    preserved_readback = {
        "id": "c3",
        "object_story_spec": {"page_id": "p"},
        "asset_feed_spec": {
            "images": [{"hash": "h1"}, {"hash": "h2"}],
            "asset_customization_rules": [{"customization_spec": {}}],
        },
    }
    with patch("meta_ads_mcp.core.ads.make_api_request") as mock_api, _mock_page_discovery():
        mock_api.side_effect = [{"id": "c3"}, preserved_readback]
        result_json = await create_ad_creative(
            account_id="act_1",
            page_id="p",
            link_url="https://ex.com",
            image_hashes=["h1", "h2"],
            asset_customization_rules=[
                {"placement_groups": ["FEED"], "customization_spec": {"image_hashes": ["h1"]}},
                {"placement_groups": ["STORY"], "customization_spec": {"image_hashes": ["h2"]}},
            ],
            optimization_type="DEGREES_OF_FREEDOM",
            headline="Hi",
            description="Desc",
            message="Msg",
            access_token="tok",
        )
        result = json.loads(result_json)
        warning = result.get("warning")
        assert warning is not None
        warn_text = warning if isinstance(warning, str) else " ".join(warning)
        assert "placement-specific images are respected" not in warn_text
        # The downgrade lands the creative in PAC, which routes by placement
        # without the ad set's is_dynamic_creative flag. The warning must not
        # claim rules depend on is_dynamic_creative (they don't — that's the
        # gate for regular Dynamic Creative, not Placement Asset Customization).
        assert "depends on" not in warn_text and "take effect depends" not in warn_text
        assert "Placement" in warn_text or "PLACEMENT" in warn_text
