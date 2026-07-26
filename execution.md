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
| M6 | Demo-ready product | Stitch UI integrated, deploy live, agent narrative honest | 🟡 IN-PROGRESS — Stitch UI integrated (E11); user portal + institution portal live with consent-gated access (§3b Phase 6/7); two real agent components added (`belge_agent.py`, `danisman_llm.py`, §3b Phase 7/7.5) alongside the still-honestly-labeled deterministic pipeline steps — agent narrative is now partially, not fully, corrected (OQ-38 stays open for the jury-facing framing); deploy-live (E12) still TODO |

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

**Phase 3 status: ✅ DONE (U20–U24). OQ-43 fully resolved — PO chose to build both stretch items.** Real results:

- **U20:** new "Model Validity" section on `/audit` — both models' ROC-AUC+CI, ECE/Brier, per-persona AUC, sourced live from `/api/metrikler`; carries the "not yet validated on real data" / "no-go is a valid outcome" caveat verbatim in the UI, not just in docs.
- **U21:** `lib/skor.ts`'s hardcoded `KLASIK_ESIK`/`AKS_ESIK` (680/650) replaced with a fetch-once-with-fallback from `/api/politika`'s new `portfoy_esikleri` field — **caught mid-implementation that these were never the same eshikler as `politika.py`'s AKS decision bands (720/620/540)**; extended `services.politika()` to carry both distinctly labeled, rather than wiring the wrong numbers through.
- **U22:** `CustomerDetailPage` now shows Geleneksel Bant PD / PD-Gap / Kapasite Sinyali when available (verified live: customer #1, classic score 812 → band-implied PD 17.0%, PD-Gap +17.0pp, capacity signal 84/100).
- **U24:** new `/upload` page (`CsvUploadPage.tsx`) wired to the previously-unused `POST /api/csv-skorla` — drag/drop or file-picker CSV upload, downloadable example CSV, renders AKS score/karar/limit + SHAP factors + danışman notes. `api.ts` got a `postDosya()` multipart helper (no manual `Content-Type`, so the browser sets the boundary) and a `CsvSkorSonuc` type intentionally narrower than `SkorSonuc` — no `klasik_skor`/Formülasyon B fields, since an uploaded statement has no known bank score. Verified two ways: (1) `curl` multipart POST against a running Django server — real 200 with a real AKS score, SHAP factors, advisor text; (2) live in `claude-in-chrome` on `http://localhost:5174/upload` — real file selected via the actual `<input type=file>` (DataTransfer-backed, not mocked), "Skorla" clicked, UI rendered the same score (AKS 850, düşük risk, 42.500 TL) with SHAP cards; also drove the error path (CSV missing required columns) and confirmed the red error banner shows the backend's exact `hata` message and clears stale results. Screenshot capture itself was broken in this session's extension (script-injection timeout), so this was DOM/console-verified rather than pixel-verified — no console errors beyond the pre-existing React Router future-flag warnings. `tsc --noEmit` clean.
- **U23:** new "Senaryo Simülatörü (What-If)" section on `CustomerDetailPage`, wired to the previously-unused `POST /api/simulasyon` — 9 sliders (one per behavioral feature, ranges calibrated off observed min/max in the synthetic dataset), debounced (400ms) live re-scoring, mevcut/senaryo score comparison with delta + resulting `karar`, "Sıfırla" reset. Also hardened `api.ts`'s generic `post()` to surface the backend's real `hata` message on failure (previously just `status statusText`) — benefits `simulasyon` and every other POST caller, including the pre-existing `asistan` endpoint. Verified live in `claude-in-chrome` against customer #1: dragging the gider/gelir oranı slider (via a real dispatched `input`/`change` event on the native slider, not a mocked call) from its baseline to 4.0 dropped the score from 850 → 300 with karar flipping to "ek teminat/gözden geçirme önerilir" — confirms the model responds in the correct direction, not just that the request succeeds; "Sıfırla" correctly reverted to 850 with no diff. No console errors.
- Frontend `tsc --noEmit && vite build` clean.

**Phase 3 exit gate: ✅ PASSED for U20–U24** — golden path verified live in-browser for all five (score a demo customer → view metrics panel → view decision-mechanism transparency → upload a statement → run a what-if scenario), incl. boundary persona `klasik_maasli` #1. This closes out the PO's original four-part ask (model optimization, decision mechanism + training, metrics, frontend) for this cycle; remaining items are all logged as open questions (OQ-40/41/44) or explicitly out of scope (U2).

### How this maps back to the PO's four-part ask

| Ask | Where it lands |
|---|---|
| Model optimizasyonu | Phase 1: U1–U9 |
| Karar mekanizması değişiklikleri + veri ile eğitim | Phase 1: U1 (data), U10, U11 (mechanism) |
| Metrik değişiklikleri (top priority) | Phase 1: U6, U7, U9, U10 (compute/fix) → Phase 2: U15, U17 (expose) → Phase 3: U20, U22 (display) |
| Frontend değişiklikleri | Phase 3: U20–U24 |

**Explicitly out of scope this cycle:** any edit inside `01-data/` (generators or datasets); real external data acquisition (R7); auth/login; deploy/CI changes (E12).

### Phase 4 — Unsupervised learning integration (PO-directed extension)

PO's ask, verbatim (paraphrased from Turkish): retrain/improve the model using more/broader data, **combined with unsupervised learning**; PO's own model preference is logistic regression (already in production per U8), but wanted a genuine second opinion on alternatives.

**Scoping decision, made explicitly rather than guessed:** "model çıktılarına göre modeli eğitmeliyiz" (retrain based on model outputs) was interpreted as *periodic retraining on new real labeled data*, **not** as pseudo-labeling/self-training on the model's own predictions — the latter is a textbook goal-seeking trap (the model reinforcing its own errors, exactly the failure mode `etiketleme.py`'s circularity already demonstrated once — architecture.md §5.1) and isn't defensible under the project's anti-goal-seeking mandate (§10 rule 5). Real external data acquisition is still blocked on R3/R7/OQ-36 (no real data exists yet); no `01-data/` edit was made. Two concrete, honest, **auxiliary** (not decision-overriding) unsupervised components were built instead:

