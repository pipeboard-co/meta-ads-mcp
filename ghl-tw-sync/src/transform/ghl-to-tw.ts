/**
 * Transformation layer: GoHighLevel → TripleWhale Orders
 * Maps GHL contacts to TW order records
 */

import type { GHLContact } from '../types/ghl.js';
import type { TWOrder } from '../types/triplewhale.js';

export interface TransformOptions {
  shop: string; // e.g., "rtt.com"
  platform?: string; // e.g., "shopify_ghl"
  currency?: string; // Default currency (e.g., "GBP", "USD")
  defaultRevenue?: number; // Default revenue if not available in GHL
}

/**
 * Transform a GHL contact into a TripleWhale order
 * @param contact GHL contact
 * @param options Transform options (shop, platform, currency, etc.)
 * @returns TripleWhale order record
 */
export function contactToOrder(
  contact: GHLContact,
  options: TransformOptions
): TWOrder | null {
  // Skip contacts without email (required field)
  if (!contact.email) {
    console.warn(`Contact ${contact.id} skipped: missing email`);
    return null;
  }

  // Extract revenue from custom fields if available
  // You can customize this based on your GHL custom field structure
  let orderRevenue = options.defaultRevenue || 0;
  if (contact.customFields?.order_value || contact.customFields?.revenue) {
    orderRevenue = Number(contact.customFields.order_value || contact.customFields.revenue);
  }

  // Use contact creation date as order date
  const createdAt = contact.dateAdded
    ? new Date(contact.dateAdded).toISOString()
    : new Date().toISOString();

  return {
    customer: {
      id: contact.id,
      email: contact.email.toLowerCase().trim(),
      phone: contact.phone ? normalizePhone(contact.phone) : undefined,
      first_name: contact.firstName?.trim(),
      last_name: contact.lastName?.trim(),
    },
    shop: options.shop,
    order_id: `ghl_${contact.id}`, // Generate order ID from contact ID
    platform: options.platform || 'gohighlevel',
    created_at: createdAt,
    currency: options.currency || 'USD',
    order_revenue: orderRevenue,
  };
}

/**
 * Batch transform contacts to orders
 * @param contacts Array of GHL contacts
 * @param options Transform options
 * @returns Array of TripleWhale orders (null values filtered out)
 */
export function batchTransformContacts(
  contacts: GHLContact[],
  options: TransformOptions
): TWOrder[] {
  const orders = contacts
    .map((contact) => contactToOrder(contact, options))
    .filter((order): order is TWOrder => order !== null);

  console.log(`Transformed ${orders.length} contacts to orders (${contacts.length - orders.length} skipped)`);
  return orders;
}

/**
 * Normalize phone number to E.164 format (digits only with country code)
 * @param phone Phone number
 * @returns Normalized phone number
 */
function normalizePhone(phone: string): string {
  // Remove all non-digit characters
  const digits = phone.replace(/\D/g, '');

  // Add + prefix if not present and starts with country code
  if (digits.length >= 10 && !digits.startsWith('+')) {
    return `+${digits}`;
  }

  return digits;
}

/**
 * Filter orders by date range
 * @param orders Array of orders
 * @param startDate Start date (inclusive)
 * @param endDate End date (inclusive)
 * @returns Filtered orders
 */
export function filterOrdersByDate(
  orders: TWOrder[],
  startDate?: Date,
  endDate?: Date
): TWOrder[] {
  return orders.filter((order) => {
    const orderDate = new Date(order.created_at);

    if (startDate && orderDate < startDate) {
      return false;
    }
    if (endDate && orderDate > endDate) {
      return false;
    }
    return true;
  });
}

/**
 * Deduplicate orders by order_id
 * @param orders Array of orders
 * @returns Deduplicated orders
 */
export function deduplicateOrders(orders: TWOrder[]): TWOrder[] {
  const seen = new Set<string>();
  return orders.filter((order) => {
    if (seen.has(order.order_id)) {
      return false;
    }
    seen.add(order.order_id);
    return true;
  });
}

/**
 * Validate order data
 * @param order Order to validate
 * @returns true if valid, false otherwise
 */
export function validateOrder(order: TWOrder): boolean {
  if (!order.customer?.id || !order.customer?.email) {
    console.error(`Invalid order: missing customer id or email`);
    return false;
  }

  if (!order.order_id || !order.shop || !order.platform) {
    console.error(`Invalid order: missing required fields`);
    return false;
  }

  if (!order.created_at) {
    console.error(`Invalid order: missing created_at`);
    return false;
  }

  if (typeof order.order_revenue !== 'number' || order.order_revenue < 0) {
    console.error(`Invalid order: invalid order_revenue`);
    return false;
  }

  return true;
}
