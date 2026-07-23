# Streamable HTTP Transport Setup

## Overview

Meta Ads MCP supports **Streamable HTTP Transport**, which allows you to run the server as a standalone HTTP API. This enables direct integration with web applications, custom dashboards, and any system that can make HTTP requests.

## Quick Start

### 1. Start the HTTP Server

```bash
# Basic HTTP server (default: localhost:8080)
python -m meta_ads_mcp --transport streamable-http

# Custom host and port
python -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port 9000
```

### 2. Set Authentication

Set your Pipeboard token as an environment variable. This is optional for HTTP transport if you provide the token in the header, but it can be useful for command-line use.

```bash
export PIPEBOARD_API_TOKEN=your_pipeboard_token
```

### 3. Make HTTP Requests

The server accepts JSON-RPC 2.0 requests at the `/mcp` endpoint. Use the `Authorization` header to provide your token.

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your_pipeboard_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "get_ad_accounts",
      "arguments": {"limit": 5}
    }
  }'
```

## Configuration Options

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--transport` | Transport mode | `stdio` |
| `--host` | Server host address | `localhost` |
| `--port` | Server port | `8080` |
| `--sse-response` | Return responses as SSE streams instead of JSON | `false` (JSON) |

### Examples

```bash
# Local development server
python -m meta_ads_mcp --transport streamable-http --host localhost --port 8080

# Production server (accessible externally)
python -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port 8080

# Custom port
python -m meta_ads_mcp --transport streamable-http --port 9000
```

## Security Model (read before exposing the port)

The HTTP transport uses a **per-request** authentication model that is
deliberately different from stdio. Understanding it is the difference between a
safe deployment and leaking your Meta account to the internet.

- **stdio (local):** the server acts as whatever credential is configured in its
  environment — `META_ACCESS_TOKEN`, `PIPEBOARD_API_TOKEN`, or a stored login.
  Only the local process that launched it can talk to it, so this is expected
  and safe. *If all you want is to use the MCP locally, prefer stdio.*

- **streamable-http (network):** every request must carry **its own** token
  header — `Authorization: Bearer <token>`, `X-META-ACCESS-TOKEN`, or the legacy
  `X-PIPEBOARD-API-TOKEN`. Requests without one are rejected with
  `401 Unauthorized`. The server-side `META_ACCESS_TOKEN` environment variable is
  **intentionally not** used as an implicit fallback for HTTP requests — if it
  were, any caller who can reach the port would act as you. This gating is
  enforced by `AuthInjectionMiddleware`.

**Operational rules:**

1. **Do not expose the raw port to an untrusted network.** `--host 0.0.0.0`
   binds to every interface. Put the server behind an authenticating reverse
   proxy (or a private network / firewall), exactly as the hosted MCP at
   `*.mcp.pipeboard.co` does (localhost-bound Python process behind a proxy).
2. **Avoid setting `META_ACCESS_TOKEN` on a network-exposed HTTP server.** It is
   an operator-wide, long-lived credential. Have callers pass their own tokens
   in headers instead. If you must set it (e.g. single-tenant behind a trusted
   proxy), ensure the port is unreachable by untrusted callers.
3. **The auth gate applies in both response modes** — default JSON and
   `--sse-response`. (Historically `--sse-response` had a bug where the gate was
   not attached to the served app; see `SECURITY.md`, GHSA-8353-5qhw-8hfw. Fixed
   in `1.0.119` — upgrade if you use `--sse-response`.)
4. **If you ever exposed an unauthenticated server, rotate the Meta access
   token** and review Graph API access logs.

## Authentication

### Primary Method: Bearer Token (Recommended)

1. Sign up at [Pipeboard.co](https://pipeboard.co)
2. Generate an API token at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)
3. Include the token in the `Authorization` HTTP header:

```bash
curl -H "Authorization: Bearer your_pipeboard_token" \
     -X POST http://localhost:8080/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

#### Remote MCP: Token in URL

When using the hosted Remote MCP at `https://mcp.pipeboard.co/meta-ads-mcp`, you can alternatively authenticate by including the token as a URL parameter:

```
https://mcp.pipeboard.co/meta-ads-mcp?token=YOUR_PIPEBOARD_TOKEN
```

This is particularly useful for MCP clients that don't support interactive authentication flows.

### Alternative Method: Direct Meta Token

If you have a Meta Developer App, you can use a direct access token via the `X-META-ACCESS-TOKEN` header. This is less common.

```bash
curl -H "X-META-ACCESS-TOKEN: your_meta_access_token" \
     -X POST http://localhost:8080/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Available Endpoints

### Server URL Structure

**Base URL**: `http://localhost:8080`  
**MCP Endpoint**: `/mcp`

### MCP Protocol Methods

| Method | Description |
|--------|-------------|
| `initialize` | Initialize MCP session and exchange capabilities |
| `tools/list` | Get list of all available Meta Ads tools |
| `tools/call` | Execute a specific tool with parameters |

### Response Format

