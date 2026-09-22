"""Regression tests for the removal of the MCP image-resource interface.

`utils.ad_creative_images` was a process-global dict of ad creative images, and
`resources.list_resources` / `resources.get_resource` were registered as MCP
resources that enumerated and returned its entries with no caller scoping and
no use of the request credential (GHSA-25fp-988j-w29f).

Nothing had written to that dict since 0.4.0 — `create_resource_from_image()`
kept the only write and had no call sites — so the interface served an
always-empty cache. It is removed rather than scoped: there is no working
behaviour to keep, and leaving an unscoped global around invites the write path
to come back with it. These tests fail if any piece returns.
"""

import importlib

import pytest


def test_resources_module_is_gone():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("meta_ads_mcp.core.resources")


def test_utils_exposes_no_global_image_cache():
    from meta_ads_mcp.core import utils

    assert not hasattr(utils, "ad_creative_images"), "the process-global image cache is back"
    assert not hasattr(utils, "create_resource_from_image"), "the unscoped cache writer is back"


@pytest.mark.asyncio
async def test_no_image_resources_are_registered():
    from meta_ads_mcp.core.server import mcp_server

    uris = {str(resource.uri) for resource in await mcp_server.list_resources()}
    templates = {str(t.uriTemplate) for t in await mcp_server.list_resource_templates()}

    assert not any(uri.startswith("meta-ads://") for uri in uris), uris
    assert not any(t.startswith("meta-ads://") for t in templates), templates


@pytest.mark.asyncio
async def test_reading_a_removed_image_resource_fails():
    """The handler that returned any caller's bytes must no longer resolve."""
    from meta_ads_mcp.core.server import mcp_server

    with pytest.raises(Exception):
        await mcp_server.read_resource("meta-ads://images/deadbeef")


@pytest.mark.asyncio
async def test_image_tools_survived_the_removal():
    from meta_ads_mcp.core.server import mcp_server

    tool_names = {tool.name for tool in await mcp_server.list_tools()}

    for expected in ("get_ad_image", "get_ad_creatives"):
        assert expected in tool_names, f"{expected} disappeared with the resource interface"
