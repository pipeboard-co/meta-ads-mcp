import hashlib
import pytest
import json
from unittest.mock import AsyncMock, patch

from meta_ads_mcp.core.audiences import (
    get_custom_audiences,
    create_custom_audience,
    create_lookalike_audience,
    add_users_to_custom_audience,
    _normalize_and_hash_email,
)


class TestGetCustomAudiences:
    """Test cases for get_custom_audiences function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful retrieval of custom audiences."""
        mock_response = {
            "data": [
                {
                    "id": "123",
                    "name": "Test Audience",
                    "subtype": "ENGAGEMENT",
                    "approximate_count_lower_bound": 950,
                    "approximate_count_upper_bound": 1050,
                }
            ]
        }

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await get_custom_audiences(
                account_id="act_123456789", access_token="test_token"
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {"fields": "id,name,subtype,approximate_count_lower_bound,approximate_count_upper_bound,data_source,delivery_status"},
            )

            result_data = json.loads(result)
            assert result_data["data"][0]["name"] == "Test Audience"

    @pytest.mark.asyncio
    async def test_no_account_id(self):
        """Test that an empty account_id returns an error."""
        result = await get_custom_audiences(account_id="", access_token="test_token")

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_act_prefix_normalization(self):
        """Test that account_id without act_ prefix is normalized."""
        mock_response = {"data": []}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            await get_custom_audiences(
                account_id="123456789", access_token="test_token"
            )

            mock_api.assert_called_once_with(
                "act_123456789/customaudiences",
                "test_token",
                {"fields": "id,name,subtype,approximate_count_lower_bound,approximate_count_upper_bound,data_source,delivery_status"},
            )


