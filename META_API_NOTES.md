# Meta Ads API Notes and Limitations

## Frequency Cap Visibility
The Meta Marketing API has some limitations regarding frequency cap visibility:

1. **Optimization Goal Dependency**: Frequency cap settings (`frequency_control_specs`) are only visible in API responses for ad sets where the optimization goal is set to REACH. For other optimization goals (like LINK_CLICKS, CONVERSIONS, etc.), the frequency caps will still work but won't be visible through the API.

2. **Verifying Frequency Caps**: Since frequency caps may not be directly visible, you can verify they're working by monitoring:
   - The frequency metric in ad insights
   - The ratio between reach and impressions over time
   - The actual frequency cap behavior in the Meta Ads Manager UI

## Other API Behaviors to Note

1. **Field Visibility**: Some fields may not appear in API responses even when explicitly requested. This doesn't necessarily mean the field isn't set - it may just not be visible through the API.

2. **Response Filtering**: The API may filter out empty or default values from responses to reduce payload size. If a field is missing from a response, it might mean:
   - The field is not set
   - The field has a default value
   - The field is not applicable for the current configuration

3. **Best Practices**:
   - Always verify important changes through both the API and Meta Ads Manager UI
   - Use insights and metrics to confirm behavioral changes when direct field access is limited
   - Consider the optimization goal when setting up features like frequency caps

## Deprecated and Removed Fields (v22.0 / v25.0)

### Removed in v22.0
- **`impressions` metric** — removed from the Media Insights API (`/{media_id}/insights`) across all media types: FEED images, FEED videos, REELS, STORIES, and CAROUSEL albums. Confirmed via live API testing on v25.0. Passing `impressions` returns a 400 error: *"Starting from version v22.0 and above, the impressions metric is no longer supported for the queried media."*
- **`plays`** and **`ig_reels_aggregated_all_plays_count`** — removed for Reels. Use `views` instead for Reel view counts.

### Removed in v25.0
- **`approximate_count`** field on custom audiences — replaced by `approximate_count_lower_bound` and `approximate_count_upper_bound`.
- **`IG_BUSINESS` subtype** for custom audiences — use `ENGAGEMENT` subtype with an IG engagement rule instead.

### Safe Media Insights Metrics (v25.0)
| Media Type | Supported Metrics |
|---|---|
| IMAGE / VIDEO / CAROUSEL (FEED) | `reach`, `saved`, `shares`, `views`, `total_interactions` |
| REELS | `reach`, `saved`, `shares`, `views`, `total_interactions` |
| STORIES | `reach`, `replies`, `taps_forward`, `taps_back`, `exits` |

## Updates and Changes
Meta frequently updates their API behavior. These notes will be updated as we discover new limitations or changes in the API's behavior.