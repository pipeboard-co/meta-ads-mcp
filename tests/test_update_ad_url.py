"""Tests for update_ad_url.

update_ad_url changes the destination URL / url_tags of an existing (possibly
running) ad by cloning its current creative, changing only the URL, creating a
new creative, and swapping it onto the SAME ad (ad_id unchanged). These tests
mock make_api_request and assert the request sequence and the cloned params for
each creative shape, plus dry-run and validation behaviour.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.ads import update_ad_url

NEW = "https://example.com/new"
OLD = "https://example.com/old"


def _seq(*responses):
    """AsyncMock whose successive calls return the given responses in order."""
    return AsyncMock(side_effect=list(responses))


def _parse(raw):
    """Parse a tool result, unwrapping the {"data": "<json>"} envelope that the
    meta_api_tool decorator puts around error responses."""
    parsed = json.loads(raw)
    if isinstance(parsed, dict) and list(parsed.keys()) == ["data"] and isinstance(parsed["data"], str):
        return json.loads(parsed["data"])
    return parsed


@pytest.mark.asyncio
class TestUpdateAdUrl:

    async def test_link_data_url_change(self):
        ad = {"account_id": "123", "creative": {
            "id": "old_cr", "name": "cr", "url_tags": "utm_source=facebook",
            "object_story_spec": {"page_id": "P", "instagram_user_id": "IG", "link_data": {
                "link": OLD, "image_hash": "h", "image_url": "https://readonly.example",
                "call_to_action": {"type": "SIGN_UP", "value": {"link": OLD}}}}}}
        mock = _seq(ad, {"id": "new_cr"}, {"link_url": NEW}, {"success": True})
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", website_url=NEW, access_token="t"))

        assert result["success"] is True
        assert result["old_creative_id"] == "old_cr"
        assert result["new_creative_id"] == "new_cr"
        # create call = 2nd
        create = mock.call_args_list[1]
        assert create.args[0].endswith("/adcreatives")
        oss = json.loads(create.args[2]["object_story_spec"])
        assert oss["link_data"]["link"] == NEW
        assert oss["link_data"]["call_to_action"]["value"]["link"] == NEW
        assert "image_url" not in oss["link_data"]           # read-only stripped (#1443051)
        assert oss["link_data"]["image_hash"] == "h"          # kept
        assert create.args[2]["url_tags"] == "utm_source=facebook"  # preserved
        # swap call = 4th, onto the same ad
        swap = mock.call_args_list[3]
        assert swap.args[0] == "ad1"
        assert json.loads(swap.args[2]["creative"])["creative_id"] == "new_cr"

    async def test_asset_feed_url_change(self):
        ad = {"account_id": "123", "creative": {
            "id": "old_cr", "name": "cr", "url_tags": "utm_source=facebook",
            "object_story_spec": {"page_id": "P", "instagram_user_id": "IG"},
            "asset_feed_spec": {
                "link_urls": [{"website_url": OLD, "display_url": OLD, "adlabels": [{"name": "default_url"}]}],
                "bodies": [{"text": "b"}], "optimization_type": "DEGREES_OF_FREEDOM"}}}
        mock = _seq(ad, {"id": "new_cr"}, {"link_url": NEW}, {"success": True})
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", website_url=NEW, access_token="t"))

        assert result["success"] is True
        afs = json.loads(mock.call_args_list[1].args[2]["asset_feed_spec"])
        assert afs["link_urls"][0]["website_url"] == NEW
        assert afs["link_urls"][0]["display_url"] == NEW
        assert afs["bodies"] == [{"text": "b"}]               # variants preserved

    async def test_video_data_url_change(self):
        ad = {"account_id": "123", "creative": {
            "id": "old_cr", "name": "cr", "url_tags": "u",
            "object_story_spec": {"page_id": "P", "instagram_user_id": "IG", "video_data": {
                "video_id": "V", "image_url": "https://readonly.example", "image_hash": "h",
                "call_to_action": {"type": "SIGN_UP", "value": {"link_caption": "cap", "link": OLD}}}},
            "asset_feed_spec": {"bodies": [{"text": "b"}], "optimization_type": "DEGREES_OF_FREEDOM"}}}
        mock = _seq(ad, {"id": "new_cr"}, {"call_to_action": {"value": {"link": NEW}}}, {"success": True})
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", website_url=NEW, access_token="t"))

        assert result["success"] is True
        oss = json.loads(mock.call_args_list[1].args[2]["object_story_spec"])
        vd = oss["video_data"]
        assert vd["call_to_action"]["value"]["link"] == NEW
        assert vd["call_to_action"]["value"]["link_caption"] == "cap"  # caption preserved
        assert "image_url" not in vd                                   # stripped

    async def test_partnership_url_change(self):
        ad = {"account_id": "123", "creative": {
            "id": "old_cr", "name": "cr", "url_tags": "u",
            "source_instagram_media_id": "MEDIA",
            "instagram_branded_content": {"sponsor_id": "S"},
            "facebook_branded_content": {"sponsor_page_id": "PG"},
            "call_to_action": {"type": "SIGN_UP", "value": {"link_caption": "cap", "link": OLD}}}}
        mock = _seq(ad, {"id": "new_cr"}, {"call_to_action": {"value": {"link": NEW}}}, {"success": True})
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", website_url=NEW, access_token="t"))

        assert result["success"] is True
        params = mock.call_args_list[1].args[2]
        assert params["source_instagram_media_id"] == "MEDIA"
        assert json.loads(params["call_to_action"])["value"]["link"] == NEW
        assert json.loads(params["instagram_branded_content"])["sponsor_id"] == "S"
        assert json.loads(params["facebook_branded_content"])["sponsor_page_id"] == "PG"

    async def test_dry_run_does_not_swap(self):
        ad = {"account_id": "123", "creative": {
            "id": "old_cr", "name": "cr",
            "object_story_spec": {"link_data": {"link": OLD}}}}
        mock = _seq(ad, {"id": "new_cr"}, {"link_url": NEW})  # no swap response
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", website_url=NEW, dry_run=True, access_token="t"))

        assert result["success"] is True and result["dry_run"] is True
        assert result["new_creative_id"] == "new_cr"
        assert mock.call_count == 3  # read, create, verify — never swap

    async def test_no_params_is_error(self):
        mock = _seq()
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", access_token="t"))
        assert "error" in result
        assert mock.call_count == 0

    async def test_verify_mismatch_aborts_swap(self):
        ad = {"account_id": "123", "creative": {
            "id": "old_cr", "name": "cr", "object_story_spec": {"link_data": {"link": OLD}}}}
        # verify returns a DIFFERENT url -> must not swap
        mock = _seq(ad, {"id": "new_cr"}, {"link_url": "https://example.com/wrong"})
        with patch("meta_ads_mcp.core.ads.make_api_request", mock):
            result = _parse(await update_ad_url("ad1", website_url=NEW, access_token="t"))
        assert "error" in result
        assert result["observed_url"] == "https://example.com/wrong"
        assert mock.call_count == 3  # never swapped
