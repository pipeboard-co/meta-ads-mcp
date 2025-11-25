#!/usr/bin/env tsx
import { config } from 'dotenv';
import * as readline from 'readline';
import https from 'https';

config();

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function exchangeCodeForToken(code: string, clientId: string, clientSecret: string): Promise<string> {
  const data = new URLSearchParams({
    code: code,
    client_id: clientId,
    client_secret: clientSecret,
    redirect_uri: 'http://localhost',
    grant_type: 'authorization_code'
  });

  return new Promise((resolve, reject) => {
    const req = https.request(
      'https://oauth2.googleapis.com/token',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(data.toString())
        }
      },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            if (json.refresh_token) {
              resolve(json.refresh_token);
            } else if (json.error) {
              reject(new Error(`OAuth error: ${json.error_description || json.error}`));
            } else {
              reject(new Error('No refresh token in response'));
            }
          } catch (error) {
            reject(error);
          }
        });
      }
    );

    req.on('error', reject);
    req.write(data.toString());
    req.end();
  });
}

async function main() {
  console.log('\n🔐 Google Ads OAuth2 Refresh Token Generator\n');

  const clientId = process.env.GOOGLE_ADS_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_ADS_CLIENT_SECRET;
  const developerToken = process.env.GOOGLE_ADS_DEVELOPER_TOKEN;

  if (!clientId || !clientSecret || !developerToken) {
    console.error('❌ Missing required environment variables.');
    console.error('Please set GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, and GOOGLE_ADS_DEVELOPER_TOKEN in .env');
    process.exit(1);
  }

  console.log('✅ Environment variables loaded\n');

  // Generate OAuth URL manually
  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
    `client_id=${encodeURIComponent(clientId)}` +
    `&redirect_uri=${encodeURIComponent('http://localhost')}` +
    `&scope=${encodeURIComponent('https://www.googleapis.com/auth/adwords')}` +
    `&response_type=code` +
    `&access_type=offline` +
    `&prompt=consent`;

  console.log('📋 Step 1: Open this URL in your browser:\n');
  console.log('\x1b[36m%s\x1b[0m', authUrl);
  console.log('\n📋 Step 2: Sign in and authorize the application');
  console.log('📋 Step 3: After redirect, copy the code from the URL');
  console.log('   Example: http://localhost/?code=4/0AY0e-g7xXxXxXx...');
  console.log('   Copy everything after "code=" and before "&scope"\n');

  const code = await question('Enter the authorization code: ');

  console.log('\n🔄 Exchanging code for refresh token...\n');

  try {
    const token = await exchangeCodeForToken(code.trim(), clientId, clientSecret);

    console.log('✅ Success! Your refresh token:\n');
    console.log('\x1b[32m%s\x1b[0m', token);
    console.log('\n📝 Add this to your .env file:');
    console.log('\x1b[33m%s\x1b[0m', `GOOGLE_ADS_REFRESH_TOKEN=${token}`);
    console.log('\n💡 The token has been copied above. Update your .env file now.\n');

  } catch (error: any) {
    console.error('❌ Error:', error.message);
    console.log('\n💡 Common issues:');
    console.log('  • Code expired (codes expire quickly, try again)');
    console.log('  • Code already used (get a new code)');
    console.log('  • Wrong client ID/secret in .env');
    process.exit(1);
  }

  rl.close();
}

main();
