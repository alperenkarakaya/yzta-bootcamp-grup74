# ROADMAP — Master Delivery Plan
## Intelligent Offer Optimization Bridge Layer (Bootcamp Build)

This is the **single master roadmap** the whole team works from. It consolidates — it does **not** invent — the 83 tasks defined in `07-bootcamp-workstreams/workstreams.md` + `ws1.md`–`ws5.md`, sized with story points and sequenced across sprints S0–S4. Definitions live in the ws files; **operational status lives here** (see §6 Update Rules).

**Sources consolidated:** `07-bootcamp-workstreams/ws1.md`–`ws5.md` (all tasks), `07-bootcamp-workstreams/workstreams.md` (sprint sequencing S0–S4, dependency graph, gates), `TRACEABILITY.md` §8, `00-program/open-questions.md`.

---

## 1. Header

### Mission
Build a working, demonstrable **bridge layer** that sits between a *simulated* bank credit-decision engine and the final customer offer, and **optimizes the offer within the bank's approved risk policy** — using a multi-agent AI architecture (analysis, policy-guard, offer-optimization, explanation, fairness-audit agents) over a synthetic-but-honest credit portfolio. The project's defining feature is also its strongest safety story: the layer is *architecturally incapable* of overriding the bank's model, and every offer adjustment is auditable.

### Hard boundary (standing constraint — verbatim, binds every task in this roadmap)
> **The bridge layer optimizes offers *within* the bank model's approved policy. It never re-scores customers, never overrides or changes the engine's segment, never adjusts the engine's inputs, never auto-approves above-policy limits.** (source `early-phase-plan-credit-offer-optimization.md` §4, §6)

Enforced by: **BWS3** deterministic policy-guard agent · **BWS5** append-only audit trail + boundary tests · **BWS4** segment rendered read-only · **BWS1** narrative. Any task that appears to weaken this boundary is a defect.

### Legend

**Story points (Fibonacci):** `1` trivial · `2` small · `3` small-plus · `5` medium · `8` large. Anything that would be `13` was **split** into two ≤8 tasks (see §7 Sizing Notes). Base mapping: **S→2, M→5, L→8** (per-task adjustments justified in §7).

**Status values:** `TODO` (not started) · `IN-PROGRESS` · `BLOCKED` (note blocker) · `REVIEW` (in team/persona review) · `DONE`. All tasks start `TODO`.

**Markers:** 🔴 = on the critical path · `[INFERRED]` = sprint placement decided here because the ws sequencing did not pin it (listed in §7.4).

**ID scheme:** `BWS<n>-T<k>` = task `T<k>` in `ws<n>.md`. Splits use letter suffixes (`BWS3-T13a`, `BWS3-T13b`). IDs match the ws files exactly.

**Sprints stay relative** (S0–S4) because bootcamp duration is unresolved (**OQ-27**). Calendar mapping placeholder: see §4.3.

---

## §1. Business & Domain (BWS1)

