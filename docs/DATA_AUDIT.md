# Data Audit Workflow - Complete Meta Infrastructure Audit

This guide shows how to use the data-audit skill with both Meta Ads MCP and Gateway MCP for comprehensive auditing.

## Overview

A complete Meta audit requires checking both:
1. **Advertising Infrastructure** (Meta Ads MCP) - Campaigns, ads, targeting, performance
2. **Tracking Infrastructure** (Gateway MCP) - CAPI, Signals Gateway, event quality

## Prerequisites

- Meta Ads MCP configured and running
- Gateway MCP configured (when released)
- data-audit skill enabled in Claude
- Meta Business Manager access
- CAPI Gateway or Pixel configured

## Complete Audit Checklist

### Phase 1: Account Discovery

**Using Meta Ads MCP:**

- [ ] List all ad accounts
- [ ] Get account details and status
- [ ] Identify associated pages
- [ ] List business assets
- [ ] Check account permissions

**Commands:**
```plaintext
"List my Meta ad accounts"
"Get details for account act_XXXXX"
"Show me pages for this account"
```

### Phase 2: Infrastructure Analysis

**Using Gateway MCP:**

- [ ] Check CAPI Gateway status
- [ ] Verify Signals Gateway pipelines
- [ ] Review domain routing configuration
- [ ] Check gateway health metrics
- [ ] Validate event schemas

**Commands:**
```plaintext
"List my CAPI Gateways"
"Check gateway configuration for pixel XXXXX"
"Verify Signals Gateway pipeline status"
"Review domain routing for domain.com"
```

### Phase 3: Campaign Analysis

**Using Meta Ads MCP:**

- [ ] List all active campaigns
- [ ] Get campaign performance metrics
- [ ] Review ad set configuration
- [ ] Analyze ad creative performance
- [ ] Check targeting settings
- [ ] Review budget allocation

**Commands:**
```plaintext
"List active campaigns for last 30 days"
"Get insights for campaign XXXXX"
"Show me ad sets with ROAS > 2"
"Analyze creative performance"
```

### Phase 4: Event Quality Assessment

**Using Gateway MCP:**

- [ ] Validate event schemas
- [ ] Check match quality scores
- [ ] Review deduplication settings
- [ ] Test event flow
- [ ] Analyze error rates
- [ ] Check event volume trends

**Commands:**
```plaintext
"Validate purchase event schema"
"Calculate match quality for recent events"
"Check deduplication configuration"
"Send test conversion event"
```

### Phase 5: Integration Validation

**Using Both MCPs:**

- [ ] Verify conversion events match campaign objectives
- [ ] Check optimization event volume
- [ ] Validate attribution windows
- [ ] Review conversion value settings
- [ ] Confirm proper event parameter mapping

**Commands:**
```plaintext
"Compare campaign objectives with tracked events"
"Check optimization event volume for campaign XXXXX"
"Verify attribution settings"
```

### Phase 6: Performance Deep Dive

**Using Meta Ads MCP:**

- [ ] Identify top/bottom performing campaigns
- [ ] Analyze ROAS by ad set
- [ ] Review cost per conversion trends
- [ ] Check frequency and reach metrics
- [ ] Evaluate creative fatigue

**Commands:**
```plaintext
"Show campaigns ranked by ROAS"
"Get frequency metrics for active campaigns"
"Identify ad sets with declining performance"
```

### Phase 7: Recommendations

**Using Both MCPs:**

- [ ] Infrastructure improvements (Gateway)
- [ ] Campaign optimizations (Ads)
- [ ] Budget reallocation suggestions (Ads)
- [ ] Tracking enhancements (Gateway)
- [ ] Creative testing recommendations (Ads)

## Example Complete Audit

### Step 1: Initialize Audit

```plaintext
User: "Run a complete audit of my Meta advertising and tracking infrastructure."

AI: Starting comprehensive Meta audit using both Meta Ads MCP and Gateway MCP...
```

### Step 2: Account Discovery

```plaintext
[Meta Ads MCP]

โœ… Found 2 ad accounts:
  1. Main Business Account (act_123456)
     - Status: Active
     - Currency: USD
     - Time zone: America/Los_Angeles
     
  2. Test Account (act_789012)  
     - Status: Active
     - Currency: USD
     - Time zone: America/New_York

โœ… Associated Pages:
  - Main Business Page (ID: 987654)
  - Product Launch Page (ID: 456789)
```

