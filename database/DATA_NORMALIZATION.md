# Data Normalization Strategy

## Principii de bază

```
┌─────────────────────────────────────────────────────────────┐
│                    API RAW DATA                             │
│  (instabil, verbose, platform-specific)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              daily_metrics.raw_payload_json                 │
│  (backup complet, neprocesat)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ NORMALIZARE
┌─────────────────────────────────────────────────────────────┐
│               daily_metrics.metrics_json                    │
│  (normalizat, stabil, cross-platform)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ AGREGARE SĂPTĂMÂNALĂ
┌─────────────────────────────────────────────────────────────┐
│                  weekly_snapshots                           │
│  (sumarizat pentru audit + AI)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ VECTORIZARE
┌─────────────────────────────────────────────────────────────┐
│                   rag_documents                             │
│  (text natural pentru AI retrieval)                         │
└─────────────────────────────────────────────────────────────┘
```

---

# PARTEA 1: Categorii Metrici Brute per Platformă

---

## META ADS - Categorii Raw

### 1.1 DELIVERY (Livrare de bază)
| Metric Raw | Tip | Note |
|------------|-----|------|
| `impressions` | int | - |
| `reach` | int | Unici |
| `frequency` | float | impressions/reach |
| `spend` | currency | În moneda contului |
| `date_start`, `date_stop` | date | Perioada |

### 1.2 CLICKS & TRAFFIC
| Metric Raw | Tip | Note |
|------------|-----|------|
| `clicks` | int | Toate click-urile |
| `link_clicks` | int | actions[action_type=link_click] |
| `outbound_clicks` | int | Click-uri externe |
| `unique_clicks` | int | Unici |
| `unique_link_clicks` | int | Unici |
| `ctr` | float | API-calculated |
| `unique_ctr` | float | API-calculated |
| `cpc` | currency | API-calculated |
| `cost_per_unique_click` | currency | API-calculated |

### 1.3 CONVERSIONS (din actions[])
| Metric Raw | Tip | Note |
|------------|-----|------|
| `actions[purchase]` | int | Achiziții |
| `actions[add_to_cart]` | int | Coș |
| `actions[initiate_checkout]` | int | Checkout |
| `actions[lead]` | int | Lead-uri |
| `actions[complete_registration]` | int | Înregistrări |
| `actions[subscribe]` | int | Abonări |
| `actions[contact]` | int | Contact |
| `actions[view_content]` | int | Vizualizări |
| `action_values[purchase]` | currency | Valoare achiziții |
| `action_values[*]` | currency | Valori per acțiune |
| `conversions` | int | Agregat |
| `conversion_values` | currency | Agregat |

### 1.4 VIDEO METRICS
| Metric Raw | Tip | Note |
|------------|-----|------|
| `video_play_actions` | int | Play-uri |
| `video_p25_watched_actions` | int | 25% |
| `video_p50_watched_actions` | int | 50% |
| `video_p75_watched_actions` | int | 75% |
| `video_p100_watched_actions` | int | 100% |
| `video_avg_time_watched_actions` | seconds | Medie |
| `video_thruplay_watched_actions` | int | ThruPlay |

### 1.5 ENGAGEMENT
| Metric Raw | Tip | Note |
|------------|-----|------|
| `actions[post_engagement]` | int | Total |
| `actions[page_engagement]` | int | Page |
| `actions[post_reaction]` | int | Reacții |
| `actions[comment]` | int | Comentarii |
| `actions[post_save]` | int | Salvări |
| `actions[onsite_conversion.post_save]` | int | - |

### 1.6 MESSAGING
| Metric Raw | Tip | Note |
|------------|-----|------|
| `actions[onsite_conversion.messaging_conversation_started_7d]` | int | Conversații noi |
| `actions[onsite_conversion.messaging_first_reply]` | int | Primul răspuns |

### 1.7 QUALITY & RELEVANCE
| Metric Raw | Tip | Note |
|------------|-----|------|
| `quality_ranking` | enum | BELOW_AVERAGE/AVERAGE/ABOVE_AVERAGE |
| `engagement_rate_ranking` | enum | - |
| `conversion_rate_ranking` | enum | - |

