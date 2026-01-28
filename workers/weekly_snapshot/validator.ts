/**
 * Weekly Snapshot Engine - Validator Module
 * ==========================================
 * STEP 1 din WEEKLY_SNAPSHOT_ENGINE.md: VALIDARE
 *
 * Responsabilități:
 * - Validează target_week_start (trebuie să fie Luni)
 * - Validează că săptămâna este în trecut sau curentă
 * - Validează client_id dacă este furnizat
 * - Extrage lista de clienți de procesat
 * - Verifică existența snapshot-urilor (skip/update/insert)
 */

import type { WorkerParams, ClientToProcess } from './types';

// ============================================================================
// VALIDATION ERRORS
// ============================================================================

export class ValidationError extends Error {
  constructor(
    message: string,
    public code: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

// ============================================================================
// PARAMETER VALIDATION
// ============================================================================

/**
 * Validează parametrii de intrare ai workerului.
 *
 * @throws ValidationError dacă parametrii sunt invalizi
 */
export async function validateParams(params: WorkerParams): Promise<void> {
  // TODO: Implementare STEP 1, pași 1-4 din design
  //
  // 1. Verifică că weekStart este o dată validă
  // 2. Verifică că weekStart este Luni (day_of_week = 1)
  // 3. Verifică că weekStart nu este în viitor
  // 4. Dacă clientId este furnizat, verifică format UUID valid

  const dayOfWeek = params.weekStart.getDay();
  // În JavaScript: 0 = Duminică, 1 = Luni
  if (dayOfWeek !== 1) {
    throw new ValidationError(
      `week-start must be a Monday. Got: ${params.weekStart.toISOString()} (day ${dayOfWeek})`,
      'INVALID_WEEK_START'
    );
  }

  const today = new Date();
  today.setHours(23, 59, 59, 999);
  if (params.weekStart > today) {
    throw new ValidationError(
      `week-start cannot be in the future`,
      'FUTURE_WEEK_START'
    );
  }

  if (params.clientId !== null) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(params.clientId)) {
      throw new ValidationError(
        `Invalid client-id format: ${params.clientId}`,
        'INVALID_CLIENT_ID'
      );
    }
  }
}

// ============================================================================
// CLIENT DISCOVERY
// ============================================================================

/**
 * Extrage lista de clienți de procesat.
 * Verifică și existența snapshot-urilor pentru a determina INSERT/UPDATE/SKIP.
 *
 * @returns Lista de clienți cu acțiunea asociată
 */
export async function discoverClients(
  params: WorkerParams
): Promise<ClientToProcess[]> {
  // TODO: Implementare STEP 1, pași 5-6 din design
  //
  // 5. DACĂ clientId specificat → [clientId]
  //    ALTFEL → SELECT id FROM clients WHERE status = 'active'
  //
  // 6. Pentru fiecare client, verifică dacă snapshot există:
  //    - DACĂ există ȘI force_regenerate = FALSE → SKIP
  //    - DACĂ există ȘI force_regenerate = TRUE → UPDATE
  //    - DACĂ nu există → INSERT
  //
  // Query-uri necesare:
  // - SELECT * FROM clients WHERE status = 'active'
  // - SELECT id FROM weekly_snapshots WHERE client_id = ? AND week_start = ?

  console.log('[validator] discoverClients: STUB - returning empty list');

  // STUB: Returnează listă goală
  // În implementarea reală, va face query la DB
  return [];
}

// ============================================================================
// WEEK CALCULATIONS
// ============================================================================

/**
 * Calculează week_end din week_start.
 */
export function calculateWeekEnd(weekStart: Date): Date {
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 6);
  return weekEnd;
}

/**
 * Calculează săptămâna anterioară.
 */
export function calculatePreviousWeek(weekStart: Date): { start: Date; end: Date } {
  const prevStart = new Date(weekStart);
  prevStart.setDate(prevStart.getDate() - 7);

  const prevEnd = new Date(weekStart);
  prevEnd.setDate(prevEnd.getDate() - 1);

  return { start: prevStart, end: prevEnd };
}

/**
 * Extrage anul ISO și numărul săptămânii.
 */
export function getIsoWeekInfo(date: Date): { year: number; weekNumber: number } {
  // TODO: Implementare corectă ISO 8601 week number
  // Pentru moment, aproximare simplă

  const startOfYear = new Date(date.getFullYear(), 0, 1);
  const days = Math.floor((date.getTime() - startOfYear.getTime()) / (24 * 60 * 60 * 1000));
  const weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);

  return {
    year: date.getFullYear(),
    weekNumber,
  };
}
