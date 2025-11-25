# Fix Your Tracking - Unified Meta MCP Platform

> Complete Meta advertising and tracking infrastructure management through AI

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](https://www.typescriptlang.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green)](https://modelcontextprotocol.io/)

## 🎯 Overview

Fix Your Tracking is a unified repository providing comprehensive advertising platform integration through MCP servers and CLI tools:

### 🎨 **Meta Ads MCP** (Python)
Campaign management, ad performance analysis, and creative optimization

### 🏭️ **Gateway MCP** (TypeScript)
CAPI Gateway, Signals Gateway, and tracking infrastructure management

### 🔧 **Google Ads MCP & CLI** (Python/TypeScript)
Google Ads campaign management, auditing, and AI-powered optimization

### 🛠️ **Platform CLI Tools** (TypeScript)
Direct API access for GoHighLevel, TripleWhale, and cross-platform data synchronization

Together, these tools enable comprehensive data audit workflows across Meta, Google, and CRM platforms - from analyzing ad performance to validating tracking infrastructure and syncing attribution data.

> **DISCLAIMER:** This is an unofficial third-party tool and is not associated with, endorsed by, or affiliated with Meta in any way.

## 🚀 Quick Start

### Option 1: Remote MCP (Recommended - No Setup Required)

**[Get started with Pipeboard Remote MCP](https://pipeboard.co)** - Just connect your Meta account and start using AI to manage your campaigns and tracking. No installation needed!

### Option 2: Local Installation (Advanced Users)

```bash
# Clone the repository
git clone https://github.com/Organized-AI/fix-your-tracking
cd fix-your-tracking

# Install Meta Ads MCP (Python)
pip install -e .

# Install Gateway MCP (TypeScript)
cd gateway_mcp
npm install && npm run build
```

## 📋 Features Comparison

| Feature | Meta Ads MCP | Gateway MCP |
|---------|--------------|-------------|
| **Campaign Management** | ✅ Primary | - |
| **Ad Performance Analysis** | ✅ Primary | - |
| **Budget Optimization** | ✅ Primary | - |
| **Creative Testing** | ✅ Primary | - |
| **Targeting Management** | ✅ Primary | - |
| **CAPI Gateway Setup** | - | ✅ Primary |
| **Signals Gateway** | - | ✅ Primary |
| **Event Validation** | - | ✅ Primary |
| **Tracking Infrastructure** | Support | ✅ Primary |
| **Complete Data Audits** | ✅ Required | ✅ Required |

## 🛠️ CLI Tools

### **ghl-cli** - GoHighLevel Management
Command-line tool for managing GoHighLevel contacts and opportunities.

```bash
cd ghl-cli
npm install
npm run dev setup  # Check configuration

# List and export contacts
npm run dev contacts list --location-id <location_id>
npm run dev contacts list --export contacts.json

# Manage opportunities
npm run dev opportunities list --pipeline-id <pipeline_id>
npm run dev opportunities list --status won --export won_deals.json
```

**Features:**
- List/export contacts with filtering by tags and status
- Opportunity management by pipeline and status
- Rate limiting (100 req/10s)
- JSON export format
- Beautiful terminal output

**Setup:** See [ghl-cli/README.md](ghl-cli/README.md)

### **triplewhale-cli** - TripleWhale Attribution
Push offline events and view attribution metrics for e-commerce analytics.

```bash
cd triplewhale-cli
npm install

# Push single event
npm run dev push-event --shop <shop_id> --event <event_type> --value <value>

# Push batch events from JSON
npm run dev push-events --file events.json
```

**Features:**
- Push offline conversion events
- View attribution metrics
- Batch event processing
- E-commerce analytics integration

### **ghl-tw-sync** - Data Synchronization
Automated sync tool to push GoHighLevel data to TripleWhale attribution dashboard.

```bash
cd ghl-tw-sync
npm install

# Test connection
npm run dev test

# Sync opportunities to TripleWhale
npm run dev sync --days 30

# Import from CSV
npm run dev import-csv --file opportunities.csv
```

**Features:**
- Automated GHL → TripleWhale sync
- Transform GHL opportunities to TW attribution events
- CSV import support
- Progress tracking and error handling
- Configurable sync intervals

**Setup & Documentation:** See [ghl-tw-sync/TRIPLEWHALE_DATA_IN_DOCS.md](ghl-tw-sync/TRIPLEWHALE_DATA_IN_DOCS.md)

### **google-ads-wizard** - Google Ads CLI
AI-powered Google Ads campaign auditing and management.

```bash
cd google-ads-wizard/google-ads-wizard
npm install

# List campaigns
npm run dev campaigns list

# Run AI-powered audit
npm run dev audit --account-id <account_id> --output report.pdf
```

**Features:**
- Campaign listing with performance metrics
- AI-powered audits using Claude Sonnet 4
- PDF and JSON report generation
- RTT methodology (Tracking, Targeting, Testing)
- Auto-generated .cursor/rules AI context

**Documentation:** See [google-ads-wizard/google-ads-wizard/README.md](google-ads-wizard/google-ads-wizard/README.md)

## 🔧 Configuration

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
    "gateway-mcp": {
      "command": "node",
      "args": ["/path/to/fix-your-tracking/gateway_mcp/build/index.js"],
      "env": {
        "META_APP_ID": "your_app_id",
        "META_APP_SECRET": "your_app_secret",
        "META_ACCESS_TOKEN": "your_access_token"
      }
    }
  }
}
```

### Remote MCP Configuration (Easiest)

For Claude Pro/Max users:

1. Go to [claude.ai/settings/integrations](https://claude.ai/settings/integrations)
2. Add integration: `https://mcp.pipeboard.co/meta-ads-mcp`
3. Follow OAuth flow to connect your Meta account

