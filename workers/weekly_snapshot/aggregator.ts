/**
 * Weekly Snapshot Engine - Aggregator Module
 * ===========================================
 * STEP 3 din WEEKLY_SNAPSHOT_ENGINE.md: AGREGARE METRICI
 *
 * Responsabilități:
 * - Sumează metricile absolute (spend, impressions, clicks, etc.)
 * - Calculează metrici derivate (CTR, CPC, CPM, CPA, ROAS)
 * - Protecție divide-by-zero
 */

import type { DailyMetricRow, AggregatedMetrics } from './types';

// ============================================================================
// AGGREGATION FUNCTIONS
// ============================================================================

/**
 * Agregă metricile zilnice într-un total.
 *
 * Implementează STEP 3, pași 13-15 din design.
 */
export function aggregateMetrics(metrics: DailyMetricRow[]): AggregatedMetrics {
  // TODO: Implementare STEP 3, pași 13-15 din design
  //
  // 13. Inițializează acumulatori la 0
  // 14. Pentru fiecare rând, adună valorile (cu COALESCE la 0)
  // 15. Calculează metrici derivate cu protecție divide-by-zero

  console.log(`[aggregator] aggregateMetrics(${metrics.length} rows): STUB`);

  // STUB: Inițializare acumulatori
  let totalSpend = 0;
  let totalImpressions = 0;
  let totalClicks = 0;
  let totalReach = 0;
  let totalConversions = 0;
  let totalLeads = 0;
  let totalPurchases = 0;
  let totalRevenue = 0;
  let totalVideoViews = 0;
  let totalEngagements = 0;

  // TODO: Pas 14 - Iterare și sumare
  // for (const row of metrics) {
  //   totalSpend += row.spend ?? 0;
  //   totalImpressions += row.impressions ?? 0;
  //   // ... etc
  // }

  // STUB: Pas 15 - Calcul metrici derivate
  const avgCtr = calculateCtr(totalClicks, totalImpressions);
  const avgCpc = calculateCpc(totalSpend, totalClicks);
  const avgCpm = calculateCpm(totalSpend, totalImpressions);
  const avgCpa = calculateCpa(totalSpend, totalConversions);
  const avgRoas = calculateRoas(totalRevenue, totalSpend);

  return {
    totalSpend,
    totalImpressions,
    totalClicks,
    totalReach,
    totalConversions,
    totalLeads,
    totalPurchases,
    totalRevenue,
    totalVideoViews,
    totalEngagements,
    avgCtr,
    avgCpc,
    avgCpm,
    avgCpa,
    avgRoas,
  };
}

// ============================================================================
// DERIVED METRICS CALCULATIONS (cu protecție divide-by-zero)
// ============================================================================

/**
 * CTR = clicks / impressions * 100
 */
export function calculateCtr(clicks: number, impressions: number): number | null {
  // Pas 15a: DACĂ total_impressions > 0 ATUNCI (clicks/impressions)*100 ALTFEL NULL
  if (impressions <= 0) return null;
  return (clicks / impressions) * 100;
}

/**
 * CPC = spend / clicks
 */
export function calculateCpc(spend: number, clicks: number): number | null {
  // Pas 15b: DACĂ total_clicks > 0 ATUNCI spend/clicks ALTFEL NULL
  if (clicks <= 0) return null;
  return spend / clicks;
}

/**
 * CPM = spend / impressions * 1000
 */
export function calculateCpm(spend: number, impressions: number): number | null {
  // Pas 15c: DACĂ total_impressions > 0 ATUNCI (spend/impressions)*1000 ALTFEL NULL
  if (impressions <= 0) return null;
  return (spend / impressions) * 1000;
}

/**
 * CPA = spend / conversions
 */
export function calculateCpa(spend: number, conversions: number): number | null {
  // Pas 15d: DACĂ total_conversions > 0 ATUNCI spend/conversions ALTFEL NULL
  if (conversions <= 0) return null;
  return spend / conversions;
}

/**
 * ROAS = revenue / spend
 */
export function calculateRoas(revenue: number, spend: number): number | null {
  // Pas 15e: DACĂ total_spend > 0 ATUNCI revenue/spend ALTFEL NULL
  if (spend <= 0) return null;
  return revenue / spend;
}

// ============================================================================
// EMPTY AGGREGATION
// ============================================================================

/**
 * Returnează o agregare goală (toate valorile 0 sau null).
 */
export function emptyAggregation(): AggregatedMetrics {
  return {
    totalSpend: 0,
    totalImpressions: 0,
    totalClicks: 0,
    totalReach: 0,
    totalConversions: 0,
    totalLeads: 0,
    totalPurchases: 0,
    totalRevenue: 0,
    totalVideoViews: 0,
    totalEngagements: 0,
    avgCtr: null,
    avgCpc: null,
    avgCpm: null,
    avgCpa: null,
    avgRoas: null,
  };
}
