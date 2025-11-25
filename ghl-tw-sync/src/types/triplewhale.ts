/**
 * TripleWhale API Types
 */

export interface TWConfig {
  apiKey: string;
  shopId?: string;
  baseUrl: string;
}

export interface TWOfflineEvent {
  event_name: string;
  event_time: number; // Unix timestamp
  action_source: string; // 'physical_store' | 'phone_call' | 'email' | 'system_generated' | 'other'
  user_data: TWUserData;
  custom_data?: TWCustomData;
  event_source_url?: string;
  opt_out?: boolean;
}

export interface TWUserData {
  email?: string[];
  phone?: string[];
  first_name?: string[];
  last_name?: string[];
  city?: string[];
  state?: string[];
  zip_code?: string[];
  country?: string[];
  external_id?: string[]; // Customer ID from your system
  client_ip_address?: string;
  client_user_agent?: string;
  fbc?: string; // Facebook Click ID
  fbp?: string; // Facebook Browser ID
}

export interface TWCustomData {
  currency?: string;
  value?: number;
  content_name?: string;
  content_category?: string;
  content_ids?: string[];
  contents?: TWContent[];
  num_items?: number;
  status?: string;
  order_id?: string;
}

export interface TWContent {
  id: string;
  quantity?: number;
  item_price?: number;
}

export interface TWBatchEventsRequest {
  data: TWOfflineEvent[];
}

export interface TWEventsResponse {
  events_received: number;
  messages?: string[];
  fbtrace_id?: string;
}

export interface TWMetricsResponse {
  shop_id: string;
  metrics: TWMetric[];
  date_range: {
    start_date: string;
    end_date: string;
  };
}

export interface TWMetric {
  date: string;
  metric_name: string;
  value: number;
}

export interface TWAPIError {
  error: {
    message: string;
    type: string;
    code: number;
    fbtrace_id?: string;
  };
}

export interface PushEventOptions {
  eventName: string;
  actionSource: string;
  userData: {
    email?: string;
    phone?: string;
    firstName?: string;
    lastName?: string;
    city?: string;
    state?: string;
    zipCode?: string;
    country?: string;
    externalId?: string;
  };
  customData?: {
    currency?: string;
    value?: number;
    contentName?: string;
    orderId?: string;
  };
  eventTime?: Date;
}

export interface PushEventsFromFileOptions {
  file: string;
  validate?: boolean;
}

// TripleWhale Orders API Types
export interface TWOrder {
  customer: {
    id: string;
    email: string;
    phone?: string;
    first_name?: string;
    last_name?: string;
  };
  shop: string;
  order_id: string;
  platform: string;
  created_at: string; // ISO 8601 format
  currency: string;
  order_revenue: number;
}

export interface TWOrdersResponse {
  success: boolean;
  orders_received?: number;
  message?: string;
}
