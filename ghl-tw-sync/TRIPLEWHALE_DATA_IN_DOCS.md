# TripleWhale Data-In API Documentation

## Overview

The TripleWhale Data-In API allows you to integrate custom sales platforms and third-party tools that don't have native TripleWhale support. This document covers the use cases and setup requirements for Custom Sales Platforms.

---

## Data-In API Use Cases

### 1. Custom Sales Platform
**Purpose**: Upload backend orders, products, and subscriptions from unsupported sales platforms

**Available Endpoints**:
- **Orders**: Upload customer details, items, and transaction totals
- **Products**: Send product details, variants, titles, and tags
- **Subscriptions**: Submit billing schedules and customer subscription information

**Use Case**: If your business uses a custom-built or non-native sales platform (not Shopify, WooCommerce, BigCommerce, etc.), you can push order data directly to TripleWhale for analytics.

---

### 2. Custom 3rd-Party Integrations
**Purpose**: Integrate ad spend and survey response data from non-native platforms

**Available Endpoints**:
- **Ads**: Upload ad data (spend, clicks, impressions) from ad platforms without native support
- **Post-Purchase Surveys**: Submit survey responses linked to orders

**Use Case**: Track marketing spend and customer feedback from platforms that TripleWhale doesn't natively support.

---

### 3. Data Enrichment for Native Sales Platforms
**Purpose**: Enhance Shopify, WooCommerce, or BigCommerce records with missing fields

**Available Endpoints**:
- **Enrich Orders**: Add fields like shipping costs or custom tags to existing orders
- **Enrich Products**: Add cost data to Shopify product variants

**Use Case**: If you have a Shopify store but want to add additional fields (like custom shipping costs or tags) that aren't available in the native integration.

---

### 4. Data Enrichment for Pixel Attribution
**Purpose**: Track offline events like leads and demo bookings

**Available Endpoint**:
- **Enrich Pixel with Offline Events**: Submit lead, MQL, SQL, opportunity, and custom event data

**Use Case**: Track conversions that happen outside your website (e.g., phone calls, in-person demos, CRM events).

---

## Processing Timeline

- **Recent data** (past 2 days): ~5 minutes
- **Older data**: up to 20 minutes

---

## Key Recommendation

**Always check native support first!** Before implementing custom integrations, review the [TripleWhale Integrations page](https://www.triplewhale.com/integrations) to see if your platform is already supported natively.

---

# Custom Sales Platform Setup Overview

## What is a Custom Sales Platform Integration?

TripleWhale enables businesses that don't use native platforms (Shopify, WooCommerce, BigCommerce) to integrate their custom sales platform through two required components:

1. **Backend API Connection** - for orders, products, subscriptions
2. **Headless Pixel Installation** - for attribution and customer journey tracking

---

## Two Required Components

### 1. Backend API Connection

**Purpose**: Transmits orders, products, and subscriptions data from your system

**Key Points**:
- Provides source-of-truth financial information
- Sent from server-side infrastructure
- Required for all custom sales platforms

**Data Transmitted**:
- Orders (customer details, items, totals)
- Products (variants, titles, tags)
- Subscriptions (billing schedules, customer info)

---

### 2. Headless Pixel Installation

**Purpose**: Tracks attribution and customer journey data

**Key Points**:
- Captures session information and visitor behavior
- Installed on website/client-side
- Enables attribution tracking

**Data Tracked**:
- Page views
- Add to cart events
- Checkout initiated
- Purchase events
- Custom events

---

## Data Ingestion Sources

TripleWhale accepts data from three channels:

| Source | Data Types |
|--------|-----------|
| **Pixel** | Attribution, funnel tracking, session data |
| **Sales Platform** | Revenue, subscriptions, LTV, refunds |
| **3rd-Party Integrations** | Marketing channels, ad spend, email/SMS |

---

## Critical Prerequisites

⚠️ **IMPORTANT**: Attribution and customer journey stitching (Pixel) **require an order record to be sent via the API**.

- Pixel events **cannot function** without corresponding order records
- Order records can come from either:
  - Native platforms (Shopify, WooCommerce, BigCommerce)
  - Custom platforms (via Data-In API)

---

## Recommended Implementation Sequence

1. **Send Pixel events BEFORE submitting orders via API**
   - Maximizes attribution accuracy
   - Improves customer journey tracking

2. **Alternative**: Send orders first, then Pixel events
   - Still functions but with reduced matching reliability

---

## Optional Integrations

The following are **completely optional** (not required for core setup):
- Meta Ads
- Klaviyo
- Other marketing platforms

**Note**: These enhance marketing insights but aren't needed for basic Custom Sales Platform functionality.

---

## Setup Resources

### Documentation Links
- **API Setup Guide**: Detailed API integration instructions
- **Pixel Setup Guide**: Client-side tracking implementation
- **Demo Repository**: Working code samples
- **Knowledge Base**:
  - Landing pages integration
  - Headless stores setup
  - Custom events tracking

---

## Next Steps for GHL-TW Sync

Based on this documentation, here's what we need to do:

### 1. **Register Custom Sales Platform in TripleWhale**
- Go to Integrations → Data In
- Create/reconnect a Custom Sales Platform account
- Note the shop identifier (e.g., `custom-msp` or `42455633232`)

### 2. **Send Order Data via API**
- Endpoint: `/api/v2/data-in/orders`
- Method: POST
- Authentication: `x-api-key` header
- Required: Orders: Write scope on API key

### 3. **Verify Shop Identifier**
- Use the exact shop ID from TripleWhale dashboard
- Include in every order payload as `shop` field

### 4. **Test with Small Batch**
- Start with 10 contacts
- Verify orders appear in TripleWhale dashboard
- Scale up to full 18,568 contacts

---

## Troubleshooting Notes

### 403 Forbidden Error
Possible causes:
1. API key missing "Orders: Write" scope
2. Shop identifier not registered in Data-In section
3. Shop ID mismatch between API payload and TW account
4. Custom Sales Platform account disconnected/not set up

### Solution
1. Verify API key has "Orders: Write" scope
2. Confirm Custom Sales Platform is active in Data-In section
3. Use exact shop identifier from TripleWhale dashboard
4. Reconnect any disconnected accounts
