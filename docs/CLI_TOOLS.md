# CLI Tools Documentation

Complete guide to using the Fix Your Tracking CLI tools for direct platform integration and data synchronization.

## Overview

The Fix Your Tracking repository includes four powerful CLI tools for managing advertising platforms and CRM data:

1. **ghl-cli** - GoHighLevel contacts and opportunities management
2. **triplewhale-cli** - TripleWhale attribution and offline event tracking
3. **ghl-tw-sync** - Automated data synchronization between GoHighLevel and TripleWhale
4. **google-ads-wizard** - AI-powered Google Ads campaign auditing and management

All CLI tools are built with TypeScript, featuring:
- Beautiful terminal output with colors and progress indicators
- JSON export capabilities
- Environment-based configuration
- Rate limiting and error handling
- Comprehensive type safety

---

## 🔧 ghl-cli - GoHighLevel Management

### Overview
Command-line tool for managing GoHighLevel contacts and opportunities with filtering, export, and beautiful terminal output.

### Installation

```bash
cd ghl-cli
npm install
```

### Configuration

Create a `.env` file:

```env
GHL_API_KEY=your_api_key_here
GHL_LOCATION_ID=your_default_location_id
GHL_API_BASE_URL=https://rest.gohighlevel.com
```

**Getting Your API Key:**
1. Log in to GoHighLevel
2. Go to Settings → Integrations → API
3. Create or copy an API key
4. Add to `.env` file

### Commands

#### Setup & Configuration
```bash
npm run dev setup
```
Displays API key status, location ID, and validates configuration.

#### Contacts Management

**List all contacts:**
```bash
npm run dev contacts list --location-id <location_id>
```

**Filter contacts by status:**
```bash
npm run dev contacts list --location-id <location_id> --status active
```

**Export contacts to JSON:**
```bash
npm run dev contacts list --export contacts.json
npm run dev contacts list --location-id <location_id> --export filtered_contacts.json
```

#### Opportunities Management

**List all opportunities:**
```bash
npm run dev opportunities list --location-id <location_id>
```

**Filter by pipeline:**
```bash
npm run dev opportunities list --pipeline-id <pipeline_id>
```

**Filter by status:**
```bash
npm run dev opportunities list --status won
npm run dev opportunities list --status open
npm run dev opportunities list --status lost
```

**Export opportunities:**
```bash
npm run dev opportunities list --status won --export won_deals.json
```

### Features
- Rate limiting (100 requests/10 seconds)
- Pagination handling
- Tag filtering
- Custom field support
- JSON export with formatting
- Beautiful terminal output with chalk and ora

### Rate Limits
- GoHighLevel API: 100 requests per 10 seconds
- Automatic rate limit handling with delays
- Progress indicators for long operations

---

## 📊 triplewhale-cli - TripleWhale Attribution

### Overview
Push offline conversion events and view attribution metrics for e-commerce analytics.

### Installation

```bash
cd triplewhale-cli
npm install
```

### Configuration

Create a `.env` file:

```env
TW_API_KEY=your_triplewhale_api_key
TW_SHOP_ID=your_shopify_shop_id
TW_API_BASE_URL=https://api.triplewhale.com
```

**Getting Your API Key:**
1. Log in to TripleWhale
2. Navigate to Settings → API
3. Generate an API key
4. Copy to `.env` file

### Commands

#### Push Single Event
```bash
npm run dev push-event --shop <shop_id> --event <event_type> --value <value>
```

**Example:**
```bash
npm run dev push-event --shop mystore --event purchase --value 299.99
```

**Event Types:**
- `purchase` - Completed purchase
- `add_to_cart` - Item added to cart
- `initiate_checkout` - Checkout started
- `view_content` - Product viewed
- `custom` - Custom event

#### Push Batch Events

Create a JSON file with events:

```json
[
  {
    "event": "purchase",
    "value": 299.99,
    "email": "customer@example.com",
    "timestamp": "2024-01-15T10:30:00Z",
    "properties": {
      "order_id": "12345",
      "product_id": "ABC123"
    }
  },
  {
    "event": "purchase",
    "value": 149.99,
    "email": "another@example.com",
    "timestamp": "2024-01-15T11:45:00Z"
  }
]
```

Push the batch:
```bash
npm run dev push-events --file events.json
```

### Features
- Single and batch event pushing
- JSON file import
- Attribution metrics viewing
- Progress tracking for batches
- Error handling and retry logic
- Event validation

### Use Cases
- Push offline sales to attribution dashboard
- Import historical conversion data
- Sync CRM conversions to TripleWhale
- Track phone orders and offline events

---

## 🔄 ghl-tw-sync - Data Synchronization