| ID | Task | SP | Sprint | Depends on | Traces to | Owner | Status |
|---|---|---|---|---|---|---|---|
| BWS1-T1 | Problem one-pager: P1/P2/P3 + "diagnose the mix" thesis | 5 | S0 | — | §1.1, K1/K2, D1 | TBD | TODO |
| BWS1-T2 | Root-cause & impacted-party summary | 2 | S0 | BWS1-T1 | §1.2, §1.3 | TBD | TODO |
| BWS1-T3 | 🔴 Define policy ranges per segment (machine-readable config) | 5 | S0 | BWS1-T1 | §4, A5, boundary | TBD | TODO |
| BWS1-T4 | 🔴 Co-author ground-truth definition ("deserved segment") | 5 | S0 | BWS1-T1 | A2, E2, K11 | TBD | TODO |
| BWS1-T5 | Success-metrics & baseline book (O5 metric + risk-adjusted sizing formula) | 5 | S0 | BWS1-T1, BWS1-T4 | §8, O5, D9, K9 | TBD | TODO |
| BWS1-T6 | Illustrative opportunity sizing (O1–O8; O5 headline) on synthetic data | 5 | S2 | BWS1-T5, BWS2-T2, BWS2-T13 | §4, D5, A4/A10 | TBD | TODO |
| BWS1-T7 | Persona catalogue + assumption register | 5 | S0 `[INFERRED]` | — | §3, D3, A2(review) | TBD | TODO |
| BWS1-T8 | Regulatory-awareness write-up (fair lending, explainability, data protection, responsible lending, EU AI Act high-risk) | 8 | S1 | BWS1-T1 | §6.3, D7, A6, H13 | TBD | TODO |
| BWS1-T9 | Map each regulatory obligation → architectural control | 5 | S1 | BWS1-T8 | §6, D7, D10 | TBD | TODO |
| BWS1-T10 | Refresh risk register for build reality (sim vs real-world flags) | 2 | S1 | BWS1-T1 | §6, D6 | TBD | TODO |
| BWS1-T11 | Fairness position note (consume BWS3 fairness output) | 5 | S3 `[INFERRED]` | BWS3-T11, BWS2-T16 | H14, E9, D7, R4 | TBD | TODO |
| BWS1-T12 | Shared Risk–Business metric one-pager (spec for shared screen) | 2 | S2 `[INFERRED]` | BWS1-T5, BWS1-T6 | §3 tension, E7, D9, K10 | TBD | TODO |
| BWS1-T13 | Business case + jury narrative arc | 8 | S3 | BWS1-T1/T5/T6 | review R1–R6, D1 | TBD | TODO |
| BWS1-T14 | Honest-limits register ("what evidence does / doesn't support") | 5 | S3 | BWS1-T6, BWS1-T11 | R1/R2/R3/R4/R6 | TBD | TODO |
| BWS1-T15 | Track OQ-27…31 impact on business framing | 1 | S0 `[INFERRED]` | — | OQ-27…31 | TBD | TODO |

**BWS1 total: 68 SP** (S0 28 · S1 15 · S2 7 · S3 18 · S4 0)

---

## §2. Data & Simulation (BWS2)

| ID | Task | SP | Sprint | Depends on | Traces to | Owner | Status |
|---|---|---|---|---|---|---|---|
| BWS2-T1 | 🔴 Design synthetic schema (M1–M9 → fields) | 8 | S0 | BWS1-T4 | §7.1 M1–M9, D8, A1 | TBD | TODO |
| BWS2-T2 | 🔴 Data-generating process with seeded P1/P2/P3 mix (portfolio v1) | 8 | S1 | BWS2-T1, BWS1-T4 | §1.1, A1, K2 | TBD | TODO |
| BWS2-T3 | Implement ground-truth labels ("true" risk + deserved segment) | 5 | S1 `[INFERRED]` | BWS2-T2, BWS1-T4 | A2, E2, K11 | TBD | TODO |
| BWS2-T4 | Generate boundary cohorts | 5 | S1 | BWS2-T2 | H1, O2 | TBD | TODO |
| BWS2-T5 | Generate stale-score / migration time series | 5 | S1 | BWS2-T2 | H2, H8, U6 | TBD | TODO |
| BWS2-T6 | Generate thin-file / new-to-bank cohort | 5 | S1 | BWS2-T2 | H3 | TBD | TODO |
| BWS2-T7 | Generate override logs (asymmetric, with outcomes) | 5 | S1 | BWS2-T2 | H4, M6 | TBD | TODO |
| BWS2-T8 | Generate within-segment behavioral signals | 5 | S2 | BWS2-T2 | H5, U1/U2, O1 | TBD | TODO |
| BWS2-T9 | Generate past limit-increase campaign results | 5 | S2 | BWS2-T2 | H7, U3, O6 | TBD | TODO |
| BWS2-T10 | Generate attrition/closure data w/ destination | 2 | S2 | BWS2-T2 | H11, U4 | TBD | TODO |
| BWS2-T11 | Generate complaint verbatims + NPS (LLM-authored) | 5 | S2 | BWS2-T2 | H9/H10, M8/U5 | TBD | TODO |
| BWS2-T12 | Generate protected/proxy attrs + seed correctable disparity | 5 | S2 | BWS2-T2, BWS1-T4 | H14, OPT5, E9, R4 | TBD | TODO |
| BWS2-T13 | Generate per-segment financials (revenue, EL, capital proxy) | 5 | S1 | BWS2-T2 | H6, M9/U8, O5 | TBD | TODO |
| BWS2-T14 | Write the data dictionary | 5 | S1 | BWS2-T2 | §7 rule, D8 | TBD | TODO |
| BWS2-T15 | Data-quality checks | 2 | S3 | BWS2-T2…T14 | §6.5, E5 | TBD | TODO |
| BWS2-T16 | Bias / representativeness report | 5 | S3 | BWS2-T12 | §6.3, §8.2, H14 | TBD | TODO |
| BWS2-T17 | Reproducible seeded generator + curated demo subset ("wow cases") | 5 | S4 | BWS2-T2 | demo, R5 | TBD | TODO |
| BWS2-T18 | Ground-truth honesty appendix | 2 | S3 | BWS2-T3 | R1/R4, K11 | TBD | TODO |

