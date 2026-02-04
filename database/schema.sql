-- ============================================================================
-- MCP + RAG MARKETING PLATFORM - DATABASE SCHEMA
-- Version: 1.0.0
-- PostgreSQL 14+
-- ============================================================================
-- LEGENDA:
--   [SSoT] = Single Source of Truth
--   [RAG]  = Sursa pentru RAG/Vector Store
--   [REQ]  = Obligatoriu
--   [OPT]  = Optional
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector pentru embeddings

-- ============================================================================
-- 1. CLIENTS (Clienți) [SSoT]
-- ============================================================================
-- Sursa principală pentru identitatea clientului
-- ============================================================================

CREATE TABLE clients (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]
    external_id         VARCHAR(100) UNIQUE,                          -- [OPT] ID din CRM extern

    -- Date client
    name                VARCHAR(255) NOT NULL,                        -- [REQ]
    slug                VARCHAR(100) UNIQUE NOT NULL,                 -- [REQ] URL-friendly identifier
    industry            VARCHAR(100),                                 -- [OPT] Industrie
    company_size        VARCHAR(50),                                  -- [OPT] startup/sme/enterprise
    website             VARCHAR(500),                                 -- [OPT]

    -- Contact principal
    contact_name        VARCHAR(255),                                 -- [OPT]
    contact_email       VARCHAR(255),                                 -- [OPT]
    contact_phone       VARCHAR(50),                                  -- [OPT]

    -- Status
    status              VARCHAR(20) NOT NULL DEFAULT 'active',        -- [REQ] active/paused/churned
    onboarding_date     DATE,                                         -- [OPT]
    churn_date          DATE,                                         -- [OPT]

    -- Configurare AI
    ai_persona_notes    TEXT,                                         -- [OPT] Note pentru AI despre cum să comunice
    preferred_language  VARCHAR(10) DEFAULT 'ro',                     -- [OPT] Limba preferată

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    created_by          UUID,                                         -- [OPT] User ID

    -- Constraints
    CONSTRAINT chk_client_status CHECK (status IN ('active', 'paused', 'churned', 'onboarding'))
);

CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_slug ON clients(slug);
CREATE INDEX idx_clients_industry ON clients(industry);

-- ============================================================================
-- 2. PLATFORMS (Platforme disponibile) [SSoT]
-- ============================================================================
-- Lookup table pentru platformele suportate
-- ============================================================================

CREATE TABLE platforms (
    id                  VARCHAR(50) PRIMARY KEY,                      -- [REQ] meta/google/ga4/tiktok
    name                VARCHAR(100) NOT NULL,                        -- [REQ]
    api_version         VARCHAR(20),                                  -- [OPT]
    is_active           BOOLEAN DEFAULT true,                         -- [REQ]
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed data
INSERT INTO platforms (id, name) VALUES
    ('meta', 'Meta Ads (Facebook/Instagram)'),
    ('google', 'Google Ads'),
    ('ga4', 'Google Analytics 4'),
    ('tiktok', 'TikTok Ads'),
    ('linkedin', 'LinkedIn Ads');

-- ============================================================================
-- 3. ACCOUNTS (Conturi per platformă) [SSoT]
-- ============================================================================
-- Un client poate avea multiple conturi pe aceeași platformă
-- ============================================================================

CREATE TABLE accounts (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]
    client_id           UUID NOT NULL REFERENCES clients(id),         -- [REQ]
    platform_id         VARCHAR(50) NOT NULL REFERENCES platforms(id),-- [REQ]

    -- Date cont extern
    external_account_id VARCHAR(255) NOT NULL,                        -- [REQ] act_XXX pentru Meta
    account_name        VARCHAR(255) NOT NULL,                        -- [REQ]

    -- Status și configurare
    status              VARCHAR(20) NOT NULL DEFAULT 'active',        -- [REQ]
    currency            VARCHAR(10) NOT NULL DEFAULT 'RON',           -- [REQ]
    timezone            VARCHAR(50) DEFAULT 'Europe/Bucharest',       -- [OPT]

    -- Acces API (criptat sau referință la vault)
    credentials_ref     VARCHAR(255),                                 -- [OPT] Referință la secret manager
    last_sync_at        TIMESTAMPTZ,                                  -- [OPT]
    sync_status         VARCHAR(20) DEFAULT 'pending',                -- [OPT] pending/syncing/success/error
    sync_error          TEXT,                                         -- [OPT]

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]

    -- Constraints
    CONSTRAINT uq_account_platform UNIQUE (platform_id, external_account_id),
    CONSTRAINT chk_account_status CHECK (status IN ('active', 'paused', 'disconnected', 'error'))
);

