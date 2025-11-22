# Google Ads Wizard - MCP Server Migration Plan

## Overview

The Google Ads Wizard CLI can be easily converted to an MCP (Model Context Protocol) server, allowing Claude Desktop to directly access Google Ads data.

## Why CLI First?

✅ **Works immediately** - No MCP token approval needed
✅ **Faster development** - No Claude restarts for changes
✅ **Standard debugging** - Use normal Node.js tools
✅ **Proven architecture** - Test everything before MCP conversion

## MCP Benefits (Future)

🚀 **Direct Claude Access** - Claude can call tools directly
🚀 **Better Context** - Real-time data in conversations
🚀 **Seamless Integration** - Works alongside Pipeboard Meta MCP
🚀 **Cross-Platform Analysis** - Compare Google Ads + Meta Ads in one conversation

---

## Architecture Comparison

### Current CLI Architecture
```
User → Terminal → CLI Commands → Google Ads API → Claude API → PDF/JSON
```

### Future MCP Architecture
```
User → Claude Desktop → MCP Server → Google Ads API
                              ↓
                         Claude (built-in) → Response
```

---

## MCP Server Structure

```
google-ads-wizard/
├── src/
│   ├── mcp/
│   │   ├── server.ts           # MCP server entry point
│   │   ├── tools.ts            # Tool definitions
│   │   └── handlers.ts         # Tool handlers
│   ├── api/
│   │   └── google-ads-client.ts  # ✅ Already built (reuse)
│   ├── analysis/
│   │   └── claude-client.ts      # ✅ Already built (adapt)
│   └── generators/
│       └── pdf-report.ts         # ✅ Already built (reuse)
└── claude_desktop_config.json  # MCP configuration
```

---

## MCP Tools to Expose

### 1. `google_ads_get_account_info`
Get account details
```json
{
  "name": "google_ads_get_account_info",
  "description": "Get Google Ads account information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "customer_id": {
        "type": "string",
        "description": "Google Ads customer ID"
      }
    },
    "required": ["customer_id"]
  }
}
```

### 2. `google_ads_list_campaigns`
List campaigns with performance
```json
{
  "name": "google_ads_list_campaigns",
  "description": "List campaigns with performance metrics",
  "inputSchema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"},
      "status": {"type": "string", "enum": ["active", "paused", "all"]}
    }
  }
}
```

### 3. `google_ads_get_performance`
Get performance metrics
```json
{
  "name": "google_ads_get_performance",
  "description": "Get account performance metrics for last 30 days",
  "inputSchema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"}
    }
  }
}
```

### 4. `google_ads_get_keywords`
Get keyword performance
```json
{
  "name": "google_ads_get_keywords",
  "description": "Get keyword performance data",
  "inputSchema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"},
      "limit": {"type": "number", "default": 100}
    }
  }
}
```

### 5. `google_ads_audit`
Run comprehensive audit (uses Claude internally)
```json
{
  "name": "google_ads_audit",
  "description": "Run comprehensive RTT-style audit",
  "inputSchema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"},
      "output_format": {"type": "string", "enum": ["json", "pdf"]}
    }
  }
}
```

---

## Implementation Steps

### Step 1: Create MCP Server Entry Point

**File:** `src/mcp/server.ts`

```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { tools } from './tools.js';
import { handleToolCall } from './handlers.js';

const server = new Server(
  {
    name: 'google-ads-wizard',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  return await handleToolCall(request);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Google Ads Wizard MCP server running on stdio');
}

main().catch(console.error);
```

### Step 2: Define Tools

**File:** `src/mcp/tools.ts`

```typescript
export const tools = [
  {
    name: 'google_ads_get_account_info',
    description: 'Get Google Ads account information including name, currency, status',
    inputSchema: {
      type: 'object',
      properties: {
        customer_id: {
          type: 'string',
          description: 'Google Ads customer ID (e.g., 8888034950)',
        },
      },
      required: ['customer_id'],
    },
  },
  {
    name: 'google_ads_list_campaigns',
    description: 'List campaigns with performance metrics (last 30 days)',
    inputSchema: {
      type: 'object',
      properties: {
        customer_id: { type: 'string' },
        status: {
          type: 'string',
          enum: ['active', 'paused', 'all'],
          default: 'all',
        },
      },
      required: ['customer_id'],
    },
  },
  {
    name: 'google_ads_get_performance',
    description: 'Get overall account performance metrics',
    inputSchema: {
      type: 'object',
      properties: {
        customer_id: { type: 'string' },
      },
      required: ['customer_id'],
    },
  },
  {
    name: 'google_ads_get_keywords',
    description: 'Get keyword performance data with quality scores',
    inputSchema: {
      type: 'object',
      properties: {
        customer_id: { type: 'string' },
        limit: { type: 'number', default: 100 },
      },
      required: ['customer_id'],
    },
  },
  {
    name: 'google_ads_audit',
    description: 'Run comprehensive RTT-style audit analysis',
    inputSchema: {
      type: 'object',
      properties: {
        customer_id: { type: 'string' },
      },
      required: ['customer_id'],
    },
  },
];
```

### Step 3: Implement Handlers

**File:** `src/mcp/handlers.ts`

