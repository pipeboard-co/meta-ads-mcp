# Deploying Meta Ads MCP to Render

This guide walks you through deploying your Meta Ads MCP application to Render.

## Prerequisites

1. **Add Payment Information** (Required even for free tier)
   - Visit https://dashboard.render.com/billing
   - Add a credit card (you won't be charged if you use free/starter plans)

2. **Ensure Code is Pushed to GitHub**
   - Your repo: https://github.com/pipeboard-co/meta-ads-mcp
   - Branch: `main`

## Deployment Options

### Option 1: One-Click Deployment (Recommended)

Use the `render.yaml` blueprint file to deploy the entire stack with one click:

1. Visit: https://dashboard.render.com/select-repo
2. Select your repository: `pipeboard-co/meta-ads-mcp`
3. Render will automatically detect the `render.yaml` file
4. Review the services and click "Apply"

### Option 2: Manual Deployment via Render Dashboard

#### Step 1: Deploy Python Backend

1. Go to https://dashboard.render.com/web/new
2. Connect your GitHub repository: `pipeboard-co/meta-ads-mcp`
3. Configure the service:
   - **Name**: `meta-ads-mcp-backend`
   - **Region**: Ohio (US East)
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_http_server.py`
   - **Plan**: Starter ($7/month) or Free

4. Add Environment Variables:
   ```
   META_APP_ID=665587869862344
   META_APP_SECRET=2eebb6109153f476f9df8625d673917e
   POSTGRES_URL=postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   PYTHON_VERSION=3.11
   ```

5. Click "Create Web Service"

#### Step 2: Verify Backend Deployment

Once deployed, your backend will be available at:
- **URL**: `https://meta-ads-mcp-backend.onrender.com`
- **Health Check**: `https://meta-ads-mcp-backend.onrender.com/health`
- **MCP Endpoint**: `https://meta-ads-mcp-backend.onrender.com/mcp`

Test the health endpoint:
```bash
curl https://meta-ads-mcp-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "meta-ads-mcp",
  "tools": 30,
  "transport": "streamable-http-json",
  "auth": "PAT via Authorization header"
}
```

### Option 3: Deploy Using Render MCP (After Adding Payment)

Once payment info is added, you can use the Render MCP integration:

```bash
# This will be automated once payment is configured
```

## Next Steps: Deploy Frontend

After the backend is deployed successfully, deploy the Next.js frontend:

1. Go to https://dashboard.render.com/web/new
2. Select your repository: `pipeboard-co/meta-ads-mcp`
3. Configure:
   - **Name**: `meta-ads-mcp-frontend`
   - **Region**: Ohio (US East)
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: Node
   - **Build Command**: `corepack enable && pnpm install && pnpm build`
   - **Start Command**: `pnpm start`
   - **Plan**: Starter

4. Add Environment Variables:
   ```
   POSTGRES_URL=postgresql://neondb_owner:npg_0GKMQL1jJPBS@ep-lucky-sunset-adv3mq0g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   AUTH_SECRET=<generate-random-32-char-string>
   META_APP_ID=665587869862344
   META_APP_SECRET=2eebb6109153f476f9df8625d673917e
   NEXT_PUBLIC_META_APP_ID=665587869862344
   META_REDIRECT_URI=https://meta-ads-mcp-frontend.onrender.com/setup/callback
   NEXT_PUBLIC_MCP_SERVER_URL=https://meta-ads-mcp-backend.onrender.com/mcp
   ```

## Database Configuration

You're using **Neon PostgreSQL** (already configured):
- Connection string is included in the environment variables above
- No additional database setup needed on Render

## Update Meta App Configuration

After deployment, update your Meta App settings:

1. Go to https://developers.facebook.com/apps/665587869862344/settings/basic/
2. Update **OAuth Redirect URIs**:
   - Add: `https://meta-ads-mcp-frontend.onrender.com/setup/callback`
3. Update **App Domains**:
   - Add: `meta-ads-mcp-frontend.onrender.com`
   - Add: `meta-ads-mcp-backend.onrender.com`

## Monitoring & Logs

- **Backend Logs**: https://dashboard.render.com/web/meta-ads-mcp-backend/logs
- **Frontend Logs**: https://dashboard.render.com/web/meta-ads-mcp-frontend/logs
- **Metrics**: Available in each service's dashboard

## Troubleshooting

### Build Fails

1. Check the build logs in Render dashboard
2. Verify `requirements.txt` includes all dependencies
3. Ensure Python version is set correctly (3.11+)

### Service Won't Start

1. Check that `run_http_server.py` is in the root directory
2. Verify all required environment variables are set
3. Check the service logs for errors

### Database Connection Issues

1. Verify the Neon database connection string is correct
2. Ensure the database allows connections from Render's IP ranges
3. Test the connection string locally first

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_MCP_SERVER_URL` points to the correct backend URL
2. Check CORS settings in the backend
3. Ensure both services are in the same region (lower latency)

## Cost Estimate

- **Backend (Starter)**: $7/month (or Free with limitations)
- **Frontend (Starter)**: $7/month (or Free with limitations)
- **Database (Neon)**: Free tier (already configured)

**Total**: $0-14/month depending on plan selection

## Security Notes

⚠️ **Important**: The credentials in this file are currently hardcoded. For production:

1. Rotate your Meta App Secret regularly
2. Use Render's Secret Files feature for sensitive data
3. Enable environment variable encryption
4. Set up proper monitoring and alerts

## Support

- **Render Support**: https://render.com/docs
- **Your Repository**: https://github.com/pipeboard-co/meta-ads-mcp
- **Issues**: Report issues on your GitHub repo

