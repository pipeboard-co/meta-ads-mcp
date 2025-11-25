# Easy Way to Get Refresh Token

## Using Google OAuth Playground (5 minutes)

This is the easiest and most reliable method.

### Step 1: Open OAuth Playground

Click this link: **https://developers.google.com/oauthplayground/**

### Step 2: Configure with Your Credentials

1. Click the **gear/settings icon** in the top-right corner
2. Check the box: **"Use your own OAuth credentials"**
3. Enter these values:

```
OAuth Client ID: your_client_id.apps.googleusercontent.com

OAuth Client secret: GOCSPX-your_client_secret
```

4. Click **"Close"**

### Step 3: Select Google Ads API Scope

1. In the left panel, find the text box under "Input your own scopes"
2. Paste this scope:
```
https://www.googleapis.com/auth/adwords
```
3. Click **"Authorize APIs"** button

### Step 4: Authorize

1. A Google sign-in window will appear
2. Sign in with your Google account (the one that has Google Ads access)
3. Click **"Allow"** to grant permissions
4. You'll be redirected back to the OAuth Playground

### Step 5: Exchange Authorization Code

1. Click the **"Exchange authorization code for tokens"** button
2. You'll see a JSON response on the right side

### Step 6: Copy the Refresh Token

1. In the JSON response, find the line that says: `"refresh_token": "1//0gXxXxXxXxXxXx..."`
2. Copy the entire token (everything between the quotes)
3. It will look like: `1//04fdR_lZO_V4oCgYIARAAGAQSNwF-L9Ir...`

### Step 7: Update .env File

Send me the refresh token and I'll update your .env file, or you can do it manually:

```env
GOOGLE_ADS_REFRESH_TOKEN=1//04fdR_lZO_V4oCgYIARAAGAQSNwF-L9Ir...
```

---

## Alternative: I Can Guide You Through It Live

If you'd prefer, you can:
1. Open the OAuth Playground link above
2. Follow steps 1-5
3. Share the authorization code with me (NOT the refresh token yet)
4. I can help exchange it for the refresh token

---

## Quick Start Link

Click here to go directly to OAuth Playground:
👉 **https://developers.google.com/oauthplayground/**

Then follow the steps above!
