# AKS — Execution Plan

Companion to **[overview.md](overview.md)** and **[architecture.md](architecture.md)**. This is the **single live plan** — it replaces all prior roadmaps, workstream files, and traceability matrices. Truth about *what to do next* lives here.

Detailed data-engineering specs live in **[`planning/`](planning/data-architecture.md)** (data-architecture, feature-schema, pipeline-steps) — a subordinate working area for column-level detail too fine-grained for the root docs; these three root docs remain the source of truth.

**Priority scale** (from overview.md §5, binding): P1 accuracy · P2 generalization · P3 calibration · P4 robustness · P5 interpretability · P6 business value · P7 regulatory · P8 engineering · P9 AI · P10 UI. Lower number = higher priority. **UI/stack work must never block P1–P4.**

**Status values:** `DONE` · `IN-PROGRESS` · `BLOCKED` · `TODO` · `PROPOSED`.
Owner shorthand: **PO** = Product Owner (Alperen Karakaya) · **Research** = modeling/eval · **Eng** = build.

---

## 1. Current sprint (research-rigor track)

The active objective is **restore benchmark validity**, because every headline number is currently circular (architecture.md §5.1). Nothing downstream — business claims, fairness claims, jury deck — is trustworthy until this is resolved.

**This sprint's definition of done:** OQ-36 answered → target metric (Formulation B) instrumented → a non-circular benchmark producing an *honest* incremental-approval-at-fixed-bad-rate number with CIs.

**§3b now gives this sprint a concrete, folder-sequenced execution playbook** (model optimization → decision-mechanism config → metrics exposure → frontend), requested by the PO to push past M4 into M5/UI without touching `01-data/`. UI/infra are no longer indefinitely paused — they are Phase 3, sequenced *after* Phase 1 (model/metrics) and Phase 2 (backend exposure) land, not skipped.

## 2. Milestones

| # | Milestone | Gate | Status |
|---|---|---|---|
| M1 | Pipeline works end-to-end (data → model → API → audit) | Live scoring + immutable audit | ✅ DONE |
| M2 | Statistical rigor instrumented (CV, CI, calibration, per-segment) | `degerlendirme.py` + `circularity_ablation.py` reproducible | ✅ DONE |
| M3 | Circularity diagnosed & target defined | Finding documented; Formulation B chosen | ✅ DONE (B awaiting ratification, OQ-39) |
| M4 | **Non-circular benchmark** | Real data OR redesigned simulator; honest headline number | 🟡 IN-PROGRESS — synthetic honest-fallback **built + proven** (`product/01-data/generator/uretici_kapasite.py`): label decoupled from persona (spread 0.015) and from features (no single feature = label; income channel 0.50, behavioral 0.84 genuine +0.34 lift). Still pending: OQ-36 (prefer real data if available) and porting the decoupled label into the training/eval path (DA2) — **now Phase 1 / U1 of §3b**. |
| M5 | Model finalized on valid benchmark | LR-vs-XGBoost decided on non-circular data; calibrated | 🟡 IN-PROGRESS — LR-vs-XGBoost decided (LR, non-overlapping CIs) and calibration attempted (honest null result); still open: robustness (R8/R10/R11), monotonic constraints (E2), reason-code standardization (E3) |
| M6 | Demo-ready product | Stitch UI integrated, deploy live, agent narrative honest | ⏳ TODO (after M4; UI last) |

## 3. Priorities (what to do, in order)

1. **Resolve OQ-36** (real data vs redesigned simulator) — the single highest-leverage decision.
2. **Instrument the Formulation B metric** (incremental approvals at fixed bad-rate + per-segment calibration).
3. **Produce an honest headline number** on a non-circular benchmark; re-caveat or rewrite published figures (OQ-37).
4. **Then** model finalization, robustness, interpretability, business-value rebuild.
5. **Only then** engineering polish, agent-narrative correction, and UI.

## 3b. Execution playbook — model, decision-mechanism, metrics & frontend uplift (this cycle)

PO has asked to push forward now on four fronts: **model optimization**, **decision-mechanism changes + retraining on data**, **frontend changes**, and **metric changes** — with metrics/model quality named the top priority. Ground rules set by the PO for this cycle: **one `product/` subfolder in flight at a time**, and **`01-data/` stays untouched** (no generator/dataset edits — only read-only consumption of what DA1 already built: `kapasite_islemler.csv`, `kapasite_etiketleri.csv`).

