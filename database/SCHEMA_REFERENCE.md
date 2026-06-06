# MCP + RAG Marketing Platform - Schema Reference

## Diagrama Relațiilor (ERD Simplificată)

```
┌─────────────┐
│  platforms  │ (lookup)
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────┐     1:N     ┌─────────────┐
│   clients   │────────────▶│   accounts  │
└──────┬──────┘             └──────┬──────┘
       │                           │
       │ 1:N                       │ 1:N
       ▼                           ▼
┌─────────────────┐        ┌───────────────┐
│  client_context │        │ daily_metrics │
└─────────────────┘        └───────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐
│    kpis     │
└─────────────┘

       ┌─────────────────────────────┐
       │                             │
       ▼                             ▼
┌─────────────────┐         ┌───────────────────┐
│ weekly_snapshots│────────▶│   rag_documents   │
└─────────────────┘         └───────────────────┘
                                     ▲
       ┌─────────────────────────────┘
       │
┌─────────────────┐
│ ai_interactions │
└─────────────────┘

┌─────────────┐
│  audit_log  │ (independent - logs all tables)
└─────────────┘
```

---

## Clasificarea Tabelelor

### Single Source of Truth (SSoT)

| Tabel | Scop | Populat de |
|-------|------|------------|
| `clients` | Identitatea clienților | Manual / CRM sync |
| `platforms` | Platforme suportate | Seed data |
| `accounts` | Conturi advertising | MCP ingest |
| `kpis` | Target-uri definite | Manual |
| `client_context` | Context strategic | Manual |
| `daily_metrics` | Metrici zilnice | MCP ingest (API) |
| `weekly_snapshots` | Agregate săptămânale | Job automat |
| `audit_log` | Log modificări | Triggers |
| `ai_interactions` | Log AI | Automat |

### Surse pentru RAG (Vector Store)

| Tabel | Ce se vectorizează | Prioritate |
|-------|-------------------|------------|
| `kpis` | Descrierea target-urilor | Alta |
| `client_context` | Tot conținutul | Alta |
| `daily_metrics` | Rezumate agregate | Medie |
| `weekly_snapshots` | `summary_text`, `highlights`, `concerns` | Alta |
| `rag_documents` | Documente pre-procesate | Alta |

---

## Câmpuri Obligatorii vs Opționale

### clients

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `name` | ✅ | Numele clientului |
| `slug` | ✅ | URL-friendly, unic |
| `status` | ✅ | Default: 'active' |
| `created_at` | ✅ | Auto |
| `updated_at` | ✅ | Auto |
| `external_id` | ❌ | Pentru integrare CRM |
| `industry` | ❌ | Util pentru segmentare |
| `company_size` | ❌ | startup/sme/enterprise |
| `website` | ❌ | |
| `contact_*` | ❌ | Date contact |
| `ai_persona_notes` | ❌ | Instrucțiuni AI |
| `preferred_language` | ❌ | Default: 'ro' |

### accounts

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `client_id` | ✅ | FK către clients |
| `platform_id` | ✅ | FK către platforms |
| `external_account_id` | ✅ | ID din platformă (act_XXX) |
| `account_name` | ✅ | |
| `status` | ✅ | Default: 'active' |
| `currency` | ✅ | Default: 'RON' |
| `created_at` | ✅ | Auto |
| `updated_at` | ✅ | Auto |
| `timezone` | ❌ | Default: Europe/Bucharest |
| `credentials_ref` | ❌ | Referință vault |
| `last_sync_at` | ❌ | Ultima sincronizare |
| `sync_status` | ❌ | pending/syncing/success/error |
| `sync_error` | ❌ | Mesaj eroare |

### kpis

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `client_id` | ✅ | FK către clients |
| `period_type` | ✅ | monthly/quarterly/yearly |
| `period_start` | ✅ | |
| `period_end` | ✅ | |
| `metric_name` | ✅ | spend/roas/cpa/etc. |
| `target_value` | ✅ | Valoarea țintă |
| `target_unit` | ✅ | Default: 'absolute' |
| `created_at` | ✅ | Auto |
| `updated_at` | ✅ | Auto |
| `account_id` | ❌ | NULL = toate conturile |
| `warning_threshold` | ❌ | Default: 0.80 |
| `critical_threshold` | ❌ | Default: 0.60 |
| `notes` | ❌ | Context suplimentar |
| `created_by` | ❌ | User ID |

### client_context

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `client_id` | ✅ | FK către clients |
| `context_type` | ✅ | strategy/brand_guidelines/etc. |
| `title` | ✅ | Titlu document |
| `content` | ✅ | Conținut text |
| `is_active` | ✅ | Default: true |
| `created_at` | ✅ | Auto |
| `updated_at` | ✅ | Auto |
| `valid_from` | ❌ | Default: today |
| `valid_until` | ❌ | NULL = permanent |
| `priority` | ❌ | 1-10, default 5 |
| `created_by` | ❌ | User ID |

