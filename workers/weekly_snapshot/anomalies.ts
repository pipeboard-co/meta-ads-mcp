/**
 * Weekly Snapshot Engine - Anomalies Module
 * ===========================================
 * STEP 6 din WEEKLY_SNAPSHOT_ENGINE.md: DETECTARE ANOMALII
 *
 * Responsabilități:
 * - Detectează spike-uri/drop-uri de spend
 * - Detectează scăderi semnificative de ROAS
 * - Detectează creșteri de CPA
 * - Detectează drop-uri de conversii fără scădere spend
 * - Verifică completitudinea datelor
 * - Verifică KPI-uri critice
 */

import type { WowResult, KpiResult, Anomaly, DataFlag } from './types';

// ============================================================================
// THRESHOLD CONSTANTS
// ============================================================================

const THRESHOLDS = {
  SPEND_SPIKE: 50, // +50% spend = spike warning
  SPEND_DROP: -50, // -50% spend = info
  ROAS_DECLINE: -30, // -30% ROAS = critical
  CPA_INCREASE: 50, // +50% CPA = warning
  CONVERSION_DROP: -40, // -40% conversions = critical
  DATA_COMPLETENESS: 0.7, // <70% = warning
  MIN_SPEND_FOR_ALERT: 100, // Minimum spend pentru alertă ROAS
};

// ============================================================================
// SPEND ANOMALIES
// ============================================================================

/**
 * Detectează anomalii de spend.
 *
 * Implementează STEP 6, pas 24 din design.
 */
export function detectSpendAnomalies(wow: WowResult): Anomaly[] {
  // TODO: Implementare STEP 6, pas 24 din design
  //
  // 24. Verifică anomalii de spend:
  //     DACĂ spend_wow > 50:
  //       ADAUGĂ {type: "spend_spike", severity: "warning", ...}
  //     DACĂ spend_wow < -50:
  //       ADAUGĂ {type: "spend_drop", severity: "info", ...}

  console.log('[anomalies] detectSpendAnomalies: STUB');

  const anomalies: Anomaly[] = [];
  const spendChange = wow.spend.changePercent ?? 0;

  if (spendChange > THRESHOLDS.SPEND_SPIKE) {
    anomalies.push({
      type: 'spend_spike',
      severity: 'warning',
      metric: 'spend',
      message: `Spend crescut cu ${spendChange.toFixed(1)}% vs săptămâna anterioară`,
      detectedAt: new Date(),
    });
  }

  if (spendChange < THRESHOLDS.SPEND_DROP) {
    anomalies.push({
      type: 'spend_drop',
      severity: 'info',
      metric: 'spend',
      message: `Spend scăzut cu ${Math.abs(spendChange).toFixed(1)}% vs săptămâna anterioară`,
      detectedAt: new Date(),
    });
  }

  return anomalies;
}

// ============================================================================
// PERFORMANCE ANOMALIES
// ============================================================================

/**
 * Detectează anomalii de performanță (ROAS, CPA).
 *
 * Implementează STEP 6, pas 25 din design.
 */
export function detectPerformanceAnomalies(
  wow: WowResult,
  totalSpend: number,
  totalConversions: number
): Anomaly[] {
  // TODO: Implementare STEP 6, pas 25 din design
  //
  // 25. Verifică anomalii de performanță:
  //     DACĂ roas_wow < -30 ȘI total_spend > 100:
  //       ADAUGĂ {type: "roas_decline", severity: "critical", ...}
  //     DACĂ cpa_wow > 50 ȘI total_conversions > 0:
  //       ADAUGĂ {type: "cpa_increase", severity: "warning", ...}

  console.log('[anomalies] detectPerformanceAnomalies: STUB');

  const anomalies: Anomaly[] = [];
  const roasChange = wow.roas.changePercent ?? 0;
  const cpaChange = wow.cpa.changePercent ?? 0;

  if (roasChange < THRESHOLDS.ROAS_DECLINE && totalSpend > THRESHOLDS.MIN_SPEND_FOR_ALERT) {
    anomalies.push({
      type: 'roas_decline',
      severity: 'critical',
      metric: 'roas',
      message: `ROAS scăzut semnificativ cu ${Math.abs(roasChange).toFixed(1)}%`,
      detectedAt: new Date(),
    });
  }

  if (cpaChange > THRESHOLDS.CPA_INCREASE && totalConversions > 0) {
    anomalies.push({
      type: 'cpa_increase',
      severity: 'warning',
      metric: 'cpa',
      message: `CPA crescut cu ${cpaChange.toFixed(1)}%`,
      detectedAt: new Date(),
    });
  }

  return anomalies;
}

