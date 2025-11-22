# Google Ads Wizard - Setup Guide

Complete guide to get your Google Ads Wizard CLI up and running.

## Prerequisites

- Node.js 18+ installed
- Google Ads account with API access
- Anthropic API key (Claude)
- Google Ads Manager Account (MCC) or direct account access

---

## Step 1: Get Google Ads OAuth Refresh Token

The Google Ads API requires OAuth2 authentication. You need to generate a refresh token.

### 1.1 Verify Your Credentials

Check your `.env` file has these values (from the build guide):

```env
GOOGLE_ADS_DEVELOPER_TOKEN=hAZxzK3EmeT4ZrZixdGUgQ
GOOGLE_ADS_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=GOCSPX-your_client_secret
GOOGLE_ADS_LOGIN_CUSTOMER_ID=4761832056
```

### 1.2 Run the Token Generator

```bash
npm run get-token
```

This will:
1. Generate an OAuth authorization URL
2. Open it in your browser
3. Ask you to authorize the application
4. Provide you with a refresh token

### 1.3 Authorize the Application

1. Copy the URL from the terminal
2. Open it in your browser
3. Sign in with your Google Ads account
4. Click "Allow" to grant permissions
5. Copy the authorization code from the redirect URL (it will be in the URL bar after `code=`)

Example redirect URL:
```
http://localhost/?code=4/0AY0e-g7xXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx&scope=https://www.googleapis.com/auth/adwords
```

Copy everything after `code=` and before `&scope`

### 1.4 Update Your .env

Add the refresh token to your `.env`:

```env
GOOGLE_ADS_REFRESH_TOKEN=1//0gXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx
```

---

## Step 2: Verify Anthropic API Key

Make sure your `.env` has your Claude API key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get your API key from: https://console.anthropic.com/

---

## Step 3: Test the Setup

### Test 1: Verify Environment

```bash
npm run dev setup
```

This shows your configuration and documentation links.

### Test 2: List Campaigns (Simple Test)

```bash
npm run dev -- campaigns 8888034950
```

This fetches campaigns for customer ID 8888034950 (Carrara).

If successful, you'll see:
- Account name
- Campaign list with performance metrics
- Status, budget, clicks, conversions

### Test 3: Run Full Audit

```bash
npm run dev -- audit 8888034950
```

This will:
1. Fetch all account data
2. Analyze with Claude Sonnet 4 (temperature 0)
3. Generate RTT-style PDF report
4. Create `.cursor/rules` context file

Expected output:
```
✅ Audit Complete!

Account: Carrara Treatment Center
Health Score: 7/10
Critical Issues: 3
Recommendations: 8

📁 Files Generated:
  • Report: ./audit-report.pdf
  • Context: ./.cursor/rules
```

---

## Troubleshooting

### Error: "invalid_grant"

**Cause:** Refresh token is invalid or expired

**Solution:**
1. Run `npm run get-token` again
2. Generate a new refresh token
3. Update `.env` with the new token

### Error: "Missing required Google Ads API credentials"

**Cause:** .env file not loaded or missing values

**Solution:**
1. Verify `.env` exists in the project root
2. Check all required fields are filled
3. Don't use quotes around values in .env

### Error: "ANTHROPIC_API_KEY not found"

**Cause:** Missing or invalid Claude API key

**Solution:**
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-api03-...`

### Error: "Customer not found" or "Permission denied"

**Cause:** Customer ID not accessible with your credentials

**Solution:**
1. Verify the customer ID is correct
2. Make sure your Google Ads account has access
3. Check GOOGLE_ADS_LOGIN_CUSTOMER_ID is your MCC ID

---

## Common Customer IDs

Based on your setup:

- **Carrara Treatment Center:** 8888034950
- **Login MCC Account:** 4761832056

---

## Next Steps After Setup

1. **Run Regular Audits**
   ```bash
   npm run dev -- audit 8888034950 --output audit-$(date +%Y%m%d).pdf
   ```

2. **Check Campaign Performance**
   ```bash
   npm run dev -- campaigns 8888034950 --status active
   ```

3. **Review .cursor/rules**
   - Auto-generated AI context
   - Updates with each audit
   - Helps AI assistants understand your account

4. **Export to JSON for Analysis**
   ```bash
   npm run dev -- audit 8888034950 --format json
   ```

---

## Google Ads API Setup (If Needed)

If you need to set up Google Ads API access from scratch:

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create new project

2. **Enable Google Ads API**
   - Navigate to APIs & Services
   - Enable "Google Ads API"

3. **Create OAuth2 Credentials**
   - Go to Credentials
   - Create OAuth 2.0 Client ID
   - Application type: Desktop app
   - Save Client ID and Client Secret

4. **Get Developer Token**
   - Go to https://ads.google.com/
   - Tools & Settings → API Center
   - Request developer token
   - Note: Test accounts work immediately, production requires approval

5. **Update .env with your credentials**

---

## Support & Documentation

- **Google Ads API Docs:** https://developers.google.com/google-ads/api/docs/start
- **Anthropic API Docs:** https://docs.anthropic.com/en/api/getting-started
- **OAuth2 Guide:** https://developers.google.com/google-ads/api/docs/oauth/overview

---

## Quick Reference

```bash
# Get refresh token (one-time setup)
npm run get-token

# List campaigns
npm run dev -- campaigns <customer-id>

# Run audit (PDF)
npm run dev -- audit <customer-id>

# Run audit (JSON)
npm run dev -- audit <customer-id> --format json

# Show help
npm run dev -- --help

# Show command help
npm run dev -- audit --help
```

---

**You're all set!** 🚀

Run `npm run dev -- audit 8888034950` to generate your first audit.