**BWS2 total: 87 SP** (S0 8 · S1 43 · S2 22 · S3 9 · S4 5)

---

## §3. AI Core & Agentic Architecture (BWS3) ★ *(highest evaluation weight)*

| ID | Task | SP | Sprint | Depends on | Traces to | Owner | Status |
|---|---|---|---|---|---|---|---|
| BWS3-T1 | Agent inventory + boundary spec (guard-before-commit invariant) | 5 | S0 | BWS1-T3 | §4, K5, L3, D10 | TBD | TODO |
| BWS3-T2 | LLM provider / orchestration spike + structured-output contract | 5 | S0 | BWS3-T1 | L6, OQ-29 | TBD | TODO |
| BWS3-T3 | 🔴 Policy-guard agent (deterministic; block + reason-code; never mutate segment) | 8 | S1 | BWS3-T1, BWS1-T3, BWS5-T3 | §4, K5, R6 | TBD | TODO |
| BWS3-T4 | 🔴 Analysis agent (segment + signals → evidence) | 8 | S1 | BWS5-T3, BWS2-T2 | H1/H2/H3/H5/H8, O1/O2 | TBD | TODO |
| BWS3-T5 | Classical ML: within-segment signal separation (no re-score) | 5 | S2 | BWS3-T4, BWS2-T8 | H5, O1, L4 | TBD | TODO |
| BWS3-T6 | Classical ML: stale-score/migration + attrition signals | 5 | S2 | BWS3-T4, BWS2-T5, BWS2-T10 | H2/H8/H11 | TBD | TODO |
| BWS3-T7 | 🔴 Offer-optimization agent (within-policy; calls guard) | 8 | S2 | BWS3-T4, BWS3-T3, BWS1-T3 | O1, A1, §4 | TBD | TODO |
| BWS3-T8 | Graduated / staged offer logic | 5 | S3 | BWS3-T7, BWS2-T9 | O6, H7 | TBD | TODO |
| BWS3-T9 | RAG over policy corpus (grounds explanations + guard rationale) | 8 | S2 | BWS1-T8 | L6, D7, O4 | TBD | TODO |
| BWS3-T10 | 🔴 Explanation agent (staff evidence pack O2 + customer explanation O4) | 8 | S2 | BWS3-T4, BWS3-T9, BWS2-T11 | O2/O4, H9/H10 | TBD | TODO |
| BWS3-T11 | Fairness-audit agent (detect + correct seeded disparity) | 8 | S2 | BWS2-T12, BWS3-T7 | H14, E9 | TBD | TODO |
| BWS3-T12 | Orchestrator (routing, guard-before-commit, audit writes) | 5 | S2 | BWS3-T3/T4/T7/T10/T11, BWS5-T5 | K5, D10 | TBD | TODO |
| BWS3-T13a | Eval harness: optimization correctness vs GT + **guard coverage (100%)** | 5 | S2 | BWS3-T7, BWS2-T3 | L4, A2, §8.1 | TBD | TODO |
| BWS3-T13b | Eval harness: latency/determinism eval + CI integration | 5 | S2 | BWS3-T13a, BWS5-T11 | R6, L4 | TBD | TODO |
| BWS3-T14 | LLM-as-judge explanation-quality eval | 5 | S3 | BWS3-T10 | H10, L6 | TBD | TODO |
| BWS3-T15 | Guardrail hardening (prompt-injection, refuse "override segment") | 5 | S3 | BWS3-T3, BWS3-T12 | §6, R6 | TBD | TODO |
| BWS3-T16 | Failure-mode fallbacks (LLM down → base offer unchanged, logged) | 2 | S4 | BWS3-T12 | R6, boundary | TBD | TODO |
| BWS3-T17 | Determinism/latency tuning for live demo | 2 | S4 | BWS3-T12, BWS3-T13b | R6, demo | TBD | TODO |