### 1.8 INSTABIL / DEPRECATED
| Metric Raw | Status | Note |
|------------|--------|------|
| `relevance_score` | DEPRECATED | Nu mai există |
| `estimated_ad_recallers` | INSTABIL | Se schimbă frecvent |
| `cost_per_estimated_ad_recallers` | INSTABIL | - |

---

## GOOGLE ADS - Categorii Raw

### 2.1 DELIVERY (Livrare de bază)
| Metric Raw | Tip | Note |
|------------|-----|------|
| `metrics.impressions` | int | - |
| `metrics.clicks` | int | - |
| `metrics.cost_micros` | int | ÷ 1,000,000 |
| `metrics.ctr` | float | API-calculated |
| `metrics.average_cpc` | int | micros |
| `metrics.average_cpm` | int | micros |

### 2.2 CONVERSIONS
| Metric Raw | Tip | Note |
|------------|-----|------|
| `metrics.conversions` | float | Poate fi fracționat |
| `metrics.conversions_value` | float | - |
| `metrics.all_conversions` | float | Include view-through |
| `metrics.all_conversions_value` | float | - |
| `metrics.view_through_conversions` | int | - |
| `metrics.cost_per_conversion` | int | micros |
| `metrics.cost_per_all_conversions` | int | micros |
| `metrics.value_per_conversion` | float | - |
| `metrics.conversions_by_conversion_date` | float | Data conversiei |

### 2.3 SEARCH SPECIFIC
| Metric Raw | Tip | Note |
|------------|-----|------|
| `metrics.search_impression_share` | float | % |
| `metrics.search_top_impression_share` | float | Top of page |
| `metrics.search_absolute_top_impression_share` | float | Absolute top |
| `metrics.search_budget_lost_impression_share` | float | Pierdut buget |
| `metrics.search_rank_lost_impression_share` | float | Pierdut rank |
| `metrics.search_exact_match_impression_share` | float | Exact match |
| `metrics.average_page_views` | float | - |

### 2.4 SHOPPING / PMAX
| Metric Raw | Tip | Note |
|------------|-----|------|
| `metrics.all_conversions_from_interactions_rate` | float | - |
| `metrics.cross_device_conversions` | float | - |
| `metrics.content_impression_share` | float | Display |
| `metrics.content_budget_lost_impression_share` | float | - |

### 2.5 VIDEO (YouTube)
| Metric Raw | Tip | Note |
|------------|-----|------|
| `metrics.video_views` | int | - |
| `metrics.video_quartile_p25_rate` | float | % |
| `metrics.video_quartile_p50_rate` | float | % |
| `metrics.video_quartile_p75_rate` | float | % |
| `metrics.video_quartile_p100_rate` | float | % |
| `metrics.video_view_rate` | float | % |
| `metrics.average_cpv` | int | micros |
| `metrics.engagements` | int | - |
| `metrics.engagement_rate` | float | - |

### 2.6 BIDDING & OPTIMIZATION
| Metric Raw | Tip | Note |
|------------|-----|------|
| `metrics.optimization_score_uplift` | float | - |
| `metrics.historical_quality_score` | int | 1-10 |
| `metrics.historical_creative_quality_score` | enum | - |
| `metrics.historical_landing_page_quality_score` | enum | - |

### 2.7 INSTABIL / GRANULAR EXCESIV
| Metric Raw | Status | Note |
|------------|--------|------|
| `metrics.active_view_*` | INSTABIL | ViewAbility metrici |
| `metrics.gmail_*` | DEPRECATED | Gmail ads |
| `metrics.interaction_event_types` | GRANULAR | Prea detaliat |
| `metrics.sk_ad_network_*` | SPECIFIC | iOS only |

---

## GA4 - Categorii Raw

### 3.1 USERS & SESSIONS
| Metric Raw | Tip | Note |
|------------|-----|------|
| `totalUsers` | int | - |
| `newUsers` | int | - |
| `activeUsers` | int | - |
| `sessions` | int | - |
| `sessionsPerUser` | float | - |
| `engagedSessions` | int | >10s sau conversie |
| `engagementRate` | float | engagedSessions/sessions |

