/**
 * Weekly Snapshot Engine - Audit Module
 * =======================================
 * STEP 10 din WEEKLY_SNAPSHOT_ENGINE.md: AUDIT LOG
 *
 * Responsabilități:
 * - Loghează evenimente în audit_log
 * - Format consistent pentru toate evenimentele
 * - Suport pentru batch și per-client events
 */

import type { AuditEvent, AuditLogEntry, ClientProcessingResult } from './types';

// ============================================================================
// AUDIT EVENT BUILDERS
// ============================================================================

/**
 * Loghează începutul unui batch.
 *
 * Event: START_BATCH
 */
export async function logBatchStart(
  batchId: string,
  weekStart: Date,
  clientsCount: number,
  triggeredBy: 'cron' | 'manual',
  forceRegenerate: boolean
): Promise<void> {
  // TODO: Implementare din secțiunea 6 a design-ului
  //
  // INSERT INTO audit_log (table_name, record_id, action, new_values)
  // VALUES ('system', :batchId, 'INSERT', {...})

  console.log(`[audit] START_BATCH: ${batchId}`);

  const entry: AuditLogEntry = {
    tableName: 'system',
    recordId: batchId,
    action: 'INSERT',
    clientId: null,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'START_BATCH',
      week_start: weekStart.toISOString().split('T')[0],
      clients_to_process: clientsCount,
      triggered_by: triggeredBy,
      force_regenerate: forceRegenerate,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează începutul procesării unui client.
 *
 * Event: CLIENT_START
 */
export async function logClientStart(
  clientId: string,
  weekStart: Date
): Promise<void> {
  console.log(`[audit] CLIENT_START: ${clientId}`);

  const entry: AuditLogEntry = {
    tableName: 'weekly_snapshots',
    recordId: null,
    action: 'INSERT',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'CLIENT_START',
      week_start: weekStart.toISOString().split('T')[0],
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează crearea unui snapshot.
 *
 * Event: SNAPSHOT_CREATED
 */
export async function logSnapshotCreated(
  snapshotId: string,
  clientId: string,
  weekNumber: number,
  year: number,
  dataCompleteness: number,
  kpiCount: number,
  anomaliesCount: number,
  flags: string[],
  durationMs: number
): Promise<void> {
  console.log(`[audit] SNAPSHOT_CREATED: ${snapshotId}`);

  const entry: AuditLogEntry = {
    tableName: 'weekly_snapshots',
    recordId: snapshotId,
    action: 'INSERT',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'SNAPSHOT_CREATED',
      week: `${year}-W${String(weekNumber).padStart(2, '0')}`,
      data_completeness: dataCompleteness,
      kpi_count: kpiCount,
      anomalies_count: anomaliesCount,
      flags,
      duration_ms: durationMs,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează actualizarea unui snapshot.
 *
 * Event: SNAPSHOT_UPDATED
 */
export async function logSnapshotUpdated(
  snapshotId: string,
  clientId: string,
  changes: string[],
  reason: string
): Promise<void> {
  console.log(`[audit] SNAPSHOT_UPDATED: ${snapshotId}`);

  const entry: AuditLogEntry = {
    tableName: 'weekly_snapshots',
    recordId: snapshotId,
    action: 'UPDATE',
    clientId,
    userId: null,
    oldValues: { status: 'existing' },
    newValues: {
      event: 'SNAPSHOT_UPDATED',
      changes,
      reason,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează un snapshot sărit.
 *
 * Event: SNAPSHOT_SKIPPED
 */
export async function logSnapshotSkipped(
  clientId: string,
  weekStart: Date,
  reason: string,
  details: Record<string, unknown>
): Promise<void> {
  console.log(`[audit] SNAPSHOT_SKIPPED: ${clientId} - ${reason}`);

  const entry: AuditLogEntry = {
    tableName: 'weekly_snapshots',
    recordId: null,
    action: 'INSERT',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'SNAPSHOT_SKIPPED',
      week: weekStart.toISOString().split('T')[0],
      reason,
      details,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează o eroare la procesare.
 *
 * Event: SNAPSHOT_FAILED
 */
export async function logSnapshotFailed(
  clientId: string,
  weekStart: Date,
  error: string,
  stepFailed: string
): Promise<void> {
  console.error(`[audit] SNAPSHOT_FAILED: ${clientId} at ${stepFailed} - ${error}`);

  const entry: AuditLogEntry = {
    tableName: 'weekly_snapshots',
    recordId: null,
    action: 'INSERT',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'SNAPSHOT_FAILED',
      week: weekStart.toISOString().split('T')[0],
      error,
      step_failed: stepFailed,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează crearea unui document RAG.
 *
 * Event: RAG_CREATED
 */
export async function logRagCreated(
  ragId: string,
  snapshotId: string,
  clientId: string
): Promise<void> {
  console.log(`[audit] RAG_CREATED: ${ragId}`);

  const entry: AuditLogEntry = {
    tableName: 'rag_documents',
    recordId: ragId,
    action: 'INSERT',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'RAG_CREATED',
      snapshot_id: snapshotId,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează actualizarea unui document RAG.
 *
 * Event: RAG_UPDATED
 */
export async function logRagUpdated(
  ragId: string,
  clientId: string,
  contentChanged: boolean
): Promise<void> {
  console.log(`[audit] RAG_UPDATED: ${ragId}`);

  const entry: AuditLogEntry = {
    tableName: 'rag_documents',
    recordId: ragId,
    action: 'UPDATE',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'RAG_UPDATED',
      content_changed: contentChanged,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează detectarea unei anomalii.
 *
 * Event: ANOMALY_DETECTED
 */
export async function logAnomalyDetected(
  snapshotId: string,
  clientId: string,
  anomalyType: string,
  severity: string,
  metric: string | undefined,
  currentValue: number,
  previousValue: number | null,
  changePercent: number | null,
  thresholdExceeded: number
): Promise<void> {
  console.log(`[audit] ANOMALY_DETECTED: ${anomalyType} for ${clientId}`);

  const entry: AuditLogEntry = {
    tableName: 'weekly_snapshots',
    recordId: snapshotId,
    action: 'INSERT',
    clientId,
    userId: null,
    oldValues: null,
    newValues: {
      event: 'ANOMALY_DETECTED',
      anomaly_type: anomalyType,
      severity,
      metric,
      current_value: currentValue,
      previous_value: previousValue,
      change_percent: changePercent,
      threshold_exceeded: thresholdExceeded,
    },
  };

  await writeAuditLog(entry);
}

/**
 * Loghează finalizarea batch-ului.
 *
 * Event: BATCH_COMPLETE
 */
export async function logBatchComplete(
  batchId: string,
  results: ClientProcessingResult[],
  totalDurationMs: number
): Promise<void> {
  const successCount = results.filter((r) => r.status === 'success').length;
  const partialCount = results.filter((r) => r.status === 'partial').length;
  const failedCount = results.filter((r) => r.status === 'failed').length;
  const skippedCount = results.filter((r) => r.status === 'skipped').length;

  console.log(
    `[audit] BATCH_COMPLETE: ${successCount} success, ${partialCount} partial, ${failedCount} failed, ${skippedCount} skipped`
  );

  const entry: AuditLogEntry = {
    tableName: 'system',
    recordId: batchId,
    action: 'UPDATE',
    clientId: null,
    userId: null,
    oldValues: { status: 'running' },
    newValues: {
      event: 'BATCH_COMPLETE',
      status: 'completed',
      success_count: successCount,
      partial_count: partialCount,
      failed_count: failedCount,
      skipped_count: skippedCount,
      total_duration_ms: totalDurationMs,
      avg_per_client_ms:
        results.length > 0 ? Math.round(totalDurationMs / results.length) : 0,
    },
  };

  await writeAuditLog(entry);
}

// ============================================================================
// AUDIT LOG WRITER
// ============================================================================

/**
 * Scrie o intrare în audit_log.
 *
 * Query: INSERT INTO audit_log (table_name, record_id, action, client_id, user_id, old_values, new_values)
 *        VALUES (:tableName, :recordId, :action, :clientId, :userId, :oldValues, :newValues)
 */
async function writeAuditLog(entry: AuditLogEntry): Promise<void> {
  // TODO: Implementare reală cu query PostgreSQL
  //
  // În implementarea reală:
  // await db.query(
  //   `INSERT INTO audit_log (table_name, record_id, action, client_id, user_id, old_values, new_values)
  //    VALUES ($1, $2, $3, $4, $5, $6, $7)`,
  //   [entry.tableName, entry.recordId, entry.action, entry.clientId, entry.userId,
  //    JSON.stringify(entry.oldValues), JSON.stringify(entry.newValues)]
  // );

  // STUB: Log în consolă
  console.log('[audit] writeAuditLog:', JSON.stringify(entry.newValues));
}

// ============================================================================
// BATCH ID GENERATOR
// ============================================================================

/**
 * Generează un ID unic pentru batch.
 */
export function generateBatchId(weekStart: Date): string {
  const dateStr = weekStart.toISOString().split('T')[0].replace(/-/g, '');
  const timeStr = new Date()
    .toISOString()
    .split('T')[1]
    .split('.')[0]
    .replace(/:/g, '');
  return `batch_${dateStr}_${timeStr}`;
}
