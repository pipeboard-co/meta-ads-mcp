## Advanced GAQL Query Examples

### 1. Multi-level Performance Analysis with Geographic and Device Segmentation

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  segments.geo_target_region,
  segments.device,
  segments.day_of_week,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.cost_per_conversion,
  metrics.conversion_rate,
  metrics.return_on_ad_spend
FROM ad_group
WHERE
  campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND segments.date DURING LAST_90_DAYS
  AND metrics.impressions > 100
ORDER BY
  segments.geo_target_region,
  segments.device,
  metrics.return_on_ad_spend DESC
LIMIT 1000
```

This query provides a comprehensive performance breakdown by geography, device type, and day of week, helping identify specific combinations that drive the best return on ad spend.

### 2. Bidding Strategy Effectiveness Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.bidding_strategy_type,
  bidding_strategy.id,
  bidding_strategy.name,
  bidding_strategy.type,
  campaign.target_cpa.target_cpa_micros,
  campaign.target_roas.target_roas,
  segments.date,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.average_cpc,
  metrics.cost_per_conversion
FROM campaign
WHERE
  campaign.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
  AND metrics.impressions > 0
ORDER BY
  campaign.bidding_strategy_type,
  segments.date
```

This query helps analyze the effectiveness of different bidding strategies by comparing key performance metrics across campaigns using various automated bidding approaches.

### 3. Ad Performance by Landing Page with Quality Score Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  ad_group_ad.ad.id,
  ad_group_ad.ad.final_urls,
  ad_group_ad.ad.type,
  ad_group_ad.ad.expanded_text_ad.headline_part1,
  ad_group_ad.ad.expanded_text_ad.headline_part2,
  ad_group_criterion.keyword.text,
  ad_group_criterion.quality_info.quality_score,
  ad_group_criterion.quality_info.creative_quality_score,
  ad_group_criterion.quality_info.post_click_quality_score,
  ad_group_criterion.quality_info.search_predicted_ctr,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.average_cpc,
  metrics.ctr
FROM ad_group_ad
WHERE
  campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND ad_group_ad.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
  AND metrics.impressions > 100
ORDER BY
  metrics.conversion_value DESC,
  ad_group_criterion.quality_info.quality_score DESC
```

This query examines ad performance in relation to landing pages and quality scores, helping identify high-performing ad creatives and their associated landing pages.

### 4. Keyword Performance Analysis with Impression Share and Position Metrics

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  ad_group_criterion.criterion_id,
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.absolute_top_impression_percentage,
  metrics.top_impression_percentage,
  metrics.search_impression_share,
  metrics.search_rank_lost_impression_share,
  metrics.search_budget_lost_impression_share
FROM keyword_view
WHERE
  campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND ad_group_criterion.status = 'ENABLED'
  AND segments.date DURING LAST_90_DAYS
  AND metrics.impressions > 10
ORDER BY
  metrics.conversion_value DESC,
  metrics.search_impression_share ASC
```

This query helps identify keywords that are performing well but may be limited by impression share, indicating opportunities for bid or budget adjustments.

### 5. Complex Audience Segmentation Performance Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  segments.audience.id,
  segments.audience.name,
  segments.audience.type,
  segments.date,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.average_cpc,
  metrics.ctr,
  metrics.conversion_rate,
  metrics.value_per_conversion
FROM ad_group
WHERE
  campaign.advertising_channel_type = 'DISPLAY'
  AND campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND segments.date DURING LAST_90_DAYS
  AND segments.audience.id IS NOT NULL
ORDER BY
  segments.audience.type,
  metrics.conversion_value DESC
