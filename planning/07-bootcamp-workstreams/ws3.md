# BWS3 — AI Core & Agentic Architecture ★
### The bridge-layer intelligence itself

**One-line mission:** build the multi-agent bridge layer that optimizes offers *within policy* — the highest-evaluation-weight workstream. The single most important component is the one that makes the hard boundary **structurally impossible to breach**.

**★ Highest jury weight** (AI/agents + innovation, `workstreams.md` scoring table). Staff first if headcount is tight (OQ-28).

**Boundary reminder (the flagship feature):** the layer **never re-scores, never overrides the segment, never changes engine inputs, never auto-approves above policy** (source §4). In this architecture that is enforced by a **deterministic policy-guard agent** — not an LLM — so override is impossible by construction, and every attempt is logged. Innovation and integrity are the same artifact (review L3).

---

## Objective
Deliver a working, auditable, multi-agent bridge layer that: ingests the simulated engine's segment + customer signals, proposes an optimized offer *within the segment's approved policy range*, explains it, audits it for fairness, and blocks anything out of bounds — with an evaluation harness proving it behaves. Combine LLM reasoning where it adds value (explanation, signal narrative, verbatim analysis) with classical ML / deterministic logic where correctness and auditability are non-negotiable (guard, limits).

## In scope
- **Multi-agent design & orchestration:**
  - *Analysis agent* — reads engine output + BWS2 signals, surfaces within-segment differentiation evidence (H5) and boundary/stale/thin-file flags (H1/H2/H3/H8).
  - *Policy-guard agent* — **deterministic**; validates every proposed offer against the segment's approved range (BWS1 policy config); blocks + logs violations. Hard gate.
  - *Offer-optimization agent* — proposes the within-policy offer (limit/pricing within band) using analysis evidence; supports graduated offers (O6).
  - *Explanation agent* — generates staff-facing evidence pack (O2) and customer-facing explanation + improvement path (O4) via LLM with structured output.
  - *Fairness-audit agent* — computes disparity metrics on adjustments, flags/corrects seeded disparity (H14).
  - *Orchestrator* — routes, enforces guard-before-commit, writes to the audit trail (BWS5).
- **Modern technique usage:** tool use / function calling, **structured outputs**, **RAG over the policy corpus** (BWS1 regulatory-awareness + policy docs), **LLM-as-judge** evaluation of explanation quality (H10).
- **Classical ML** where appropriate: within-segment signal separation (H5), stale-score/migration signal (H2/H8), attrition (H11) — *signal existence / offer support only, never a re-score* (source H5 guard).
- **Agent-evaluation harness:** ground-truth-based tests (BWS2 labels) for optimization correctness, guard coverage, explanation quality, fairness, determinism/latency.