**BWS3 total: 102 SP** (S0 10 · S1 16 · S2 57 · S3 15 · S4 4) — *18 rows (17 original + 1 split; see §7.3)*

---

## §4. Product, UX & Explainability (BWS4)

| ID | Task | SP | Sprint | Depends on | Traces to | Owner | Status |
|---|---|---|---|---|---|---|---|
| BWS4-T1 | UX flows + wireframes (offer, evidence pack, explanation, graduated) | 5 | S0 | BWS1-T7 | O1/O2/O4/O6, personas | TBD | TODO |
| BWS4-T2 | Demo story arc (with BWS1) | 5 | S0 | BWS1-T1 | R1/R5, D1 | TBD | TODO |
| BWS4-T3 | App skeleton + routing + design system | 5 | S1 | BWS4-T1 | L5 | TBD | TODO |
| BWS4-T4 | Offer screen (segment **read-only** + within-policy offer + policy band) | 8 | S1 | BWS4-T3, BWS5-T4 | O1, §4, K5 | TBD | TODO |
| BWS4-T5 | Staff evidence pack (O2) + route-to-review action | 8 | S2 | BWS4-T4, BWS3-T4 | O2, H1/H4 | TBD | TODO |
| BWS4-T6 | Customer explanation + improvement path (O4) | 8 | S2 | BWS4-T4, BWS3-T10 | O4, H9/H10, A3 | TBD | TODO |
| BWS4-T7 | Graduated / staged offer UI (O6) | 5 | S3 | BWS4-T4, BWS3-T8 | O6, H7 | TBD | TODO |
| BWS4-T8 | Fairness view (disparity + corrected result) | 5 | S3 `[INFERRED]` | BWS3-T11 | H14, E9 | TBD | TODO |
| BWS4-T9 | Audit view (adjustment lineage; segment unchanged) | 5 | S3 `[INFERRED]` | BWS5-T5 | D10, K5 | TBD | TODO |
| BWS4-T10 | Shared risk-adjusted metric screen (Risk + Business persona) | 5 | S3 `[INFERRED]` | BWS1-T12, BWS5-T7 | §3 tension, E7, O5 | TBD | TODO |
| BWS4-T11 | 🔴 Wire screens to BWS5 API + BWS3 structured outputs | 8 | S2 | BWS5-T4, BWS3-T7, BWS3-T10 | integration | TBD | TODO |
| BWS4-T12 | Empty/error/latency states + LLM-timeout fallback UX | 2 | S3 | BWS4-T11 | R6 | TBD | TODO |
| BWS4-T13 | Accessibility + explainability polish (jargon-free, attribute-safe) | 5 | S3 | BWS4-T5, BWS4-T6 | H10, §6.3, R4 | TBD | TODO |
| BWS4-T14 | Curate demo dataset walkthrough (with BWS2) | 2 | S4 | BWS2-T17 | R4/R5 | TBD | TODO |
| BWS4-T15 | 🔴 End-to-end demo script + presenter notes (incl. honest-limits slide) | 8 | S3 | BWS4-T4/T5/T6/T7 | R1–R6 | TBD | TODO |
| BWS4-T16 | 🔴 Record backup demo video; rehearse | 5 | S4 | BWS4-T15, BWS5-T13 | program DoD | TBD | TODO |

