# Meta Ads MCP - Local Installation Guide

This guide covers everything you need to know about installing and running Meta Ads MCP locally on your machine. For the easier Remote MCP option, **[🚀 get started here](https://pipeboard.co)**.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Authentication Setup](#authentication-setup)
- [MCP Client Configuration](#mcp-client-configuration)
- [Development Installation](#development-installation)
- [Privacy and Security](#privacy-and-security)
- [Testing and Verification](#testing-and-verification)
- [Debugging and Logs](#debugging-and-logs)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Prerequisites

- **Python 3.8 or higher**
- **[uv](https://docs.astral.sh/uv/) package manager** (recommended) or pip
- **Meta Ads account** with appropriate permissions
- **MCP-compatible client** (Claude Desktop, Cursor, Cherry Studio, etc.)

## Installation Methods

### Method 1: Using uvx (Recommended)

```bash
# Install via uvx (automatically handles dependencies)
uvx meta-ads-mcp
```

### Method 2: Using pip

```bash
# Install via pip
pip install meta-ads-mcp
```

### Method 3: Development Installation

```bash
# Clone the repository
git clone https://github.com/pipeboard-co/meta-ads-mcp.git
cd meta-ads-mcp

# Install in development mode
uv pip install -e .
# Or with pip
pip install -e .
```

## Authentication Setup

You have two authentication options:

### Option 1: Pipeboard Authentication (Recommended)

This is the easiest method that handles all OAuth complexity for you:

1. **Sign up to Pipeboard**
   - Visit [Pipeboard.co](https://pipeboard.co)
   - Create an account

2. **Generate API Token**
   - Go to [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)
   - Generate a new API token
   - Copy the token securely

3. **Set Environment Variable**
   ```bash
   # On macOS/Linux
   export PIPEBOARD_API_TOKEN=your_pipeboard_token_here
   
   # On Windows (Command Prompt)
   set PIPEBOARD_API_TOKEN=your_pipeboard_token_here
   
   # On Windows (PowerShell)
   $env:PIPEBOARD_API_TOKEN="your_pipeboard_token_here"
   ```

4. **Make it Persistent**
   
   Add to your shell profile (`.bashrc`, `.zshrc`, etc.):
   ```bash
   echo 'export PIPEBOARD_API_TOKEN=your_pipeboard_token_here' >> ~/.bashrc
   source ~/.bashrc
   ```

### Option 2: Custom Meta App

If you prefer to use your own Meta Developer App, see [CUSTOM_META_APP.md](CUSTOM_META_APP.md) for detailed instructions.

## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uvx",
      "args": ["meta-ads-mcp"],
      "env": {
        "PIPEBOARD_API_TOKEN": "your_pipeboard_token"
      }
    }
  }
}
```

### Cursor

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uvx", 
      "args": ["meta-ads-mcp"],
      "env": {
        "PIPEBOARD_API_TOKEN": "your_pipeboard_token"
      }
    }
  }
}
```

### Cherry Studio

In Cherry Studio settings, add a new MCP server:
- **Name**: Meta Ads MCP
- **Command**: `uvx`
- **Arguments**: `["meta-ads-mcp"]`
- **Environment Variables**: `PIPEBOARD_API_TOKEN=your_pipeboard_token`

## Development Installation

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/pipeboard-co/meta-ads-mcp.git
cd meta-ads-mcp

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"  # If dev dependencies are defined
```

### Running from Source

```bash
# Set environment variable
export PIPEBOARD_API_TOKEN=your_token

# Run directly
python -m meta_ads_mcp

# Or if installed in development mode
meta-ads-mcp
```

### Testing Your Installation

```bash
# Test the installation
python -c "import meta_ads_mcp; print('Installation successful!')"

# Test MCP server startup
meta-ads-mcp --help
```

## Privacy and Security

### Token Storage and Caching

Meta Ads MCP follows security best practices:

1. **Secure Token Cache Location**:
   - **Windows**: `%APPDATA%\meta-ads-mcp\token_cache.json`
   - **macOS**: `~/Library/Application Support/meta-ads-mcp/token_cache.json`
   - **Linux**: `~/.config/meta-ads-mcp/token_cache.json`

2. **Automatic Token Management**:
   - Tokens are cached securely after first authentication
   - You don't need to provide access tokens for each command
   - Tokens are automatically refreshed when needed

3. **Environment Variable Security**:
   - `PIPEBOARD_API_TOKEN` should be kept secure
   - Don't commit tokens to version control
   - Use environment files (`.env`) for local development

### Security Best Practices

```bash
# Create a .env file for local development (never commit this)
echo "PIPEBOARD_API_TOKEN=your_token_here" > .env

# Add .env to .gitignore
echo ".env" >> .gitignore

# Load environment variables from .env
source .env
```

## Testing and Verification

### Basic Functionality Test

Once installed and configured, test with your MCP client:

1. **Verify Account Access**
   ```
   Ask your LLM: "Use mcp_meta_ads_get_ad_accounts to show my Meta ad accounts"
   ```

2. **Check Account Details**
   ```
   Ask your LLM: "Get details for account act_XXXXXXXXX using mcp_meta_ads_get_account_info"
   ```

3. **List Campaigns**
   ```
   Ask your LLM: "Show me my active campaigns using mcp_meta_ads_get_campaigns"
   ```

### Manual Testing with Python

```python
# Test authentication
from meta_ads_mcp.core.auth import get_access_token

try:
    token = get_access_token()
    print("Authentication successful!")
    print(f"Token starts with: {token[:10]}...")
except Exception as e:
    print(f"Authentication failed: {e}")
```

### Testing with MCP Client

When using Meta Ads MCP with an LLM interface:

1. Ensure the `PIPEBOARD_API_TOKEN` environment variable is set
2. Verify account access by calling `mcp_meta_ads_get_ad_accounts`
3. Check specific account details with `mcp_meta_ads_get_account_info`
4. Test campaign retrieval with `mcp_meta_ads_get_campaigns`

## Debugging and Logs

### Log File Locations

Debug logs are automatically created in platform-specific locations:

- **macOS**: `~/Library/Application\ Support/meta-ads-mcp/meta_ads_debug.log`
- **Windows**: `%APPDATA%\meta-ads-mcp\meta_ads_debug.log`
- **Linux**: `~/.config/meta-ads-mcp/meta_ads_debug.log`

### Enabling Debug Mode

```bash
# Set debug environment variable
export META_ADS_DEBUG=true

# Run with verbose output
meta-ads-mcp --verbose
```

### Viewing Logs

```bash
# On macOS/Linux
tail -f ~/Library/Application\ Support/meta-ads-mcp/meta_ads_debug.log

# On Windows
type %APPDATA%\meta-ads-mcp\meta_ads_debug.log
```

### Common Debug Commands

```bash
# Check if MCP server starts correctly
meta-ads-mcp --test-connection

# Verify environment variables
echo $PIPEBOARD_API_TOKEN

# Test Pipeboard authentication
python -c "
from meta_ads_mcp.core.pipeboard_auth import test_auth
test_auth()
"
```

## Troubleshooting

### Authentication Issues

#### Problem: "PIPEBOARD_API_TOKEN not set"
```bash
# Solution: Set the environment variable
export PIPEBOARD_API_TOKEN=your_token_here

# Verify it's set
echo $PIPEBOARD_API_TOKEN
```

#### Problem: "Invalid Pipeboard token"
1. Check your token at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)
2. Regenerate if necessary
3. Update your environment variable

#### Problem: "Authentication failed"
```bash
# Clear cached tokens and retry
rm -rf ~/.config/meta-ads-mcp/token_cache.json  # Linux
rm -rf ~/Library/Application\ Support/meta-ads-mcp/token_cache.json  # macOS

# Force re-authentication
python test_pipeboard_auth.py --force-login
```

### Installation Issues

#### Problem: "Command not found: uvx"
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install meta-ads-mcp
```

#### Problem: "Permission denied"
```bash
# Use user installation
pip install --user meta-ads-mcp

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install meta-ads-mcp
```

#### Problem: "Python version incompatible"
```bash
# Check Python version
python --version

# Update to Python 3.8+
# Use pyenv or your system's package manager
```

### Runtime Issues

#### Problem: "Failed to connect to Meta API"
1. Check internet connection
2. Verify Meta API status
3. Check rate limits
4. Ensure account permissions

#### Problem: "MCP client can't find server"
1. Verify the command path in your MCP client config
2. Check environment variables are set in the client
3. Test the command manually in terminal

#### Problem: "SSL/TLS errors"
```bash
# Update certificates
pip install --upgrade certifi

# Or use system certificates
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```

### API Errors

#### Problem: "Insufficient permissions"
- Ensure your Meta account has access to the ad accounts
- Check if your Pipeboard token has the right scopes
- Verify account roles in Meta Business Manager

#### Problem: "Rate limit exceeded"
- Wait before retrying
- Reduce request frequency
- Check if multiple instances are running

#### Problem: "Account not found"
- Verify account ID format (should be `act_XXXXXXXXX`)
- Check account access permissions
- Ensure account is active

### Performance Issues

#### Problem: "Slow response times"
```bash
# Check network latency
ping graph.facebook.com

# Clear cache
rm -rf ~/.config/meta-ads-mcp/token_cache.json

# Check system resources
top  # or htop on Linux/macOS
```

## Advanced Configuration

### Custom Configuration File

Create `~/.config/meta-ads-mcp/config.json`:

```json
{
  "api_version": "v21.0",
  "timeout": 30,
  "max_retries": 3,
  "debug": false,
  "cache_duration": 3600
}
```

### Environment Variables

```bash
# API Configuration
export META_API_VERSION=v21.0
export META_API_TIMEOUT=30
export META_ADS_DEBUG=true

# Cache Configuration  
export META_ADS_CACHE_DIR=/custom/cache/path
export META_ADS_CACHE_DURATION=3600

# Pipeboard Configuration
export PIPEBOARD_API_BASE=https://api.pipeboard.co
export PIPEBOARD_API_TOKEN=your_token_here
```

### Transport Configuration

Meta Ads MCP uses **stdio transport** by default. For HTTP transport:

See [STREAMABLE_HTTP_SETUP.md](STREAMABLE_HTTP_SETUP.md) for streamable HTTP transport configuration.

### Custom Meta App Integration

For advanced users who want to use their own Meta Developer App:

1. Follow [CUSTOM_META_APP.md](CUSTOM_META_APP.md) guide
2. Set up OAuth flow
3. Configure environment variables:
   ```bash
   export META_APP_ID=your_app_id
   export META_APP_SECRET=your_app_secret
   export META_REDIRECT_URI=your_redirect_uri
   ```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** for detailed error messages
2. **Search existing issues** on GitHub
3. **Join our Discord** at [discord.gg/YzMwQ8zrjr](https://discord.gg/YzMwQ8zrjr)
4. **Email support** at info@pipeboard.co
5. **Consider Remote MCP** at [pipeboard.co](https://pipeboard.co) as an alternative

---

**Quick Alternative**: If local installation is causing issues, try our [Remote MCP service](https://pipeboard.co) - no local setup required! 