### 3.2 ENGAGEMENT
| Metric Raw | Tip | Note |
|------------|-----|------|
| `userEngagementDuration` | seconds | Total |
| `averageSessionDuration` | seconds | Medie |
| `screenPageViews` | int | - |
| `screenPageViewsPerSession` | float | - |
| `bounceRate` | float | % |
| `eventCount` | int | - |
| `eventsPerSession` | float | - |

### 3.3 ECOMMERCE
| Metric Raw | Tip | Note |
|------------|-----|------|
| `ecommercePurchases` | int | Tranzacții |
| `purchaseRevenue` | currency | - |
| `totalRevenue` | currency | Include refunds |
| `averagePurchaseRevenue` | currency | Per tranzacție |
| `addToCarts` | int | - |
| `checkouts` | int | - |
| `itemsViewed` | int | - |
| `itemsAddedToCart` | int | - |
| `itemsPurchased` | int | - |
| `cartToViewRate` | float | % |
| `purchaseToViewRate` | float | % |

### 3.4 ACQUISITION
| Metric Raw | Tip | Note |
|------------|-----|------|
| `sessionSource` | string | Dimensiune |
| `sessionMedium` | string | Dimensiune |
| `sessionCampaignName` | string | Dimensiune |
| `firstUserSource` | string | Prima vizită |
| `firstUserMedium` | string | Prima vizită |

### 3.5 CONVERSIONS (Events)
| Metric Raw | Tip | Note |
|------------|-----|------|
| `conversions` | int | Evenimente marcate |
| `eventValue` | currency | - |
| `eventCountPerUser` | float | - |

### 3.6 GRANULAR / ZGOMOT
| Metric Raw | Status | Note |
|------------|--------|------|
| `scrolledUsers` | GRANULAR | Prea specific |
| `crashAffectedUsers` | SPECIFIC | App only |
| `dauPerMau` | AGREGAT | Calculabil |
| `wauPerMau` | AGREGAT | Calculabil |

---

# PARTEA 2: Set Minim Metrici Normalizate

---

## METRICI CORE (Obligatorii - Toți Clienții)

| Metric Normalizat | Tip | Meta Ads | Google Ads | GA4 |
|-------------------|-----|----------|------------|-----|
| `spend` | decimal | `spend` | `cost_micros / 1M` | N/A |
| `impressions` | int | `impressions` | `metrics.impressions` | N/A |
| `clicks` | int | `clicks` | `metrics.clicks` | N/A |
| `reach` | int | `reach` | N/A | `totalUsers` |
| `ctr` | decimal | `ctr` | `metrics.ctr` | N/A |
| `cpc` | decimal | `cpc` | `average_cpc / 1M` | N/A |
| `cpm` | decimal | calc | `average_cpm / 1M` | N/A |

---

## METRICI CONVERSIE (Obligatorii pentru Ads)

| Metric Normalizat | Tip | Meta Ads | Google Ads | GA4 |
|-------------------|-----|----------|------------|-----|
| `conversions` | int | `actions[purchase]` + `actions[lead]` | `metrics.conversions` | `conversions` |
| `conversion_value` | decimal | `action_values[*]` sum | `conversions_value` | `purchaseRevenue` |
| `leads` | int | `actions[lead]` | seg. by conv. action | event count |
| `purchases` | int | `actions[purchase]` | seg. by conv. action | `ecommercePurchases` |
| `cpa` | decimal | calc | `cost_per_conversion / 1M` | N/A |
| `roas` | decimal | calc | calc | calc |

---

## METRICI VIDEO (Opțional - Doar Video Ads)

| Metric Normalizat | Tip | Meta Ads | Google Ads | GA4 |
|-------------------|-----|----------|------------|-----|
| `video_views` | int | `video_play_actions` | `metrics.video_views` | N/A |
| `video_view_rate` | decimal | calc | `video_view_rate` | N/A |
| `video_p25` | int | `video_p25_watched_actions` | calc din rate | N/A |
| `video_p50` | int | `video_p50_watched_actions` | calc din rate | N/A |
| `video_p75` | int | `video_p75_watched_actions` | calc din rate | N/A |
| `video_p100` | int | `video_p100_watched_actions` | calc din rate | N/A |
| `cpv` | decimal | calc | `average_cpv / 1M` | N/A |

---

## METRICI ECOMMERCE (Opțional - Doar Clienți Ecomm)

