# Meta Ads MCP

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that lets AI assistants run your Meta Ads end to end — launch campaigns, upload creatives, update budgets, and dig into performance through natural conversation. Works across Facebook, Instagram, and other Meta surfaces.

This is the **Meta Ads node** of the [Pipeboard](https://pipeboard.co) MCP family — five remote MCP servers (Meta, Google, TikTok, Snap, Reddit) plus a unified [Pipeboard CLI](https://github.com/pipeboard-co/pipeboard-cli), **230+ tools** in total, one auth, one safety model. If you are comparing single-platform MCPs, you are looking at one node of a network — see [The Pipeboard MCP Family](#the-pipeboard-mcp-family) below.

> **Note:** This is an independent open-source project that uses Meta's public APIs. If you're looking for an officially approved Meta app, check out [Pipeboard](https://pipeboard.co). Meta, Facebook, Instagram, and other Meta brand names are trademarks of their respective owners.

[![Meta Ads MCP Server Demo](https://github.com/user-attachments/assets/3e605cee-d289-414b-814c-6299e7f3383e)](https://github.com/user-attachments/assets/3e605cee-d289-414b-814c-6299e7f3383e)

[![MCP Badge](https://lobehub.com/badge/mcp/nictuku-meta-ads-mcp)](https://lobehub.com/mcp/nictuku-meta-ads-mcp)

mcp-name: co.pipeboard/meta-ads-mcp

## Community & Support

- [Discord](https://discord.gg/YzMwQ8zrjr). Join the community.
- [Email Support](mailto:info@pipeboard.co). Email us for support.

## Table of Contents

- [The Pipeboard MCP Family](#the-pipeboard-mcp-family)
- [🚀 Getting started with Remote MCP (Recommended for Marketers)](#getting-started-with-remote-mcp-recommended)
- [Pipeboard CLI (Alternative to MCP)](#pipeboard-cli-alternative-to-mcp)
- [Local Installation (Technical Users Only)](#local-installation-technical-users-only)
- [Features](#features)
- [Configuration](#configuration)
- [Available MCP Tools](#available-mcp-tools)
- [Licensing](#licensing)
- [Privacy and Security](#privacy-and-security)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## The Pipeboard MCP Family

Pipeboard ships a remote [MCP server](https://modelcontextprotocol.io/) for every major ad platform — plus a single-binary [CLI](https://github.com/pipeboard-co/pipeboard-cli) that wraps all of them. **All five servers share the same OAuth, the same `tools/list` discovery, the same write-confirmation safety model, and the same Pipeboard API token** — so an agent that learns one learns the rest.

### Remote MCP servers

| Platform | Remote MCP URL | Surface |
|---|---|---|
| **Meta Ads MCP** (Facebook + Instagram) | `https://meta-ads.mcp.pipeboard.co/` | **42 tools** — campaigns, ad sets, ads, creatives (incl. dynamic creative testing), image upload, insights, interest / behavior / demographic / geo targeting, page management |
| **Google Ads MCP** | `https://google-ads.mcp.pipeboard.co/` | **59 tools** — campaigns, ad groups, responsive search ads, Performance Max, keywords, GAQL queries, extensions (sitelinks, callouts, structured snippets), audiences, asset uploads, generic mutate |
| **TikTok Ads MCP** | `https://tiktok-ads.mcp.pipeboard.co/` | **59 tools** — campaigns, ad groups, ads, identities, image and video upload, audience and creative management, insights |
| **Snap Ads MCP** | `https://snap-ads.mcp.pipeboard.co/` | **37 tools** — ad accounts, campaigns, ad squads, ads, creatives, media upload, insights |
| **Reddit Ads MCP** | `https://reddit-ads.mcp.pipeboard.co/` | **33 tools** — accounts, campaigns, ad groups, ads, performance reports |

**That is 230+ tools across five ad platforms behind one auth.** Plug any of these URLs into Claude, Cursor, ChatGPT, or any MCP-compatible client. Connect your ad accounts once at [pipeboard.co](https://pipeboard.co) and every client gets access.

### Pipeboard CLI — the same tools, in your shell

[**Pipeboard CLI**](https://github.com/pipeboard-co/pipeboard-cli) is a single Go binary that exposes every MCP tool above as a typed shell command — built for AI coding agents (Claude Code, Cline, OpenClaw, Codex) and automation scripts that prefer subprocess calls over JSON-RPC:

```bash
brew install pipeboard-co/tap/pipeboard
export PIPEBOARD_API_TOKEN=<your-token>

pipeboard meta-ads get-campaigns   --account-id act_123
pipeboard google-ads execute-gaql-query   --customer-id 1234567890 --query "..."
pipeboard tiktok-ads get-campaigns --advertiser-id 7605685552884596737
```

Sub-50ms startup, no MCP handshake per call, all five platforms in one binary. Full docs in the [pipeboard-cli repo](https://github.com/pipeboard-co/pipeboard-cli).

### Why a family instead of one MCP per repo?

- **One account, every platform** — auth once at [pipeboard.co](https://pipeboard.co); manage Meta + Google + TikTok + Snap + Reddit from the same agent session
- **Cross-platform questions get cross-platform answers** — "which channel had the cheapest signups last week?" actually works
- **Same safety contract everywhere** — writes are explicit, new campaigns start paused where the platform supports it, and confirmation prompts look identical across all five servers
- **One token, one rate-limit ceiling, one place to revoke** — no juggling separate OAuth flows or per-vendor installs

Single-platform MCP benchmarks miss the point. The value is the network, not the node.

## Getting started with Remote MCP (Recommended)

The fastest and most reliable way to get started is to **[🚀 Get started with our Meta Ads Remote MCP](https://pipeboard.co)**. Our cloud service uses streamable HTTP transport for reliable, scalable access to your Meta Ads account. No technical setup required — just connect and start launching, updating, and analyzing campaigns with AI!

### For Claude Pro/Max Users

1. Go to [claude.ai/settings/integrations](https://claude.ai/settings/integrations) (requires Claude Pro or Max)
2. Click "Add Integration" and enter:
   - **Name**: "Pipeboard Meta Ads" (or any name you prefer)
   - **Integration URL**: `https://meta-ads.mcp.pipeboard.co/`
3. Click "Connect" next to the integration and follow the prompts to:
   - Login to Pipeboard
   - Connect your Facebook Ads account

That's it! You can now ask Claude to analyze your Meta ad campaigns, get performance insights, and manage your advertising.

#### Advanced: Direct Token Authentication (Claude)

For direct token-based authentication without the interactive flow, use this URL format when adding the integration:

```
https://meta-ads.mcp.pipeboard.co/?token=YOUR_PIPEBOARD_TOKEN
```

Get your token at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens).

### For Cursor Users

Add the following to your `~/.cursor/mcp.json`. Once you enable the remote MCP, click on "Needs login" to finish the login process.


```json
{
  "mcpServers": {
    "meta-ads-remote": {
      "url": "https://meta-ads.mcp.pipeboard.co/"
    }
  }
}
```

#### Advanced: Direct Token Authentication (Cursor)

If you prefer to authenticate without the interactive login flow, you can include your Pipeboard API token directly in the URL:

```json
{
  "mcpServers": {
    "meta-ads-remote": {
      "url": "https://meta-ads.mcp.pipeboard.co/?token=YOUR_PIPEBOARD_TOKEN"
    }
  }
}
```

Get your token at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens).

### For Other MCP Clients

Use the Remote MCP URL: `https://meta-ads.mcp.pipeboard.co/`

**[📖 Get detailed setup instructions for your AI client here](https://pipeboard.co)**

#### Advanced: Direct Token Authentication (OpenClaw and other clients)

For MCP clients that support token-based authentication, you can append your Pipeboard API token to the URL:

```
https://meta-ads.mcp.pipeboard.co/?token=YOUR_PIPEBOARD_TOKEN
```

This bypasses the interactive login flow and authenticates immediately. Get your token at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens).

### Other platforms

Meta Ads is one of five remote MCP servers in the family — see [The Pipeboard MCP Family](#the-pipeboard-mcp-family) for Google Ads, TikTok Ads, Snap Ads, and Reddit Ads, all set up the same way.

## Pipeboard CLI (Alternative to MCP)

If your agent prefers shell commands over JSON-RPC, the [Pipeboard CLI](https://github.com/pipeboard-co/pipeboard-cli) exposes every tool in the family as a typed subcommand — see [the family section above](#pipeboard-cli--the-same-tools-in-your-shell) for the quick install and the [pipeboard-cli repo](https://github.com/pipeboard-co/pipeboard-cli) for full docs.

## Local Installation (Advanced Technical Users Only)

🚀 **We strongly recommend using [Remote MCP](https://pipeboard.co) instead** - it's faster, more reliable, and requires no technical setup.

Meta Ads MCP also supports a local streamable HTTP transport, allowing you to run it as a standalone HTTP API for web applications and custom integrations. See **[Streamable HTTP Setup Guide](STREAMABLE_HTTP_SETUP.md)** for complete instructions.

## Features

- **Campaign Management**: Launch campaigns, ad sets, and ads, update budgets, pause and resume, and apply targeting changes — all from a conversation, with explicit confirmation on every write
- **Creative Operations**: Upload images, build creatives, and update copy, headlines, descriptions, and CTAs without leaving your AI client
- **Dynamic Creative Testing**: One API for both simple ads (single headline/description) and full A/B testing (multiple headlines/descriptions)
- **AI-Powered Campaign Analysis**: Let your favorite LLM analyze performance and surface actionable insights
- **Strategic Recommendations**: Receive data-backed suggestions for optimizing ad spend, targeting, and creative content
- **Budget Optimization**: Get recommendations for reallocating budget to better-performing ad sets
- **Creative Improvement**: Receive feedback on ad copy, imagery, and calls-to-action
- **Automated Monitoring**: Ask any MCP-compatible LLM to track performance metrics and alert you about significant changes
- **Cross-Platform Integration**: Works with Facebook, Instagram, and all Meta ad surfaces
- **Universal LLM Support**: Compatible with any MCP client including Claude Desktop, Cursor, Cherry Studio, and more
- **Enhanced Search**: Generic search function includes page searching when queries mention "page" or "pages"
- **Simple Authentication**: Easy setup with secure OAuth authentication
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Configuration

### Remote MCP (Recommended)

**[✨ Get started with Remote MCP here](https://pipeboard.co)** - no technical setup required! Just connect your Facebook Ads account and start asking AI to analyze your campaigns.

### Local Installation (Advanced Technical Users)

For advanced users who need to self-host, the package can be installed from source. Local installations require creating your own Meta Developer App. **We recommend using [Remote MCP](https://pipeboard.co) for a simpler experience.**

### Available MCP Tools

1. `mcp_meta_ads_get_ad_accounts`
   - Get ad accounts accessible by a user
   - Inputs:
     - `access_token` (optional): Meta API access token (will use cached token if not provided)
     - `user_id`: Meta user ID or "me" for the current user
     - `limit`: Maximum number of accounts to return (default: 200)
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
     - `objective`: Campaign objective (ODAX, outcome-based). Must be one of:
       - `OUTCOME_AWARENESS`
       - `OUTCOME_TRAFFIC`
       - `OUTCOME_ENGAGEMENT`
       - `OUTCOME_LEADS`
       - `OUTCOME_SALES`
       - `OUTCOME_APP_PROMOTION`
       
       Note: Legacy objectives such as `BRAND_AWARENESS`, `LINK_CLICKS`, `CONVERSIONS`, `APP_INSTALLS`, etc. are no longer valid for new campaigns and will cause a 400 error. Use the outcome-based values above. Common mappings:
       - `BRAND_AWARENESS` → `OUTCOME_AWARENESS`
       - `REACH` → `OUTCOME_AWARENESS`
       - `LINK_CLICKS`, `TRAFFIC` → `OUTCOME_TRAFFIC`
       - `POST_ENGAGEMENT`, `PAGE_LIKES`, `EVENT_RESPONSES`, `VIDEO_VIEWS` → `OUTCOME_ENGAGEMENT`
       - `LEAD_GENERATION` → `OUTCOME_LEADS`
       - `CONVERSIONS`, `CATALOG_SALES`, `MESSAGES` (sales-focused flows) → `OUTCOME_SALES`
       - `APP_INSTALLS` → `OUTCOME_APP_PROMOTION`
     - `status`: Initial campaign status (default: PAUSED)
     - `special_ad_categories`: List of special ad categories if applicable
     - `daily_budget`: Daily budget in account currency (in cents)
     - `lifetime_budget`: Lifetime budget in account currency (in cents)
     - `bid_strategy`: Bid strategy. Must be one of: `LOWEST_COST_WITHOUT_CAP`, `LOWEST_COST_WITH_BID_CAP`, `COST_CAP`, `LOWEST_COST_WITH_MIN_ROAS`.
   - Returns: Confirmation with new campaign details

   - Example:
     ```json
     {
       "name": "2025 - Bedroom Furniture - Awareness",
       "account_id": "act_123456789012345",
       "objective": "OUTCOME_AWARENESS",
       "special_ad_categories": [],
       "status": "PAUSED",
       "buying_type": "AUCTION",
       "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
       "daily_budget": 10000
     }
     ```

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
     - `bid_amount`: Bid amount in cents. Required for LOWEST_COST_WITH_BID_CAP, COST_CAP, TARGET_COST.
     - `bid_strategy`: Bid strategy (e.g., 'LOWEST_COST_WITHOUT_CAP', 'LOWEST_COST_WITH_MIN_ROAS')
     - `bid_constraints`: Bid constraints dict. Required for LOWEST_COST_WITH_MIN_ROAS (e.g., `{"roas_average_floor": 20000}`)
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
      - `headline`: Single headline for simple ads (cannot be used with headlines)
      - `headlines`: List of headlines for dynamic creative testing (cannot be used with headline)
      - `description`: Single description for simple ads (cannot be used with descriptions)
      - `descriptions`: List of descriptions for dynamic creative testing (cannot be used with description)
      - `dynamic_creative_spec`: Dynamic creative optimization settings
      - `call_to_action_type`: CTA button type (e.g., 'LEARN_MORE')
      - `instagram_actor_id`: Optional Instagram account ID
      - `access_token` (optional): Meta API access token
    - Returns: Confirmation with new creative details

15. `mcp_meta_ads_update_ad_creative`
    - Update an existing ad creative with new content or settings
    - Inputs:
      - `creative_id`: Meta Ads creative ID to update
      - `name`: New creative name
      - `message`: New ad copy/text
      - `headline`: Single headline for simple ads (cannot be used with headlines)
      - `headlines`: New list of headlines for dynamic creative testing (cannot be used with headline)
      - `description`: Single description for simple ads (cannot be used with descriptions)
      - `descriptions`: New list of descriptions for dynamic creative testing (cannot be used with description)
      - `dynamic_creative_spec`: New dynamic creative optimization settings
      - `call_to_action_type`: New call to action button type
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: Confirmation with updated creative details

16. `mcp_meta_ads_upload_ad_image`
    - Upload an image to use in Meta Ads creatives
    - Inputs:
      - `account_id`: Meta Ads account ID (format: act_XXXXXXXXX)
      - `image_path`: Path to the image file to upload
      - `name`: Optional name for the image
      - `access_token` (optional): Meta API access token
    - Returns: JSON response with image details including hash

17. `mcp_meta_ads_get_ad_image`
    - Get, download, and visualize a Meta ad image in one step
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `ad_id`: Meta Ads ad ID
    - Returns: The ad image ready for direct visual analysis

18. `mcp_meta_ads_update_ad`
    - Update an ad with new settings
    - Inputs:
      - `ad_id`: Meta Ads ad ID
      - `status`: Update ad status (ACTIVE, PAUSED, etc.)
      - `bid_amount`: Bid amount in account currency (in cents for USD)
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: Confirmation with updated ad details and a confirmation link

19. `mcp_meta_ads_update_adset`
    - Update an ad set with new settings including frequency caps
    - Inputs:
      - `adset_id`: Meta Ads ad set ID
      - `frequency_control_specs`: List of frequency control specifications
      - `bid_strategy`: Bid strategy (e.g., 'LOWEST_COST_WITH_BID_CAP', 'LOWEST_COST_WITH_MIN_ROAS')
      - `bid_amount`: Bid amount in cents. Required for LOWEST_COST_WITH_BID_CAP, COST_CAP, TARGET_COST.
      - `bid_constraints`: Bid constraints dict. Required for LOWEST_COST_WITH_MIN_ROAS (e.g., `{"roas_average_floor": 20000}`)
      - `status`: Update ad set status (ACTIVE, PAUSED, etc.)
      - `targeting`: Targeting specifications including targeting_automation
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: Confirmation with updated ad set details and a confirmation link

20. `mcp_meta_ads_get_insights`
    - Get performance insights for a campaign, ad set, ad or account
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `object_id`: ID of the campaign, ad set, ad or account
      - `time_range`: Time range for insights (default: maximum)
      - `breakdown`: Optional breakdown dimension (e.g., age, gender, country)
      - `level`: Level of aggregation (ad, adset, campaign, account)
      - `action_attribution_windows` (optional): List of attribution windows for conversion data (e.g., ["1d_click", "1d_view", "7d_click", "7d_view"]). When specified, actions and cost_per_action_type include additional fields for each window. The 'value' field always shows 7d_click attribution.
    - Returns: Performance metrics for the specified object

21. `mcp_meta_ads_get_login_link`
    - Get a clickable login link for Meta Ads authentication
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
    - Returns: A clickable resource link for Meta authentication

22. `mcp_meta_ads_create_budget_schedule`
    - Create a budget schedule for a Meta Ads campaign
    - Inputs:
      - `campaign_id`: Meta Ads campaign ID
      - `budget_value`: Amount of budget increase
      - `budget_value_type`: Type of budget value ("ABSOLUTE" or "MULTIPLIER")
      - `time_start`: Unix timestamp for when the high demand period should start
      - `time_end`: Unix timestamp for when the high demand period should end
      - `access_token` (optional): Meta API access token
    - Returns: JSON string with the ID of the created budget schedule or an error message

23. `mcp_meta_ads_search_interests`
    - Search for interest targeting options by keyword
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `query`: Search term for interests (e.g., "baseball", "cooking", "travel")
      - `limit`: Maximum number of results to return (default: 25)
    - Returns: Interest data with id, name, audience_size, and path fields

24. `mcp_meta_ads_get_interest_suggestions`
    - Get interest suggestions based on existing interests
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `interest_list`: List of interest names to get suggestions for (e.g., ["Basketball", "Soccer"])
      - `limit`: Maximum number of suggestions to return (default: 25)
    - Returns: Suggested interests with id, name, audience_size, and description fields

25. `mcp_meta_ads_validate_interests`
    - Validate interest names or IDs for targeting
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `interest_list`: List of interest names to validate (e.g., ["Japan", "Basketball"])
      - `interest_fbid_list`: List of interest IDs to validate (e.g., ["6003700426513"])
    - Returns: Validation results showing valid status and audience_size for each interest

26. `mcp_meta_ads_search_behaviors`
    - Get all available behavior targeting options
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `limit`: Maximum number of results to return (default: 50)
    - Returns: Behavior targeting options with id, name, audience_size bounds, path, and description

27. `mcp_meta_ads_search_demographics`
    - Get demographic targeting options
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `demographic_class`: Type of demographics ('demographics', 'life_events', 'industries', 'income', 'family_statuses', 'user_device', 'user_os')
      - `limit`: Maximum number of results to return (default: 50)
    - Returns: Demographic targeting options with id, name, audience_size bounds, path, and description

28. `mcp_meta_ads_search_geo_locations`
    - Search for geographic targeting locations
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `query`: Search term for locations (e.g., "New York", "California", "Japan")
      - `location_types`: Types of locations to search (['country', 'region', 'city', 'zip', 'geo_market', 'electoral_district'])
      - `limit`: Maximum number of results to return (default: 25)
    - Returns: Location data with key, name, type, and geographic hierarchy information

29. `mcp_meta_ads_search` (Enhanced)
    - Generic search across accounts, campaigns, ads, and pages
    - Automatically includes page searching when query mentions "page" or "pages"
    - Inputs:
      - `access_token` (optional): Meta API access token (will use cached token if not provided)
      - `query`: Search query string (e.g., "Injury Payouts pages", "active campaigns")
    - Returns: List of matching record IDs in ChatGPT-compatible format

## Licensing

Meta Ads MCP is licensed under the [Business Source License 1.1](LICENSE), which means:

- ✅ **Free to use** for individual and business purposes
- ✅ **Modify and customize** as needed
- ✅ **Redistribute** to others
- ✅ **Becomes fully open source** (Apache 2.0) on January 1, 2029

The only restriction is that you cannot offer this as a competing hosted service. For questions about commercial licensing, please contact us.

## Privacy and Security

Meta Ads MCP follows security best practices with secure token management and automatic authentication handling. 

- **Remote MCP**: All authentication is handled securely in the cloud - no local token storage required
- **Local Installation**: Tokens are cached securely on your local machine

## Testing

### Basic Testing

Test your Meta Ads MCP connection with any MCP client:

1. **Verify Account Access**: Ask your LLM to use `mcp_meta_ads_get_ad_accounts`
2. **Check Account Details**: Use `mcp_meta_ads_get_account_info` with your account ID
3. **List Campaigns**: Try `mcp_meta_ads_get_campaigns` to see your ad campaigns

For detailed local installation testing, see the source repository.

## Troubleshooting

### 💡 Quick Fix: Skip the Technical Setup!

The easiest way to avoid any setup issues is to **[🎯 use our Remote MCP instead](https://pipeboard.co)**. No downloads, no configuration - just connect your ads account and start getting AI insights on your campaigns immediately!

### Local Installation Issues

For local installation issues, refer to the source repository. **For the easiest experience, we recommend using [Remote MCP](https://pipeboard.co) instead.**
