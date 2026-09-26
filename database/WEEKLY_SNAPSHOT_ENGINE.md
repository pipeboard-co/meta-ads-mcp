# Weekly Snapshot Engine - Design Document

---

# 1. PSEUDOLOGICĂ DETERMINISTĂ

## FAZA A: Inițializare

```
1. Primește parametrii de intrare:
   - target_week_start (DATE, Luni)
   - client_id (UUID, opțional - NULL = toți clienții activi)
   - force_regenerate (BOOL, default FALSE)

2. Calculează week_end:
   - week_end = target_week_start + 6 zile (Duminică)

3. Calculează previous_week:
   - prev_week_start = target_week_start - 7 zile
   - prev_week_end = target_week_start - 1 zi

4. Validează target_week_start:
   - TREBUIE să fie Luni (day_of_week = 1)
   - TREBUIE să fie în trecut sau săptămâna curentă
   - DACĂ nu → ABORT cu eroare INVALID_WEEK_START

5. Extrage lista de clienți de procesat:
   - DACĂ client_id specificat → [client_id]
   - ALTFEL → SELECT id FROM clients WHERE status = 'active'

6. Pentru fiecare client, verifică dacă snapshot există:
   - DACĂ există ȘI force_regenerate = FALSE → SKIP
   - DACĂ există ȘI force_regenerate = TRUE → marchează pentru UPDATE
   - DACĂ nu există → marchează pentru INSERT
```

## FAZA B: Extragere Date (per client)

```
7. Extrage conturile active ale clientului:
   - accounts[] = SELECT * FROM accounts
                  WHERE client_id = :client_id
                  AND status = 'active'

8. DACĂ accounts[] este GOL:
   - Setează flag: NO_ACTIVE_ACCOUNTS
   - Continuă cu snapshot gol (va fi marcat partial)

9. Pentru fiecare account, extrage daily_metrics:
   - current_week_metrics[] = SELECT * FROM daily_metrics
                               WHERE account_id = :account_id
                               AND date BETWEEN :week_start AND :week_end

10. Numără zilele cu date:
    - days_with_data = COUNT(DISTINCT date) din current_week_metrics
    - expected_days = 7 (sau mai puțin dacă săptămâna curentă)

11. Calculează data_completeness:
    - data_completeness = days_with_data / expected_days
    - DACĂ data_completeness < 0.5 → flag INSUFFICIENT_DATA

12. Extrage metrici săptămâna anterioară (pentru WoW):
    - prev_week_metrics[] = SELECT * FROM daily_metrics
                            WHERE account_id = :account_id
                            AND date BETWEEN :prev_week_start AND :prev_week_end
```

## FAZA C: Agregare Metrici

```
13. Inițializează acumulatori la 0:
    - total_spend = 0
    - total_impressions = 0
    - total_clicks = 0
    - total_reach = 0
    - total_conversions = 0
    - total_leads = 0
    - total_purchases = 0
    - total_revenue = 0
    - total_video_views = 0
    - total_engagements = 0

14. Pentru fiecare rând din current_week_metrics[]:
    - total_spend += COALESCE(row.spend, 0)
    - total_impressions += COALESCE(row.impressions, 0)
    - total_clicks += COALESCE(row.clicks, 0)
    - total_reach += COALESCE(row.reach, 0)
    - total_conversions += COALESCE(row.conversions, 0)
    - total_leads += COALESCE(row.leads, 0)
    - total_purchases += COALESCE(row.purchases, 0)
    - total_revenue += COALESCE(row.revenue, 0)
    - total_video_views += COALESCE(row.video_views, 0)
    - total_engagements += COALESCE(row.engagements, 0)

15. Calculează metrici derivate (cu protecție divide-by-zero):
    - avg_ctr = DACĂ total_impressions > 0
                ATUNCI (total_clicks / total_impressions) * 100
                ALTFEL NULL
    - avg_cpc = DACĂ total_clicks > 0
                ATUNCI total_spend / total_clicks
                ALTFEL NULL
    - avg_cpm = DACĂ total_impressions > 0
                ATUNCI (total_spend / total_impressions) * 1000
                ALTFEL NULL
    - avg_cpa = DACĂ total_conversions > 0
                ATUNCI total_spend / total_conversions
                ALTFEL NULL
    - avg_roas = DACĂ total_spend > 0
                 ATUNCI total_revenue / total_spend
                 ALTFEL NULL

16. Repetă pașii 14-15 pentru prev_week_metrics[] → prev_totals
```