| Metric Normalizat | Tip | Meta Ads | Google Ads | GA4 |
|-------------------|-----|----------|------------|-----|
| `revenue` | decimal | `action_values[purchase]` | `conversions_value` | `purchaseRevenue` |
| `transactions` | int | `actions[purchase]` | seg | `ecommercePurchases` |
| `avg_order_value` | decimal | calc | calc | `averagePurchaseRevenue` |
| `add_to_cart` | int | `actions[add_to_cart]` | seg | `addToCarts` |
| `initiate_checkout` | int | `actions[initiate_checkout]` | seg | `checkouts` |

---

## METRICI ENGAGEMENT (Opțional - Awareness/Branding)

| Metric Normalizat | Tip | Meta Ads | Google Ads | GA4 |
|-------------------|-----|----------|------------|-----|
| `engagements` | int | `actions[post_engagement]` | `metrics.engagements` | `engagedSessions` |
| `engagement_rate` | decimal | calc | `engagement_rate` | `engagementRate` |
| `likes_reactions` | int | `actions[post_reaction]` | N/A | N/A |
| `comments` | int | `actions[comment]` | N/A | N/A |
| `shares` | int | `actions[share]` | N/A | N/A |
| `saves` | int | `actions[post_save]` | N/A | N/A |

---

## METRICI GA4-ONLY (Opțional - Analytics)

| Metric Normalizat | Tip | Sursă GA4 |
|-------------------|-----|-----------|
| `users` | int | `totalUsers` |
| `new_users` | int | `newUsers` |
| `sessions` | int | `sessions` |
| `bounce_rate` | decimal | `bounceRate` |
| `avg_session_duration` | decimal | `averageSessionDuration` |
| `pages_per_session` | decimal | `screenPageViewsPerSession` |

---

## METRICI SEARCH (Opțional - Doar Google Search)

| Metric Normalizat | Tip | Sursă Google Ads |
|-------------------|-----|------------------|
| `impression_share` | decimal | `search_impression_share` |
| `top_impression_share` | decimal | `search_top_impression_share` |
| `lost_impression_share_budget` | decimal | `search_budget_lost_impression_share` |
| `lost_impression_share_rank` | decimal | `search_rank_lost_impression_share` |

---

# PARTEA 3: Mapping Detaliat Brut → Normalizat

---

## REGULI DE TRANSFORMARE

### Valori monetare
```
Meta:    spend        → spend (direct, în moneda contului)
Google:  cost_micros  → spend (÷ 1,000,000)
GA4:     N/A          → N/A (GA4 nu are spend)
```

### Conversii (cea mai complexă)
```
Meta:    actions[] array → parse action_type, sum values
Google:  metrics.conversions → direct (poate fi float, round)
GA4:     conversions → direct (event-based)

Mapping actions[]:
- action_type = "purchase"           → purchases
- action_type = "lead"               → leads
- action_type = "add_to_cart"        → add_to_cart
- action_type = "initiate_checkout"  → initiate_checkout
- action_type = "complete_registration" → registrations
- action_type = "contact"            → contact_submissions
```

### Metrici calculate
```
ctr = clicks / impressions * 100
cpm = spend / impressions * 1000
cpc = spend / clicks
cpa = spend / conversions
roas = conversion_value / spend
engagement_rate = engagements / impressions * 100
video_view_rate = video_views / impressions * 100
```

---

# PARTEA 4: Ce Rămâne DOAR în raw_payload_json

---

## NU SE PROPAGĂ ÎN metrics_json

### META ADS - Excluse
| Metric | Motiv |
|--------|-------|
| `quality_ranking` | Enum, nu numeric agregabil |
| `engagement_rate_ranking` | Enum |
| `conversion_rate_ranking` | Enum |
| `estimated_ad_recallers` | Instabil, deprecated curând |
| `ad_id`, `adset_id`, `campaign_id` | Deja în coloane separate |
| `date_start`, `date_stop` | Deja în coloana `date` |
| `account_id` | Deja FK |
| Orice metric cu prefix `unique_` | Redundant cu versiunea normală |
| `inline_*` | Breakdown granular |
| `outbound_clicks_ctr` | Derivabil |
| `website_ctr` | Derivabil |