All responses follow JSON-RPC 2.0 format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    // Tool response data
  }
}
```

## Example Usage

### 1. Initialize Session

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {"roots": {"listChanged": true}},
      "clientInfo": {"name": "my-app", "version": "1.0.0"}
    }
  }'
```

### 2. List Available Tools

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 2
  }'
```

### 3. Get Ad Accounts

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 3,
    "params": {
      "name": "get_ad_accounts",
      "arguments": {"limit": 10}
    }
  }'
```

### 4. Get Campaign Performance

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 4,
    "params": {
      "name": "get_insights",
      "arguments": {
        "object_id": "act_701351919139047",
        "time_range": "last_30d",
        "level": "campaign"
      }
    }
  }'
```

## Client Examples

### Python Client

```python
import requests
import json

class MetaAdsMCPClient:
    def __init__(self, base_url="http://localhost:8080", token=None):
        self.base_url = base_url
        self.endpoint = f"{base_url}/mcp"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def call_tool(self, tool_name, arguments=None):
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {"name": tool_name}
        }
        if arguments:
            payload["params"]["arguments"] = arguments
        
        response = requests.post(self.endpoint, headers=self.headers, json=payload)
        return response.json()

# Usage
client = MetaAdsMCPClient(token="your_pipeboard_token")
result = client.call_tool("get_ad_accounts", {"limit": 5})
print(json.dumps(result, indent=2))
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class MetaAdsMCPClient {
    constructor(baseUrl = 'http://localhost:8080', token = null) {
        this.baseUrl = baseUrl;
        this.endpoint = `${baseUrl}/mcp`;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        };
        if (token) {
            this.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    async callTool(toolName, arguments = null) {
        const payload = {
            jsonrpc: '2.0',
            method: 'tools/call',
            id: 1,
            params: { name: toolName }
        };
        if (arguments) {
            payload.params.arguments = arguments;
        }

        try {
            const response = await axios.post(this.endpoint, payload, { headers: this.headers });
            return response.data;
        } catch (error) {
            return { error: error.message };
        }
    }
}

// Usage
const client = new MetaAdsMCPClient('http://localhost:8080', 'your_pipeboard_token');
client.callTool('get_ad_accounts', { limit: 5 })
    .then(result => console.log(JSON.stringify(result, null, 2)));
```

## Production Deployment

### Security Considerations

See **[Security Model](#security-model-read-before-exposing-the-port)** above for
the per-request auth model and why it matters. In short:

1. **Use HTTPS**: In production, run behind a reverse proxy with SSL/TLS
2. **Authentication**: Every request must carry its own token header; the server
   returns `401` otherwise. Do not rely on a server-side `META_ACCESS_TOKEN` as
   an implicit credential for HTTP callers — it is not used as a fallback.
3. **Network Security**: Never expose the raw port to an untrusted network. Bind
   to localhost behind an authenticating proxy, or restrict with firewalls.
4. **Avoid `META_ACCESS_TOKEN` on network-exposed servers**: it is an
   operator-wide credential; prefer per-request header tokens.
5. **Rate Limiting**: Consider implementing rate limiting for public APIs

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8080

CMD ["python", "-m", "meta_ads_mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]
```

### Environment Variables

```bash
# For Pipeboard-based authentication. The token will be used for stdio,
# but for HTTP it should be passed in the Authorization header.
export PIPEBOARD_API_TOKEN=your_pipeboard_token

# Optional (for custom Meta apps)
export META_APP_ID=your_app_id
export META_APP_SECRET=your_app_secret

# Optional (for direct Meta token).
# WARNING: on the HTTP transport this is NOT used as a fallback credential for
# incoming requests — callers must pass their own token header (see "Security
# Model"). Setting it on a network-exposed server is an operator-wide credential
# risk; prefer stdio, or keep the port unreachable by untrusted callers.
export META_ACCESS_TOKEN=your_access_token
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the server is running and accessible on the specified port.
2. **Authentication Failed**: Verify your Bearer token is valid and included in the `Authorization` header.
3. **404 Not Found**: Make sure you're using the correct endpoint (`/mcp`).
4. **JSON-RPC Errors**: Check that your request follows the JSON-RPC 2.0 format.

### Debug Mode

Enable verbose logging by setting the log level in your environment if the application supports it, or check the application's logging configuration. The current implementation logs to a file.

### Health Check

Test if the server is running by sending a `tools/list` request:

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your_token" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Migration from stdio

If you're currently using stdio transport with MCP clients, you can support both stdio for local clients and HTTP for web applications. The application can only run in one mode at a time, so you may need to run two separate instances if you need both simultaneously.

1. **Keep existing MCP client setup** (Claude Desktop, Cursor, etc.) using stdio.
2. **Add HTTP transport** for web applications and custom integrations by running a separate server instance with the `--transport streamable-http` flag.
3. **Use the same authentication method**:
    - For stdio, the `PIPEBOARD_API_TOKEN` environment variable is used.
    - For HTTP, pass the token in the `Authorization: Bearer <token>` header.

Both transports access the same Meta Ads functionality and use the same underlying authentication system. 