## FAZA D: Calcul Week-over-Week

```
17. Definește funcție WoW_change(current, previous):
    - DACĂ previous = 0 SAU previous = NULL:
      - DACĂ current > 0 → returnează +100.00 (creștere de la 0)
      - ALTFEL → returnează 0.00 (fără schimbare)
    - ALTFEL:
      - returnează ((current - previous) / previous) * 100

18. Calculează WoW pentru fiecare metrică:
    - spend_wow = WoW_change(total_spend, prev_total_spend)
    - impressions_wow = WoW_change(total_impressions, prev_total_impressions)
    - clicks_wow = WoW_change(total_clicks, prev_total_clicks)
    - conversions_wow = WoW_change(total_conversions, prev_total_conversions)
    - revenue_wow = WoW_change(total_revenue, prev_total_revenue)
    - roas_wow = WoW_change(avg_roas, prev_avg_roas)
    - cpa_wow = WoW_change(avg_cpa, prev_avg_cpa)
      - NOTĂ: pentru CPA, WoW negativ = îmbunătățire

19. Determină trend general:
    - DACĂ roas_wow > 10 ȘI conversions_wow > 0 → trend = "improving"
    - DACĂ roas_wow < -10 SAU conversions_wow < -20 → trend = "declining"
    - ALTFEL → trend = "stable"
```

## FAZA E: Calcul KPI Status

```
20. Extrage KPI-urile active pentru client și perioadă:
    - active_kpis[] = SELECT * FROM kpis
                      WHERE client_id = :client_id
                      AND :week_start >= period_start
                      AND :week_end <= period_end

21. DACĂ active_kpis[] este GOL:
    - Setează flag: NO_KPIS_DEFINED
    - kpi_status = {} (obiect gol)
    - SKIP la Faza F

22. Pentru fiecare KPI din active_kpis[]:

    22a. Identifică valoarea actuală:
         - MATCH kpi.metric_name:
           - "spend" → actual = total_spend
           - "conversions" → actual = total_conversions
           - "leads" → actual = total_leads
           - "revenue" → actual = total_revenue
           - "roas" → actual = avg_roas
           - "cpa" → actual = avg_cpa
           - "ctr" → actual = avg_ctr
           - DEFAULT → actual = NULL, flag UNKNOWN_METRIC

    22b. Calculează progresul în perioada KPI:
         - kpi_duration_days = kpi.period_end - kpi.period_start + 1
         - elapsed_days = :week_end - kpi.period_start + 1
         - elapsed_days = MIN(elapsed_days, kpi_duration_days)
         - period_progress = elapsed_days / kpi_duration_days

    22c. Calculează target proratat:
         - DACĂ kpi.metric_name IN ("spend", "conversions", "leads", "revenue"):
           - prorated_target = kpi.target_value * period_progress
         - DACĂ kpi.metric_name IN ("roas", "cpa", "ctr"):
           - prorated_target = kpi.target_value (nu se proratează)

    22d. Calculează achievement:
         - DACĂ prorated_target > 0:
           - achievement = actual / prorated_target
         - ALTFEL:
           - achievement = NULL

    22e. Determină status:
         - DACĂ kpi.metric_name = "cpa" (mai mic = mai bine):
           - DACĂ actual <= prorated_target → status = "exceeded"
           - DACĂ actual <= prorated_target * 1.2 → status = "on_track"
           - DACĂ actual <= prorated_target * 1.5 → status = "warning"
           - ALTFEL → status = "critical"
         - ALTFEL (mai mare = mai bine):
           - DACĂ achievement >= 1.0 → status = "exceeded"
           - DACĂ achievement >= kpi.warning_threshold → status = "on_track"
           - DACĂ achievement >= kpi.critical_threshold → status = "warning"
           - ALTFEL → status = "critical"

    22f. Salvează în kpi_status[kpi.metric_name]:
         - target: kpi.target_value
         - prorated_target: prorated_target
         - actual: actual
         - achievement: achievement (as percentage)
         - status: status
         - period_progress: period_progress (as percentage)
```

## FAZA F: Detectare Anomalii

