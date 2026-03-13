/**
 * Weekly Snapshot Engine - Extractor Module
 * ==========================================
 * STEP 2 din WEEKLY_SNAPSHOT_ENGINE.md: EXTRAGERE DATE
 *
 * Responsabilități:
 * - Extrage conturile active ale clientului
 * - Extrage daily_metrics pentru săptămâna curentă
 * - Extrage daily_metrics pentru săptămâna anterioară (pentru WoW)
 * - Calculează data_completeness
 * - Setează flag-uri pentru date lipsă
 */

import type {
  ClientToProcess,
  AccountInfo,
  DailyMetricRow,
  ExtractedData,
  DataFlag,
} from './types';

// ============================================================================
// ACCOUNT EXTRACTION
// ============================================================================

/**
 * Extrage conturile active ale unui client.
 *
 * Query: SELECT * FROM accounts
 *        WHERE client_id = :clientId AND status = 'active'
 */
export async function extractAccounts(clientId: string): Promise<AccountInfo[]> {
  // TODO: Implementare STEP 2, pas 7 din design
  //
  // 7. Extrage conturile active ale clientului:
  //    accounts[] = SELECT * FROM accounts
  //                 WHERE client_id = :client_id
  //                 AND status = 'active'

  console.log(`[extractor] extractAccounts(${clientId}): STUB`);

  // STUB: Returnează listă goală
  return [];
}

// ============================================================================
// METRICS EXTRACTION
// ============================================================================

/**
 * Extrage metricile zilnice pentru o perioadă.
 *
 * Query: SELECT * FROM daily_metrics
 *        WHERE account_id IN (:accountIds)
 *        AND date BETWEEN :startDate AND :endDate
 */
export async function extractDailyMetrics(
  accountIds: string[],
  startDate: Date,
  endDate: Date
): Promise<DailyMetricRow[]> {
  // TODO: Implementare STEP 2, pas 9 din design
  //
  // 9. Pentru fiecare account, extrage daily_metrics:
  //    current_week_metrics[] = SELECT * FROM daily_metrics
  //                             WHERE account_id = :account_id
  //                             AND date BETWEEN :week_start AND :week_end

  console.log(
    `[extractor] extractDailyMetrics(${accountIds.length} accounts, ${startDate.toISOString()} - ${endDate.toISOString()}): STUB`
  );

  // STUB: Returnează listă goală
  return [];
}

// ============================================================================
// DATA COMPLETENESS
// ============================================================================

/**
 * Calculează completitudinea datelor.
 *
 * @returns Numărul de zile cu date și procentul de completitudine
 */
export function calculateDataCompleteness(
  metrics: DailyMetricRow[],
  expectedDays: number
): { daysWithData: number; completeness: number } {
  // TODO: Implementare STEP 2, pași 10-11 din design
  //
  // 10. Numără zilele cu date:
  //     days_with_data = COUNT(DISTINCT date) din current_week_metrics
  //     expected_days = 7 (sau mai puțin dacă săptămâna curentă)
  //
  // 11. Calculează data_completeness:
  //     data_completeness = days_with_data / expected_days

  const uniqueDates = new Set(
    metrics.map((m) => m.date.toISOString().split('T')[0])
  );
  const daysWithData = uniqueDates.size;
  const completeness = expectedDays > 0 ? daysWithData / expectedDays : 0;

  return { daysWithData, completeness };
}

// ============================================================================
// MAIN EXTRACTION FUNCTION
// ============================================================================

/**
 * Extrage toate datele necesare pentru un client.
 * Orchestrează extragerea conturilor, metricilor și calculul completitudinii.
 */
export async function extractClientData(
  client: ClientToProcess,
  weekStart: Date,
  weekEnd: Date,
  prevWeekStart: Date,
  prevWeekEnd: Date
): Promise<ExtractedData> {
  // TODO: Implementare completă STEP 2 din design
  //
  // Pașii 7-12:
  // 7. Extrage conturile active
  // 8. Verifică dacă există conturi (flag NO_ACTIVE_ACCOUNTS)
  // 9. Extrage daily_metrics pentru săptămâna curentă
  // 10-11. Calculează data_completeness
  // 12. Extrage daily_metrics pentru săptămâna anterioară

  console.log(`[extractor] extractClientData(${client.id}): STUB`);

  const flags: DataFlag[] = [];

  // STUB: Extrage conturi
  const accounts = await extractAccounts(client.id);

  if (accounts.length === 0) {
    flags.push('NO_ACTIVE_ACCOUNTS');
  }

  const accountIds = accounts.map((a) => a.id);

  // STUB: Extrage metrici săptămâna curentă
  const currentWeekMetrics = await extractDailyMetrics(accountIds, weekStart, weekEnd);

  // Calculează completitudinea
  const expectedDays = 7; // TODO: Ajustează pentru săptămâna curentă
  const { daysWithData, completeness } = calculateDataCompleteness(
    currentWeekMetrics,
    expectedDays
  );

  if (completeness < 0.5) {
    flags.push('INSUFFICIENT_DATA');
  }

  // STUB: Extrage metrici săptămâna anterioară
  const previousWeekMetrics = await extractDailyMetrics(
    accountIds,
    prevWeekStart,
    prevWeekEnd
  );

  if (previousWeekMetrics.length === 0) {
    flags.push('NO_PREVIOUS_DATA');
  }

  return {
    clientId: client.id,
    accounts,
    currentWeekMetrics,
    previousWeekMetrics,
    daysWithData,
    expectedDays,
    dataCompleteness: completeness,
    flags,
  };
}
