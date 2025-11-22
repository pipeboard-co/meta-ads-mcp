---
description: Use this to write better GAQL queries
globs: 
alwaysApply: false
---
# Google Ads Query Language (GAQL) Guidelines

## Overview

The Google Ads Query Language (GAQL) is a powerful tool for querying the Google Ads API that allows you to retrieve:

1. **Resources** and their related attributes, segments, and metrics using `GoogleAdsService.Search` or `GoogleAdsService.SearchStream`
2. **Metadata** about available fields and resources using `GoogleAdsFieldService`

## Field Categories

Understanding field categories is essential for building effective GAQL queries:

1. **RESOURCE**: Represents a primary entity (e.g., `campaign`, `ad_group`) that can be used in the FROM clause
2. **ATTRIBUTE**: Properties of a resource (e.g., `campaign.id`, `campaign.name`). Including these may segment results depending on the resource relationship
3. **SEGMENT**: Fields that always segment search queries (e.g., `segments.date`, `segments.device`)
4. **METRIC**: Performance data fields (e.g., `metrics.impressions`, `metrics.clicks`) that never segment search queries

## Query Structure

A GAQL query consists of the following components:

```
SELECT
  <field_1>,
  <field_2>,
  ...
FROM <resource>
WHERE <condition_1> AND <condition_2> AND ...
ORDER BY <field_1> [ASC|DESC], <field_2> [ASC|DESC], ...
LIMIT <number_of_results>
```

### SELECT Clause

The `SELECT` clause specifies the fields to return in the query results:

```
SELECT
  campaign.id,
  campaign.name,
  metrics.impressions,
  segments.device
```

Only fields that are marked as `selectable: true` in the `GoogleAdsField` metadata can be used in the SELECT clause.

### FROM Clause

The `FROM` clause specifies the primary resource type to query from. Only one resource can be specified, and it must have the category `RESOURCE`.

```
FROM campaign
```

### WHERE Clause (optional)

The `WHERE` clause specifies conditions to filter the results. Only fields marked as `filterable: true` in the `GoogleAdsField` metadata can be used for filtering.

```
WHERE 
  campaign.status = 'ENABLED'
  AND metrics.impressions > 1000
  AND segments.date DURING LAST_30_DAYS
```

### ORDER BY Clause (optional)

The `ORDER BY` clause specifies how to sort the results. Only fields marked as `sortable: true` in the `GoogleAdsField` metadata can be used for sorting.

```
ORDER BY metrics.impressions DESC, campaign.id
```

### LIMIT Clause (optional)

The `LIMIT` clause restricts the number of results returned.

```
LIMIT 100
```

## Field Metadata Exploration

To explore available fields and their properties, use the `GoogleAdsFieldService`:

```
SELECT
  name,
  category,
  selectable,
  filterable,
  sortable,
  selectable_with,
  attribute_resources,
  metrics,
  segments,
  data_type,
  enum_values,
  is_repeated
WHERE name = "campaign.id"
```

Key metadata properties to understand:

- **`selectable`**: Whether the field can be used in a SELECT clause
- **`filterable`**: Whether the field can be used in a WHERE clause
- **`sortable`**: Whether the field can be used in an ORDER BY clause
- **`selectable_with`**: Lists resources, segments, and metrics that are selectable with this field
- **`attribute_resources`**: For RESOURCE fields, lists the resources that are selectable with this resource and don't segment metrics
- **`metrics`**: For RESOURCE fields, lists metrics that are selectable when this resource is in the FROM clause
- **`segments`**: For RESOURCE fields, lists fields that segment metrics when this resource is used in the FROM clause
- **`data_type`**: Determines which operators can be used with the field in WHERE clauses
- **`enum_values`**: Lists possible values for ENUM type fields
- **`is_repeated`**: Whether the field can contain multiple values

## Data Types and Operators

Different field data types support different operators in WHERE clauses:

### String Fields
- `=`, `!=`, `IN`, `NOT IN`
- `LIKE`, `NOT LIKE` (case-sensitive string matching)
- `CONTAINS ANY`, `CONTAINS ALL`, `CONTAINS NONE` (for repeated fields)

### Numeric Fields
- `=`, `!=`, `<`, `<=`, `>`, `>=`
- `IN`, `NOT IN`

### Date Fields
- `=`, `!=`, `<`, `<=`, `>`, `>=`
- `DURING` (with named date ranges)
- `BETWEEN` (with date literals)

### Enum Fields
- `=`, `!=`, `IN`, `NOT IN`
- Values must match exactly as listed in `enum_values`

### Boolean Fields
- `=`, `!=`
- Values must be `TRUE` or `FALSE`

## Date Ranges

### Literal Date Ranges
```
WHERE segments.date BETWEEN '2020-01-01' AND '2020-01-31'
```

### Named Date Ranges
```
WHERE segments.date DURING LAST_7_DAYS
WHERE segments.date DURING LAST_14_DAYS
WHERE segments.date DURING LAST_30_DAYS
WHERE segments.date DURING LAST_90_DAYS
WHERE segments.date DURING THIS_MONTH
WHERE segments.date DURING LAST_MONTH
WHERE segments.date DURING THIS_QUARTER
```

### Date Functions
```
WHERE segments.date = YESTERDAY
WHERE segments.date = TODAY
```

## Case Sensitivity Rules

1. **Field and resource names**: Case-sensitive (`campaign.id` not `Campaign.Id`)
2. **Enumeration values**: Case-sensitive (`'ENABLED'` not `'enabled'`)
3. **String literals in conditions**:
   - Case-insensitive by default (`WHERE campaign.name = 'brand campaign'`)
   - Use `LIKE` for case-sensitive matching (`WHERE campaign.name LIKE 'Brand Campaign'`)