```
23. Inițializează anomalies[] = []

24. Verifică anomalii de spend:
    - DACĂ spend_wow > 50:
      - ADAUGĂ {type: "spend_spike", severity: "warning",
                message: "Spend crescut cu X% vs săptămâna anterioară"}
    - DACĂ spend_wow < -50:
      - ADAUGĂ {type: "spend_drop", severity: "info",
                message: "Spend scăzut cu X% vs săptămâna anterioară"}

25. Verifică anomalii de performanță:
    - DACĂ roas_wow < -30 ȘI total_spend > 100:
      - ADAUGĂ {type: "roas_decline", severity: "critical",
                message: "ROAS scăzut semnificativ cu X%"}
    - DACĂ cpa_wow > 50 ȘI total_conversions > 0:
      - ADAUGĂ {type: "cpa_increase", severity: "warning",
                message: "CPA crescut cu X%"}

26. Verifică anomalii de volum:
    - DACĂ conversions_wow < -40 ȘI spend_wow >= -10:
      - ADAUGĂ {type: "conversion_drop", severity: "critical",
                message: "Conversii scăzute X% fără scădere proporțională de spend"}

27. Verifică lipsă date:
    - DACĂ data_completeness < 0.7:
      - ADAUGĂ {type: "incomplete_data", severity: "warning",
                message: "Date incomplete pentru X din 7 zile"}

28. Verifică KPI-uri critice:
    - PENTRU FIECARE kpi IN kpi_status:
      - DACĂ kpi.status = "critical":
        - ADAUGĂ {type: "kpi_critical", severity: "critical",
                  metric: kpi.metric_name,
                  message: "KPI [metric] la X% din target"}
```

## FAZA G: Generare Highlights și Concerns

```
29. Inițializează highlights[] = []

30. Generează highlights (performanțe bune):
    - DACĂ any kpi.status = "exceeded":
      - ADAUGĂ "KPI [metric] depășit: [actual] vs target [target]"
    - DACĂ roas_wow > 20 ȘI avg_roas > 1:
      - ADAUGĂ "ROAS îmbunătățit cu X% (de la Y la Z)"
    - DACĂ conversions_wow > 20:
      - ADAUGĂ "Conversii crescute cu X%"
    - DACĂ cpa_wow < -15:
      - ADAUGĂ "CPA optimizat cu X%"

31. Inițializează concerns[] = []

32. Generează concerns (probleme):
    - PENTRU FIECARE anomaly IN anomalies WHERE severity IN ("warning", "critical"):
      - ADAUGĂ anomaly.message
    - DACĂ data_completeness < 1.0:
      - ADAUGĂ "Date lipsă pentru X zile din săptămână"
    - DACĂ NO_KPIS_DEFINED:
      - ADAUGĂ "Nu sunt definite KPI-uri pentru această perioadă"

33. Generează recommendations[] = []:
    - DACĂ any kpi.status = "critical":
      - ADAUGĂ "Revizuire urgentă necesară pentru [metric]"
    - DACĂ cpa_wow > 30:
      - ADAUGĂ "Analiză audiență și creative recomandate"
    - DACĂ spend_wow > 40 ȘI conversions_wow < 10:
      - ADAUGĂ "Verificare eficiență scalare buget"
```

## FAZA H: Construire snapshot_json

```
34. Construiește obiectul snapshot_json (vezi secțiunea 2)

35. Calculează year și week_number din target_week_start:
    - year = EXTRACT(ISOYEAR FROM target_week_start)
    - week_number = EXTRACT(WEEK FROM target_week_start)
```

## FAZA I: Generare summary_text

```
36. Construiește summary_text folosind template-ul (vezi secțiunea 3)

37. Validează summary_text:
    - DACĂ lungime > 4000 caractere → trunchiază la 4000
    - DACĂ lungime < 100 caractere → flag SUMMARY_TOO_SHORT
```

## FAZA J: Persistare

```
38. Determină tipul operației:
    - DACĂ snapshot existent marcat pentru UPDATE → UPDATE
    - ALTFEL → INSERT

39. Construiește record-ul weekly_snapshots:
    - id: UUID nou (pentru INSERT) sau existent (pentru UPDATE)
    - client_id: client_id
    - account_id: NULL (agregat la nivel client)
    - week_start: target_week_start
    - week_end: week_end
    - year: year
    - week_number: week_number
    - total_spend: total_spend
    - total_impressions: total_impressions
    - total_clicks: total_clicks
    - total_conversions: total_conversions
    - total_leads: total_leads
    - total_revenue: total_revenue
    - avg_ctr: avg_ctr
    - avg_cpc: avg_cpc
    - avg_cpm: avg_cpm
    - avg_cpa: avg_cpa
    - avg_roas: avg_roas
    - spend_wow_change: spend_wow
    - conv_wow_change: conversions_wow
    - roas_wow_change: roas_wow
    - kpi_spend_status: kpi_status["spend"].status sau NULL
    - kpi_conv_status: kpi_status["conversions"].status sau NULL
    - kpi_roas_status: kpi_status["roas"].status sau NULL
    - summary_text: summary_text
    - highlights: highlights[]
    - concerns: concerns[]
    - recommendations: recommendations[]
    - snapshot_json: snapshot_json
    - generated_at: NOW()

40. Execută INSERT sau UPDATE

41. DACĂ operația reușește:
    - Loghează în audit_log (vezi secțiunea 6)
    - Returnează {success: true, snapshot_id: id}

42. DACĂ operația eșuează:
    - Loghează eroare în audit_log
    - Returnează {success: false, error: message}
```

