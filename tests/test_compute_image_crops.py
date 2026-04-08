"""
Tests for the compute_image_crops tool.

This tool is pure computation (no API calls) and should return correct
centered crop boxes for any source image dimensions.
"""
import json
import math
import pytest
from meta_ads_mcp.core.ads import compute_image_crops, _compute_crop_box


# ---------------------------------------------------------------------------
# _compute_crop_box — unit tests for the math
# ---------------------------------------------------------------------------

class TestComputeCropBox:
    """Verify the crop box geometry for various source/target ratio combos."""

    def _check_ratio(self, box, kw, kh, tolerance=0.02):
        """Assert the box has the right aspect ratio within tolerance."""
        x1, y1 = box[0]
        x2, y2 = box[1]
        width = x2 - x1
        height = y2 - y1
        actual = width / height
        expected = kw / kh
        assert abs(actual - expected) <= tolerance, (
            f"Ratio {actual:.4f} != expected {expected:.4f} for {kw}x{kh} on box {box}"
        )

    def _check_centered(self, box, src_w, src_h):
        """Assert the box is centered in the source image."""
        x1, y1 = box[0]
        x2, y2 = box[1]
        width = x2 - x1
        height = y2 - y1
        # Check symmetry: offsets on each side should differ by at most 1 pixel.
        left_pad = x1
        right_pad = src_w - x2
        top_pad = y1
        bottom_pad = src_h - y2
        assert abs(left_pad - right_pad) <= 1, f"Not horizontally centered: {box}"
        assert abs(top_pad - bottom_pad) <= 1, f"Not vertically centered: {box}"

    def _check_fits(self, box, src_w, src_h):
        """Assert the box fits within the source image."""
        x1, y1 = box[0]
        x2, y2 = box[1]
        assert x1 >= 0 and y1 >= 0, f"Box starts outside image: {box}"
        assert x2 <= src_w and y2 <= src_h, f"Box ends outside image: {box}"

    def test_square_source_100x100_key(self):
        """1080x1080 source + 100x100 key → full image."""
        box = _compute_crop_box(1080, 1080, 100, 100)
        assert box == [[0, 0], [1080, 1080]]

    def test_square_source_400x500_key(self):
        """1080x1080 source + 400x500 (4:5 portrait) → width cropped, full height."""
        box = _compute_crop_box(1080, 1080, 400, 500)
        x1, y1 = box[0]
        x2, y2 = box[1]
        assert y1 == 0 and y2 == 1080, "Should use full height"
        assert x1 > 0, "Should crop width"
        self._check_ratio(box, 400, 500)
        self._check_centered(box, 1080, 1080)
        self._check_fits(box, 1080, 1080)

    def test_square_source_600x360_key(self):
        """1080x1080 source + 600x360 (~1.67:1 landscape) → height cropped, full width."""
        box = _compute_crop_box(1080, 1080, 600, 360)
        x1, y1 = box[0]
        x2, y2 = box[1]
        assert x1 == 0 and x2 == 1080, "Should use full width"
        assert y1 > 0, "Should crop height"
        self._check_ratio(box, 600, 360)
        self._check_centered(box, 1080, 1080)
        self._check_fits(box, 1080, 1080)

    def test_wide_source_400x500_key(self):
        """Wide source (1920x1080) + 4:5 portrait key."""
        box = _compute_crop_box(1920, 1080, 400, 500)
        self._check_ratio(box, 400, 500)
        self._check_centered(box, 1920, 1080)
        self._check_fits(box, 1920, 1080)
        # Height should be capped at 1080
        assert box[1][1] == 1080

    def test_tall_source_600x360_key(self):
        """Tall source (1080x1920) + 600x360 landscape key."""
        box = _compute_crop_box(1080, 1920, 600, 360)
        self._check_ratio(box, 600, 360)
        self._check_centered(box, 1080, 1920)
        self._check_fits(box, 1080, 1920)
        # Width should be capped at 1080
        assert box[1][0] == 1080

    def test_all_valid_keys_on_square_source(self):
        """All 6 valid keys should produce valid boxes for a 1080x1080 source."""
        from meta_ads_mcp.core.ads import _VALID_CROP_KEYS
        for key, kw, kh in _VALID_CROP_KEYS:
            box = _compute_crop_box(1080, 1080, kw, kh)
            self._check_ratio(box, kw, kh)
            self._check_centered(box, 1080, 1080)
            self._check_fits(box, 1080, 1080)

    def test_non_square_source_100x100_key(self):
        """1200x628 (landscape) + 100x100 → height-limited square."""
        box = _compute_crop_box(1200, 628, 100, 100)
        x1, y1 = box[0]
        x2, y2 = box[1]
        assert y2 - y1 == 628, "Should use full height for square crop on landscape"
        assert x2 - x1 == 628
        self._check_centered(box, 1200, 628)


