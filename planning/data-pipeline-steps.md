# AKS — Data Pipeline Steps

The ordered steps that turn raw input into a scored, audited, calibrated decision — and the guardrails at each step. Implements [`data-architecture.md`](data-architecture.md) and [`feature-schema.md`](feature-schema.md). Each step names the product folder that owns it and the task ID from [`../execution.md`](../execution.md).

Legend: 🟢 exists today · 🟡 extend · 🔴 new. Gate = a check that must pass before the next step runs.

---

## The pipeline

```
[1] Ingest ──► [2] Validate/normalize ──► [3] Feature engineering ──► [4] Labeling
                                                │ (feature_store)          │ (etiketler)
                                                ▼                          ▼
[8] Persist+Audit ◄── [7] Score+Explain ◄── [6] Evaluate (GATE) ◄── [5] Train+Calibrate
        │
        ▼
[9] Monitor (drift / early-warning / gaming)
```

### Step 1 — Ingest 🟡 · `01-data` (#19)
- Sources: transactions (synthetic now; real via OQ-36), later open-banking API (T1), CSV upload (exists).
- Write raw rows to `islemler` with governance columns (`kaynak`, `alindigi_zaman`, `kvkk_sinifi`, `yasal_dayanak`, `riza_id`).
- **Gate:** any `acik_riza`-basis column requires an active `Consent` row, else the column is dropped, not defaulted.

### Step 2 — Validate & normalize 🔴 · `01-data` (#19)
- Schema/type validation, dedupe, currency normalization (`para_birimi`), category canonicalization.
- **PII tagging** stamped per column; retention deadline (`saklama_bitis`) set.
- **Gate:** reject/quarantine malformed rows; never silently coerce.

### Step 3 — Feature engineering 🟡 · `02-ai-agents` (#20)
- Compute the §2 feature set (T0 now; T1 when available) into a **versioned** `feature_store` row.
- **Point-in-time rule:** only use `islemler` with `tarih` before the outcome window start.
- **Gate (anti-circularity firewall):** deny-list check — assert no feature column is derived from any `etiketler` column. Fail the build if violated.

### Step 4 — Labeling 🔴 · `01-data` (#19)
- Produce `temerrut_gerceklesen` from **real outcomes** (preferred) or a **decoupled generator** (persona must not determine both features and label — architecture.md §5.1).
- Attach `outcome_penceresi`; enforce a time lag between features and outcome.
- **Gate (M4):** modeling may not proceed until this label is demonstrably non-circular (re-run `circularity_ablation.py`; XGB-vs-LR gap and non-causal-subset AUC must move toward chance).

### Step 5 — Train & calibrate 🟡 · `02-ai-agents` (#20)
- Fit the model; produce **Formulation B** outputs: `pd_davranissal`, then overlay `pd_geleneksel_bant` → `pd_fark`, `kapasite_sinyali`.
- **Per-segment calibration** (isotonic/Platt) → `calibration_ece_segment`, `calibration_version`.
- Prefer logistic regression over XGBoost until a non-circular benchmark says otherwise (architecture.md §5.2).

### Step 6 — Evaluate 🟢→🟡 · `02-ai-agents` (#20) — **THE GATE**
- Reuse `degerlendirme.py`: repeated stratified k-fold + bootstrap CI, per-persona breakdown, Brier/ECE, reliability.
- **Primary metric:** incremental-approval-at-fixed-bad-rate on the thin-file subpopulation, with pre-registered acceptance thresholds (execution.md R12).
- **Gate:** if the pre-registered thresholds are not met, **"no-go is a valid outcome"** — do not ship the model; report it.

### Step 7 — Score & explain 🟢→🟡 · `02-ai-agents` (#20) + `04-backend` (#21)
- O(1) feature-store lookup → score → SHAP → **adverse-action-style reason codes** (execution.md E3).
- Emit `kapasite_sinyali`, `pd_fark`, and a **within-policy** limit suggestion only.
- **Boundary gate:** the classic score is read-only; no stage writes it.

### Step 8 — Persist & audit 🟢→🟡 · `04-backend` (#21)
- Write `Assessment` (+ new Formulation-B fields) and the **immutable** `AuditLog` (+ `karar_kaynagi`, `itiraz_durumu`, `yasal_dayanak`, `riza_id`).
- Best-effort write must never break scoring (existing pattern).
- **Human-oversight gate:** an adverse automated decision is contestable → routes to a human who can override (KVKK Art. 11).

### Step 9 — Monitor 🔴 · `02-ai-agents` (#20) + `05-business` (#23)
- **Drift:** PSI on features + score over time (hook into `Orkestrator` score history).
- **Early-warning (T2, monitoring-only):** `zorluk_sayfasi_erisimi` → pre-delinquency flag, never an origination feature.
- **Gaming (RQ-3):** watch the high-gaming-risk features (`gelir_duzenliligi`, `fatura_odeme_duzeni`) for manipulation patterns.

## Cross-cutting governance · `05-business` (#23), runs alongside every step
- **Hypothesis registry:** every column cites a hypothesis before it may be populated (data minimization).
- **Lawful-basis mapping + DPIA** before any T1/T2/T3 column goes live.
- **Out-of-scope register:** RL limit optimization, psychometrics, dense device metadata, blockchain — recorded as rejected/deferred with reasons (data-architecture.md §6).

## Ordering & gates summary

| Step | Owner | Task | Blocking gate |
|---|---|---|---|
| 1 Ingest | 01-data | #19 | consent present for `acik_riza` columns |
| 2 Validate | 01-data | #19 | reject malformed; PII tagged |
| 3 Features | 02-ai-agents | #20 | **anti-circularity deny-list** |
| 4 Labeling | 01-data | #19 | **M4 non-circular label** |
| 5 Train/calibrate | 02-ai-agents | #20 | per-segment calibration produced |
| 6 Evaluate | 02-ai-agents | #20 | **pre-registered thresholds (no-go valid)** |
| 7 Score/explain | 02/04 | #20/#21 | **boundary: classic score read-only** |
| 8 Persist/audit | 04-backend | #21 | **human-oversight contestability** |
| 9 Monitor | 02/05 | #20/#23 | drift/gaming alarms wired |

**Everything downstream of Step 4 stays blocked on the non-circular benchmark (execution.md M4 / OQ-36).** Building richer features or a fancier model on top of a circular label would repeat the exact error the mandate exists to prevent.
