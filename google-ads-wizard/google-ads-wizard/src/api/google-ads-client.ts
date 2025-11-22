import https from 'https';

export interface GoogleAdsConfig {
  developer_token: string;
  client_id: string;
  client_secret: string;
  refresh_token: string;
}

const API_VERSION = 'v19';

async function getAccessToken(config: GoogleAdsConfig): Promise<string> {
  const data = new URLSearchParams({
    client_id: config.client_id,
    client_secret: config.client_secret,
    refresh_token: config.refresh_token,
    grant_type: 'refresh_token'
  });

  return new Promise((resolve, reject) => {
    const req = https.request(
      'https://oauth2.googleapis.com/token',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        }
      },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            if (json.access_token) {
              resolve(json.access_token);
            } else {
              reject(new Error(`Failed to get access token: ${JSON.stringify(json)}`));
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

async function executeQuery(accessToken: string, developerToken: string, customerId: string, loginCustomerId: string, query: string): Promise<any> {
  const url = `https://googleads.googleapis.com/${API_VERSION}/customers/${customerId}/googleAds:search`;

  const data = JSON.stringify({ query });

  return new Promise((resolve, reject) => {
    const req = https.request(
      url,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'developer-token': developerToken,
          'login-customer-id': loginCustomerId,
          'Content-Type': 'application/json',
        }
      },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          if (res.statusCode === 200) {
            try {
              resolve(JSON.parse(body));
            } catch (error) {
              reject(new Error(`Failed to parse response: ${body}`));
            }
          } else {
            reject(new Error(`API request failed (${res.statusCode}): ${body}`));
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

export function createGoogleAdsClient() {
  const config: GoogleAdsConfig = {
    developer_token: process.env.GOOGLE_ADS_DEVELOPER_TOKEN || '',
    client_id: process.env.GOOGLE_ADS_CLIENT_ID || '',
    client_secret: process.env.GOOGLE_ADS_CLIENT_SECRET || '',
    refresh_token: process.env.GOOGLE_ADS_REFRESH_TOKEN || '',
  };

  const loginCustomerId = process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID || '';

  // Validate required credentials
  if (!config.developer_token || !config.client_id || !config.client_secret || !config.refresh_token) {
    throw new Error('Missing required Google Ads API credentials. Check your .env file.');
  }

  let accessToken: string | null = null;

  async function getToken(): Promise<string> {
    if (!accessToken) {
      accessToken = await getAccessToken(config);
    }
    return accessToken;
  }

  return {
    async getAccountInfo(customerId: string) {
      const token = await getToken();

      const query = `
        SELECT
          customer.id,
          customer.descriptive_name,
          customer.currency_code,
          customer.time_zone,
          customer.status
        FROM customer
        LIMIT 1
      `;

      const result = await executeQuery(token, config.developer_token, customerId, loginCustomerId, query);

      if (result.results && result.results.length > 0) {
        return result.results[0].customer;
      }
      throw new Error('No account information found');
    },

    async getCampaigns(customerId: string) {
      const token = await getToken();

      const query = `
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.advertising_channel_type,
          campaign.bidding_strategy_type,
          campaign_budget.amount_micros,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.ctr,
          metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
      `;

      const result = await executeQuery(token, config.developer_token, customerId, loginCustomerId, query);
      return result.results || [];
    },

    async getPerformanceMetrics(customerId: string) {
      const token = await getToken();

      const query = `
        SELECT
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value,
          metrics.ctr,
          metrics.average_cpc,
          metrics.average_cpm,
          metrics.cost_per_conversion
        FROM customer
        WHERE segments.date DURING LAST_30_DAYS
      `;

      const result = await executeQuery(token, config.developer_token, customerId, loginCustomerId, query);

      if (result.results && result.results.length > 0) {
        return result.results[0].metrics;
      }
      return {};
    },

    async getKeywordPerformance(customerId: string) {
      const token = await getToken();

      const query = `
        SELECT
          ad_group.id,
          ad_group.name,
          ad_group_criterion.keyword.text,
          ad_group_criterion.keyword.match_type,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.ctr,
          metrics.quality_score
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
          AND metrics.impressions > 0
        ORDER BY metrics.cost_micros DESC
        LIMIT 100
      `;

      try {
        const result = await executeQuery(token, config.developer_token, customerId, loginCustomerId, query);
        return result.results || [];
      } catch (error) {
        return [];
      }
    },

    async getConversionTracking(customerId: string) {
      const token = await getToken();

      const query = `
        SELECT
          conversion_action.id,
          conversion_action.name,
          conversion_action.type,
          conversion_action.status,
          conversion_action.primary_for_goal,
          metrics.conversions,
          metrics.conversions_value
        FROM conversion_action
      `;

      try {
        const result = await executeQuery(token, config.developer_token, customerId, loginCustomerId, query);
        return result.results || [];
      } catch (error) {
        return [];
      }
    },
  };
}
