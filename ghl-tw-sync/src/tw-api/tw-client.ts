/**
 * TripleWhale API Client
 * Handles authentication and API calls to TripleWhale Data-In API
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  TWConfig,
  TWOfflineEvent,
  TWBatchEventsRequest,
  TWEventsResponse,
  TWAPIError,
  TWUserData,
  TWCustomData,
  PushEventOptions,
  TWOrder,
  TWOrdersResponse,
} from '../types/triplewhale.js';

export class TWClient {
  private client: AxiosInstance;
  private config: TWConfig;

  constructor(config: TWConfig) {
    this.config = config;

    this.client = axios.create({
      baseURL: config.baseUrl,
      headers: {
        'x-api-key': config.apiKey,
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<TWAPIError>) => {
        if (error.response) {
          const errorMsg = error.response.data?.error?.message || error.message;
          throw new Error(`TripleWhale API Error (${error.response.status}): ${errorMsg}`);
        }
        throw new Error(`TripleWhale API Request Failed: ${error.message}`);
      }
    );
  }

  /**
   * Normalize user data to TripleWhale format (arrays)
   */
  private normalizeUserData(userData: Partial<PushEventOptions['userData']>): TWUserData {
    const normalized: TWUserData = {};

    if (userData.email) {
      normalized.email = [this.hashEmail(userData.email)];
    }
    if (userData.phone) {
      normalized.phone = [this.normalizePhone(userData.phone)];
    }
    if (userData.firstName) {
      normalized.first_name = [userData.firstName.toLowerCase().trim()];
    }
    if (userData.lastName) {
      normalized.last_name = [userData.lastName.toLowerCase().trim()];
    }
    if (userData.city) {
      normalized.city = [userData.city.toLowerCase().trim()];
    }
    if (userData.state) {
      normalized.state = [userData.state.toLowerCase().trim()];
    }
    if (userData.zipCode) {
      normalized.zip_code = [userData.zipCode.replace(/\s/g, '').toLowerCase()];
    }
    if (userData.country) {
      normalized.country = [userData.country.toLowerCase().trim()];
    }
    if (userData.externalId) {
      normalized.external_id = [userData.externalId];
    }

    return normalized;
  }

  /**
   * Hash email for privacy (simple lowercase for now, should use SHA256 in production)
   */
  private hashEmail(email: string): string {
    return email.toLowerCase().trim();
  }

  /**
   * Normalize phone number (remove non-digits)
   */
  private normalizePhone(phone: string): string {
    return phone.replace(/\D/g, '');
  }

  /**
   * Push a single offline event
   */
  async pushEvent(options: PushEventOptions): Promise<TWEventsResponse> {
    const userData = this.normalizeUserData(options.userData);

    const customData: TWCustomData = {};
    if (options.customData) {
      if (options.customData.currency) customData.currency = options.customData.currency;
      if (options.customData.value !== undefined) customData.value = options.customData.value;
      if (options.customData.contentName) customData.content_name = options.customData.contentName;
      if (options.customData.orderId) customData.order_id = options.customData.orderId;
    }

    const event: TWOfflineEvent = {
      event_name: options.eventName,
      event_time: options.eventTime ? Math.floor(options.eventTime.getTime() / 1000) : Math.floor(Date.now() / 1000),
      action_source: options.actionSource,
      user_data: userData,
      custom_data: Object.keys(customData).length > 0 ? customData : undefined,
    };

    const response = await this.client.post<TWEventsResponse>(
      '/data-in/pixel/offline-events',
      {
        data: [event],
      }
    );

    return response.data;
  }

  /**
   * Push multiple offline events in batch
   */
  async pushEvents(events: TWOfflineEvent[]): Promise<TWEventsResponse> {
    const batchRequest: TWBatchEventsRequest = {
      data: events,
    };

    const response = await this.client.post<TWEventsResponse>(
      '/data-in/pixel/offline-events',
      batchRequest
    );

    return response.data;
  }

  /**
   * Push events from a properly formatted JSON file
   */
  async pushEventsFromFile(events: TWOfflineEvent[]): Promise<TWEventsResponse> {
    return this.pushEvents(events);
  }

  /**
   * Validate an offline event structure
   */
  validateEvent(event: any): boolean {
    if (!event.event_name || typeof event.event_name !== 'string') {
      throw new Error('Missing or invalid event_name');
    }

    if (!event.event_time || typeof event.event_time !== 'number') {
      throw new Error('Missing or invalid event_time (must be Unix timestamp)');
    }

    if (!event.action_source || typeof event.action_source !== 'string') {
      throw new Error('Missing or invalid action_source');
    }

    if (!event.user_data || typeof event.user_data !== 'object') {
      throw new Error('Missing or invalid user_data');
    }

    // At least one user identifier required
    const hasIdentifier =
      event.user_data.email ||
      event.user_data.phone ||
      event.user_data.external_id;

    if (!hasIdentifier) {
      throw new Error('At least one user identifier required (email, phone, or external_id)');
    }

    return true;
  }

  /**
   * Push orders to TripleWhale data-in/orders endpoint
   * @param orders Array of orders to push
   * @returns Response with orders received count
   */
  async pushOrders(orders: TWOrder[]): Promise<TWOrdersResponse> {
    const response = await this.client.post<TWOrdersResponse>(
      '/api/v2/data-in/orders',
      orders
    );

    return response.data;
  }

  /**
   * Test the API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      // Try to push a test event (you might want to adjust this)
      const testEvent: TWOfflineEvent = {
        event_name: 'Connection Test',
        event_time: Math.floor(Date.now() / 1000),
        action_source: 'system_generated',
        user_data: {
          external_id: ['test'],
        },
      };

      await this.pushEvents([testEvent]);
      return true;
    } catch (error) {
      return false;
    }
  }
}

/**
 * Create a TripleWhale client instance from environment variables
 */
export function createTWClient(): TWClient {
  const apiKey = process.env.TW_API_KEY;
  const baseUrl = process.env.TW_API_BASE_URL || 'https://api.triplewhale.com';

  if (!apiKey) {
    throw new Error(
      'TW_API_KEY not found in environment variables. Please set it in your .env file.'
    );
  }

  return new TWClient({
    apiKey,
    baseUrl,
    shopId: process.env.TW_SHOP_ID,
  });
}
