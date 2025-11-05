# Fix Your Tracking - Unified Meta MCP Suite

> Complete AI-powered Meta advertising and tracking infrastructure management

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![MCP Badge](https://lobehub.com/badge/mcp/nictuku-meta-ads-mcp)](https://lobehub.com/mcp/nictuku-meta-ads-mcp)

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) suite for managing all aspects of Meta advertising and tracking through AI. This unified repository provides two complementary MCP servers:

## 🎯 Two MCPs, One Complete Solution

### Meta Ads MCP (Python) - Campaign Management
**Status: ✅ Production Ready**

Manage and optimize your Meta advertising campaigns:
- ✅ 29 working tools for complete campaign lifecycle
- ✅ Ad performance analysis and insights
- ✅ Creative testing and optimization
- ✅ Budget management and recommendations
- ✅ Targeting and audience tools
- ✅ Remote MCP available via [Pipeboard](https://pipeboard.co)

### Gateway MCP (TypeScript) - Infrastructure Management  
**Status: 🚧 In Development**

Manage your Meta tracking infrastructure:
- 📋 CAPI Gateway setup and configuration
- 📋 Signals Gateway pipeline management
- 📋 Event validation and testing
- 📋 Infrastructure monitoring and analytics
- 📋 Health checks and diagnostics

## 🚀 Quick Start

### For Marketers: Use Remote MCP (Recommended)

The fastest way to get started with Meta Ads MCP:

**[Get started with Remote MCP](https://pipeboard.co)** - No technical setup required!

1. Go to [claude.ai/settings/integrations](https://claude.ai/settings/integrations)
2. Add integration URL: `https://mcp.pipeboard.co/meta-ads-mcp`
3. Connect your Meta account and start optimizing!

### For Developers: Local Installation

```bash
# Clone the repository
git clone https://github.com/Organized-AI/fix-your-tracking
cd fix-your-tracking

# Set up Meta Ads MCP (Python)
pip install -e .

# Set up Gateway MCP (TypeScript)
cd gateway_mcp
npm install
npm run build
cd ..
```

## 📋 Configuration

### Claude Desktop Setup

Add both servers to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "python",
      "args": ["-m", "meta_ads_mcp"],
      "env": {
        "META_APP_ID": "your_app_id",
        "META_APP_SECRET": "your_app_secret"
      }
    },
    "meta-gateway": {
      "command": "node",
      "args": ["./gateway_mcp/build/index.js"],
      "env": {
        "META_APP_ID": "your_app_id",
        "META_APP_SECRET": "your_app_secret",
        "META_ACCESS_TOKEN": "your_access_token"
      }
    }
  }
}
```

## 🔍 Use Cases

### Complete Data Audit Workflow

The unified MCPs enable comprehensive audits:

```
1. Infrastructure Check (Gateway MCP)
   • Verify CAPI Gateway configuration
   • Check Signals Gateway pipelines  
   • Validate event tracking setup
   • Review domain routing

2. Campaign Analysis (Meta Ads MCP)
   • Retrieve campaign performance
   • Analyze ad set efficiency
   • Review creative performance
   • Examine targeting settings

3. Unified Recommendations
   • Infrastructure improvements
   • Campaign optimizations
   • Tracking enhancements
   • Complete audit report
