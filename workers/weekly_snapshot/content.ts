/**
 * Weekly Snapshot Engine - Content Generator Module
 * ===================================================
 * STEP 7 din WEEKLY_SNAPSHOT_ENGINE.md: GENERARE CONTENT
 *
 * Responsabilități:
 * - Generează highlights[] (performanțe bune)
 * - Generează concerns[] (probleme)
 * - Generează recommendations[]
 * - Construiește summary_text pentru RAG
 * - Construiește snapshot_json complet
 */

import type {
  ClientToProcess,
  AggregatedMetrics,
  WowResult,
  KpiResult,
  Anomaly,
  GeneratedContent,
  DataFlag,
  KpiFlag,
} from './types';

// ============================================================================
// HIGHLIGHTS GENERATION
// ============================================================================

/**
 * Generează highlights (performanțe bune).
 *
 * Implementează STEP 7, pași 29-30 din design.
 */
export function generateHighlights(
  wow: WowResult,
  kpiResult: KpiResult,
  metrics: AggregatedMetrics
): string[] {
  // TODO: Implementare STEP 7, pas 30 din design
  //
  // 30. Generează highlights:
  //     DACĂ any kpi.status = "exceeded":
  //       ADAUGĂ "KPI [metric] depășit: [actual] vs target [target]"
  //     DACĂ roas_wow > 20 ȘI avg_roas > 1:
  //       ADAUGĂ "ROAS îmbunătățit cu X%"
  //     ... etc

  console.log('[content] generateHighlights: STUB');

  const highlights: string[] = [];

  // KPI-uri depășite
  for (const [metricName, kpi] of Object.entries(kpiResult.kpiStatus)) {
    if (kpi.status === 'exceeded') {
      highlights.push(
        `KPI ${metricName} depășit: ${kpi.actual} vs target ${kpi.target} (${kpi.achievementPercent?.toFixed(0)}%)`
      );
    }
  }

  // ROAS îmbunătățit
  const roasChange = wow.roas.changePercent ?? 0;
  if (roasChange > 20 && (metrics.avgRoas ?? 0) > 1) {
    highlights.push(
      `ROAS îmbunătățit cu ${roasChange.toFixed(1)}% (de la ${wow.roas.previousValue?.toFixed(2) ?? 'N/A'} la ${metrics.avgRoas?.toFixed(2) ?? 'N/A'})`
    );
  }

  // Conversii crescute
  const convChange = wow.conversions.changePercent ?? 0;
  if (convChange > 20) {
    highlights.push(`Conversii crescute cu ${convChange.toFixed(1)}%`);
  }

  // CPA optimizat
  const cpaChange = wow.cpa.changePercent ?? 0;
  if (cpaChange < -15) {
    highlights.push(`CPA optimizat cu ${Math.abs(cpaChange).toFixed(1)}%`);
  }

  return highlights;
}

// ============================================================================
// CONCERNS GENERATION
// ============================================================================

/**
 * Generează concerns (probleme).
 *
 * Implementează STEP 7, pași 31-32 din design.
 */
export function generateConcerns(
  anomalies: Anomaly[],
  dataCompleteness: number,
  flags: (DataFlag | KpiFlag)[]
): string[] {
  // TODO: Implementare STEP 7, pas 32 din design
  //
  // 32. Generează concerns:
  //     - Din anomalii cu severity warning/critical
  //     - Date lipsă
  //     - KPI-uri nedefinite

  console.log('[content] generateConcerns: STUB');

  const concerns: string[] = [];

  // Din anomalii
  for (const anomaly of anomalies) {
    if (anomaly.severity === 'warning' || anomaly.severity === 'critical') {
      concerns.push(anomaly.message);
    }
  }

  // Date incomplete
  if (dataCompleteness < 1.0) {
    const daysWithData = Math.round(dataCompleteness * 7);
    concerns.push(`Date lipsă pentru ${7 - daysWithData} zile din săptămână`);
  }

  // KPI-uri nedefinite
  if (flags.includes('NO_KPIS_DEFINED')) {
    concerns.push('Nu sunt definite KPI-uri pentru această perioadă');
  }

  return concerns;
}

// ============================================================================
// RECOMMENDATIONS GENERATION
// ============================================================================

/**
 * Generează recomandări.
 *
 * Implementează STEP 7, pas 33 din design.
 */
export function generateRecommendations(
  kpiResult: KpiResult,
  wow: WowResult
): string[] {
  // TODO: Implementare STEP 7, pas 33 din design
  //
  // 33. Generează recommendations[]:
  //     DACĂ any kpi.status = "critical":
  //       ADAUGĂ "Revizuire urgentă necesară pentru [metric]"
  //     DACĂ cpa_wow > 30:
  //       ADAUGĂ "Analiză audiență și creative recomandate"
  //     ... etc

  console.log('[content] generateRecommendations: STUB');

  const recommendations: string[] = [];

  // KPI-uri critice
  for (const [metricName, kpi] of Object.entries(kpiResult.kpiStatus)) {
    if (kpi.status === 'critical') {
      recommendations.push(`Revizuire urgentă necesară pentru ${metricName}`);
    }
  }

  // CPA crescut
  const cpaChange = wow.cpa.changePercent ?? 0;
  if (cpaChange > 30) {
    recommendations.push('Analiză audiență și creative recomandate');
  }

  // Spend crescut fără conversii
  const spendChange = wow.spend.changePercent ?? 0;
  const convChange = wow.conversions.changePercent ?? 0;
  if (spendChange > 40 && convChange < 10) {
    recommendations.push('Verificare eficiență scalare buget');
  }

  return recommendations;
}

