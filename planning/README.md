# Early Phase Working Package — Credit Offer Optimization Bridge Layer
**This file is the master plan and index for the whole package. Read it first in any future session.**

## What this is

An execution-ready **Phase 1 (Early Phase) working package** for the "Intelligent Offer Optimization Bridge Layer for Credit Segmentation" consulting engagement, built entirely from the source of truth:

> **`early-phase-plan-credit-offer-optimization.md`** (project root)

Every artifact traces to that document's IDs: sub-problems **P1–P3**, assumptions **A1–A10**, hypotheses **H1–H14**, opportunities **O1–O8**, deliverables **D1–D11**, exit criteria **E1–E10**, §6 risks, §7 data inventory, §8 KPIs, Appendices A/B. The source document wins any conflict; ambiguities go to the open-questions log (`00-program/open-questions.md`), never resolved by guessing.

## Hard constraints (binding on all future work in this package)

1. **No solution design, no algorithms, no ML model recommendations, no product code, no architecture.** Phase 1 is planning, discovery, templates, validation protocols, and project-management artifacts only (source scope-discipline line, quoted in `00-program/charter.md` §2).
2. **The bridge-layer boundaries are bright lines** (source §4, verbatim): the layer shall never re-score customers, override segments automatically, adjust the engine's inputs, or auto-approve above-policy limits.
3. **"No-go is a valid outcome"** (source §10) is preserved in every decision-related artifact: charter, workplan, D5, D11, E10 checklist, steering pack.
4. **Data minimization** (source §7 rule): no data item is collected without a stated hypothesis.
5. **Do not rename source IDs.** New IDs exist only where the source assigned none, declared conventions: data items **M1–M9 / U1–U8 / OPT1–OPT5**; risks **R-BUS-xx / R-AI-xx / R-REG-xx / R-OPS-xx / R-DAT-xx**; open questions **OQ-01…OQ-26** (OQ-01–10 = Appendix B verbatim); milestones **MS1–MS6**; workstreams **WS1–WS6**.

## Package structure (50 files)

```
credit-calc/
├── early-phase-plan-credit-offer-optimization.md   ← SOURCE OF TRUTH (do not edit)
├── README.md                    ← this file: master plan + self-review record
├── CLAUDE.md                    ← session pointer for Claude Code
├── TRACEABILITY.md              ← A/H/O/D/E/data → artifact matrix + orphan/defect log
├── 00-program/
│   ├── charter.md               ← objectives, scope, quoted boundaries, governance, decision rights
│   ├── workplan.md              ← weeks 1–10 (Appendix A expanded), critical path → E1–E10
│   ├── raci.md                  ← D1–D11 × all §3 stakeholders (+Finance/IT/CRO flags)
│   └── open-questions.md        ← OQ-01…OQ-26 (Appendix B + found ambiguities)
├── 01-hypothesis-validation/
│   ├── h01.md … h14.md          ← per hypothesis: statement, verbatim falsification, data (M/U/OPT),
│   │                               protocol (business terms), sign-offs, effort, exit criteria fed
│   └── validation-plan.md       ← dependency groups, waves, H→data→D→E table, A1–A10 coverage,
│                                   "≥10 tested" deferral priority (OQ-26)
├── 02-stakeholders/             ← one interview guide per §3 group (8–12 questions each,
│   │                               evidence lists, tensions incl. Risk-vs-Business shared metric, D3 feeds)
│   ├── guide-credit-risk.md          guide-business-commercial.md
│   ├── guide-model-risk-validation.md guide-compliance-legal.md
│   ├── guide-data-science.md         guide-product-team.md
│   ├── guide-executives.md           guide-front-line.md
│   ├── guide-internal-audit.md       guide-customer.md   (customer research guide)
│   └── guide-regulator-dialogue.md   (contingent brief — via Compliance only, per H13)
├── 03-data/
│   ├── data-inventory-tracker.md ← all 22 §7 categories (M/U/OPT), status cells TODO, E5 gate rules
│   └── data-request-pack.md      ← formal Data Office request; every item cites its hypothesis;
│                                    OPT1/OPT4 excluded (minimization); OPT5 legal-gated placeholder
├── 04-deliverables/              ← skeleton templates D1–D11, sign-off blocks per source §9
│   ├── d01-problem-definition-diagnosis.md        d02-current-state-decision-flow-map.md
│   ├── d03-stakeholder-analysis-engagement-log.md d04-assumption-hypothesis-validation-report.md
│   ├── d05-opportunity-assessment-prioritization.md d06-risk-register.md
│   ├── d07-regulatory-legal-position-paper.md     d08-data-inventory-access-disposition.md
│   ├── d09-success-metrics-baseline-book.md       d10-governance-accountability-proposal.md
│   └── d11-mid-phase-charter-draft.md
├── 05-risk-and-compliance/
│   ├── risk-register.md          ← all 26 §6 risks with IDs, owners, mitigations, trigger indicators
│   └── regulatory-workplan.md    ← D7 production: H13 opinion, jurisdiction scan, H14 protocol
│                                    (process level), legal-basis mapping
└── 06-gates/
    ├── exit-criteria-checklist.md          ← E1–E10 gates (verbatim tests/consequences) + minuted
    │                                          E10 Go/No-Go decision template
    └── steering-committee-pack-outline.md  ← week-10 pack; proceed/pivot/stop argued equally
```

