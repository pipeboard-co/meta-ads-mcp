"""Regression tests for GHSA-prmg-4fr3-mm6x.

The token cache holds a long-lived Meta access token (~60 days). It was written
with a bare `open(path, "w")` into a directory created by `mkdir()` with no
mode, so under the usual 0022 umask it landed at 0644 inside 0755 — readable by
every other local user on a shared host.
"""

import json
import os
import platform
import stat
import time

import pytest

from meta_ads_mcp.core.auth import (
    TOKEN_CACHE_DIR_MODE,
    TOKEN_CACHE_FILE_MODE,
    AuthManager,
    TokenInfo,
    _restrict_permissions,
)

pytestmark = pytest.mark.skipif(
    platform.system() == "Windows",
    reason="POSIX permission bits do not apply on Windows",
)


def _mode(path) -> int:
    return stat.S_IMODE(os.stat(path).st_mode)


@pytest.fixture
def home(tmp_path, monkeypatch):
    """Point the platform cache lookup at a scratch HOME."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    (tmp_path / "Library" / "Application Support").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".config").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def manager(home):
    auth_manager = AuthManager(app_id="test-app-id")
    auth_manager.token_info = TokenInfo(
        access_token="EAAG" + "x" * 60,
        expires_in=60 * 24 * 3600,
        user_id="123",
    )
    return auth_manager


def test_token_cache_file_is_owner_only(manager):
    manager._save_token_to_cache()
    cache_path = manager._get_token_cache_path()

    assert _mode(cache_path) == TOKEN_CACHE_FILE_MODE
    assert not _mode(cache_path) & 0o077, "group/other can read the Meta token"


def test_token_cache_directory_is_owner_only(manager):
    cache_dir = manager._get_token_cache_path().parent

    assert _mode(cache_dir) == TOKEN_CACHE_DIR_MODE
    assert not _mode(cache_dir) & 0o077


def test_permissions_hold_under_a_permissive_umask(manager):
    """0644 came from the umask, so the umask is what the fix must survive."""
    previous = os.umask(0o000)
    try:
        manager._save_token_to_cache()
    finally:
        os.umask(previous)

    assert _mode(manager._get_token_cache_path()) == TOKEN_CACHE_FILE_MODE


def test_existing_world_readable_cache_is_narrowed_on_save(manager):
    cache_path = manager._get_token_cache_path()
    cache_path.write_text("{}")
    os.chmod(cache_path, 0o644)

    manager._save_token_to_cache()

    assert _mode(cache_path) == TOKEN_CACHE_FILE_MODE


def test_existing_world_readable_cache_is_narrowed_on_load(manager, home):
    """A cache written by an older version is repaired without re-authenticating."""
    cache_path = manager._get_token_cache_path()
    cache_path.write_text(
        json.dumps(
            {
                "access_token": "EAAG" + "y" * 60,
                "expires_in": 60 * 24 * 3600,
                "created_at": int(time.time()),
                "user_id": "123",
            }
        )
    )
    os.chmod(cache_path, 0o644)

    assert AuthManager(app_id="test-app-id")._load_cached_token() is True
    assert _mode(cache_path) == TOKEN_CACHE_FILE_MODE


def test_saved_token_is_still_readable_by_its_owner(manager):
    manager._save_token_to_cache()

    data = json.loads(manager._get_token_cache_path().read_text())

    assert data["access_token"] == manager.token_info.access_token


def test_restrict_permissions_survives_a_missing_file(tmp_path):
    """Best effort: a vanished path must not raise into the caller."""
    _restrict_permissions(tmp_path / "gone.json", TOKEN_CACHE_FILE_MODE)
