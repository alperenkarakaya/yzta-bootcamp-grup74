# AKS — Execution Plan

Companion to **[overview.md](overview.md)** and **[architecture.md](architecture.md)**. This is the **single live plan** — it replaces all prior roadmaps, workstream files, and traceability matrices. Truth about *what to do next* lives here.

Detailed data-engineering specs live in **[`planning/`](planning/data-architecture.md)** (data-architecture, feature-schema, pipeline-steps) — a subordinate working area for column-level detail too fine-grained for the root docs; these three root docs remain the source of truth.

**Priority scale** (from overview.md §5, binding): P1 accuracy · P2 generalization · P3 calibration · P4 robustness · P5 interpretability · P6 business value · P7 regulatory · P8 engineering · P9 AI · P10 UI. Lower number = higher priority. **UI/stack work must never block P1–P4.**

**Status values:** `DONE` · `IN-PROGRESS` · `BLOCKED` · `TODO` · `PROPOSED`.
Owner shorthand: **PO** = Product Owner (Alperen Karakaya) · **Research** = modeling/eval · **Eng** = build.

---

## 1. Current sprint (research-rigor track)

The active objective is **restore benchmark validity**, because every headline number is currently circular (architecture.md §5.1). Nothing downstream — business claims, fairness claims, jury deck — is trustworthy until this is resolved. UI and infra are deliberately paused behind it.

**This sprint's definition of done:** OQ-36 answered → target metric (Formulation B) instrumented → a non-circular benchmark producing an *honest* incremental-approval-at-fixed-bad-rate number with CIs.

## 2. Milestones

| # | Milestone | Gate | Status |
|---|---|---|---|
| M1 | Pipeline works end-to-end (data → model → API → audit) | Live scoring + immutable audit | ✅ DONE |
| M2 | Statistical rigor instrumented (CV, CI, calibration, per-segment) | `degerlendirme.py` + `circularity_ablation.py` reproducible | ✅ DONE |
| M3 | Circularity diagnosed & target defined | Finding documented; Formulation B chosen | ✅ DONE (B awaiting ratification, OQ-39) |
| M4 | **Non-circular benchmark** | Real data OR redesigned simulator; honest headline number | 🟡 IN-PROGRESS — synthetic honest-fallback **built + proven** (`product/01-data/generator/uretici_kapasite.py`): label decoupled from persona (spread 0.015) and from features (no single feature = label; income channel 0.50, behavioral 0.84 genuine +0.34 lift). Still pending: OQ-36 (prefer real data if available) and porting the decoupled label into the training/eval path (DA2). |
| M5 | Model finalized on valid benchmark | LR-vs-XGBoost decided on non-circular data; calibrated | ⏳ TODO (after M4) |
| M6 | Demo-ready product | Stitch UI integrated, deploy live, agent narrative honest | ⏳ TODO (after M4; UI last) |

## 3. Priorities (what to do, in order)

1. **Resolve OQ-36** (real data vs redesigned simulator) — the single highest-leverage decision.
2. **Instrument the Formulation B metric** (incremental approvals at fixed bad-rate + per-segment calibration).
3. **Produce an honest headline number** on a non-circular benchmark; re-caveat or rewrite published figures (OQ-37).
4. **Then** model finalization, robustness, interpretability, business-value rebuild.
5. **Only then** engineering polish, agent-narrative correction, and UI.

## 4. Research & experiment tasks

| ID | Task | Prio | Status | Depends on | Owner | Expected outcome |
|---|---|---|---|---|---|---|
| R1 | Ablation proof of circularity | P1 | ✅ DONE | — | Research | `circularity_ablation.py`: XGB≈LR (Δ0.0004), confounding structural |
| R2 | Evaluation harness (CV+CI+calibration+per-segment) | P1–P3 | ✅ DONE | — | Research | `degerlendirme.py` reusable regardless of OQ-36 |
| R3 | Decide real-data vs simulator redesign (OQ-36) | P1 | 🔴 BLOCKED | PO input | PO | Chooses gold-standard (real) vs honest-fallback (synthetic) fix path |
| R4 | Ratify target definition = Formulation B (OQ-39) | P1 | 🟡 PROPOSED | — | PO | Locks calibration (not AUC) as headline metric |
| R5 | Instrument incremental-approval-at-fixed-bad-rate metric | P1/P6 | ⏳ TODO | R3, R4 | Research | The number a bank/investor actually cares about, with CIs |
| R6 | Simulator redesign — decouple feature-gen from label-gen | P1 | ⏳ TODO | R3 (if synthetic) | Research | Non-circular synthetic population; persona no longer determines both |
| R7 | Acquire/prep Home Credit dataset; mask rich features to simulate thin-file | P1 | ⏳ TODO | R3 (if real) | Research | Real-outcome proving ground for Formulation B |
| R8 | Out-of-persona holdout + out-of-time split | P2 | ⏳ TODO | M4 | Research | Genuine generalization estimate |
| R9 | Per-segment calibration (Brier/ECE) + isotonic/Platt if needed | P3 | ⏳ TODO | M4 | Research | Calibration guarantee, the acceptance criterion |
| R10 | Thin-file small-sample / sparse-history stress test | P4 | ⏳ TODO | M4 | Research | Model degrades gracefully, not confidently, where data is sparse |
| R11 | Gaming-resistance review of the 4 causal features (RQ-3) | P4 | ⏳ TODO | — | Research | Which features are user-manipulable; robustness verdict |
| R12 | Pre-register acceptance thresholds X (approvals), Y (ECE) | P1 | ⏳ TODO | R4 | Research+PO | Anti-goal-seeking: numbers fixed before results |

