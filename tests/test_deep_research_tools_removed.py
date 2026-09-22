"""Regression tests for the removal of the OpenAI Deep Research `search`/`fetch` tools.

The `openai_deep_research` module cached Meta Ads records in a module-level
singleton keyed only by `"<type>:<id>"`. Under `--transport streamable-http`
one process serves every caller, so `fetch` — which read that cache with no
credential resolution and no ownership check — returned one caller's cached
ad-account, campaign, ad, page and business records to any other caller
(GHSA-j7p8-g5m6-3wv5).

The module is gone rather than scoped: in production 100% of `fetch` calls
already failed (70% "Record not found", the rest schema-validation errors from
clients treating it as a generic Graph fetch), so the tool had no working use
to preserve. These tests fail if it comes back.
"""

import importlib

import pytest


def test_openai_deep_research_module_is_gone():
    """The module that held the process-global record cache must not exist."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("meta_ads_mcp.core.openai_deep_research")


def test_core_package_exports_no_search_or_fetch():
    import meta_ads_mcp.core as core

    assert not hasattr(core, "fetch"), "fetch was re-exported from meta_ads_mcp.core"
    assert not hasattr(core, "search"), "search was re-exported from meta_ads_mcp.core"
    assert "fetch" not in core.__all__
    assert "search" not in core.__all__


@pytest.mark.asyncio
async def test_search_and_fetch_are_not_registered_tools():
    from meta_ads_mcp.core.server import mcp_server

    tool_names = {tool.name for tool in await mcp_server.list_tools()}

    assert "fetch" not in tool_names, "the cross-caller-readable fetch tool is registered again"
    assert "search" not in tool_names, "the deep-research search tool is registered again"


@pytest.mark.asyncio
async def test_unrelated_tools_survived_the_removal():
    """Removing the module must not take neighbouring tools with it."""
    from meta_ads_mcp.core.server import mcp_server

    tool_names = {tool.name for tool in await mcp_server.list_tools()}

    for expected in ("get_ad_accounts", "get_campaigns", "get_insights", "search_interests"):
        assert expected in tool_names, f"{expected} disappeared along with the deep-research tools"
