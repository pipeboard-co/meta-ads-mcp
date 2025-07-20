# Meta Ads MCP

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for interacting with Meta Ads API. This tool enables AI models to access, analyze, and manage Meta advertising campaigns through a standardized interface, allowing LLMs to retrieve performance data, visualize ad creatives, and provide strategic insights for Facebook, Instagram, and other Meta platforms.

> **DISCLAIMER:** This is an unofficial third-party tool and is not associated with, endorsed by, or affiliated with Meta in any way. This project is maintained independently and uses Meta's public APIs according to their terms of service. Meta, Facebook, Instagram, and other Meta brand names are trademarks of their respective owners.

[![Meta Ads MCP Server Demo](https://github.com/user-attachments/assets/3e605cee-d289-414b-814c-6299e7f3383e)](https://github.com/user-attachments/assets/3e605cee-d289-414b-814c-6299e7f3383e)

## Community & Support

- [Discord](https://discord.gg/hNxpJcqM52). Join the community.
- [Email Support](info@pipeboard.co). Email us for support.

## Table of Contents

- [🚀 Getting started with Remote MCP (Recommended for Marketers)](#getting-started-with-remote-mcp-recommended)
- [Local Installation (Technical Users Only)](#local-installation-technical-users-only)
- [Features](#features)
- [Configuration](#configuration)
- [Available MCP Tools](#available-mcp-tools)
- [Privacy and Security](#privacy-and-security)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Getting started with Remote MCP (Recommended)

The fastest and most reliable way to get started is to **[🚀 Get started with our Meta Ads Remote MCP](https://pipeboard.co)**. Our cloud service uses streamable HTTP transport for reliable, scalable access to Meta Ads data. No technical setup required - just connect and start analyzing your ad campaigns with AI!

### For Claude Pro/Max Users

1. Go to [claude.ai/settings/integrations](https://claude.ai/settings/integrations) (requires Claude Pro or Max)
2. Click "Add Integration" and enter:
   - **Name**: "Pipeboard Meta Ads" (or any name you prefer)
   - **Integration URL**: `https://mcp.pipeboard.co/meta-ads-mcp`
3. Click "Connect" next to the integration and follow the prompts to:
   - Login to Pipeboard
   - Connect your Facebook Ads account

That's it! You can now ask Claude to analyze your Meta ad campaigns, get performance insights, and manage your advertising.

### For Cursor Users

Add the following to your `~/.cursor/mcp.json`. Once you enable the remote MCP, click on "Needs login" to finish the login process.


```json
{
  "mcpServers": {
    "meta-ads-remote": {
      "url": "https://mcp.pipeboard.co/meta-ads-mcp"
    }
  }
}
```

### For Other MCP Clients

Use the Remote MCP URL: `https://mcp.pipeboard.co/meta-ads-mcp`

**[📖 Get detailed setup instructions for your AI client here](https://pipeboard.co)**

## Local Installation (Technical Users Only)

If you're a developer or need to customize the installation, you can run Meta Ads MCP locally. **Most marketers should use the Remote MCP above instead!** For complete technical setup instructions, see our **[Local Installation Guide](LOCAL_INSTALLATION.md)**.

Meta Ads MCP also supports **streamable HTTP transport**, allowing you to run it as a standalone HTTP API for web applications and custom integrations. See **[Streamable HTTP Setup Guide](STREAMABLE_HTTP_SETUP.md)** for complete instructions.

### Quick Local Setup

```bash
# Install via uvx (recommended)
uvx meta-ads-mcp

# Set your Pipeboard token
export PIPEBOARD_API_TOKEN=your_pipeboard_token

# Add to your MCP client configuration
```

For detailed step-by-step instructions, authentication setup, debugging, and troubleshooting, visit **[LOCAL_INSTALLATION.md](LOCAL_INSTALLATION.md)**.

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

## Configuration

### Remote MCP (Recommended)

**[✨ Get started with Remote MCP here](https://pipeboard.co)** - no technical setup required! Just connect your Facebook Ads account and start asking AI to analyze your campaigns.

### Local Installation (Technical Users)

For local installation configuration, authentication options, and advanced technical setup, see our **[Local Installation Guide](LOCAL_INSTALLATION.md)**.

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

20. `mcp_meta_ads_get_login_link`
    - Get a clickable login link for Meta Ads authentication
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: A clickable resource link for Meta authentication

21. `mcp_meta-ads_create_budget_schedule`
    - Create a budget schedule for a Meta Ads campaign.
    - Inputs:
      - `campaign_id`: Meta Ads campaign ID.
      - `budget_value`: Amount of budget increase.
      - `budget_value_type`: Type of budget value ("ABSOLUTE" or "MULTIPLIER").
      - `time_start`: Unix timestamp for when the high demand period should start.
      - `time_end`: Unix timestamp for when the high demand period should end.
      - `access_token` (optional): Meta API access token.
    - Returns: JSON string with the ID of the created budget schedule or an error message.

## Privacy and Security

Meta Ads MCP follows security best practices with secure token management and automatic authentication handling. 

- **Remote MCP**: All authentication is handled securely in the cloud - no local token storage required
- **Local Installation**: Tokens are cached securely on your local machine - see [Local Installation Guide](LOCAL_INSTALLATION.md) for details

## Testing

### Basic Testing

Test your Meta Ads MCP connection with any MCP client:

1. **Verify Account Access**: Ask your LLM to use `mcp_meta_ads_get_ad_accounts`
2. **Check Account Details**: Use `mcp_meta_ads_get_account_info` with your account ID
3. **List Campaigns**: Try `mcp_meta_ads_get_campaigns` to see your ad campaigns

For detailed local installation testing, see [Local Installation Guide](LOCAL_INSTALLATION.md).

## Troubleshooting

### 💡 Quick Fix: Skip the Technical Setup!

The easiest way to avoid any setup issues is to **[🎯 use our Remote MCP instead](https://pipeboard.co)**. No downloads, no configuration - just connect your ads account and start getting AI insights on your campaigns immediately!

### Local Installation Issues

For comprehensive troubleshooting, debugging, and local installation issues, see our **[Local Installation Guide](LOCAL_INSTALLATION.md)** which includes:

- Authentication troubleshooting
- Installation issues and solutions  
- API error resolution
- Debug logs and diagnostic commands
- Performance optimization tips 
