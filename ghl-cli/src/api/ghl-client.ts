/**
 * GoHighLevel API Client
 * Handles authentication and API calls to GHL REST API
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  GHLConfig,
  GHLContact,
  GHLContactsResponse,
  GHLOpportunity,
  GHLOpportunitiesResponse,
  GHLPipeline,
  GHLAPIError,
  ContactsQueryParams,
  OpportunitiesQueryParams,
} from '../types/ghl.js';

export class GHLClient {
  private client: AxiosInstance;
  private config: GHLConfig;
  private requestCount: number = 0;
  private requestWindow: number = Date.now();

  constructor(config: GHLConfig) {
    this.config = config;

    this.client = axios.create({
      baseURL: config.baseUrl,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Version': '2021-07-28',
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<GHLAPIError>) => {
        if (error.response) {
          const errorMsg = error.response.data?.message || error.message;
          throw new Error(`GHL API Error (${error.response.status}): ${errorMsg}`);
        }
        throw new Error(`GHL API Request Failed: ${error.message}`);
      }
    );
  }

  /**
   * Rate limiting: GHL allows 100 requests per 10 seconds
   * This method implements a simple rate limiter
   */
  private async checkRateLimit(): Promise<void> {
    const now = Date.now();
    const windowDuration = 10000; // 10 seconds

    // Reset counter if window has passed
    if (now - this.requestWindow > windowDuration) {
      this.requestCount = 0;
      this.requestWindow = now;
    }

    // If we've hit the limit, wait until window resets
    if (this.requestCount >= 100) {
      const waitTime = windowDuration - (now - this.requestWindow);
      console.warn(`Rate limit approaching, waiting ${Math.ceil(waitTime / 1000)}s...`);
      await new Promise((resolve) => setTimeout(resolve, waitTime));
      this.requestCount = 0;
      this.requestWindow = Date.now();
    }

    this.requestCount++;
  }

  /**
   * Get all contacts for a location
   * @param params Query parameters for filtering contacts
   * @returns Array of contacts
   */
  async getContacts(params: ContactsQueryParams): Promise<GHLContact[]> {
    await this.checkRateLimit();

    const queryParams: any = {
      locationId: params.locationId,
      limit: params.limit || 100,
    };

    if (params.startAfter) {
      queryParams.startAfter = params.startAfter;
    }

    if (params.query) {
      queryParams.query = params.query;
    }

    const response = await this.client.get<GHLContactsResponse>('/contacts/', {
      params: queryParams,
    });

    let contacts = response.data.contacts || [];

    // Handle pagination if there are more results
    if (response.data.nextPage && contacts.length < (params.limit || Infinity)) {
      const nextPageContacts = await this.getContacts({
        ...params,
        startAfter: response.data.nextPage,
      });
      contacts = [...contacts, ...nextPageContacts];
    }

    return contacts;
  }

  /**
   * Get a single contact by ID
   * @param contactId Contact ID
   * @returns Contact details
   */
  async getContact(contactId: string): Promise<GHLContact> {
    await this.checkRateLimit();

    const response = await this.client.get<{ contact: GHLContact }>(`/contacts/${contactId}`);
    return response.data.contact;
  }

  /**
   * Search contacts by query
   * @param locationId Location ID
   * @param query Search query
   * @returns Array of matching contacts
   */
  async searchContacts(locationId: string, query: string): Promise<GHLContact[]> {
    return this.getContacts({ locationId, query });
  }

  /**
   * Get opportunities for a location
   * @param params Query parameters for filtering opportunities
   * @returns Array of opportunities
   */
  async getOpportunities(params: OpportunitiesQueryParams): Promise<GHLOpportunity[]> {
    await this.checkRateLimit();

    const queryParams: any = {
      location_id: params.locationId,
      limit: params.limit || 100,
    };

    if (params.pipelineId) {
      queryParams.pipelineId = params.pipelineId;
    }

    if (params.startAfter) {
      queryParams.startAfter = params.startAfter;
    }

    if (params.status && params.status !== 'all') {
      queryParams.status = params.status;
    }

    const response = await this.client.get<GHLOpportunitiesResponse>('/opportunities/', {
      params: queryParams,
    });

    let opportunities = response.data.opportunities || [];

    // Handle pagination if there are more results
    if (response.data.nextPage && opportunities.length < (params.limit || Infinity)) {
      const nextPageOpps = await this.getOpportunities({
        ...params,
        startAfter: response.data.nextPage,
      });
      opportunities = [...opportunities, ...nextPageOpps];
    }

    return opportunities;
  }

  /**
   * Get a single opportunity by ID
   * @param opportunityId Opportunity ID
   * @returns Opportunity details
   */
  async getOpportunity(opportunityId: string): Promise<GHLOpportunity> {
    await this.checkRateLimit();

    const response = await this.client.get<{ opportunity: GHLOpportunity }>(
      `/opportunities/${opportunityId}`
    );
    return response.data.opportunity;
  }

  /**
   * Get all pipelines for a location
   * @param locationId Location ID
   * @returns Array of pipelines
   */
  async getPipelines(locationId: string): Promise<GHLPipeline[]> {
    await this.checkRateLimit();

    const response = await this.client.get<{ pipelines: GHLPipeline[] }>(
      `/opportunities/pipelines`,
      {
        params: { locationId },
      }
    );

    return response.data.pipelines || [];
  }

  /**
   * Test the API connection
   * @returns true if connection is successful
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.checkRateLimit();
      // Try to get locations/account info as a connectivity test
      await this.client.get('/locations/');
      return true;
    } catch (error) {
      return false;
    }
  }
}

/**
 * Create a GHL client instance from environment variables
 */
export function createGHLClient(): GHLClient {
  const apiKey = process.env.GHL_API_KEY;
  const baseUrl = process.env.GHL_API_BASE_URL || 'https://rest.gohighlevel.com';

  if (!apiKey) {
    throw new Error(
      'GHL_API_KEY not found in environment variables. Please set it in your .env file.'
    );
  }

  return new GHLClient({
    apiKey,
    baseUrl,
    locationId: process.env.GHL_LOCATION_ID,
  });
}
