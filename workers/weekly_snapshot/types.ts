/**
 * Weekly Snapshot Engine - Type Definitions
 * ==========================================
 * Contractul de date pentru întregul worker.
 * Toate modulele importă tipurile de aici.
 */

// ============================================================================
// INPUT TYPES
// ============================================================================

export interface WorkerParams {
  weekStart: Date;
  clientId: string | null;
  forceRegenerate: boolean;
}

export interface ClientToProcess {
  id: string;
  name: string;
  slug: string;
  status: string;
  currency: string;
  action: 'INSERT' | 'UPDATE' | 'SKIP';
  existingSnapshotId?: string;
}

export interface AccountInfo {
  id: string;
  clientId: string;
  platformId: string;
  externalAccountId: string;
  accountName: string;
  currency: string;
  status: string;
}

// ============================================================================
// EXTRACTED DATA TYPES
// ============================================================================

export interface DailyMetricRow {
  id: string;
  accountId: string;
  date: Date;
  campaignId?: string;
  campaignName?: string;
  spend?: number;
  impressions?: number;
  clicks?: number;
  reach?: number;
  conversions?: number;
  leads?: number;
  purchases?: number;
  revenue?: number;
  videoViews?: number;
  engagements?: number;
}

export interface ExtractedData {
  clientId: string;
  accounts: AccountInfo[];
  currentWeekMetrics: DailyMetricRow[];
  previousWeekMetrics: DailyMetricRow[];
  daysWithData: number;
  expectedDays: number;
  dataCompleteness: number;
  flags: DataFlag[];
}

export type DataFlag =
  | 'NO_ACTIVE_ACCOUNTS'
  | 'INSUFFICIENT_DATA'
  | 'NO_PREVIOUS_DATA'
  | 'INCOMPLETE_PREVIOUS'
  | 'PARTIAL_ACCOUNTS'
  | 'SYNC_ERROR';

// ============================================================================
// AGGREGATED METRICS TYPES
// ============================================================================

export interface AggregatedMetrics {
  totalSpend: number;
  totalImpressions: number;
  totalClicks: number;
  totalReach: number;
  totalConversions: number;
  totalLeads: number;
  totalPurchases: number;
  totalRevenue: number;
  totalVideoViews: number;
  totalEngagements: number;
  // Calculated
  avgCtr: number | null;
  avgCpc: number | null;
  avgCpm: number | null;
  avgCpa: number | null;
  avgRoas: number | null;
}

// ============================================================================
// WOW TYPES
// ============================================================================

export interface WowChange {
  changePercent: number | null;
  direction: 'up' | 'down' | 'stable';
  previousValue: number | null;
  isImprovement?: boolean; // Pentru CPA (mai mic = mai bine)
}

export interface WowResult {
  spend: WowChange;
  impressions: WowChange;
  clicks: WowChange;
  conversions: WowChange;
  revenue: WowChange;
  roas: WowChange;
  cpa: WowChange;
  trend: 'improving' | 'declining' | 'stable';
}

// ============================================================================
// KPI TYPES
// ============================================================================

export interface KpiDefinition {
  id: string;
  clientId: string;
  metricName: string;
  targetValue: number;
  targetUnit: string;
  periodStart: Date;
  periodEnd: Date;
  warningThreshold: number;
  criticalThreshold: number;
}

export interface KpiStatusEntry {
  target: number;
  proratedTarget: number;
  actual: number | null;
  achievementPercent: number | null;
  status: 'exceeded' | 'on_track' | 'warning' | 'critical';
  periodProgressPercent: number;
}

export interface KpiResult {
  kpiStatus: Record<string, KpiStatusEntry>;
  flags: KpiFlag[];
}

export type KpiFlag = 'NO_KPIS_DEFINED' | 'UNKNOWN_METRIC' | 'INVALID_KPI_TARGET';

// ============================================================================
// ANOMALY TYPES
// ============================================================================

export interface Anomaly {
  type: string;
  severity: 'info' | 'warning' | 'critical';
  metric?: string;
  message: string;
  detectedAt: Date;
}

// ============================================================================
// CONTENT TYPES
// ============================================================================

export interface GeneratedContent {
  highlights: string[];
  concerns: string[];
  recommendations: string[];
  summaryText: string;
  snapshotJson: Record<string, unknown>;
}

// ============================================================================
// PERSISTENCE TYPES
// ============================================================================

export interface SnapshotRecord {
  id: string;
  clientId: string;
  accountId: string | null;
  weekStart: Date;
  weekEnd: Date;
  year: number;
  weekNumber: number;
  totalSpend: number;
  totalImpressions: number;
  totalClicks: number;
  totalConversions: number;
  totalLeads: number;
  totalRevenue: number;
  avgCtr: number | null;
  avgCpc: number | null;
  avgCpm: number | null;
  avgCpa: number | null;
  avgRoas: number | null;
  spendWowChange: number | null;
  convWowChange: number | null;
  roasWowChange: number | null;
  kpiSpendStatus: string | null;
  kpiConvStatus: string | null;
  kpiRoasStatus: string | null;
  summaryText: string;
  highlights: string[];
  concerns: string[];
  recommendations: string[];
  snapshotJson: Record<string, unknown>;
  generatedAt: Date;
}

export interface PersistenceResult {
  success: boolean;
  snapshotId: string | null;
  action: 'INSERT' | 'UPDATE' | 'SKIP';
  error?: string;
}

// ============================================================================
// RAG TYPES
// ============================================================================

export interface RagDocumentInput {
  snapshotId: string;
  clientId: string;
  clientName: string;
  weekStart: Date;
  weekEnd: Date;
  year: number;
  weekNumber: number;
  summaryText: string;
}

export interface RagResult {
  success: boolean;
  ragDocumentId: string | null;
  action: 'INSERT' | 'UPDATE' | 'SKIP';
  error?: string;
}

// ============================================================================
// AUDIT TYPES
// ============================================================================

export type AuditEvent =
  | 'START_BATCH'
  | 'CLIENT_START'
  | 'SNAPSHOT_CREATED'
  | 'SNAPSHOT_UPDATED'
  | 'SNAPSHOT_SKIPPED'
  | 'SNAPSHOT_FAILED'
  | 'RAG_CREATED'
  | 'RAG_UPDATED'
  | 'BATCH_COMPLETE'
  | 'ANOMALY_DETECTED';

export interface AuditLogEntry {
  tableName: string;
  recordId: string | null;
  action: 'INSERT' | 'UPDATE' | 'DELETE';
  clientId: string | null;
  userId: string | null;
  oldValues: Record<string, unknown> | null;
  newValues: Record<string, unknown>;
}

// ============================================================================
// PROCESSING RESULT TYPES
// ============================================================================

export type ClientProcessingStatus = 'success' | 'partial' | 'failed' | 'skipped';

export interface ClientProcessingResult {
  clientId: string;
  clientName: string;
  status: ClientProcessingStatus;
  snapshotId: string | null;
  ragDocumentId: string | null;
  flags: (DataFlag | KpiFlag)[];
  anomaliesCount: number;
  durationMs: number;
  error?: string;
}

// ============================================================================
// FINAL OUTPUT TYPE
// ============================================================================

export interface WorkerOutput {
  weekStart: string;
  weekEnd: string;
  processed: number;
  success: number;
  partial: number;
  failed: number;
  skipped: number;
  durationMs: number;
  results?: ClientProcessingResult[];
}