### GOOGLE ADS - Excluse
| Metric | Motiv |
|--------|-------|
| `active_view_*` | Viewability - instabil |
| `gmail_*` | Deprecated |
| `sk_ad_network_*` | iOS specific |
| `interaction_event_types` | Granular excesiv |
| `historical_*` | Date istorice, nu curente |
| `segments.*` | Dimensiuni, nu metrici |
| `customer.*` | Metadata cont |
| `campaign.*` | Metadata, nu performance |

### GA4 - Excluse
| Metric | Motiv |
|--------|-------|
| `crashAffectedUsers` | App-only |
| `crashFreeUsersRate` | App-only |
| `dauPerMau`, `wauPerMau` | Calculabile din users |
| `scrolledUsers` | Prea granular |
| Dimensiuni (`source`, `medium`) | Deja în coloane breakdown |
| `firstUser*` | Attribution complexity |

---

## NU SE PROPAGĂ ÎN weekly_snapshots

| Categorie | Exemple | Motiv |
|-----------|---------|-------|
| Breakdown per ad/adset | metrics per ad_id | Prea granular pentru audit |
| Hourly data | orice metric hourly | Zgomot |
| Quality rankings | quality_ranking | Non-numeric |
| Impression share details | lost_is_budget per day | Variabilitate zilnică mare |
| Video quartiles | video_p25, p50, p75 | Aggregare non-sensical |
| Unique variants | unique_clicks | Redundant |

---

## NU SE PROPAGĂ ÎN RAG / AI

| Categorie | Exemple | Motiv |
|-----------|---------|-------|
| Raw IDs | campaign_id, ad_id | Non-semantic |
| Micros values | cost_micros | Confuz |
| Timestamps | created_time, updated_time | Zgomot |
| Technical metadata | api_version, request_id | Irelevant |
| Deprecated metrics | relevance_score | Outdated |
| Platform-specific jargon | sk_ad_network | Confuz |

---

# PARTEA 5: Reguli Weekly Snapshots

---

## CE INTRĂ ÎN WEEKLY_SNAPSHOTS

### Agregări SUM
```
total_spend         = SUM(spend) din daily_metrics
total_impressions   = SUM(impressions)
total_clicks        = SUM(clicks)
total_conversions   = SUM(conversions)
total_leads         = SUM(leads)
total_revenue       = SUM(revenue)
total_video_views   = SUM(video_views)
total_engagements   = SUM(engagements)
```

### Agregări AVERAGE (weighted unde e cazul)
```
avg_ctr  = SUM(clicks) / SUM(impressions) * 100
avg_cpc  = SUM(spend) / SUM(clicks)
avg_cpm  = SUM(spend) / SUM(impressions) * 1000
avg_cpa  = SUM(spend) / SUM(conversions)
avg_roas = SUM(revenue) / SUM(spend)
```

### Week-over-Week
```
spend_wow_change = (this_week.spend - last_week.spend) / last_week.spend * 100
conv_wow_change  = (this_week.conversions - last_week.conversions) / last_week.conversions * 100
roas_wow_change  = (this_week.roas - last_week.roas) / last_week.roas * 100
```

### KPI Status
```
Pentru fiecare KPI activ al clientului:

progress = actual_value / target_value

Dacă progress >= 1.0:       status = "exceeded"
Dacă progress >= 0.80:      status = "on_track"
Dacă progress >= 0.60:      status = "warning"
Dacă progress < 0.60:       status = "critical"
```

---

## CE NU INTRĂ ÎN WEEKLY_SNAPSHOTS

| Element | Motiv |
|---------|-------|
| Metrici per campaign/adset/ad | Prea granular |
| Daily breakdown | Se pierde scopul agregării |
| Video quartiles | SUM nu are sens |
| Quality rankings | Enum, nu agregabil |
| Impression share | Medie nu e relevantă |
| Unique metrics | Redundant |
| Raw action types | Deja sumarizate în conversions |

---

## REGULA GENERALĂ: Granular vs Zgomot

