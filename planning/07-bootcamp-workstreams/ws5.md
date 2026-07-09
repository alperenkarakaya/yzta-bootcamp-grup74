# BWS5 — Engineering, Integration & Quality
### The substrate everything runs on — and the audit trail that operationalizes governance

**One-line mission:** own the repo, the simulated bank engine + its interception seam, the APIs between engine ↔ bridge ↔ UI, the **audit trail** (traceability of every offer adjustment — this operationalizes D10), testing, CI, deployment for demo day, and the agent monitoring/eval harness runtime.

**Boundary reminder:** BWS5 makes the boundary *enforceable and provable*. The **audit trail** logs every adjustment with the segment (unchanged), base offer, optimized offer, policy bound checked, guard result, and responsible agent — so anyone can verify the layer never overrode the bank (source §4, §6; D10; review K5/R6).

---

## Objective
Provide a clean, reproducible engineering foundation under `./product/` so the other workstreams integrate without friction: a simulated engine with a well-defined seam, typed APIs, a durable audit store, an evaluation/monitoring harness runtime, tests + CI, and a demo-day deployment with a rollback plan. Turn the source's D2 (decision-flow map) and D10 (governance/audit) from documents into running code.

## In scope
- **Repo structure `./product/`**: modules for sim engine, bridge layer (BWS3 plugs in), UI (BWS4), data (BWS2), audit store, eval harness; env/setup, secrets handling (LLM keys — OQ-29).
- **Simulated bank engine (review A5):** score → segment → base offer, with a clean, one-directional **interception seam** (bridge reads segment + signals, returns an optimized offer; cannot write back a segment). This *is* the "insertion point" (source E6).
- **APIs / contracts:** engine→bridge (segment + signals), bridge→UI (optimized offer + explanation + fairness + audit ref), all typed/structured (aligns with BWS3 structured outputs).
- **Audit trail / lineage store (operationalizes D10):** append-only log of every adjustment; queryable; exportable for the demo.
- **Testing:** unit + integration + end-to-end; **boundary tests** that assert no segment mutation and no out-of-policy commit; fixtures from BWS2.
- **CI**: run tests + BWS3 eval harness on every change; block merge on red or on a boundary-test failure.
- **Deployment for demo day**: hosted, reproducible, with a smoke test and rollback/backup plan.
- **Agent monitoring**: capture agent traces, latencies, guard-block events, errors for the demo and for debugging.

## Out of scope
- The agent logic itself (→ BWS3 — BWS5 provides the runtime, audit API, and CI it runs in).
- Data content (→ BWS2 — BWS5 stores/serves it) and UI design (→ BWS4 — BWS5 serves the API).
- Business framing (→ BWS1). BWS5 never defines policy ranges; it enforces them via the guard's config and the audit tests.

## Inputs from the planning package
- **Deliverables:** D2 (current-state decision flow → as-built architecture of our sim), D10 (governance & accountability → audit trail + lineage), supports D8 (data storage) and D9 (metric instrumentation).
- **Exit criteria:** E6 (viable insertion point — we build the seam), supports E8 (governance/audit accepted → audit trail), E10 (go/no-go on demo readiness).
- **Assumptions:** A8 (interception feasible — trivially true, we design the seam).
- **Risks (mitigations owned here):** R-OPS (no insertion point → we build one; ownership vacuum → audit lineage; front-line confusion → clear two-layer trace), R-DAT (data quality via tests). Vendor/contract risks kept "sim: N/A, real-world: applies" (review A5).
- **Deltas:** L1 (architecture in scope), A5 (sim engine + seam), K7 (exit gates as CI gates), K8 (traceability), R6 (determinism/auditability).

## Dependencies on other workstreams
- **Provides to BWS3:** the sim-engine output contract, the audit API to write through, agent runtime/hosting, secrets.
- **Provides to BWS4:** the bridge→UI API and hosting.
- **Provides to BWS2:** the schema landing zone + fixtures wiring.
- **Provides to BWS1:** metric instrumentation hooks (O5) and audit exports for the governance/regulatory narrative.
- **Consumes from BWS1:** policy-range config (to load into the guard) and success-metric definitions (to instrument).
- **Consumes from BWS2:** schema + generator (to serve behind the engine).
- **Consumes from BWS3:** agent contracts + eval harness (to run in CI).