## FAZA K: Propagare RAG

```
43. DUPĂ persistare reușită, creează/actualizează rag_document:

    43a. Calculează content_hash:
         - content_hash = SHA256(summary_text)

    43b. Verifică dacă documentul există:
         - existing = SELECT id FROM rag_documents
                      WHERE source_type = 'weekly_snapshot'
                      AND source_id = :snapshot_id

    43c. DACĂ existing:
         - DACĂ content_hash = existing.content_hash → SKIP (nemodificat)
         - ALTFEL → UPDATE conținut și embedding = NULL (va fi regenerat)

    43d. ALTFEL:
         - INSERT nou rag_document cu:
           - source_type: 'weekly_snapshot'
           - source_id: snapshot_id
           - source_table: 'weekly_snapshots'
           - client_id: client_id
           - title: "Raport săptămânal {week_number}/{year} - {client_name}"
           - content: summary_text
           - content_hash: content_hash
           - document_date: week_end
           - period_start: week_start
           - period_end: week_end
           - tags: ['weekly', 'performance', year, 'W' + week_number]
           - embedding: NULL (va fi populat de embedding worker)
           - is_active: TRUE

44. Loghează în audit_log crearea/actualizarea rag_document
```

---

# 2. STRUCTURA EXACTĂ snapshot_json

```json
{
  "version": "1.0",
  "generated_at": "2024-01-15T08:30:00Z",
  "week": {
    "start": "2024-01-08",
    "end": "2024-01-14",
    "year": 2024,
    "number": 2
  },
  "client": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Acme Corp",
    "slug": "acme-corp"
  },
  "data_quality": {
    "completeness": 1.0,
    "days_with_data": 7,
    "expected_days": 7,
    "accounts_included": 2,
    "accounts_total": 2,
    "flags": []
  },
  "performance": {
    "spend": {
      "value": 15420.50,
      "currency": "RON",
      "formatted": "15.420,50 RON"
    },
    "impressions": {
      "value": 2450000,
      "formatted": "2.45M"
    },
    "clicks": {
      "value": 48500,
      "formatted": "48.5K"
    },
    "reach": {
      "value": 890000,
      "formatted": "890K"
    },
    "conversions": {
      "value": 342,
      "formatted": "342"
    },
    "leads": {
      "value": 89,
      "formatted": "89"
    },
    "purchases": {
      "value": 253,
      "formatted": "253"
    },
    "revenue": {
      "value": 45230.00,
      "currency": "RON",
      "formatted": "45.230,00 RON"
    },
    "video_views": {
      "value": 125000,
      "formatted": "125K"
    },
    "engagements": {
      "value": 8900,
      "formatted": "8.9K"
    }
  },
  "calculated_metrics": {
    "ctr": {
      "value": 1.98,
      "formatted": "1.98%"
    },
    "cpc": {
      "value": 0.32,
      "currency": "RON",
      "formatted": "0,32 RON"
    },
    "cpm": {
      "value": 6.29,
      "currency": "RON",
      "formatted": "6,29 RON"
    },
    "cpa": {
      "value": 45.09,
      "currency": "RON",
      "formatted": "45,09 RON"
    },
    "roas": {
      "value": 2.93,
      "formatted": "2.93x"
    },
    "cost_per_lead": {
      "value": 173.26,
      "currency": "RON",
      "formatted": "173,26 RON"
    }
  },
  "week_over_week": {
    "spend": {
      "change_percent": 12.5,
      "direction": "up",
      "previous_value": 13707.11
    },
    "impressions": {
      "change_percent": 8.2,
      "direction": "up",
      "previous_value": 2264000
    },
    "clicks": {
      "change_percent": 15.1,
      "direction": "up",
      "previous_value": 42137
    },
    "conversions": {
      "change_percent": 22.1,
      "direction": "up",
      "previous_value": 280
    },
    "revenue": {
      "change_percent": 18.7,
      "direction": "up",
      "previous_value": 38104.00
    },
    "roas": {
      "change_percent": 5.5,
      "direction": "up",
      "previous_value": 2.78
    },
    "cpa": {
      "change_percent": -7.9,
      "direction": "down",
      "previous_value": 48.95,
      "is_improvement": true
    },
    "trend": "improving"
  },
  "kpi_status": {
    "spend": {
      "target": 60000.00,
      "prorated_target": 15000.00,
      "actual": 15420.50,
      "achievement_percent": 102.8,
      "status": "exceeded",
      "period_progress_percent": 25.0
    },
    "conversions": {
      "target": 1200,
      "prorated_target": 300,
      "actual": 342,
      "achievement_percent": 114.0,
      "status": "exceeded",
      "period_progress_percent": 25.0
    },
    "roas": {
      "target": 3.0,
      "prorated_target": 3.0,
      "actual": 2.93,
      "achievement_percent": 97.7,
      "status": "on_track",
      "period_progress_percent": 25.0
    },
    "cpa": {
      "target": 50.00,
      "prorated_target": 50.00,
      "actual": 45.09,
      "achievement_percent": 110.9,
      "status": "exceeded",
      "period_progress_percent": 25.0
    }
  },
  "anomalies": [
    {
      "type": "conversion_spike",
      "severity": "info",
      "metric": "conversions",
      "message": "Conversii crescute cu 22.1% - verifică sursa creșterii",
      "detected_at": "2024-01-15T08:30:00Z"
    }
  ],
  "highlights": [
    "KPI conversii depășit: 342 vs target 300 (114%)",
    "KPI CPA depășit: 45,09 RON vs target 50 RON",
    "Conversii crescute cu 22.1% față de săptămâna anterioară",
    "CPA optimizat cu 7.9%"
  ],
  "concerns": [],
  "recommendations": [
    "ROAS la 97.7% din target - monitorizare atentă recomandat"
  ],
  "platforms_breakdown": {
    "meta": {
      "spend": 12500.00,
      "conversions": 285,
      "roas": 3.12
    },
    "google": {
      "spend": 2920.50,
      "conversions": 57,
      "roas": 2.15
    }
  }
}
```

