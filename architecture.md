# AKS — Architecture (Engineering Specification)

Companion to **[overview.md](overview.md)** (vision, status, decisions) and **[execution.md](execution.md)** (plan, backlog, risks). This file is the *how and why* of the system. **Every AI and ML component here justifies its existence; every architectural decision states why it exists.**

---

## 1. System architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ 03-frontend — React 18 + Vite 5 + TypeScript                          │
│ Views: Customer eval · Portfolio · Fairness · AKS Assistant           │
│ (Google Stitch design pending — OQ-34)                                │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ REST/JSON (CORS; dev proxy /api → :8000)
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 04-backend — Django 5.2 + Django REST Framework 3.17                  │
│  api/   — 11 endpoints (§10); services.py wraps aks_core              │
│  audit/ — Customer · Assessment · AuditLog (immutable); read-only admin│
│  cache  — Upstash Redis for portfolio/fairness aggregates (TTL 600s)  │
└──────────┬───────────────────────────────────────┬───────────────────┘
           │ import (aks_core)                      │ Django ORM
           ▼                                        ▼
┌────────────────────────────────┐   ┌──────────────────────────────────┐
│ 02-ai-agents / aks_core         │   │ Supabase (Postgres)               │
│  ozellik/  feature extraction   │   │  customers                       │
│  model/    egitim, etiketleme,  │   │  assessments (history)           │
│            aciklama(SHAP),      │   │  audit_log (classic score        │
│            adalet, is_etkisi,   │   │   UNCHANGED + aks score +         │
│            degerlendirme,       │   │   policy note + agents used)     │
│            circularity_ablation │   └──────────────────────────────────┘
│  agents/   veri, skorlama,      │
│            danisman, orkestrator,│   (SQLite + LocMemCache fallback
│            asistan (the 1 agent)│    when no credentials → demo runs
│  artifacts/ model.joblib        │    offline)
└───────────────┬────────────────┘
                │ reads
                ▼