## Task breakdown

| # | Task | Size | Traces to | Feeds |
|---|---|---|---|---|
| T1 | Repo skeleton `./product/` (modules, env, setup, README, secrets handling) | M | L1, OQ-29 | all |
| T2 | **Sim bank engine**: score → segment → base offer, seeded from BWS2 data | M | A5, D2, review A5 | BWS3, BWS4 |
| T3 | **Interception seam + API contract** (engine→bridge: segment+signals; one-directional, no segment write-back) | L | E6, §4, K5, A8 | BWS3, G0/G1 gates |
| T4 | bridge→UI API (optimized offer + explanation + fairness + audit ref), typed/structured | M | integration, BWS3 structured outputs | BWS4 |
| T5 | **Audit trail / lineage store** (append-only: segment unchanged, base→optimized, policy bound, guard result, agent) | L | D10, K5, §6 | boundary tests, BWS4 audit view |
| T6 | Load BWS1 **policy-range config** into the guard; config-as-code with validation | M | §4 policy ranges, A5 | BWS3 guard |
| T7 | Metric instrumentation hooks (O5 under-lending metric + risk-adjusted counters) | M | O5, §8, D9 | BWS1, BWS4 metric screen |
| T8 | **Boundary tests**: assert no segment mutation, no out-of-policy commit, guard-block logged | L | K5, §4, R6 | CI gate, boundary review |
| T9 | Unit + integration tests with BWS2 fixtures | M | K8, E5 | CI |
| T10 | End-to-end test: portfolio → engine → bridge → offer → audit entry | M | program DoD | G2/G3 |
| T11 | **CI pipeline**: run tests + BWS3 eval harness; block on red or boundary-test failure | M | K7, L4 | all, gates |
| T12 | Agent monitoring: capture traces, latencies, guard-block events, errors | M | R6, D10 | demo, debugging |
| T13 | **Deploy for demo day** (hosted, reproducible) + smoke test | L | E10, demo | demo day |
| T14 | Rollback / backup plan + offline fallback dataset wiring (with BWS2) | S | demo risk, review R5 | demo day |
| T15 | Audit export (CSV/JSON) for the governance/regulatory narrative | S | D10, D7 | BWS1 deck |
| T16 | Performance/robustness pass (latency budget for live demo, LLM-timeout handling) | M | R6, demo | BWS3/BWS4 |
| T17 | Weekly traceability-check tooling (ID scan over ws1–ws5 + TRACEABILITY §8) | S | K8, ritual | all |

## Definition of done
- `./product/` runs end-to-end locally and deployed: engine → bridge → UI → audit, seeded from BWS2 data.
- The **interception seam is one-directional** and covered by boundary tests proving no segment mutation and no out-of-policy commit; CI blocks on any boundary-test failure.
- Audit trail records full lineage for every adjustment and is exportable; the BWS4 audit view reads it live.
- CI runs tests + BWS3 eval harness green; agent monitoring captures traces + guard-block events.
- Demo deployment has a smoke test, a rollback plan, and an offline fallback dataset.

## Demo-day contribution
- The **infrastructure that makes the boundary provable**: pull up the audit trail and show, for any offer, that the segment was untouched and the policy bound was checked.
- The **"it actually runs" credibility**: deployed app, green CI, eval harness in the pipeline — execution-quality evidence.
- The **safety net**: rollback + recorded backup so the live demo cannot fully fail.

## Suggested owner skill profile
Full-stack / platform engineer who can stand up a clean repo, typed APIs, a datastore, CI, and a deploy quickly; values testing and reproducibility; understands audit/lineage and why append-only logging matters for trust. The "make it real and keep it green" engineer. Pairs with BWS3 (contracts/runtime) and BWS4 (API/hosting).