---

# 3. STRUCTURA EXACTĂ summary_text (PENTRU RAG)

```
RAPORT SĂPTĂMÂNAL: {client_name}
Săptămâna {week_number}/{year} ({week_start} - {week_end})

═══════════════════════════════════════════════════

REZUMAT PERFORMANȚĂ:

Spend total: {spend} {currency}
Impresii: {impressions_formatted}
Click-uri: {clicks_formatted}
Conversii: {conversions}
Venituri: {revenue} {currency}

Metrici cheie:
• CTR: {ctr}%
• CPC: {cpc} {currency}
• CPM: {cpm} {currency}
• CPA: {cpa} {currency}
• ROAS: {roas}x

═══════════════════════════════════════════════════

COMPARAȚIE CU SĂPTĂMÂNA ANTERIOARĂ:

• Spend: {spend_wow_direction} {spend_wow_abs}% ({prev_spend} → {spend})
• Conversii: {conv_wow_direction} {conv_wow_abs}% ({prev_conv} → {conversions})
• ROAS: {roas_wow_direction} {roas_wow_abs}% ({prev_roas}x → {roas}x)
• CPA: {cpa_wow_direction} {cpa_wow_abs}% ({prev_cpa} → {cpa})

Trend general: {trend}

═══════════════════════════════════════════════════

STATUS KPI-URI:

{FOR EACH kpi IN kpi_status:}
• {kpi.metric_name}: {kpi.status_emoji} {kpi.status}
  Actual: {kpi.actual} | Target: {kpi.target} | Realizare: {kpi.achievement}%
{END FOR}

═══════════════════════════════════════════════════

HIGHLIGHTS:
{FOR EACH highlight IN highlights:}
✓ {highlight}
{END FOR}

{IF concerns NOT EMPTY:}
ATENȚIONĂRI:
{FOR EACH concern IN concerns:}
⚠ {concern}
{END FOR}
{END IF}

{IF recommendations NOT EMPTY:}
RECOMANDĂRI:
{FOR EACH rec IN recommendations:}
→ {rec}
{END FOR}
{END IF}

═══════════════════════════════════════════════════

Raport generat automat la {generated_at}.
Date complete: {data_completeness_percent}% ({days_with_data}/7 zile)
```

