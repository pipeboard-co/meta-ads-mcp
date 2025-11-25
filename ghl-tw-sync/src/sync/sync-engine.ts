/**
 * Sync Engine - Orchestrates GHL → TripleWhale data synchronization
 */

import { GHLClient } from '../ghl-api/ghl-client.js';
import { TWClient } from '../tw-api/tw-client.js';
import type { GHLContact } from '../types/ghl.js';
import type { TWOrder } from '../types/triplewhale.js';
import {
  batchTransformContacts,
  deduplicateOrders,
  filterOrdersByDate,
  validateOrder,
  type TransformOptions,
} from '../transform/ghl-to-tw.js';

export interface SyncOptions {
  locationId: string;
  tags?: string[]; // Filter contacts by tags
  shop: string; // Shop identifier (e.g., "rtt.com")
  platform?: string; // Platform identifier (default: "gohighlevel")
  currency?: string; // Default currency (default: "USD")
  defaultRevenue?: number; // Default revenue if not in GHL (default: 0)
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  dryRun?: boolean;
  batchSize?: number;
  delayMs?: number;
}

export interface CSVSyncOptions {
  contacts: GHLContact[]; // Contacts from CSV
  shop: string; // Shop identifier (e.g., "rtt.com")
  platform?: string; // Platform identifier (default: "gohighlevel")
  currency?: string; // Default currency (default: "USD")
  defaultRevenue?: number; // Default revenue if not in GHL (default: 0)
  startDate?: Date;
  endDate?: Date;
  dryRun?: boolean;
  batchSize?: number;
  batchDelay?: number;
}

export interface SyncResult {
  success: boolean;
  contactsFetched: number;
  ordersCreated: number;
  ordersPushed: number;
  errors: string[];
  duration: number;
}

export class SyncEngine {
  private ghlClient: GHLClient;
  private twClient: TWClient;

  constructor(ghlClient: GHLClient, twClient: TWClient) {
    this.ghlClient = ghlClient;
    this.twClient = twClient;
  }

