/**
 * Weekly Snapshot Engine - KPI Engine Module
 * ============================================
 * STEP 5 din WEEKLY_SNAPSHOT_ENGINE.md: CALCUL KPI STATUS
 *
 * Responsabilități:
 * - Extrage KPI-urile active pentru client și perioadă
 * - Mapează metricile agregate la KPI-uri
 * - Calculează target-ul proratat
 * - Calculează achievement-ul
 * - Determină status-ul (exceeded/on_track/warning/critical)
 */

import type {
  AggregatedMetrics,
  KpiDefinition,
  KpiStatusEntry,
  KpiResult,
  KpiFlag,
} from './types';

// ============================================================================
// KPI EXTRACTION
// ============================================================================

/**
 * Extrage KPI-urile active pentru un client într-o perioadă.
 *
 * Query: SELECT * FROM kpis
 *        WHERE client_id = :clientId
 *        AND :weekStart >= period_start
 *        AND :weekEnd <= period_end
 */
export async function extractActiveKpis(
  clientId: string,
  weekStart: Date,
  weekEnd: Date
): Promise<KpiDefinition[]> {
  // TODO: Implementare STEP 5, pas 20 din design
  //
  // 20. Extrage KPI-urile active pentru client și perioadă:
  //     active_kpis[] = SELECT * FROM kpis
  //                     WHERE client_id = :client_id
  //                     AND :week_start >= period_start
  //                     AND :week_end <= period_end

  console.log(`[kpi_engine] extractActiveKpis(${clientId}): STUB`);

  // STUB: Returnează listă goală
  return [];
}

// ============================================================================
// METRIC MAPPING
// ============================================================================

/**
 * Mapează numele metricii KPI la valoarea din AggregatedMetrics.
 *
 * Implementează STEP 5, pas 22a din design.
 */
export function getActualValueForKpi(
  metricName: string,
  metrics: AggregatedMetrics
): number | null {
  // TODO: Implementare STEP 5, pas 22a din design
  //
  // 22a. Identifică valoarea actuală:
  //      MATCH kpi.metric_name:
  //        "spend" → actual = total_spend
  //        "conversions" → actual = total_conversions
  //        ... etc

  const mapping: Record<string, number | null> = {
    spend: metrics.totalSpend,
    impressions: metrics.totalImpressions,
    clicks: metrics.totalClicks,
    conversions: metrics.totalConversions,
    leads: metrics.totalLeads,
    purchases: metrics.totalPurchases,
    revenue: metrics.totalRevenue,
    roas: metrics.avgRoas,
    cpa: metrics.avgCpa,
    ctr: metrics.avgCtr,
    cpc: metrics.avgCpc,
    cpm: metrics.avgCpm,
  };

  return mapping[metricName] ?? null;
}

// ============================================================================
// PRORATION LOGIC
// ============================================================================

/**
 * Calculează target-ul proratat și progresul perioadei.
 *
 * Implementează STEP 5, pași 22b-22c din design.
 */
export function calculateProratedTarget(
  kpi: KpiDefinition,
  weekEnd: Date
): { proratedTarget: number; periodProgress: number } {
  // TODO: Implementare STEP 5, pași 22b-22c din design
  //
  // 22b. Calculează progresul în perioada KPI:
  //      kpi_duration_days = period_end - period_start + 1
  //      elapsed_days = week_end - period_start + 1
  //      period_progress = elapsed_days / kpi_duration_days
  //
  // 22c. Calculează target proratat:
  //      DACĂ metric IN (spend, conversions, leads, revenue):
  //        prorated_target = target_value * period_progress
  //      DACĂ metric IN (roas, cpa, ctr):
  //        prorated_target = target_value (nu se proratează)

  console.log('[kpi_engine] calculateProratedTarget: STUB');

  const kpiDurationDays =
    Math.ceil(
      (kpi.periodEnd.getTime() - kpi.periodStart.getTime()) / (24 * 60 * 60 * 1000)
    ) + 1;

  let elapsedDays =
    Math.ceil(
      (weekEnd.getTime() - kpi.periodStart.getTime()) / (24 * 60 * 60 * 1000)
    ) + 1;
  elapsedDays = Math.min(elapsedDays, kpiDurationDays);

  const periodProgress = elapsedDays / kpiDurationDays;

  // Metrici care se proratează (cumulative)
  const cumulativeMetrics = ['spend', 'conversions', 'leads', 'revenue', 'purchases', 'impressions', 'clicks'];

  let proratedTarget: number;
  if (cumulativeMetrics.includes(kpi.metricName)) {
    proratedTarget = kpi.targetValue * periodProgress;
  } else {
    // Metrici rate (roas, cpa, ctr) - nu se proratează
    proratedTarget = kpi.targetValue;
  }

  return { proratedTarget, periodProgress };
}