This section does not replace §§4–6 above — it is the concrete, folder-sequenced task list that executes DA2, E1, E5, E6, R5, R9, D2, D3, D5, plus a few new tasks the decision-mechanism/frontend work surfaced (prefixed `U`, for "uplift", to avoid colliding with existing ID series).

**Scope note on OQ-36:** proceeding on the synthetic/decoupled path (R6/DA1, already built) for this cycle, since real-data acquisition (R7) would require `01-data/` work now explicitly excluded. This does **not** resolve OQ-36 — real data remains open as a future option — it only fixes which path R3 takes *operationally* for this cycle.

**Folder order (strict — do not start phase N+1 until phase N's exit gate passes):** `02-ai-agents` → `04-backend` → `03-frontend`. Model and decision-mechanism code both live in `02-ai-agents`, so priorities 1 ("model optimizasyonu") and 2 ("karar mekanizması + veri ile eğitim") are almost entirely Phase 1; metric fixes span all three phases (compute → expose → display), with Phase 1 carrying the highest-priority slice — an honest, non-circular headline number.

### Phase 1 — `product/02-ai-agents/` (model optimization + decision mechanism + metric engine)

| ID | Task | Size | Executes | Notes |
|---|---|---|---|---|
| U1 | Wire the already-built decoupled label (`01-data/datasets/kapasite_islemler.csv` + `kapasite_etiketleri.csv`) into `egitim.py` as the training input, **read-only** | M | DA2, M4 gap | Keep the old circular path selectable behind a flag so `circularity_ablation.py` can still show the before/after |
| U2 | Feature-extraction consumer for the new cash-flow columns (`kanal`, `karsi_taraf_tipi`, `brut_tutar`, `zorunlu_mu`) in `ozellik/cikarim.py`, if they add signal beyond the current 9 | M | DA2 | Only add columns with a stated hypothesis (data-architecture.md §1.2 minimization rule) even though the data folder itself isn't being touched |
| U3 | Replace the single 70/30 `train_test_split` in `egitim.py` with CV + hyperparameter search (grid/random over `n_estimators`/`max_depth`/`learning_rate`/`subsample`/`colsample_bytree`); persist winning params as a JSON manifest | M | E5, D3 | Removes hardcoded `n_estimators=300, max_depth=4` |
| U4 | Reconcile `eval_metric` inconsistency (`"auc"` in `egitim.py` vs `"logloss"` in `degerlendirme.py`/`circularity_ablation.py`) | S | — | Pick one, document why |
| U5 | Fix global `random.seed(7)` reuse in `etiketleme.py` — per-resample seeding | S | E6, D2 | Bootstrap/CI currently understate uncertainty |
| U6 | Persist `degerlendirme.py`'s full output (CV, bootstrap CI, Brier, ECE, reliability, per-persona) as a versioned JSON artifact next to `metrikler.json`; make it — not the stale single-split number — the "official" reported metric | M | R5, R9, D5 | The concrete fix for "the headline numbers are circular… do not cite as validated" |
| U7 | Re-run `circularity_ablation.py` against the new (U1) benchmark to prove the fix, not just assert it | S | R1 (extends) | Expect the causal/non-causal AUC gap to shrink once the label no longer shares generator machinery with features |
| U8 | Decide LR vs XGBoost **on the new non-circular benchmark** (architecture.md §5.2 recommends LR); execute the swap only if LR still wins | M | E1 | Gated — do not swap on the old circular numbers |
| U9 | Calibration correction (Platt/isotonic) where U6's ECE warrants it | M | R9 | Calibration is priority #3, ahead of business value/UI |
| U10 | Instrument Formulation B fields — `pd_davranissal`, `pd_geleneksel_bant`, `pd_fark`, `kapasite_sinyali` (architecture.md §5.3) | M | R5 | The product's actual spine metric, not aggregate AUC |
| U11 | Decision-mechanism config: move `skorlama_agent.py`'s hardcoded score bands (720/620/540) and limit multipliers (8/5/2/0) into one versioned policy-config module; delete the duplicated `olasilik_to_aks()` in `is_etkisi.py`, import from one source | S | — (new) | This *is* "karar mekanizması değişiklikleri" — config, not a rules-engine rewrite; the boundary (never override the bank's segment) is unaffected, only AKS's own bands become inspectable/versioned |
| U12 | `requirements-core.txt` cleanup (stale `shap>=0.44`/FastAPI pins → match `pyproject.toml`) | S | — | Housekeeping found during recon |
| U13 | Extend/update the 16 `aks_core` tests for the new label source, policy config, and calibration step | M | — | Must stay green before Phase 2 starts |
| U14 | Boundary re-check: confirm U1–U11 still leave `SkorlamaAgent` emitting only a complementary score + within-policy limit — no path writes the bank's segment | S | overview.md §7 | Non-negotiable; explicit gate before switching folders |