## Execution plan at a glance (detail: `00-program/workplan.md`)

- **Weeks 1–2 (WS1 Mobilize & map):** charter signed, Appendix B questions issued, data request pack sent, interviews begin, D2 walkthrough, ground-truth workshop #1, H13 legal ToR.
- **Weeks 2–4 (WS2 Legal & governance, parallel):** jurisdiction scan, legal-basis mapping, governance pre-alignment, mock-review setup.
- **Weeks 3–6 (WS3 Evidence):** H1–H8 backtests/cohorts, H9–H11 customer analyses. **E2 (ground truth signed) targeted week 4 — critical path.**
- **Weeks 5–7 (WS4 Sizing & synthesis):** P1/P2/P3 quantification (D1), risk-adjusted O1–O8 sizing (D5), H14 fairness audit after week-5 legal gate.
- **Weeks 7–8 (WS5 Alignment):** D9 KPI negotiation (E7), D10 governance acceptance (E8), D6/D7/D8 closure.
- **Weeks 8–10 (WS6 Close):** steering pack, D11 draft, **E10 minuted Go/No-Go (proceed / pivot / stop)**.
- **Critical path:** data request (wk1) → M-data delivery (wk3) → E2 (wk4) → H1–H4 (wk4–6) → D1 (wk7) → D5 (wk7–8) → E7 (wk8) → E10 (wk10). Single points of failure: Mandatory data delivery and ground-truth signature.

## Current status

All 50 planning artifacts are **built and internally consistent**; all bank-dependent content is explicitly marked **TODO** (tracker statuses, risk L/I scores, names in sign-off blocks, OQ answers). Nothing here presumes bank data or decisions. Next actions when the engagement starts: charter signatures (OQ-23), issue `03-data/data-request-pack.md`, assign Appendix B questions per `00-program/open-questions.md`.