CREATE INDEX idx_accounts_client ON accounts(client_id);
CREATE INDEX idx_accounts_platform ON accounts(platform_id);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_last_sync ON accounts(last_sync_at);

-- ============================================================================
-- 4. KPIS (Target-uri și obiective) [SSoT] [RAG]
-- ============================================================================
-- KPI-uri definite per client, per platformă, per perioadă
-- ============================================================================

CREATE TABLE kpis (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]
    client_id           UUID NOT NULL REFERENCES clients(id),         -- [REQ]
    account_id          UUID REFERENCES accounts(id),                 -- [OPT] NULL = toate conturile

    -- Perioadă
    period_type         VARCHAR(20) NOT NULL,                         -- [REQ] monthly/quarterly/yearly
    period_start        DATE NOT NULL,                                -- [REQ]
    period_end          DATE NOT NULL,                                -- [REQ]

    -- Metrici target
    metric_name         VARCHAR(100) NOT NULL,                        -- [REQ] spend/impressions/clicks/conversions/roas/cpa/ctr/cpm
    target_value        DECIMAL(18,4) NOT NULL,                       -- [REQ]
    target_unit         VARCHAR(20) NOT NULL DEFAULT 'absolute',      -- [REQ] absolute/percentage/currency

    -- Praguri alertă
    warning_threshold   DECIMAL(5,2) DEFAULT 0.80,                    -- [OPT] 80% din target = warning
    critical_threshold  DECIMAL(5,2) DEFAULT 0.60,                    -- [OPT] 60% din target = critical

    -- Context
    notes               TEXT,                                         -- [OPT]

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    created_by          UUID,                                         -- [OPT]

    -- Constraints
    CONSTRAINT chk_kpi_period CHECK (period_end > period_start),
    CONSTRAINT chk_kpi_period_type CHECK (period_type IN ('weekly', 'monthly', 'quarterly', 'yearly')),
    CONSTRAINT chk_kpi_metric CHECK (metric_name IN (
        'spend', 'impressions', 'clicks', 'conversions', 'leads',
        'roas', 'cpa', 'cpl', 'ctr', 'cpm', 'cpc', 'revenue',
        'reach', 'frequency', 'engagement_rate', 'video_views'
    ))
);

CREATE INDEX idx_kpis_client ON kpis(client_id);
CREATE INDEX idx_kpis_period ON kpis(period_start, period_end);
CREATE INDEX idx_kpis_metric ON kpis(metric_name);

-- ============================================================================
-- 5. CLIENT_CONTEXT (Context client pentru AI) [SSoT] [RAG]
-- ============================================================================
-- Informații textuale despre client pentru RAG
-- ============================================================================