// ============================================================================
// VOLUME ANOMALIES
// ============================================================================

/**
 * Detectează anomalii de volum (conversii vs spend).
 *
 * Implementează STEP 6, pas 26 din design.
 */
export function detectVolumeAnomalies(wow: WowResult): Anomaly[] {
  // TODO: Implementare STEP 6, pas 26 din design
  //
  // 26. Verifică anomalii de volum:
  //     DACĂ conversions_wow < -40 ȘI spend_wow >= -10:
  //       ADAUGĂ {type: "conversion_drop", severity: "critical", ...}

  console.log('[anomalies] detectVolumeAnomalies: STUB');

  const anomalies: Anomaly[] = [];
  const convChange = wow.conversions.changePercent ?? 0;
  const spendChange = wow.spend.changePercent ?? 0;

  if (convChange < THRESHOLDS.CONVERSION_DROP && spendChange >= -10) {
    anomalies.push({
      type: 'conversion_drop',
      severity: 'critical',
      metric: 'conversions',
      message: `Conversii scăzute ${Math.abs(convChange).toFixed(1)}% fără scădere proporțională de spend`,
      detectedAt: new Date(),
    });
  }

  return anomalies;
}

// ============================================================================
// DATA QUALITY ANOMALIES
// ============================================================================

/**
 * Detectează probleme de calitate a datelor.
 *
 * Implementează STEP 6, pas 27 din design.
 */
export function detectDataQualityAnomalies(
  dataCompleteness: number,
  daysWithData: number
): Anomaly[] {
  // TODO: Implementare STEP 6, pas 27 din design
  //
  // 27. Verifică lipsă date:
  //     DACĂ data_completeness < 0.7:
  //       ADAUGĂ {type: "incomplete_data", severity: "warning", ...}

  console.log('[anomalies] detectDataQualityAnomalies: STUB');

  const anomalies: Anomaly[] = [];

  if (dataCompleteness < THRESHOLDS.DATA_COMPLETENESS) {
    anomalies.push({
      type: 'incomplete_data',
      severity: 'warning',
      message: `Date incomplete pentru ${daysWithData} din 7 zile`,
      detectedAt: new Date(),
    });
  }

  return anomalies;
}

// ============================================================================
// KPI ANOMALIES
// ============================================================================

/**
 * Detectează KPI-uri în stare critică.
 *
 * Implementează STEP 6, pas 28 din design.
 */
export function detectKpiAnomalies(kpiResult: KpiResult): Anomaly[] {
  // TODO: Implementare STEP 6, pas 28 din design
  //
  // 28. Verifică KPI-uri critice:
  //     PENTRU FIECARE kpi IN kpi_status:
  //       DACĂ kpi.status = "critical":
  //         ADAUGĂ {type: "kpi_critical", severity: "critical", ...}

  console.log('[anomalies] detectKpiAnomalies: STUB');

  const anomalies: Anomaly[] = [];

  for (const [metricName, kpi] of Object.entries(kpiResult.kpiStatus)) {
    if (kpi.status === 'critical') {
      anomalies.push({
        type: 'kpi_critical',
        severity: 'critical',
        metric: metricName,
        message: `KPI ${metricName} la ${kpi.achievementPercent?.toFixed(1) ?? 0}% din target`,
        detectedAt: new Date(),
      });
    }
  }

  return anomalies;
}

// ============================================================================
// MAIN ANOMALY DETECTION
// ============================================================================

/**
 * Detectează toate anomaliile.
 *
 * Orchestrează STEP 6 complet.
 */
export function detectAllAnomalies(
  wow: WowResult,
  kpiResult: KpiResult,
  dataCompleteness: number,
  daysWithData: number,
  totalSpend: number,
  totalConversions: number
): Anomaly[] {
  console.log('[anomalies] detectAllAnomalies: STUB');

  const allAnomalies: Anomaly[] = [
    ...detectSpendAnomalies(wow),
    ...detectPerformanceAnomalies(wow, totalSpend, totalConversions),
    ...detectVolumeAnomalies(wow),
    ...detectDataQualityAnomalies(dataCompleteness, daysWithData),
    ...detectKpiAnomalies(kpiResult),
  ];

  // Sortează după severity (critical > warning > info)
  const severityOrder = { critical: 0, warning: 1, info: 2 };
  allAnomalies.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);

  return allAnomalies;
}