```typescript
import { createGoogleAdsClient } from '../api/google-ads-client.js';
import { analyzeAccount } from '../analysis/claude-client.js';

export async function handleToolCall(request: any) {
  const { name, arguments: args } = request.params;

  try {
    const client = createGoogleAdsClient();

    switch (name) {
      case 'google_ads_get_account_info':
        const accountInfo = await client.getAccountInfo(args.customer_id);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(accountInfo, null, 2),
            },
          ],
        };

      case 'google_ads_list_campaigns':
        const campaigns = await client.getCampaigns(args.customer_id);
        const filtered = args.status === 'all' ? campaigns :
          campaigns.filter((c: any) =>
            args.status === 'active' ? c.campaign?.status === 'ENABLED' :
            c.campaign?.status === 'PAUSED'
          );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(filtered, null, 2),
            },
          ],
        };

      case 'google_ads_get_performance':
        const performance = await client.getPerformanceMetrics(args.customer_id);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(performance, null, 2),
            },
          ],
        };

      case 'google_ads_get_keywords':
        const keywords = await client.getKeywordPerformance(args.customer_id);
        const limited = keywords.slice(0, args.limit || 100);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(limited, null, 2),
            },
          ],
        };

      case 'google_ads_audit':
        const [info, camps, perf, keys, conv] = await Promise.all([
          client.getAccountInfo(args.customer_id),
          client.getCampaigns(args.customer_id),
          client.getPerformanceMetrics(args.customer_id),
          client.getKeywordPerformance(args.customer_id),
          client.getConversionTracking(args.customer_id),
        ]);

        const analysis = await analyzeAccount({
          accountInfo: info,
          campaigns: camps,
          performance: perf,
          keywords: keys,
          conversions: conv,
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(analysis, null, 2),
            },
          ],
        };

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
}
```

### Step 4: Update package.json

```json
{
  "scripts": {
    "mcp": "tsx src/mcp/server.ts"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  }
}
```

### Step 5: Claude Desktop Configuration

**File:** `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-ads-wizard": {
      "command": "node",
      "args": [
        "/Users/jordaaan/Library/Mobile Documents/com~apple~CloudDocs/BHT Promo iCloud/Organized AI/Windsurf/Fix Your Tracking/fix-your-tracking/google-ads-wizard/google-ads-wizard/dist/mcp/server.js"
      ],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "hAZxzK3EmeT4ZrZixdGUgQ",
        "GOOGLE_ADS_CLIENT_ID": "your_client_id.apps.googleusercontent.com",
        "GOOGLE_ADS_CLIENT_SECRET": "GOCSPX-your_client_secret",
        "GOOGLE_ADS_REFRESH_TOKEN": "1//04fdR_lZO_V4oCgYIARAAGAQSNwF-L9Ir...",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "4761832056",
        "ANTHROPIC_API_KEY": "sk-ant-api03-..."
      }
    }
  }
}
```

---

## Testing MCP Server

### Test 1: Build and Run
```bash
npm run build
npm run mcp
```

### Test 2: Use with Claude Desktop

In Claude Desktop, you can say:
```
Use google_ads_get_account_info for customer 8888034950
```

Claude will:
1. Call the MCP tool
2. Get the account data
3. Analyze and respond

---

## Benefits of MCP vs CLI

| Feature | CLI | MCP |
|---------|-----|-----|
| Setup Time | ✅ Immediate | ⏳ Requires config |
| Claude Integration | ❌ Manual copy/paste | ✅ Automatic |
| Debugging | ✅ Easy | ⚠️ Harder |
| Iteration Speed | ✅ Fast | ⚠️ Slower (restart needed) |
| User Experience | ⚠️ Terminal | ✅ Chat interface |
| Cross-Platform | ❌ Separate tools | ✅ Unified (with Meta MCP) |

---

## When to Migrate to MCP

Migrate when:
1. ✅ CLI is fully tested and working
2. ✅ All bugs are fixed
3. ✅ You want Claude Desktop integration
4. ✅ You want to combine with Pipeboard Meta MCP

---

## Dual Mode Support

Best approach: **Support both CLI and MCP**

```
google-ads-wizard/
├── src/
│   ├── index.ts          # CLI entry (keep for debugging)
│   ├── mcp/
│   │   └── server.ts     # MCP entry (for Claude Desktop)
│   └── shared/           # Shared code (both use)
```

Benefits:
- CLI for development and debugging
- MCP for production Claude Desktop use
- Same underlying code
- Best of both worlds

---

## Next Steps

1. **Finish CLI** - Get refresh token, test audit
2. **Verify Everything Works** - Run multiple audits
3. **Install MCP SDK** - `npm install @modelcontextprotocol/sdk`
4. **Create MCP Server** - Follow steps above
5. **Test Locally** - Run MCP server standalone
6. **Configure Claude Desktop** - Add to MCP config
7. **Test Integration** - Use from Claude Desktop

---

## Current Status

✅ CLI fully built and ready
✅ All core functionality tested
✅ Architecture ready for MCP
⏳ Waiting for refresh token to test
⏳ MCP server implementation pending

**Recommendation:** Get the CLI working first (just need refresh token), then migrate to MCP.

---

Ready to migrate to MCP? Let me know and I'll implement the MCP server!