See [Integration Guide](docs/INTEGRATION_GUIDE.md) for detailed setup instructions.

## 📚 Documentation

### MCP Servers
- **[Integration Guide](docs/INTEGRATION.md)** - Complete setup and configuration
- **[Data Audit Workflow](docs/DATA_AUDIT.md)** - End-to-end audit examples
- **[Meta Ads Tools Reference](META_API_NOTES.md)** - Complete tool reference (29 tools)
- **[Streamable HTTP Setup](STREAMABLE_HTTP_SETUP.md)** - Advanced HTTP transport

### CLI Tools
- **[ghl-cli Documentation](ghl-cli/README.md)** - GoHighLevel CLI setup and usage
- **[triplewhale-cli Documentation](triplewhale-cli/)** - TripleWhale event pushing
- **[ghl-tw-sync Documentation](ghl-tw-sync/TRIPLEWHALE_DATA_IN_DOCS.md)** - Sync setup guide
- **[google-ads-wizard Documentation](google-ads-wizard/google-ads-wizard/README.md)** - Google Ads CLI guide
- **[Google Ads API Reference](docs/google_ads/)** - GAQL queries and best practices

## 🎯 Use Cases

### Campaign Performance Analysis
```
"Analyze my Meta ad campaigns from the last 30 days and identify the top 3 performers by ROAS"
```

### Tracking Infrastructure Audit
```
"Audit my Meta tracking setup including CAPI Gateway configuration and Pixel events"
```

### Budget Optimization
```
"Review my campaign spend and suggest budget reallocations to improve overall ROAS"
```

### Creative Performance Testing
```
"Show me the creative performance for campaign X and suggest improvements for underperforming ads"
```

### CRM Data Export (CLI)
```bash
# Export all won opportunities from GoHighLevel
ghl-cli opportunities list --status won --export won_deals.json
```

### Attribution Tracking (CLI)
```bash
# Push offline conversion events to TripleWhale
triplewhale-cli push-events --file offline_conversions.json
```

### Cross-Platform Sync (CLI)
```bash
# Sync 30 days of GHL opportunities to TripleWhale attribution
ghl-tw-sync sync --days 30
```

### Google Ads Audit (CLI)
```bash
# Run AI-powered audit of Google Ads account
google-ads-wizard audit --account-id 123456789 --output audit-report.pdf
```

## 🏭️ Repository Structure

```
fix-your-tracking/
├── meta_ads_mcp/           # Python - Meta Campaign Management (Production)
│   ├── core/               # Core API client and auth
│   ├── __init__.py
│   └── __main__.py
├── gateway_mcp/            # TypeScript - Meta Infrastructure (In Development)
│   ├── src/
│   │   ├── tools/          # Gateway management tools
│   │   ├── api/            # Meta API clients
│   │   └── utils/          # Utilities and helpers
│   ├── package.json
│   └── tsconfig.json
├── google_ads_mcp/         # Python - Google Ads MCP Server
│   ├── core/               # Google Ads API client
│   ├── __init__.py
│   └── server.py
├── google-ads-wizard/      # TypeScript - Google Ads CLI & Wizard
│   ├── google-ads-wizard/  # Main CLI application
│   │   ├── src/            # Analysis, API, generators, integrations
│   │   ├── dist/           # Compiled output
│   │   └── README.md       # Setup and usage guide
│   └── src/                # CLI wrapper
├── ghl-cli/                # TypeScript - GoHighLevel CLI
│   ├── src/
│   │   ├── api/            # GHL API client
│   │   ├── commands/       # Contacts & opportunities commands
│   │   ├── types/          # TypeScript definitions
│   │   └── utils/          # Export & formatting utilities
│   ├── package.json
│   └── README.md           # Complete usage guide
├── triplewhale-cli/        # TypeScript - TripleWhale CLI
│   ├── src/
│   │   ├── api/            # TripleWhale API client
│   │   ├── commands/       # Event push commands
│   │   ├── types/          # TypeScript definitions
│   │   └── utils/          # File reader utilities
│   └── package.json
├── ghl-tw-sync/            # TypeScript - GHL to TripleWhale Sync
│   ├── src/
│   │   ├── ghl-api/        # GoHighLevel API client
│   │   ├── tw-api/         # TripleWhale API client
│   │   ├── sync/           # Sync engine
│   │   ├── transform/      # GHL to TW data transformation
│   │   ├── commands/       # Sync, test, import commands
│   │   └── types/          # Shared type definitions
│   ├── package.json
│   └── TRIPLEWHALE_DATA_IN_DOCS.md
├── docs/                   # Comprehensive documentation
│   ├── INTEGRATION.md      # Integration guide
│   ├── DATA_AUDIT.md       # Data audit workflows
│   └── google_ads/         # Google Ads documentation
├── tests/                  # Test suite (40+ tests)
├── examples/               # Usage examples
├── README.md               # This file
├── pyproject.toml          # Python dependencies
└── package.json            # Root package management
```

