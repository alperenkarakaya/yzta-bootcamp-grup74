# Bootcamp Workstreams — Master File
## Intelligent Offer Optimization Bridge Layer — build restructured into 5 owned workstreams

> **⚠️ Superseded on priorities (2026-07-10).** The BWS3 framing below ("★ highest jury weight, multi-agent architecture") is contradicted by the agent audit in `../RESEARCH_STRATEGY.md §2.3` (only the LLM assistant is a real agent) and by the statistical-rigor mandate (AI is priority #9, below model validity). The 5-workstream *ownership/dependency structure* remains useful; the *AI-weighting and jury-optics rationale* is historical. Current priorities: `../RESEARCH_STRATEGY.md`.

**Read order:** this file first, then `ws1.md … ws5.md`. Grounded in the source of truth (`../early-phase-plan-credit-offer-optimization.md`) and the delta layer (`../bootcamp-adaptation-review.md`). Every task in every ws file traces to a source ID (P/A/H/O/D/E/§7/§8) or to a bootcamp-adaptation delta (K/A/L/R). See `../TRACEABILITY.md` §8 for the item→workstream map.

**ID convention (to avoid collision):** bootcamp workstreams are **BWS1–BWS5** in traceability; the source's Appendix-A workstreams are **source-WS1…6**. They are different partitions of the work (see `../bootcamp-adaptation-review.md` §6).

---

## The hard boundary — invariant across all five workstreams

> **The bridge layer optimizes offers *within* the bank model's approved policy. It never re-scores customers, never overrides or changes the engine's segment, never adjusts the engine's inputs, never auto-approves above-policy limits.** (source §4, §6)

In the bootcamp this is no longer a paper promise — it is a **hard-coded architectural constraint**:
- **BWS3** implements a deterministic **policy-guard agent** that blocks any proposed offer outside the segment's approved range.
- **BWS5** implements an **audit trail** that logs every offer adjustment with the segment (unchanged), the base offer, the optimized offer, the policy bound checked, and the responsible agent.
- **BWS4** renders the segment on screen as **fixed/read-only**; only the within-policy offer is shown as optimized.
- **BWS1** narrates it as our domain integrity *and* our strongest jury story (innovation = integrity; see review L3).

Any task in any workstream that appears to weaken this boundary is a defect, not a feature.

---

## The five workstreams at a glance

| BWS | Name | One-line mission | Highest jury axis it serves | Suggested owner |
|---|---|---|---|---|
| **BWS1** | Business & Domain | Own the problem (P1/P2/P3), the domain rules, the regulatory-awareness narrative, and the jury-facing business case | Business value; Presentation | Domain/PM-minded, strong writer |
| **BWS2** | Data & Simulation | Generate the synthetic portfolio that makes H1–H14 testable and provides ground truth | Execution quality | Data engineer / analyst |
| **BWS3** | AI Core & Agentic ★ | Build the multi-agent bridge layer + guard + eval harness (highest weight) | AI/agents; Innovation | ML/LLM engineer |
| **BWS4** | Product, UX & Explainability | Build the demoable surface + explanations + demo script | Presentation; Innovation | Product/frontend + UX |
| **BWS5** | Engineering, Integration & Quality | Repo, sim engine seam, APIs, audit trail, tests, CI, deploy, monitoring | Execution quality | Full-stack / platform engineer |

★ **BWS3 carries the highest evaluation weight** (agentic AI). Staff it first if headcount is tight (OQ-28).

---

## Dependency graph (BWS → BWS)

```
                       ┌────────────────────────────┐
                       │  BWS1 Business & Domain      │
                       │  (problem, rules, metrics,   │
                       │   personas, regulatory note) │
                       └───────┬───────────┬──────────┘
              policy ranges,   │           │   success metrics,
              ground-truth def,│           │   personas, demo story
              P1/P2/P3 mix     ▼           ▼
      ┌───────────────────────────┐   ┌───────────────────────────┐
      │ BWS2 Data & Simulation     │──▶│ BWS4 Product, UX & Explain │
      │ (synthetic portfolio,      │   │ (offer screens, evidence   │
      │  ground truth, data dict)  │   │  pack, explanations, demo) │
      └──────────┬─────────────────┘   └──────────▲────────────────┘
                 │ labelled data,                 │ rendered offers,
                 │ signals, cohorts               │ explanations
                 ▼                                │
      ┌───────────────────────────┐               │
      │ BWS3 AI Core & Agentic  ★  │───────────────┘
      │ (agents, guard, RAG, eval) │  optimized offers + explanations
      └──────────┬─────────────────┘
                 │ agent contracts, guard rules, logs
                 ▼
      ┌───────────────────────────────────────────────────────────┐
      │ BWS5 Engineering, Integration & Quality                     │
      │ (sim engine seam, APIs, audit trail, tests, CI, deploy)     │
      │  — the substrate everything runs on; consumes all above     │
      └───────────────────────────────────────────────────────────┘
```

**Reading the graph:**
- **BWS1 is the upstream source of truth for meaning** (problem framing, policy ranges, ground-truth definition, success metrics, personas). Everyone consumes it.
- **BWS2 feeds BWS3** (labelled/ground-truth data) and **BWS4** (data to display).
- **BWS3 feeds BWS4** (optimized offers + explanations) and is bound by **BWS1** (policy ranges) and **BWS5** (guard/audit contracts).
- **BWS5 is the substrate**: it defines the sim-engine seam BWS3 plugs into, the APIs BWS4 calls, and the audit store all writes flow through. It both *enables* (early: seam + repo) and *consumes* (late: integration + deploy).

**Critical path:** `BWS1 policy ranges + ground truth` → `BWS2 synthetic data v1` → `BWS5 sim-engine seam + API contract` → `BWS3 guard agent + optimization agent` → `BWS4 offer screen` → `BWS5 integration + deploy` → **demo**. Single points of failure: (1) ground-truth definition (blocks BWS2 labels and all H1–H4 demos), (2) the sim-engine seam + guard contract (blocks integration). Both are scheduled in Sprint 1.

---

## Suggested sprint sequencing (relative — calendar TBD via OQ-27)

Expressed in **relative sprints** because bootcamp duration is unconfirmed (OQ-27). If the bootcamp is N weeks, map Sprint k proportionally. A "sprint" below ≈ one integration cycle, not a fixed number of days.

| Sprint | Theme | BWS1 | BWS2 | BWS3 ★ | BWS4 | BWS5 | Gate at end |
|---|---|---|---|---|---|---|---|
| **S0 Mobilize** | Agree meaning + skeleton | Problem one-pager (P1/P2/P3), policy ranges, **ground-truth definition (A2/E2)**, success metrics | Synthetic schema design (M/U items) | Agent inventory + boundary spec; provider spike (OQ-29) | Persona catalogue, demo story draft, wireframes | Repo `./product/` skeleton, **sim-engine seam + API contract**, audit-store stub | **G0:** ground truth signed off (internal); seam contract frozen |
| **S1 Data + Engine** | Data flows through a stub | Regulatory-awareness draft (D7-as-note), risk register refresh | **Synthetic portfolio v1** (M1–M9 fields, seeded P1/P2/P3 mix, hard cohorts) + data dictionary | Analysis agent + **policy-guard agent** (deterministic) on stub data | Offer screen (static data), segment shown read-only | Sim bank engine (score→segment→base offer), audit trail v1, CI green | **G1 (≈source E6):** working insertion point demonstrated; guard blocks an out-of-policy offer |
| **S2 Intelligence** | Agents produce real optimizations | Opportunity sizing v1 (O5 metric, D5) on synthetic data | Useful signals (U1–U8), stale-score/thin-file/override cohorts, bias checks | Offer-optimization + explanation + fairness-audit agents; **RAG over policy docs**; eval harness v1 | Staff evidence pack (O2), customer explanation + improvement path (O4) | End-to-end wiring BWS2→3→4; audit trail v2 (full lineage); agent monitoring | **G2 (≈source E1/E3):** modelled problem material + at least O1/O2/O4 demonstrable end-to-end |
| **S3 Integrate + Harden** | One clean end-to-end run | Business case + jury narrative; regulatory note final | Data-quality/bias report; ground-truth honesty appendix (R1/R4) | Guardrail + eval hardening; graduated-offer logic (O6) support; LLM-as-judge on explanations | Graduated offers (O6) UI; full demo script; accessibility/explainability polish | Integration tests, load/robustness, **deploy for demo day**, audit export | **G3 (≈source E7/E8/E10):** shared risk-adjusted metric on screen; demo runbook green |
| **S4 Demo polish** | Rehearse + de-risk | Presentation deck, honest-limits slide (R1–R6) | Fallback dataset + seeded "wow" cases | Determinism/latency checks; failure-mode fallbacks | Rehearse demo; record backup video | Freeze, smoke tests, rollback plan | **G4 (≈source E10):** go/no-go on demo readiness (no-go allowed) |

If N is very short, collapse S3+S4 and cut scope to O1/O2/O4 + O5 metric (drop O6 build; keep it "designed, not built" per review R5).

---

## Cross-cutting rituals

1. **Weekly traceability check (owned jointly, ~30 min).** Re-run the ID coverage over `ws1–ws5.md` and `../TRACEABILITY.md` §8: every task still maps to a source ID or a review delta; no orphaned tasks; no out-of-range IDs; no task that weakens the hard boundary. Update the orphan log if anything drifts.
2. **Integration checkpoint each sprint gate (G0–G4).** All five owners run the current end-to-end path together; a gate is passed only when the cross-BWS handoffs work (contracts in the dependency graph). No "works on my branch" gates.
3. **Boundary review (every gate).** One owner plays the "Model-Risk persona" and tries to make the layer override a segment or exceed policy. If they can, it is a P0 defect. This operationalizes review K5/L3/R6 and source §6 "silent scope creep."
4. **Ground-truth honesty log (continuous).** BWS2 records every data-generating assumption; BWS1 keeps the "what we can and cannot claim" list (review R1/R4) current, so the demo's honesty slide is never a scramble.
5. **Demo dry-run from S2 onward.** Every sprint ends with a 5-minute run of whatever works, to catch integration and narrative gaps early (BWS4 drives).
6. **Open-questions sweep (weekly).** Check OQ-27…OQ-31 (duration, team, tech rules, jury rubric, demo format) for answers; when answered, update sequencing and the jury-scoring table below.

---

## Jury-scoring alignment table

Which workstream produces the evidence for each evaluation dimension. **Dimensions are inferred (OQ-30)** and must be reconciled with the official rubric when known. ●=primary evidence, ○=supporting.

| Evaluation dimension (inferred) | BWS1 | BWS2 | BWS3 ★ | BWS4 | BWS5 | Headline evidence artifact |
|---|---|---|---|---|---|---|
| **AI & agentic architecture** | ○ | ○ | ● | ○ | ○ | Multi-agent bridge layer + deterministic policy-guard + eval harness (BWS3) |
| **Innovation / novel technology** | ○ | ○ | ● | ● | ○ | Guard agent that makes bank-override *structurally impossible* + RAG over policy + LLM-as-judge (BWS3/BWS4) |
| **Business value / domain** | ● | ○ | ○ | ● | | P1/P2/P3 diagnosis + O5 under-lending metric + risk-adjusted sizing (BWS1) |
| **Execution quality** | ○ | ● | ○ | ○ | ● | Synthetic data + full audit trail + tests/CI/deploy + traceability (BWS2/BWS5) |
| **Presentation / storytelling** | ● | ○ | ○ | ● | ○ | Demo script: engine → bridge → optimized offer → explanation → audit + fairness, with honest-limits slide (BWS4/BWS1) |
| **Responsible AI / trust** (likely sub-criterion) | ● | ○ | ● | ● | ○ | Fairness-audit agent + explainability + regulatory-awareness note + boundary (BWS1/BWS3/BWS4) |

**Coverage read:** every inferred dimension has at least one **●** owner; BWS3 anchors the two highest-weight axes; no dimension is orphaned.

---

## Definition of done — program level (all workstreams)

The program is demo-ready when:
- A customer/portfolio flows **end-to-end**: simulated engine → bridge layer → optimized offer **within policy** → staff evidence pack + customer explanation → audit trail + fairness dashboard update live.
- The **policy-guard demonstrably blocks** an attempted out-of-policy / segment-override action, logged in the audit trail (boundary proof).
- The **O5 under-lending metric** and a **risk-adjusted sizing** figure render from the synthetic portfolio, with the honesty caveat (review R1) on screen.
- **H1–H4 (problem existence)** and at least the **O1/O2/O4** value mechanisms are demonstrable on the synthetic data; deferred items are listed as "designed, not built" (review R5).
- **Traceability** (§8) shows zero orphaned tasks; **OQ-27…OQ-31** are answered or explicitly flagged as assumptions in the deck.
- A recorded backup demo exists (BWS4/BWS5).

---

## Self-review — file completeness
- **Dependency graph** between the 5 workstreams: present (BWS1 upstream, BWS5 substrate, critical path + SPOFs named). ✔
- **Suggested sprint sequencing:** present as relative sprints S0–S4 with per-BWS activities and gates, calendar-agnostic pending OQ-27. ✔
- **Cross-cutting rituals:** integration checkpoints, weekly traceability check, boundary review, honesty log, demo dry-run, OQ sweep. ✔
- **Jury-scoring alignment table:** present, maps each inferred dimension to workstreams, flagged provisional pending OQ-30. ✔
- **Hard boundary** stated as an invariant and assigned owners (BWS3 guard, BWS5 audit, BWS4 UI, BWS1 narrative). ✔
- **Per-ws file completeness:** each of ws1–ws5 has objective, in-scope / out-of-scope, a 10–20 task breakdown with S/M/L sizes, dependencies on other workstreams, planning-package inputs (A/H/O/D/E/§7/§8 IDs), definition of done, demo-day contribution, and owner skill profile. ✔ (ws1: 15 tasks, ws2: 18, ws3: 17, ws4: 16, ws5: 17.)

## Self-review — task traceability (the required closing check)
**Claim:** every task in ws1–ws5 traces to either the **source plan** (`../early-phase-plan-credit-offer-optimization.md`) or the **bootcamp-adaptation review** (`../bootcamp-adaptation-review.md`).

**Method:** every task table in ws1–ws5 carries a mandatory **"Traces to"** column; the ID scan below confirms each value resolves to a source ID (P/A/H/O/D/E/§n/§7 M-U-OPT/§8) or a review delta (K#/A#/L#/R#) or a logged OQ.

| Workstream | Tasks | All tasks have a "Traces to" value | Trace targets used |
|---|---|---|---|
| ws1 Business | T1–T15 | ✔ | §1.1/§1.2/§1.3, §3, §4, §6.3, §8; A2/A5/A9; O5/O6/O7; D1/D3/D5/D6/D7/D9/D10; E1/E2/E7/E9; H13/H14; K1/K2/K9/K10/K11, A2/A3/A6/A7, R1–R6; OQ-27…31 |
| ws2 Data | T1–T18 | ✔ | §1.1/§1.2, §6.3/§6.5, §7 M1–M9/U1–U8/OPT5, §8.2; A1/A2/A7; H1–H11/H14; O1/O5/O6; D8; E2/E5; A1/K9/K11/R1/R4 |
| ws3 AI Core | T1–T17 | ✔ | §4, §6/§6.2/§6.3; A1/A2/A6/A9; H1–H5/H7/H8/H10/H11/H14; O1/O2/O4/O6/O8; D4/D7/D10; E1/E6/E9; K5/L2/L3/L4/L6/R4/R6; OQ-29 |
| ws4 Product | T1–T16 | ✔ | §3, §4, §6.3; A3; H1/H4/H7/H9/H10/H14; O1/O2/O4/O6; D1/D9/D10; E7/E9; K5/K10/L5/A2/R1/R4/R5/R6 |
| ws5 Eng | T1–T17 | ✔ | §4, §6, §8; A5/A8; O5; D2/D7/D8/D9/D10; E5/E6/E8/E10; K5/K7/K8/L1/A5/R5/R6; OQ-29 |

**Untraceable tasks:** **none.** Every task resolves to a source ID or a review delta (or a logged OQ where the task is "track/answer an open question").

**Notes on trace *targets* that are themselves deltas (not source):** tasks tracing only to review deltas (e.g., ws4 T2 story arc → R1/R5; ws5 T17 traceability tooling → K8; ws1 T15 → OQ sweep) are intentionally bootcamp-introduced work; the review is an authorized second source of truth per the task brief, so these are traceable, not orphans. All such tasks were cross-checked to not weaken the hard boundary.

**Source items with no ws task (checked, all intentional):** none analytical — the four deliberate deferrals are logged in `../TRACEABILITY.md` §8.1 (source-WS relabeling B1; sim-N/A vendor/bureau risks B2; OPT1/OPT4 DO-NOT-COLLECT B3; unknown externalities → OQ-27…31 B4). No silent orphan remains.
