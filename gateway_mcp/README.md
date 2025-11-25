# Gateway MCP - Meta Infrastructure Management

> Programmatically manage Meta CAPI Gateway and Signals Gateway infrastructure through AI

This is the Gateway MCP component of the Fix Your Tracking unified repository. It provides tools for managing Meta's tracking infrastructure:

- **CAPI Gateway**: Set up and manage Conversions API Gateways
- **Signals Gateway**: Configure first-party data pipelines
- **Event Management**: Validate, test, and monitor event tracking
- **Gateway Monitoring**: Health checks and performance analytics

## Quick Start

```bash
# Install dependencies
cd gateway_mcp
npm install

# Build
npm run build

# Run in development
npm run dev
```

## Integration

This Gateway MCP works alongside the Meta Ads MCP to provide complete tracking infrastructure management. See the main [repository README](../README.md) for full integration details.

## Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
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

## Development Status

- ✅ Project structure established
- 🚧 Authentication implementation in progress
- 📋 CAPI Gateway tools planned
- 📋 Signals Gateway tools planned
- 📋 Event management tools planned
- 📋 Monitoring tools planned

## Documentation

See the main repository [docs/](../docs/) directory for comprehensive documentation on using both MCPs together.