```

### Integration Matrix

| Use Case | Meta Ads MCP | Gateway MCP |
|----------|--------------|-------------|
| Campaign analysis | ✅ Primary | - |
| Ad performance | ✅ Primary | - |
| Budget optimization | ✅ Primary | - |
| Creative testing | ✅ Primary | - |
| CAPI Gateway setup | - | 🚧 Primary |
| Event tracking | - | 🚧 Primary |
| Signals Gateway | - | 🚧 Primary |
| Infrastructure audit | Support | 🚧 Primary |
| End-to-end audit | ✅ Required | 🚧 Required |

## 🛠️ Features

### Meta Ads MCP Features (Production)

- **AI-Powered Campaign Analysis**: Let AI analyze campaigns and provide actionable insights
- **Strategic Recommendations**: Data-backed suggestions for optimizing ad spend and targeting
- **Automated Monitoring**: Track performance metrics and alert on significant changes
- **Budget Optimization**: Recommendations for reallocating budget to better-performing ad sets
- **Creative Improvement**: Feedback on ad copy, imagery, and calls-to-action
- **Dynamic Creative Testing**: A/B testing with multiple headlines/descriptions
- **Campaign Management**: Create, update, and manage campaigns, ad sets, and ads
- **Cross-Platform Integration**: Facebook, Instagram, and all Meta ad platforms
- **Universal LLM Support**: Compatible with Claude, ChatGPT, and any MCP client

### Gateway MCP Features (In Development)

- **CAPI Gateway Management**: Create and configure Conversions API Gateways
- **Signals Gateway Integration**: Set up first-party data pipelines
- **Event Management**: Validate, test, and monitor event tracking
- **Gateway Monitoring**: Health checks and performance analytics
- **Domain Routing**: Configure custom domain routing for gateways
- **Multi-Destination Pipelines**: Route events to multiple destinations

## 📚 Documentation

- [Meta Ads MCP Tools Reference](docs/META_ADS_TOOLS.md) - Complete tool documentation
- [Gateway MCP Guide](gateway_mcp/README.md) - Gateway MCP setup and usage
- [Integration Guide](docs/INTEGRATION.md) - Using both MCPs together
- [Data Audit Workflow](docs/DATA_AUDIT.md) - Complete audit procedures
- [Streamable HTTP Setup](STREAMABLE_HTTP_SETUP.md) - HTTP transport configuration

## 👥 Community & Support

- [Discord](https://discord.gg/YzMwQ8zrjr) - Join the community
- [Email Support](mailto:support@organized.ai) - Get help
- [GitHub Issues](https://github.com/Organized-AI/fix-your-tracking/issues) - Report bugs

## 📜 Available Tools

### Meta Ads MCP (29 Tools)

**Account Management**
- `mcp_meta_ads_get_ad_accounts` - List accessible ad accounts
- `mcp_meta_ads_get_account_info` - Get account details
- `mcp_meta_ads_get_account_pages` - List associated pages

**Campaign Management**
- `mcp_meta_ads_get_campaigns` - List campaigns with filtering
- `mcp_meta_ads_get_campaign_details` - Get campaign details
- `mcp_meta_ads_create_campaign` - Create new campaigns
- `mcp_meta_ads_create_budget_schedule` - Schedule budget changes

**Ad Set Management**
- `mcp_meta_ads_get_adsets` - List ad sets
- `mcp_meta_ads_get_adset_details` - Get ad set details
- `mcp_meta_ads_create_adset` - Create new ad sets
- `mcp_meta_ads_update_adset` - Update ad set settings

**Ad Management**
- `mcp_meta_ads_get_ads` - List ads with filtering
- `mcp_meta_ads_get_ad_details` - Get ad details
- `mcp_meta_ads_create_ad` - Create new ads
- `mcp_meta_ads_update_ad` - Update ad settings

**Creative Management**
- `mcp_meta_ads_get_ad_creatives` - Get creative details
- `mcp_meta_ads_create_ad_creative` - Create ad creatives
- `mcp_meta_ads_update_ad_creative` - Update creatives
- `mcp_meta_ads_upload_ad_image` - Upload images
- `mcp_meta_ads_get_ad_image` - Download and visualize images

**Targeting Tools**
- `mcp_meta_ads_search_interests` - Search interest targeting
- `mcp_meta_ads_get_interest_suggestions` - Get interest suggestions
- `mcp_meta_ads_validate_interests` - Validate interests
- `mcp_meta_ads_search_behaviors` - Search behavior targeting
- `mcp_meta_ads_search_demographics` - Search demographics
- `mcp_meta_ads_search_geo_locations` - Search locations

**Analytics & Insights**
- `mcp_meta_ads_get_insights` - Get performance insights

**Utilities**
- `mcp_meta_ads_search` - Generic search across resources
- `mcp_meta_ads_get_login_link` - Get authentication link

### Gateway MCP (Planned Tools)

**Authentication**
- `meta_authenticate` - OAuth flow
- `meta_get_business_accounts` - List businesses
- `meta_get_pixels` - List pixels

**CAPI Gateway**
- `capi_gateway_create` - Create CAPI Gateway
- `capi_gateway_configure` - Configure settings
- `capi_gateway_setup_domain` - Set up custom domain
- `capi_gateway_get_status` - Health check
- `capi_gateway_list` - List gateways

**Signals Gateway**
- `signals_gateway_create_pipeline` - Create pipeline
- `signals_gateway_add_source` - Add data source
- `signals_gateway_add_destination` - Configure destination
- `signals_gateway_set_filters` - Set filters

**Event Management**
- `capi_send_event` - Send test event
- `capi_validate_event` - Validate schema
- `capi_check_deduplication` - Verify dedup

## ⚖️ Licensing

- **Meta Ads MCP**: [Business Source License 1.1](LICENSE) - Free for all use, becomes Apache 2.0 on January 1, 2029
- **Gateway MCP**: [Apache License 2.0](gateway_mcp/LICENSE) - Fully open source

The only BSL restriction: Cannot offer Meta Ads MCP as a competing hosted service.

## 🔒 Privacy and Security

- **Remote MCP**: Cloud-based authentication, no local token storage
- **Local Installation**: Secure token caching on your machine
- **OAuth Flow**: Industry-standard authentication
- **No Data Storage**: Your data stays with Meta and your local environment

## ✅ Testing

### Meta Ads MCP

```bash
# Test account access
python -m meta_ads_mcp
# Ask AI: "List my Meta ad accounts"