**BWS4 total: 89 SP** (S0 10 · S1 13 · S2 24 · S3 35 · S4 7)

---

## §5. Engineering, Integration & Quality (BWS5)

| ID | Task | SP | Sprint | Depends on | Traces to | Owner | Status |
|---|---|---|---|---|---|---|---|
| BWS5-T1 | Repo skeleton `./product/` (modules, env, secrets handling) | 5 | S0 | — | L1, OQ-29 | TBD | TODO |
| BWS5-T2 | 🔴 Sim bank engine (score → segment → base offer) | 5 | S1 | BWS5-T1, BWS5-T3, BWS2-T2 | A5, D2 | TBD | TODO |
| BWS5-T3 | 🔴 Interception seam + API contract (one-directional; no segment write-back) | 8 | S0 | BWS5-T1, BWS3-T1, BWS1-T3 | E6, §4, K5, A8 | TBD | TODO |
| BWS5-T4 | bridge→UI API (offer + explanation + fairness + audit ref), typed | 5 | S1 | BWS5-T3 | BWS3 structured outputs | TBD | TODO |
| BWS5-T5 | Audit trail / lineage store (append-only, full lineage) | 8 | S1 | BWS5-T1, BWS5-T3 | D10, K5, §6 | TBD | TODO |
| BWS5-T6 | Load BWS1 policy-range config into guard (config-as-code + validation) | 5 | S1 | BWS1-T3, BWS3-T3 | §4 policy ranges | TBD | TODO |
| BWS5-T7 | Metric instrumentation hooks (O5 + risk-adjusted counters) | 5 | S2 | BWS1-T5, BWS5-T2 | O5, §8, D9 | TBD | TODO |
| BWS5-T8 | Boundary tests (no segment mutation; no out-of-policy commit; guard-block logged) | 8 | S1 | BWS3-T3, BWS5-T5 | K5, §4, R6 | TBD | TODO |
| BWS5-T9 | Unit + integration tests with BWS2 fixtures | 5 | S1 | BWS5-T2, BWS2-T3 | K8, E5 | TBD | TODO |
| BWS5-T10 | 🔴 End-to-end test (portfolio → engine → bridge → offer → audit) | 5 | S2 | BWS5-T4, BWS3-T7, BWS4-T11 | program DoD | TBD | TODO |
| BWS5-T11 | CI pipeline (tests + BWS3 eval harness; block on red / boundary fail) | 5 | S1 | BWS5-T9 | K7, L4 | TBD | TODO |
| BWS5-T12 | Agent monitoring (traces, latency, guard-block events, errors) | 5 | S2 | BWS5-T5, BWS3-T12 | R6, D10 | TBD | TODO |
| BWS5-T13 | 🔴 Deploy for demo day (hosted, reproducible) + smoke test | 8 | S3 | BWS5-T10 | E10, demo | TBD | TODO |
| BWS5-T14 | Rollback / backup plan + offline fallback dataset wiring | 2 | S4 | BWS5-T13, BWS2-T17 | demo risk, R5 | TBD | TODO |
| BWS5-T15 | Audit export (CSV/JSON) for governance/regulatory narrative | 2 | S3 | BWS5-T5 | D10, D7 | TBD | TODO |
| BWS5-T16 | Performance/robustness pass (latency budget, LLM-timeout handling) | 5 | S3 | BWS5-T13 | R6, demo | TBD | TODO |
| BWS5-T17 | Weekly traceability-check tooling (ID scan over ws1–ws5 + §8) | 2 | S0 `[INFERRED]` | — | K8, ritual | TBD | TODO |

**BWS5 total: 88 SP** (S0 15 · S1 41 · S2 15 · S3 15 · S4 2)

---

## 4. Sprint View

