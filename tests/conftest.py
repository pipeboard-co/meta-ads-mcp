"""
Pytest configuration for Meta Ads MCP tests

This file provides common fixtures and configuration for all tests.
"""

import pytest
import requests
import time
import os


@pytest.fixture(scope="session")
def server_url():
    """Default server URL for tests"""
    return os.environ.get("MCP_TEST_SERVER_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def check_server_running(server_url):
    """
    Check if the MCP server is running before running tests.
    
    This fixture will skip tests if the server is not available.
    """
    try:
        response = requests.get(f"{server_url}/", timeout=5)
        # We expect 404 for root path, but it means server is running
        if response.status_code not in [200, 404]:
            pytest.skip(f"MCP server not responding correctly at {server_url}")
        return True
    except requests.exceptions.RequestException:
        pytest.skip(
            f"MCP server not running at {server_url}. "
            f"Start with: python -m meta_ads_mcp --transport streamable-http"
        )


@pytest.fixture
def test_headers():
    """Common test headers for HTTP requests"""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "MCP-Test-Client/1.0"
    }


@pytest.fixture
def bearer_auth_headers(test_headers):
    """Headers with a Meta access token in the Authorization header"""
    headers = test_headers.copy()
    headers["Authorization"] = "Bearer test_meta_access_token_12345"
    return headers


@pytest.fixture
def meta_app_auth_headers(test_headers):
    """Headers with Meta app ID authentication"""
    headers = test_headers.copy()
    headers["X-META-APP-ID"] = "123456789012345"
    return headers 