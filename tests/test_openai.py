import os
import pytest

# Skip this test entirely if the optional 'openai' dependency is not installed
openai = pytest.importorskip("openai", reason="openai package not installed")


@pytest.mark.skipif(
    not os.getenv("PIPEBOARD_API_TOKEN"),
    reason="PIPEBOARD_API_TOKEN not set - skipping OpenAI integration test"
)
def test_openai_mcp_integration():
    """Test OpenAI integration with Meta Ads MCP via Pipeboard."""
    client = openai.OpenAI()

    resp = client.responses.create(
        model="gpt-4.1",
        tools=[{
            "type": "mcp",
            "server_label": "meta-ads",
            "server_url": "https://mcp.pipeboard.co/meta-ads-mcp",
            "headers": {
                "Authorization": f"Bearer {os.getenv('PIPEBOARD_API_TOKEN')}"
            },
            "require_approval": "never",
        }],
        input="What are my meta ad accounts? Do not pass access_token since auth is already done.",
    )

    assert resp.output_text is not None
    print(resp.output_text)