### 4.1 Task IDs per workstream per sprint

| Sprint | BWS1 | BWS2 | BWS3 ★ | BWS4 | BWS5 |
|---|---|---|---|---|---|
| **S0** | T1,T2,T3,T4,T5,T7,T15 | T1 | T1,T2 | T1,T2 | T1,T3,T17 |
| **S1** | T8,T9,T10 | T2,T3,T4,T5,T6,T7,T13,T14 | T3,T4 | T3,T4 | T2,T4,T5,T6,T8,T9,T11 |
| **S2** | T6,T12 | T8,T9,T10,T11,T12 | T5,T6,T7,T9,T10,T11,T12,T13a,T13b | T5,T6,T11 | T7,T10,T12 |
| **S3** | T11,T13,T14 | T15,T16,T18 | T8,T14,T15 | T7,T8,T9,T10,T12,T13,T15 | T13,T15,T16 |
| **S4** | — | T17 | T16,T17 | T14,T16 | T14 |

### 4.2 Story points per workstream per sprint + grand totals

| Sprint | BWS1 | BWS2 | BWS3 ★ | BWS4 | BWS5 | **Sprint total** | Flag |
|---|---|---|---|---|---|---|---|
| **S0** | 28 | 8 | 10 | 10 | 15 | **71** | — |
| **S1** | 15 | 43 | 16 | 13 | 41 | **128** | 🟠 REBALANCE-CANDIDATE |
| **S2** | 7 | 22 | 57 | 24 | 15 | **125** | 🟠 REBALANCE-CANDIDATE |
| **S3** | 18 | 9 | 15 | 35 | 15 | **92** | — |
| **S4** | 0 | 5 | 4 | 7 | 2 | **18** | — (intentionally light: rehearsal/freeze) |
| **Per-WS total** | **68** | **87** | **102** | **89** | **88** | **434** | |

**Average sprint load = 86.8 SP. Outlier threshold (>40% above avg) = 121.5 SP.**

**🟠 S1 (128 SP, +47%) — REBALANCE-CANDIDATE.** Driver: BWS2 (43) front-loads all mandatory-data cohort generation, and BWS5 (41) builds engine + audit + boundary tests + CI at once. *Suggested moves (suggest only — not applied):*
- Slip **BWS5-T9** (unit+integration tests, 5) and part of **BWS5-T11** (CI, 5) into S2 — tests can accrue incrementally after the engine exists.
- BWS2's cohort tasks (T4–T7) are dependency-pinned to S1 (need portfolio v1). Rather than move them, **parallelize within BWS2** (a second owner/pair) — ties to team size **OQ-28**.

**🟠 S2 (125 SP, +44%) — REBALANCE-CANDIDATE.** Driver: BWS3 (57) — the entire agent build lands here. *Suggested moves (suggest only):*
- Slip **BWS4-T5** (staff evidence pack O2, 8) to S3, accepting that the G2 milestone demonstrates O1 (offer screen) + O4 (explanation) with O2 following in S3.
- **BWS3-T9** (RAG, 8) could slip to S3 if S2 explanations first use non-RAG grounding; re-ground in S3. Trade-off: weaker explanation quality at G2.

**Structural note:** S1+S2 hold the dependency-packed core (data → agents → integration); S0 (71) and S4 (18) have slack. Because the middle is dependency-bound, the cleanest rebalance is usually **more calendar/parallelism, not task shuffling** — resolve against **OQ-27** (duration), **OQ-28** (team size), **OQ-32** (velocity) before moving tasks. All suggestions above are advisory; no task was moved.

### 4.3 Calendar mapping placeholder (resolve once OQ-27 answers duration)

Sprints are relative until **OQ-27** sets bootcamp duration. Fill the "Calendar weeks" row then:

| | S0 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|
| Theme | Mobilize | Data + Engine | Intelligence | Integrate + Harden | Demo polish |
| Calendar weeks | _TBD (OQ-27)_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| *Illustrative — 8-week bootcamp* | wk 1 | wk 2–3 | wk 4–5 | wk 6–7 | wk 8 |
| *Illustrative — 5-week bootcamp* | wk 1 (½) | wk 1½–2 | wk 3 | wk 4 | wk 5 |