# ---------------------------------------------------------------------------
# compute_image_crops — integration tests for the MCP tool
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_default_keys_1080x1080():
    """Default call returns all 6 keys for 1080x1080."""
    result_str = await compute_image_crops(image_width=1080, image_height=1080)
    result = json.loads(result_str)

    crops = result["image_crops"]
    assert set(crops.keys()) == {"100x100", "100x72", "400x500", "400x150", "600x360", "90x160"}

    # Spot-check the classic 1080x1080 values
    assert crops["100x100"] == [[0, 0], [1080, 1080]]
    # 400x500: width should be ~864, centered → x1=108
    x1, y1 = crops["400x500"][0]
    x2, y2 = crops["400x500"][1]
    assert y1 == 0 and y2 == 1080
    assert abs((x2 - x1) / (y2 - y1) - 400 / 500) < 0.02


@pytest.mark.asyncio
async def test_specific_keys():
    """Can request a subset of keys."""
    result_str = await compute_image_crops(
        image_width=1080, image_height=1080, crop_keys=["100x100", "600x360"]
    )
    result = json.loads(result_str)
    assert set(result["image_crops"].keys()) == {"100x100", "600x360"}


@pytest.mark.asyncio
async def test_invalid_key_produces_warning():
    """Requesting 191x100 (invalid) returns a warning and skips the key."""
    result_str = await compute_image_crops(
        image_width=1080, image_height=1080, crop_keys=["100x100", "191x100"]
    )
    result = json.loads(result_str)
    # 191x100 should be absent
    assert "191x100" not in result["image_crops"]
    # 100x100 should be present
    assert "100x100" in result["image_crops"]
    # Warning should mention 191x100
    assert "warnings" in result
    assert any("191x100" in w for w in result["warnings"])


@pytest.mark.asyncio
async def test_landscape_source_1200x628():
    """1200x628 (typical landscape) produces valid boxes."""
    result_str = await compute_image_crops(image_width=1200, image_height=628)
    result = json.loads(result_str)
    crops = result["image_crops"]

    # All boxes must fit within the source
    for key, box in crops.items():
        x1, y1 = box[0]
        x2, y2 = box[1]
        assert x1 >= 0 and y1 >= 0
        assert x2 <= 1200 and y2 <= 628, f"{key}: box {box} exceeds source"


@pytest.mark.asyncio
async def test_portrait_source_1080x1920():
    """1080x1920 (stories) produces valid boxes."""
    result_str = await compute_image_crops(image_width=1080, image_height=1920)
    result = json.loads(result_str)
    crops = result["image_crops"]

    for key, box in crops.items():
        x1, y1 = box[0]
        x2, y2 = box[1]
        assert x1 >= 0 and y1 >= 0
        assert x2 <= 1080 and y2 <= 1920, f"{key}: box {box} exceeds source"


@pytest.mark.asyncio
async def test_invalid_dimensions():
    """Negative or zero dimensions return an error."""
    result_str = await compute_image_crops(image_width=0, image_height=1080)
    result = json.loads(result_str)
    assert "error" in result

    result_str = await compute_image_crops(image_width=1080, image_height=-5)
    result = json.loads(result_str)
    assert "error" in result


@pytest.mark.asyncio
async def test_result_includes_usage_hint():
    """Result always includes a usage hint."""
    result_str = await compute_image_crops(image_width=1080, image_height=1080)
    result = json.loads(result_str)
    assert "usage" in result
    assert "create_ad_creative" in result["usage"]


@pytest.mark.asyncio
async def test_source_dimensions_echoed():
    """Result echoes the source dimensions for confirmation."""
    result_str = await compute_image_crops(image_width=1200, image_height=628)
    result = json.loads(result_str)
    assert result["source_dimensions"] == {"width": 1200, "height": 628}
