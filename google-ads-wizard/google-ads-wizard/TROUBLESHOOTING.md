# Troubleshooting Guide

## Error: "unauthorized_client"

This error typically occurs when:

### Issue 1: OAuth Client Configuration

The Google Cloud OAuth client needs to be properly configured:

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com/

2. **Navigate to Credentials**
   - APIs & Services → Credentials

3. **Check OAuth 2.0 Client Configuration**
   - Application type should be: **Desktop app** (NOT Web application)
   - If it's a Web application, the redirect URIs need to include `http://localhost`

4. **Fix:**
   - If wrong type: Create a new OAuth 2.0 Client ID
   - Choose "Desktop app"
   - Download the JSON credentials
   - Update your .env with the new CLIENT_ID and CLIENT_SECRET

### Issue 2: Developer Token Status

The developer token might be in test mode:

1. **Check Token Status**
   - Go to https://ads.google.com/
   - Tools & Settings → API Center
   - Check if token is "Under review" or "Test"

2. **Test Token Limitations:**
   - Test tokens only work with test manager accounts
   - Customer ID 8888034950 must be a test account
   - Check if your MCC (4761832056) is a test account

3. **Fix:**
   - If using test token: Ensure both MCC and customer account are test accounts
   - If production needed: Wait for Google to approve your developer token

### Issue 3: Redirect URI Mismatch

The redirect URI in the code must match Google Cloud Console:

1. **Current redirect URI:** `http://localhost`

2. **Check in Google Cloud Console:**
   - Credentials → OAuth 2.0 Client IDs → Click your client
   - Authorized redirect URIs should include: `http://localhost`

3. **Fix:**
   - Add `http://localhost` to authorized redirect URIs
   - OR use `urn:ietf:wg:oauth:2.0:oob` for manual code entry

### Solution Steps

**Option 1: Create New Desktop OAuth Client**

```bash
# 1. Go to Google Cloud Console
# https://console.cloud.google.com/apis/credentials

# 2. Create OAuth 2.0 Client ID
#    - Application type: Desktop app
#    - Name: Google Ads Wizard CLI

# 3. Download JSON credentials

# 4. Update .env with new credentials
GOOGLE_ADS_CLIENT_ID=<new-client-id>
GOOGLE_ADS_CLIENT_SECRET=<new-client-secret>

# 5. Get new refresh token
npm run get-token
```

**Option 2: Use Test Manager Account**

If your developer token is in "Test" mode:

```bash
# 1. Verify your MCC is a test account
# 2. Create a test customer account
# 3. Link test customer to test MCC
# 4. Use test customer ID instead of 8888034950
```

**Option 3: Manual OAuth Flow (Fallback)**

Update `scripts/get-refresh-token.ts` to use:

```typescript
redirect_uri: 'urn:ietf:wg:oauth:2.0:oob'
```

Then in Google Cloud Console:
- Add `urn:ietf:wg:oauth:2.0:oob` to authorized redirect URIs

---

## Quick Diagnostic

Run this to check your setup:

```bash
# Check environment variables
cat .env

# Expected:
# GOOGLE_ADS_DEVELOPER_TOKEN=hAZxzK3EmeT4ZrZixdGUgQ
# GOOGLE_ADS_CLIENT_ID=667496289341-...
# GOOGLE_ADS_CLIENT_SECRET=GOCSPX-...
# GOOGLE_ADS_REFRESH_TOKEN=1//04...
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=4761832056
```

---

## Alternative: Use Google Ads API Playground

Google provides an OAuth playground:

1. **Go to OAuth Playground**
   - https://developers.google.com/oauthplayground/

2. **Configure**
   - Click gear icon (top right)
   - Check "Use your own OAuth credentials"
   - Enter your CLIENT_ID and CLIENT_SECRET

3. **Authorize**
   - Select scopes: `https://www.googleapis.com/auth/adwords`
   - Click "Authorize APIs"
   - Exchange authorization code for tokens
   - Copy the refresh token

4. **Update .env**
   ```env
   GOOGLE_ADS_REFRESH_TOKEN=<token-from-playground>
   ```

---

## Common Issues

### "Getting metadata from plugin failed with error: invalid_grant"
- **Cause:** Refresh token is invalid or expired
- **Fix:** Run `npm run get-token` again

### "Getting metadata from plugin failed with error: unauthorized_client"
- **Cause:** OAuth client configuration mismatch
- **Fix:** Follow "Option 1" above to create new Desktop OAuth client

### "Developer token is invalid"
- **Cause:** Token not approved or wrong format
- **Fix:** Check token in Google Ads API Center

### "Customer not found"
- **Cause:** Customer ID doesn't exist or no access
- **Fix:** Verify customer ID in Google Ads UI

---

## Need More Help?

- **Google Ads API Documentation:** https://developers.google.com/google-ads/api/docs/oauth/overview
- **OAuth 2.0 for Desktop Apps:** https://developers.google.com/identity/protocols/oauth2/native-app
- **Google Ads API Forum:** https://groups.google.com/g/adwords-api

---

## Working Configuration Example

For reference, a working setup looks like:

```env
# OAuth Client (Desktop app type)
GOOGLE_ADS_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=GOCSPX-ABC123xyz

# Developer Token (Test or Approved)
GOOGLE_ADS_DEVELOPER_TOKEN=ABCdefGHI123_xyz

# OAuth Refresh Token (From npm run get-token)
GOOGLE_ADS_REFRESH_TOKEN=1//0gXxXxXxXxXxXx

# Manager Account ID
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
```

The key points:
- OAuth client must be "Desktop app" type
- Developer token must match account type (test/production)
- Refresh token must be obtained with correct client credentials
- Customer IDs must be accessible from the login customer ID