*(Illustrative rows are examples only, weighted toward the heavier S1/S2; not a commitment. If duration is very short, collapse S3+S4 and cut scope to O1/O2/O4 + O5 metric per review R5.)*

---

## 5. Critical Path & Milestones

### 5.1 Critical path (🔴 — the chain that sets minimum duration)

```
BWS1-T4 (ground-truth def, S0) ┐
BWS1-T3 (policy ranges, S0) ───┤
BWS2-T1 (schema, S0) ──────────┴─▶ BWS2-T2 (portfolio v1, S1)
BWS5-T3 (seam + API contract, S0) ─▶ BWS5-T2 (sim engine, S1)
        │                                    │
        └────────────┬───────────────────────┘
                     ▼
   BWS3-T3 (policy-guard, S1) + BWS3-T4 (analysis agent, S1)
                     ▼
   BWS3-T7 (offer-optimization agent, S2) ─▶ BWS3-T10 (explanation agent, S2)
                     ▼
   BWS4-T11 (wire screens ↔ API, S2) ─▶ BWS5-T10 (end-to-end test, S2)
                     ▼
   BWS5-T13 (deploy, S3) ─▶ BWS4-T15 (demo script, S3) ─▶ BWS4-T16 (rehearse + record, S4)
```

**Critical-path tasks:** BWS1-T3, BWS1-T4, BWS2-T1, BWS2-T2, BWS5-T3, BWS5-T2, BWS3-T3, BWS3-T4, BWS3-T7, BWS3-T10, BWS4-T11, BWS5-T10, BWS5-T13, BWS4-T15, BWS4-T16. **Two single points of failure** (per `workstreams.md`): the **ground-truth definition** (BWS1-T4) and the **seam + guard contract** (BWS5-T3 / BWS3-T3). Protect these first.

### 5.2 Milestones

| # | Milestone | Definition | Sprint (gate) | Key task IDs |
|---|---|---|---|---|
| **M1** | Foundations frozen | Ground-truth definition, policy ranges, seam + API contract, and synthetic schema agreed and frozen | End S0 (G0) | BWS1-T3, BWS1-T4, BWS2-T1, BWS5-T3, BWS3-T1 |
| **M2** | Simulated engine + synthetic portfolio ready | Sim engine produces base offers; portfolio v1 with ground-truth labels + data dictionary exists | End S1 | BWS5-T2, BWS2-T2, BWS2-T3, BWS2-T14 |
| **M3** | Policy-guard enforcing boundary end-to-end | Guard blocks an out-of-policy / segment-override attempt, logged in the audit trail; boundary tests green | End S1 (G1 ≈ source E6) | BWS3-T3, BWS5-T5, BWS5-T8 |
| **M4** | Bridge layer intelligent & integrated | Optimization + explanation + fairness agents + RAG + eval harness live; O1/O2/O4 demonstrable end-to-end on synthetic data | End S2 (G2 ≈ source E1/E3) | BWS3-T7, BWS3-T10, BWS3-T11, BWS3-T13a/b, BWS4-T5, BWS4-T6, BWS4-T11, BWS5-T10 |
| **M5** | First full demo run deployed | Deployed app; shared risk-adjusted metric, graduated offers, fairness + audit views; demo script drafted | End S3 (G3 ≈ source E7/E8) | BWS5-T13, BWS4-T15, BWS4-T7, BWS4-T10, BWS1-T13 |
| **M6** | Demo-day ready (go/no-go) | Rehearsed, recorded backup, frozen, honest-limits slide integrated; go/no-go taken (no-go allowed) | End S4 (G4 ≈ source E10) | BWS4-T16, BWS5-T14, BWS1-T14, BWS2-T17 |

---

## 6. Consistency & Update Rules

**ROADMAP.md is the operational source for task status. The ws files (`ws1.md`–`ws5.md`) remain the definition source.**