  /**
   * Sync contacts from GHL to TripleWhale orders
   * @param options Sync options
   * @returns Sync result
   */
  async syncContacts(options: SyncOptions): Promise<SyncResult> {
    const startTime = Date.now();
    const result: SyncResult = {
      success: false,
      contactsFetched: 0,
      ordersCreated: 0,
      ordersPushed: 0,
      errors: [],
      duration: 0,
    };

    try {
      // Step 1: Fetch contacts from GHL (with tag filtering)
      console.log('Fetching contacts from GHL...');
      if (options.tags && options.tags.length > 0) {
        console.log(`Filtering by tags: ${options.tags.join(', ')}`);
      }

      const contacts = await this.ghlClient.getContacts({
        locationId: options.locationId,
        limit: options.limit,
        tags: options.tags,
      });
      result.contactsFetched = contacts.length;

      if (contacts.length === 0) {
        console.log('No contacts found matching criteria');
        result.success = true;
        result.duration = Date.now() - startTime;
        return result;
      }

      console.log(`Found ${contacts.length} contacts`);

      // Step 2: Transform contacts to TW orders
      console.log('Transforming contacts to TripleWhale orders...');
      const transformOptions: TransformOptions = {
        shop: options.shop,
        platform: options.platform || 'gohighlevel',
        currency: options.currency || 'USD',
        defaultRevenue: options.defaultRevenue || 0,
      };

      let orders = batchTransformContacts(contacts, transformOptions);
      result.ordersCreated = orders.length;

      // Step 3: Filter by date range if specified
      if (options.startDate || options.endDate) {
        orders = filterOrdersByDate(orders, options.startDate, options.endDate);
        console.log(`Filtered to ${orders.length} orders within date range`);
      }

      // Step 4: Deduplicate orders
      const originalCount = orders.length;
      orders = deduplicateOrders(orders);
      if (orders.length < originalCount) {
        console.log(`Removed ${originalCount - orders.length} duplicate orders`);
      }

      // Step 5: Validate orders
      const validOrders = orders.filter((order) => {
        const isValid = validateOrder(order);
        if (!isValid) {
          result.errors.push(`Invalid order: ${order.order_id}`);
        }
        return isValid;
      });

      if (validOrders.length < orders.length) {
        console.log(`Removed ${orders.length - validOrders.length} invalid orders`);
      }

      // Step 6: Push orders to TripleWhale
      if (options.dryRun) {
        console.log('DRY RUN - Would push orders:', validOrders.length);
        result.ordersPushed = 0;
      } else {
        result.ordersPushed = await this.pushOrdersInBatches(
          validOrders,
          options.batchSize || 100,
          options.delayMs || 1000
        );
      }

      result.success = true;
    } catch (error) {
      result.success = false;
      result.errors.push(`Sync failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      result.duration = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Push orders to TripleWhale in batches
   * @param orders Array of orders to push
   * @param batchSize Number of orders per batch
   * @param delayMs Delay between batches in milliseconds
   * @returns Total number of orders successfully pushed
   */
  private async pushOrdersInBatches(
    orders: TWOrder[],
    batchSize: number,
    delayMs: number
  ): Promise<number> {
    let totalPushed = 0;
    const totalBatches = Math.ceil(orders.length / batchSize);

    for (let i = 0; i < totalBatches; i++) {
      const start = i * batchSize;
      const end = Math.min((i + 1) * batchSize, orders.length);
      const batch = orders.slice(start, end);

      console.log(`Pushing batch ${i + 1}/${totalBatches} (${batch.length} orders)...`);

      try {
        const result = await this.twClient.pushOrders(batch);
        totalPushed += result.orders_received || batch.length;
        console.log(`✓ Batch ${i + 1}/${totalBatches} complete (${result.orders_received || batch.length} orders received)`);
      } catch (error) {
        console.error(`✗ Batch ${i + 1}/${totalBatches} failed:`, error instanceof Error ? error.message : 'Unknown error');
      }

      // Delay between batches (except for the last one)
      if (i < totalBatches - 1 && delayMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }

    return totalPushed;
  }

  /**
   * Sync contacts from CSV to TripleWhale orders
   * @param options CSV sync options
   * @returns Sync result
   */
  async syncFromCSV(options: CSVSyncOptions): Promise<SyncResult> {
    const startTime = Date.now();
    const result: SyncResult = {
      success: false,
      contactsFetched: options.contacts.length,
      ordersCreated: 0,
      ordersPushed: 0,
      errors: [],
      duration: 0,
    };

    try {
      const contacts = options.contacts;

      if (contacts.length === 0) {
        console.log('No contacts provided');
        result.success = true;
        result.duration = Date.now() - startTime;
        return result;
      }

      console.log(`Processing ${contacts.length} contacts from CSV`);

      // Step 1: Transform contacts to TW orders
      console.log('Transforming contacts to TripleWhale orders...');
      const transformOptions: TransformOptions = {
        shop: options.shop,
        platform: options.platform || 'gohighlevel',
        currency: options.currency || 'USD',
        defaultRevenue: options.defaultRevenue || 0,
      };

      let orders = batchTransformContacts(contacts, transformOptions);
      result.ordersCreated = orders.length;
      console.log(`Transformed ${contacts.length} contacts to ${orders.length} orders (${contacts.length - orders.length} skipped)`);

      // Step 2: Filter by date range if specified
      if (options.startDate || options.endDate) {
        orders = filterOrdersByDate(orders, options.startDate, options.endDate);
        console.log(`Filtered to ${orders.length} orders within date range`);
      }

      // Step 3: Deduplicate orders
      const originalCount = orders.length;
      orders = deduplicateOrders(orders);
      if (orders.length < originalCount) {
        console.log(`Removed ${originalCount - orders.length} duplicate orders`);
      }

      // Step 4: Validate orders
      const validOrders = orders.filter((order) => {
        const isValid = validateOrder(order);
        if (!isValid) {
          result.errors.push(`Invalid order: ${order.order_id}`);
        }
        return isValid;
      });

      if (validOrders.length < orders.length) {
        console.log(`Removed ${orders.length - validOrders.length} invalid orders`);
      }

      // Step 5: Push orders to TripleWhale
      if (options.dryRun) {
        console.log('DRY RUN - Would push orders:', validOrders.length);
        result.ordersPushed = 0;
      } else {
        result.ordersPushed = await this.pushOrdersInBatches(
          validOrders,
          options.batchSize || 100,
          options.batchDelay || 1000
        );
      }

      result.success = true;
    } catch (error) {
      result.success = false;
      result.errors.push(`CSV sync failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      result.duration = Date.now() - startTime;
    }

    return result;
  }

  /**
   * Test sync with a small sample
   * @param locationId GHL location ID
   * @param shop Shop identifier
   * @param tags Optional tags to filter by
   * @param limit Number of contacts to test (default: 10)
   * @returns Sync result
   */
  async testSync(
    locationId: string,
    shop: string,
    tags?: string[],
    limit: number = 10
  ): Promise<SyncResult> {
    console.log(`Running test sync with ${limit} contacts...`);
    return this.syncContacts({
      locationId,
      shop,
      tags,
      limit,
      dryRun: true,
    });
  }
}
