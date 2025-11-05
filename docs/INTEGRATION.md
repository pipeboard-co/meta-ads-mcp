# Integration Guide - Using Both MCPs Together

This guide shows how to use Meta Ads MCP and Gateway MCP together for complete Meta advertising and tracking management.

## Overview

The two MCPs complement each other:

```
┌─────────────────────┐         ┌─────────────────────┐
│  Meta Ads MCP        │         │  Gateway MCP        │
│  (Python)            │         │  (TypeScript)       │
│─────────────────────│         │─────────────────────│
│                     │         │                     │
│ • Campaign Mgmt      │         │ • CAPI Gateway      │
│ • Ad Performance     │         │ • Signals Gateway   │
│ • Creative Testing   │◀──────▶│ • Event Tracking    │
│ • Budget Optimization│         │ • Infrastructure    │
│ • Targeting          │         │ • Health Monitoring │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘

         Together: Complete Advertising + Tracking Solution
```

## Configuration

### Claude Desktop

Configure both servers in `claude_desktop_config.json`:

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
      "args": ["/absolute/path/to/fix-your-tracking/gateway_mcp/build/index.js"],
      "env": {
        "META_APP_ID": "your_app_id",
        "META_APP_SECRET": "your_app_secret",
        "META_ACCESS_TOKEN": "your_access_token",
        "META_PIXEL_ID": "your_pixel_id"
      }
    }
  }
}
```

### Cursor IDE

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "python",
      "args": ["-m", "meta_ads_mcp"]
    },
    "meta-gateway": {
      "command": "node",
      "args": ["/absolute/path/to/gateway_mcp/build/index.js"]
    }
  }
}
```

## Common Workflows

### 1. Complete Data Audit

Run a full audit of your Meta advertising and tracking:

```plaintext
Phase 1: Infrastructure Analysis (Gateway MCP)
"Check my CAPI Gateway configuration"
"Verify my Signals Gateway pipelines"
"Validate event tracking setup"
"Review domain routing configuration"

Phase 2: Campaign Analysis (Meta Ads MCP)
"List all active campaigns"
"Get performance insights for the last 30 days"
"Show me ad sets with highest ROAS"
"Analyze creative performance"

Phase 3: Integration Check
"Are my conversion events tracking properly?"
"Check match quality for my events"
"Compare campaign performance with event volume"

Phase 4: Recommendations
"What infrastructure improvements should I make?"
"How can I optimize my campaigns?"
"Generate a complete audit report"
```

### 2. New Campaign Setup with Tracking

```plaintext
Step 1: Verify Infrastructure (Gateway MCP)
"Check if CAPI Gateway is configured for domain X"
"Validate event schema for purchase events"
"Test sending a sample conversion event"

Step 2: Create Campaign (Meta Ads MCP)
"Create a new sales campaign for product Y"
"Set up ad sets with conversion optimization"
"Create dynamic creative ads"

Step 3: Validate Integration
"Send test conversion and verify it appears in Meta"
"Check event match quality"
"Confirm deduplication is working"
```

### 3. Troubleshooting Poor Campaign Performance

```plaintext
Step 1: Check Tracking (Gateway MCP)
"Review event flow for the last 7 days"
"Check for any tracking errors"
"Verify gateway health status"
"Analyze match quality scores"

Step 2: Review Campaign Settings (Meta Ads MCP)
"Get campaign optimization settings"
"Check targeting configuration"
"Review budget allocation"
"Analyze ad creative performance"

Step 3: Identify Issues
"Are conversion events being tracked?"
"Is match quality affecting delivery?"
"Are there budget limitations?"
"Is creative performance declining?"

Step 4: Implement Fixes
"Fix any gateway configuration issues"
"Adjust campaign settings based on data"
"Update creatives as needed"
"Optimize budget allocation"
```

## Tool Coordination

### When to Use Each MCP

**Use Meta Ads MCP for:**
- Campaign performance analysis
- Budget management
- Creative testing
- Targeting optimization
- Ad account management
- Audience insights

**Use Gateway MCP for:**
- CAPI Gateway setup
- Event validation
- Signals Gateway configuration
- Infrastructure monitoring
- Match quality analysis
- Domain routing

### Workflow Patterns

#### Pattern 1: Infrastructure-First
Good for new campaigns or major changes.

1. Gateway MCP: Verify/setup infrastructure
2. Gateway MCP: Test event tracking
3. Meta Ads MCP: Create campaigns
4. Meta Ads MCP: Monitor performance
5. Gateway MCP: Validate event flow

#### Pattern 2: Campaign-First  
Good for existing infrastructure.

1. Meta Ads MCP: Create/update campaigns
2. Gateway MCP: Verify events tracking
3. Meta Ads MCP: Monitor and optimize
4. Gateway MCP: Check infrastructure health

#### Pattern 3: Diagnostic
Good for troubleshooting issues.

1. Gateway MCP: Check infrastructure status
2. Meta Ads MCP: Review campaign settings
3. Gateway MCP: Analyze event quality
4. Meta Ads MCP: Identify optimization opportunities
5. Apply fixes in appropriate MCP

