/**
 * Weekly Snapshot Engine - RAG Propagation Module
 * =================================================
 * STEP 9 din WEEKLY_SNAPSHOT_ENGINE.md: PROPAGARE RAG
 *
 * Responsabilități:
 * - Creează/actualizează rag_document
 * - Calculează content_hash pentru deduplicare
 * - Marchează embedding = NULL pentru regenerare
 * - Setează tags pentru filtrare
 */

import type { RagDocumentInput, RagResult } from './types';
import { createHash } from 'crypto';

// ============================================================================
// CONTENT HASH
// ============================================================================

/**
 * Calculează SHA-256 hash pentru content.
 *
 * Implementează STEP 9, pas 43a din design.
 */
export function calculateContentHash(content: string): string {
  return createHash('sha256').update(content).digest('hex');
}

// ============================================================================
// RAG DOCUMENT CHECK
// ============================================================================

/**
 * Verifică dacă documentul RAG există deja.
 *
 * Query: SELECT id, content_hash FROM rag_documents
 *        WHERE source_type = 'weekly_snapshot' AND source_id = :snapshotId
 */
async function findExistingRagDocument(
  snapshotId: string
): Promise<{ id: string; contentHash: string } | null> {
  // TODO: Implementare STEP 9, pas 43b din design
  //
  // 43b. Verifică dacă documentul există:
  //      existing = SELECT id, content_hash FROM rag_documents
  //                 WHERE source_type = 'weekly_snapshot'
  //                 AND source_id = :snapshot_id

  console.log(`[rag] findExistingRagDocument(${snapshotId}): STUB`);

  // STUB: Returnează null (document nou)
  return null;
}

// ============================================================================
// RAG DOCUMENT INSERT
// ============================================================================

/**
 * Inserează un nou document RAG.
 */
async function insertRagDocument(
  input: RagDocumentInput,
  contentHash: string
): Promise<RagResult> {
  // TODO: Implementare STEP 9, pas 43d din design
  //
  // 43d. INSERT nou rag_document cu:
  //      - source_type: 'weekly_snapshot'
  //      - source_id: snapshot_id
  //      - source_table: 'weekly_snapshots'
  //      - client_id, title, content, content_hash
  //      - document_date, period_start, period_end
  //      - tags: ['weekly', 'performance', year, 'W' + week_number]
  //      - embedding: NULL (va fi populat de embedding worker)
  //      - is_active: TRUE

  console.log(`[rag] insertRagDocument(${input.snapshotId}): STUB`);

  // STUB: Generează ID
  const ragId = generateUUID();

  // STUB: Ar trebui să facă INSERT în rag_documents
  // const tags = ['weekly', 'performance', String(input.year), `W${input.weekNumber}`];

  return {
    success: true,
    ragDocumentId: ragId,
    action: 'INSERT',
  };
}

// ============================================================================
// RAG DOCUMENT UPDATE
// ============================================================================

/**
 * Actualizează un document RAG existent.
 */
async function updateRagDocument(
  existingId: string,
  input: RagDocumentInput,
  newContentHash: string
): Promise<RagResult> {
  // TODO: Implementare STEP 9, pas 43c din design
  //
  // 43c. DACĂ content_hash diferit:
  //      UPDATE rag_documents SET
  //        content = :content,
  //        content_hash = :new_hash,
  //        embedding = NULL,  -- Va fi regenerat
  //        updated_at = NOW()
  //      WHERE id = :existing_id

  console.log(`[rag] updateRagDocument(${existingId}): STUB`);

  return {
    success: true,
    ragDocumentId: existingId,
    action: 'UPDATE',
  };
}

// ============================================================================
// BUILD DOCUMENT TITLE
// ============================================================================

/**
 * Construiește titlul documentului RAG.
 */
export function buildRagTitle(
  clientName: string,
  weekNumber: number,
  year: number
): string {
  return `Raport săptămânal ${weekNumber}/${year} - ${clientName}`;
}

// ============================================================================
// BUILD TAGS
// ============================================================================

/**
 * Construiește tag-urile pentru documentul RAG.
 */
export function buildRagTags(year: number, weekNumber: number): string[] {
  return ['weekly', 'performance', String(year), `W${weekNumber}`];
}

// ============================================================================
// MAIN RAG PROPAGATION
// ============================================================================

/**
 * Propagă snapshot-ul către RAG.
 *
 * Orchestrează STEP 9, pași 43-44 din design.
 */
export async function propagateToRag(input: RagDocumentInput): Promise<RagResult> {
  // TODO: Implementare STEP 9 complet din design
  //
  // 43a. Calculează content_hash
  // 43b. Verifică dacă documentul există
  // 43c. Dacă există și content_hash diferit → UPDATE
  // 43d. Dacă nu există → INSERT

  console.log(`[rag] propagateToRag(${input.snapshotId}): STUB`);

  try {
    // Pas 43a: Calculează content_hash
    const contentHash = calculateContentHash(input.summaryText);

    // Pas 43b: Verifică dacă există
    const existing = await findExistingRagDocument(input.snapshotId);

    if (existing) {
      // Pas 43c: Verifică dacă conținutul s-a schimbat
      if (existing.contentHash === contentHash) {
        console.log('[rag] Content unchanged, skipping update');
        return {
          success: true,
          ragDocumentId: existing.id,
          action: 'SKIP',
        };
      }

      // Update cu noul conținut
      return updateRagDocument(existing.id, input, contentHash);
    } else {
      // Pas 43d: Insert nou document
      return insertRagDocument(input, contentHash);
    }
  } catch (error) {
    console.error('[rag] Error propagating to RAG:', error);
    return {
      success: false,
      ragDocumentId: null,
      action: 'INSERT',
      error: (error as Error).message,
    };
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