┌────────────────────────────────┐
│ 01-data                         │
│  generator/veri/uretici.py      │
│  datasets/*.csv                 │
└────────────────────────────────┘
```

**Why this shape.** The AI/ML core is an installable package (`aks_core`, `pip install -e`) so the API server and the research/CLI scripts import the *exact same code* — no `from src.*` drift, no divergence between "what's demoed" and "what's evaluated". Django (not FastAPI) is chosen because the audit-trail and Supabase requirements get ORM, migrations, a read-only admin browser, and auth for free; the API surface is thin (DRF views delegating to `services.py`). All external services are optional with graceful fallback because a demo must never depend on network/credentials.

## 2. Component diagram & responsibilities

| Component | Path | Responsibility | Type |
|---|---|---|---|
| Feature extraction | `aks_core/ozellik/cikarim.py` | Raw transactions → 9 behavioral features | Deterministic pure function |
| Labeling | `aks_core/model/etiketleme.py` | Derive default label (synthetic) | Deterministic + injected noise |
| Training | `aks_core/model/egitim.py` | Fit model; classic-score baseline | ML |
| Explainability | `aks_core/model/aciklama.py` | SHAP factors | ML-adjacent |
| Fairness | `aks_core/model/adalet.py` | Equal-opportunity statistics | Deterministic |
| Business impact | `aks_core/model/is_etkisi.py` | Rescued-creditworthy segment sizing | Deterministic |
| Evaluation harness | `aks_core/model/degerlendirme.py` | CV + CI + calibration + per-persona | Deterministic |
| Circularity diagnostic | `aks_core/model/circularity_ablation.py` | Benchmark-validity proof | Deterministic |
| `VeriAgent` | `aks_core/agents/veri_agent.py` | Calls feature extraction | **Not an agent** — pipeline stage |
| `SkorlamaAgent` | `aks_core/agents/skorlama_agent.py` | `predict_proba` + scaling → score/decision | **Not an agent** — scoring service |
| `DanismanAgent` | `aks_core/agents/danisman_agent.py` | Template-fills SHAP into advice | **Not an agent** — deterministic NLG (correct) |
| `Orkestrator` | `aks_core/agents/orkestrator.py` | Sequential coordination + in-memory log | **Not an agent** — orchestration |
| `AsistanAgent` | `aks_core/agents/asistan.py` | Grounded NL Q&A over precomputed context | **The one genuine agent** |

## 3. Data flow (one scoring request)

```
Raw transactions (CSV / demo / user upload)
   │  VeriAgent (feature extraction)
   ▼
9 behavioral features
   │  SkorlamaAgent (model.predict_proba → score 300–850, risk level, decision, suggested limit)
   ▼
AKS score + risk + credit decision + suggested limit (TL)
   │  Aciklayici (SHAP) → DanismanAgent
   ▼
"why this score" explanation + improvement suggestions
   │  Orkestrator (in-memory history + score-change tracking)
   ▼
api/services.py → Django ORM: Assessment (history) + AuditLog (immutable, classic score preserved)
   │  DRF view
   ▼
JSON → React
```

`services.py::_denetim_yaz()` writes both `Assessment` and `AuditLog` **best-effort** — if persistence fails (e.g. no DB), the scoring response is unaffected. The demo never breaks on infrastructure.

## 4. Agent architecture — five-question audit

Applying overview.md §6's five-question test to each "agent":

| Component | Passes? | Verdict & why |
|---|---|---|
| `VeriAgent` | No | Pure deterministic feature extraction. Rename to a pipeline stage in jury-facing material; keep the code. |
| `SkorlamaAgent` | No | `predict_proba` + scaling. A scoring service, not an agent. |
| `DanismanAgent` | No — **and that is correct** | Templated NLG from SHAP. Keep deterministic: this is a regulated-adjacent explanation surface; templated text is more auditable than an LLM. Do **not** add an LLM here without a specific justification. |
| `Orkestrator` | No | Sequential coordinator + log. Orchestration code. |
| `AsistanAgent` | **Yes (all five)** | Solves an open-ended NL interface over fixed facts; classical code can't; an LLM is the right tool; value = user comprehension/trust (measurable via task success + hallucination rate); validated by grounding checks. **Hardening required:** it must never state a number not present in its context (`baglam`); needs a hallucination-rate eval harness before it can be trusted on a compliance-adjacent surface. |
| Fairness audit (`adalet.py`) | N/A | Deterministic equal-opportunity statistics. Do **not** wrap in agent framing. |

**Bottom line:** one real agent (`AsistanAgent`), honestly scoped. This is the stronger research story than an inflated "3–5 agent" narrative.

## 5. Statistical & model pipeline

### 5.1 The circularity finding (why the current benchmark is invalid)

Traced in code, not inferred:

- `etiketleme.py` generates the default label as a sigmoid over `gider_gelir_orani`, `bakiye_trendi`, `gelir_duzenliligi`, `fatura_odeme_duzeni` (+ Gaussian noise std 0.9, stochastic Bernoulli draw; intercept binary-searched to a target default rate). **4 of 9 features causally drive the label.**
- `egitim.py::klasik_risk_skoru` (the "classical baseline") sees only `persona + income volume` — structurally barred from those 4.
- The ML model trains on all 9, including the 4 causal ones, verbatim.

**Consequence:** "behavioral AUC 0.829 vs classical 0.729" is true *by construction* for any model class — a model that sees a variable's causal drivers beats one that cannot. It is **not** evidence of hidden capacity. All downstream numbers (973/1084 rescued; fairness gap 1.00→0.39) inherit this.

**Ablation (`circularity_ablation.py`, 5-fold stratified CV + bootstrap 95% CI):**

| Model | AUC (mean) | 95% CI |
|---|---|---|
| Oracle (Bayes-optimal) | 0.9006 | ceiling |
| XGBoost, 9 features | 0.8525 | [0.833, 0.879] |
| Logistic regression, 9 features | 0.8529 | [0.825, 0.889] |
| Logistic regression, **4 causal features only** | 0.8547 | [0.828, 0.890] |
| Logistic regression, **5 "non-causal" features only** | 0.8235 | [0.795, 0.860] |

Two findings: (a) XGBoost vs 9-feature LR differ by **0.0004 AUC** — its complexity buys nothing; (b) the 5 "non-causal" features *alone* reach 0.82, so the confounding is **structural** (persona-conditioning shapes the whole feature vector jointly), not limited to 4 columns. **The fix cannot be "hide the 4 columns."** It must decouple persona-conditioned feature generation from label generation at the generator level (draw a customer-level latent capacity independently within each persona's plausible range), or move to real data.

### 5.2 Model choice — logistic regression preferred over XGBoost

Evaluation harness (`degerlendirme.py`, 2000 customers, base default rate 0.195):

| Model | ROC-AUC (95% CI) | PR-AUC | Brier | ECE |
|---|---|---|---|---|
| XGBoost (current production) | 0.842 [0.832, 0.853] | 0.698 | 0.098 | 0.032 |
| Logistic regression (9 feats) | **0.852 [0.841, 0.864]** | 0.709 | 0.098 | **0.018** |

LR equals/beats XGBoost on AUC, PR-AUC, and calibration while being simpler (#8), more interpretable (#5), better calibrated (#3). Per the mandate ("classical wins by default"), **LR is the standing recommendation.** The *swap* is deliberately gated on the benchmark fix — optimizing a model against a metric already shown circular would repeat the error. XGBoost reaches only 94.7% of oracle AUC (0.8525/0.9006): consistent with "recovering a roughly-linear generating rule", not "discovering nonlinear structure".

### 5.3 Target definition — Formulation B (the product's spine)

The mission's exact words — *discover hidden capacity the pipeline **fails to recognize***, NOT replace the bank's model, NOT predict default, NOT generate a new score — define a **residual/disagreement problem**: where does behavioral evidence contradict the thin file *in the direction of more capacity*?

| Axis | A: within-segment ranking | **B: calibrated capacity + PD-gap** | C: uplift / reject-inference |
|---|---|---|---|
| Output | PD rank in a thin-file band | Calibrated behavioral PD + gap vs traditional-implied PD | Causal effect of extending credit |
| Offline-evaluable today? | Weakly (within-seg AUC 0.61–0.68) | **Yes** (calibration + incremental-approval-at-fixed-bad-rate) | No (needs experimental data) |
| Regulatory posture | De-facto PD model → heaviest burden; violates "not predict default" | **Supplementary capacity evidence within the bank's policy** | Cutting-edge, hard to explain |
| Mission fit | Partial (it *is* default prediction) | **Strong** | Purest in theory, premature |

**Decision: B now, engineered to graduate into C.** B uses the same calibrated-probability machinery (calibration is already priority #3), reframes the output as a supplementary capacity signal + PD-gap, preserves the "never replace the bank" boundary, and makes **calibration the headline metric**. C is a *graduation, not a rewrite*: B's output (calibrated capacity PD + gap) is exactly the input a champion/challenger pilot needs. Do not attempt C before that experimental data exists.

## 6. Evaluation pipeline

Built as `degerlendirme.py` — model-/data-agnostic, reusable regardless of how OQ-36/37 resolve. Produces: repeated stratified k-fold, bootstrap 95% CIs on ROC-AUC/PR-AUC, Brier score, ECE, reliability curve, and **per-persona subgroup breakdown**.

**Per-persona finding (why aggregate AUC misleads):**

| Persona | XGBoost AUC | LR AUC | n | Read |
|---|---|---|---|---|
| `dusuk_hacim_riskli` (negative control) | 0.898 | 0.883 | 301 | Easy task — separates the genuinely risky |
| `klasik_maasli` (prime baseline) | 0.710 | 0.721 | 608 | Moderate |
| `stajyer_degisken_gelir` (target) | 0.716 | 0.790 | 497 | Moderate |
| **`ogrenci_yuksek_hacim` (PRIMARY target)** | **0.681** | **0.615** | 594 | **Weak — the segment the thesis is about** |

The 0.84 aggregate is carried by cleanly separating the negative-control group — which is (a) the confounded between-persona separation, and (b) *not the product's job*. Rigor caveat: within-persona AUC is partly depressed by narrower feature spread, so 0.61 ≠ directly comparable to 0.84. The defensible claim: *the aggregate advertises a capability demonstrated mostly on the group the product doesn't need to help.*

**Pre-registered evaluation design for Formulation B (fix numbers X, Y before results land):**
- **Baseline:** traditional-band-only approval to a fixed bad-rate budget.
- **Primary metric:** incremental approval rate at fixed bad-rate on the thin-file subpopulation (a point on the combined-policy decision curve), bootstrap 95% CI.
- **Secondary:** per-segment ECE/Brier (calibration), stability across time/folds (robustness), reason-code coverage (interpretability).
- **Acceptance:** ≥ X% incremental approvals at ≤ baseline bad rate, ECE ≤ Y on thin-file, CIs excluding zero.
- **Proving ground:** a real dataset with outcomes. **Home Credit Default Risk (Kaggle)** is the strongest candidate (bureau + behavioral + application data, documented thin-file population, real outcomes). Honest caveat: approved-only outcomes are themselves selected (the selective-labels problem is the field's core difficulty, not a flaw we introduced).

## 7. Feature engineering pipeline

`aks_core/ozellik/cikarim.py` → `OZELLIK_ADLARI` (9 features): `toplam_gelir_hacmi`, `toplam_gider_hacmi`, `gelir_islem_sayisi`, `gelir_kaynagi_sayisi`, `gelir_duzenliligi`, `gider_gelir_orani`, `bakiye_trendi`, `fatura_odeme_duzeni`, `hesap_hareket_yogunlugu`. Pure deterministic function of raw transactions. **Gaming-resistance is an open research task (RQ-3):** of the 4 label-causal features, which are user-manipulable (e.g. can a customer structure transfers to inflate `gelir_duzenliligi`)? A production capacity signal must be robust to strategic behavior.

## 8. Explainability & fairness

- **Explainability:** SHAP factors per score (`aciklama.py`), template-filled into advice by `DanismanAgent`. **Planned:** monotonic constraints aligned with domain priors (e.g. `gider_gelir_orani` ↑ ⇒ risk ↑) so a feature's effect cannot flip sign in ways hard to defend to a regulator, and standardization of SHAP output into **adverse-action-style reason codes**.
- **Fairness:** `adalet.py` computes equal-opportunity statistics (approval rate of creditworthy customers across groups), exposed at `/api/adalet`. The model uses no discriminatory signals (age, gender) directly — only behavioral/financial features. **Caveat:** the current fairness numbers (0.4%→97.8%, gap 1.00→0.39) inherit the §5.1 circularity — persona is a confounder correlated with the label's causal features; the "improvement" is the same circularity through a demographic lens, not an independent finding.

## 9. Policy layer & audit layer (the boundary, in code)

The boundary from overview.md §7 is operationalized here — it *is* the architecture, not a note.

`product/04-backend/audit/models.py`:

| Model | Purpose | Critical fields |
|---|---|---|
| `Customer` | Demo customer identity + persona | `external_id`, `persona` |
| `Assessment` | Full record of each scoring (history / `/gecmis`) | `klasik_skor`, `aks_skor`, `risk_seviyesi`, `karar`, `onerilen_limit`, `ozellikler` (JSON), `kaynak` |
| `AuditLog` | **Immutable** audit row; read-only in Django admin | `klasik_skor` (annotated "**UNCHANGED**"), `aks_skor`, `politika_notu` (default: *"AKS is complementary; the bank's segment/score was not changed."*), `ajanlar` (agents used), `kaynak`, `created_at` |

Django admin sets `has_change_permission = has_delete_permission = False` on `AuditLog`. Nothing in the request path can mutate the bank's segment: `SkorlamaAgent` only emits the *complementary* score + a within-policy limit suggestion; the classic score is read-only input.

## 10. API architecture

Base `http://localhost:8000/api`. DRF views in `product/04-backend/api/views.py`; JSON bodies (except CSV upload = multipart).

| Method | Path | Purpose |
|---|---|---|
| GET | `/bilgi` | Service info: model name, feature list, demo count |
| GET | `/demo-musteriler?adet_per_persona=3` | Sample customer IDs per persona |
| GET | `/skorla/{musteri_id}` | Score a demo customer (writes audit row, `kaynak="demo"`) |
| POST | `/skorla` | Score from raw transactions (audit, `kaynak="api"`) |
| POST | `/aciklama` | SHAP factor explanation |
| POST | `/simulasyon` | "What-if" — effect of feature changes on the score |
| GET | `/portfoy?...` | Portfolio analysis: rescued creditworthy segment + illustrative revenue (**Redis cache, TTL 600s**) |
| GET | `/adalet?...` | Equal-opportunity fairness report (**Redis cache, TTL 600s**) |
| POST | `/csv-skorla` | Score a user's own statement CSV (multipart; audit, `kaynak="csv"`) |
| POST | `/asistan` | Ask the AKS Assistant (Gemini or rule-based) |
| GET | `/gecmis/{musteri_id}` | Persisted assessment history (DB; falls back to orchestrator memory) |

## 11. Database & infrastructure

- **Database:** Supabase (Postgres) via Django ORM. `DATABASE_URL` unset → local SQLite (`aks_dev.sqlite3`). `python manage.py check_connections` reports live-vs-fallback for both DB and cache.
- **Cache:** Upstash Redis via `django-redis` (`rediss://` TLS). `REDIS_URL` unset → Django `LocMemCache`. Caches the heavy `/portfoy` & `/adalet` aggregates (they re-score *all* customers per call) and rate-limits the LLM assistant.
- **Secrets contract (`.env`, never committed; `.env.example` documents it):** `GEMINI_API_KEY`, `DATABASE_URL`, `SUPABASE_URL/ANON_KEY/SERVICE_ROLE_KEY`, `REDIS_URL`, `DJANGO_SECRET_KEY/DEBUG/ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `AKS_DATA_DIR`, `AKS_MODEL`. **All optional** — empty → SQLite + LocMem + rule-based assistant.

## 12. Deployment

Target: Docker + Render, Django serving the built React bundle as a single web service; Supabase + Upstash hosted. Each migration step lands as its own commit for independent rollback. The old FastAPI `Dockerfile`/`render.yaml` in `product/04-backend/_legacy_fastapi/` is **reference only, not live**. Deployment config is updated *after* the Google Stitch design integrates (OQ-34) and Supabase/Upstash credentials exist (OQ-35). **Priority note:** the entire stack/deploy track is priority #8 — it is production-ready and *not* the bottleneck; it is intentionally not pushed further until the #1–#3 research items (§5) are addressed.

## 13. Future architecture ideas

- **Real-data path (OQ-36):** if Home Credit / LendingClub / open-banking data is available, demote the synthetic generator to unit-test fixtures and make real outcomes the benchmark.
- **Simulator redesign (A2):** if staying synthetic, rebuild `uretici.py` so a *calibratable* behavioral capacity signal exists and diverges from a traditional-thin signal for a knowable subpopulation — with persona **not** determining both features and label.
- **Second genuine agent (OQ-38, optional):** the most plausible candidate is an explanation/recommendation *ranker* doing genuine constrained optimization over candidate interventions (not template lookup) — only if it passes the five-question test.
- **Calibration layer:** isotonic/Platt on top of the base model, per-segment.
- **Drift monitoring:** PSI-based hook wired into `Orkestrator`'s score-over-time tracking.
- **Optimization pipeline:** convert the calibrated capacity PD + PD-gap into a policy engine that recommends the maximal within-policy limit at a fixed portfolio bad-rate — the productized decision-curve output.
