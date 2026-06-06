/**
 * Weekly Snapshot Engine - Persistence Module
 * =============================================
 * STEP 8 din WEEKLY_SNAPSHOT_ENGINE.md: PERSISTARE
 *
 * Responsabilități:
 * - INSERT sau UPDATE în weekly_snapshots
 * - Retry logic (3x cu backoff)
 * - Returnează rezultatul operației
 */

import type {
  SnapshotRecord,
  PersistenceResult,
  ClientToProcess,
  AggregatedMetrics,
  WowResult,
  KpiResult,
  GeneratedContent,
} from './types';

// ============================================================================
// RETRY CONFIGURATION
// ============================================================================

const RETRY_CONFIG = {
  maxRetries: 3,
  backoffMs: [1000, 2000, 4000], // 1s, 2s, 4s
};

// ============================================================================
// RECORD BUILDING
// ============================================================================

/**
 * Construiește record-ul pentru weekly_snapshots.
 *
 * Implementează STEP 8, pas 39 din design.
 */
export function buildSnapshotRecord(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  year: number,
  weekNumber: number,
  metrics: AggregatedMetrics,
  wow: WowResult,
  kpiResult: KpiResult,
  content: GeneratedContent,
  existingId?: string
): SnapshotRecord {
  // TODO: Implementare STEP 8, pas 39 din design
  //
  // 39. Construiește record-ul weekly_snapshots:
  //     - id: UUID nou (INSERT) sau existent (UPDATE)
  //     - toate câmpurile din tabelul weekly_snapshots

  console.log('[persistence] buildSnapshotRecord: STUB');

  return {
    id: existingId ?? generateUUID(),
    clientId: client.id,
    accountId: null, // Agregat la nivel client
    weekStart,
    weekEnd,
    year,
    weekNumber,
    totalSpend: metrics.totalSpend,
    totalImpressions: metrics.totalImpressions,
    totalClicks: metrics.totalClicks,
    totalConversions: metrics.totalConversions,
    totalLeads: metrics.totalLeads,
    totalRevenue: metrics.totalRevenue,
    avgCtr: metrics.avgCtr,
    avgCpc: metrics.avgCpc,
    avgCpm: metrics.avgCpm,
    avgCpa: metrics.avgCpa,
    avgRoas: metrics.avgRoas,
    spendWowChange: wow.spend.changePercent,
    convWowChange: wow.conversions.changePercent,
    roasWowChange: wow.roas.changePercent,
    kpiSpendStatus: kpiResult.kpiStatus['spend']?.status ?? null,
    kpiConvStatus: kpiResult.kpiStatus['conversions']?.status ?? null,
    kpiRoasStatus: kpiResult.kpiStatus['roas']?.status ?? null,
    summaryText: content.summaryText,
    highlights: content.highlights,
    concerns: content.concerns,
    recommendations: content.recommendations,
    snapshotJson: content.snapshotJson,
    generatedAt: new Date(),
  };
}

// ============================================================================
// INSERT OPERATION
// ============================================================================

/**
 * Inserează un nou snapshot în baza de date.
 */
async function insertSnapshot(record: SnapshotRecord): Promise<PersistenceResult> {
  // TODO: Implementare STEP 8, pas 40 (INSERT) din design
  //
  // Query: INSERT INTO weekly_snapshots (...) VALUES (...)

  console.log(`[persistence] insertSnapshot(${record.id}): STUB`);

  // STUB: Simulează succes
  return {
    success: true,
    snapshotId: record.id,
    action: 'INSERT',
  };
}

// ============================================================================
// UPDATE OPERATION
// ============================================================================

/**
 * Actualizează un snapshot existent.
 */
async function updateSnapshot(record: SnapshotRecord): Promise<PersistenceResult> {
  // TODO: Implementare STEP 8, pas 40 (UPDATE) din design
  //
  // Query: UPDATE weekly_snapshots SET ... WHERE id = :id

  console.log(`[persistence] updateSnapshot(${record.id}): STUB`);

  // STUB: Simulează succes
  return {
    success: true,
    snapshotId: record.id,
    action: 'UPDATE',
  };
}

// ============================================================================
// RETRY LOGIC
// ============================================================================

/**
 * Execută operația cu retry logic.
 *
 * Implementează regulile de eroare din design (5.5):
 * - INSERT/UPDATE fail → RETRY 3x cu backoff (1s, 2s, 4s)
 * - După 3 fails: FAILED
 */
async function executeWithRetry(
  operation: () => Promise<PersistenceResult>,
  operationName: string
): Promise<PersistenceResult> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= RETRY_CONFIG.maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      console.error(
        `[persistence] ${operationName} attempt ${attempt + 1} failed:`,
        lastError.message
      );

      if (attempt < RETRY_CONFIG.maxRetries) {
        const backoffMs = RETRY_CONFIG.backoffMs[attempt] ?? 4000;
        console.log(`[persistence] Retrying in ${backoffMs}ms...`);
        await sleep(backoffMs);
      }
    }
  }

  return {
    success: false,
    snapshotId: null,
    action: 'INSERT', // or UPDATE
    error: lastError?.message ?? 'Unknown error after retries',
  };
}

// ============================================================================
// MAIN PERSISTENCE FUNCTION
// ============================================================================

/**
 * Persistă snapshot-ul în baza de date.
 *
 * Orchestrează STEP 8, pași 38-42 din design.
 */
export async function persistSnapshot(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  year: number,
  weekNumber: number,
  metrics: AggregatedMetrics,
  wow: WowResult,
  kpiResult: KpiResult,
  content: GeneratedContent
): Promise<PersistenceResult> {
  // TODO: Implementare STEP 8 complet din design
  //
  // 38. Determină tipul operației (INSERT/UPDATE)
  // 39. Construiește record
  // 40. Execută INSERT sau UPDATE
  // 41-42. Handle success/failure

  console.log(`[persistence] persistSnapshot(${client.id}): STUB`);

  // Pas 38: Determină tipul operației
  const isUpdate = client.action === 'UPDATE';
  const existingId = client.existingSnapshotId;

  // Pas 39: Construiește record
  const record = buildSnapshotRecord(
    client,
    weekStart,
    weekEnd,
    year,
    weekNumber,
    metrics,
    wow,
    kpiResult,
    content,
    isUpdate ? existingId : undefined
  );

  // Pas 40: Execută cu retry
  if (isUpdate) {
    return executeWithRetry(
      () => updateSnapshot(record),
      `updateSnapshot(${record.id})`
    );
  } else {
    return executeWithRetry(
      () => insertSnapshot(record),
      `insertSnapshot(${record.id})`
    );
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function generateUUID(): string {
  // Simple UUID v4 generator (în producție, folosește crypto.randomUUID())
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
