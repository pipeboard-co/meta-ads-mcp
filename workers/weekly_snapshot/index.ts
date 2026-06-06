#!/usr/bin/env node
/**
 * Weekly Snapshot Engine - Main Entry Point
 * ===========================================
 *
 * CLI pentru generarea snapshot-urilor săptămânale.
 *
 * Exemplu de rulare:
 *   npx ts-node workers/weekly_snapshot/index.ts --week-start=2024-01-08
 *   npx ts-node workers/weekly_snapshot/index.ts --week-start=2024-01-08 --client-id=UUID --force
 *
 * Argumente:
 *   --week-start=YYYY-MM-DD  (obligatoriu) Data de Luni a săptămânii țintă
 *   --client-id=UUID         (opțional) Procesează doar acest client
 *   --force                  (flag) Regenerează snapshot-uri existente
 *
 * Output (JSON):
 *   {
 *     "week_start": "YYYY-MM-DD",
 *     "week_end": "YYYY-MM-DD",
 *     "processed": number,
 *     "success": number,
 *     "partial": number,
 *     "failed": number,
 *     "skipped": number,
 *     "duration_ms": number
 *   }
 */

import type {
  WorkerParams,
  WorkerOutput,
  ClientToProcess,
  ClientProcessingResult,
  ExtractedData,
  AggregatedMetrics,
  WowResult,
  KpiResult,
  Anomaly,
  GeneratedContent,
  DataFlag,
  KpiFlag,
} from './types';

// ============================================================================
// MODULE IMPORTS
// ============================================================================

import {
  validateParams,
  discoverClients,
  calculateWeekEnd,
  calculatePreviousWeek,
  getIsoWeekInfo,
  ValidationError,
} from './validator';

import { extractClientData } from './extractor';
import { aggregateMetrics, emptyAggregation } from './aggregator';
import { calculateAllWowChanges, emptyWowResult } from './wow';
import { calculateKpiStatus, emptyKpiResult } from './kpi_engine';
import { detectAllAnomalies } from './anomalies';
import { generateAllContent } from './content';
import { persistSnapshot } from './persistence';
import { propagateToRag, buildRagTitle, buildRagTags } from './rag';
import {
  generateBatchId,
  logBatchStart,
  logClientStart,
  logSnapshotCreated,
  logSnapshotUpdated,
  logSnapshotSkipped,
  logSnapshotFailed,
  logRagCreated,
  logRagUpdated,
  logBatchComplete,
} from './audit';

// ============================================================================
// CLI ARGUMENT PARSING
// ============================================================================

function parseArguments(): WorkerParams {
  const args = process.argv.slice(2);

  let weekStart: Date | null = null;
  let clientId: string | null = null;
  let forceRegenerate = false;

  for (const arg of args) {
    if (arg.startsWith('--week-start=')) {
      const dateStr = arg.split('=')[1];
      weekStart = new Date(dateStr);
      if (isNaN(weekStart.getTime())) {
        console.error(`Error: Invalid date format for --week-start: ${dateStr}`);
        console.error('Expected format: YYYY-MM-DD');
        process.exit(1);
      }
    } else if (arg.startsWith('--client-id=')) {
      clientId = arg.split('=')[1];
    } else if (arg === '--force') {
      forceRegenerate = true;
    } else if (arg === '--help' || arg === '-h') {
      printUsage();
      process.exit(0);
    } else {
      console.error(`Error: Unknown argument: ${arg}`);
      printUsage();
      process.exit(1);
    }
  }

  if (!weekStart) {
    console.error('Error: --week-start is required');
    printUsage();
    process.exit(1);
  }

  return {
    weekStart,
    clientId,
    forceRegenerate,
  };
}

function printUsage(): void {
  console.log(`
Usage: npx ts-node workers/weekly_snapshot/index.ts [options]

Options:
  --week-start=YYYY-MM-DD  (required) Monday of the target week
  --client-id=UUID         (optional) Process only this client
  --force                  (optional) Regenerate existing snapshots
  --help, -h               Show this help message

Examples:
  npx ts-node workers/weekly_snapshot/index.ts --week-start=2024-01-08
  npx ts-node workers/weekly_snapshot/index.ts --week-start=2024-01-08 --client-id=550e8400-e29b-41d4-a716-446655440000
  npx ts-node workers/weekly_snapshot/index.ts --week-start=2024-01-08 --force
`);
}