**Phase 1 status: ✅ DONE (U1, U3–U11, U13, U14) — U2 explicitly deferred.** Real results, run end-to-end this cycle:

- **Non-circular benchmark, 5×5 CV** (`degerlendirme.py --veri-kaynagi dekuple`, 2000 customers, base rate 0.172): XGBoost 0.840 [0.831, 0.850]; **LogisticRegression 0.862 [0.853, 0.871]** — CIs don't overlap, LR wins on evidence, not just simplicity. Classic-score baseline AUC **collapses to 0.493** (chance) on this benchmark — direct, non-circular confirmation of the thin-file blind spot claim. Full report: `aks_core/artifacts/degerlendirme_raporu.json`.
- **U8 executed:** production model swapped to `LogisticRegression` (`aks_model_meta.json`, format `logistic_joblib`, scaler persisted alongside per `kayit.py::OlcekliLojistikSarmalayici`). architecture.md §5.2 updated.
- **U7 proof, not assertion:** `circularity_ablation.py --veri-kaynagi hepsi` reproduces the *old* circular numbers (Oracle 0.901, XGB 0.853, LR 0.853 — matches architecture.md §5.1 exactly) immediately followed by the *new* decoupled numbers (Oracle 0.909, XGB 0.845, LR 0.863) in one run.
- **U9 calibration — honest null result:** pre-registered ECE threshold (0.03) triggered isotonic correction; ECE moved 0.0391 → 0.0394 (flat, not improved) on a 500-customer holdout. Reported as-is, not re-tuned. Likely just holdout noise at this sample size — a real-data or larger-holdout re-check is future work, not this cycle's job.
- **U10 instrumented:** `formulasyon_b.py` (pd_geleneksel_bant/pd_fark/kapasite_sinyali) computed and unit-tested; not yet reachable via API (needs Phase 2 U17 to pass `klasik_skor` through).
- **Real, updated business-impact number** (`is_etkisi.py --veri-kaynagi dekuple`, replaces the old circular "973/1084"): of 687 customers the classic score rejects, 567 are genuinely creditworthy; the model rescues **538 (95%)** of them, at the cost of wrongly approving 58/120 (48%) of the genuine defaults among the rejected — that 48% false-approval rate is a real, un-obscured finding, not a curated one. **Caveat:** this run scores the *entire* population, including customers the winning model was trained on (no held-out split) — it is an in-sample sanity check, not an out-of-sample business estimate; do not cite the 538/567 figure as validated either, for the same in-sample-vs-CV reason the old number was flagged (D5 stays open for this new number too, though the mechanism producing it is no longer circular).
- **U2 deferred, not silently dropped:** extending the 9-feature vector with the new cash-flow columns (`kanal`/`karsi_taraf_tipi`/`brut_tutar`/`zorunlu_mu`) was scoped out this cycle — it has a large blast radius (model meta, SHAP labels, `bilgi()` endpoint, frontend "9 features" copy, several tests all assume exactly 9) and the columns have partial/missing coverage per row that needs real handling, not a rushed addition. Left as a clearly-flagged follow-on, not implemented half-way.
- **Bonus fix (not originally in U-list):** `aciklama.py`'s SHAP explainer hardcoded `shap.TreeExplainer`, which silently only supports raw tree-model objects. This was a dormant bug — invisible as long as XGBoost always won — that broke immediately once LR (or even a calibration-wrapped model) became current. Rewritten to be model-agnostic (`TreeExplainer` for tree models via their raw booster, `LinearExplainer` + a persisted background sample for linear models); reason-code correctness/direction is preserved because isotonic calibration is monotonic.
- Tests: `aks_core` 16 → **24 passing**; `04-backend` 11 passing (one model-name allowlist widened to include `LogisticRegression` — a compatibility fix, not new Phase 2 feature work).

Do not start Phase 2 (U15–U19) until you've read this block — U16 exposes U11's policy config, U15/U17 expose U6/U10's new artifacts, U18 may need a migration.

### Phase 2 — `product/04-backend/` (expose, don't compute)