```

This query analyzes the performance of different audience segments across display campaigns, helping identify the most valuable audience types.

### 6. Shopping Campaign Product Performance Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  segments.product_item_id,
  segments.product_title,
  segments.product_type_l1,
  segments.product_type_l2,
  segments.product_type_l3,
  segments.product_type_l4,
  segments.product_type_l5,
  segments.product_brand,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.ctr,
  metrics.conversion_rate,
  metrics.return_on_ad_spend
FROM shopping_performance_view
WHERE
  campaign.advertising_channel_type = 'SHOPPING'
  AND campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
  AND metrics.impressions > 0
ORDER BY
  metrics.return_on_ad_spend DESC
```

This query provides a detailed breakdown of shopping campaign performance by product attributes, helping identify high-performing products and product categories.

### 7. Ad Schedule Performance with Bid Modifier Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  ad_schedule_view.day_of_week,
  ad_schedule_view.start_hour,
  ad_schedule_view.end_hour,
  campaign_criterion.bid_modifier,
  segments.date,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.ctr,
  metrics.conversion_rate,
  metrics.value_per_conversion
FROM ad_schedule_view
WHERE
  campaign.status = 'ENABLED' 
  AND segments.date DURING LAST_14_DAYS
ORDER BY
  ad_schedule_view.day_of_week,
  ad_schedule_view.start_hour
```

This query analyzes performance across different ad schedules and compares it with the applied bid modifiers, helping identify opportunities for schedule-based bid adjustments.

### 8. Cross-Campaign Asset Performance Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  asset.id,
  asset.type,
  asset.name,
  asset.text_asset.text,
  asset.image_asset.full_size.url,
  asset_performance_label,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.cost_micros,
  metrics.ctr
FROM asset_performance_label_view
WHERE
  campaign.status = 'ENABLED'
  AND ad_group.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
ORDER BY
  asset.type,
  metrics.conversions DESC
```

This query helps analyze performance of assets (images, text, etc.) across campaigns, helping identify high-performing creative elements.

### 9. Geographic Performance with Location Bid Modifier Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  geographic_view.country_criterion_id,
  geographic_view.location_type,
  geographic_view.geo_target_constant,
  campaign_criterion.bid_modifier,
  segments.date,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  metrics.cost_micros,
  metrics.ctr,
  metrics.conversion_rate
FROM geographic_view
WHERE
  campaign.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
ORDER BY
  geographic_view.country_criterion_id,
  metrics.conversion_value DESC
```

This query analyzes performance across different geographic locations and compares it with location bid modifiers, helping identify opportunities for geographic bid adjustments.

### 10. Advanced Budget Utilization and Performance Analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign_budget.amount_micros,
  campaign_budget.total_amount_micros,
  campaign_budget.delivery_method,
  campaign_budget.reference_count,
  campaign_budget.has_recommended_budget,
  campaign_budget.recommended_budget_amount_micros,
  segments.date,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value,
  (metrics.cost_micros * 1.0) / (campaign_budget.amount_micros * 1.0) AS budget_utilization_rate
FROM campaign
WHERE
  campaign.status IN ('ENABLED', 'PAUSED')
  AND segments.date DURING LAST_30_DAYS
ORDER BY
  segments.date DESC,
  budget_utilization_rate DESC
```

This query helps analyze budget utilization across campaigns, with a calculated field for budget utilization rate, helping identify campaigns that consistently use their full budget or need budget adjustments.

## Practical Applications of These Queries

These advanced GAQL queries can help you:

1. **Identify performance trends** across different dimensions (geographic, temporal, device-based)
2. **Optimize bidding strategies** by comparing performance across different automated bidding approaches
3. **Improve quality scores** by analyzing the relationship between landing pages, ad creatives, and performance metrics
4. **Maximize impression share** for high-performing keywords and ad groups
5. **Refine audience targeting** by identifying the most valuable audience segments
6. **Optimize product feeds** for shopping campaigns by analyzing performance at the product level
7. **Fine-tune ad scheduling** based on day and hour performance analysis
8. **Improve creative assets** by identifying high-performing images, text, and other creative elements
9. **Adjust geographic targeting** based on performance differences across locations
10. **Optimize budget allocation** to maximize return on ad spend

