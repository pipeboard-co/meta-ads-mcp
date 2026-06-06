/**
 * Weekly Snapshot Engine - Week-over-Week Module
 * ================================================
 * STEP 4 din WEEKLY_SNAPSHOT_ENGINE.md: CALCUL WoW
 *
 * Responsabilități:
 * - Calculează schimbarea procentuală pentru fiecare metrică
 * - Determină direcția schimbării (up/down/stable)
 * - Determină trend-ul general (improving/declining/stable)
 * - Marchează îmbunătățirile pentru metrici inverse (CPA)
 */

import type { AggregatedMetrics, WowChange, WowResult } from './types';

// ============================================================================
// WOW CHANGE CALCULATION
// ============================================================================

/**
 * Calculează schimbarea procentuală între două valori.
 *
 * Implementează STEP 4, pas 17 din design.
 *
 * Reguli:
 * - DACĂ previous = 0 SAU previous = NULL:
 *   - DACĂ current > 0 → +100.00 (creștere de la 0)
 *   - ALTFEL → 0.00 (fără schimbare)
 * - ALTFEL → ((current - previous) / previous) * 100
 */
export function calculateWowChange(
  current: number | null,
  previous: number | null,
  isLowerBetter: boolean = false
): WowChange {
  // TODO: Implementare STEP 4, pas 17 din design

  console.log(`[wow] calculateWowChange(${current}, ${previous}): STUB`);

  // Handle null values
  const curr = current ?? 0;
  const prev = previous ?? 0;

  let changePercent: number | null;
  let direction: 'up' | 'down' | 'stable';

  if (prev === 0 || previous === null) {
    if (curr > 0) {
      changePercent = 100.0;
      direction = 'up';
    } else {
      changePercent = 0.0;
      direction = 'stable';
    }
  } else {
    changePercent = ((curr - prev) / prev) * 100;

    if (changePercent > 1) {
      direction = 'up';
    } else if (changePercent < -1) {
      direction = 'down';
    } else {
      direction = 'stable';
    }
  }

  const result: WowChange = {
    changePercent: Math.round(changePercent * 100) / 100, // Round to 2 decimals
    direction,
    previousValue: previous,
  };

  // Pentru metrici unde mai mic = mai bine (CPA)
  if (isLowerBetter) {
    result.isImprovement = direction === 'down';
  }

  return result;
}

// ============================================================================
// TREND DETERMINATION
// ============================================================================

/**
 * Determină trend-ul general bazat pe WoW changes.
 *
 * Implementează STEP 4, pas 19 din design.
 *
 * Reguli:
 * - DACĂ roas_wow > 10 ȘI conversions_wow > 0 → "improving"
 * - DACĂ roas_wow < -10 SAU conversions_wow < -20 → "declining"
 * - ALTFEL → "stable"
 */
export function determineTrend(
  roasWow: WowChange,
  conversionsWow: WowChange
): 'improving' | 'declining' | 'stable' {
  // TODO: Implementare STEP 4, pas 19 din design

  console.log('[wow] determineTrend: STUB');

  const roasChange = roasWow.changePercent ?? 0;
  const convChange = conversionsWow.changePercent ?? 0;

  if (roasChange > 10 && convChange > 0) {
    return 'improving';
  }

  if (roasChange < -10 || convChange < -20) {
    return 'declining';
  }

  return 'stable';
}

// ============================================================================
// MAIN WOW CALCULATION
// ============================================================================

/**
 * Calculează toate WoW changes pentru metricile agregate.
 *
 * Implementează STEP 4, pas 18 din design.
 */
export function calculateAllWowChanges(
  current: AggregatedMetrics,
  previous: AggregatedMetrics
): WowResult {
  // TODO: Implementare STEP 4, pas 18 din design
  //
  // 18. Calculează WoW pentru fiecare metrică:
  //     - spend_wow, impressions_wow, clicks_wow
  //     - conversions_wow, revenue_wow
  //     - roas_wow, cpa_wow (NOTĂ: pentru CPA, negativ = îmbunătățire)

  console.log('[wow] calculateAllWowChanges: STUB');

  const spend = calculateWowChange(current.totalSpend, previous.totalSpend);
  const impressions = calculateWowChange(current.totalImpressions, previous.totalImpressions);
  const clicks = calculateWowChange(current.totalClicks, previous.totalClicks);
  const conversions = calculateWowChange(current.totalConversions, previous.totalConversions);
  const revenue = calculateWowChange(current.totalRevenue, previous.totalRevenue);
  const roas = calculateWowChange(current.avgRoas, previous.avgRoas);
  const cpa = calculateWowChange(current.avgCpa, previous.avgCpa, true); // isLowerBetter

  const trend = determineTrend(roas, conversions);

  return {
    spend,
    impressions,
    clicks,
    conversions,
    revenue,
    roas,
    cpa,
    trend,
  };
}

// ============================================================================
// EMPTY WOW RESULT
// ============================================================================

/**
 * Returnează un WoW result gol (când nu există date anterioare).
 */
export function emptyWowResult(): WowResult {
  const emptyChange: WowChange = {
    changePercent: null,
    direction: 'stable',
    previousValue: null,
  };

  return {
    spend: emptyChange,
    impressions: emptyChange,
    clicks: emptyChange,
    conversions: emptyChange,
    revenue: emptyChange,
    roas: emptyChange,
    cpa: { ...emptyChange, isImprovement: undefined },
    trend: 'stable',
  };
}