// ============================================================================
// STATUS DETERMINATION
// ============================================================================

/**
 * Determină status-ul KPI bazat pe achievement.
 *
 * Implementează STEP 5, pas 22e din design.
 */
export function determineKpiStatus(
  metricName: string,
  actual: number | null,
  proratedTarget: number,
  warningThreshold: number,
  criticalThreshold: number
): 'exceeded' | 'on_track' | 'warning' | 'critical' {
  // TODO: Implementare STEP 5, pas 22e din design
  //
  // 22e. Determină status:
  //      DACĂ metric = "cpa" (mai mic = mai bine):
  //        actual <= target → exceeded
  //        actual <= target * 1.2 → on_track
  //        actual <= target * 1.5 → warning
  //        ALTFEL → critical
  //      ALTFEL (mai mare = mai bine):
  //        achievement >= 1.0 → exceeded
  //        achievement >= warning_threshold → on_track
  //        achievement >= critical_threshold → warning
  //        ALTFEL → critical

  console.log('[kpi_engine] determineKpiStatus: STUB');

  if (actual === null || proratedTarget <= 0) {
    return 'warning'; // Cannot determine
  }

  // CPA: mai mic = mai bine
  if (metricName === 'cpa') {
    if (actual <= proratedTarget) return 'exceeded';
    if (actual <= proratedTarget * 1.2) return 'on_track';
    if (actual <= proratedTarget * 1.5) return 'warning';
    return 'critical';
  }

  // Alte metrici: mai mare = mai bine
  const achievement = actual / proratedTarget;

  if (achievement >= 1.0) return 'exceeded';
  if (achievement >= warningThreshold) return 'on_track';
  if (achievement >= criticalThreshold) return 'warning';
  return 'critical';
}

// ============================================================================
// MAIN KPI CALCULATION
// ============================================================================

/**
 * Calculează status-ul tuturor KPI-urilor pentru un client.
 *
 * Orchestrează STEP 5 complet.
 */
export async function calculateKpiStatus(
  clientId: string,
  weekStart: Date,
  weekEnd: Date,
  metrics: AggregatedMetrics
): Promise<KpiResult> {
  // TODO: Implementare STEP 5, pași 20-22 din design

  console.log(`[kpi_engine] calculateKpiStatus(${clientId}): STUB`);

  const flags: KpiFlag[] = [];
  const kpiStatus: Record<string, KpiStatusEntry> = {};

  // Pas 20: Extrage KPI-uri active
  const activeKpis = await extractActiveKpis(clientId, weekStart, weekEnd);

  // Pas 21: Verifică dacă există KPI-uri
  if (activeKpis.length === 0) {
    flags.push('NO_KPIS_DEFINED');
    return { kpiStatus, flags };
  }

  // Pas 22: Pentru fiecare KPI
  for (const kpi of activeKpis) {
    // 22a: Obține valoarea actuală
    const actual = getActualValueForKpi(kpi.metricName, metrics);

    if (actual === null && !['roas', 'cpa', 'ctr', 'cpc', 'cpm'].includes(kpi.metricName)) {
      flags.push('UNKNOWN_METRIC');
      continue;
    }

    // 22b-22c: Calculează target proratat
    const { proratedTarget, periodProgress } = calculateProratedTarget(kpi, weekEnd);

    if (kpi.targetValue === 0) {
      flags.push('INVALID_KPI_TARGET');
      continue;
    }

    // 22d: Calculează achievement
    const achievementPercent =
      proratedTarget > 0 && actual !== null
        ? (actual / proratedTarget) * 100
        : null;

    // 22e: Determină status
    const status = determineKpiStatus(
      kpi.metricName,
      actual,
      proratedTarget,
      kpi.warningThreshold,
      kpi.criticalThreshold
    );

    // 22f: Salvează
    kpiStatus[kpi.metricName] = {
      target: kpi.targetValue,
      proratedTarget,
      actual,
      achievementPercent,
      status,
      periodProgressPercent: periodProgress * 100,
    };
  }

  return { kpiStatus, flags };
}

// ============================================================================
// EMPTY KPI RESULT
// ============================================================================

/**
 * Returnează un KPI result gol.
 */
export function emptyKpiResult(): KpiResult {
  return {
    kpiStatus: {},
    flags: ['NO_KPIS_DEFINED'],
  };
}
