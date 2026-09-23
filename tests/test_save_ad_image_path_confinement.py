"""Regression tests for GHSA-2h5x-4qc8-3x27.

`save_ad_image_locally` built its destination from two caller-supplied tool
arguments with no validation: `os.path.join(output_dir, f"{ad_id}_{hash}.jpg")`.
join() returns an absolute second argument unchanged and does not neutralize
"..", and `os.makedirs(output_dir)` would build whatever tree was needed, so a
caller could drop the downloaded image anywhere the process could write.

`resolve_ad_image_save_path` now decides the path, and it is called before
anything touches the disk.
"""

import os

import pytest

from meta_ads_mcp.core.ads import UnsafeSavePathError, resolve_ad_image_save_path

AD_ID = "120250589548040262"
IMAGE_HASH = "60dff700e54f59a38ec6e626c7b2f3f5"


@pytest.fixture
def base_dir(tmp_path, monkeypatch):
    """Point the allowed base at a scratch directory."""
    base = tmp_path / "workdir"
    base.mkdir()
    monkeypatch.setenv("META_ADS_IMAGE_OUTPUT_DIR", str(base))
    return base


def test_default_output_dir_lands_under_the_base(base_dir):
    path = resolve_ad_image_save_path(AD_ID, IMAGE_HASH, "ad_images")

    assert path == str(base_dir / "ad_images" / f"{AD_ID}_{IMAGE_HASH}.jpg")


def test_nested_subdirectories_are_allowed(base_dir):
    path = resolve_ad_image_save_path(AD_ID, IMAGE_HASH, "creatives/2026/q3")

    assert path.startswith(str(base_dir) + os.sep)


def test_empty_output_dir_writes_into_the_base(base_dir):
    path = resolve_ad_image_save_path(AD_ID, IMAGE_HASH, "")

    assert path == str(base_dir / f"{AD_ID}_{IMAGE_HASH}.jpg")


@pytest.mark.parametrize(
    "output_dir",
    [
        "/etc/cron.d",              # absolute path discards the base in join()
        "/tmp",
        "../escaped",               # traversal
        "../../../../tmp/evil",
        "ad_images/../../outside",  # traversal after a legitimate-looking prefix
    ],
)
def test_output_dir_escapes_are_rejected(base_dir, output_dir):
    with pytest.raises(UnsafeSavePathError):
        resolve_ad_image_save_path(AD_ID, IMAGE_HASH, output_dir)


@pytest.mark.parametrize(
    "ad_id",
    [
        "/tmp/PWNED",               # absolute id discards the directory
        "../../../../tmp/evil",     # traversal through the filename
        "123/../../etc/passwd",
        "not-an-id",
        "",
        "12 3",
    ],
)
def test_non_numeric_ad_ids_are_rejected(base_dir, ad_id):
    with pytest.raises(UnsafeSavePathError):
        resolve_ad_image_save_path(ad_id, IMAGE_HASH, "ad_images")


@pytest.mark.parametrize("image_hash", ["../../evil", "a/b", "", "hash with spaces"])
def test_unsafe_image_hashes_are_rejected(base_dir, image_hash):
    with pytest.raises(UnsafeSavePathError):
        resolve_ad_image_save_path(AD_ID, image_hash, "ad_images")


def test_symlink_out_of_the_base_is_rejected(base_dir, tmp_path):
    """realpath resolution is what catches this, not string matching."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (base_dir / "escape").symlink_to(outside)

    with pytest.raises(UnsafeSavePathError):
        resolve_ad_image_save_path(AD_ID, IMAGE_HASH, "escape")


def test_rejection_creates_nothing_on_disk(base_dir):
    """The path is resolved before any makedirs, so a rejected call is inert."""
    before = sorted(os.listdir(base_dir))

    with pytest.raises(UnsafeSavePathError):
        resolve_ad_image_save_path(AD_ID, IMAGE_HASH, "../../../../tmp/evil-tree")

    assert sorted(os.listdir(base_dir)) == before
    assert not os.path.exists("/tmp/evil-tree")


def test_base_defaults_to_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("META_ADS_IMAGE_OUTPUT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    path = resolve_ad_image_save_path(AD_ID, IMAGE_HASH, "ad_images")

    assert path == os.path.join(os.path.realpath(tmp_path), "ad_images", f"{AD_ID}_{IMAGE_HASH}.jpg")