CREATE TABLE client_context (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]
    client_id           UUID NOT NULL REFERENCES clients(id),         -- [REQ]

    -- Tip context
    context_type        VARCHAR(50) NOT NULL,                         -- [REQ]

    -- Conținut
    title               VARCHAR(255) NOT NULL,                        -- [REQ]
    content             TEXT NOT NULL,                                -- [REQ]

    -- Validitate
    valid_from          DATE DEFAULT CURRENT_DATE,                    -- [OPT]
    valid_until         DATE,                                         -- [OPT] NULL = permanent

    -- Priorități RAG
    priority            INTEGER DEFAULT 5,                            -- [OPT] 1-10, mai mare = mai important
    is_active           BOOLEAN DEFAULT true,                         -- [REQ]

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    created_by          UUID,                                         -- [OPT]

    -- Constraints
    CONSTRAINT chk_context_type CHECK (context_type IN (
        'strategy',           -- Strategie generală
        'brand_guidelines',   -- Ghid de brand
        'target_audience',    -- Audiență țintă
        'competitors',        -- Competitori
        'seasonality',        -- Sezonalitate
        'budget_notes',       -- Note buget
        'creative_notes',     -- Note creative
        'performance_notes',  -- Note performanță
        'meeting_notes',      -- Note ședințe
        'campaign_brief',     -- Brief campanie
        'restrictions',       -- Restricții
        'other'              -- Altele
    )),
    CONSTRAINT chk_context_priority CHECK (priority BETWEEN 1 AND 10)
);

CREATE INDEX idx_context_client ON client_context(client_id);
CREATE INDEX idx_context_type ON client_context(context_type);
CREATE INDEX idx_context_active ON client_context(is_active) WHERE is_active = true;
CREATE INDEX idx_context_valid ON client_context(valid_from, valid_until);

-- ============================================================================
-- 6. DAILY_METRICS (Metrici zilnice normalizate) [SSoT] [RAG]
-- ============================================================================
-- Datele extrase din API-uri, normalizate într-un format comun
-- ============================================================================

CREATE TABLE daily_metrics (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]
    account_id          UUID NOT NULL REFERENCES accounts(id),        -- [REQ]

    -- Dimensiuni temporale
    date                DATE NOT NULL,                                -- [REQ]

    -- Dimensiuni opționale (pentru breakdown)
    campaign_id         VARCHAR(255),                                 -- [OPT] ID campanie extern
    campaign_name       VARCHAR(500),                                 -- [OPT]
    adset_id            VARCHAR(255),                                 -- [OPT] ID ad set extern
    adset_name          VARCHAR(500),                                 -- [OPT]
    ad_id               VARCHAR(255),                                 -- [OPT] ID ad extern
    ad_name             VARCHAR(500),                                 -- [OPT]

    -- Metrici de bază (toate opționale, depind de platformă)
    spend               DECIMAL(18,4),                                -- [OPT] Buget cheltuit
    impressions         BIGINT,                                       -- [OPT]
    reach               BIGINT,                                       -- [OPT]
    clicks              BIGINT,                                       -- [OPT]
    link_clicks         BIGINT,                                       -- [OPT]

    -- Metrici de conversie
    conversions         BIGINT,                                       -- [OPT]
    leads               BIGINT,                                       -- [OPT]
    purchases           BIGINT,                                       -- [OPT]
    revenue             DECIMAL(18,4),                                -- [OPT]

    -- Metrici video
    video_views         BIGINT,                                       -- [OPT]
    video_views_p25     BIGINT,                                       -- [OPT]
    video_views_p50     BIGINT,                                       -- [OPT]
    video_views_p75     BIGINT,                                       -- [OPT]
    video_views_p100    BIGINT,                                       -- [OPT]

    -- Metrici engagement
    engagements         BIGINT,                                       -- [OPT]
    likes               BIGINT,                                       -- [OPT]
    comments            BIGINT,                                       -- [OPT]
    shares              BIGINT,                                       -- [OPT]

    -- Metrici calculate (denormalizate pentru query rapid)
    ctr                 DECIMAL(10,6),                                -- [OPT] clicks/impressions * 100
    cpc                 DECIMAL(18,4),                                -- [OPT] spend/clicks
    cpm                 DECIMAL(18,4),                                -- [OPT] spend/impressions * 1000
    cpa                 DECIMAL(18,4),                                -- [OPT] spend/conversions
    roas                DECIMAL(10,4),                                -- [OPT] revenue/spend

    -- Metadata import
    raw_data            JSONB,                                        -- [OPT] Datele brute din API
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]

    -- Constraints
    CONSTRAINT uq_daily_metrics UNIQUE (account_id, date, campaign_id, adset_id, ad_id)
);