class TestCreateCustomAudience:
    """Test cases for create_custom_audience function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful creation of a custom audience."""
        mock_response = {"id": "audience_123"}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await create_custom_audience(
                account_id="act_123",
                name="My Audience",
                subtype="ENGAGEMENT",
                access_token="test_token",
            )

            # Verify a POST call was made to the correct endpoint
            call_args = mock_api.call_args
            assert call_args[0][0] == "act_123/customaudiences"
            assert call_args[1].get("method") == "POST" or (
                len(call_args[0]) > 3 and call_args[0][3] == "POST"
            )

            result_data = json.loads(result)
            assert result_data["id"] == "audience_123"

    @pytest.mark.asyncio
    async def test_with_rule_dict(self):
        """Test that a rule dict is passed through to make_api_request."""
        mock_response = {"id": "audience_456"}
        rule = {"inclusions": {"operator": "or", "rules": []}}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            await create_custom_audience(
                account_id="act_123",
                name="My Audience",
                subtype="ENGAGEMENT",
                access_token="test_token",
                rule=rule,
            )

            call_args = mock_api.call_args
            # params is the third positional arg
            params = call_args[0][2]
            assert params["rule"] == rule

    @pytest.mark.asyncio
    async def test_missing_name(self):
        """Test that an empty name returns an error."""
        result = await create_custom_audience(
            account_id="act_123",
            name="",
            subtype="ENGAGEMENT",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_invalid_subtype(self):
        """Test that an invalid subtype returns an error."""
        result = await create_custom_audience(
            account_id="act_123",
            name="My Audience",
            subtype="INVALID_TYPE",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "INVALID_TYPE" in nested["error"]

    @pytest.mark.asyncio
    async def test_ig_business_subtype_rejected(self):
        """Test that IG_BUSINESS subtype is rejected (removed in v25.0)."""
        result = await create_custom_audience(
            account_id="act_123",
            name="My IG Audience",
            subtype="IG_BUSINESS",
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "IG_BUSINESS" in nested["error"] and "v25.0" in nested["error"]


class TestCreateLookalikeAudience:
    """Test cases for create_lookalike_audience function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful creation of a lookalike audience."""
        mock_response = {"id": "lookalike_456"}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await create_lookalike_audience(
                account_id="act_123",
                name="Lookalike",
                origin_audience_id="audience_123",
                country="GR",
                access_token="test_token",
            )

            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["lookalike_spec"]["country"] == "GR"
            assert params["lookalike_spec"]["ratio"] == 0.01

            result_data = json.loads(result)
            assert result_data["id"] == "lookalike_456"

    @pytest.mark.asyncio
    async def test_default_ratio(self):
        """Test that the default ratio is 0.01."""
        mock_response = {"id": "lookalike_789"}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            await create_lookalike_audience(
                account_id="act_123",
                name="Lookalike",
                origin_audience_id="audience_123",
                country="GR",
                access_token="test_token",
            )

            call_args = mock_api.call_args
            params = call_args[0][2]
            assert params["lookalike_spec"]["ratio"] == 0.01

    @pytest.mark.asyncio
    async def test_invalid_ratio_too_high(self):
        """Test that a ratio above 0.20 returns an error."""
        result = await create_lookalike_audience(
            account_id="act_123",
            name="Lookalike",
            origin_audience_id="audience_123",
            country="GR",
            access_token="test_token",
            ratio=0.5,
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested


class TestNormalizeAndHashEmail:
    """Unit tests for the _normalize_and_hash_email helper."""

    def test_lowercase(self):
        """Uppercase email is lowercased before hashing."""
        assert _normalize_and_hash_email("User@Example.COM") == _normalize_and_hash_email("user@example.com")

    def test_strips_surrounding_whitespace(self):
        """Leading/trailing whitespace is stripped."""
        assert _normalize_and_hash_email("  user@example.com  ") == _normalize_and_hash_email("user@example.com")

    def test_strips_internal_spaces(self):
        """Spaces around @ are removed (e.g. 'info @ yiart.gr' → 'info@yiart.gr')."""
        assert _normalize_and_hash_email("info @ yiart.gr") == _normalize_and_hash_email("info@yiart.gr")

    def test_strips_tabs(self):
        """Trailing tabs are stripped."""
        assert _normalize_and_hash_email("user@example.com\t\t") == _normalize_and_hash_email("user@example.com")

    def test_returns_sha256_hex(self):
        """Returns a 64-character hex string."""
        result = _normalize_and_hash_email("user@example.com")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestAddUsersToCustomAudience:
    """Test cases for add_users_to_custom_audience function."""

    @pytest.mark.asyncio
    async def test_success(self):
        """Test successful upload of email list."""
        mock_response = {"num_received": 2, "num_invalid_skipped": 0, "invalid_entry_samples": []}

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = mock_response

            result = await add_users_to_custom_audience(
                audience_id="6933647088203",
                emails=["user@example.com", "other@example.com"],
                access_token="test_token",
            )

            call_args = mock_api.call_args
            assert call_args[0][0] == "6933647088203/users"
            assert call_args[1].get("method") == "POST" or (
                len(call_args[0]) > 3 and call_args[0][3] == "POST"
            )

            params = call_args[0][2]
            assert params["payload"]["schema"] == ["EMAIL_SHA256"]
            assert len(params["payload"]["data"]) == 2

            result_data = json.loads(result)
            assert result_data["num_received"] == 2

    @pytest.mark.asyncio
    async def test_emails_are_hashed(self):
        """Emails are normalized and SHA-256 hashed before upload."""
        expected_hash = hashlib.sha256("user@example.com".encode()).hexdigest()

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {"num_received": 1}

            await add_users_to_custom_audience(
                audience_id="123",
                emails=["User@Example.COM"],
                access_token="test_token",
            )

            params = mock_api.call_args[0][2]
            assert params["payload"]["data"][0][0] == expected_hash

    @pytest.mark.asyncio
    async def test_already_hashed_skips_hashing(self):
        """Pre-hashed emails are passed through unchanged."""
        pre_hashed = "a" * 64

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {"num_received": 1}

            await add_users_to_custom_audience(
                audience_id="123",
                emails=[pre_hashed],
                access_token="test_token",
                already_hashed=True,
            )

            params = mock_api.call_args[0][2]
            assert params["payload"]["data"][0][0] == pre_hashed

    @pytest.mark.asyncio
    async def test_missing_audience_id(self):
        """Empty audience_id returns an error without calling the API."""
        result = await add_users_to_custom_audience(
            audience_id="",
            emails=["user@example.com"],
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_empty_emails_list(self):
        """Empty emails list returns an error without calling the API."""
        result = await add_users_to_custom_audience(
            audience_id="123",
            emails=[],
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested

    @pytest.mark.asyncio
    async def test_non_string_emails_rejected(self):
        """Non-string entries in the emails list return an error."""
        result = await add_users_to_custom_audience(
            audience_id="123",
            emails=["valid@example.com", None, 42],
            access_token="test_token",
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "strings" in nested["error"]

    @pytest.mark.asyncio
    async def test_already_hashed_invalid_format_rejected(self):
        """already_hashed=True rejects hashes that are not 64-char lowercase hex."""
        result = await add_users_to_custom_audience(
            audience_id="123",
            emails=["a" * 40],  # SHA-1 length, not SHA-256
            access_token="test_token",
            already_hashed=True,
        )

        result_data = json.loads(result)
        assert "data" in result_data
        nested = json.loads(result_data["data"])
        assert "error" in nested
        assert "64" in nested["error"]

    @pytest.mark.asyncio
    async def test_dirty_emails_normalized(self):
        """Emails with spaces/tabs/mixed case are normalized before hashing."""
        expected = hashlib.sha256("info@yiart.gr".encode()).hexdigest()

        with patch(
            "meta_ads_mcp.core.audiences.make_api_request", new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = {"num_received": 1}

            await add_users_to_custom_audience(
                audience_id="123",
                emails=["info @ yiart.gr"],
                access_token="test_token",
            )

            params = mock_api.call_args[0][2]
            assert params["payload"]["data"][0][0] == expected