## Out of scope
- Generating data (→ BWS2) and policy ranges (→ BWS1 — consumed as config).
- The UI (→ BWS4 — BWS3 exposes structured outputs it renders).
- Deployment, the audit *store* itself, and CI (→ BWS5 — BWS3 writes through BWS5's audit API).
- **Any capability to re-score or change the segment.** Not built, not stubbed, not reachable.

## Inputs from the planning package
- **Hypotheses:** H1–H5, H7, H8, H11 (analysis/optimization), H9/H10 (explanation), H14 (fairness).
- **Opportunities:** O1 (within-segment differentiation), O2 (boundary flagging + evidence pack), O6 (graduated offers), O8 (advisory signal enrichment).
- **Assumptions:** A1 (under-classification exists — detect it), A2 (ground truth — evaluate against), A6/A9 (bounded + auditable → governance acceptance).
- **Deliverables:** feeds D1 (diagnosis), D4 (hypothesis validation), D5 (O-sizing evidence), D10 (audit requirements).
- **Exit criteria:** E1 (materiality — detectable), E6 (insertion point — the layer plugs in), E9 (fairness executed).
- **Risks (mitigations owned here):** ground-truth ambiguity, feedback loops, bias amplification, opacity, silent scope creep (source §6.2) → guard + explainability + fairness agent + eval harness + logging.
- **Deltas:** L2 (models), L3 (agents), L4 (experimentation), L6 (novel tech), K5 (boundary), R6 (determinism where it binds).

## Dependencies on other workstreams
- **Consumes from BWS1:** policy ranges (guard config), ground-truth definition, regulatory corpus for RAG, success metrics.
- **Consumes from BWS2:** labelled data, cohorts, signals, train/eval splits.
- **Consumes from BWS5:** the sim-engine output contract (segment + signals in), the audit API (log out), agent runtime/hosting, secrets for LLM provider (OQ-29).
- **Provides to BWS4:** structured optimized offers + explanations + evidence packs + fairness results to render.
- **Provides to BWS1:** fairness-audit output (E9) and H1–H5/H7/H8/H11 validation evidence (D4).

## Task breakdown

| # | Task | Size | Traces to | Feeds |
|---|---|---|---|---|
| T1 | Agent inventory + **boundary spec** (what each agent may/may not touch; guard-before-commit invariant) | M | §4, K5, L3, D10 | all agents, boundary review |
| T2 | LLM provider / orchestration framework spike; structured-output contract | M | L6, OQ-29 | BWS5, all agents |
| T3 | **Policy-guard agent (deterministic)**: validate offer ∈ segment approved range; block + reason-code; never mutate segment | L | §4, K5, R6, E-boundary | orchestrator, audit |
| T4 | Analysis agent: consume engine segment + signals; emit within-segment + boundary/stale/thin-file evidence | L | H1/H2/H3/H5/H8, O1/O2 | optimization, explanation |
| T5 | Classical ML: within-segment signal separation experiment (signal existence only, no re-score) | M | H5, O1, L4, §6 H5-guard | analysis agent, D4 |
| T6 | Classical ML: stale-score/migration + attrition signals | M | H2/H8/H11 | analysis agent, D4 |
| T7 | Offer-optimization agent: propose within-policy offer; call guard before returning | L | O1, A1, §4 | orchestrator, BWS4 |
| T8 | Graduated / staged offer logic ("limit → X after behavior Y within policy") | M | O6, H7 | BWS4, BWS1 |
| T9 | **RAG over policy corpus** (BWS1 regulatory-awareness + policy docs) grounding explanations/guard rationale | L | L6, D7, O4 | explanation, guard rationale |
| T10 | Explanation agent: staff evidence pack (O2) + customer explanation & improvement path (O4), structured output | L | O2/O4, H9/H10 | BWS4 |
| T11 | Fairness-audit agent: disparity metrics on adjustments; detect + correct seeded disparity | L | H14, E9, §6.3 | BWS1, BWS4 |
| T12 | Orchestrator: routing, guard-before-commit enforcement, audit-log writes | M | K5, D10 | BWS5 |
| T13 | **Agent-evaluation harness**: optimization correctness vs ground truth, **guard coverage (must be 100%)**, latency/determinism | L | L4, A2, R6, §8.1 | G-gates, deck |
| T14 | **LLM-as-judge** explanation-quality eval (clarity, faithfulness, no protected-attribute leakage) | M | H10, L6, review R4 | BWS4, deck |
| T15 | Guardrail hardening: prompt-injection resistance, refusal on out-of-scope asks (e.g., "override the segment") | M | §6 opacity/scope-creep, R6 | boundary review |
| T16 | Failure-mode fallbacks (LLM down/timeout → safe default = base offer unchanged, logged) | S | R6, boundary | BWS5, demo |
| T17 | Determinism/latency tuning for live demo | S | R6, demo | BWS4/BWS5 |

## Definition of done
- Guard agent achieves **100% coverage** in the eval harness: **no out-of-policy or segment-override action can be committed**; every attempt is logged with a reason code.
- End-to-end: engine segment + signals → analysis → optimized within-policy offer → explanation → fairness check → audit write, on the synthetic data.
- H1–H5/H7/H8/H11 evidence produced against ground truth; H14 disparity detected and corrected; H9/H10 explanations pass LLM-as-judge.
- RAG grounds explanations in the policy corpus; structured outputs stable for BWS4.
- Eval harness runs in CI (BWS5); failure-mode fallback verified to keep the base offer unchanged.

## Demo-day contribution
- **The flagship moment:** attempt to push an offer above the segment's policy / force a segment override → the **guard blocks it live**, logged in the audit trail. "Our most advanced AI component is also the reason the bank can trust us."
- The **agent trace**: show the orchestrator routing through analysis → optimization → guard → explanation → fairness.
- The **eval harness numbers** (guard coverage, optimization vs ground truth, fairness pre/post) as execution + AI-quality evidence.

## Suggested owner skill profile
ML/LLM engineer fluent in agent frameworks, function calling / structured outputs, RAG, and evaluation; comfortable mixing classical ML with LLMs and drawing the deterministic-vs-generative line correctly. Understands why the guard must be code, not a prompt. This is the technical center of gravity — the strongest builder on the team. Pairs with BWS2 (data/eval) and BWS5 (integration).