### Bootcamp adaptation layer (added on top of the original package)
The engagement is confirmed to be an **AI & Technology bootcamp capstone**, not a real bank client. A delta layer re-interprets the package for that reality **without editing the source of truth**:
- **`bootcamp-adaptation-review.md`** — KEEP / ADAPT / LIFT / RISK review. Lifts the "no solution/model/architecture" constraint (now in scope and high-scoring), swaps real bank data→synthetic simulation, real stakeholders→personas, legal opinion→regulatory-awareness note, and maps the 10-week plan to bootcamp sprints. **The hard boundary (never override the bank's segment) is preserved and hardened into architecture.**
- **`07-bootcamp-workstreams/`** — `workstreams.md` (dependency graph, sprint sequencing S0–S4, cross-cutting rituals, jury-scoring alignment) + `ws1.md`–`ws5.md` (BWS1 Business, BWS2 Data/Simulation, BWS3 AI Core & Agentic ★, BWS4 Product/UX, BWS5 Engineering/Integration). Build lands under `./product/`.
- **`TRACEABILITY.md` §8** — source ID → bootcamp workstream (BWS1–BWS5) map + bootcamp orphan/deferral log.
- **`ROADMAP.md`** — the single master delivery plan the team works from: all 83 ws tasks consolidated (84 rows after 1 documented split) with Fibonacci story points, sprint S0–S4 placement, dependencies, critical path, and 6 milestones. **Operational source for task status**; ws files stay the definition source.
- New open questions **OQ-27…OQ-32** (bootcamp duration, team, tech rules, jury rubric, demo format, team velocity) — logged, not guessed.

## Self-review record (run at build time)

**(a) Coverage** — automated ID scan across all 48 package files (excluding source): every one of **P1–P3, A1–A10, H1–H14, O1–O8, D1–D11, E1–E10, M1–M9, U1–U8, OPT1–OPT5, and all 26 risk IDs** appears in ≥1 artifact — **0 missing**. All 26 OQ references map to defined log entries. §8.1 KPIs appear in charter §7 / D9 §4; all eight §8.2 KPIs templated with baseline requirements in D9 §2; §1.2 root causes → D1 §6 + guides; §2.1 steps → D2 §2; §2.3 pain points → guides/D2 §7.
**(b) Scope discipline** — keyword scan for solution/model/architecture design language: all hits are verbatim source quotes or explicit "no design" disclaimers. H5/H8 protocols carry the source's own scope guards ("signal existence only — no model building"; cadence replay of the bank's existing model).
**(c) Cross-references** — automated checks: no out-of-range IDs (no A11+, H15+, O9+, D12+, E11+, M10+, U9+, OPT6+, R-\*-06+/R-REG-07+); no broken `.md` file references.
**Items that could not be traced to a downstream analytical artifact (by design, logged as defects and resolved):** OPT1 and OPT4 carry no Phase-1 hypothesis in the source — per the source's own §7 minimization rule they are dispositioned **DO-NOT-COLLECT** (tracker) and routed to OQ-22; U7's opportunity-not-hypothesis purpose is flagged as OQ-21. Full log: `TRACEABILITY.md` §7.

**Bootcamp roadmap self-review (run at ROADMAP.md build time):**
- **Task count reconciliation** — ws files 83 tasks → `ROADMAP.md` 84 rows; delta = +1, the single documented split `BWS3-T13`→`T13a`/`T13b` (§7.3). Every original T-number appears exactly once (or as its two halves); none dropped or duplicated. Detail: `TRACEABILITY.md` §8.2.
- **Story points** — BWS1 68 · BWS2 87 · BWS3 102 · BWS4 89 · BWS5 88 = **434 SP**. Mapping S→2/M→5/L→8; one adjustment (BWS1-T15 S→1, admin); one split (BWS3-T13, >8).
- **Critical-path integrity** — all 15 🔴 tasks have every dependency scheduled in an earlier or same sprint (verified in `ROADMAP.md` §5.1). Two SPOFs: ground-truth definition (BWS1-T4) and seam+guard contract (BWS5-T3/BWS3-T3).
- **Sprint load** — avg 86.8 SP; S1 (128) and S2 (125) flagged REBALANCE-CANDIDATE (>40% over), with suggest-only moves; not silently rebalanced (`ROADMAP.md` §4.2).
- **[INFERRED] placements** — 9, all listed with reasoning in `ROADMAP.md` §7.4.
- **Undecidable → OQ** — team velocity vs. sprint load logged as **OQ-32** (not guessed).

## Rules for future sessions editing this package

1. Read the source document before changing anything; never contradict it or rename its IDs.
2. New scope, new data categories, or new risks require an open-questions entry and the declared ID conventions.
3. Keep "no-go is a valid outcome" language intact in charter, D5, D11, E10 checklist, and steering pack.
4. After any edit, re-run the traceability checks (ID coverage, no invalid IDs, no broken refs) and update `TRACEABILITY.md` and this status section.