// ============================================================================
// SINGLE CLIENT PROCESSING
// ============================================================================

/**
 * Procesează un singur client.
 *
 * Execută STEP 2-9 din design pentru un client.
 */
async function processClient(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  prevWeekStart: Date,
  prevWeekEnd: Date,
  year: number,
  weekNumber: number
): Promise<ClientProcessingResult> {
  const startTime = Date.now();
  const allFlags: (DataFlag | KpiFlag)[] = [];

  try {
    // ══════════════════════════════════════════════════════════════════════
    // STEP 2: EXTRAGERE DATE
    // Vezi: extractor.ts
    // Pași 7-12 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 2: Extracting data...`);
    const extractedData = await extractClientData(
      client,
      weekStart,
      weekEnd,
      prevWeekStart,
      prevWeekEnd
    );
    allFlags.push(...extractedData.flags);

    // Verifică dacă avem date suficiente
    if (extractedData.flags.includes('INSUFFICIENT_DATA') && extractedData.daysWithData === 0) {
      await logSnapshotSkipped(client.id, weekStart, 'NO_DATA', {
        accounts_checked: extractedData.accounts.length,
        days_with_data: extractedData.daysWithData,
      });
      return {
        clientId: client.id,
        clientName: client.name,
        status: 'skipped',
        snapshotId: null,
        ragDocumentId: null,
        flags: allFlags,
        anomaliesCount: 0,
        durationMs: Date.now() - startTime,
        error: 'No data available for this week',
      };
    }

    // ══════════════════════════════════════════════════════════════════════
    // STEP 3: AGREGARE METRICI
    // Vezi: aggregator.ts
    // Pași 13-16 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 3: Aggregating metrics...`);
    const currentMetrics = aggregateMetrics(extractedData.currentWeekMetrics);
    const previousMetrics = extractedData.previousWeekMetrics.length > 0
      ? aggregateMetrics(extractedData.previousWeekMetrics)
      : emptyAggregation();

    // ══════════════════════════════════════════════════════════════════════
    // STEP 4: CALCUL WoW
    // Vezi: wow.ts
    // Pași 17-19 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 4: Calculating WoW...`);
    const wowResult = extractedData.flags.includes('NO_PREVIOUS_DATA')
      ? emptyWowResult()
      : calculateAllWowChanges(currentMetrics, previousMetrics);

    // ══════════════════════════════════════════════════════════════════════
    // STEP 5: CALCUL KPI STATUS
    // Vezi: kpi_engine.ts
    // Pași 20-22 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 5: Calculating KPI status...`);
    const kpiResult = await calculateKpiStatus(
      client.id,
      weekStart,
      weekEnd,
      currentMetrics
    );
    allFlags.push(...kpiResult.flags);

    // ══════════════════════════════════════════════════════════════════════
    // STEP 6: DETECTARE ANOMALII
    // Vezi: anomalies.ts
    // Pași 23-28 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 6: Detecting anomalies...`);
    const anomalies = detectAllAnomalies(
      wowResult,
      kpiResult,
      extractedData.dataCompleteness,
      extractedData.daysWithData,
      currentMetrics.totalSpend,
      currentMetrics.totalConversions
    );

    // ══════════════════════════════════════════════════════════════════════
    // STEP 7: GENERARE CONTENT
    // Vezi: content.ts
    // Pași 29-37 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 7: Generating content...`);
    const content = generateAllContent(
      client,
      weekStart,
      weekEnd,
      year,
      weekNumber,
      currentMetrics,
      wowResult,
      kpiResult,
      anomalies,
      extractedData.dataCompleteness,
      extractedData.daysWithData,
      extractedData.accounts.length,
      extractedData.accounts.length, // TODO: Get total accounts
      allFlags
    );

    // ══════════════════════════════════════════════════════════════════════
    // STEP 8: PERSISTARE
    // Vezi: persistence.ts
    // Pași 38-42 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 8: Persisting snapshot...`);
    const persistResult = await persistSnapshot(
      client,
      weekStart,
      weekEnd,
      year,
      weekNumber,
      currentMetrics,
      wowResult,
      kpiResult,
      content
    );

    if (!persistResult.success) {
      await logSnapshotFailed(client.id, weekStart, persistResult.error ?? 'Unknown', 'PERSISTENCE');
      return {
        clientId: client.id,
        clientName: client.name,
        status: 'failed',
        snapshotId: null,
        ragDocumentId: null,
        flags: allFlags,
        anomaliesCount: anomalies.length,
        durationMs: Date.now() - startTime,
        error: persistResult.error,
      };
    }

    // Log snapshot created/updated
    if (persistResult.action === 'INSERT') {
      await logSnapshotCreated(
        persistResult.snapshotId!,
        client.id,
        weekNumber,
        year,
        extractedData.dataCompleteness,
        Object.keys(kpiResult.kpiStatus).length,
        anomalies.length,
        allFlags.map(String),
        Date.now() - startTime
      );
    } else {
      await logSnapshotUpdated(
        persistResult.snapshotId!,
        client.id,
        ['full_regeneration'],
        'force_regenerate'
      );
    }

    // ══════════════════════════════════════════════════════════════════════
    // STEP 9: PROPAGARE RAG
    // Vezi: rag.ts
    // Pași 43-44 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log(`[${client.slug}] STEP 9: Propagating to RAG...`);
    const ragResult = await propagateToRag({
      snapshotId: persistResult.snapshotId!,
      clientId: client.id,
      clientName: client.name,
      weekStart,
      weekEnd,
      year,
      weekNumber,
      summaryText: content.summaryText,
    });

    if (ragResult.success && ragResult.ragDocumentId) {
      if (ragResult.action === 'INSERT') {
        await logRagCreated(ragResult.ragDocumentId, persistResult.snapshotId!, client.id);
      } else if (ragResult.action === 'UPDATE') {
        await logRagUpdated(ragResult.ragDocumentId, client.id, true);
      }
    }

    // ══════════════════════════════════════════════════════════════════════
    // RESULT
    // ══════════════════════════════════════════════════════════════════════
    const status = allFlags.length > 0 ? 'partial' : 'success';

    return {
      clientId: client.id,
      clientName: client.name,
      status,
      snapshotId: persistResult.snapshotId,
      ragDocumentId: ragResult.ragDocumentId,
      flags: allFlags,
      anomaliesCount: anomalies.length,
      durationMs: Date.now() - startTime,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    await logSnapshotFailed(client.id, weekStart, errorMessage, 'PROCESSING');

    return {
      clientId: client.id,
      clientName: client.name,
      status: 'failed',
      snapshotId: null,
      ragDocumentId: null,
      flags: allFlags,
      anomaliesCount: 0,
      durationMs: Date.now() - startTime,
      error: errorMessage,
    };
  }
}

// ============================================================================
// MAIN ORCHESTRATOR
// ============================================================================

/**
 * Funcția principală care orchestrează întregul proces.
 *
 * Execută STEP 1-10 din WEEKLY_SNAPSHOT_ENGINE.md
 */
async function main(): Promise<void> {
  const startTime = Date.now();

  // ════════════════════════════════════════════════════════════════════════
  // PARSE ARGUMENTS
  // ════════════════════════════════════════════════════════════════════════
  console.log('Weekly Snapshot Engine - Starting...\n');

  const params = parseArguments();
  console.log(`Parameters:`);
  console.log(`  week-start: ${params.weekStart.toISOString().split('T')[0]}`);
  console.log(`  client-id: ${params.clientId ?? '(all active clients)'}`);
  console.log(`  force: ${params.forceRegenerate}`);
  console.log('');

  try {
    // ══════════════════════════════════════════════════════════════════════
    // STEP 1: VALIDARE
    // Vezi: validator.ts
    // Pași 1-6 din WEEKLY_SNAPSHOT_ENGINE.md
    // ══════════════════════════════════════════════════════════════════════
    console.log('STEP 1: Validating parameters...');
    await validateParams(params);

    const weekEnd = calculateWeekEnd(params.weekStart);
    const { start: prevWeekStart, end: prevWeekEnd } = calculatePreviousWeek(params.weekStart);
    const { year, weekNumber } = getIsoWeekInfo(params.weekStart);

    console.log(`  Week: ${year}-W${String(weekNumber).padStart(2, '0')}`);
    console.log(`  Period: ${params.weekStart.toISOString().split('T')[0]} - ${weekEnd.toISOString().split('T')[0]}`);
    console.log(`  Previous: ${prevWeekStart.toISOString().split('T')[0]} - ${prevWeekEnd.toISOString().split('T')[0]}`);
    console.log('');

    // Discover clients
    console.log('STEP 1: Discovering clients...');
    const clients = await discoverClients(params);
    console.log(`  Found ${clients.length} clients to process`);
    console.log('');

    if (clients.length === 0) {
      const output: WorkerOutput = {
        weekStart: params.weekStart.toISOString().split('T')[0],
        weekEnd: weekEnd.toISOString().split('T')[0],
        processed: 0,
        success: 0,
        partial: 0,
        failed: 0,
        skipped: 0,
        durationMs: Date.now() - startTime,
      };

      console.log('\nOutput:');
      console.log(JSON.stringify(output, null, 2));
      return;
    }

    // ══════════════════════════════════════════════════════════════════════
    // BATCH START AUDIT
    // ══════════════════════════════════════════════════════════════════════
    const batchId = generateBatchId(params.weekStart);
    await logBatchStart(
      batchId,
      params.weekStart,
      clients.length,
      'manual', // TODO: Detect if cron or manual
      params.forceRegenerate
    );

    // ══════════════════════════════════════════════════════════════════════
    // STEP 2-9: PROCESS EACH CLIENT
    // ══════════════════════════════════════════════════════════════════════
    const results: ClientProcessingResult[] = [];

    for (const client of clients) {
      console.log(`\n${'═'.repeat(60)}`);
      console.log(`Processing: ${client.name} (${client.slug})`);
      console.log(`Action: ${client.action}`);
      console.log(`${'═'.repeat(60)}`);

      if (client.action === 'SKIP') {
        console.log('Skipping (already exists, use --force to regenerate)');
        results.push({
          clientId: client.id,
          clientName: client.name,
          status: 'skipped',
          snapshotId: client.existingSnapshotId ?? null,
          ragDocumentId: null,
          flags: [],
          anomaliesCount: 0,
          durationMs: 0,
        });
        continue;
      }

      await logClientStart(client.id, params.weekStart);

      const result = await processClient(
        client,
        params.weekStart,
        weekEnd,
        prevWeekStart,
        prevWeekEnd,
        year,
        weekNumber
      );

      results.push(result);

      console.log(`\nResult: ${result.status.toUpperCase()}`);
      if (result.flags.length > 0) {
        console.log(`Flags: ${result.flags.join(', ')}`);
      }
      if (result.anomaliesCount > 0) {
        console.log(`Anomalies: ${result.anomaliesCount}`);
      }
      console.log(`Duration: ${result.durationMs}ms`);
    }

    // ══════════════════════════════════════════════════════════════════════
    // STEP 10: RAPORT FINAL
    // Pas din WEEKLY_SNAPSHOT_ENGINE.md: secțiunea 4, Step 10
    // ══════════════════════════════════════════════════════════════════════
    const totalDuration = Date.now() - startTime;
    await logBatchComplete(batchId, results, totalDuration);

    // ══════════════════════════════════════════════════════════════════════
    // OUTPUT
    // ══════════════════════════════════════════════════════════════════════
    const output: WorkerOutput = {
      weekStart: params.weekStart.toISOString().split('T')[0],
      weekEnd: weekEnd.toISOString().split('T')[0],
      processed: results.length,
      success: results.filter((r) => r.status === 'success').length,
      partial: results.filter((r) => r.status === 'partial').length,
      failed: results.filter((r) => r.status === 'failed').length,
      skipped: results.filter((r) => r.status === 'skipped').length,
      durationMs: totalDuration,
    };

    console.log('\n' + '═'.repeat(60));
    console.log('BATCH COMPLETE');
    console.log('═'.repeat(60));
    console.log('\nOutput:');
    console.log(JSON.stringify(output, null, 2));
  } catch (error) {
    if (error instanceof ValidationError) {
      console.error(`\nValidation Error: ${error.message}`);
      console.error(`Code: ${error.code}`);
      process.exit(1);
    }

    console.error('\nFatal Error:', error);
    process.exit(1);
  }
}

// ============================================================================
// ENTRY POINT
// ============================================================================

main().catch((error) => {
  console.error('Unhandled error:', error);
  process.exit(1);
});