| ID | Task | Size | Notes |
|---|---|---|---|
| U25 | Anomaly/out-of-distribution (OOD) detection — `aks_core/model/anomali.py`, IsolationForest fit on train-split features, transparency signal only | M | Passes the five-question test as a deterministic auxiliary statistical component (same category as SHAP), not an agent; never changes score/decision (boundary, overview.md §7) |
| U26 | Unsupervised segment discovery — `aks_core/model/segmentasyon.py`, K-Means (k=2..6 swept by silhouette score) over the 9 behavioral features, offline research report | M | Explicitly NOT wired into any scoring/decision path — same "research script" category as `is_etkisi.py`/`degerlendirme.py` |

**Phase 4 status: ✅ DONE (U25, U26).** Real results:

- **U25 (anomaly/OOD):** `IsolationForest(n_estimators=200, contamination=0.05)` fit on the same `Xtr` split `egit()` already uses (no leakage — same OOF discipline as calibration/Formulation B), persisted portably via joblib (`artifacts/anomali_model.joblib`, ~2.7MB) — safe cross-platform like the existing LR persistence (pure sklearn/NumPy state, no XGBoost-style C++ buffer). Wired into `SkorlamaAgent.calistir()` as optional fields (`anomali_bayrak`, `anomali_skoru`) — loads via `anomali.yukle()` which returns `None` gracefully if the artifact is absent, mirroring the existing calibration-optional pattern; scoring never breaks if it's missing. Propagated explicitly through `Orkestrator.degerlendir()`'s whitelist dict (that dict does NOT spread `skor`, so both new keys had to be added there by hand — caught this by reading the code rather than assuming a spread) and through `views.py`'s `skorla_demo`/`skorla`/`csv_skorla` response dicts. Surfaced in the frontend as an amber "Atipik Profil (OOD)" badge on `CustomerDetailPage` and as a banner on `/upload`'s result. **Verified live, both ends of the flag:** re-ran `python -m aks_core.model.egitim` end-to-end (deterministic — reproduced the exact same LR AUC 0.8499 and ECE 0.0391→0.0394 as the pre-existing manifest, confirming no regression) then queried `/api/skorla/{id}` across a spread of demo customers — #200 came back flagged (`anomali_bayrak: true`, tipiklik −0.5745) and rendered the badge correctly in `claude-in-chrome`; the small hand-written example CSV used for U24 testing also flags true via `/api/csv-skorla` (6 transactions is itself an atypical shape relative to the ~150-txn training customers) and rendered correctly on `/upload` too.
- **U26 (segmentation):** `python -m aks_core.model.segmentasyon` on the dekuple dataset selected **k=3** (silhouette 0.389 — moderate separation, not sharp). Honest finding, not smoothed over: the discovered clusters cleanly separate `ogrenci_yuksek_hacim` (590/590 pure) and mostly separate `klasik_maasli` (579/582), but **`stajyer_degisken_gelir` and `dusuk_hacim_riskli` collapse into the same cluster** (531 + 286 mixed) — unsupervised discovery does *not* cleanly rediscover all 4 hardcoded personas from behavioral features alone. Per-cluster default rates are also nearly flat (16.8–17.5%) — clustering on these 9 features doesn't separate risk either. This is a real, unflattering result reported as-is (consistent with "no-go is a valid outcome"), not cherry-picked. New `GET /api/segmentasyon` endpoint (503 + instruction if the report hasn't been generated, same pattern as `/api/metrikler`) and a new "Segmentasyon (Denetimsiz Keşif)" panel on `/audit` — verified live, 3 cluster cards rendered with size/default-rate/persona-mix, no console errors.
- **Model-choice second opinion (PO explicitly invited this):** logistic regression is confirmed as the right call, not deferred-to — it's already winning the non-circular benchmark on non-overlapping CIs (Phase 1). Recommendation: keep XGBoost/LightGBM in `egit()`'s search pool (already true) rather than removing them, since real data (once R7/OQ-36 unblocks) may not be linear the way the synthetic generator is — but don't swap production away from LR without a repeat of the same CI-based comparison that justified U8.
- Tests: `aks_core` 24/24 still passing (no new tests added for U25/U26 — both are opt-in auxiliary signals with no behavior change to existing scoring paths when the artifacts are absent; `python manage.py test` 15/15 still passing).