## Ordering and Limiting Results

### Ordering
- Results can be ordered by one or more fields
- Use `ASC` (default) or `DESC` to specify direction
- Only fields marked as `sortable: true` can be used

```
ORDER BY metrics.impressions DESC, campaign.id ASC
```

### Limiting
- Use LIMIT to restrict the number of rows returned
- Always use ORDER BY with LIMIT for consistent pagination
- The maximum value is system-dependent

```
LIMIT 100
```

## Query Examples

### Basic Campaign Query
```
SELECT
  campaign.id,
  campaign.name,
  campaign.status
FROM campaign
ORDER BY campaign.id
```

### Query with Metrics and Filtering
```
SELECT
  campaign.id,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM campaign
WHERE 
  campaign.status = 'ENABLED'
  AND metrics.impressions > 1000
ORDER BY metrics.impressions DESC
LIMIT 10
```

### Query with Segments
```
SELECT
  campaign.id,
  campaign.name,
  segments.date,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions
FROM campaign
WHERE 
  segments.date DURING LAST_30_DAYS
  AND campaign.status = 'ENABLED'
ORDER BY segments.date DESC, metrics.impressions DESC
```

### Query with Attributed Resources
```
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  bidding_strategy.id,
  bidding_strategy.name,
  bidding_strategy.type
FROM campaign
WHERE campaign.status = 'ENABLED'
```

### Field Metadata Query
```
SELECT
  name,
  category,
  selectable,
  filterable,
  sortable,
  data_type,
  enum_values
WHERE name LIKE 'campaign.%'
```

I'll help add information about assets to the GAQL guidelines document. Here's how I would incorporate the new information:

```markdown:gaql-google-ads-query-language.mdc
// ... existing code ...

## Asset Queries

### Asset Entity Queries

You can get a list of assets and their attributes by querying the `asset` entity:

```
SELECT
  asset.id,
  asset.name,
  asset.resource_name,
  asset.type
FROM asset
```

### Type-Specific Asset Attributes

Assets have type-specific attributes that can be queried based on their type:

```
SELECT
  asset.id,
  asset.name,
  asset.resource_name,
  asset.youtube_video_asset.youtube_video_id
FROM asset
WHERE asset.type = 'YOUTUBE_VIDEO'
```

### Asset Metrics at Different Levels

Asset metrics are available through three main resources:

1. **ad_group_asset**: Asset metrics at the ad group level
2. **campaign_asset**: Asset metrics at the campaign level
3. **customer_asset**: Asset metrics at the customer level

Example of querying ad-group level asset metrics:

```
SELECT
  ad_group.id,
  asset.id,
  metrics.clicks,
  metrics.impressions
FROM ad_group_asset
WHERE segments.date DURING LAST_MONTH
ORDER BY metrics.impressions DESC
```

### Ad-Level Asset Performance

Ad-level performance metrics for assets are aggregated in the `ad_group_ad_asset_view`. 

**Note**: The `ad_group_ad_asset_view` only returns information for assets related to App ads.

This view includes the `performance_label` attribute with the following possible values:
- `BEST`: Best performing assets
- `GOOD`: Good performing assets
- `LOW`: Worst performing assets
- `LEARNING`: Asset has impressions but stats aren't statistically significant yet
- `PENDING`: Asset doesn't have performance information yet (may be under review)
- `UNKNOWN`: Value unknown in this version
- `UNSPECIFIED`: Not specified

Example query for ad-level asset performance:

```
SELECT
  ad_group_ad_asset_view.ad_group_ad,
  ad_group_ad_asset_view.asset,
  ad_group_ad_asset_view.field_type,
  ad_group_ad_asset_view.performance_label,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM ad_group_ad_asset_view
WHERE segments.date DURING LAST_MONTH
ORDER BY ad_group_ad_asset_view.performance_label
```

### Asset Source Information

- `Asset.source` is only accurate for mutable Assets
- For the source of RSA (Responsive Search Ad) Assets, use `AdGroupAdAsset.source`

// ... existing code ...
```

This addition provides comprehensive information about querying assets in GAQL, including different asset types, how to access metrics at various levels, performance labeling, and important notes about asset source information.


## Best Practices

1. **Field Selection**: Only select the fields you need to reduce response size and improve performance.

2. **Filtering**: Apply filters in the `WHERE` clause to limit results to relevant data.

3. **Verify Field Properties**: Before using a field in a query, check its metadata to ensure it's selectable, filterable, or sortable as needed.

4. **Result Ordering**: Always use `ORDER BY` to ensure consistent results, especially when using pagination.

5. **Result Limiting**: Use `LIMIT` to restrict number of returned rows and improve performance.

6. **Handle Repeated Fields**: For fields where `is_repeated = true`, use appropriate operators like `CONTAINS ANY`, `CONTAINS ALL`, or `CONTAINS NONE`.

7. **Understand Segmentation**: Be aware that including segment fields or certain attribute fields will cause metrics to be segmented in the results.

8. **Date Handling**: Use appropriate date functions and ranges for filtering by date segments.

9. **Pagination**: For large result sets, use the page token provided in the response to retrieve subsequent pages.

10. **Check Enum Values**: For enum fields, verify the allowed values in the `enum_values` property before using them in queries.

By following these guidelines and understanding the metadata of GAQL fields, you'll be able to create effective and efficient GAQL queries for retrieving and analyzing your Google Ads data.