### daily_metrics

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `account_id` | ✅ | FK către accounts |
| `date` | ✅ | Data metricii |
| `imported_at` | ✅ | Auto |
| `campaign_*` | ❌ | Breakdown campanie |
| `adset_*` | ❌ | Breakdown ad set |
| `ad_*` | ❌ | Breakdown ad |
| `spend` | ❌ | Depinde de platformă |
| `impressions` | ❌ | |
| `clicks` | ❌ | |
| `conversions` | ❌ | |
| `revenue` | ❌ | |
| `ctr/cpc/cpm/cpa/roas` | ❌ | Calculate |
| `raw_data` | ❌ | JSONB original |

### weekly_snapshots

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `client_id` | ✅ | FK către clients |
| `week_start` | ✅ | Luni |
| `week_end` | ✅ | Duminică |
| `year` | ✅ | |
| `week_number` | ✅ | ISO week |
| `generated_at` | ✅ | Auto |
| `account_id` | ❌ | NULL = agregat client |
| `total_*` | ❌ | Metrici agregate |
| `avg_*` | ❌ | Metrici calculate |
| `*_wow_change` | ❌ | Comparații WoW |
| `kpi_*_status` | ❌ | Status vs KPI |
| `summary_text` | ❌ | Pentru RAG |
| `highlights` | ❌ | Array pentru RAG |
| `concerns` | ❌ | Array pentru RAG |
| `recommendations` | ❌ | Array pentru RAG |
| `approved_by` | ❌ | User care a verificat |
| `approved_at` | ❌ | |

### rag_documents

| Câmp | Obligatoriu | Note |
|------|:-----------:|------|
| `id` | ✅ | Auto-generat UUID |
| `source_type` | ✅ | Tipul sursei |
| `source_id` | ✅ | ID din tabelul sursă |
| `source_table` | ✅ | Numele tabelului |
| `title` | ✅ | Titlu document |
| `content` | ✅ | Text pentru vectorizare |
| `content_hash` | ✅ | SHA-256 deduplicare |
| `is_active` | ✅ | Default: true |
| `created_at` | ✅ | Auto |
| `updated_at` | ✅ | Auto |
| `client_id` | ❌ | NULL = global |
| `document_date` | ❌ | |
| `period_start` | ❌ | |
| `period_end` | ❌ | |
| `tags` | ❌ | Array text |
| `embedding` | ❌ | Vector 1536 |
| `expires_at` | ❌ | |

---

## Fluxul Datelor

```
┌─────────────────────────────────────────────────────────────┐
│                     API INGEST (MCP)                        │
│  Meta Ads / Google Ads / GA4 / TikTok / LinkedIn           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    daily_metrics                            │
│  (normalizat, toate platformele într-un format comun)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼ (job săptămânal)
┌─────────────────────────────────────────────────────────────┐
│                   weekly_snapshots                          │
│  (agregate + rezumate pentru audit)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼ (procesare RAG)
┌─────────────────────────────────────────────────────────────┐
│                    rag_documents                            │
│  (vectorizat pentru AI retrieval)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI CHAT                                │
│  Telegram Bot → RAG Query → Răspuns                         │
│  "Nu am date suficiente" dacă confidence < threshold        │
└─────────────────────────────────────────────────────────────┘
```

---

## Strategia RAG

### Ce documente se creează automat:

1. **Din weekly_snapshots** (după fiecare audit):
   - `summary_text` + `highlights` + `concerns`
   - Tag-uri: client_slug, săptămâna, anul

2. **Din client_context** (la creare/update):
   - Conținutul complet
   - Tag-uri: context_type, client_slug

3. **Din kpis** (la creare/update):
   - Target formatat human-readable
   - Tag-uri: metric_name, period_type, client_slug

### Comportament AI:

- AI citește **EXCLUSIV** din `rag_documents`
- Filtrat pe `client_id` + `is_active = true`
- Ordered by similarity (cosine) + `priority`
- Dacă `confidence_score < 0.7`:
  ```
  "Nu am date suficiente pentru a răspunde la această întrebare."
  ```

---

## Audit Săptămânal

### Checklist automat:

1. `weekly_snapshots` generat pentru toți clienții activi
2. Status KPI calculat (`on_track`/`warning`/`critical`)
3. `rag_documents` actualizat cu rezumatele noi
4. `ai_interactions` revizuit pentru feedback negativ

### Query audit:

```sql
-- Clienți cu probleme săptămâna curentă
SELECT
    c.name,
    ws.kpi_spend_status,
    ws.kpi_roas_status,
    ws.concerns
FROM weekly_snapshots ws
JOIN clients c ON ws.client_id = c.id
WHERE ws.week_start = date_trunc('week', CURRENT_DATE)::date
  AND (ws.kpi_spend_status = 'critical'
       OR ws.kpi_roas_status = 'critical');
```

---

## Scalabilitate (10 → 1.000 clienți)

| Mecanism | Implementare |
|----------|-------------|
| Partițonare | `daily_metrics` pe lună |
| Indexare | HNSW pentru vectori |
| Caching | Redis pentru query-uri frecvente |
| Batch processing | Job-uri nocturne pentru agregate |
| Connection pooling | PgBouncer |