**Phase 4 exit gate: ✅ PASSED** — both components verified live in-browser (not just via API), boundary re-confirmed (neither anomaly detection nor segmentation can write to `klasik_skor` or change `karar` — they're additive fields only), no regression in the existing model/test suite.

### Phase 5 — Generalization & robustness (R8, R10, R11)

**Why this phase, and why now:** after Phase 4 (unsupervised/AI-adjacent work, priority #9), the binding priority order (overview.md §5) says P2 (generalization) and P4 (robustness) rank *above* that — R8/R10/R11 were already open, unstarted backlog items sitting at those higher priorities. Picked as the next phase specifically to catch the project back up the priority order rather than continuing further down it, not guessed — same rationale documented here for anyone auditing scope decisions later.

New module: `aks_core/model/genelleme_saglamlik.py`, persists `artifacts/genelleme_saglamlik_raporu.json`, served via new `GET /api/genelleme-saglamlik` (503-until-generated, same pattern as `/api/metrikler`/`/api/segmentasyon`), surfaced in a new "Genelleme & Sağlamlık (R8/R10/R11)" panel on `/audit`.

**Phase 5 status: ✅ DONE.** Real results, not illustrative:

- **R8 (out-of-persona holdout):** each of the 4 personas held out entirely from training in turn (fresh `LogisticRegression(C=1.0)`, same hyperparameter as production, refit on the remaining 3 personas), then tested on the never-seen persona. Result: AUC 0.857–0.881 across all four held-out personas — close to the random-k-fold benchmark (0.862), meaning the model is **not** persona-memorizing; it generalizes to a behavioral profile it never trained on. A genuinely reassuring finding, not asserted without the test.
- **R8 (out-of-time split): explicitly NOT done, with reason, not silently skipped.** Checked first: every customer's transactions in `kapasite_islemler.csv` span the same 6-month window (2026-01-01 to 2026-06-29) — the generator doesn't simulate temporal drift, so an early-customers-vs-late-customers split would only measure generator randomness, not real-world time drift. A genuine out-of-time test needs real data (OQ-36). Reported as an honest gap in the JSON report (`out_of_time_split.durum`), not faked.
- **R10 (thin-file stress test):** 150 sampled customers scored on their full history, then re-scored on just their first K transactions (K=5,8,12,20,40); measured both score drift from the full-history score and how often the anomaly detector (U25) flags the truncated profile. Result — **graceful, not overconfident, degradation:** at K=5, mean absolute score drift is 190 points and the anomaly detector flags **100%** of them; drift shrinks and the flag rate falls smoothly as K grows (K=40: drift 78 points, flag rate 14%). This is the two Phase 4/5 components cross-validating each other: the model doesn't confidently output a wrong score for a thin file — the auxiliary OOD signal correctly catches that it's operating outside its comfort zone.
- **R11 (gaming-resistance, RQ-3's first quantitative answer):** each of the 4 causal features perturbed by a fixed 25% "improvement" (200 sampled customers), average resulting AKS score gain measured. Result, **not smoothed over:** `gider_gelir_orani` (expense/income ratio) is a clear outlier — average **+73 points**, p90 **+265 points** — versus `fatura_odeme_duzeni` (+6), `bakiye_trendi` (+1), `gelir_duzenliligi` (−2, noise-level). This is a real, actionable finding: the single feature the model leans on most for score movement is also the one most plausibly cheap to manipulate (spend less / route income differently for a short window) — flagged as a concrete robustness risk, not just a theoretical RQ-3 mention. **Recommendation, not yet executed (new open decision):** either down-weight `gider_gelir_orani`'s influence (e.g. monotonic-constraint cap, per the already-planned interpretability work in architecture.md §8) or corroborate it with a longer observation window / an independent signal before it alone can swing a decision band.
- Tests: `aks_core` 24/24 still passing, `04-backend` 15/15 still passing — no existing behavior changed, this phase only added new opt-in read paths.
- **Bug caught and fixed during implementation, not shipped:** first draft of `genelleme_saglamlik.py` manually called `scaler.transform()` before passing features to the loaded model — but `kayit.py`'s LR wrapper (`OlcekliLojistikSarmalayici.predict_proba`) already scales internally (same as `SkorlamaAgent.calistir()` does — it passes raw vectors). This would have silently double-scaled every R10/R11 score. Found by reading `kayit.py` before trusting the first draft's numbers, fixed before the run that produced the results above.

**Phase 5 exit gate: ✅ PASSED** — new endpoint + panel verified live in `claude-in-chrome` (3 cards render: R8 per-persona AUC table, R10 drift/anomaly-rate table, R11 sensitivity bars), no console errors, full test suite green.

### Phase 6 — User portal (market-facing, two interfaces)

PO's ask, verbatim (paraphrased): a real user-side login where a user uploads their own data, gets it analyzed, and sees the result — moving toward market, with **two separate interfaces**: one the bank uses, one the end user uses.

**Two architecture decisions asked of the PO before starting (not guessed — this exact question was already an open item, OQ-33):**
1. Auth backend: **Django's own session auth** (chosen) over Supabase Auth (would need credentials that are currently blocked, OQ-35).
2. Interface separation: **same React app, separate route/nav section** (chosen, `/portal/*`) over a second standalone frontend app.

**What was built:**

*Backend:*
- `Assessment.user` FK added (`audit/migrations/0003_assessment_user.py`) — nullable, only ever set for `kaynak="portal"` rows; bank/demo scoring paths are completely unaffected (`user=None` always for them).
- `services.csv_ayristir()` — extracted the CSV column/row-validation logic that used to live only inside the `csv_skorla` view, so the new authenticated upload path doesn't duplicate it. `csv_skorla` itself got shorter as a result (refactor side-effect, not scope creep — same behavior, verified by the existing `04-backend` test suite staying green).
- `services.degerlendir()` gained an optional `user=` param, threaded through to `_denetim_yaz()` — only sets `Assessment.user` when the caller is authenticated.
- New `api/auth_views.py`: `GET /api/auth/ben` (session check, also `@ensure_csrf_cookie`-decorated so the frontend always has a CSRF cookie to work with), `POST /api/auth/kayit` (register — email/password/name, `django.contrib.auth`'s built-in PBKDF2 hashing, `AUTH_PASSWORD_VALIDATORS` now enforces an 8-char minimum where it used to be empty), `POST /api/auth/giris` (login), `POST /api/auth/cikis` (logout, `IsAuthenticated`-gated).
- New `api/portal_views.py`: `POST /api/portal/yukle` (authenticated CSV upload → score, `kaynak="portal"`, tied to `request.user`), `GET /api/portal/gecmis` (the logged-in user's own history only — `Assessment.objects.filter(user=request.user)`).
- **Bug found and fixed during live testing, not shipped broken:** Django 4+'s CSRF middleware checks the request's `Origin` header against `CSRF_TRUSTED_ORIGINS`, separately from the cookie/header token match. The Vite dev proxy makes requests arrive at Django looking like they're on a different origin than what the browser sent — this 403'd every authenticated POST in `claude-in-chrome` even with a correct CSRF token, until `CSRF_TRUSTED_ORIGINS` was added (derived from the existing `CORS_ALLOWED_ORIGINS` env var, so no new config surface). Also caught `.env`'s existing `CORS_ALLOWED_ORIGINS` value not covering port 5174 (Vite's fallback port when 5173 is busy) — widened the default and the checked-in `.env`/`.env.example`.

*Frontend:*
- `api.ts`: `credentials: "same-origin"` added to every fetch helper (`get`/`post`/`postDosya`), a `csrfTokenAl()` cookie reader, `X-CSRFToken` header attached to state-changing requests, and a friendlier fallback error message ("Bu işlem için giriş yapmalısınız.") for bare 401/403 responses that don't carry a `hata` field.
- `components/PortalLayout.tsx` — separate nav/branding ("AKS Portal"), session-gates every child route (`api.ben()` on mount; redirects to `/portal/giris` if not authenticated), passes the user down via `<Outlet context={kullanici}>`.
- `pages/portal/PortalLoginPage.tsx` — combined login/register form (tab toggle), redirects to `/portal` if already authenticated.
- `pages/portal/PortalPage.tsx` — the user-facing "upload my own statement, see my score" screen (same visual language as the bank's `CsvUploadPage`, including the OOD/anomaly banner from Phase 4) plus a live "Geçmişim" (my history) list.
- `App.tsx` — new route tree: `/portal/giris` (public) and `/portal` (gated, under `PortalLayout`), fully separate from the bank's `Layout`-wrapped routes. A small "Kullanıcı Portalı" link was added to the bank nav for discoverability, and nothing was added going the other direction (the portal doesn't expose or link to any bank-internal page).

**Verified live end-to-end in `claude-in-chrome`, not just via curl:** register → auto-login → redirected to `/portal` → real file (`DataTransfer`-backed `<input type=file>`) uploaded → real score rendered with the OOD banner logic intact → "Geçmişim" shows the new entry → logout → direct navigation to `/portal` correctly bounces to `/portal/giris` (route guard confirmed, not just the login form) → bank-side nav link to `/portal` confirmed present. Full suite still green after all changes: `aks_core` 24/24, `04-backend` 15/15, `tsc --noEmit` clean.

**Deliberately not done this cycle, flagged rather than silently skipped:**
- No password-reset / email-verification flow (a real product would need one before public launch; this is a working demo-grade auth system, not yet hardened for a genuine market release).
- No KVKK/consent UI or data-retention policy on the portal upload (execution.md §5b DA5 was already open and TODO before this phase; real end-user PII upload makes it more urgent, not less — flagged as a new open decision below, not resolved by assumption).
- `Assessment.ozellikler` (JSON of the uploaded statement's derived features) is still stored for portal uploads exactly as it already was for demo/CSV/API scoring — no new data-minimization pass was done specifically for the portal path.

**Phase 6 exit gate: ✅ PASSED** for the two chosen architecture decisions (Django auth, same-app route split) — both implemented, both verified live. Compliance/consent hardening remains open (OQ-46) and should happen before any real (non-demo) user data is accepted.

### Phase 7 — Market sürümü: belge işleme, kimlik/rıza, risk iştahı, gerçek agent katmanı

PO's ask, verbatim (paraphrased): kullanıcılar PDF ekstre yükleyebilsin (CSV/Excel'e normalize edilip modele girsin); her kullanıcının kendi hesabı + "kimlik numarası gibi" bir AKS numarası olsun, şirketler bu numarayı müşteriden isteyebilsin; veri isim/soyisim tutulmadan bu numara üzerinden saklansın ama başkasının verisini yüklemek zorlaştırılsın; agent yapısı **gerçekten** doğrulanıp kullanılsın; bankalara **3 risk seviyesinde** (risksiz/orta/riskli) öneri üretilsin. "Veri kısmı çok önemli" vurgusu PO'nun kendi ifadesiyle kaydedildi.

**PO ile bu turda netleştirilen kararlar (tahmin edilmedi, soruldu):**

| Konu | Karar |
|---|---|
| Doküman | Bu bölüm `finalDecision.md` yerine buraya (execution.md §3b Phase 7) yazıldı — CLAUDE.md'nin "asla 4. doküman" kuralı korunuyor |
| Kimlik | **E-posta + telefon OTP.** TCKN/isim/soyisim YOK. Telefon yalnızca `HMAC-SHA256` hash'i olarak saklanır. AKS numarası rastgele üretilir, hiçbir kişisel veriden türetilmez |
| Erişim | **Müşteri onayı ile.** Kurum AKS no ile talep açar, müşteri onaylar/reddeder; onay süreli (varsayılan 30 gün) ve istenildiği an iptal edilebilir; her olay değiştirilemez rıza defterine yazılır |
| LLM | **Claude API + tool-calling.** Yapı kuruldu, `ANTHROPIC_API_KEY` PO tarafından sonra eklenecek (aşağıda TODO) — anahtarsız ortamda sıfır regresyonla eski deterministik yola düşer |

**Dürüstlük notu (bağlayıcı, plana da yazıldı):** "başkasının verisini yüklemeyi ENGELLEME" iddiası kasıtlı olarak yapılmadı — minimum kişisel veriyle (isim/TCKN yok) bir dosyanın gerçekten o kişiye ait olduğunu ispatlamak teknik olarak imkânsız. Ürün bunun yerine **tespit + izlenebilirlik + hesap verebilirlik** iddia ediyor: belge parmak izi çakışması, zorunlu sahiplik beyanı (zaman+IP ile rıza kaydına yazılır), davranışsal tutarlılık kontrolü. Gerçek çözüm (açık bankacılık — veri dosyadan değil bankadan yetkiyle gelir) üretim yolu olarak burada belgeleniyor, bu turda kurulmadı (yeni OQ-51).

#### 7.1 — Belge işleme hattı (PDF/Excel/CSV → model)

Yeni paket `aks_core/belge/` (`okuyucu.py`, `pdf_okuyucu.py` — pdfplumber, tablo→metin iki stratejili —, `tablo_okuyucu.py` — pandas/openpyxl, bulanık kolon eşleme —, `normalizer.py` — kanonik şema + kategori güveni —, `parmak_izi.py`, `kalite.py`). `services.csv_ayristir` yerini `services.belge_ayristir`'e bıraktı (geriye uyumlu sarmalayıcı korundu); `/api/csv-skorla` ve `/api/portal/yukle` artık CSV/XLSX/PDF üçünü de kabul ediyor (URL/adlandırma tarihsel nedenlerle "csv" kalmaya devam ediyor).

**İki kritik bulgu, sessizce geçilmedi:**
- `ozellik_cikar()`'ın 9 özelliğinden 2'si (`gelir_kaynagi_sayisi`, `fatura_odeme_duzeni`) doğrudan `kategori` alanına bağımlı — PDF/Excel'den kategori çıkarımı hatalıysa bu ikisi bozulur. Çözüm: `normalizer.py` her satır için bir kategori güveni üretir, ortalama `<0.6` ise `dusuk_kategori_guveni` bayrağı.
- Model **180 günlük** pencerede eğitildi; yüklenen bir PDF 3 aylık olabilir. `ozellik_cikar()` **DEĞİŞTİRİLMEDİ** (eğitim/servis tutarlılığı, P1 > her şey) — bunun yerine `kalite.py` pencere ±%35'ten fazla sapınca `pencere_uyumsuz` bayrağı üretiyor. Pencerenin gerçekten normalize edilmesi ancak modelin farklı pencere uzunluklarıyla yeniden eğitilmesiyle mümkün — **yeni OQ-52**.

`requirements.txt`/`pyproject.toml`'a `pdfplumber`/`pandas`/`openpyxl` **açıkça** eklendi (önceden kurulu ama beyan edilmemiş bağımlılıklardı). Test: `test_belge.py` (20 test) — aynı içeriğin CSV/XLSX/PDF hâllerinin **aynı parmak izini** verdiği, bozuk PDF'in anlamlı hata verdiği, kategori tahmin doğruluğunun ölçüldüğü doğrulandı.

#### 7.2 — Kimlik, rıza ve çok kiracılılık

Yeni Django app `kimlik/`: `Profil` (aks_no, telefon_hash), `TelefonDogrulama` (OTP, hash'li kod, 5 dk/5 deneme sınırı), `Kurum`, `KurumUyeligi`, `ErisimTalebi`, `RizaKaydi` (`audit.AuditLog` ile AYNI append-only desen — `save()`/`delete()` `RizaIhlali` fırlatır).

- **AKS numarası** (`kimlik/aks_no.py`): rastgele 45-bit → Crockford Base32 + checksum → `AKS-XXXX-XXXX-XC`. Hiçbir kişisel veriden türetilmiyor; kayıt anında (`auth_views.kayit`) otomatik üretiliyor.
- **Telefon** (`kimlik/telefon.py`): yalnızca `HMAC-SHA256(AKS_PEPPER, numara)` saklanıyor, `unique=True` (bir numara bir hesap — Sybil direnci). SMS sağlayıcısı yok — `DEBUG=True` iken kod API yanıtında görünür (**yeni OQ-47**: gerçek SMS sağlayıcısı).
- **Kiracılık zorlaması** (`kimlik/izinler.py`): `KurumUyesi` (DRF permission) + `aktif_riza()` (durum=`onaylandi` VE `gecerlilik_bitis > now`). Kurum kapsamlı her view ikisinden de geçiyor.
- `audit.Assessment` genişletildi: `profil` (FK, string referans `"kimlik.Profil"` — dairesel import yok), `belge_parmak_izi`, `sahiplik_beyani`, `sahiplik_bayraklari` (JSON), `kaynak_format`, `yukleme_ip`.
- Kurum onboarding **öz-kayıt değil**, kasıtlı olarak provizyonlanır — `kimlik/management/commands/bootstrap_kurum.py` demo kurum + personel oluşturur (**yeni OQ-53**: gerçek kurum onboarding süreci — sözleşme+manuel doğrulama mı, otomatik mi).

Test: `kimlik/tests.py` (17 test) — çapraz kurum sızıntısı yok, süresi dolmuş/iptal edilmiş rıza erişim vermiyor, `RizaKaydi` değiştirilemez, kayıt otomatik AKS no üretiyor; hepsi canlı Django test client ile (mock değil).

#### 7.3 — Sahiplik savunması (3 katman, TESPİT — ENGELLEME değil)

| Katman | Uygulama | Kişisel veri |
|---|---|---|
| Belge parmak izi | `api/sahiplik.py::coklu_sahiplik_kontrol` — aynı içerik farklı profil altında görülürse HER İKİ kayıt da (yeni + retroaktif eski) `coklu_sahiplik_supheli` ile işaretlenir | Yok |
| Zorunlu beyan | `portal_yukle` artık `beyan` alanı olmadan 400 döner; zaman (`Assessment.created_at`) + IP (`yukleme_ip`) ile kaydedilir | IP |
| Davranışsal tutarlılık | `api/sahiplik.py::davranissal_tutarlilik_kontrol` — yeni yüklemenin gelir ölçeği, aynı profilin geçmiş medyanından 3 kattan fazla saparsa `profil_tutarsiz` | Yok |

Bayraklar **kararı hiçbir zaman değiştirmez** — `anomali_bayrak` ile aynı desen (şeffaflık sinyali, overview.md §7 sınırı korunuyor). Canlı doğrulama (curl, aşağıda): aynı CSV içeriği ikinci bir hesapla yüklendiğinde ikisi de `coklu_sahiplik_supheli` alıyor; beyan olmadan istek 400 dönüyor.

#### 7.4 — Risk iştahı: 3 seviyeli banka önerisi

Yeni `aks_core/model/risk_istahi.py`. Üç profil **keyfi skor kesimiyle değil hedef kötü oranla** tanımlı: `ihtiyatli` (≤%3), `dengeli` (≤%6), `atak` (≤%10). Yöntem: `egitim.py::egit()`'in AYNI train/test bölmesi (seed=42, `test_size=0.25`, stratify=y) yeniden üretilerek gerçek bir held-out küme elde edilir (sızıntı yok); her aday AKS eşiği için onay oranı/kötü oran/beklenen kâr-zarar (`is_etkisi.py` ile AYNI varsayımlar: ort_kredi=25000, getiri_orani=0.12, zarar_orani=0.55) hesaplanır, kötü oran hedefini aşmayan eşikler arasından net kârı maksimize eden seçilir. Bootstrap %95 CI raporlanır. **Yalnızca dekuple veri kaynağıyla çalışır** — döngüsel veri üzerinde "hedef kötü oran" anlamsız olurdu, kod bunu zorluyor (`ValueError`).

Gerçekleşen sonuç (`risk_istahi_raporu.json`, n_test=500): ihtiyatlı eşik 835 (kötü oran %2.8, onay %35.4), dengeli eşik 760 (kötü oran %5.0, onay %60.2), atak eşik 690 (kötü oran %7.5, onay %79.6) — monoton, beklenen yönde.

`GET /api/risk-istahi` (genel rapor) + `kimlik/kurum_views.py::musteri_detay`'a gömülü müşteri-bazlı 3-profil onay/red (`GET /api/kimlik/kurum/musteri/<aks_no>` yanıtının `risk_istahi` alanı) — ağır hesaplama tekrarlanmıyor, yalnızca persiste edilmiş eşiklerle karşılaştırma. Rapor `_METRIK_UYARISI` ile aynı ruhta dürüstlük şerhi taşıyor: sentetik/dekuple, held-out ama sentetik, "nihai politika" değil. Test: `test_risk_istahi.py` (8 test).

#### 7.5 — Gerçek agent katmanı (OQ-38'in kısmi kapanışı)

**Dürüst tespit:** `veri_agent`/`skorlama_agent` gerçek agent değil — deterministik pipeline adımları (OQ-38 hâlâ tam kapanmadı, jüriye sunum diline nasıl yansıtılacağı ayrı bir karar). Bunun üstüne **iki gerçek** bileşen eklendi:

- **`agents/belge_agent.py`** — hedefi var (dosyayı başarılı şekilde skorlanabilir listeye çevirmek), birden fazla strateji dener (format-özel okuyucu, PDF için tablo→metin sırasıyla), kendi çıktısını denetler (kalite bayrakları, min. işlem sayısı), her adımı bir İZ olarak bırakır (`meta["iz"]`, kullanıcı arayüzünde "Belge Agent İzi" paneli olarak görünür). Beş-soru testini (overview.md §6) gerçekten geçiyor.
- **`agents/danisman_llm.py`** — Claude API (`claude-sonnet-5`) tool-calling: model yalnızca 5 tanımlı araçla (`skor_getir`, `faktor_getir`, `politika_getir`, `senaryo_calistir`, `gecmis_getir`) veri okuyabilir, sayı uyduramaz. **İki katmanlı zorlama:** (1) `aks_skor`/`karar`/`onerilen_limit` her zaman `SkorlamaAgent`'ten gelir, LLM çıktısı ayrı bir `anlati` alanı; (2) yanıt-sonrası doğrulama (`_dogrula`) — metindeki sayılar araç çıktılarında (+ AKS'nin sabit 300/850 ölçeği + ≤12 doğal-dil sayıları) yoksa yanıt reddedilir, deterministik kural motoruna düşülür (`anlati_reddedildi=True`). `ANTHROPIC_API_KEY` yoksa (test ortamı dahil her zaman) `services.asistan_yanit()` eski yola (Gemini varsa dener, yoksa kural motoru) sıfır regresyonla düşer.

**TODO, açıkça bırakıldı:** `ANTHROPIC_API_KEY` PO tarafından eklenip canlı tool-calling + guard'ın gerçekten tetiklendiğinin uçtan uca doğrulanması gerekiyor — mock'lanmış unit testler (`test_danisman_llm.py`, 10 test, sahte `anthropic.Anthropic` ile) akışı kanıtlıyor ama gerçek API çağrısı bu turda yapılmadı.

#### 7.6 — Frontend (iki ayrı, genişletilmiş arayüz)

**Kullanıcı portalı** (`/portal/*`, `PortalLayout` genişletildi — üst nav): `PortalPage` artık PDF/XLSX/CSV kabul ediyor, zorunlu sahiplik beyanı checkbox'ı (beyansız gönder butonu disabled), sahiplik/kalite bayrak uyarıları, "Belge Agent İzi" paneli; yeni `PortalProfilPage` (AKS no + kopyala, telefon OTP akışı), `PortalTaleplerPage` (gelen talepleri onayla/reddet/iptal et), `PortalRizaPage` (rıza defteri).

**Kurum arayüzü** (yeni, `/kurum/*`, ayrı `KurumLayout` + login-only giriş — öz-kayıt yok): `KurumMusterilerPage` (AKS no + amaç ile talep aç, aktif erişimleri listele), `KurumMusteriDetayPage` (skor/SHAP/bayraklar + **3 seviyeli risk iştahı kartları**, onaylanır/onaylanmaz + eşik). Mevcut banka demo sayfaları (`Layout`, Intelligence/Portfolio/Audit/Customers) **değiştirilmedi** — model kanıtı olarak jüriye gerekli; nav'a "Kurum Girişi" linki eklendi. `CsvUploadPage` de PDF/XLSX kabul edecek şekilde genişletildi (anonim yol, `sahiplik_bayraklari` her zaman boş).

`src/api.ts`: yeni tipler (`BelgeMeta`, `RiskIstahiRaporu`, `ProfilBilgisi`, `ErisimTalebiKaydi`, `RizaDefteriKaydi`, `KurumBilgisi`, `KurumMusteriDetay`, vb.) + 12 yeni `api.*` fonksiyonu — mevcut `csrfTokenAl()`/`_hataMesaji()`/`credentials:"same-origin"` deseni aynen kullanıldı, yeni bir HTTP katmanı yazılmadı. `tsc --noEmit` temiz.

**Canlı uçtan uca doğrulama (Chrome eklentisi bu oturumda bağlanamadı — curl + cookie jar ile HTTP seviyesinde, frontend'in kullandığı aynı API sözleşmesiyle doğrulandı, tıklama-tabanlı değil):** kayıt → AKS no üretildi → beyansız yükleme 400 → beyanlı yükleme 200 (agent izi + `pencere_uyumsuz` bayrağı gerçekten tetiklendi, 47 günlük test verisiyle) → kurum rızasız erişim denedi → 403 → kurum talep açtı → müşteri talebi gördü ve onayladı → kurum artık görebiliyor + 3 seviyeli risk kartları doğru (skor 850, üç profilde de onay) → rıza defteri tam geçmişi gösterdi → müşteri rızayı iptal etti → kurum tekrar 403 → aynı CSV ikinci bir hesapla yüklendi → **her iki** kayıt da `coklu_sahiplik_supheli` aldı.

#### 7.7 — Test durumu ve regresyon

`aks_core` pytest: 24 → **67 passing** (belge: 20, belge_agent: 5, risk_istahi: 8, danisman_llm: 10). `04-backend` Django: 15 → **41 passing** (kimlik kiracılık: 17, sahiplik savunması: 6, risk iştahı/asistan wiring: 2, önceki 15 dahil). `tsc --noEmit` temiz. **Model regresyon kontrolü:** `python -m aks_core.model.egitim` yeniden çalıştırıldı — LR AUC **0.8499** ve ECE **0.0391→0.0394** birebir aynı üretildi (seed=42) — belge/kimlik/agent katmanlarının hiçbiri modele dokunmadığının kanıtı.

**Bu turda bilinçli olarak yapılmayanlar (sessizce atlanmadı):**
- Açık bankacılık entegrasyonu (gerçek sahiplik ispatı) — üretim yolu olarak belgelendi, kurulmadı.
- Gerçek SMS sağlayıcısı (OQ-47) ve gerçek kurum onboarding süreci (OQ-53) — demo/manuel seviyede bırakıldı.
- `ozellik_cikar()`'ın pencere-bağımsız hale getirilmesi (OQ-52) — modelin yeniden eğitilmesini gerektirir, bu turun kapsamı dışında tutuldu.
- Canlı `ANTHROPIC_API_KEY` testi — anahtar PO'da, TODO olarak kaldı.

**Phase 7 exit gate: ✅ PASSED** — 7 alt fazın hepsi (belge hattı, kimlik/rıza/kiracılık, sahiplik savunması, risk iştahı, agent katmanı, frontend, doküman) tamamlandı ve test edildi; sıfır regresyon.

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
| R8 | Out-of-persona holdout + out-of-time split | P2 | 🟡 PARTIAL — DONE (out-of-persona), N/A (out-of-time) | M4 | Research | Genuine generalization estimate — see §3b Phase 5 for results and why out-of-time isn't meaningful on this synthetic dataset |
| R9 | Per-segment calibration (Brier/ECE) + isotonic/Platt if needed | P3 | ✅ DONE | M4 | Research | Isotonic correction implemented (`kalibrasyon.py`, threshold-gated); honest null result this run (ECE 0.0391→0.0394, not improved) — see §3b Phase 1 results |
| R10 | Thin-file small-sample / sparse-history stress test | P4 | ✅ DONE | M4 | Research | Model degrades gracefully, not confidently, where data is sparse — see §3b Phase 5 |
| R11 | Gaming-resistance review of the 4 causal features (RQ-3) | P4 | ✅ DONE | — | Research | Which features are user-manipulable; robustness verdict — see §3b Phase 5 |
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
| OQ-33 | Supabase Auth vs plain Django auth — for the bank panel, still deferred (bank panel has no login); for the new **user portal** (§3b Phase 6), 🟢 RESOLVED by PO — Django's own session auth, no Supabase credentials needed | Frontend login flow | 🟢 Resolved for portal; bank panel still deferred |
| OQ-40 | Does "don't touch `01-data/`" commit this cycle to the synthetic/decoupled path (R6) over real-data acquisition (R7), or is it just this sprint's scope? | U1, R3 | 🟡 Proceeding synthetic-only this cycle per current PO instruction; OQ-36 itself stays open |
| OQ-41 | Decision-mechanism config (U11): a simple versioned constants module, or a DB-backed/admin-editable policy table? | U11 sizing | 🔴 Awaiting PO |
| OQ-42 | Execute the XGBoost→LR swap (U8/E1) this cycle if LR wins on the new benchmark, or keep XGBoost live and only report the recommendation? | U8 | 🟢 RESOLVED — swap executed. Not a guess: the project's own binding mandate ("classical wins by default" when equal-or-better) already committed to this outcome in architecture.md §5.2 before this cycle; the new benchmark's non-overlapping CIs [0.853,0.871] vs [0.831,0.850] made it unambiguous rather than a judgment call |
| OQ-43 | Are the stretch frontend items (U23 what-if simulator, U24 CSV upload) in scope this cycle or deferred? | Phase 3 sizing | 🟢 RESOLVED — PO chose to build both; U24 shipped and verified live in-browser, U23 shipped and verified live in-browser (score correctly moves 850→300 in the tested scenario) |
| OQ-44 | Should the *live* demo dataset (`sentetik_islemler.csv`, powers `/api/demo-musteriler`, `/api/skorla/{id}`, `/api/portfoy`, `/api/adalet`) be switched to the decoupled `kapasite_islemler.csv` so the whole live product reflects M4, not just offline training/eval scripts? Changes which demo customers/personas appear throughout the UI. | `services.py::VERI_YOLU`, `_skorla_hepsi()` | 🔴 Awaiting PO — `/api/portfoy`/`/api/adalet` carry an explicit `"veri_kaynagi":"dongusel"` caveat in the meantime (§3b Phase 2) |
| OQ-45 | R11 (§3b Phase 5) found `gider_gelir_orani` alone buys +73 (avg) to +265 (p90) AKS points for a fixed 25% "improvement" — far more than the other 3 causal features combined. Cap its influence (monotonic constraint) now, or corroborate with a longer window/independent signal first, or accept the risk and just disclose it? | `cikarim.py`, model retraining, architecture.md §8 (planned monotonic constraints) | 🔴 Awaiting PO |
| OQ-46 | User portal (§3b Phase 6) now accepts real end-user-uploaded statements tied to a real account — this makes DA5 (KVKK/consent/lawful-basis governance, already TODO before this phase) more urgent. What's the minimum before accepting *real* (non-demo) user data: explicit consent checkbox + privacy notice text only, or a full data-retention/deletion policy + DPA-style documentation? | `PortalPage.tsx`, `PortalLoginPage.tsx`, DA5 | 🔴 Awaiting PO — current portal is demo-grade, not yet market-ready on this axis. §3b Phase 7 added the ownership-declaration checkbox (7.3) but not a full retention/deletion policy — this OQ stays open |
| OQ-47 | §3b Phase 7/7.2: no real SMS provider is wired — OTP codes are demo-mode only (`DEBUG=True` returns the code in the API response). Which provider (Twilio, Netgsm, İleti Merkezi, …) and who sets up the account/credentials? | `kimlik/telefon.py`, `kimlik/views.py::telefon_gonder` | 🔴 Awaiting PO |
| OQ-48 | §3b Phase 7/7.5: `ANTHROPIC_API_KEY` is not yet set — `danisman_llm.py`'s tool-calling path is unit-tested (mocked) but never exercised against the real Claude API. Who adds the key and when should the live end-to-end verification happen? | `.env`, `danisman_llm.py` | 🔴 Awaiting PO (TODO, not blocking — deterministic fallback works today) |
| OQ-49 | §3b Phase 7/7.6: the bank-side `Layout.tsx` demo/research pages (Intelligence, Portfolio, Audit, Customers) were kept untouched alongside the new consent-gated `kurum/*` pages. Once the product is genuinely market-facing, should the demo pages be removed/gated behind a flag, or do they stay permanently as the research/evidence surface (jury-facing, not customer-facing)? | `Layout.tsx`, `App.tsx` route tree | 🔴 Awaiting PO |
| OQ-50 | §3b Phase 7/7.4: `risk_istahi.py`'s three profiles (ihtiyatli/dengeli/atak) use illustrative bad-rate targets (≤3%/6%/10%) and the same `is_etkisi.py` profit assumptions (ort_kredi=25000, getiri_orani=0.12, zarar_orani=0.55) chosen without bank input. Should these targets/assumptions be configurable per bank (a real product would let each institution set its own), or are they meant to stay fixed, illustrative defaults? | `risk_istahi.py::PROFILLER` | 🔴 Awaiting PO |
| OQ-51 | §3b Phase 7 "honesty note": minimum-PII ownership defense (fingerprint + declaration + behavioral consistency) can only *detect*, never *prove*, document ownership. The real fix is open banking (data arrives from the bank with authorization, not as a user-uploaded file). Is open banking integration a near-term roadmap item, or an accepted long-term limitation for this product? | `aks_core/belge/`, `kimlik/`, architecture.md | 🔴 Awaiting PO |
| OQ-52 | §3b Phase 7/7.1: the model was trained on a 180-day transaction window; uploaded PDFs/statements are often shorter (a `pencere_uyumsuz` flag now surfaces this, verified live at 47 days). Fixing this properly requires retraining on variable/normalized windows. Prioritize this retraining now, or keep flagging the mismatch and defer? | `ozellik/cikarim.py`, `egitim.py`, `belge/kalite.py` | 🔴 Awaiting PO |
| OQ-53 | §3b Phase 7/7.2: institution ("kurum") onboarding is currently manual (`bootstrap_kurum` management command, no self-serve registration) — a deliberate choice since a self-registering "institution" would weaken the consent system's "the institution's identity is verified" assumption. What should real institution onboarding look like: a contract + manual verification process, or an automated one with its own trust mechanism? | `kimlik/management/commands/bootstrap_kurum.py`, `kimlik/models.py::Kurum` | 🔴 Awaiting PO |

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