```
┌─────────────────────────────────────────────────────────────┐
│ ÎNTREBARE: Această metrică ajută la o DECIZIE SĂPTĂMÂNALĂ?  │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
         DA → include                    NU → exclude
              │                               │
              ▼                               ▼
    Exemple:                        Exemple:
    - Spend total                   - Spend per ad
    - ROAS mediu                    - CTR per hour
    - Conversii totale              - Impression share daily
    - CPA mediu                     - Video p25/p50/p75
    - WoW changes                   - Quality ranking
```

---

## STRUCTURA SUMMARY_TEXT (pentru RAG)

Template generat automat:

```
Săptămâna {week_number}/{year} pentru {client_name}:

PERFORMANȚĂ:
- Spend total: {spend} {currency} ({spend_wow_change}% vs săpt. anterioară)
- Conversii: {conversions} ({conv_wow_change}% vs săpt. anterioară)
- ROAS: {roas}x ({roas_wow_change}% vs săpt. anterioară)
- CPA mediu: {cpa} {currency}

STATUS KPI-uri:
- Spend: {kpi_spend_status} ({spend_progress}% din target)
- Conversii: {kpi_conv_status} ({conv_progress}% din target)
- ROAS: {kpi_roas_status} ({roas_progress}% din target)

HIGHLIGHTS:
{highlights[]}

CONCERNS:
{concerns[]}
```

---

## MATRICE FINALĂ: Fluxul Datelor

```
┌──────────────────┬──────────────┬─────────────────┬─────────────┬─────────┐
│ Metric           │ raw_payload  │ metrics_json    │ weekly_snap │ RAG/AI  │
├──────────────────┼──────────────┼─────────────────┼─────────────┼─────────┤
│ spend            │ ✓            │ ✓ (normalized)  │ ✓ (SUM)     │ ✓       │
│ impressions      │ ✓            │ ✓               │ ✓ (SUM)     │ ✓       │
│ clicks           │ ✓            │ ✓               │ ✓ (SUM)     │ ✓       │
│ conversions      │ ✓            │ ✓ (aggregated)  │ ✓ (SUM)     │ ✓       │
│ revenue          │ ✓            │ ✓               │ ✓ (SUM)     │ ✓       │
│ ctr/cpc/cpm      │ ✓            │ ✓ (calculated)  │ ✓ (AVG)     │ ✓       │
│ cpa/roas         │ ✓            │ ✓ (calculated)  │ ✓ (AVG)     │ ✓       │
│ video_views      │ ✓            │ ✓               │ ✓ (SUM)     │ ✓       │
│ video_p25/50/75  │ ✓            │ ✓               │ ✗           │ ✗       │
│ actions[] raw    │ ✓            │ ✗ (parsed)      │ ✗           │ ✗       │
│ quality_ranking  │ ✓            │ ✗               │ ✗           │ ✗       │
│ impression_share │ ✓            │ ✓               │ ✗           │ ✗       │
│ cost_micros      │ ✓            │ ✗ (converted)   │ ✗           │ ✗       │
│ ad_id/adset_id   │ ✓            │ ✗ (in columns)  │ ✗           │ ✗       │
│ WoW changes      │ ✗            │ ✗               │ ✓           │ ✓       │
│ KPI status       │ ✗            │ ✗               │ ✓           │ ✓       │
└──────────────────┴──────────────┴─────────────────┴─────────────┴─────────┘

Legendă:
✓ = prezent/propagat
✗ = exclus/netransformat
```

---

## DECIZII CHEIE

| # | Decizie | Rațiune |
|---|---------|---------|
| 1 | Spend, Impressions, Clicks, Conversions, Revenue sunt OBLIGATORII | KPI-uri universale |
| 2 | Video metrics doar dacă clientul are video ads | Reduce zgomot |
| 3 | Ecommerce metrics doar dacă clientul are ecomm | Reduce zgomot |
| 4 | Quality rankings NU se propagă | Non-aggregabile |
| 5 | Impression share NU intră în weekly | Volatilitate zilnică mare |
| 6 | Video quartiles NU intră în weekly | SUM nu are sens semantic |
| 7 | AI vede DOAR text din weekly_snapshots | Controlat, stabil |
| 8 | raw_payload_json = backup complet | Recovery și debug |
| 9 | Micros se convertesc la import | Evită confuzii |
| 10 | WoW se calculează la agregare | Relevante pentru audit |