### Overview
Automated synchronization tool that transforms GoHighLevel opportunities into TripleWhale attribution events.

### Installation

```bash
cd ghl-tw-sync
npm install
```

### Configuration

Create a `.env` file with credentials for both platforms:

```env
# GoHighLevel Configuration
GHL_API_KEY=your_ghl_api_key
GHL_LOCATION_ID=your_location_id
GHL_API_BASE_URL=https://rest.gohighlevel.com

# TripleWhale Configuration
TW_API_KEY=your_triplewhale_api_key
TW_SHOP_ID=your_shop_id
TW_API_BASE_URL=https://api.triplewhale.com

# Sync Configuration
SYNC_INTERVAL_HOURS=24
SYNC_BATCH_SIZE=100
```

### Commands

#### Test Connection
```bash
npm run dev test
```
Validates API keys and connectivity for both platforms.

#### Sync Opportunities

**Sync last 30 days:**
```bash
npm run dev sync --days 30
```

**Sync specific date range:**
```bash
npm run dev sync --start-date 2024-01-01 --end-date 2024-01-31
```

**Sync with custom batch size:**
```bash
npm run dev sync --days 7 --batch-size 50
```

#### Import from CSV

Create a CSV file with GoHighLevel opportunities:

```csv
id,contact_email,monetary_value,status,pipeline_id,created_at
opp_123,customer@example.com,299.99,won,pipe_abc,2024-01-15T10:30:00Z
opp_124,buyer@example.com,149.99,won,pipe_abc,2024-01-15T11:45:00Z
```

Import:
```bash
npm run dev import-csv --file opportunities.csv
```

### Data Transformation

The sync engine automatically transforms GHL data to TripleWhale format:

**GoHighLevel Opportunity →**
```json
{
  "id": "opp_123",
  "contact": {
    "email": "customer@example.com"
  },
  "monetaryValue": 299.99,
  "status": "won",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**→ TripleWhale Event**
```json
{
  "event": "purchase",
  "email": "customer@example.com",
  "value": 299.99,
  "timestamp": "2024-01-15T10:30:00Z",
  "properties": {
    "source": "gohighlevel",
    "opportunity_id": "opp_123",
    "status": "won"
  }
}
```

### Features
- Automated bi-directional sync
- Smart deduplication
- Progress tracking with cli-progress
- Error logging and recovery
- Configurable sync intervals
- CSV import/export
- Dry-run mode
- Incremental sync support

### Scheduling

Use cron for automated syncing:

```bash
# Sync every 6 hours
0 */6 * * * cd /path/to/ghl-tw-sync && npm run dev sync --days 1

# Daily full sync at midnight
0 0 * * * cd /path/to/ghl-tw-sync && npm run dev sync --days 7
```

### Documentation
See [TRIPLEWHALE_DATA_IN_DOCS.md](../ghl-tw-sync/TRIPLEWHALE_DATA_IN_DOCS.md) for detailed TripleWhale API documentation and data mapping.

---

## 🎯 google-ads-wizard - Google Ads CLI

### Overview
AI-powered CLI for Google Ads campaign management, auditing, and optimization using Claude Sonnet 4.

### Installation

```bash
cd google-ads-wizard/google-ads-wizard
npm install
```

### Configuration

Create a `.env` file:

```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_oauth_client_id
GOOGLE_ADS_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_account_id
ANTHROPIC_API_KEY=your_claude_api_key
```

**Setup Guide:** See [GET_TOKEN_EASY.md](../google-ads-wizard/google-ads-wizard/GET_TOKEN_EASY.md)

### Commands

#### List Campaigns
```bash
npm run dev campaigns list --account-id <customer_id>
```

**With filters:**
```bash
npm run dev campaigns list --account-id <customer_id> --status ENABLED
npm run dev campaigns list --account-id <customer_id> --type SEARCH
```

#### Run AI-Powered Audit

**Generate PDF report:**
```bash
npm run dev audit --account-id <customer_id> --output audit-report.pdf
```

**Export to JSON:**
```bash
npm run dev audit --account-id <customer_id> --output audit-data.json --format json
```

**Audit with specific date range:**
```bash
npm run dev audit --account-id <customer_id> \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --output january-audit.pdf
```

### Audit Features

The AI-powered audit uses Claude Sonnet 4 to analyze:

**RTT Methodology:**
1. **Tracking** - Conversion tracking setup and accuracy
2. **Targeting** - Audience targeting and optimization
3. **Testing** - Creative testing and experimentation

**Report Includes:**
- Campaign performance metrics
- Budget utilization analysis
- Targeting recommendations
- Creative performance insights
- Conversion tracking validation
- Optimization opportunities
- Action items prioritized by impact

### Features
- Campaign listing with performance metrics
- AI-powered audits with Claude Sonnet 4
- PDF and JSON report generation
- GAQL query builder
- Conversion tracking validation
- Auto-generated .cursor/rules AI context
- Bulk operations support

### Documentation
- [MCP_MIGRATION.md](../google-ads-wizard/google-ads-wizard/MCP_MIGRATION.md) - MCP server setup
- [PHASE1_COMPLETE.md](../google-ads-wizard/google-ads-wizard/PHASE1_COMPLETE.md) - Development log
- [PHASE2_COMPLETE.md](../google-ads-wizard/google-ads-wizard/PHASE2_COMPLETE.md) - Advanced features
- [docs/google_ads/](../docs/google_ads/) - API reference and GAQL guides

---

## 🔗 Integration Workflows

### Workflow 1: CRM to Attribution Pipeline

Sync GoHighLevel opportunities to TripleWhale for complete attribution:

```bash
# Step 1: Test connections
cd ghl-tw-sync
npm run dev test

