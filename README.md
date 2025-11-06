# Fix Your Tracking - Unified Meta MCP Platform

> Complete Meta advertising and tracking infrastructure management through AI

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](https://www.typescriptlang.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green)](https://modelcontextprotocol.io/)

## 🎯 Overview

Fix Your Tracking is a unified repository providing two complementary Model Context Protocol (MCP) servers that enable complete control over Meta's advertising and tracking infrastructure:

### 🎨 **Meta Ads MCP** (Python)
Campaign management, ad performance analysis, and creative optimization

### 🏭️ **Gateway MCP** (TypeScript)  
CAPI Gateway, Signals Gateway, and tracking infrastructure management

Together, these MCPs enable comprehensive data audit workflows, from analyzing ad performance to validating tracking infrastructure.

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

- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - Complete setup and configuration
- **[Data Audit Workflow](docs/DATA_AUDIT_WORKFLOW.md)** - End-to-end audit examples
- **[Meta Ads Tools Reference](META_API_NOTES.md)** - Complete tool reference (29 tools)
- **[Streamable HTTP Setup](STREAMABLE_HTTP_SETUP.md)** - Advanced HTTP transport

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

## 🏭️ Repository Structure

```
fix-your-tracking/
├── meta_ads_mcp/           # Python - Campaign Management (Production)
│   ├── core/               # Core API client and auth
│   ├── __init__.py
│   └── __main__.py
├── gateway_mcp/            # TypeScript - Infrastructure (In Development)
│   ├── src/
│   │   ├── tools/          # Gateway management tools
│   │   ├── api/            # Meta API clients
│   │   └── utils/          # Utilities and helpers
│   ├── package.json
│   └── tsconfig.json
├── docs/                   # Comprehensive documentation
│   ├── INTEGRATION_GUIDE.md
│   └── DATA_AUDIT_WORKFLOW.md
├── README.md              # This file
├── pyproject.toml         # Python dependencies
└── package.json           # Root package management
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

**Integration Enhancements**
- [ ] Unified authentication flow
- [ ] Cross-MCP workflow automation
- [ ] Enhanced audit reporting
- [ ] Real-time monitoring dashboards

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