-- Partițonare pe lună pentru scalabilitate
-- CREATE TABLE daily_metrics_2024_01 PARTITION OF daily_metrics FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE INDEX idx_daily_date ON daily_metrics(date);
CREATE INDEX idx_daily_account ON daily_metrics(account_id);
CREATE INDEX idx_daily_account_date ON daily_metrics(account_id, date);
CREATE INDEX idx_daily_campaign ON daily_metrics(campaign_id) WHERE campaign_id IS NOT NULL;
CREATE INDEX idx_daily_imported ON daily_metrics(imported_at);

-- ============================================================================
-- 7. WEEKLY_SNAPSHOTS (Agregate săptămânale pentru audit) [SSoT] [RAG]
-- ============================================================================
-- Pre-calculate pentru audit săptămânal și RAG
-- ============================================================================

CREATE TABLE weekly_snapshots (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]
    client_id           UUID NOT NULL REFERENCES clients(id),         -- [REQ]
    account_id          UUID REFERENCES accounts(id),                 -- [OPT] NULL = agregat la nivel de client

    -- Perioadă
    week_start          DATE NOT NULL,                                -- [REQ] Luni
    week_end            DATE NOT NULL,                                -- [REQ] Duminică
    year                INTEGER NOT NULL,                             -- [REQ]
    week_number         INTEGER NOT NULL,                             -- [REQ] ISO week

    -- Metrici agregate
    total_spend         DECIMAL(18,4),                                -- [OPT]
    total_impressions   BIGINT,                                       -- [OPT]
    total_reach         BIGINT,                                       -- [OPT]
    total_clicks        BIGINT,                                       -- [OPT]
    total_conversions   BIGINT,                                       -- [OPT]
    total_leads         BIGINT,                                       -- [OPT]
    total_revenue       DECIMAL(18,4),                                -- [OPT]

    -- Metrici calculate
    avg_ctr             DECIMAL(10,6),                                -- [OPT]
    avg_cpc             DECIMAL(18,4),                                -- [OPT]
    avg_cpm             DECIMAL(18,4),                                -- [OPT]
    avg_cpa             DECIMAL(18,4),                                -- [OPT]
    avg_roas            DECIMAL(10,4),                                -- [OPT]

    -- Comparație Week-over-Week
    spend_wow_change    DECIMAL(10,4),                                -- [OPT] Procent schimbare vs săptămâna anterioară
    conv_wow_change     DECIMAL(10,4),                                -- [OPT]
    roas_wow_change     DECIMAL(10,4),                                -- [OPT]

    -- Status vs KPI
    kpi_spend_status    VARCHAR(20),                                  -- [OPT] on_track/warning/critical/exceeded
    kpi_conv_status     VARCHAR(20),                                  -- [OPT]
    kpi_roas_status     VARCHAR(20),                                  -- [OPT]

    -- Rezumat generat pentru RAG
    summary_text        TEXT,                                         -- [OPT] Rezumat human-readable
    highlights          TEXT[],                                       -- [OPT] Array de highlights
    concerns            TEXT[],                                       -- [OPT] Array de probleme
    recommendations     TEXT[],                                       -- [OPT] Array de recomandări

    -- Audit
    generated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    approved_by         UUID,                                         -- [OPT] User care a aprobat
    approved_at         TIMESTAMPTZ,                                  -- [OPT]

    -- Constraints
    CONSTRAINT uq_weekly_snapshot UNIQUE (client_id, account_id, week_start),
    CONSTRAINT chk_week_dates CHECK (week_end = week_start + INTERVAL '6 days')
);

CREATE INDEX idx_weekly_client ON weekly_snapshots(client_id);
CREATE INDEX idx_weekly_dates ON weekly_snapshots(week_start, week_end);
CREATE INDEX idx_weekly_year_week ON weekly_snapshots(year, week_number);