## 🤝 Integration with Data Audit Skill

Designed to work with the [data-audit skill](https://github.com/Organized-AI/data-audit-skill):

```markdown
### Complete Meta Audit Workflow

1. **Account Discovery** (Meta Ads MCP)
   - Retrieve all ad accounts, campaigns, ad sets, and ads
   
2. **Performance Analysis** (Meta Ads MCP)
   - Analyze metrics, identify optimization opportunities

3. **Infrastructure Check** (Gateway MCP)
   - Verify CAPI Gateway, validate Signals Gateway, check event tracking

4. **Recommendations** (Both MCPs)
   - Campaign optimizations, tracking improvements, infrastructure updates
```

## 🔐 Security & Privacy

- **Secure Authentication**: OAuth 2.0 flow for Meta API access
- **Token Management**: Automatic token refresh and secure storage
- **No Data Storage**: All operations are real-time API calls
- **Audit Logging**: Track all changes and API interactions

## 📄 Licensing

### Meta Ads MCP
Licensed under [Business Source License 1.1](LICENSE) - Free to use with source-available code. Converts to Apache 2.0 on January 1, 2029.

### Gateway MCP  
Licensed under [Apache License 2.0](gateway_mcp/LICENSE) - Fully open source.

## 🛠️ Development

### Meta Ads MCP (Python)
```bash
pip install -e .
pytest
black meta_ads_mcp/
```

### Gateway MCP (TypeScript)
```bash
cd gateway_mcp
npm install
npm run build
npm run dev
npm test
```

## 🌟 Community & Support

- **Discord**: [Join our community](https://discord.gg/YzMwQ8zrjr)
- **Email**: info@pipeboard.co
- **Issues**: [GitHub Issues](https://github.com/Organized-AI/fix-your-tracking/issues)
- **Documentation**: [Full docs](https://pipeboard.co/docs)

## 🚦 Roadmap

### Current Status
- ✅ Meta Ads MCP - Production Ready (29 tools)
- ✅ Google Ads MCP - Production Ready
- ✅ Google Ads Wizard CLI - Production Ready
- ✅ GoHighLevel CLI - Production Ready
- ✅ TripleWhale CLI - Production Ready
- ✅ GHL-TW Sync Tool - Production Ready
- 🚧 Gateway MCP - In Development (Foundation complete)

### Upcoming Features

**Gateway MCP V1.0**
- [ ] Complete CAPI Gateway management
- [ ] Signals Gateway pipeline configuration
- [ ] Event validation and testing
- [ ] Gateway health monitoring

**Gateway MCP V2.0**
- [ ] Automated optimization recommendations
- [ ] Predictive diagnostics
- [ ] Multi-account management
- [ ] Advanced analytics

**CLI Tools Enhancements**
- [ ] Interactive setup wizards for all CLI tools
- [ ] Automated scheduling for ghl-tw-sync
- [ ] Real-time sync monitoring dashboard
- [ ] Bulk operations and batch processing
- [ ] Enhanced error reporting and retry logic

**Integration Enhancements**
- [ ] Unified authentication flow across all tools
- [ ] Cross-platform workflow automation
- [ ] Enhanced audit reporting with multi-platform support
- [ ] Real-time monitoring dashboards
- [ ] Webhook support for event-driven automation

## 🙏 Acknowledgments

- Inspired by the needs of digital marketers and data analysts
- Built on [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by Meta Marketing API
- Community-driven development

## 📝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development workflow
- Testing requirements
- Pull request process

## ⭐ Show Your Support

If you find this project helpful:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🤝 Contribute code

---

Made with ❤️ by [Organized AI](https://organized.ai)

**Related Projects:**
- [Data Audit Skill](https://github.com/Organized-AI/data-audit-skill)
- [Pipeboard](https://pipeboard.co)