## 5. Model & engineering tasks

| ID | Task | Prio | Status | Depends on | Owner | Expected outcome |
|---|---|---|---|---|---|---|
| E1 | Swap XGBoost → logistic regression as reported model | P1/P8 | ⏳ TODO (gated) | M4 | Research | Simpler, better-calibrated model — but only on a valid benchmark |
| E2 | Monotonic constraints aligned with domain priors | P5 | ⏳ TODO | M5 | Research | Defensible sign of each feature's effect |
| E3 | SHAP → adverse-action-style reason codes | P5/P7 | ⏳ TODO | M5 | Research+Eng | Regulator-facing explanation surface |
| E4 | Rebuild revenue/loss on RAROC-consistent basis | P6 | ⏳ TODO | M4 | Research | Expected loss + capital/funding cost, not flat loss-rate heuristic |
| E5 | Hyperparameter search + lightweight experiment tracking | P8 | ⏳ TODO | M5 | Eng | No hardcoded params; logged JSON manifest per run |
| E6 | Per-resample seeding discipline (fix global `random.seed(7)`) | P8 | ⏳ TODO | — | Eng | Bootstrap/resampling stops understating uncertainty |
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
| DA2 | 02-ai-agents: feature extraction for new cash-flow columns + **Formulation B** target + per-segment calibration | P1/P3 | ⏳ TODO | DA1, M4 | Research | `pd_davranissal`/`pd_geleneksel_bant`/`pd_fark`/`kapasite_sinyali` + calibration |
| DA3 | 04-backend: `FeatureStore`/`Consent`/`DataProvenance` tables + extend `Assessment`/`AuditLog` + migrations + API fields | P8 | ⏳ TODO | DA2 | Eng | O(1) scoring lookup; provenance/consent + human-oversight fields persisted |
| DA4 | 03-frontend: surface PD-gap / capacity / calibration + provenance/consent state | P10 | ⏳ TODO | DA3 | Eng | Real Formulation-B fields shown; no fabricated data |
| DA5 | 05-business: hypothesis registry + KVKK/lawful-basis mapping + DPIA/human-oversight posture + out-of-scope register | P7 | ⏳ TODO | — (parallel; gates T1/T2/T3 columns) | PO+Eng | No column without a hypothesis + lawful basis; rejected capabilities documented |

## 6. Technical debt

| ID | Item | Prio | Status | Notes |
|---|---|---|---|---|
| D1 | Port 22 Sprint-2 tests off FastAPI/`src.*` to Django `APIClient` + `aks_core` | P8 | 🔴 TODO | They don't run post-migration; add **boundary tests** proving no agent can mutate the classic score |
| D2 | Global `random.seed(7)` reused per label-generation call | P8 | 🔴 TODO | Same as E6 — silently understates resampling uncertainty |
| D3 | Hardcoded hyperparameters (`n_estimators=300, max_depth=4`) | P8 | 🔴 TODO | Same as E5 |
| D4 | `_legacy_fastapi/` kept as reference | — | ACCEPTED | Delete once Django parity is fully trusted and tests are ported |
| D5 | Published numbers (AUC 0.829, 973/1084, fairness gap) still cited in artifacts | P1 | 🟡 IN-PROGRESS | Must be caveated everywhere or rewritten once M4 lands (OQ-37) |

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
| **OQ-36** | Real benchmark dataset access (Home Credit / LendingClub / open-banking)? | R3/R7 — the fix path itself | 🔴 Highest-leverage; awaiting PO |
| **OQ-37** | Fix circular numbers now (rewrite published figures) or after demo day (keep + caveat)? | D5, any numbers-facing edit | 🔴 Awaiting PO |
| **OQ-38** | Correct agent narrative to "one real agent" now, or invest in a 2nd genuine agent first? | Jury-facing material | 🔴 Awaiting PO |
| **OQ-39** | Ratify Formulation B as the operational target? | R5, all modeling | 🟡 PROPOSED — proceeding unless founder objects |
| OQ-34 | Google Stitch export format (HTML+Tailwind vs React/JSX)? | E11 | 🟢 RESOLVED — plain HTML+Tailwind (5 pages under `product/03-frontend/stitch-output/`), confirmed by direct inspection and ported into React components |
| OQ-35 | Supabase + Upstash credentials — who creates accounts? | E9, E10 | 🟡 Awaiting PO |
| OQ-33 | Supabase Auth vs plain Django auth for the bank panel? | Frontend login flow | 🟢 Deferred (backend works without auth) |

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