**How to update:**
1. **Status changes happen ONLY in ROADMAP.md** — edit the `Status` cell (TODO → IN-PROGRESS → REVIEW → DONE; use BLOCKED with a note). Do not track status in the ws files.
2. **Scope changes happen in the ws files first**, then sync here — if a task's definition, size, or dependencies change, edit the ws file, then update the matching ROADMAP row and re-run the reconciliation (§7 / TRACEABILITY §8). Never change scope only in ROADMAP.
3. **New tasks:** add to the ws file with the next `T<k>` id, then add the ROADMAP row; update the task count in TRACEABILITY §8 and README self-review.
4. **Owners** default to `TBD` until assignment (ties to **OQ-28**); set the `Owner` cell when a member/pair takes a workstream.
5. **Sprint placement** follows `workstreams.md` S0–S4 sequencing + the dependency graph; new placements not pinned there are marked `[INFERRED]`.
6. **The hard boundary is non-negotiable** — no status or scope edit may introduce a task that lets the layer override the bank's segment or exceed policy.

---

## 7. Sizing Notes (Appendix)

### 7.1 Mapping rule
Default conversion from the ws-file S/M/L sizes: **S→2, M→5, L→8** (Fibonacci). Applied to every task unless adjusted below.

### 7.2 Per-task adjustments (each ±1 Fibonacci step, with justification)
| Task | ws size | Default | Adjusted to | Justification |
|---|---|---|---|---|
| BWS1-T15 | S | 2 | **1** | Administrative OQ-impact tracking; no build deliverable — trivial. |

*(All other 82 tasks use the default mapping with no adjustment.)*

### 7.3 Splits (tasks that would exceed 8 points)
| Original | ws size | Split into | Each SP | Justification |
|---|---|---|---|---|
| BWS3-T13 (agent-evaluation harness) | L | **BWS3-T13a** (optimization-correctness vs ground truth + **100% guard-coverage** eval) + **BWS3-T13b** (latency/determinism eval + CI integration) | 5 + 5 | The harness spans a functional-correctness/safety-coverage suite and a distinct non-functional (latency/determinism) + CI-wiring effort; as one task it exceeded 8. Split preserves traceability via suffixes; both trace to ws3.md T13 (L4/A2/§8.1/R6). |

### 7.4 `[INFERRED]` sprint placements (not pinned by workstreams.md sequencing)
| Task | Placed | Reasoning |
|---|---|---|
| BWS1-T7 (persona catalogue) | S0 | Personas are needed early for BWS4 wireframes (S0/S1); ws1 owns them though `workstreams.md` listed "persona catalogue" under BWS4's S0 cell. |
| BWS1-T12 (shared-metric one-pager) | S2 | Spec must exist before BWS4 builds the shared-metric screen (S3); depends on metric def (S0) + sizing (S2). |
| BWS1-T11 (fairness position note) | S3 | Consumes BWS3 fairness-agent output (S2) and bias report (S3). |
| BWS1-T15 (OQ tracking) | S0 | Continuous/administrative; anchored at project start. |
| BWS2-T3 (ground-truth labels) | S1 | Labels annotate the portfolio (BWS2-T2, S1), so cannot precede it; the ground-truth *definition* (BWS1-T4) is what freezes at G0. Placed S1 for dependency consistency (ws2 DoD had implied G0). |
| BWS4-T8 (fairness view) | S3 | Renders fairness-agent output (S2); grouped with S3 view-building/polish to relieve the S2 peak. |
| BWS4-T9 (audit view) | S3 | Renders audit trail v2 (BWS5, S2); view work grouped in S3. |
| BWS4-T10 (shared-metric screen) | S3 | Depends on instrumentation (BWS5-T7, S2) + one-pager (BWS1-T12, S2); feeds E7 at G3. |
| BWS5-T17 (traceability tooling) | S0 | Ritual tooling; set up at project start so weekly checks run from S1. |

---

*ROADMAP consolidated from the ws files with no new work introduced. Self-review printed with the delivering response and recorded in `README.md`.*