// ============================================================================
// SUMMARY TEXT GENERATION
// ============================================================================

/**
 * Generează summary_text pentru RAG.
 *
 * Implementează STEP 7, pas 36 din design.
 * Folosește template-ul din WEEKLY_SNAPSHOT_ENGINE.md, secțiunea 3.
 */
export function generateSummaryText(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  weekNumber: number,
  year: number,
  metrics: AggregatedMetrics,
  wow: WowResult,
  kpiResult: KpiResult,
  highlights: string[],
  concerns: string[],
  recommendations: string[],
  dataCompleteness: number,
  daysWithData: number
): string {
  // TODO: Implementare STEP 7, pas 36 din design
  // Folosește template-ul exact din WEEKLY_SNAPSHOT_ENGINE.md

  console.log('[content] generateSummaryText: STUB');

  // STUB: Template simplificat
  const lines: string[] = [
    `RAPORT SĂPTĂMÂNAL: ${client.name}`,
    `Săptămâna ${weekNumber}/${year} (${formatDate(weekStart)} - ${formatDate(weekEnd)})`,
    '',
    '═══════════════════════════════════════════════════',
    '',
    'REZUMAT PERFORMANȚĂ:',
    '',
    `Spend total: ${formatCurrency(metrics.totalSpend, client.currency)}`,
    `Impresii: ${formatNumber(metrics.totalImpressions)}`,
    `Click-uri: ${formatNumber(metrics.totalClicks)}`,
    `Conversii: ${metrics.totalConversions}`,
    `Venituri: ${formatCurrency(metrics.totalRevenue, client.currency)}`,
    '',
    'Metrici cheie:',
    `• CTR: ${metrics.avgCtr?.toFixed(2) ?? 'N/A'}%`,
    `• CPC: ${formatCurrency(metrics.avgCpc ?? 0, client.currency)}`,
    `• CPM: ${formatCurrency(metrics.avgCpm ?? 0, client.currency)}`,
    `• CPA: ${formatCurrency(metrics.avgCpa ?? 0, client.currency)}`,
    `• ROAS: ${metrics.avgRoas?.toFixed(2) ?? 'N/A'}x`,
    '',
    '═══════════════════════════════════════════════════',
    '',
    'COMPARAȚIE CU SĂPTĂMÂNA ANTERIOARĂ:',
    '',
    `• Spend: ${formatWowChange(wow.spend)}`,
    `• Conversii: ${formatWowChange(wow.conversions)}`,
    `• ROAS: ${formatWowChange(wow.roas)}`,
    `• CPA: ${formatWowChange(wow.cpa)}`,
    '',
    `Trend general: ${translateTrend(wow.trend)}`,
    '',
    '═══════════════════════════════════════════════════',
    '',
    'STATUS KPI-URI:',
    '',
  ];

  // KPI-uri
  for (const [metricName, kpi] of Object.entries(kpiResult.kpiStatus)) {
    const emoji = getStatusEmoji(kpi.status);
    lines.push(`• ${metricName}: ${emoji} ${translateStatus(kpi.status)}`);
    lines.push(`  Actual: ${kpi.actual} | Target: ${kpi.target} | Realizare: ${kpi.achievementPercent?.toFixed(0) ?? 'N/A'}%`);
  }

  if (Object.keys(kpiResult.kpiStatus).length === 0) {
    lines.push('Nu sunt definite KPI-uri pentru această perioadă.');
  }

  lines.push('');
  lines.push('═══════════════════════════════════════════════════');
  lines.push('');

  // Highlights
  if (highlights.length > 0) {
    lines.push('HIGHLIGHTS:');
    for (const h of highlights) {
      lines.push(`✓ ${h}`);
    }
    lines.push('');
  }

  // Concerns
  if (concerns.length > 0) {
    lines.push('ATENȚIONĂRI:');
    for (const c of concerns) {
      lines.push(`⚠ ${c}`);
    }
    lines.push('');
  }

  // Recommendations
  if (recommendations.length > 0) {
    lines.push('RECOMANDĂRI:');
    for (const r of recommendations) {
      lines.push(`→ ${r}`);
    }
    lines.push('');
  }

  lines.push('═══════════════════════════════════════════════════');
  lines.push('');
  lines.push(`Raport generat automat la ${new Date().toISOString()}.`);
  lines.push(`Date complete: ${(dataCompleteness * 100).toFixed(0)}% (${daysWithData}/7 zile)`);

  return lines.join('\n');
}

// ============================================================================
// SNAPSHOT JSON GENERATION
// ============================================================================