### Exemplu Concret summary_text:

```
RAPORT SĂPTĂMÂNAL: Acme Corp
Săptămâna 2/2024 (08.01.2024 - 14.01.2024)

═══════════════════════════════════════════════════

REZUMAT PERFORMANȚĂ:

Spend total: 15.420,50 RON
Impresii: 2.45M
Click-uri: 48.5K
Conversii: 342
Venituri: 45.230,00 RON

Metrici cheie:
• CTR: 1.98%
• CPC: 0,32 RON
• CPM: 6,29 RON
• CPA: 45,09 RON
• ROAS: 2.93x

═══════════════════════════════════════════════════

COMPARAȚIE CU SĂPTĂMÂNA ANTERIOARĂ:

• Spend: ↑ 12.5% (13.707 RON → 15.420 RON)
• Conversii: ↑ 22.1% (280 → 342)
• ROAS: ↑ 5.5% (2.78x → 2.93x)
• CPA: ↓ 7.9% (48,95 RON → 45,09 RON)

Trend general: În creștere

═══════════════════════════════════════════════════

STATUS KPI-URI:

• Spend: ✅ DEPĂȘIT
  Actual: 15.420 RON | Target: 15.000 RON | Realizare: 102.8%
• Conversii: ✅ DEPĂȘIT
  Actual: 342 | Target: 300 | Realizare: 114.0%
• ROAS: 🟡 PE DRUM BUN
  Actual: 2.93x | Target: 3.00x | Realizare: 97.7%
• CPA: ✅ DEPĂȘIT
  Actual: 45,09 RON | Target: 50,00 RON | Realizare: 110.9%

═══════════════════════════════════════════════════

HIGHLIGHTS:
✓ KPI conversii depășit: 342 vs target 300 (114%)
✓ KPI CPA depășit: 45,09 RON vs target 50 RON
✓ Conversii crescute cu 22.1% față de săptămâna anterioară
✓ CPA optimizat cu 7.9%

RECOMANDĂRI:
→ ROAS la 97.7% din target - monitorizare atentă recomandată

═══════════════════════════════════════════════════

Raport generat automat la 15.01.2024 08:30.
Date complete: 100% (7/7 zile)
```

---

# 4. ORDINEA OPERAȚIILOR

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                            │
│                    (Rulează săptămânal, Luni)                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: VALIDARE                                                │
│ ───────────────                                                 │
│ • Verifică că target_week este valid (Luni, în trecut)          │
│ • Încarcă lista clienți activi                                  │
│ • Verifică existența snapshot-urilor (skip/update/insert)       │
│                                                                 │
│ DEPENDENȚE: Niciuna                                             │
│ EȘEC: ABORT total, log eroare                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: EXTRAGERE DATE (per client, PARALELIZABIL)              │
│ ─────────────────────────────────────────────────               │
│ • Query daily_metrics pentru săptămâna curentă                  │
│ • Query daily_metrics pentru săptămâna anterioară               │
│ • Calculează data_completeness                                  │
│                                                                 │
│ DEPENDENȚE: STEP 1                                              │
│ EȘEC per client: Marchează PARTIAL, continuă cu ceilalți        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: AGREGARE METRICI (per client)                           │
│ ────────────────────────────────────                            │
│ • SUM pentru metrici absolute                                   │
│ • Calcul metrici derivate (CTR, CPC, CPA, ROAS)                 │
│ • Agregare pentru ambele săptămâni                              │
│                                                                 │
│ DEPENDENȚE: STEP 2                                              │
│ EȘEC: Marchează FAILED, continuă cu ceilalți                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: CALCUL WoW (per client)                                 │
│ ───────────────────────────────                                 │
│ • Calculează change% pentru fiecare metrică                     │
│ • Determină trend general                                       │
│                                                                 │
│ DEPENDENȚE: STEP 3 (current + previous aggregations)            │
│ EȘEC: WoW = NULL, continuă                                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: CALCUL KPI STATUS (per client)                          │
│ ─────────────────────────────────────                           │
│ • Extrage KPI-uri active pentru perioadă                        │
│ • Calculează prorated target                                    │
│ • Determină achievement și status                               │
│                                                                 │
│ DEPENDENȚE: STEP 3 (aggregated actuals) + tabel kpis            │
│ EȘEC: kpi_status = {}, flag NO_KPIS, continuă                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: DETECTARE ANOMALII (per client)                         │
│ ─────────────────────────────────────                           │
│ • Verifică thresholds pentru spike/drop                         │
│ • Verifică KPI-uri critice                                      │
│ • Verifică data completeness                                    │
│                                                                 │
│ DEPENDENȚE: STEP 4 (WoW) + STEP 5 (KPI status)                  │
│ EȘEC: anomalies = [], continuă                                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: GENERARE CONTENT (per client)                           │
│ ────────────────────────────────────                            │
│ • Construiește highlights[]                                     │
│ • Construiește concerns[]                                       │
│ • Construiește recommendations[]                                │
│ • Generează summary_text                                        │
│ • Construiește snapshot_json                                    │
│                                                                 │
│ DEPENDENȚE: STEP 3, 4, 5, 6                                     │
│ EȘEC: FAILED, nu se salvează                                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: PERSISTARE (per client)                                 │
│ ────────────────────────────────                                │
│ • INSERT sau UPDATE în weekly_snapshots                         │
│ • Log în audit_log                                              │
│                                                                 │
│ DEPENDENȚE: STEP 7                                              │
│ EȘEC: RETRY 3x, apoi FAILED + log                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9: PROPAGARE RAG (per client, ASYNC)                       │
│ ────────────────────────────────────────                        │
│ • Crează/actualizează rag_document                              │
│ • Marchează embedding = NULL pentru regenerare                  │
│                                                                 │
│ DEPENDENȚE: STEP 8 (snapshot saved)                             │
│ EȘEC: Log warning, snapshot rămâne valid                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 10: RAPORT FINAL                                           │
│ ───────────────────────                                         │
│ • Agregează rezultate: success/partial/failed per client        │
│ • Trimite notificare (dacă configurată)                         │
│ • Log sumar în audit_log                                        │
│                                                                 │
│ DEPENDENȚE: STEP 8, 9                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