-- ============================================================================
-- 8. RAG_DOCUMENTS (Documente pentru vector store) [RAG]
-- ============================================================================
-- Documente procesate și vectorizate pentru AI
-- ============================================================================

CREATE TABLE rag_documents (
    -- Identificare
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]

    -- Sursa documentului
    source_type         VARCHAR(50) NOT NULL,                         -- [REQ]
    source_id           UUID NOT NULL,                                -- [REQ] ID din tabelul sursă
    source_table        VARCHAR(100) NOT NULL,                        -- [REQ] Numele tabelului sursă

    -- Scop
    client_id           UUID REFERENCES clients(id),                  -- [OPT] NULL = document global

    -- Conținut
    title               VARCHAR(500) NOT NULL,                        -- [REQ]
    content             TEXT NOT NULL,                                -- [REQ]
    content_hash        VARCHAR(64) NOT NULL,                         -- [REQ] SHA-256 pentru deduplicare

    -- Metadate pentru filtrare
    document_date       DATE,                                         -- [OPT]
    period_start        DATE,                                         -- [OPT]
    period_end          DATE,                                         -- [OPT]
    tags                TEXT[],                                       -- [OPT]

    -- Vector embedding
    embedding           vector(1536),                                 -- [OPT] OpenAI ada-002 sau similar

    -- Status
    is_active           BOOLEAN DEFAULT true,                         -- [REQ]
    expires_at          TIMESTAMPTZ,                                  -- [OPT]

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]

    -- Constraints
    CONSTRAINT chk_rag_source_type CHECK (source_type IN (
        'weekly_snapshot',    -- Din weekly_snapshots
        'client_context',     -- Din client_context
        'kpi_definition',     -- Din kpis
        'performance_alert',  -- Alerte generate
        'manual_note'         -- Note manuale
    ))
);

CREATE INDEX idx_rag_client ON rag_documents(client_id);
CREATE INDEX idx_rag_source ON rag_documents(source_type, source_id);
CREATE INDEX idx_rag_active ON rag_documents(is_active) WHERE is_active = true;
CREATE INDEX idx_rag_date ON rag_documents(document_date);
CREATE INDEX idx_rag_tags ON rag_documents USING GIN(tags);

-- Index pentru căutare vectorială (HNSW pentru performanță)
CREATE INDEX idx_rag_embedding ON rag_documents
    USING hnsw (embedding vector_cosine_ops)
    WHERE is_active = true AND embedding IS NOT NULL;

-- ============================================================================
-- 9. AUDIT_LOG (Log pentru audit) [SSoT]
-- ============================================================================
-- Tracking pentru toate modificările
-- ============================================================================

CREATE TABLE audit_log (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]

    -- Ce s-a modificat
    table_name          VARCHAR(100) NOT NULL,                        -- [REQ]
    record_id           UUID NOT NULL,                                -- [REQ]
    action              VARCHAR(20) NOT NULL,                         -- [REQ] INSERT/UPDATE/DELETE

    -- Context
    client_id           UUID,                                         -- [OPT]
    user_id             UUID,                                         -- [OPT]

    -- Detalii
    old_values          JSONB,                                        -- [OPT]
    new_values          JSONB,                                        -- [OPT]

    -- Timestamp
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]

    -- Constraints
    CONSTRAINT chk_audit_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_record ON audit_log(record_id);
CREATE INDEX idx_audit_client ON audit_log(client_id);
CREATE INDEX idx_audit_date ON audit_log(created_at);

-- ============================================================================
-- 10. AI_INTERACTIONS (Log interacțiuni AI) [SSoT]
-- ============================================================================
-- Pentru audit și îmbunătățire
-- ============================================================================

