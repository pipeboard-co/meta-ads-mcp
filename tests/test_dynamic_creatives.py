"""Tests for dynamic creative features including multiple headlines and descriptions.

Tests for the enhanced create_ad_creative function that supports:
- Multiple headlines
- Multiple descriptions  
- Dynamic creative optimization settings
- Creative update functionality
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from meta_ads_mcp.core.ads import create_ad_creative, update_ad_creative


@pytest.mark.asyncio
class TestDynamicCreatives:
    """Test cases for dynamic creative features."""
    
    async def test_create_ad_creative_single_headline(self):
        """Test creating ad creative with single headline (simple case)."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Test Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                headline="Single Headline",
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with single headline in object_story_spec
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative creation
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            # Should use object_story_spec with link_data for simple creatives (not asset_feed_spec)
            assert "object_story_spec" in creative_data
            assert "link_data" in creative_data["object_story_spec"]
            assert creative_data["object_story_spec"]["link_data"]["name"] == "Single Headline"
            assert "asset_feed_spec" not in creative_data
    
    async def test_create_ad_creative_single_description(self):
        """Test creating ad creative with single description (simple case)."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Test Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                description="Single Description",
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with single description in object_story_spec
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative creation
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            # Should use object_story_spec with link_data for simple creatives (not asset_feed_spec)
            assert "object_story_spec" in creative_data
            assert "link_data" in creative_data["object_story_spec"]
            assert creative_data["object_story_spec"]["link_data"]["description"] == "Single Description"
            assert "asset_feed_spec" not in creative_data
    
    async def test_create_ad_creative_cannot_mix_headline_and_headlines(self):
        """Test that mixing headline and headlines parameters raises error."""
        
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test Creative",
            image_hash="abc123",
            page_id="987654321",
            link_url="https://example.com",
            message="Test message",
            headline="Single Headline",
            headlines=["Headline 1", "Headline 2"],
            call_to_action_type="LEARN_MORE"
        )
        
        result_data = json.loads(result)
        
        # Check if error is wrapped in "data" field (MCP error response format)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'headline' and 'headlines'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'headline' and 'headlines'" in result_data["error"]
    
    async def test_create_ad_creative_cannot_mix_description_and_descriptions(self):
        """Test that mixing description and descriptions parameters raises error."""
        
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test Creative",
            image_hash="abc123",
            page_id="987654321",
            link_url="https://example.com",
            message="Test message",
            description="Single Description",
            descriptions=["Description 1", "Description 2"],
            call_to_action_type="LEARN_MORE"
        )
        
        result_data = json.loads(result)
        
        # Check if error is wrapped in "data" field (MCP error response format)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'description' and 'descriptions'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'description' and 'descriptions'" in result_data["error"]

    
    async def test_create_ad_creative_multiple_headlines(self):
        """Test creating ad creative with multiple headlines."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Test Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                headlines=["Headline 1", "Headline 2", "Headline 3"],
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with multiple headlines
            # We need to check the first call (creative creation), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative creation
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            # Should use asset_feed_spec with titles array format (Meta API uses "titles" not "headlines")
            assert "asset_feed_spec" in creative_data
            assert "titles" in creative_data["asset_feed_spec"]
            assert creative_data["asset_feed_spec"]["titles"] == [
                {"text": "Headline 1"}, 
                {"text": "Headline 2"}, 
                {"text": "Headline 3"}
            ]
    
    async def test_create_ad_creative_multiple_descriptions(self):
        """Test creating ad creative with multiple descriptions."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Test Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                descriptions=["Description 1", "Description 2"],
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with multiple descriptions
            # We need to check the first call (creative creation), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative creation
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            # Should use asset_feed_spec with descriptions array format
            assert "asset_feed_spec" in creative_data
            assert "descriptions" in creative_data["asset_feed_spec"]
            assert creative_data["asset_feed_spec"]["descriptions"] == [
                {"text": "Description 1"}, 
                {"text": "Description 2"}
            ]
    
    async def test_create_ad_creative_dynamic_creative_spec(self):
        """Test creating ad creative with dynamic_creative_spec optimization settings."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Test Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                headlines=["Headline 1", "Headline 2"],
                descriptions=["Description 1", "Description 2"],
                dynamic_creative_spec={
                    "headline_optimization": True,
                    "description_optimization": True
                },
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with dynamic_creative_spec
            # We need to check the first call (creative creation), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative creation
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            # Should include dynamic_creative_spec
            assert "dynamic_creative_spec" in creative_data
            assert creative_data["dynamic_creative_spec"]["headline_optimization"] is True
            assert creative_data["dynamic_creative_spec"]["description_optimization"] is True
    
    async def test_create_ad_creative_multiple_headlines_and_descriptions(self):
        """Test creating ad creative with both multiple headlines and descriptions."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await create_ad_creative(
                access_token="test_token",
                account_id="act_123456789",
                name="Test Creative",
                image_hash="abc123",
                page_id="987654321",
                link_url="https://example.com",
                message="Test message",
                headlines=["Headline 1", "Headline 2", "Headline 3"],
                descriptions=["Description 1", "Description 2"],
                dynamic_creative_spec={
                    "headline_optimization": True,
                    "description_optimization": True
                },
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with both multiple headlines and descriptions
            # We need to check the first call (creative creation), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative creation
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "asset_feed_spec" in creative_data
            assert "titles" in creative_data["asset_feed_spec"]
            assert "descriptions" in creative_data["asset_feed_spec"]
            assert "dynamic_creative_spec" in creative_data
    
    async def test_create_ad_creative_validation_max_headlines(self):
        """Test validation for maximum number of headlines."""
        
        # Create list with more than 5 headlines (assuming 5 is the limit)
        too_many_headlines = [f"Headline {i}" for i in range(6)]
        
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test Creative",
            image_hash="abc123",
            page_id="987654321",
            headlines=too_many_headlines
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "maximum" in error_data["error"].lower() or "limit" in error_data["error"].lower()
        else:
            assert "error" in result_data
            assert "maximum" in result_data["error"].lower() or "limit" in result_data["error"].lower()
    
    async def test_create_ad_creative_validation_max_descriptions(self):
        """Test validation for maximum number of descriptions."""
        
        # Create list with more than 5 descriptions (assuming 5 is the limit)
        too_many_descriptions = [f"Description {i}" for i in range(6)]
        
        result = await create_ad_creative(
            access_token="test_token",
            account_id="act_123456789",
            name="Test Creative",
            image_hash="abc123",
            page_id="987654321",
            descriptions=too_many_descriptions
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "maximum" in error_data["error"].lower() or "limit" in error_data["error"].lower()
        else:
            assert "error" in result_data
            assert "maximum" in result_data["error"].lower() or "limit" in result_data["error"].lower()
    

    
    async def test_update_ad_creative_add_headlines(self):
        """Test updating an existing creative to add multiple headlines."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Updated Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                headlines=["New Headline 1", "New Headline 2", "New Headline 3"]
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with updated headlines
            # We need to check the first call (creative update), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative update
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "asset_feed_spec" in creative_data
            assert "titles" in creative_data["asset_feed_spec"]
            assert creative_data["asset_feed_spec"]["titles"] == [
                {"text": "New Headline 1"}, 
                {"text": "New Headline 2"}, 
                {"text": "New Headline 3"}
            ]
    
    async def test_update_ad_creative_add_descriptions(self):
        """Test updating an existing creative to add multiple descriptions."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Updated Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                descriptions=["New Description 1", "New Description 2"]
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with updated descriptions
            # We need to check the first call (creative update), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative update
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "asset_feed_spec" in creative_data
            assert "descriptions" in creative_data["asset_feed_spec"]
            assert creative_data["asset_feed_spec"]["descriptions"] == [
                {"text": "New Description 1"}, 
                {"text": "New Description 2"}
            ]
    
    async def test_update_ad_creative_update_dynamic_spec(self):
        """Test updating an existing creative's dynamic_creative_spec."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Updated Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                dynamic_creative_spec={
                    "headline_optimization": True,
                    "description_optimization": False
                }
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with updated dynamic_creative_spec
            # We need to check the first call (creative update), not the second call (details fetch)
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            # First call should be the creative update
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "dynamic_creative_spec" in creative_data
            assert creative_data["dynamic_creative_spec"]["headline_optimization"] is True
            assert creative_data["dynamic_creative_spec"]["description_optimization"] is False
    
    async def test_update_ad_creative_no_creative_id(self):
        """Test update_ad_creative with empty creative_id provided."""
        
        result = await update_ad_creative(
            creative_id="",  # Now provide the required parameter but with empty value
            access_token="test_token",
            headlines=["New Headline"]
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "creative id" in error_data["error"].lower()
        else:
            assert "error" in result_data
            assert "creative id" in result_data["error"].lower()
    
    async def test_update_ad_creative_cannot_mix_headline_and_headlines(self):
        """Test that mixing headline and headlines parameters raises error in update."""
        
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            headline="Single Headline",
            headlines=["Headline 1", "Headline 2"]
        )
        
        result_data = json.loads(result)
        
        # Check if error is wrapped in "data" field (MCP error response format)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'headline' and 'headlines'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'headline' and 'headlines'" in result_data["error"]
    
    async def test_update_ad_creative_cannot_mix_description_and_descriptions(self):
        """Test that mixing description and descriptions parameters raises error in update."""
        
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            description="Single Description",
            descriptions=["Description 1", "Description 2"]
        )
        
        result_data = json.loads(result)
        
        # Check if error is wrapped in "data" field (MCP error response format)
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "Cannot specify both 'description' and 'descriptions'" in error_data["error"]
        else:
            assert "error" in result_data
            assert "Cannot specify both 'description' and 'descriptions'" in result_data["error"]

    async def test_update_ad_creative_validation_max_headlines(self):
        """Test validation for maximum number of headlines in update."""
        
        # Create list with more than 5 headlines (limit)
        too_many_headlines = [f"Headline {i}" for i in range(6)]
        
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            headlines=too_many_headlines
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "maximum 5 headlines" in error_data["error"].lower()
        else:
            assert "error" in result_data
            assert "maximum 5 headlines" in result_data["error"].lower()
    
    async def test_update_ad_creative_validation_max_descriptions(self):
        """Test validation for maximum number of descriptions in update."""
        
        # Create list with more than 5 descriptions (limit)
        too_many_descriptions = [f"Description {i}" for i in range(6)]
        
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            descriptions=too_many_descriptions
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "maximum 5 descriptions" in error_data["error"].lower()
        else:
            assert "error" in result_data
            assert "maximum 5 descriptions" in result_data["error"].lower()
    
    async def test_update_ad_creative_validation_headline_length(self):
        """Test validation for headline character limit."""
        
        # Create headline longer than 40 characters
        long_headline = "A" * 41
        
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            headlines=[long_headline]
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "40 character limit" in error_data["error"]
        else:
            assert "error" in result_data
            assert "40 character limit" in result_data["error"]
    
    async def test_update_ad_creative_validation_description_length(self):
        """Test validation for description character limit."""
        
        # Create description longer than 125 characters
        long_description = "A" * 126
        
        result = await update_ad_creative(
            access_token="test_token",
            creative_id="123456789",
            descriptions=[long_description]
        )
        
        result_data = json.loads(result)
        # The error might be wrapped in a 'data' field
        if "data" in result_data:
            error_data = json.loads(result_data["data"])
            assert "error" in error_data
            assert "125 character limit" in error_data["error"]
        else:
            assert "error" in result_data
            assert "125 character limit" in result_data["error"]
    
    async def test_update_ad_creative_name_only(self):
        """Test updating just the creative name."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Updated Creative Name",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                name="Updated Creative Name"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with just the name
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "name" in creative_data
            assert creative_data["name"] == "Updated Creative Name"
            # Should not have asset_feed_spec since no dynamic content
            assert "asset_feed_spec" not in creative_data
    
    async def test_update_ad_creative_message_only(self):
        """Test updating just the creative message."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                message="Updated message text"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify the API call was made with object_story_spec
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "object_story_spec" in creative_data
            assert creative_data["object_story_spec"]["link_data"]["message"] == "Updated message text"
    
    async def test_update_ad_creative_cta_with_dynamic_content(self):
        """Test updating call_to_action_type with dynamic creative content."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                headlines=["Test Headline"],
                call_to_action_type="SHOP_NOW"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify CTA is added to asset_feed_spec when dynamic content exists
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "asset_feed_spec" in creative_data
            assert "call_to_action_types" in creative_data["asset_feed_spec"]
            assert creative_data["asset_feed_spec"]["call_to_action_types"] == ["SHOP_NOW"]
    
    async def test_update_ad_creative_cta_without_dynamic_content(self):
        """Test updating call_to_action_type without dynamic creative content."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Test Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                call_to_action_type="LEARN_MORE"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify CTA is added to object_story_spec when no dynamic content
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            assert "object_story_spec" in creative_data
            assert "call_to_action" in creative_data["object_story_spec"]["link_data"]
            assert creative_data["object_story_spec"]["link_data"]["call_to_action"]["type"] == "LEARN_MORE"
    
    async def test_update_ad_creative_combined_updates(self):
        """Test updating multiple parameters at once."""
        
        sample_creative_data = {
            "id": "123456789",
            "name": "Multi-Updated Creative",
            "status": "ACTIVE"
        }
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_creative_data
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                name="Multi-Updated Creative",
                message="Updated message",
                headlines=["New Headline 1", "New Headline 2"],
                descriptions=["New Description 1"],
                call_to_action_type="SIGN_UP"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            
            # Verify all updates are included
            call_args_list = mock_api.call_args_list
            assert len(call_args_list) >= 1
            
            first_call = call_args_list[0]
            creative_data = first_call[0][2]  # params is the third argument
            
            # Should have name
            assert creative_data["name"] == "Multi-Updated Creative"
            
            # Should have asset_feed_spec with all dynamic content
            assert "asset_feed_spec" in creative_data
            assert "titles" in creative_data["asset_feed_spec"]
            assert "descriptions" in creative_data["asset_feed_spec"]
            assert "bodies" in creative_data["asset_feed_spec"]
            assert "call_to_action_types" in creative_data["asset_feed_spec"]
            
            # Verify content
            assert creative_data["asset_feed_spec"]["titles"] == [
                {"text": "New Headline 1"}, {"text": "New Headline 2"}
            ]
            assert creative_data["asset_feed_spec"]["descriptions"] == [
                {"text": "New Description 1"}
            ]
            assert creative_data["asset_feed_spec"]["bodies"] == [
                {"text": "Updated message"}
            ]
            assert creative_data["asset_feed_spec"]["call_to_action_types"] == ["SIGN_UP"]
    
    async def test_update_ad_creative_api_error_handling(self):
        """Test error handling when API request fails."""
        
        with patch('meta_ads_mcp.core.ads.make_api_request', new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = Exception("API request failed")
            
            result = await update_ad_creative(
                access_token="test_token",
                creative_id="123456789",
                name="Test Creative"
            )
            
            result_data = json.loads(result)
            # The error might be wrapped in a 'data' field
            if "data" in result_data:
                error_data = json.loads(result_data["data"])
                assert "error" in error_data
                assert error_data["error"] == "Failed to update ad creative"
                assert "details" in error_data
                assert "update_data_sent" in error_data
            else:
                assert "error" in result_data
                assert result_data["error"] == "Failed to update ad creative"
                assert "details" in result_data
                assert "update_data_sent" in result_data
 