/**
 * Construiește snapshot_json complet.
 *
 * Implementează STEP 7, pas 34 din design.
 * Structura exactă din WEEKLY_SNAPSHOT_ENGINE.md, secțiunea 2.
 */
export function buildSnapshotJson(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  year: number,
  weekNumber: number,
  metrics: AggregatedMetrics,
  wow: WowResult,
  kpiResult: KpiResult,
  anomalies: Anomaly[],
  highlights: string[],
  concerns: string[],
  recommendations: string[],
  dataCompleteness: number,
  daysWithData: number,
  accountsIncluded: number,
  accountsTotal: number,
  flags: (DataFlag | KpiFlag)[]
): Record<string, unknown> {
  // TODO: Implementare STEP 7, pas 34 din design
  // Structura exactă din WEEKLY_SNAPSHOT_ENGINE.md, secțiunea 2

  console.log('[content] buildSnapshotJson: STUB');

  return {
    version: '1.0',
    generated_at: new Date().toISOString(),
    week: {
      start: weekStart.toISOString().split('T')[0],
      end: weekEnd.toISOString().split('T')[0],
      year,
      number: weekNumber,
    },
    client: {
      id: client.id,
      name: client.name,
      slug: client.slug,
    },
    data_quality: {
      completeness: dataCompleteness,
      days_with_data: daysWithData,
      expected_days: 7,
      accounts_included: accountsIncluded,
      accounts_total: accountsTotal,
      flags,
    },
    performance: {
      spend: { value: metrics.totalSpend, currency: client.currency },
      impressions: { value: metrics.totalImpressions },
      clicks: { value: metrics.totalClicks },
      conversions: { value: metrics.totalConversions },
      leads: { value: metrics.totalLeads },
      revenue: { value: metrics.totalRevenue, currency: client.currency },
    },
    calculated_metrics: {
      ctr: { value: metrics.avgCtr },
      cpc: { value: metrics.avgCpc, currency: client.currency },
      cpm: { value: metrics.avgCpm, currency: client.currency },
      cpa: { value: metrics.avgCpa, currency: client.currency },
      roas: { value: metrics.avgRoas },
    },
    week_over_week: wow,
    kpi_status: kpiResult.kpiStatus,
    anomalies,
    highlights,
    concerns,
    recommendations,
  };
}

// ============================================================================
// MAIN CONTENT GENERATION
// ============================================================================

/**
 * Generează tot conținutul pentru snapshot.
 *
 * Orchestrează STEP 7 complet.
 */
export function generateAllContent(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  year: number,
  weekNumber: number,
  metrics: AggregatedMetrics,
  wow: WowResult,
  kpiResult: KpiResult,
  anomalies: Anomaly[],
  dataCompleteness: number,
  daysWithData: number,
  accountsIncluded: number,
  accountsTotal: number,
  flags: (DataFlag | KpiFlag)[]
): GeneratedContent {
  console.log('[content] generateAllContent: STUB');

  const highlights = generateHighlights(wow, kpiResult, metrics);
  const concerns = generateConcerns(anomalies, dataCompleteness, flags);
  const recommendations = generateRecommendations(kpiResult, wow);

  const summaryText = generateSummaryText(
    client,
    weekStart,
    weekEnd,
    weekNumber,
    year,
    metrics,
    wow,
    kpiResult,
    highlights,
    concerns,
    recommendations,
    dataCompleteness,
    daysWithData
  );

  const snapshotJson = buildSnapshotJson(
    client,
    weekStart,
    weekEnd,
    year,
    weekNumber,
    metrics,
    wow,
    kpiResult,
    anomalies,
    highlights,
    concerns,
    recommendations,
    dataCompleteness,
    daysWithData,
    accountsIncluded,
    accountsTotal,
    flags
  );

  return {
    highlights,
    concerns,
    recommendations,
    summaryText,
    snapshotJson,
  };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0].split('-').reverse().join('.');
}

function formatCurrency(value: number, currency: string): string {
  return `${value.toLocaleString('ro-RO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`;
}

function formatNumber(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toString();
}

function formatWowChange(change: { changePercent: number | null; direction: string }): string {
  if (change.changePercent === null) return 'N/A';
  const arrow = change.direction === 'up' ? '↑' : change.direction === 'down' ? '↓' : '→';
  return `${arrow} ${Math.abs(change.changePercent).toFixed(1)}%`;
}

function translateTrend(trend: string): string {
  const translations: Record<string, string> = {
    improving: 'În creștere',
    declining: 'În scădere',
    stable: 'Stabil',
  };
  return translations[trend] ?? trend;
}

function translateStatus(status: string): string {
  const translations: Record<string, string> = {
    exceeded: 'DEPĂȘIT',
    on_track: 'PE DRUM BUN',
    warning: 'ATENȚIE',
    critical: 'CRITIC',
  };
  return translations[status] ?? status;
}

function getStatusEmoji(status: string): string {
  const emojis: Record<string, string> = {
    exceeded: '✅',
    on_track: '🟡',
    warning: '🟠',
    critical: '🔴',
  };
  return emojis[status] ?? '⚪';
}