### Step 3: Infrastructure Check

```plaintext
[Gateway MCP]

โœ… CAPI Gateway Status:
  - Gateway ID: gateway_abc123
  - Status: Active
  - Domain: yourdomain.com
  - Health: โœ… Operational
  
โš ๏ธ Signals Gateway:
  - No active pipelines found
  - Recommendation: Consider setting up first-party data pipeline

โœ… Event Configuration:
  - Purchase events: โœ… Properly configured
  - Add to Cart: โœ… Properly configured  
  - View Content: โš ๏ธ Missing some parameters
```

### Step 4: Campaign Analysis

```plaintext
[Meta Ads MCP]

โœ… Active Campaigns (Last 30 Days):

1. Spring Sale Campaign
   - Status: Active
   - Objective: OUTCOME_SALES
   - Spend: $5,234
   - ROAS: 3.2
   - Performance: โœ… Strong
   
2. Brand Awareness Campaign
   - Status: Active
   - Objective: OUTCOME_AWARENESS
   - Spend: $2,100
   - Reach: 45,000
   - CPM: $12.50
   - Performance: โœ… Good
   
3. Retargeting Campaign
   - Status: Active
   - Objective: OUTCOME_SALES
   - Spend: $3,456
   - ROAS: 1.8
   - Performance: โš ๏ธ Below target (target ROAS: 2.5)
```

### Step 5: Event Quality Check

```plaintext
[Gateway MCP]

โœ… Event Quality Metrics:

Purchase Events (Last 7 days):
  - Volume: 1,234 events
  - Match Quality: 8.2/10 โœ…
  - Deduplication: 98.5% โœ…
  - Error Rate: 0.8% โœ…
  
Add to Cart Events:
  - Volume: 4,567 events
  - Match Quality: 7.1/10 โš ๏ธ
  - Deduplication: 97.2% โœ…
  - Error Rate: 2.3% โš ๏ธ
  
โš ๏ธ Issues Found:
  - Add to Cart match quality could be improved
  - Missing email parameter in 15% of events
  - Phone number formatting inconsistent
```

### Step 6: Integration Analysis

```plaintext
[Both MCPs]

โœ… Campaign-Event Alignment:

1. Spring Sale Campaign
   - Optimization Event: Purchase
   - Event Volume: โœ… 1,234 conversions (excellent)
   - Match Quality: โœ… 8.2/10
   - Verdict: โœ… Optimal configuration
   
2. Retargeting Campaign  
   - Optimization Event: Purchase
   - Event Volume: โš ๏ธ 234 conversions (low)
   - Match Quality: โœ… 8.2/10
   - Verdict: โš ๏ธ Volume too low for effective optimization
```

### Step 7: Recommendations

```plaintext
[Comprehensive Recommendations]

๐Ÿ"ง Infrastructure Improvements (Gateway MCP):

1. HIGH PRIORITY: Improve Add to Cart event quality
   - Add email parameter to remaining 15% of events
   - Standardize phone number formatting
   - Target: Increase match quality from 7.1 to 8.0+
   
2. MEDIUM PRIORITY: Set up Signals Gateway
   - Create first-party data pipeline
   - Route CRM data to Meta
   - Improve audience targeting

3. LOW PRIORITY: Add custom conversions
   - Track "High Value Purchase" (>$200)
   - Track "Repeat Customer" events
   - Enable value-based optimization

๐Ÿš€ Campaign Optimizations (Meta Ads MCP):

1. HIGH PRIORITY: Fix Retargeting Campaign
   - Current ROAS: 1.8 (target: 2.5)
   - Issue: Low conversion volume (234 vs target 500+)
   - Actions:
     โ€ข Expand audience size by 2-3x
     โ€ข Consider using Value optimization
     โ€ข Test different ad creatives
   
2. MEDIUM PRIORITY: Scale Spring Sale Campaign
   - Current: $5,234 spend, 3.2 ROAS
   - Opportunity: Strong performance indicates room to scale
   - Actions:
     โ€ข Increase daily budget by 20%
     โ€ข Duplicate top-performing ad sets
     โ€ข Test new audience expansions
   
3. LOW PRIORITY: Optimize Brand Awareness
   - Current CPM: $12.50
   - Actions:
     โ€ข Test different placements
     โ€ข Experiment with video creative
     โ€ข Consider carousel format

๐Ÿ'ฐ Budget Recommendations:

- Decrease Retargeting: -$500/day (until fixed)
- Increase Spring Sale: +$300/day
- Maintain Brand Awareness: No change
- Net: Reallocate $200/day to top performer

๐Ÿ"Š Expected Impact:

- ROAS improvement: +15-20%
- Conversion volume: +25-30%
- Match quality: +0.9 points
- Overall efficiency: +18%
```

