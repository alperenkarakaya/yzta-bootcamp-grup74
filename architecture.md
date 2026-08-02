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
| Anomaly/OOD detection | `aks_core/model/anomali.py` | Flags profiles outside the training distribution (§5.4) | Unsupervised ML, auxiliary — never changes score/decision |
| Segmentation | `aks_core/model/segmentasyon.py` | Unsupervised persona discovery, offline report (§5.5) | Unsupervised ML, research — not wired to any decision path |
| Risk appetite policies | `aks_core/model/risk_istahi.py` | 3-tier bank recommendation from target bad-rate (§5.6) | Deterministic, held-out benchmark |
| Document pipeline | `aks_core/belge/` | PDF/XLSX/CSV → canonical transaction schema (§5.7) | Deterministic, format-agnostic |
| `VeriAgent` | `aks_core/agents/veri_agent.py` | Calls feature extraction | **Not an agent** — pipeline stage |
| `SkorlamaAgent` | `aks_core/agents/skorlama_agent.py` | `predict_proba` + scaling → score/decision | **Not an agent** — scoring service |
| `DanismanAgent` | `aks_core/agents/danisman_agent.py` | Template-fills SHAP into advice | **Not an agent** — deterministic NLG (correct) |
| `Orkestrator` | `aks_core/agents/orkestrator.py` | Sequential coordination + in-memory log | **Not an agent** — orchestration |
| `AsistanAgent` | `aks_core/agents/asistan.py` | Grounded NL Q&A over precomputed context (Gemini-optional/rule fallback) | Genuine agent — now the fallback path behind `danisman_llm` (§4) |
| `BelgeAgent` | `aks_core/agents/belge_agent.py` | Multi-strategy document parsing with self-check + trace (§4, §5.7) | **Genuine agent** |
| Danışman LLM agent | `aks_core/agents/danisman_llm.py` | Claude **or Gemini** tool-calling over 5 grounded tools; verifies its own numbers (§4) | **Genuine agent** — preferred path when either `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` is set (Claude takes priority if both) |

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
| `AsistanAgent` | **Yes (all five)** | Solves an open-ended NL interface over fixed facts; classical code can't; an LLM is the right tool; value = user comprehension/trust (measurable via task success + hallucination rate); validated by grounding checks. Now the fallback implementation behind `services.asistan_yanit()` only when **neither** `ANTHROPIC_API_KEY` **nor** `GEMINI_API_KEY` is set (execution.md §3b Phase 7/7.10) — its own Gemini enrichment path (`gemini_fonksiyonu`) is effectively superseded by `danisman_llm`'s Gemini tool-calling path whenever a key is present, but kept as-is for the fully-keyless case. |
| `BelgeAgent` (execution.md §3b Phase 7/7.5) | **Yes (all five)** | Goal: turn an arbitrary uploaded file into a scorable transaction list. Tries multiple strategies (format-specific reader; for PDF, table-extraction then text-regex, in order); self-checks its own output (quality flags, minimum-row threshold) rather than trusting the first parse; leaves a step-by-step trace (`meta["iz"]`) a human can audit; a classical fixed pipeline can't branch on "did strategy 1 actually work" the way this does. Deterministic (no LLM) — being agentic doesn't require an LLM; it requires a goal, strategy selection, self-monitoring, and traceability, all of which this has. |
| Danışman LLM agent (`danisman_llm.py`, execution.md §3b Phase 7/7.5, §7.10) | **Yes (all five)** | Solves the same open-ended NL interface as `AsistanAgent` but via genuine tool-calling (Claude **or Gemini**, 5 grounded tools: `skor_getir`/`faktor_getir`/`politika_getir`/`senaryo_calistir`/`gecmis_getir`) instead of one prompt with everything pre-embedded — the model *chooses* which facts it needs. **Hardening implemented, not just planned:** (1) `aks_skor`/`karar`/`onerilen_limit` in the API response always come from `SkorlamaAgent`, never from the LLM; (2) post-response verification (`_dogrula`) rejects any reply containing a number absent from its own tool outputs (the AKS 300/850 scale and natural-language counts ≤12 are allow-listed), falling back to the deterministic rule engine (`anlati_reddedildi=True`) rather than surface an unverified number — **identical guard for both providers**, provider-agnostic by construction. This is the hallucination guard `AsistanAgent`'s row above says is still needed — implemented here, not yet ported back onto `AsistanAgent` itself. Provider priority: Claude if `ANTHROPIC_API_KEY` set, else Gemini if `GEMINI_API_KEY` set, else `AsistanAgent` fallback (zero regression). Response carries a `saglayici` field (`"anthropic"\|"gemini"\|"kural"`) for traceability. **Live end-to-end verified for Gemini** (§7.10: real `POST /api/asistan` call, model genuinely invoked `faktor_getir`/`skor_getir`, all numbers in the reply traced back to tool output); Claude side still unit-tested-only (mocked client), live verification remains OQ-48. |
| Fairness audit (`adalet.py`) | N/A | Deterministic equal-opportunity statistics. Do **not** wrap in agent framing. |

**Bottom line:** three genuine agents now (`AsistanAgent`, `BelgeAgent`, the Claude/Gemini tool-calling danışman), honestly scoped — up from one. `VeriAgent`/`SkorlamaAgent`/`DanismanAgent`/`Orkestrator` remain correctly labeled as pipeline stages, not agents; renaming them in jury-facing material (vs. keeping the code names for backward compatibility) is still an open framing decision (OQ-38) — this cycle added real agentic capability rather than resolving the narrative question.

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

**Status: this fix is now built and the production training path uses it** (execution.md §3b Phase 1, U1). `egitim.py::egit()` defaults to `veri_kaynagi="dekuple"`, reading `01-data/generator/veri/uretici_kapasite.py`'s already-built decoupled dataset (`kapasite_islemler.csv` + `kapasite_etiketleri.csv`, read-only). `circularity_ablation.py --veri-kaynagi hepsi` reproduces both the table above (old, circular) *and* the new one back to back as proof, not assertion — on the decoupled data the classic-score baseline's AUC collapses to **0.493** (chance), directly confirming the thin-file blind spot claim non-circularly. This is a synthetic honest-fallback, not real data (OQ-36 remains open).