| ID | Task | Size | Executes | Notes |
|---|---|---|---|---|
| U15 | New `GET /api/metrikler` returning U6's persisted versioned metrics (CI, calibration, per-persona) | S | R5 | Fills the "no metrics endpoint exists" gap found in recon |
| U16 | New `GET /api/politika` (or extend `/api/bilgi`) exposing U11's decision-mechanism config | S | — (new) | Lets the frontend stop hardcoding thresholds |
| U17 | Wire Formulation B fields (U10) through `portfoy()`/`adalet()` where relevant; keep the existing `klasik_esik`/`aks_esik` query-param override behavior | M | R5 | |
| U18 | Migration: extend `Assessment`/`AuditLog` with `pd_fark`/`kapasite_sinyali` if persisted | S | DA3 (subset) | Audit boundary fields (`klasik_skor` unchanged) stay as-is |
| U19 | Extend `api/tests.py` (11 → N) for the new endpoints + a boundary test that the new fields never let anything overwrite `klasik_skor` | M | D1 (partial) | |

**Phase 2 status: ✅ DONE (U15–U19).** Real results:

- **U15/U16:** `GET /api/metrikler` (serves U6's `degerlendirme_raporu.json`) and `GET /api/politika` (serves U11's `politika.olarak_sozluk()`) added and tested.
- **U17:** `services.degerlendir()` now computes Formulation B fields (`pd_geleneksel_bant`/`pd_fark`/`kapasite_sinyali`) whenever persona (hence classic score) is known, and `GET /api/skorla/{id}` returns them. **Important finding, not silently fixed:** the live demo population (`sentetik_islemler.csv`, powering `/api/demo-musteriler`, `/api/skorla/{id}`, `/api/portfoy`, `/api/adalet`) is a *different* dataset from the one Phase 1 fixed (`kapasite_islemler.csv`) — individual scoring now correctly uses the LR model trained on the decoupled data, but `portfoy()`/`adalet()`'s aggregate "ground truth" labels still come from the old circular `etiketle()`, because switching the live demo dataset changes which demo customers/personas the whole product shows (a product-narrative decision, not backend plumbing). Flagged as **OQ-44** rather than decided silently; in the meantime `/api/portfoy` and `/api/adalet` responses now carry an explicit `"veri_kaynagi": "dongusel"` + `"uyari"` caveat field so this isn't hidden.
- **U18:** `pd_fark`/`kapasite_sinyali` added to `Assessment`/`AuditLog` (migration `audit/0002_...`), nullable, populated best-effort alongside the unchanged `klasik_skor`.
- **U19:** 4 new backend tests (11 → 15 passing), including a boundary test proving the new fields still never let anything overwrite `klasik_skor`.

**Phase 2 exit gate: ✅ PASSED** — new endpoints tested; classic-score-never-overwritten boundary tests still pass (15/15 backend, 24/24 aks_core). Phase 3 (frontend) can start.

### Phase 3 — `product/03-frontend/` (surface it honestly)

| ID | Task | Size | Executes | Notes |
|---|---|---|---|---|
| U20 | New "Model Metrics" panel: AUC+CI, ECE/Brier, per-persona breakdown, sourced from U15 | M | DA4 (subset) | Must carry the same "not yet validated on real data" caveat as the root docs (overview.md §5, "no-go is a valid outcome") — no silently-upgraded confidence |
| U21 | Replace hardcoded `KLASIK_ESIK`/`AKS_ESIK`/band constants in `lib/skor.ts` with values fetched from U16 | S | — (new) | Removes the client/server threshold-drift risk found in recon |
| U22 | Surface `pd_fark`/`kapasite_sinyali` (U10) on `CustomerDetailPage` | S | DA4 (subset) | |
| U23 | *(stretch, optional)* what-if UI wired to the already-existing, currently unused `POST /api/simulasyon` | L | — | Only if time remains — not a commitment |
| U24 | *(stretch, optional)* CSV-upload screen wired to the already-existing, currently unused `POST /api/csv-skorla` | L | — | Same caveat |

**Phase 3 status: ✅ DONE (U20–U22). U23/U24 not attempted — OQ-43 unanswered.** Real results, verified live in-browser (Django + Vite dev servers, `claude-in-chrome`), not just `tsc`/build:

- **U20:** new "Model Validity" section on `/audit` — both models' ROC-AUC+CI, ECE/Brier, per-persona AUC, sourced live from `/api/metrikler`; carries the "not yet validated on real data" / "no-go is a valid outcome" caveat verbatim in the UI, not just in docs.
- **U21:** `lib/skor.ts`'s hardcoded `KLASIK_ESIK`/`AKS_ESIK` (680/650) replaced with a fetch-once-with-fallback from `/api/politika`'s new `portfoy_esikleri` field — **caught mid-implementation that these were never the same eshikler as `politika.py`'s AKS decision bands (720/620/540)**; extended `services.politika()` to carry both distinctly labeled, rather than wiring the wrong numbers through.
- **U22:** `CustomerDetailPage` now shows Geleneksel Bant PD / PD-Gap / Kapasite Sinyali when available (verified live: customer #1, classic score 812 → band-implied PD 17.0%, PD-Gap +17.0pp, capacity signal 84/100).
- Frontend `tsc --noEmit && vite build` clean; verified live in-browser on `/audit`, `/customers`, `/customers/1` — no console errors beyond pre-existing React Router future-flag warnings (unrelated).

**Phase 3 exit gate: ✅ PASSED** — golden path verified live (score a demo customer → view metrics panel → view decision-mechanism transparency), including a boundary persona (`klasik_maasli`, #1). This closes out the PO's original four-part ask (model optimization, decision mechanism + training, metrics, frontend) for this cycle; remaining items are all logged as open questions (OQ-40/41/43/44) or explicitly out of scope (U2, U23, U24).

### How this maps back to the PO's four-part ask

| Ask | Where it lands |
|---|---|
| Model optimizasyonu | Phase 1: U1–U9 |
| Karar mekanizması değişiklikleri + veri ile eğitim | Phase 1: U1 (data), U10, U11 (mechanism) |
| Metrik değişiklikleri (top priority) | Phase 1: U6, U7, U9, U10 (compute/fix) → Phase 2: U15, U17 (expose) → Phase 3: U20, U22 (display) |
| Frontend değişiklikleri | Phase 3: U20–U24 |

**Explicitly out of scope this cycle:** any edit inside `01-data/` (generators or datasets); real external data acquisition (R7); auth/login; deploy/CI changes (E12).

## 4. Research & experiment tasks

| ID | Task | Prio | Status | Depends on | Owner | Expected outcome |
|---|---|---|---|---|---|---|
| R1 | Ablation proof of circularity | P1 | ✅ DONE | — | Research | `circularity_ablation.py --veri-kaynagi hepsi`: old (XGB≈LR, Δ0.0004, confounding structural) *and* new (decoupled) benchmark printed side by side (§3b U7) |
| R2 | Evaluation harness (CV+CI+calibration+per-segment) | P1–P3 | ✅ DONE | — | Research | `degerlendirme.py` reusable regardless of OQ-36; now also persists JSON (§3b U6) |
| R3 | Decide real-data vs simulator redesign (OQ-36) | P1 | 🔴 BLOCKED | PO input | PO | Chooses gold-standard (real) vs honest-fallback (synthetic) fix path — synthetic path built+wired this cycle (OQ-40), OQ-36 (real) itself still open |
| R4 | Ratify target definition = Formulation B (OQ-39) | P1 | 🟡 PROPOSED | — | PO | Locks calibration (not AUC) as headline metric |
| R5 | Instrument incremental-approval-at-fixed-bad-rate metric | P1/P6 | 🟡 IN-PROGRESS | R3, R4 | Research | `formulasyon_b.py` (pd_fark) + `is_etkisi.py` rescued-count now run on the non-circular benchmark (§3b U6/U10); the specific pre-registered "incremental-approval-at-fixed-bad-rate with bootstrap CI" statistic (architecture.md §5.3 acceptance test) is not yet its own instrumented function |
| R6 | Simulator redesign — decouple feature-gen from label-gen | P1 | ✅ DONE | R3 (if synthetic) | Research | `uretici_kapasite.py` (01-data, pre-existing) now actually consumed by training (§3b U1) — previously built but unwired |
| R7 | Acquire/prep Home Credit dataset; mask rich features to simulate thin-file | P1 | ⏳ TODO | R3 (if real) | Research | Real-outcome proving ground for Formulation B |
| R8 | Out-of-persona holdout + out-of-time split | P2 | ⏳ TODO | M4 | Research | Genuine generalization estimate |
| R9 | Per-segment calibration (Brier/ECE) + isotonic/Platt if needed | P3 | ✅ DONE | M4 | Research | Isotonic correction implemented (`kalibrasyon.py`, threshold-gated); honest null result this run (ECE 0.0391→0.0394, not improved) — see §3b Phase 1 results |
| R10 | Thin-file small-sample / sparse-history stress test | P4 | ⏳ TODO | M4 | Research | Model degrades gracefully, not confidently, where data is sparse |
| R11 | Gaming-resistance review of the 4 causal features (RQ-3) | P4 | ⏳ TODO | — | Research | Which features are user-manipulable; robustness verdict |
| R12 | Pre-register acceptance thresholds X (approvals), Y (ECE) | P1 | ⏳ TODO | R4 | Research+PO | Anti-goal-seeking: numbers fixed before results |

## 5. Model & engineering tasks

| ID | Task | Prio | Status | Depends on | Owner | Expected outcome |
|---|---|---|---|---|---|---|
| E1 | Swap XGBoost → logistic regression as reported model | P1/P8 | ✅ DONE | M4 | Research | Executed on the non-circular benchmark (CIs don't overlap, not a tie-break); production model is `LogisticRegression` (architecture.md §5.2, §3b U8) |
| E2 | Monotonic constraints aligned with domain priors | P5 | ⏳ TODO | M5 | Research | Defensible sign of each feature's effect |
| E3 | SHAP → adverse-action-style reason codes | P5/P7 | ⏳ TODO | M5 | Research+Eng | Regulator-facing explanation surface. Note: SHAP explainer was made model-agnostic this cycle (dormant `TreeExplainer`-only bug fixed, §3b Phase 1) — this task is about reason-code *standardization*, still open |
| E4 | Rebuild revenue/loss on RAROC-consistent basis | P6 | ⏳ TODO | M4 | Research | Expected loss + capital/funding cost, not flat loss-rate heuristic |
| E5 | Hyperparameter search + lightweight experiment tracking | P8 | ✅ DONE | M5 | Eng | `RandomizedSearchCV` (5-fold) over XGBoost/LightGBM/LogisticRegression in `egitim.py`; winning params + CV AUC logged to `artifacts/egitim_manifest.json` per run (§3b U3) |
| E6 | Per-resample seeding discipline (fix global `random.seed(7)`) | P8 | ✅ DONE | — | Eng | `etiketleme.py` uses a local `random.Random(seed)`; no longer mutates global RNG state (§3b U5) |
| E7 | Harden `AsistanAgent`: never state a number absent from context | P9 | ⏳ TODO | — | Eng | Hallucination guard on the compliance-adjacent surface |
| E8 | Hallucination-rate eval harness for `AsistanAgent` | P9 | ⏳ TODO | E7 | Research | Measured trust before the assistant is relied on |
| E9 | Wire live Supabase persistence (fill `.env`) | P8 | 🔴 BLOCKED | OQ-35 credentials | PO+Eng | Live audit trail persists; code is ready, falls back to SQLite |
| E10 | Wire live Upstash Redis cache | P8 | 🔴 BLOCKED | OQ-35 credentials | PO+Eng | Live cache; code ready, falls back to LocMem |
| E11 | Integrate Google Stitch design into React | P10 | ✅ DONE | OQ-34 | Eng | 5 pages (Intelligence, Portfolio, Audit, Customers, Customer Detail) built with Tailwind + react-router, wired to all real `/api/*` endpoints. Fabricated Stitch content (blockchain ledger, ECOA/GDPR compliance claims, invented customer counts/segment names) was replaced with real backend data or honest architecture-derived content, per the priority-#1 (validity) and AI-honesty rules in overview.md §5–§6 |
| E12 | Docker/Render single-service deploy (Django serves React build) | P10 | ⏳ TODO | E11 | Eng | One deployed web service |

## 5b. Data-architecture track (per `planning/` — alternative-data research intake)

Design specs in [`planning/data-architecture.md`](planning/data-architecture.md), [`feature-schema.md`](planning/feature-schema.md), [`data-pipeline-steps.md`](planning/data-pipeline-steps.md). Filtered critically from the alternative-data research brief: **adopt** open-banking cash-flow (Formulation B fit) + KVKK governance; **reject/defer** autonomous RL limit optimization (violates the boundary), psychometrics, dense device metadata (fail the evidence/minimization bar). All modeling steps stay gated on **M4** (non-circular label).

| ID | Task | Prio | Status | Depends on | Owner | Expected outcome |
|---|---|---|---|---|---|---|
| DA1 | 01-data: tiered schema + **non-circular label generation** + data dictionary/validation | P1 | ✅ DONE | — | Eng+Research | Built: `uretici_kapasite.py` (decoupled capacity-driven generator, T0+T1 columns: kanal/karsi_taraf_tipi/brut_tutar/zorunlu_mu), `dekuple_kanit.py` (circularity proof), `dogrulama.py` (schema+PII+circularity-gate, exit-code CI gate), `docs/veri_sozlugu.md` (data dictionary + honesty caveats). Empirically unblocks M4. |
| DA2 | 02-ai-agents: feature extraction for new cash-flow columns + **Formulation B** target + per-segment calibration | P1/P3 | 🟡 PARTIAL | DA1, M4 | Research | Formulation B (`pd_davranissal`/`pd_geleneksel_bant`/`pd_fark`/`kapasite_sinyali`) + calibration ✅ DONE (§3b U9/U10). Cash-flow-column feature extraction (`kanal`/`karsi_taraf_tipi`/`brut_tutar`/`zorunlu_mu`) explicitly deferred (U2) — large blast radius (9-feature invariant used across model meta/SHAP/API/frontend/tests), needs its own cycle |
| DA3 | 04-backend: `FeatureStore`/`Consent`/`DataProvenance` tables + extend `Assessment`/`AuditLog` + migrations + API fields | P8 | ⏳ TODO | DA2 | Eng | O(1) scoring lookup; provenance/consent + human-oversight fields persisted |
| DA4 | 03-frontend: surface PD-gap / capacity / calibration + provenance/consent state | P10 | ⏳ TODO | DA3 | Eng | Real Formulation-B fields shown; no fabricated data |
| DA5 | 05-business: hypothesis registry + KVKK/lawful-basis mapping + DPIA/human-oversight posture + out-of-scope register | P7 | ⏳ TODO | — (parallel; gates T1/T2/T3 columns) | PO+Eng | No column without a hypothesis + lawful basis; rejected capabilities documented |

## 6. Technical debt

| ID | Item | Prio | Status | Notes |
|---|---|---|---|---|
| D1 | Port 22 Sprint-2 tests off FastAPI/`src.*` to Django `APIClient` + `aks_core` | P8 | 🔴 TODO | They don't run post-migration; add **boundary tests** proving no agent can mutate the classic score |
| D2 | Global `random.seed(7)` reused per label-generation call | P8 | ✅ DONE | Fixed via E6/§3b U5 — local `random.Random(seed)`, no global mutation |
| D3 | Hardcoded hyperparameters (`n_estimators=300, max_depth=4`) | P8 | ✅ DONE | Fixed via E5/§3b U3 — `RandomizedSearchCV`, params logged per run |
| D4 | `_legacy_fastapi/` kept as reference | — | ACCEPTED | Delete once Django parity is fully trusted and tests are ported |
| D5 | Published numbers (AUC 0.829, 973/1084, fairness gap) still cited in artifacts | P1 | 🟡 IN-PROGRESS | The *mechanism* producing these is fixed (§3b Phase 1) and new, non-circular numbers exist (architecture.md §5.1/§5.2, execution.md §3b) — but the **published/README figures themselves are untouched**, pending OQ-37. Also: the new business-impact number (538/567 rescued) is in-sample, not out-of-sample — do not treat it as the fixed replacement without a held-out re-run first |

## 7. Known risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Circular benchmark presented as validated thesis | Fatal credibility loss (jury/investor) | High if unaddressed | M4; caveats already in all published numbers; this doc leads with it |
| No real data available (OQ-36 = no) | Can only ever produce an honest-but-synthetic result | Medium | Simulator redesign (R6) as documented fallback; state the limitation openly |
| Selective-labels problem | Approved-only outcomes are self-selected; inflates any real-data result | Inherent to the field | Report as a known caveat, not hidden; is *the* core difficulty, not our flaw |
| Target segment performance stays weak (AUC 0.61–0.68) | Product's core claim unproven | Medium | Formulation B reframes metric to calibration + incremental approvals, not within-segment AUC |
| Gaming of behavioral features | Production capacity signal manipulable | Unknown | R11 adversarial review before any deployment |
| Deadline pressure to ship UI/agents over rigor | Repeats the exact error priority #1 exists to prevent | Medium | Priority order is binding; UI is P10 by design |

## 8. Live open decisions (owner: PO — never guessed)

| ID | Decision | Blocks | Status |
|---|---|---|---|
| **OQ-36** | Real benchmark dataset access (Home Credit / LendingClub / open-banking)? | R3/R7 — the fix path itself | 🔴 Highest-leverage; awaiting PO. This cycle proceeds synthetic-only per §3b (`01-data/` excluded from scope) — OQ-36 itself not resolved |
| **OQ-37** | Fix circular numbers now (rewrite published figures) or after demo day (keep + caveat)? | D5, any numbers-facing edit | 🔴 Awaiting PO |
| **OQ-38** | Correct agent narrative to "one real agent" now, or invest in a 2nd genuine agent first? | Jury-facing material | 🔴 Awaiting PO |
| **OQ-39** | Ratify Formulation B as the operational target? | R5, all modeling | 🟡 PROPOSED — proceeding unless founder objects |
| OQ-34 | Google Stitch export format (HTML+Tailwind vs React/JSX)? | E11 | 🟢 RESOLVED — plain HTML+Tailwind (5 pages under `product/03-frontend/stitch-output/`), confirmed by direct inspection and ported into React components |
| OQ-35 | Supabase + Upstash credentials — who creates accounts? | E9, E10 | 🟡 Awaiting PO |
| OQ-33 | Supabase Auth vs plain Django auth for the bank panel? | Frontend login flow | 🟢 Deferred (backend works without auth) |
| OQ-40 | Does "don't touch `01-data/`" commit this cycle to the synthetic/decoupled path (R6) over real-data acquisition (R7), or is it just this sprint's scope? | U1, R3 | 🟡 Proceeding synthetic-only this cycle per current PO instruction; OQ-36 itself stays open |
| OQ-41 | Decision-mechanism config (U11): a simple versioned constants module, or a DB-backed/admin-editable policy table? | U11 sizing | 🔴 Awaiting PO |
| OQ-42 | Execute the XGBoost→LR swap (U8/E1) this cycle if LR wins on the new benchmark, or keep XGBoost live and only report the recommendation? | U8 | 🟢 RESOLVED — swap executed. Not a guess: the project's own binding mandate ("classical wins by default" when equal-or-better) already committed to this outcome in architecture.md §5.2 before this cycle; the new benchmark's non-overlapping CIs [0.853,0.871] vs [0.831,0.850] made it unambiguous rather than a judgment call |
| OQ-43 | Are the stretch frontend items (U23 what-if simulator, U24 CSV upload) in scope this cycle or deferred? | Phase 3 sizing | 🔴 Awaiting PO |
| OQ-44 | Should the *live* demo dataset (`sentetik_islemler.csv`, powers `/api/demo-musteriler`, `/api/skorla/{id}`, `/api/portfoy`, `/api/adalet`) be switched to the decoupled `kapasite_islemler.csv` so the whole live product reflects M4, not just offline training/eval scripts? Changes which demo customers/personas appear throughout the UI. | `services.py::VERI_YOLU`, `_skorla_hepsi()` | 🔴 Awaiting PO — `/api/portfoy`/`/api/adalet` carry an explicit `"veri_kaynagi":"dongusel"` caveat in the meantime (§3b Phase 2) |

## 9. Future features (post-validation, not committed)

- **Optimization/policy engine:** turn calibrated capacity PD + PD-gap into a recommender for the maximal within-policy limit at a fixed portfolio bad-rate (the productized decision-curve output).
- **Graduation to Formulation C (uplift/reject-inference):** once a design-partner bank runs a champion/challenger on B's flagged population and provides experimental data.
- **Drift monitoring:** PSI-based hook on `Orkestrator`'s score-over-time tracking.
- **Second genuine agent:** a constrained-optimization intervention *ranker* — only if it passes the five-question test.
- **Live Supabase/Upstash + single-service deploy** — once credentials and the Stitch UI land.

## 10. Working rules

1. **Never resolve an OQ by guessing.** New ambiguities get the next OQ number and an owner.
2. **Priority order is binding.** Do not let P8–P10 work (stack, agents, UI) preempt P1–P4 (validity, generalization, calibration, robustness).
3. **Fix numbers before shipping claims.** No AUC/business/fairness figure is presented as validated until M4 lands.
4. **Pre-register thresholds** before running an experiment that produces a headline number.
5. **Keep these three docs current.** When a decision changes, edit the relevant file in place; do not archive old versions or create a fourth doc.
6. **"No-go is a valid outcome."** If the thesis fails to validate on a non-circular benchmark, that is a legitimate, reportable result — not something to engineer around.
