# Google Ads Wizard CLI

AI-powered Google Ads auditing tool that generates RTT-style PDF reports using Claude Sonnet 4.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Get Google Ads OAuth Token:**
   ```bash
   npm run get-token
   # Follow the prompts to generate refresh token
   # Add the token to your .env file
   ```

4. **Test the CLI:**
   ```bash
   npm run dev -- campaigns 8888034950
   ```

📖 **Need help?** See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed setup instructions.

## Available Commands

### 1. Audit
Generate comprehensive RTT-style audit report
```bash
npm run dev -- audit <customer-id>
npm run dev -- audit 8888034950 --format pdf
npm run dev -- audit 8888034950 --compare-meta
```

### 2. Campaigns
List campaigns with performance metrics
```bash
npm run dev -- campaigns <customer-id>
npm run dev -- campaigns 8888034950 --status active
```

### 3. Compare
Cross-platform comparison (Google Ads vs Meta Ads)
```bash
npm run dev -- compare <google-id> <meta-id>
```

### 4. Setup
Interactive credential setup wizard
```bash
npm run dev setup
```

## Development

```bash
# Watch mode (auto-reload)
npm run dev

# Build TypeScript
npm run build

# Run built version
npm start
```

## Project Structure

```
src/
├── index.ts              # CLI entry point
├── api/                  # Google Ads API client
├── analysis/             # Claude AI integration
├── prompts/              # Deterministic prompts (temp 0)
├── generators/           # PDF/Markdown report generators
├── integrations/         # Pipeboard Meta MCP integration
└── utils/                # .cursor/rules generator, formatting
```

## Phase 1 Complete ✅

- [x] Project structure created
- [x] Dependencies installed
- [x] TypeScript configured
- [x] CLI entry point implemented
- [x] All 4 commands scaffolded
- [x] Build system working

## Next: Phase 2

Implement core functionality:
- Google Ads API client
- Claude AI integration
- Audit analysis
- Data formatting

## Documentation

- [Google Ads API Docs](https://developers.google.com/google-ads/api/docs/start)
- [Anthropic API Docs](https://docs.anthropic.com/en/api/getting-started)
- [Build Guide](./docs/build-guide.md)