# 5. REGULI DE EROARE

## 5.1 Date Lipsă din daily_metrics

| Situație | Acțiune | Rezultat |
|----------|---------|----------|
| 0 zile cu date | NU se creează snapshot | Log: SKIPPED_NO_DATA |
| 1-3 zile cu date | Se creează snapshot PARTIAL | Flag: INCOMPLETE_DATA, concerns += mesaj |
| 4-6 zile cu date | Se creează snapshot NORMAL | Flag: MINOR_GAPS |
| 7 zile cu date | Se creează snapshot COMPLET | data_completeness = 1.0 |

## 5.2 Cont Inactiv sau Fără Conturi

| Situație | Acțiune | Rezultat |
|----------|---------|----------|
| Client fără conturi active | NU se creează snapshot | Log: SKIPPED_NO_ACCOUNTS |
| Unele conturi inactive | Se agregă doar conturile active | Log: PARTIAL_ACCOUNTS |
| Toate conturile cu sync_error | NU se creează snapshot | Log: SKIPPED_SYNC_ERROR |

## 5.3 KPI-uri Nedefinite

| Situație | Acțiune | Rezultat |
|----------|---------|----------|
| Niciun KPI definit pentru perioadă | kpi_status = {} | Flag: NO_KPIS_DEFINED, concerns += mesaj |
| KPI cu metric necunoscut | Se ignoră acel KPI | Log: UNKNOWN_KPI_METRIC |
| KPI cu target = 0 | achievement = NULL | Flag: INVALID_KPI_TARGET |

## 5.4 Săptămâna Anterioară Fără Date

| Situație | Acțiune | Rezultat |
|----------|---------|----------|
| 0 date prev week | WoW = NULL pentru toate metricile | Flag: NO_PREVIOUS_DATA |
| Date parțiale prev week | WoW se calculează, flag warning | Flag: INCOMPLETE_PREVIOUS |

## 5.5 Erori de Persistare

| Situație | Acțiune | Rezultat |
|----------|---------|----------|
| INSERT/UPDATE fail | RETRY 3x cu backoff (1s, 2s, 4s) | După 3 fails: FAILED |
| Constraint violation | NU retry, FAILED | Log: CONSTRAINT_ERROR |
| Connection timeout | RETRY 3x | După 3 fails: FAILED |

## 5.6 Când NU se creează snapshot