### 5.2 Model choice — logistic regression preferred over XGBoost

**Status: swap executed (execution.md §3b Phase 1, U8).** The numbers below are the *old, circular-benchmark* comparison — kept for the historical record of why LR was already the standing recommendation before the fix landed:

Evaluation harness (`degerlendirme.py`, 2000 customers, base default rate 0.195, **circular label**):

| Model | ROC-AUC (95% CI) | PR-AUC | Brier | ECE |
|---|---|---|---|---|
| XGBoost (former production) | 0.842 [0.832, 0.853] | 0.698 | 0.098 | 0.032 |
| Logistic regression (9 feats) | **0.852 [0.841, 0.864]** | 0.709 | 0.098 | **0.018** |

**On the non-circular (decoupled) benchmark** — `python -m aks_core.model.degerlendirme --veri-kaynagi dekuple`, same harness, 2000 customers, base default rate 0.172:

| Model | ROC-AUC (95% CI) | PR-AUC | Brier | ECE |
|---|---|---|---|---|
| XGBoost | 0.840 [0.831, 0.850] | 0.557 | 0.105 | 0.034 |
| Logistic regression (9 feats) | **0.862 [0.853, 0.871]** | **0.610** | **0.098** | **0.014** |

The CIs **do not overlap** — LR is now the genuinely better model on a valid benchmark, not just a tie-breaker by simplicity. LR equals/beats XGBoost on AUC, PR-AUC, and calibration while being simpler (#8), more interpretable (#5), better calibrated (#3). **Production model is now `LogisticRegression`** (`aks_core/artifacts/aks_model_meta.json`, format `logistic_joblib` — a fitted `StandardScaler` is persisted alongside it, since LR trains on standardized features; see `kayit.py::OlcekliLojistikSarmalayici`). XGBoost reached only 94.7% of the *old* oracle AUC (0.8525/0.9006): consistent with "recovering a roughly-linear generating rule", not "discovering nonlinear structure" — the new benchmark's oracle ratio (XGBoost 0.845/0.909 = 93.0%) tells the same story.

**Calibration correction (U9):** a test-set ECE of 0.0391 (pre-hyperparameter-search LR, held-out split) triggered the pre-registered isotonic-correction threshold (0.03); an OOF-fit isotonic layer was applied and persisted (`kayit.py::KalibreliModel`, `artifacts/kalibrasyon.json`). Honest result: ECE moved from 0.0391 to 0.0394 on that particular holdout — essentially flat, not a meaningful improvement. Likely cause: small test set (n=500) makes binned ECE noisy at this scale, and the base model was already close to well-calibrated. Reported as-is per the anti-goal-seeking mandate (the threshold was fixed before the run; the result isn't hidden or re-tuned after the fact).

### 5.3 Target definition — Formulation B (the product's spine)

The mission's exact words — *discover hidden capacity the pipeline **fails to recognize***, NOT replace the bank's model, NOT predict default, NOT generate a new score — define a **residual/disagreement problem**: where does behavioral evidence contradict the thin file *in the direction of more capacity*?

| Axis | A: within-segment ranking | **B: calibrated capacity + PD-gap** | C: uplift / reject-inference |
|---|---|---|---|
| Output | PD rank in a thin-file band | Calibrated behavioral PD + gap vs traditional-implied PD | Causal effect of extending credit |
| Offline-evaluable today? | Weakly (within-seg AUC 0.61–0.68) | **Yes** (calibration + incremental-approval-at-fixed-bad-rate) | No (needs experimental data) |
| Regulatory posture | De-facto PD model → heaviest burden; violates "not predict default" | **Supplementary capacity evidence within the bank's policy** | Cutting-edge, hard to explain |
| Mission fit | Partial (it *is* default prediction) | **Strong** | Purest in theory, premature |

**Decision: B now, engineered to graduate into C.** B uses the same calibrated-probability machinery (calibration is already priority #3), reframes the output as a supplementary capacity signal + PD-gap, preserves the "never replace the bank" boundary, and makes **calibration the headline metric**. C is a *graduation, not a rewrite*: B's output (calibrated capacity PD + gap) is exactly the input a champion/challenger pilot needs. Do not attempt C before that experimental data exists.

**Status: instrumented in `aks_core.model.formulasyon_b`** (execution.md §3b Phase 1, U10). `pd_geleneksel_bant` is fit as an isotonic (monotonic-decreasing) mapping from classic score → *empirical* observed default rate on the training split (not a formula); `pd_fark = pd_geleneksel_bant − pd_davranissal`; `kapasite_sinyali` is a simple 0–100, 50-neutral linear rescaling of `pd_fark` (documented as a v1 approximation, not a calibrated probability itself). `SkorlamaAgent.calistir()` accepts an optional `klasik_skor` argument and returns these fields when provided; wiring `klasik_skor` through from the backend (which already computes it) is Phase 2 (§3b, U17) — not yet done, so the API doesn't surface these fields yet.

### 5.4 Anomaly / out-of-distribution detection (unsupervised, auxiliary)

**Status: instrumented in `aks_core.model.anomali`** (execution.md §3b Phase 4, U25). An `IsolationForest` (`n_estimators=200`, `contamination=0.05`) is fit on the same train split `egit()` already uses — no leakage, same OOF discipline as calibration/Formulation B. Persisted portably via joblib (pure sklearn/NumPy state, no XGBoost-style C++ buffer issue). `SkorlamaAgent.calistir()` loads it optionally (`None` if the artifact is absent — scoring is never blocked by its absence) and emits `anomali_bayrak`/`anomali_skoru` alongside the score.

**Why this exists (five-question test, overview.md §6):** not an agent — a deterministic auxiliary statistical component in the same category as SHAP (`aciklama.py`). **What it answers that SHAP doesn't:** SHAP explains *why* a score came out a given way assuming the model's fit is trustworthy for this input; the anomaly detector answers a prior question — *is this input even the kind of thing the model was fit on*. **Boundary (overview.md §7), explicitly re-verified:** this signal is additive-only — it cannot and does not modify `aks_skor`, `karar`, or `klasik_skor`; it is surfaced purely for human judgment (e.g. "trust this score a bit less").

### 5.5 Unsupervised segmentation (research, not decision-facing)

**Status: instrumented in `aks_core.model.segmentasyon`** (execution.md §3b Phase 4, U26). K-Means, sweeping k=2..6 and selecting by silhouette score, run over the 9 behavioral features (standardized). Produces an offline report (`artifacts/segmentasyon_raporu.json`), served read-only via `GET /api/segmentasyon` — same "generated artifact, 503 until produced" pattern as `/api/metrikler`. **Explicitly not wired into any scoring or decision path** — same category as `is_etkisi.py`/`degerlendirme.py`: a research script, not a pipeline stage.

**Why this exists:** the product's 4 personas (`klasik_maasli` etc.) are a label baked in by the synthetic generator, not something discovered from behavior. This asks whether unsupervised clustering on the same 9 features the model actually sees would rediscover those groups (validating that the personas correspond to real behavioral structure) or not (a sign the personas are more of a narrative convenience than a behavioral reality).

**Finding on the current synthetic/dekuple dataset, reported honestly (not smoothed over):** k=3 was selected (silhouette 0.389 — moderate, not sharp separation). `ogrenci_yuksek_hacim` (590/590) and mostly `klasik_maasli` (579/582) are cleanly recovered, but **`stajyer_degisken_gelir` and `dusuk_hacim_riskli` collapse into one cluster** — the 9 behavioral features alone do not cleanly distinguish these two personas. Per-cluster empirical default rates are also nearly flat (16.8–17.5%), so this clustering doesn't separate risk either. Consistent with "no-go is a valid outcome": this is reported as a real limitation of the current feature set/synthetic data, not cherry-picked. Not yet re-run on real data (OQ-36 still open).

### 5.6 Risk appetite policies — 3-tier bank recommendation

**Status: instrumented in `aks_core.model.risk_istahi`** (execution.md §3b Phase 7/7.4). PO's ask: give banks a **risksiz / orta / riskli** (3-tier) recommendation rather than one fixed decision band. Each tier is defined by a **target bad rate**, not an arbitrary score cut: `ihtiyatli` ≤3%, `dengeli` ≤6%, `atak` ≤10%.

**Method (no leakage, genuinely held-out):** reproduces `egitim.py::egit()`'s exact `train_test_split` (`seed=42`, `test_size=0.25`, `stratify=y`) on the decoupled dataset — since the split is deterministic given the same data ordering, this recovers the identical held-out set the production model never trained on, without needing to persist split indices separately. For each candidate AKS threshold, computes approval rate, realized bad rate, and expected profit/loss using the **same illustrative assumptions as `is_etkisi.py`** (ort_kredi=25000 TL, getiri_orani=0.12, zarar_orani=0.55 — deliberately the same numbers, so the two modules aren't quietly assuming different economics). For each tier, picks the threshold that maximizes expected profit among thresholds satisfying the bad-rate target; bootstraps a 95% CI on both the approval rate and the realized bad rate.

**Runs only on `veri_kaynagi="dekuple"`** — the function raises `ValueError` on the circular dataset rather than silently producing a number, because "target bad rate" is only meaningful against a genuine outcome label.

**Result on the current synthetic/dekuple benchmark** (n_test=500): ihtiyatlı threshold 835 (realized bad rate 2.8%, approval 35.4%), dengeli threshold 760 (5.0%, 60.2%), atak threshold 690 (7.5%, 79.6%) — monotonic in the expected direction, all three respecting their target.

**Surfaced two ways:** `GET /api/risk-istahi` (the full report) and, per customer, embedded in `GET /api/kimlik/kurum/musteri/<aks_no>` (institution-side, consent-gated — §9c) — the latter only *compares* a given score against the persisted thresholds, it does not re-run the benchmark per request. Carries the same honesty caveat as `_METRIK_UYARISI`: synthetic/decoupled data, held-out but not real-world, not a validated bank policy (OQ-50: should these targets/assumptions become bank-configurable?).

### 5.7 Document processing pipeline (PDF/Excel/CSV → model)

**Status: instrumented in `aks_core.belge` + `aks_core.agents.belge_agent`** (execution.md §3b Phase 7/7.1, 7.5). Turns an uploaded statement — CSV, XLSX, or PDF — into the canonical transaction schema `ozellik_cikar()` already expects: `{tarih, islem_tipi, kategori, tutar, aciklama}`. Modules: `okuyucu.py` (format router), `pdf_okuyucu.py` (pdfplumber — table extraction first, regex-over-text fallback second), `tablo_okuyucu.py` (pandas/openpyxl, fuzzy column matching for real bank-statement headers vs. the product's own simple CSV template), `normalizer.py` (canonicalization + a per-row category-confidence score), `parmak_izi.py` (content fingerprint, §9c), `kalite.py` (quality/fit report). `BelgeAgent` (§4) wraps this with strategy selection + self-checking + a human-readable trace; `04-backend`'s `services.belge_ayristir()` calls the agent, not the low-level `okuyucu.ayristir()` directly.

**Two risks identified and mitigated, not glossed over:**
1. **Category dependency.** 2 of the model's 9 features (`gelir_kaynagi_sayisi`, `fatura_odeme_duzeni`) are computed directly from the `kategori` field. A document without an explicit category column (most real bank PDFs) falls back to keyword-based category inference, which is necessarily less reliable than a user-supplied category — `normalizer.py` scores this per row and surfaces the average as `kategori_guveni`; below 0.6 triggers a `dusuk_kategori_guveni` flag alongside the score, not a silent best-guess.
2. **Window mismatch.** The model was trained assuming a ~180-day transaction window (`fatura_odeme_duzeni`'s `/6.0` normalization, `limit_oner()`'s 6-month assumption). A shorter uploaded statement doesn't match that assumption, and **`ozellik_cikar()` was deliberately left unchanged** (train/serve consistency is priority #1) rather than patched ad hoc for this one input path. `kalite.py` instead flags `pencere_uyumsuz` when the observed window deviates >35% from 180 days — verified live at a 47-day statement. A proper fix requires retraining across variable/normalized windows (OQ-52), not a frontend workaround.

Content fingerprinting (`parmak_izi.py`, SHA-256 over the sorted, canonicalized `(tarih, islem_tipi, kategori, tutar)` tuples — deliberately excluding free-text `aciklama`, which can differ slightly across extraction methods for the same underlying document) feeds the ownership-conflict detection in §9c.

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

`aks_core/ozellik/cikarim.py` → `OZELLIK_ADLARI` (9 features): `toplam_gelir_hacmi`, `toplam_gider_hacmi`, `gelir_islem_sayisi`, `gelir_kaynagi_sayisi`, `gelir_duzenliligi`, `gider_gelir_orani`, `bakiye_trendi`, `fatura_odeme_duzeni`, `hesap_hareket_yogunlugu`. Pure deterministic function of raw transactions.

**Gaming-resistance (RQ-3) — first quantitative answer, execution.md §3b Phase 5 (R11):** of the 4 label-causal features, `gider_gelir_orani` (expense/income ratio) is disproportionately gameable — a fixed 25% "improvement" on this one feature alone buys an average **+73 AKS points** (p90 **+265**), versus +6/+1/−2 for `fatura_odeme_duzeni`/`bakiye_trendi`/`gelir_duzenliligi` respectively. This is a real, unresolved robustness risk (OQ-45, execution.md §8), not a closed question — a production capacity signal must be robust to strategic behavior, and right now the model's single most-leaned-on lever is also its most plausibly manipulable one.

## 8. Explainability & fairness

- **Explainability:** SHAP factors per score (`aciklama.py`), template-filled into advice by `DanismanAgent`, and surfaced as reason codes on the institution's decision surface (`/kimlik/kurum/musteri/{aks_no}` → `services.aciklama_yeniden_uret()`, recomputed from the persisted feature vector since `Assessment` stores features rather than SHAP output).
- **The sign-flip risk below is not hypothetical — it already bit us.** `ONERI_HARITASI` encoded a fixed "increase this feature" assumption per factor, but the decoupled-data LogisticRegression learned the *opposite* sign for two of them (`gelir_kaynagi_sayisi` +1.0995, `gelir_duzenliligi` +0.2361 — both raise risk as they increase). The product therefore advised users to do the very thing its own model penalized, and `gelir_kaynagi_sayisi` was the **top risk driver** on a real example statement. Two more features with large coefficients (`toplam_gider_hacmi` +0.9312, `gelir_islem_sayisi`) had no advice at all. Fixed in execution.md §3b Phase 7/7.8: the map now stores `(direction, text)`, gives no directional advice where the learned direction is not defensible as behavioral guidance, and **`tests/test_danisman_yon.py` asserts every direction against the trained model's coefficient sign** — a retrain that flips a sign now fails the suite instead of silently shipping wrong advice.
- **Still planned:** monotonic constraints aligned with domain priors (e.g. `gider_gelir_orani` ↑ ⇒ risk ↑) so a feature's effect cannot flip sign at all, and standardization of SHAP output into **adverse-action-style reason codes**.
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

## 9b. User portal & authentication (execution.md §3b Phase 6)

Two interfaces on one Django backend, one React app: the bank UI (routes under `Layout`, no login, internal tool) and the user portal (`/portal/*`, under `PortalLayout`, session-gated). They share the scoring pipeline (`services.degerlendir()` → same `aks_core` orchestrator) but nothing else — no shared nav, no shared session state, no page in either interface links into the other's protected pages.

**Auth: Django's own `django.contrib.auth`, session-based** (OQ-33 resolved for this scope; Supabase Auth would need credentials that are still blocked, OQ-35). `django.contrib.auth.models.User` used directly — `username` = email, no custom user model. Passwords hashed with Django's default PBKDF2; `AUTH_PASSWORD_VALIDATORS` enforces an 8-character minimum (was empty before this phase).

**CSRF, the part that isn't obvious:** DRF's `SessionAuthentication` enforces a CSRF token match on every state-changing request once a session exists (Django's blanket `CsrfViewMiddleware` is bypassed for DRF views — DRF does its own check instead). The frontend calls `GET /api/auth/ben` on load (decorated `@ensure_csrf_cookie`) to guarantee the `csrftoken` cookie exists, then reads it and sends it back as `X-CSRFToken` on every POST. Separately, Django 4+ also validates the request's `Origin` header against `CSRF_TRUSTED_ORIGINS` — this bit 403'd every authenticated POST during dev testing even with a correct token, because the Vite proxy makes requests arrive looking like a different origin than the browser sent; fixed by deriving `CSRF_TRUSTED_ORIGINS` from the existing `CORS_ALLOWED_ORIGINS` env var.

**Data model:** `Assessment.user` (nullable FK to `auth.User`, migration `audit/0003_assessment_user.py`) — set only for `kaynak="portal"` rows. Bank/demo/API scoring paths never populate it. This is what powers a portal user's private "Geçmişim" (`GET /api/portal/gecmis`, filtered by `user=request.user` — no user can see another user's history, and the bank's `AuditLog`/aggregate views never expose portal users' identities).

**Not yet done, explicitly (OQ-46):** password reset, email verification, KVKK/consent notice, data-retention policy. This is a working demo-grade login, not yet hardened for accepting real (non-demo) personal data at market.

## 9c. Identity, consent & multi-tenancy (execution.md §3b Phase 7/7.2–7.4)

Extends §9b with what a *market* product needs beyond a demo login: a pseudonymous customer identifier institutions can request, consent-gated institution access, and an append-only consent ledger. New Django app `kimlik/`, deliberately separate from `audit/` (a different concern — identity/consent, not scoring history) and from `api/` (reusable by any future non-web client).

**Design principle — minimum personal data (PO decision, not assumed):** no name, no national ID. `Profil.aks_no` (§ below) is generated, not derived from any personal attribute. Phone number is collected **only** for one-account-per-number enforcement (Sybil resistance) and is never stored in plaintext — only `HMAC-SHA256(AKS_PEPPER, number)` is persisted (`kimlik/telefon.py`).

**AKS number** (`kimlik/aks_no.py`): 45 random bits, Crockford Base32-encoded (excludes the visually-confusable I/L/O/U), with a checksum digit — `AKS-XXXX-XXXX-XC`. Format: `gecerli_mi()` catches transcription typos when an institution's staff types the number in by hand; this is format validation, **not** identity verification (see the honesty note below). Generated automatically at registration (`api/auth_views.py::kayit` → `kimlik/aks_no.py::uret()`), retried on the (statistically negligible) chance of a collision against the DB `unique` constraint.

**Consent model — "institution access requires customer approval" (PO decision):** `Kurum` (institution) ↔ `KurumUyeligi` (staff membership, provisioned via `manage.py bootstrap_kurum`, deliberately **not** self-service — a self-registering "institution" would undermine the assumption that the institution's identity is trustworthy, OQ-53) ↔ `ErisimTalebi` (a named institution requests access to a named `Profil`, with a stated purpose) ↔ `RizaKaydi` (append-only ledger of every `talep_olusturuldu`/`onaylandi`/`reddedildi`/`iptal_edildi`/`erisim_kullanildi` event — same immutability pattern as `audit.AuditLog`: `save()` raises on any attempted update, `delete()` is blocked outright). An approval is **time-boxed** (`gecerlilik_bitis`, default 30 days) and **revocable at any time** by the customer — revocation is immediate: `izinler.aktif_riza()` (the single function every institution-facing view calls) checks `durum="onaylandi"` **and** `gecerlilik_bitis > now` on every request, not just at approval time.

**Enforcement, not just data modeling:** `kimlik/izinler.py::KurumUyesi` (DRF permission — is this user staff at *any* institution) and `aktif_riza(kurum, profil)` (is *this specific* institution's access to *this specific* customer currently valid) are composed on every institution-facing view in `kurum_views.py`. The mirror-image permission, `ProfilSahibi`, guards every *customer*-facing view: those views read `request.user.profil` directly, and an account without a `Profil` (institution staff — `bootstrap_kurum` creates only a `KurumUyeligi`) previously produced an HTTP 500 rather than a 403. The two permissions partition the two audiences explicitly instead of relying on bare `IsAuthenticated` (execution.md §3b Phase 7/7.8). Verified live (curl, cookie-jar driven, mirroring the exact frontend request shape): an institution with no consent gets 403; after approval it can view the customer; after the customer revokes, the *same* institution immediately gets 403 again; a second institution never granted access gets 403 throughout.

**The third surface, and the hole it left open (execution.md §3b Phase 7/7.11).** The two permissions above partition *customer* and *institution*. There is a third audience — the bank's own internal demo/research interface (`api/views.py`: whole demo population, portfolio and fairness aggregates, assessment history) — and until Phase 7.11 it had **no permission class at all**. With no `DEFAULT_PERMISSION_CLASSES` configured, DRF's `AllowAny` applied: any registered end user, and in fact any anonymous client, could read every one of those endpoints directly. The site-wide login gate added in §7.10 only hid the *UI*; it never protected the API. A second, narrower leak sat inside it: `services.gecmis()` filtered on `musteri_id` alone, and portal uploads are written with `musteri_id="-1"` (real identity lives in the `user`/`profil` FK), so every portal user shares that one key — one call returned all of their score histories. Adding `.exclude(kaynak="portal")` was not enough, and the test proved it: with the DB query now empty, the function fell through to its orchestrator-memory fallback (`Orkestrator.hafiza`), where portal and CSV scorings are recorded under the *same* `-1` key — the leak simply moved to the second leg. The durable fix is the `KIMLIKSIZ_MUSTERI_ID` guard: this endpoint returns empty for the identity-less sentinel before either lookup runs. Both are closed: `YoneticiKullanici` (`is_staff`) now guards all 15 endpoints except `bilgi` (service metadata, no user data), and `gecmis()` is sealed on both paths. `is_staff` is deliberate — this surface warrants the same trust level as the Django admin, so it reuses that flag rather than introducing a parallel role table. `YuzeyIzolasyonuTesti` (`api/tests.py`) pins all three audiences: anonymous → 401/403, ordinary user → 403, institution staff → 403, admin → allowed, and `gecmis()` → empty for the sentinel with *both* the DB rows and the in-memory fallback deliberately populated. The customer-facing endpoints in `api/portal_views.py` were also moved from bare `IsAuthenticated` to `ProfilSahibi`, matching `kimlik/views.py` — an account with no AKS number could otherwise upload a document and create a half-formed `Assessment` with `profil=None`. The `yonetici`/`kurum_uyesi` flags returned by `/api/auth/*` drive **post-login routing only**; forging them in the browser yields a 403, never data.

**Ownership defense — three layers, explicitly a detection posture, not a prevention claim.** With name/national-ID collection ruled out by the minimum-data decision above, *proving* a statement belongs to the uploader is not technically achievable — the product does not claim otherwise. Instead (`api/sahiplik.py`, wired into `services.degerlendir()`):

1. **Document fingerprinting** (§5.7) — if the same statement content surfaces under a second `Profil`, **both** records (the new one and, retroactively, the earlier one) are flagged `coklu_sahiplik_supheli`. Verified live: uploading the identical statement under a second account flagged both sides.
2. **Mandatory declaration** — `portal_yukle` rejects (400) any upload without an explicit "this statement is mine" confirmation; the declaration is timestamped (`Assessment.created_at`) and IP-stamped (`Assessment.yukleme_ip`).
3. **Behavioral consistency** — if a profile's new upload's income scale deviates more than 3× from that profile's own upload history median, `profil_tutarsiz` is flagged.

All three flags are **transparency signals only** — same additive-only pattern as `anomali_bayrak` (§5.4): they are never read by `SkorlamaAgent`, never change `aks_skor`/`karar`/`onerilen_limit` (overview.md §7 boundary, re-verified for this addition too). The real fix — open banking, where data arrives from the bank under authorization rather than as a user-uploaded file — is documented as the production path but not built this cycle (OQ-51).

**Data model additions:** `audit.Assessment` gained `profil` (FK to `kimlik.Profil`, declared as the string `"kimlik.Profil"` to avoid a hard import cycle between `audit` and `kimlik`), `belge_parmak_izi`, `sahiplik_beyani`, `sahiplik_bayraklari` (JSON), `kaynak_format`, `yukleme_ip` — all nullable/best-effort, none touch the pre-existing `klasik_skor`/`aks_skor` boundary fields.

**Raw transaction retention (PO decision, execution.md §3b Phase 7/7.9):** `Assessment.ham_islemler` (`JSONField`, migration `0006`) stores the parsed transaction rows themselves (`tarih`/`islem_tipi`/`kategori`/`tutar`/`aciklama`), not just the 9 derived features — previously the raw upload was discarded after scoring. Written only when a `Profil` is attached (customer's own portal upload), never for bank/demo/anonymous scoring (that data already lives in the source CSV; duplicating it would only grow the PII footprint for no benefit). Surfaced back to the customer only, via `GET /api/portal/gecmis/<id>` (`ProfilSahibi` + ownership filter — a customer can never fetch another account's detail); institutions never see transaction-level detail, only the score/SHAP/risk-appetite view already documented above — this is a deliberate asymmetry, not an oversight. **Bug found while wiring this up:** `agents/veri_agent.py::VeriAgent.calistir()` mutated its caller's transaction dicts in place (writing a raw `datetime` into `tarih_obj`), so the first attempt to persist `ham_islemler` raised `TypeError: object of type datetime is not JSON serializable` inside the best-effort audit write — silently, since `_denetim_yaz()` swallows all exceptions by design (§ above: "the demo never breaks on infrastructure"). Fixed by having `VeriAgent` operate on a shallow copy; `_denetim_yaz()` additionally whitelists only the canonical schema keys when building `ham_islemler`, as defense in depth against any future stray internal field.

## 10. API architecture

Base `http://localhost:8000/api`. DRF views in `product/04-backend/api/views.py`; JSON bodies (except CSV upload = multipart).

| Method | Path | Purpose |
|---|---|---|
Every row from `/metrikler` down to `/gecmis` is the bank-internal research surface and requires `YoneticiKullanici` (`is_staff`) — see §9c. `/bilgi` is the only unauthenticated endpoint.

| GET | `/bilgi` | Service info: model name, feature list, demo count (**only public endpoint**) |
| GET | `/metrikler` | Persisted CV+CI+calibration+per-persona report (`degerlendirme.py`); 503 until generated |
| GET | `/politika` | Decision-mechanism config: AKS score bands/multipliers + portfolio thresholds |
| GET | `/segmentasyon` | Unsupervised K-Means discovery report (§5.5); 503 until generated |
| GET | `/genelleme-saglamlik` | Out-of-persona generalization + thin-file stress test + gaming-sensitivity report (R8/R10/R11); 503 until generated |
| GET | `/risk-istahi` | 3-tier (ihtiyatli/dengeli/atak) bank recommendation report (§5.6); 503 until generated |
| GET | `/demo-musteriler?adet_per_persona=3` | Sample customer IDs per persona |
| GET | `/skorla/{musteri_id}` | Score a demo customer (writes audit row, `kaynak="demo"`) |
| POST | `/skorla` | Score from raw transactions (audit, `kaynak="api"`) |
| POST | `/aciklama` | SHAP factor explanation |
| POST | `/simulasyon` | "What-if" — effect of feature changes on the score |
| GET | `/portfoy?...` | Portfolio analysis: rescued creditworthy segment + illustrative revenue (**Redis cache, TTL 600s**) |
| GET | `/adalet?...` | Equal-opportunity fairness report (**Redis cache, TTL 600s**) |
| POST | `/csv-skorla` | Score a statement — CSV, XLSX, **or PDF** (§5.7; multipart; audit, `kaynak="csv"`; URL name kept for backward compatibility) |
| POST | `/asistan` | Ask the AKS Assistant — tool-calling (`danisman_llm`, Claude if `ANTHROPIC_API_KEY` set else Gemini if `GEMINI_API_KEY` set), else rule-based `AsistanAgent` fallback (§4) |
| GET | `/gecmis/{musteri_id}` | Persisted **demo** assessment history (DB; falls back to orchestrator memory). Excludes `kaynak="portal"` rows — see the §9c leak note |
| GET | `/auth/ben` | Current portal session (also sets the CSRF cookie) — 401 if not logged in |
| POST | `/auth/kayit` | Portal user registration (**email/password only** — no name, no TCKN, §9c) + auto-login; auto-provisions a `kimlik.Profil` (AKS number) |
| POST | `/auth/giris` | Portal user login |
| POST | `/auth/cikis` | Portal user logout (`IsAuthenticated`) |
| POST | `/portal/yukle` | Authenticated user scores their own statement — CSV/XLSX/PDF (multipart; `IsAuthenticated`; requires `beyan` ownership declaration, §9c; `kaynak="portal"`, tied to `Assessment.user`+`Assessment.profil`) |
| GET | `/portal/gecmis` | The logged-in user's own upload history only (`IsAuthenticated`) |
| GET | `/kimlik/profilim` | The logged-in user's AKS number + phone-verification status (`IsAuthenticated`) |
| POST | `/kimlik/telefon/gonder`, `/kimlik/telefon/dogrula` | Phone OTP send/verify (`IsAuthenticated`, throttled, §9c) |
| GET | `/kimlik/erisim-talepleri` | Access requests received by the logged-in customer (`IsAuthenticated`) |
| POST | `/kimlik/erisim-talebi/{id}/onayla`\|`/reddet`\|`/iptal` | Customer approves/rejects/revokes an access request (`IsAuthenticated`, §9c) |
| GET | `/kimlik/riza-defterim` | The logged-in customer's own append-only consent ledger (`IsAuthenticated`) |
| GET | `/kimlik/kurum/ben` | Current institution-staff session info (`KurumUyesi`) |
| POST | `/kimlik/kurum/erisim-talebi` | Institution requests access to a customer by AKS number + stated purpose (`KurumUyesi`, throttled) |
| GET | `/kimlik/kurum/musteriler` | Customers with a currently-active consent for this institution only (`KurumUyesi`) |
| GET | `/kimlik/kurum/musteri/{aks_no}` | Customer detail + SHAP reason codes + 3-tier risk-appetite recommendation (§5.6) — 403 without active consent (`KurumUyesi` + `aktif_riza`, §9c) |

All scoring responses (`/skorla`, `/skorla/{id}`, `/csv-skorla`) also carry `anomali_bayrak`/`anomali_skoru` (§5.4) when the optional anomaly-detection artifact is present; both are `null` otherwise, and neither ever affects `aks_skor`/`karar`. `/csv-skorla` and `/portal/yukle` additionally carry `belge_meta` (§5.7 — format, quality flags, `BelgeAgent`'s trace) and, for the portal path, `sahiplik_bayraklari` (§9c) — none of these affect the score either.

## 11. Database & infrastructure

- **Database:** Supabase (Postgres) via Django ORM. `DATABASE_URL` unset → local SQLite (`aks_dev.sqlite3`). `python manage.py check_connections` reports live-vs-fallback for both DB and cache.
- **Cache:** Upstash Redis via `django-redis` (`rediss://` TLS). `REDIS_URL` unset → Django `LocMemCache`. Caches the heavy `/portfoy` & `/adalet` aggregates (they re-score *all* customers per call) and rate-limits the LLM assistant.
- **Secrets contract (`.env`, never committed; `.env.example` documents it):** `ANTHROPIC_API_KEY` (§3b Phase 7/7.5/7.10 — first-priority tool-calling path; live end-to-end test still TODO, OQ-48), `GEMINI_API_KEY` (§7.10 — second-priority tool-calling path, **live-verified**, same `danisman_llm` agent/guard as Claude — not merely a fallback-enrichment key anymore), `AKS_PEPPER` (§9c — phone-number HMAC key; empty → falls back to `DJANGO_SECRET_KEY`, same "empty env → sane default" pattern as everything else here), `DATABASE_URL` (§7.10 — in active use, Supabase Postgres), `SUPABASE_URL/ANON_KEY/SERVICE_ROLE_KEY` (unused by any code path — only `DATABASE_URL` matters for the Postgres connection), `REDIS_URL` (§7.10 — in active use, Upstash; `IGNORE_EXCEPTIONS=True` means a broken/unreachable Redis degrades to no-op caching rather than 500ing unrelated endpoints. **Known consequence, discovered in §7.17:** this also silently disables DRF rate limiting, since throttle counters live in the cache. That is an accepted trade-off for the *security* throttles (OTP brute-force, request spam) — availability over perfect rate limiting — but it was not acceptable for the *cost* throttle on `/api/asistan`, the only endpoint calling a paid external service: Redis going down would remove the only thing protecting the API quota, at exactly the worst moment. Hence a separate always-in-process `CACHES["throttle"]` alias that cannot fail open). **Connection lifetime:** `conn_max_age=0` — deliberate, not an oversight. Holding persistent connections behind a connection pooler is an anti-pattern (pooling is the pooler's job), and since §7.11 every protected endpoint hits the DB for session auth, so a browser page issuing 5 parallel requests opened 5 connections per page and exhausted Supabase's 15-client free-tier cap within a few navigations (§7.13/7.14 — caught in live browser audit, every endpoint started returning 500), `DJANGO_SECRET_KEY/DEBUG/ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `AKS_DATA_DIR`, `AKS_MODEL`, `AKS_OTP_DEMO_KOD` (§7.12 — returns the OTP in the API response so the phone-verification flow is testable without an SMS provider; split out from `DEBUG` so that enabling it does not also expose tracebacks; **must be false in a real deployment**), `DJANGO_HTTPS` (§7.12 — turns on Secure cookies, HSTS and the HTTP→HTTPS redirect; deliberately **not** keyed off `DEBUG`, because local development already runs with `DJANGO_DEBUG=false` over plain http and Secure cookies would silently break login there. `manage.py check --deploy` passes clean with it set). **All optional** — empty → SQLite + LocMem + rule-based assistant.

## 12. Deployment

**Render (Docker), one service, one origin** (§3b Phase 7/7.15–7.16). Config: `render.yaml` (Blueprint at the repo root), `deploy/Dockerfile` (Node stage builds the React bundle, Python stage runs Django — provider-agnostic), `deploy/baslat.sh` (migrate → idempotent demo-account bootstrap → gunicorn). Supabase + Upstash stay external. `deploy/hf/yayinla.sh` publishes the same image to a Hugging Face Space and still works, but **HF is not viable on the free tier** — see below. The old FastAPI `Dockerfile`/`render.yaml` in `product/04-backend/_legacy_fastapi/` is **reference only, not live**.

- **Why not Hugging Face** (it was the first choice, and the Space was actually built and pushed successfully): HF only allows *static* Spaces for free — *"hosting Gradio and Docker Spaces on free cpu-basic requires a PRO subscription"* (HTTP 402 from `/api/repos/create`). A static Space cannot run Django, and splitting the frontend out would break cookie auth. HF remains one `deploy/hf/yayinla.sh` invocation away if a PRO subscription is ever bought.
- **Worker count is bounded by memory, not CPU, and was measured rather than guessed.** Each gunicorn worker imports the app separately (~285 MB resident: shap/xgboost/lightgbm/sklearn). Running the real image constrained to Render's free 512 MB with the original `--workers 2` produced repeated `Worker was sent SIGKILL! Perhaps out of memory?` — 8 worker boots, 6 kills, workers thrashing while still returning 200s. The same test with **1 worker peaked at 293 MB / 512 MB (57%) with zero kills**, serving every surface plus 8 parallel `/api/portfoy` requests. Hence `GUNICORN_WORKERS` defaults to **1** and `render.yaml` pins it; raise it only in proportion to available memory (~285 MB per worker).

- **Why one service rather than a static frontend host + API backend:** `api.ts` uses `credentials: "same-origin"` and every surface (portal, institution, panel) authenticates by session cookie. On a split domain the browser would not send the cookie at all; forcing `SameSite=None` would still break under third-party-cookie blocking. Django serves the built bundle via WhiteNoise (`WHITENOISE_ROOT = spa/`, served from the site root so `index.html`'s `/assets/*` references work untouched — no Vite `base` change, so the dev server is unaffected). This required **zero frontend changes**.
- **SPA fallback** (`config/urls.py`): React Router owns `/panel`, `/portal/*`, `/kurum/*`; those paths do not exist server-side, so a direct visit or page refresh would 404 without it. `api/`, `admin/` and `static/` are excluded by negative lookahead — otherwise a nonexistent API endpoint would silently return HTML instead of a JSON 404. `index.html` is served `Cache-Control: no-cache`: it is the one stable address pointing at hashed assets, and a cached copy would white-screen the app after the next deploy.
- **Host choice rationale:** the app's resident footprint is **335 MB** (shap/xgboost/lightgbm/sklearn import chain) with an 8-second Django startup, which makes 512 MB free tiers marginal; HF's free 16 GB / 2 vCPU removes the constraint. Gunicorn runs `--workers 2 --threads 4` → at most 8 concurrent requests, therefore at most 8 Postgres connections, safely under Supabase's 15-client cap (the limit that took the whole panel down in §7.14).
- **What building the image actually exposed — three dependency-declaration defects, none of which any test could catch** (tests run against whatever is already installed locally; only a from-scratch install reveals what the declarations really resolve to):
  1. `shap>=0.52` had **never been satisfiable**: shap 0.52 requires Python ≥3.12, the project is developed and validated on 3.11 (installed version: 0.51.0). The build failed outright with `No matching distribution found`. Fixed by aligning the bound to reality (`shap>=0.51`) rather than moving production to Python 3.12 — SHAP output feeds the user-facing reason codes, and shipping a SHAP version never exercised locally would violate train/serve consistency. The bound's real purpose (`>0.49`, for the xgboost≥3 `base_score` format) is preserved.
  2. `scikit-learn>=1.4` let the image install **1.9.0** while the artifacts were pickled by 1.8.0, producing `InconsistentVersionWarning: ... might lead to ... invalid results` on every worker boot. Now bounded to `>=1.8,<1.9`; **raising it requires retraining, not just editing the pin.**
  3. overview.md documented `numpy<2` as pinned, but no such bound existed in any `pyproject.toml` and the image installed numpy **2.4.6**. Adding the documented bound turned out to be *impossible*: `shap 0.51.0 requires numpy>=2`, so pip fails with `ResolutionImpossible`. The real defect was the **documentation**, and the inconsistency is on the development machine — `pip check` there reports "shap 0.51.0 has requirement numpy>=2, but you have numpy 1.26.4". The container's numpy 2.x is the correct configuration; NumPy is deliberately left unbounded above.

  Before deciding on 2 and 3, the question "does any of this change a score?" was answered empirically rather than assumed: the model's `predict_proba` over 100 real feature vectors is **bit-identical** between the local (numpy 1.26.4 / sklearn 1.8.0) and container (numpy 2.4.6 / sklearn 1.9.0) stacks — fingerprint `c37c4e2a5e88b310` on both. Nothing was silently mis-scoring. The sklearn bound was still added so that "the deployed model scores the same as the validated model" is a declared property rather than an observed coincidence.

**Environment** (Render dashboard → *Environment*; `render.yaml` marks the secret ones `sync: false` so they are never committed. The container reads them as plain env vars, and `load_dotenv` does not override real env vars, so there is no conflict with a local `.env`):

| Key | Value | Note |
|---|---|---|
| `DATABASE_URL` | Supabase session-pooler URI | Same instance as local — data persists across deploys |
| `REDIS_URL` | Upstash URI | Optional; unreachable Redis degrades to no-op caching, never 500s |
| `DJANGO_SECRET_KEY` | generated by Render (`generateValue: true`) | Never carried over from local |
| `DJANGO_ALLOWED_HOSTS` | the service hostname, e.g. `aks.onrender.com` | |
| `DJANGO_HTTPS` | `true` | Set in `render.yaml`. Render terminates TLS; `SECURE_PROXY_SSL_HEADER` is already set, so this does not loop |
| `DJANGO_DEBUG` | `false` | |
| `AKS_PEPPER` | same value as local | **Changing it orphans every existing `telefon_hash`** — phone numbers become unverifiable against stored hashes |
| `AKS_OTP_DEMO_KOD` | `true` | PO decision (§7.15): deliberate demo concession while OQ-47 (no SMS provider) is open — returns the OTP in the API response so the flow is demonstrable. Must be `false` for real users |
| `GEMINI_API_KEY` | live key | Optional; absent → deterministic rule-based assistant |
| `GUNICORN_WORKERS` | `1` | Set in `render.yaml`. Memory-bound, measured — see above |

**Priority note:** the entire stack/deploy track is priority #8 — it is *not* the bottleneck; it is intentionally not pushed further until the #1–#3 research items (§5) are addressed.

## 13. Future architecture ideas

- **Real-data path (OQ-36):** if Home Credit / LendingClub / open-banking data is available, demote the synthetic generator to unit-test fixtures and make real outcomes the benchmark.
- **Simulator redesign (A2):** if staying synthetic, rebuild `uretici.py` so a *calibratable* behavioral capacity signal exists and diverges from a traditional-thin signal for a knowable subpopulation — with persona **not** determining both features and label.
- **Open banking as the real ownership fix (OQ-51):** replace user-uploaded statements with bank-authorized data access (e.g. an Open Banking API) — this is the only way to make the sahiplik claim a *proof* rather than the current best-effort detection (§9c). The three-layer detection posture built this cycle stays useful as a defense-in-depth signal even after open banking lands.
- **Configurable risk appetite (OQ-50):** let each institution set its own target bad-rate tiers and profit assumptions instead of the current fixed illustrative defaults in `risk_istahi.py::PROFILLER`.
- **Real SMS provider (OQ-47):** wire an actual provider (Twilio/Netgsm/İleti Merkezi) behind `kimlik/telefon.py`'s OTP send path, replacing the current DEBUG-mode "code in the API response" placeholder.
- **Second genuine agent, beyond what Phase 7 already added (OQ-38, narrative framing still open):** `belge_agent.py` and `danisman_llm.py` (§4) already raised the genuine-agent count to three; the open question now is jury-facing *framing* (rename the pipeline stages, or explain the distinction), not "build a second agent."
- **Calibration layer:** isotonic/Platt on top of the base model, per-segment.
- **Drift monitoring:** PSI-based hook wired into `Orkestrator`'s score-over-time tracking.
- **Optimization pipeline:** convert the calibrated capacity PD + PD-gap into a policy engine that recommends the maximal within-policy limit at a fixed portfolio bad-rate — the productized decision-curve output.
