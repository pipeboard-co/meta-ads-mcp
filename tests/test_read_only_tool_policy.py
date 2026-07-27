from mcp.server.fastmcp import FastMCP

from meta_ads_mcp.core.tool_policy import (
    apply_read_only_tool_policy,
    read_only_mode_enabled,
)


def _tool_names(server: FastMCP) -> set[str]:
    return {tool.name for tool in server._tool_manager.list_tools()}


def test_read_only_policy_keeps_reads_and_removes_writes_and_unknown_tools():
    server = FastMCP("test-meta-ads")

    @server.tool(name="get_campaigns")
    def get_campaigns():
        return []

    @server.tool(name="create_campaign")
    def create_campaign():
        return None

    @server.tool(name="future_unreviewed_tool")
    def future_unreviewed_tool():
        return None

    removed = apply_read_only_tool_policy(server, enabled=True)

    assert _tool_names(server) == {"get_campaigns"}
    assert removed == {"create_campaign", "future_unreviewed_tool"}


def test_read_only_mode_is_opt_in_and_accepts_standard_truthy_values(monkeypatch):
    monkeypatch.delenv("META_ADS_MCP_READ_ONLY", raising=False)
    assert read_only_mode_enabled() is False

    for value in ("1", "true", "TRUE", "yes", "on"):
        monkeypatch.setenv("META_ADS_MCP_READ_ONLY", value)
        assert read_only_mode_enabled() is True

    monkeypatch.setenv("META_ADS_MCP_READ_ONLY", "0")
    assert read_only_mode_enabled() is False


def test_main_applies_read_only_policy_before_stdio_server_starts(monkeypatch):
    from meta_ads_mcp.core import server as server_module

    observed_tool_names = set()
    original_tools = dict(server_module.mcp_server._tool_manager._tools)

    def capture_run(*, transport):
        assert transport == "stdio"
        observed_tool_names.update(_tool_names(server_module.mcp_server))

    monkeypatch.setenv("META_ADS_MCP_READ_ONLY", "1")
    monkeypatch.setattr(server_module.mcp_server, "run", capture_run)
    monkeypatch.setattr("sys.argv", ["meta-ads-mcp"])

    try:
        server_module.main()
    finally:
        server_module.mcp_server._tool_manager._tools = original_tools

    assert "get_campaigns" in observed_tool_names
    assert "create_campaign" not in observed_tool_names