CREATE TABLE ai_interactions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- [REQ]

    -- Context
    client_id           UUID REFERENCES clients(id),                  -- [OPT] NULL = întrebare generală
    user_identifier     VARCHAR(255),                                 -- [OPT] Telegram ID sau similar
    channel             VARCHAR(50) NOT NULL DEFAULT 'telegram',      -- [REQ]

    -- Întrebare
    question            TEXT NOT NULL,                                -- [REQ]
    question_embedding  vector(1536),                                 -- [OPT]

    -- Răspuns
    answer              TEXT NOT NULL,                                -- [REQ]
    had_sufficient_data BOOLEAN NOT NULL,                             -- [REQ] false = "Nu am date suficiente"

    -- Surse folosite
    rag_documents_used  UUID[],                                       -- [OPT] Array de rag_documents.id
    confidence_score    DECIMAL(5,4),                                 -- [OPT] 0.0000 - 1.0000

    -- Feedback
    user_feedback       VARCHAR(20),                                  -- [OPT] positive/negative/neutral
    feedback_notes      TEXT,                                         -- [OPT]

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),           -- [REQ]
    response_time_ms    INTEGER                                       -- [OPT]
);

CREATE INDEX idx_ai_client ON ai_interactions(client_id);
CREATE INDEX idx_ai_date ON ai_interactions(created_at);
CREATE INDEX idx_ai_sufficient ON ai_interactions(had_sufficient_data);
CREATE INDEX idx_ai_feedback ON ai_interactions(user_feedback);

-- ============================================================================
-- VIEWS (Pentru simplificare query-uri)
-- ============================================================================

-- View: Clienți activi cu conturi
CREATE VIEW v_active_clients_accounts AS
SELECT
    c.id AS client_id,
    c.name AS client_name,
    c.slug,
    c.industry,
    a.id AS account_id,
    a.platform_id,
    a.account_name,
    a.currency,
    a.last_sync_at
FROM clients c
LEFT JOIN accounts a ON c.id = a.client_id AND a.status = 'active'
WHERE c.status = 'active';

-- View: Performanță săptămânală curentă
CREATE VIEW v_current_week_performance AS
SELECT
    ws.*,
    c.name AS client_name,
    a.platform_id,
    a.account_name
FROM weekly_snapshots ws
JOIN clients c ON ws.client_id = c.id
LEFT JOIN accounts a ON ws.account_id = a.id
WHERE ws.week_start = date_trunc('week', CURRENT_DATE)::date;

-- View: KPI-uri curente
CREATE VIEW v_current_kpis AS
SELECT
    k.*,
    c.name AS client_name
FROM kpis k
JOIN clients c ON k.client_id = c.id
WHERE CURRENT_DATE BETWEEN k.period_start AND k.period_end;

-- ============================================================================
-- TRIGGERS (Auto-update timestamps)
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_clients_updated
    BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_accounts_updated
    BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_kpis_updated
    BEFORE UPDATE ON kpis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_context_updated
    BEFORE UPDATE ON client_context
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_rag_updated
    BEFORE UPDATE ON rag_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- COMMENTS (Documentație în baza de date)
-- ============================================================================

COMMENT ON TABLE clients IS '[SSoT] Clienții agenției - sursa principală de adevăr';
COMMENT ON TABLE platforms IS '[SSoT] Platforme suportate (Meta, Google, etc.)';
COMMENT ON TABLE accounts IS '[SSoT] Conturi de advertising per client per platformă';
COMMENT ON TABLE kpis IS '[SSoT][RAG] Target-uri și obiective per client/perioadă';
COMMENT ON TABLE client_context IS '[SSoT][RAG] Informații contextuale pentru AI (strategie, brand, etc.)';
COMMENT ON TABLE daily_metrics IS '[SSoT][RAG] Metrici zilnice normalizate din toate platformele';
COMMENT ON TABLE weekly_snapshots IS '[SSoT][RAG] Agregate săptămânale pentru audit și AI';
COMMENT ON TABLE rag_documents IS '[RAG] Documente vectorizate pentru AI retrieval';
COMMENT ON TABLE audit_log IS '[SSoT] Log pentru toate modificările';
COMMENT ON TABLE ai_interactions IS '[SSoT] Log interacțiuni AI pentru audit';