```
SNAPSHOT NU SE CREEAZĂ DACĂ:
├── Client status != 'active'
├── 0 conturi active
├── 0 zile cu date în daily_metrics
├── Toate conturile au sync_error
└── Eroare critică în agregare (div by zero neprotejat, etc.)

SNAPSHOT SE CREEAZĂ CU FLAG-URI DACĂ:
├── Date incomplete (1-6 zile) → PARTIAL
├── KPI-uri nedefinite → NO_KPIS
├── Săptămână anterioară lipsă → NO_PREVIOUS
└── Unele conturi inactive → PARTIAL_ACCOUNTS
```

---

# 6. CE SE LOGHEAZĂ ÎN audit_log

## 6.1 Evenimente de Logat

| Eveniment | action | Când | Detalii în new_values |
|-----------|--------|------|----------------------|
| START_BATCH | INSERT | Începutul procesării batch | {week_start, clients_count, triggered_by} |
| CLIENT_START | INSERT | Începutul procesării unui client | {client_id, week_start} |
| SNAPSHOT_CREATED | INSERT | Snapshot nou creat | {snapshot_id, data_completeness, kpi_count} |
| SNAPSHOT_UPDATED | UPDATE | Snapshot existent actualizat | {snapshot_id, changes[], reason} |
| SNAPSHOT_SKIPPED | INSERT | Snapshot sărit | {client_id, reason, details} |
| SNAPSHOT_FAILED | INSERT | Eroare la creare snapshot | {client_id, error, step_failed} |
| RAG_CREATED | INSERT | Document RAG creat | {rag_id, snapshot_id} |
| RAG_UPDATED | UPDATE | Document RAG actualizat | {rag_id, content_changed} |
| BATCH_COMPLETE | INSERT | Finalizare batch | {success_count, partial_count, failed_count, skipped_count, duration_ms} |
| ANOMALY_DETECTED | INSERT | Anomalie detectată | {client_id, anomaly_type, severity, details} |

## 6.2 Structura Log Entry

```
audit_log record:
├── id: UUID
├── table_name: 'weekly_snapshots' | 'rag_documents' | 'system'
├── record_id: snapshot_id | rag_id | batch_id
├── action: 'INSERT' | 'UPDATE' | 'DELETE'
├── client_id: UUID (dacă aplicabil)
├── user_id: NULL (job automat) | UUID (manual trigger)
├── old_values: JSONB (pentru UPDATE)
├── new_values: JSONB (detalii operație)
└── created_at: TIMESTAMPTZ
```

## 6.3 Exemple Concrete

### Batch Start:
```json
{
  "table_name": "system",
  "record_id": "batch_20240115_083000",
  "action": "INSERT",
  "client_id": null,
  "new_values": {
    "event": "START_BATCH",
    "week_start": "2024-01-08",
    "clients_to_process": 45,
    "triggered_by": "cron",
    "force_regenerate": false
  }
}
```

### Snapshot Created:
```json
{
  "table_name": "weekly_snapshots",
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "INSERT",
  "client_id": "660e8400-e29b-41d4-a716-446655440000",
  "new_values": {
    "event": "SNAPSHOT_CREATED",
    "week": "2024-W02",
    "data_completeness": 1.0,
    "kpi_count": 4,
    "anomalies_count": 1,
    "flags": [],
    "duration_ms": 234
  }
}
```

### Snapshot Skipped:
```json
{
  "table_name": "weekly_snapshots",
  "record_id": null,
  "action": "INSERT",
  "client_id": "770e8400-e29b-41d4-a716-446655440000",
  "new_values": {
    "event": "SNAPSHOT_SKIPPED",
    "week": "2024-W02",
    "reason": "NO_DATA",
    "details": {
      "accounts_checked": 2,
      "days_with_data": 0
    }
  }
}
```

### Batch Complete:
```json
{
  "table_name": "system",
  "record_id": "batch_20240115_083000",
  "action": "UPDATE",
  "client_id": null,
  "old_values": {
    "status": "running"
  },
  "new_values": {
    "event": "BATCH_COMPLETE",
    "status": "completed",
    "success_count": 42,
    "partial_count": 2,
    "failed_count": 0,
    "skipped_count": 1,
    "total_duration_ms": 45230,
    "avg_per_client_ms": 1005
  }
}
```

### Anomaly Detected:
```json
{
  "table_name": "weekly_snapshots",
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "INSERT",
  "client_id": "660e8400-e29b-41d4-a716-446655440000",
  "new_values": {
    "event": "ANOMALY_DETECTED",
    "anomaly_type": "roas_decline",
    "severity": "critical",
    "metric": "roas",
    "current_value": 1.2,
    "previous_value": 2.8,
    "change_percent": -57.1,
    "threshold_exceeded": -30
  }
}
```
