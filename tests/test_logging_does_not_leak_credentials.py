"""Regression tests for GHSA-r3r9-3mrh-x966.

The report describes a credential written into the log file in full, via a URL
query string, with DEBUG logging on by default. The specific code it cites
(`pipeboard_auth.py`) was removed in 1.0.121, but the same leak was live through
a different route: `logging.basicConfig(level=DEBUG, filename=...)` installed a
handler on the *root* logger, so httpx's INFO record — "HTTP Request: GET
https://graph.facebook.com/...?access_token=<token>" — was captured in full.

These tests pin the three properties that close it: the package handler is not
on the root logger, httpx never emits that line, and nothing logs raw credential
material.
"""

import asyncio
import logging
import os
import platform
import stat

import httpx
import pytest

from meta_ads_mcp.core.utils import (
    DEFAULT_LOG_LEVEL,
    LOG_DIR_MODE,
    LOG_FILE_MODE,
    redact_secret,
    setup_logging,
)

TOKEN = "EAAGabcdefghijklmnopqrstuvwxyz0123456789"


@pytest.fixture
def log_home(tmp_path, monkeypatch):
    """Point the platform log path at a scratch HOME."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    (tmp_path / "Library" / "Application Support").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".config").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def configured_logger(log_home):
    logger = setup_logging()
    try:
        yield logger
    finally:
        for handler in [h for h in logger.handlers if getattr(h, "_meta_ads_mcp_handler", False)]:
            handler.close()
            logger.removeHandler(handler)


def _log_file(log_home):
    matches = list(log_home.rglob("meta_ads_debug.log"))
    assert matches, "no log file was created"
    return matches[0]


def test_handler_is_not_installed_on_the_root_logger(configured_logger):
    """basicConfig() put it on root, which is how third-party records got in."""
    root_handlers = logging.getLogger().handlers

    assert not any(getattr(h, "_meta_ads_mcp_handler", False) for h in root_handlers)
    assert any(getattr(h, "_meta_ads_mcp_handler", False) for h in configured_logger.handlers)
    assert configured_logger.propagate is False


def test_httpx_request_url_never_reaches_the_log_file(configured_logger, log_home):
    """The advisory's leak, reproduced through the route that was live."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    async def call():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await client.get(
                "https://graph.facebook.com/v24.0/me/adaccounts",
                params={"access_token": TOKEN, "fields": "id"},
            )

    asyncio.run(call())

    assert TOKEN not in _log_file(log_home).read_text()


def test_httpx_logger_is_held_at_warning(configured_logger):
    """Its INFO line prints the full URL, so it must not fire at all —
    including into logging the host application configures."""
    for library in ("httpx", "httpcore"):
        assert logging.getLogger(library).level >= logging.WARNING


def test_default_level_is_not_debug(configured_logger):
    assert DEFAULT_LOG_LEVEL == "INFO"
    assert configured_logger.level == logging.INFO


def test_level_is_configurable(log_home, monkeypatch):
    monkeypatch.setenv("META_ADS_LOG_LEVEL", "DEBUG")

    assert setup_logging().level == logging.DEBUG


def test_unknown_level_falls_back_to_info(log_home, monkeypatch):
    monkeypatch.setenv("META_ADS_LOG_LEVEL", "LOUD")

    assert setup_logging().level == logging.INFO


def test_repeated_setup_does_not_stack_handlers(log_home):
    first = setup_logging()
    count = len([h for h in first.handlers if getattr(h, "_meta_ads_mcp_handler", False)])

    setup_logging()
    setup_logging()

    assert len([h for h in first.handlers if getattr(h, "_meta_ads_mcp_handler", False)]) == count


@pytest.mark.skipif(platform.system() == "Windows", reason="POSIX permission bits")
def test_log_file_and_directory_are_owner_only(configured_logger, log_home):
    log_file = _log_file(log_home)

    assert stat.S_IMODE(os.stat(log_file).st_mode) == LOG_FILE_MODE
    assert stat.S_IMODE(os.stat(log_file.parent).st_mode) == LOG_DIR_MODE


@pytest.mark.parametrize(
    "secret",
    [TOKEN, "short", "a" * 200],
)
def test_redact_secret_discloses_nothing(secret):
    rendered = redact_secret(secret)

    assert secret not in rendered
    assert secret[:5] not in rendered
    assert str(len(secret)) in rendered


def test_redact_secret_handles_absent_values():
    assert redact_secret(None) == "<none>"
    assert redact_secret("") == "<none>"


def test_no_module_logs_a_credential_prefix():
    """`token[:10]` slices were the in-house version of the same mistake."""
    import pathlib

    package = pathlib.Path(__file__).resolve().parent.parent / "meta_ads_mcp"
    offenders = []
    for path in package.rglob("*.py"):
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            if "logger." not in line and "token_info" not in line:
                continue
            if "[:5]" in line or "[:10]" in line or "[:20]" in line:
                offenders.append(f"{path.name}:{number}")

    assert not offenders, f"credential prefixes in log lines: {offenders}"
