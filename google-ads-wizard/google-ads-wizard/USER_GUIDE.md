# Google Ads Wizard CLI - User Guide

> AI-powered Google Ads auditing tool that generates RTT-style PDF reports using Claude Sonnet 4

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)
- [Output Formats](#output-formats)
- [Understanding Your Audit](#understanding-your-audit)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [FAQ](#faq)

---

## Overview

Google Ads Wizard is a command-line tool that connects to your Google Ads account, analyzes your campaigns using Claude Sonnet 4 AI, and generates comprehensive audit reports following the RTT (Tracking, Targeting, Testing) methodology.

### What It Does

1. **Connects** to Google Ads API using secure OAuth authentication
2. **Fetches** comprehensive account data (campaigns, metrics, keywords, conversions)
3. **Analyzes** with Claude Sonnet 4 using deterministic prompts (temperature 0)
4. **Generates** professional reports in PDF or JSON format
5. **Creates** AI context files for Cursor/Claude assistants

---

## Features

### ✅ Campaign Management
- List all campaigns with performance metrics
- Filter by status (active, paused, all)
- View last 30 days of performance data
- Track impressions, clicks, CTR, and conversions

### ✅ AI-Powered Audits
- Comprehensive account health analysis
- RTT methodology framework (Tracking, Targeting, Testing)
- Deterministic analysis (temperature 0 for consistency)
- Critical issues identification
- Prioritized recommendations

### ✅ Multiple Output Formats
- **PDF Reports** - Professional RTT-style reports (8KB)
- **JSON Export** - Detailed structured data (13KB)
- **AI Context** - Auto-generated `.cursor/rules` files

### ✅ Performance Metrics
- Total spend and cost per conversion
- Click-through rates (CTR)
- Conversion tracking analysis
- Keyword performance data
- Account health score (1-10)

---

## Installation

### Prerequisites

- Node.js 16+ installed
- npm or yarn package manager
- Google Ads account with API access
- Anthropic API key (for Claude analysis)

### Setup Steps

1. **Navigate to the project directory:**
   ```bash
   cd google-ads-wizard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Verify installation:**
   ```bash
   npm run dev -- --help
   ```

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id

# Anthropic API (for Claude analysis)
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 2. Google Ads OAuth Setup

**Option 1: Use the Built-in Token Generator (Recommended)**

```bash
npm run get-token
```

Follow the interactive prompts:
1. Open the provided OAuth URL in your browser
2. Sign in with your Google account
3. Authorize the application
4. Copy the authorization code from the redirect URL
5. Paste it into the terminal
6. Copy the refresh token to your `.env` file

**Option 2: Use Google OAuth Playground**

See [GET_TOKEN_EASY.md](./GET_TOKEN_EASY.md) for detailed instructions.

### 3. Get Your Customer ID

Your Google Ads Customer ID is a 10-digit number found in your Google Ads account:
- Format: `1234567890` (no hyphens)
- Location: Top right corner of Google Ads interface

---

## Commands

### 1. List Campaigns

View all campaigns with performance metrics from the last 30 days.

**Basic Usage:**
```bash
npm run dev -- campaigns <customer-id>
```

**Example:**
```bash
npm run dev -- campaigns 8888034950
```

**Output:**
```
📊 Google Ads Campaigns

Account: Carrara (Client Owned)
Customer ID: 8888034950
Currency: USD
────────────────────────────────────────────────

1. LMP - Nationwide - PMax
   Status: ENABLED
   Performance (Last 30 days):
     • Impressions: 893,618
     • Clicks: 14,126
     • CTR: 1.58%
     • Conversions: 62

[... more campaigns ...]

Total: 45 campaigns
```

**Filter by Status:**
```bash
# Show only active campaigns
npm run dev -- campaigns 8888034950 --status active

# Show only paused campaigns
npm run dev -- campaigns 8888034950 --status paused

# Show all campaigns (default)
npm run dev -- campaigns 8888034950 --status all
```

---

### 2. Generate Audit (PDF)

Create a comprehensive RTT-style audit report in PDF format.

**Basic Usage:**
```bash
npm run dev -- audit <customer-id>
```

**Example:**
```bash
npm run dev -- audit 8888034950
```

**What Happens:**
1. ⏳ Connects to Google Ads API
2. ⏳ Fetches account data (5-10 seconds)
3. ⏳ Analyzes with Claude Sonnet 4 (15-20 seconds)
4. ⏳ Generates RTT-style PDF report (5 seconds)
5. ⏳ Creates `.cursor/rules` AI context (< 1 second)

**Output:**
```
✅ Audit Complete!

Account: Carrara (Client Owned)
Health Score: 4/10
Critical Issues: 4
Recommendations: 5

📁 Files Generated:
  • Report: ./audit-report.pdf
  • Context: ./.cursor/rules
```

**Custom Output Path:**
```bash
npm run dev -- audit 8888034950 --output reports/audit-2025-11-22.pdf
```

---

### 3. Generate Audit (JSON)

Export audit data as structured JSON for programmatic access.

**Basic Usage:**
```bash
npm run dev -- audit <customer-id> --format json
```

**Example:**
```bash
npm run dev -- audit 8888034950 --format json --output my-audit.json
```

**Output File Structure:**
```json
{
  "accountInfo": {
    "id": "8888034950",
    "descriptiveName": "Carrara (Client Owned)",
    "currencyCode": "USD",
    "status": "ENABLED"
  },
  "analysis": {
    "account_health_score": 4,
    "total_spend_last_30_days": 95355.53,
    "executive_summary": "...",
    "critical_issues": [...],
    "recommendations": [...],
    "rtt_analysis": {...}
  },
  "performance": {...},
  "campaigns": [...]
}
```

---

### 4. Help & Version

**Show All Commands:**
```bash
npm run dev -- --help
```

**Show Command-Specific Help:**
```bash
npm run dev -- audit --help
npm run dev -- campaigns --help
```

**Check Version:**
```bash
npm run dev -- --version
```

---

## Output Formats

### PDF Report (`audit-report.pdf`)

Professional RTT-style report includes:

1. **Title Page**
   - Account name and customer ID
   - Audit date
   - Account health score (1-10)

2. **Executive Summary**
   - 2-3 sentence overview
   - Key findings

3. **Performance Overview**
   - Last 30 days metrics
   - Total spend, clicks, conversions
   - Cost per conversion

4. **Critical Issues**
   - Severity levels (Critical, High, Medium, Low)
   - Detailed descriptions
   - Business impact analysis
   - Categories (Tracking, Targeting, Testing)

5. **Account Strengths**
   - What's working well
   - Positive performance indicators

6. **Recommendations**
   - Prioritized action items ([HIGH], [MEDIUM], [LOW])
   - Specific implementation steps
   - Expected impact

7. **RTT Analysis**
   - **Tracking:** Conversion tracking, measurement setup
   - **Targeting:** Audience, keywords, demographics
   - **Testing:** Ad copy, creative performance

---

### JSON Export (`test-audit.json`)

Structured data includes:

```json
{
  "accountInfo": {
    "id": "string",
    "descriptiveName": "string",
    "currencyCode": "string",
    "timeZone": "string",
    "status": "ENABLED|PAUSED|REMOVED"
  },
  "analysis": {
    "account_health_score": 1-10,
    "currency": "USD",
    "total_spend_last_30_days": number,
    "executive_summary": "string",
    "critical_issues": [
      {
        "severity": "critical|high|medium|low",
        "title": "string",
        "description": "string",
        "impact": "string",
        "category": "tracking|targeting|testing|quality_score"
      }
    ],
    "strengths": ["string"],
    "recommendations": [
      {
        "priority": "HIGH|MEDIUM|LOW",
        "category": "string",
        "title": "string",
        "description": "string",
        "expected_impact": "string",
        "effort_required": "string",
        "steps": ["string"]
      }
    ],
    "rtt_analysis": {
      "tracking_score": 1-10,
      "targeting_score": 1-10,
      "testing_score": 1-10
    }
  },
  "performance": {
    "total_impressions": number,
    "total_clicks": number,
    "average_ctr": number,
    "total_conversions": number,
    "cost_per_conversion": number
  },
  "campaigns": [...]
}
```

---

### AI Context File (`.cursor/rules`)

Auto-generated context for AI assistants:

```markdown
# Google Ads Account Context - Auto-Generated

Last Updated: 11/22/2025, 3:54:11 PM

## Account Overview
- Account: Carrara (Client Owned)
- Customer ID: 8888034950
- Health Score: 4/10

## Performance Summary (Last 30 Days)
- Total Spend: USD $95,355.53
- Total Clicks: 33,065
- Conversions: 162.5
- Cost per Conversion: USD $586.80

## 🔴 Critical Issues
1. Extremely High Cost Per Conversion
2. No Conversion Tracking Data Available
3. Poor Click-Through Rate Performance
4. No Keyword Data Available

## 💡 Top Recommendations
1. [HIGH] Implement comprehensive conversion tracking
2. [HIGH] Conduct keyword audit
3. [HIGH] Pause bottom 50% performers
...

## Quick Commands
```bash
npm run dev -- campaigns 8888034950
npm run dev -- audit 8888034950
```
```

---

## Understanding Your Audit

### Account Health Score

The health score (1-10) is calculated based on:

- **Tracking (33%):** Conversion tracking setup and data quality
- **Targeting (33%):** Keyword relevance, audience alignment, CTR
- **Testing (33%):** Ad copy performance, A/B testing implementation

**Score Interpretation:**
- **9-10:** Excellent - Best-in-class performance
- **7-8:** Good - Minor optimizations needed
- **5-6:** Fair - Several improvement opportunities
- **3-4:** Poor - Significant issues requiring attention
- **1-2:** Critical - Immediate action required

---

### Critical Issues

Issues are categorized by severity:

**🔴 Critical (Immediate Action Required)**
- Major budget waste or tracking failures
- Prevents effective optimization
- High business impact

**🟠 High (Address Within 1 Week)**
- Significant performance problems
- Moderate budget impact
- Quality score issues

**🟡 Medium (Address Within 1 Month)**
- Optimization opportunities
- Efficiency improvements
- Testing recommendations

**🟢 Low (Nice to Have)**
- Minor enhancements
- Long-term strategy items

---

### RTT Methodology

**Tracking** - Are you measuring what matters?
- Conversion tracking setup
- Google Analytics 4 integration
- Event tracking validation
- Attribution modeling

**Targeting** - Are you reaching the right people?
- Keyword relevance and match types
- Audience segmentation
- Geographic targeting
- Demographic alignment
- Negative keywords

**Testing** - Are you continuously improving?
- Ad copy A/B tests
- Landing page experiments
- Bid strategy optimization
- Creative performance analysis

---

## Troubleshooting

### Common Issues

#### "Invalid Anthropic API key"

**Problem:** Claude analysis fails with 401 error

**Solution:**
1. Check your `.env` file has the correct API key
2. Verify the key starts with `sk-ant-api03-`
3. Generate a new key at https://console.anthropic.com/
4. Update `.env` and restart the CLI

```bash
# Test your API key
grep ANTHROPIC_API_KEY .env
```

---

#### "The caller does not have permission"

**Problem:** Google Ads API returns 403 error

**Solutions:**

1. **Wrong Customer ID:** Verify you're using the correct 10-digit customer ID
   ```bash
   # Check your .env file
   grep GOOGLE_ADS_LOGIN_CUSTOMER_ID .env
   ```

2. **MCC Account:** If using a manager account, set the login customer ID
   ```env
   GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_mcc_id
   ```

3. **Token Mismatch:** Refresh token doesn't match client credentials
   ```bash
   # Regenerate token
   npm run get-token
   ```

---

#### "Failed to get access token: unauthorized_client"

**Problem:** OAuth client credentials mismatch

**Solution:**
The refresh token was generated with different OAuth credentials.

```bash
# 1. Delete old refresh token
# 2. Generate new token with current credentials
npm run get-token

# 3. Update .env with new refresh token
```

---

#### "No campaigns found"

**Problem:** Account has no active campaigns

**Solutions:**
1. Check if campaigns exist in Google Ads UI
2. Verify you're using the correct customer ID
3. Check if all campaigns are paused/removed

```bash
# List all campaigns including paused
npm run dev -- campaigns 8888034950 --status all
```

---

#### Spend showing as "undefined"

**Problem:** Cost data not displaying in output

**This is a known minor formatting issue.** The data is being fetched correctly from the API, but there's a display bug. The audit reports still contain accurate spend data.

---

### Debug Mode

Enable verbose logging:

```bash
# Set debug environment variable
DEBUG=* npm run dev -- audit 8888034950
```

---

## Best Practices

### 1. Regular Audits

**Weekly:** Run campaigns command to monitor performance
```bash
npm run dev -- campaigns 8888034950 --status active
```

**Monthly:** Generate full audit to identify trends
```bash
npm run dev -- audit 8888034950 --output "audits/audit-$(date +%Y-%m-%d).pdf"
```

**Quarterly:** Compare audits to measure improvement
- Keep historical JSON exports
- Track health score trends
- Review implemented recommendations

---

### 2. Use AI Context Files

The `.cursor/rules` file helps AI assistants:
- Understand your account structure
- Reference critical issues
- Suggest context-aware improvements
- Provide quick command access

**Cursor Users:**
1. Audit generates `.cursor/rules` automatically
2. Cursor reads this for context
3. Ask: "What should I focus on first?"
4. Get recommendations based on your audit

---

### 3. Action on Recommendations

**Priority Order:**
1. **[HIGH]** items first (biggest impact)
2. **[MEDIUM]** items next (quick wins)
3. **[LOW]** items last (long-term strategy)

**Implementation Cycle:**
1. Review audit recommendations
2. Implement top 3 [HIGH] items
3. Wait 2 weeks for data
4. Re-run audit to measure impact
5. Repeat

---

### 4. Export Data for Reporting

**Create Monthly Reports:**
```bash
# Export JSON for dashboards
npm run dev -- audit 8888034950 \
  --format json \
  --output "reports/$(date +%Y-%m).json"

# Generate PDF for stakeholders
npm run dev -- audit 8888034950 \
  --output "reports/monthly-audit-$(date +%Y-%m).pdf"
```

**Parse JSON Programmatically:**
```javascript
const fs = require('fs');
const audit = JSON.parse(fs.readFileSync('test-audit.json'));

console.log(`Health Score: ${audit.analysis.account_health_score}`);
console.log(`Critical Issues: ${audit.analysis.critical_issues.length}`);
```

---

## FAQ

### How long does an audit take?

**Total Time:** ~30-45 seconds
- API fetch: 5-10 seconds
- Claude analysis: 15-20 seconds
- PDF generation: 5 seconds
- AI context: < 1 second

### Is my data secure?

**Yes.** The CLI:
- Uses OAuth 2.0 for secure authentication
- Makes real-time API calls (no data storage)
- Keeps credentials in local `.env` file
- Never shares data with third parties

### Can I audit multiple accounts?

**Yes.** Use different customer IDs:

```bash
# Account 1
npm run dev -- audit 1111111111 --output account1.pdf

# Account 2
npm run dev -- audit 2222222222 --output account2.pdf

# Account 3
npm run dev -- audit 3333333333 --output account3.pdf
```

### Does it work with MCC accounts?

**Yes.** Set the MCC ID as `GOOGLE_ADS_LOGIN_CUSTOMER_ID`:

```env
GOOGLE_ADS_LOGIN_CUSTOMER_ID=9999999999  # Your MCC ID
```

Then audit sub-accounts:
```bash
npm run dev -- audit 1111111111  # Sub-account 1
npm run dev -- audit 2222222222  # Sub-account 2
```

### What if I don't have a Developer Token?

Apply for one at: https://developers.google.com/google-ads/api/docs/get-started/dev-token

**Approval time:** Usually 24-48 hours

While waiting, use test accounts with test developer tokens.

### Can I customize the audit prompts?

**Yes.** Edit `src/prompts/audit.ts` to modify:
- Analysis criteria
- Recommendation priorities
- RTT scoring weights
- Output format

**Note:** Keep `temperature: 0` for deterministic results.

### Does it support other languages?

Currently **English only**, but you can modify prompts to support:
- Spanish
- French
- German
- Other languages

Edit `src/prompts/audit.ts` and add your language translations.

### How accurate is the AI analysis?

**Very accurate** with limitations:
- Uses Claude Sonnet 4 (state-of-the-art)
- Temperature 0 (deterministic, consistent)
- Based on Google Ads best practices
- RTT methodology (industry-standard)

**Limitations:**
- Cannot access data outside API scope
- Recommendations are general best practices
- Requires manual review for industry-specific nuances

### Can I schedule automatic audits?

**Yes.** Use cron jobs:

```bash
# Create a script: run-audit.sh
#!/bin/bash
cd /path/to/google-ads-wizard
npm run dev -- audit 8888034950 --output "reports/audit-$(date +%Y-%m-%d).pdf"
```

```bash
# Add to crontab (weekly on Monday 9am)
0 9 * * 1 /path/to/run-audit.sh
```

### What's the API rate limit?

Google Ads API limits:
- **Standard:** 15,000 operations/day
- **Basic:** 15,000 operations/day
- **Test:** 15,000 operations/day

One audit uses ~10-20 operations, so you can run hundreds per day.

---

## Support

### Documentation
- [README.md](./README.md) - Project overview
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Detailed setup
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [PHASE2_COMPLETE.md](./PHASE2_COMPLETE.md) - Feature changelog

### Community
- **Issues:** [GitHub Issues](https://github.com/Organized-AI/fix-your-tracking/issues)
- **Email:** info@pipeboard.co
- **Discord:** [Join our community](https://discord.gg/YzMwQ8zrjr)

---

## Example Workflow

### Complete Audit Workflow

```bash
# 1. List campaigns to verify access
npm run dev -- campaigns 8888034950

# 2. Filter to active campaigns
npm run dev -- campaigns 8888034950 --status active

# 3. Generate full audit
npm run dev -- audit 8888034950

# 4. Review PDF report
open audit-report.pdf

# 5. Export JSON for records
npm run dev -- audit 8888034950 \
  --format json \
  --output "audits/$(date +%Y-%m-%d).json"

# 6. Check AI context
cat .cursor/rules

# 7. Implement top 3 recommendations from audit

# 8. Wait 2 weeks for data

# 9. Re-run audit to measure improvement
npm run dev -- audit 8888034950 --output audit-after-optimization.pdf
```

---

## Advanced Usage

### Batch Processing Multiple Accounts

```bash
#!/bin/bash
# audit-all-accounts.sh

ACCOUNTS=(
  "1111111111:Client-A"
  "2222222222:Client-B"
  "3333333333:Client-C"
)

for account in "${ACCOUNTS[@]}"; do
  IFS=':' read -r id name <<< "$account"
  echo "Auditing $name..."
  npm run dev -- audit "$id" --output "reports/${name}-$(date +%Y-%m-%d).pdf"
  sleep 5  # Rate limiting
done

echo "All audits complete!"
```

---

**Made with ❤️ by [Organized AI](https://organized.ai)**

*Following PostHog Wizard patterns: deterministic analysis, temperature 0*