# Step 2: Initial historical sync
npm run dev sync --days 90

# Step 3: Set up daily sync (add to cron)
0 2 * * * cd /path/to/ghl-tw-sync && npm run dev sync --days 1
```

### Workflow 2: Multi-Platform Audit

Audit both Google Ads and Meta campaigns:

```bash
# Google Ads audit
cd google-ads-wizard/google-ads-wizard
npm run dev audit --account-id <google_account> --output google-audit.pdf

# Meta Ads audit (via Claude + MCP)
# Use Claude Desktop with Meta Ads MCP to audit Meta campaigns
```

### Workflow 3: Export All CRM Data

Export contacts and opportunities for analysis:

```bash
# Export contacts
cd ghl-cli
npm run dev contacts list --export contacts.json

# Export won opportunities
npm run dev opportunities list --status won --export won_deals.json

# Export open opportunities
npm run dev opportunities list --status open --export pipeline.json
```

---

## 🛠️ Troubleshooting

### Common Issues

**Rate Limiting:**
- GHL: 100 req/10s limit enforced automatically
- TripleWhale: Check API tier limits
- Google Ads: 15K operations/day free tier

**Authentication Errors:**
- Verify API keys in `.env` files
- Check key permissions and scopes
- Refresh OAuth tokens if expired

**Connection Issues:**
- Test with `npm run dev test` commands
- Verify API base URLs
- Check firewall/proxy settings

**Data Sync Issues:**
- Check data format in CSV imports
- Verify email addresses are valid
- Review error logs in `sync.log`

### Debug Mode

Enable verbose logging:

```bash
# Add to .env
DEBUG=true
LOG_LEVEL=verbose

# Run commands
npm run dev sync --days 7 --debug
```

---

## 📈 Best Practices

### Data Export
- Export data regularly for backups
- Use filters to reduce API calls
- Schedule exports during off-peak hours

### Synchronization
- Start with small date ranges
- Monitor sync logs for errors
- Use test mode before production
- Schedule syncs during low-traffic hours

### API Keys
- Never commit `.env` files to git
- Rotate API keys quarterly
- Use separate keys for dev/prod
- Set minimum required permissions

### Performance
- Use batch operations when possible
- Implement caching for frequent queries
- Monitor API usage and limits
- Optimize query filters

---

## 🔐 Security

### API Key Management
- Store keys in `.env` files (gitignored)
- Use environment variables in production
- Implement key rotation policies
- Monitor for unauthorized access

### Data Privacy
- Encrypt exports containing PII
- Comply with GDPR/CCPA requirements
- Limit data retention periods
- Implement access controls

### Network Security
- Use HTTPS for all API calls
- Validate SSL certificates
- Implement request signing
- Use IP whitelisting where available

---

## 📝 Contributing

To add new CLI tools or enhance existing ones:

1. Follow the existing TypeScript structure
2. Use commander.js for CLI framework
3. Implement proper error handling
4. Add progress indicators for long operations
5. Include `.env.example` with all required variables
6. Write comprehensive README.md
7. Add unit tests

---

## 📚 Additional Resources

- [GoHighLevel API Docs](https://highlevel.stoplight.io/)
- [TripleWhale API Docs](https://developers.triplewhale.com/)
- [Google Ads API Docs](https://developers.google.com/google-ads/api/docs/start)
- [Commander.js Docs](https://github.com/tj/commander.js/)
- [Chalk (Terminal Colors)](https://github.com/chalk/chalk)

---

Made with ❤️ by [Organized AI](https://organized.ai)