# Test campaign retrieval
# Ask AI: "Show me my active campaigns"

# Test insights
# Ask AI: "Get performance insights for campaign X"
```

### Gateway MCP

```bash
# Build and test
cd gateway_mcp
npm test
npm run build
node build/index.js
```

## 🛣️ Roadmap

### V2.0 - Current (Meta Ads MCP Production)
- ✅ Complete Meta Ads API integration
- ✅ 29 working campaign management tools
- ✅ Remote MCP via Pipeboard
- ✅ Gateway MCP foundation established

### V2.1 - Q1 2026
- 🚧 Gateway MCP authentication
- 🚧 Basic CAPI Gateway tools
- 🚧 Event validation
- 📋 Integration documentation

### V2.5 - Q2 2026  
- 📋 Complete CAPI Gateway management
- 📋 Signals Gateway support
- 📋 Infrastructure monitoring
- 📋 Data audit skill integration

### V3.0 - Q3 2026
- 📋 Automated optimization
- 📋 Predictive diagnostics
- 📋 Multi-account management
- 📋 Advanced analytics

## 🐛 Troubleshooting

### Meta Ads MCP Issues

**Quick Fix**: Use [Remote MCP](https://pipeboard.co) to avoid setup complexity!

**Common Issues**:
- Token expiration: Reauthenticate through `mcp_meta_ads_get_login_link`
- Permission errors: Check Meta Business Manager permissions
- Rate limiting: Tools automatically handle API limits

### Gateway MCP Issues

**Development Stage**: Gateway MCP is under active development. Current builds provide:
- Server scaffolding
- Tool structure
- Type definitions

Full functionality coming in Q1-Q2 2026.

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas of focus:
- Gateway MCP tool implementation
- Documentation improvements
- Test coverage
- Example workflows

## 📌 Related Projects

- [Pipeboard](https://pipeboard.co) - Remote MCP hosting for Meta Ads
- [Stape](https://stape.io) - Server-side tagging platform
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

## 🚀 Migration from v1

Existing Meta Ads MCP users: No changes required! The consolidation:
- ✅ Maintains full backward compatibility
- ✅ Adds Gateway MCP as optional component
- ✅ No breaking changes to existing tools
- ✅ Remote MCP unaffected

---

**Disclaimer**: This is an unofficial third-party tool not associated with, endorsed by, or affiliated with Meta. Meta, Facebook, Instagram, and related brand names are trademarks of their respective owners.

Made with ❤️ by [Organized AI](https://organized.ai)
