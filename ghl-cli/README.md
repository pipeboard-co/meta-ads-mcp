# GoHighLevel CLI Tool

Command-line interface for managing GoHighLevel contacts and opportunities.

## Features

- List and export contacts
- List and export opportunities
- Filter by status, pipeline, tags
- Export data to JSON format
- Rate limit handling (100 req/10s)
- Beautiful terminal output with colors

## Installation

```bash
cd ghl-cli
npm install
```

## Configuration

Create a `.env` file in the project root:

```env
GHL_API_KEY=your_api_key_here
GHL_LOCATION_ID=your_default_location_id (optional)
GHL_API_BASE_URL=https://rest.gohighlevel.com
```

### Getting Your API Key

1. Log in to your GoHighLevel account
2. Go to Settings → Integrations → API
3. Create a new API key or use an existing one
4. Copy the API key and add it to your `.env` file

## Usage

### Setup and Configuration

Check your configuration:

```bash
npm run dev setup
```

This will display:
- API key status
- Location ID status
- Base URL
- Quick start examples

### List Contacts

**Basic usage:**
```bash
npm run dev -- contacts <location-id>
```

**With options:**
```bash
# Limit results
npm run dev -- contacts <location-id> --limit 50

# Search by query
npm run dev -- contacts <location-id> --query "john@example.com"

# Filter by tags
npm run dev -- contacts <location-id> --tags "customer" "vip"

# Export to JSON
npm run dev -- contacts <location-id> --export contacts.json
```

**Example output:**
```
Contacts:
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID                       | Name                      | Email                          | Phone           | Tags
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
abc123...                | John Doe                  | john@example.com               | 555-1234        | customer, vip
def456...                | Jane Smith                | jane@example.com               | 555-5678        | lead

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Total Contacts: 2
```

### List Opportunities

**Basic usage:**
```bash
npm run dev -- opportunities <location-id>
```

**With options:**
```bash
# Limit results
npm run dev -- opportunities <location-id> --limit 50

# Filter by status (open, won, lost, abandoned, all)
npm run dev -- opportunities <location-id> --status won

# Filter by pipeline
npm run dev -- opportunities <location-id> --pipeline <pipeline-id>

# Export to JSON
npm run dev -- opportunities <location-id> --export opportunities.json
```

**Example output:**
```
Opportunities:
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
ID                       | Name                           | Status     | Value        | Contact
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
opp123...                | Website Redesign               | won        | $5,000       | abc123...
opp456...                | SEO Package                    | open       | $2,500       | def456...

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Total Opportunities: 2
Total Value: $7,500

📊 Summary:
  Total: 2
  Open: 1
  Won: 1
  Lost: 0
  Total Value: $7,500
```

## Command Reference

### `contacts <location-id>`

List contacts for a specific location.

**Arguments:**
- `location-id` - GHL Location ID (required)

**Options:**
- `-l, --limit <number>` - Limit number of contacts (default: 100)
- `-q, --query <query>` - Search query (email, phone, name)
- `-t, --tags <tags...>` - Filter by tags (space-separated)
- `-e, --export <file>` - Export to JSON file

### `opportunities <location-id>`

List opportunities for a specific location.

**Arguments:**
- `location-id` - GHL Location ID (required)

**Options:**
- `-l, --limit <number>` - Limit number of opportunities (default: 100)
- `-p, --pipeline <pipeline-id>` - Filter by pipeline ID
- `-s, --status <status>` - Filter by status: open, won, lost, abandoned, all (default: all)
- `-e, --export <file>` - Export to JSON file

### `setup`

Display configuration and help information.

## API Rate Limits

GoHighLevel API has the following rate limits:

- **100 requests per 10 seconds**

The CLI automatically handles rate limiting and will pause if you approach the limit.

## Export Format

Exported JSON files include metadata:

```json
{
  "exportedAt": "2025-01-15T10:30:00.000Z",
  "type": "contacts",
  "count": 150,
  "data": [
    {
      "id": "contact_id",
      "locationId": "location_id",
      "contactName": "John Doe",
      "email": "john@example.com",
      "phone": "555-1234",
      "tags": ["customer", "vip"],
      "dateAdded": "2025-01-01T00:00:00.000Z"
    }
  ]
}
```

## Architecture

```
ghl-cli/
├── src/
│   ├── api/
│   │   └── ghl-client.ts      # GHL API client with rate limiting
│   ├── commands/
│   │   ├── contacts.ts         # Contacts command
│   │   └── opportunities.ts    # Opportunities command
│   ├── types/
│   │   └── ghl.ts             # TypeScript type definitions
│   ├── utils/
│   │   ├── formatter.ts        # Terminal output formatting
│   │   └── export.ts           # JSON export utilities
│   └── index.ts                # CLI entry point
├── .env                        # Configuration (not in git)
├── .env.example                # Example configuration
├── package.json
├── tsconfig.json
└── README.md
```

## Development

### Build

```bash
npm run build
```

This compiles TypeScript to the `dist/` folder.

### Run in Development Mode

```bash
npm run dev -- <command> [options]
```

### Run in Production Mode

```bash
npm start <command> [options]
```

## Troubleshooting

### Error: "GHL_API_KEY not found"

Make sure you have a `.env` file in the project root with your API key:

```env
GHL_API_KEY=your_api_key_here
```

### Error: "GHL API Error (401)"

Your API key is invalid or expired. Get a new API key from your GHL account.

### Error: "GHL API Error (403)"

Your API key doesn't have permission to access the requested resource. Check your API key permissions in GHL.

### Error: "Rate limit approaching"

The CLI automatically handles rate limiting. Wait for the message to complete.

## GoHighLevel API Documentation

- **Official API Docs:** https://highlevel.stoplight.io/docs/integrations
- **OAuth Guide:** https://highlevel.stoplight.io/docs/integrations/0443d7d1a4bd0-overview
- **Contacts API:** https://highlevel.stoplight.io/docs/integrations/7c07dd64f1dac-get-contact
- **Opportunities API:** https://highlevel.stoplight.io/docs/integrations/0aec99efe44ce-get-opportunity

## Integration with TripleWhale

This CLI tool is designed to work with the GHL-TripleWhale sync tool (coming in Phase 3):

1. Use this CLI to export contacts and opportunities to JSON
2. Use the sync tool to push that data to TripleWhale attribution dashboard
3. Combine GHL CRM data with TripleWhale analytics

## Next Steps

- Week 2: Build TripleWhale CLI tool for pushing offline events
- Week 3: Create GHL-TW sync tool with automatic data transformation
- Week 4: Testing and comprehensive documentation

## License

MIT

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the GoHighLevel API docs
- Contact support
