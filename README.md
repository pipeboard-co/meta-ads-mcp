[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/pipeboard-co-meta-ads-mcp-badge.png)](https://mseep.ai/app/pipeboard-co-meta-ads-mcp)

# Meta Ads MCP

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for interacting with Meta Ads API. This tool enables AI models to access, analyze, and manage Meta advertising campaigns through a standardized interface, allowing LLMs to retrieve performance data, visualize ad creatives, and provide strategic insights for Facebook, Instagram, and other Meta platforms.

> **DISCLAIMER:** This is an unofficial third-party tool and is not associated with, endorsed by, or affiliated with Meta in any way. This project is maintained independently and uses Meta's public APIs according to their terms of service. Meta, Facebook, Instagram, and other Meta brand names are trademarks of their respective owners.

[![Meta Ads MCP Server Demo](https://github.com/user-attachments/assets/3e605cee-d289-414b-814c-6299e7f3383e)](https://github.com/user-attachments/assets/3e605cee-d289-414b-814c-6299e7f3383e)


## Community & Support

- [Discord](https://discord.gg/hNxpJcqM52). Join the community.
- [Email Support](info@pipeboard.co). Email us for support.
  
## Quick Start

1. Sign-up to [Pipeboard](https://pipeboard.co) to authenticate with Meta (alternatively, you can setup your own [custom meta app](CUSTOM_META_APP.md))
2. Get your Pipeboard token at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens) 
3. Add this configuration to your MCP client:

```json
"mcpServers": {
  "meta-ads": {
    "command": "uvx",
    "args": ["meta-ads-mcp"],
    "env": {
      "PIPEBOARD_API_TOKEN": "your_pipeboard_token"  // Get your token at https://pipeboard.co/api-tokens
    }
  }
}
```

That's it! You can now use Meta Ads MCP in your favorite MCP client.

> **Note**: If you prefer to use your own Meta Developer App instead of Pipeboard authentication, see [CUSTOM_META_APP.md](CUSTOM_META_APP.md) for instructions.

## Features

- **AI-Powered Campaign Analysis**: Let your favorite LLM analyze your campaigns and provide actionable insights on performance
- **Strategic Recommendations**: Receive data-backed suggestions for optimizing ad spend, targeting, and creative content
- **Automated Monitoring**: Ask any MCP-compatible LLM to track performance metrics and alert you about significant changes
- **Budget Optimization**: Get recommendations for reallocating budget to better-performing ad sets
- **Creative Improvement**: Receive feedback on ad copy, imagery, and calls-to-action
- **Campaign Management**: Request changes to campaigns, ad sets, and ads (all changes require explicit confirmation)
- **Cross-Platform Integration**: Works with Facebook, Instagram, and all Meta ad platforms
- **Universal LLM Support**: Compatible with any MCP client including Claude Desktop, Cursor, Cherry Studio, and more
- **Simple Authentication**: Easy setup with secure OAuth authentication
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Advanced Setup

### Development Installation

If you're contributing to the project or need to run it directly:

```bash
# From the repository root
uv pip install -e .
```

## Privacy and Security

The Meta Ads MCP follows security best practices:

1. Tokens are cached in a platform-specific secure location:
   - Windows: `%APPDATA%\meta-ads-mcp\token_cache.json`
   - macOS: `~/Library/Application Support/meta-ads-mcp/token_cache.json`
   - Linux: `~/.config/meta-ads-mcp/token_cache.json`

2. You do not need to provide your access token for each command; it will be automatically retrieved from the cache.

## Testing

### LLM Interface Testing

When using the Meta Ads MCP with an LLM interface (like Claude):

1. Ensure the PIPEBOARD_API_TOKEN environment variable is set
2. Verify account access by calling `mcp_meta_ads_get_ad_accounts`
3. Check specific account details with `mcp_meta_ads_get_account_info`

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Verify your Pipeboard setup:
   - Check that `PIPEBOARD_API_TOKEN` is set correctly
   - Verify your token in the Pipeboard dashboard
   - Try forcing a new login: `python test_pipeboard_auth.py --force-login`

2. When using the LLM interface:
   - Ensure the PIPEBOARD_API_TOKEN environment variable is set
   - Check that the callback server is running properly

### API Errors

If you receive errors from the Meta API:
1. Ensure the user has appropriate permissions on the ad accounts
2. Check if there are rate limits or other restrictions
3. Verify your Pipeboard token hasn't expired

## Log Location

Log files are stored in a platform-specific location:

- **macOS**: `~/Library/Application Support/meta-ads-mcp/meta_ads_debug.log`
- **Windows**: `%APPDATA%\meta-ads-mcp\meta_ads_debug.log` 
- **Linux**: `~/.config/meta-ads-mcp/meta_ads_debug.log` 

## Configuration

### Pipeboard Authentication

The easiest way to use Meta Ads MCP is with Pipeboard authentication:

1. Sign up at [Pipeboard.co](https://pipeboard.co) and generate an API token
2. Set the environment variable:
   ```bash
   export PIPEBOARD_API_TOKEN=your_pipeboard_token
   ```
3. Run meta-ads-mcp - it will handle authentication automatically

### Usage with Cursor or Claude Desktop

Add this to your `claude_desktop_config.json` to integrate with Claude or `~/.cursor/mcp.json` to integrate with Cursor:

```json
"mcpServers": {
  "meta-ads": {
    "command": "uvx",
    "args": ["meta-ads-mcp"],
    "env": {
      "PIPEBOARD_API_TOKEN": "your_pipeboard_token"  // Get your token at https://pipeboard.co
    }
  }
}
```

## Transports

Meta Ads MCP uses **stdio transport** by default, which works with MCP clients like Claude Desktop and Cursor. For web applications and direct HTTP API access, see [STREAMABLE_HTTP_SETUP.md](STREAMABLE_HTTP_SETUP.md) for streamable HTTP transport configuration.

### Available MCP Tools

1. `mcp_meta_ads_get_ad_accounts`
   - Get ad accounts accessible by a user
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `user_id`: Meta user ID or "me" for the current user
     - `limit`: Maximum number of accounts to return (default: 10)
   - Returns: List of accessible ad accounts with their details

2. `mcp_meta_ads_get_account_info`
   - Get detailed information about a specific ad account
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
   - Returns: Detailed information about the specified account

3. `mcp_meta_ads_get_account_pages`
   - Get pages associated with a Meta Ads account
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX) or "me" for the current user's pages
   - Returns: List of pages associated with the account, useful for ad creation and management

4. `mcp_meta_ads_get_campaigns`
   - Get campaigns for a Meta Ads account with optional filtering
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
     - `limit`: Maximum number of campaigns to return (default: 10)
     - `status_filter`: Filter by status (empty for all, or 'ACTIVE', 'PAUSED', etc.)
   - Returns: List of campaigns matching the criteria

5. `mcp_meta_ads_get_campaign_details`
   - Get detailed information about a specific campaign
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `campaign_id`: Meta Ads campaign ID
   - Returns: Detailed information about the specified campaign

6. `mcp_meta_ads_create_campaign`
   - Create a new campaign in a Meta Ads account
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
     - `name`: Campaign name
     - `objective`: Campaign objective (AWARENESS, TRAFFIC, ENGAGEMENT, etc.)
     - `status`: Initial campaign status (default: PAUSED)
     - `special_ad_categories`: List of special ad categories if applicable
     - `daily_budget`: Daily budget in account currency (in cents)
     - `lifetime_budget`: Lifetime budget in account currency (in cents)
   - Returns: Confirmation with new campaign details

7. `mcp_meta_ads_get_adsets`
   - Get ad sets for a Meta Ads account with optional filtering by campaign
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
     - `limit`: Maximum number of ad sets to return (default: 10)
     - `campaign_id`: Optional campaign ID to filter by
   - Returns: List of ad sets matching the criteria

8. `mcp_meta_ads_get_adset_details`
   - Get detailed information about a specific ad set
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `adset_id`: Meta Ads ad set ID
   - Returns: Detailed information about the specified ad set

9. `mcp_meta_ads_create_adset`
   - Create a new ad set in a Meta Ads account
   - Inputs:
     - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
     - `campaign_id`: Meta Ads campaign ID this ad set belongs to
     - `name`: Ad set name
     - `status`: Initial ad set status (default: PAUSED)
     - `daily_budget`: Daily budget in account currency (in cents) as a string
     - `lifetime_budget`: Lifetime budget in account currency (in cents) as a string
     - `targeting`: Targeting specifications (e.g., age, location, interests)
     - `optimization_goal`: Conversion optimization goal (e.g., 'LINK_CLICKS')
     - `billing_event`: How you're charged (e.g., 'IMPRESSIONS')
     - `bid_amount`: Bid amount in account currency (in cents)
     - `bid_strategy`: Bid strategy (e.g., 'LOWEST_COST')
     - `start_time`, `end_time`: Optional start/end times (ISO 8601)
     - `access_token` (optional): Meta API access token
   - Returns: Confirmation with new ad set details

10. `mcp_meta_ads_get_ads`
    - Get ads for a Meta Ads account with optional filtering
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
      - `limit`: Maximum number of ads to return (default: 10)
      - `campaign_id`: Optional campaign ID to filter by
      - `adset_id`: Optional ad set ID to filter by
    - Returns: List of ads matching the criteria

11. `mcp_meta_ads_create_ad`
    - Create a new ad with an existing creative
    - Inputs:
      - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
      - `name`: Ad name
      - `adset_id`: Ad set ID where this ad will be placed
      - `creative_id`: ID of an existing creative to use
      - `status`: Initial ad status (default: PAUSED)
      - `bid_amount`: Optional bid amount (in cents)
      - `tracking_specs`: Optional tracking specifications
      - `access_token` (optional): Meta API access token
    - Returns: Confirmation with new ad details

12. `mcp_meta_ads_get_ad_details`
    - Get detailed information about a specific ad
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `ad_id`: Meta Ads ad ID
    - Returns: Detailed information about the specified ad

13. `mcp_meta_ads_get_ad_creatives`
    - Get creative details for a specific ad
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `ad_id`: Meta Ads ad ID
    - Returns: Creative details including text, images, and URLs

14. `mcp_meta_ads_create_ad_creative`
    - Create a new ad creative using an uploaded image hash
    - Inputs:
      - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
      - `name`: Creative name
      - `image_hash`: Hash of the uploaded image
      - `page_id`: Facebook Page ID for the ad
      - `link_url`: Destination URL
      - `message`: Ad copy/text
      - `headline`: Ad headline
      - `description`: Ad description
      - `call_to_action_type`: CTA button type (e.g., 'LEARN_MORE')
      - `instagram_actor_id`: Optional Instagram account ID
      - `access_token` (optional): Meta API access token
    - Returns: Confirmation with new creative details

15. `mcp_meta_ads_upload_ad_image`
    - Upload an image to use in Meta Ads creatives
    - Inputs:
      - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
      - `image_path`: Path to the image file to upload
      - `name`: Optional name for the image
      - `access_token` (optional): Meta API access token
    - Returns: JSON response with image details including hash

16. `mcp_meta_ads_get_ad_image`
    - Get, download, and visualize a Meta ad image in one step
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `ad_id`: Meta Ads ad ID
    - Returns: The ad image ready for direct visual analysis

17. `mcp_meta_ads_update_ad`
    - Update an ad with new settings
    - Inputs:
      - `ad_id`: Meta Ads ad ID
      - `status`: Update ad status (ACTIVE, PAUSED, etc.)
      - `bid_amount`: Bid amount in account currency (in cents for USD)
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: Confirmation with updated ad details and a confirmation link

18. `mcp_meta_ads_update_adset`
    - Update an ad set with new settings including frequency caps
    - Inputs:
      - `adset_id`: Meta Ads ad set ID
      - `frequency_control_specs`: List of frequency control specifications
      - `bid_strategy`: Bid strategy (e.g., 'LOWEST_COST_WITH_BID_CAP')
      - `bid_amount`: Bid amount in account currency (in cents for USD)
      - `status`: Update ad set status (ACTIVE, PAUSED, etc.)
      - `targeting`: Targeting specifications including targeting_automation
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: Confirmation with updated ad set details and a confirmation link

19. `mcp_meta_ads_get_insights`
    - Get performance insights for a campaign, ad set, ad or account
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `object_id`: ID of the campaign, ad set, ad or account
      - `time_range`: Time range for insights (default: maximum)
      - `breakdown`: Optional breakdown dimension (e.g., age, gender, country)
      - `level`: Level of aggregation (ad, adset, campaign, account)
    - Returns: Performance metrics for the specified object

20. `mcp_meta_ads_debug_image_download`
    - Debug image download issues and report detailed diagnostics
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `url`: Direct image URL to test (optional)
      - `ad_id`: Meta Ads ad ID (optional, used if url is not provided)
    - Returns: Diagnostic information about image download attempts

21. `mcp_meta_ads_get_login_link`
    - Get a clickable login link for Meta Ads authentication
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: A clickable resource link for Meta authentication

22. `mcp_meta-ads_create_budget_schedule`
    - Create a budget schedule for a Meta Ads campaign.
    - Inputs:
      - `campaign_id`: Meta Ads campaign ID.
      - `budget_value`: Amount of budget increase.
      - `budget_value_type`: Type of budget value ("ABSOLUTE" or "MULTIPLIER").
      - `time_start`: Unix timestamp for when the high demand period should start.
      - `time_end`: Unix timestamp for when the high demand period should end.
      - `access_token` (optional): Meta API access token.
    - Returns: JSON string with the ID of the created budget schedule or an error message.