## Audit Report Template

Use this template for documenting audits:

```markdown
# Meta Advertising & Tracking Audit Report

**Date:** [Date]
**Auditor:** [Name]
**Accounts Reviewed:** [Account IDs]

## Executive Summary

- Total Ad Spend (30 days): $X,XXX
- Overall ROAS: X.X
- Infrastructure Health: [Green/Yellow/Red]
- Event Quality: [Score]
- Priority Issues: [Number]

## Infrastructure Status

### CAPI Gateway
- Status: [Active/Inactive]
- Health: [Operational/Issues]
- Domain: [domain.com]
- Configuration: [Details]

### Signals Gateway  
- Status: [Active/Inactive/Not Set Up]
- Pipelines: [Number]
- Data Flow: [Details]

### Event Quality
- Purchase Events: [Match Quality Score]
- Add to Cart: [Match Quality Score]
- View Content: [Match Quality Score]
- Error Rate: [Percentage]

## Campaign Performance

[Table of campaigns with key metrics]

## Issues Identified

### Critical
1. [Issue description]
   - Impact: [High/Medium/Low]
   - Recommendation: [Action]
   
### Medium Priority
1. [Issue description]
   - Impact: [High/Medium/Low]  
   - Recommendation: [Action]

### Low Priority  
1. [Issue description]
   - Impact: [High/Medium/Low]
   - Recommendation: [Action]

## Recommendations

### Immediate Actions (0-7 days)
1. [Action item]
2. [Action item]

### Short Term (1-4 weeks)
1. [Action item]
2. [Action item]

### Long Term (1-3 months)
1. [Action item]
2. [Action item]

## Appendix

- Detailed metrics
- Event samples
- Configuration screenshots
- Tool outputs
```

## Automated Audit Script

Save this prompt for quick audits:

```plaintext
Run a complete Meta audit:

1. List all ad accounts and get details
2. Check CAPI Gateway status and configuration  
3. List active campaigns with 30-day performance
4. Validate event quality for purchase, add to cart, and view content
5. Check campaign-event alignment
6. Identify top 3 performance issues
7. Provide prioritized recommendations
8. Generate audit report in markdown format

Focus on actionable insights and expected ROI for each recommendation.
```

## Best Practices

1. **Run Audits Regularly**
   - Weekly: Quick performance check
   - Monthly: Full infrastructure and campaign audit  
   - Quarterly: Strategic review with leadership

2. **Document Everything**
   - Save audit reports
   - Track changes over time
   - Monitor recommendation implementation

3. **Prioritize by Impact**
   - Focus on issues affecting 20%+ of spend first
   - Address low-hanging fruit quickly
   - Plan major infrastructure changes carefully

4. **Measure Results**
   - Track KPIs before and after changes
   - Quantify improvement from recommendations
   - Adjust strategy based on results

## Troubleshooting Common Issues

### Low Match Quality

**Diagnosis:**
```plaintext
"Calculate match quality for recent purchase events"
"Identify which parameters are missing"
```

**Fix:**
```plaintext
"Review event parameter quality"
"Check which identifiers have highest match rates"
"Update implementation to include missing parameters"
```

### Campaign Not Delivering

**Diagnosis:**
```plaintext
"Get campaign delivery status"
"Check optimization event volume"
"Review targeting restrictions"
```

**Fix:**
```plaintext
"Verify sufficient conversion events"
"Broaden targeting if needed"
"Check budget adequacy"
```

### High CPAs

**Diagnosis:**
```plaintext
"Compare CPA across ad sets"
"Check event quality and match rate"
"Review creative performance"
```

**Fix:**
```plaintext
"Improve event quality if < 7.0"
"Pause underperforming ad sets"
"Test new creative approaches"
```

## Next Steps

- Review [Integration Guide](INTEGRATION.md)
- Read [Meta Ads Tools Reference](META_ADS_TOOLS.md)
- Check [Gateway MCP README](../gateway_mcp/README.md)
- Join [Discord community](https://discord.gg/YzMwQ8zrjr)

---

For audit support, email support@organized.ai