## Data Audit Skill Integration

The [data-audit skill](../data-audit.skill) uses both MCPs:

```markdown
### Complete Audit Workflow

**Phase 1: Account Discovery** (Meta Ads MCP)
- Get ad accounts
- Get account info
- List campaigns, ad sets, ads

**Phase 2: Infrastructure Analysis** (Gateway MCP)
- List CAPI Gateways
- Check gateway configuration
- Verify Signals Gateway pipelines
- Review domain routing

**Phase 3: Performance Analysis** (Meta Ads MCP)
- Get insights for campaigns
- Analyze ad set performance
- Review creative effectiveness

**Phase 4: Event Quality** (Gateway MCP)
- Validate event schemas
- Check match quality
- Test event flow
- Review error rates

**Phase 5: Recommendations** (Both MCPs)
- Infrastructure improvements
- Campaign optimizations
- Tracking enhancements
- Budget adjustments
```

## Best Practices

### 1. Sequential Verification

Always verify infrastructure before creating campaigns:

```plaintext
1. Gateway MCP: "Check CAPI Gateway status"
2. Gateway MCP: "Send test conversion event"
3. Meta Ads MCP: "Create new campaign"
4. Gateway MCP: "Verify events are flowing"
```

### 2. Regular Health Checks

Run periodic checks using both MCPs:

```plaintext
Daily:
- Gateway MCP: Check gateway health
- Meta Ads MCP: Review campaign performance

Weekly:
- Gateway MCP: Analyze event quality trends
- Meta Ads MCP: Optimize budget allocation

Monthly:
- Gateway MCP: Full infrastructure audit
- Meta Ads MCP: Comprehensive campaign review
```

### 3. Error Response

When issues arise, use both MCPs systematically:

```plaintext
1. Identify: "Campaign conversions dropped"
2. Gateway MCP: "Check gateway status and event flow"
3. Gateway MCP: "Review error logs"
4. Meta Ads MCP: "Check campaign delivery status"
5. Meta Ads MCP: "Review optimization events"
6. Apply fixes in appropriate MCP
```

## Examples

### Example 1: Launch New Product Campaign

```plaintext
User: "I want to launch a new product campaign. Help me set everything up."

AI: Using both Meta Ads MCP and Gateway MCP...

[Gateway MCP]
1. Checking CAPI Gateway configuration for your domain
2. Verifying product purchase events are properly configured
3. Testing event tracking with sample data
4. Validating match quality meets standards

[Meta Ads MCP]  
5. Creating new campaign with OUTCOME_SALES objective
6. Setting up ad sets with conversion optimization
7. Creating dynamic creative for A/B testing
8. Configuring budget and scheduling

[Verification]
9. Gateway MCP: Confirming events flow properly
10. Meta Ads MCP: Launching campaign in ACTIVE state

Your campaign is live and tracking properly!
```

### Example 2: Diagnose Poor Performance

```plaintext
User: "My campaign conversions dropped suddenly. What's wrong?"

AI: Let me check both your infrastructure and campaigns...

[Gateway MCP]
1. Gateway health: โœ… Operational
2. Event flow: โš ๏ธ Volume dropped 60% yesterday
3. Match quality: โš ๏ธ Decreased from 8.5 to 5.2
4. Error rate: โš ๏ธ Increased 3x

[Meta Ads MCP]
5. Campaign status: โœ… Active  
6. Delivery status: โš ๏ธ Limited due to low optimization events
7. Budget: โœ… No issues
8. Targeting: โœ… No changes

Diagnosis: Your CAPI Gateway is experiencing issues with event quality.
The drop in match quality is causing Meta's algorithm to struggle.

Recommended fixes:
[Gateway MCP] Review and fix event parameter quality
[Gateway MCP] Check for recent infrastructure changes
[Meta Ads MCP] Temporarily broaden targeting while fixing tracking
```

## Troubleshooting

### Both Servers Not Connecting

1. Check Claude Desktop logs: `~/Library/Logs/Claude/`
2. Verify Python is installed: `python --version`
3. Verify Node.js is installed: `node --version`  
4. Test each server independently

### One Server Works, Other Doesn't

**Meta Ads MCP fails:**
```bash
python -m meta_ads_mcp
# Check output for errors
```

**Gateway MCP fails:**
```bash
cd gateway_mcp
npm run build
node build/index.js
# Check output for errors
```

### Tools Not Appearing

1. Restart Claude Desktop after config changes
2. Check absolute paths in configuration
3. Verify environment variables are set
4. Review server logs for startup errors

## Next Steps

- Review [Meta Ads Tools Reference](META_ADS_TOOLS.md)
- Review [Gateway MCP README](../gateway_mcp/README.md)  
- Read [Data Audit Workflow](DATA_AUDIT.md)
- Join [Discord community](https://discord.gg/YzMwQ8zrjr)

---

For more help, email support@organized.ai or join our Discord.
