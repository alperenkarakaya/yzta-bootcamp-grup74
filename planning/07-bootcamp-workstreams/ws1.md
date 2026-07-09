# BWS1 — Business & Domain
### Problem, Banking Logic, Compliance Narrative

**One-line mission:** own the *meaning* of the project — the problem framing (P1/P2/P3), the credit-domain rules the product must respect, the regulatory-awareness narrative, the success metrics, and the jury-facing business case.

**Boundary reminder:** BWS1 defines the **policy ranges** every other workstream treats as hard limits, and narrates why the layer *never* overrides the bank's segment (source §4). This stream is the guardian of the "innovation = integrity" story (review K5, L3).

---

## Objective
Produce the authoritative statement of *what problem we solve, for whom, within what rules, and how we measure it* — so BWS2 can encode it, BWS3 can enforce it, and BWS4 can tell it. Turn the source's discovery-only framing into a demo-ready business case grounded in the synthetic world, honest about its limits.

## In scope
- Problem definition and the **P1/P2/P3 decomposition** (misclassification / coarse segmentation / conservative offer mapping) and the "diagnose the mix" narrative (source §1.1; review K1/K2).
- **Policy ranges per segment** (approved limit/pricing bands) that define what "within policy" means — the constraint BWS3's guard enforces (source §4, A5).
- **Ground-truth definition** ("deserved segment / right-sized offer") in collaboration with BWS2 (source A2, E2; review K11).
- **Regulatory-awareness write-up** (D7 as a note, not legal advice): fair lending, explainability, data protection/purpose limitation, responsible lending, **EU AI Act high-risk** framing (source §6.3; review A3).
- **Success metrics & baseline book** (source §8; review K9): the O5 under-lending metric, risk-adjusted (not gross) sizing method, fairness indicators.
- **Personas** derived from the §3 stakeholder map + assumption register (review A2).
- **Jury business case & narrative**, including the honest-limits framing (review R1–R6).

## Out of scope
- Generating the data (→ BWS2), building agents (→ BWS3), building UI (→ BWS4), infra (→ BWS5).
- Any real legal opinion or real financial forecast — write-ups are labelled awareness/illustrative (review A3, A6, R1, R2).
- Changing the hard boundary — BWS1 documents it, never relaxes it.

## Inputs from the planning package
- **Problem:** P1, P2, P3 (§1.1); root causes (§1.2); impacted parties (§1.3).
- **Assumptions:** A1–A10 (framing owner), esp. A2 (ground truth), A4/A5/A10 (value/appetite/win-win), A6 (regulatory classification).
- **Opportunities:** O5 (under-lending metric — headline), O6/O7 (graduated offers, counter-conservatism — narrative).
- **Deliverables:** D1 (problem diagnosis), D3 (personas/assumptions), D5 (sizing), D6 (risk register), D7 (regulatory-awareness note), D9 (metrics/baselines).
- **Exit criteria:** E1 (materiality), E2 (ground truth), E3 (value case), E4 (regulatory viability → awareness), E7 (shared metric), E9 (fairness position).
- **KPIs:** §8.1 (phase evidence) reframed to demo evidence; §8.2 (product KPIs) with synthetic baselines.
- **Deltas:** K1/K2/K9/K10/K11; A2/A3/A6/A7; R1/R2/R3.

## Dependencies on other workstreams
- **Provides to all:** policy ranges, ground-truth definition, success-metric definitions, personas, the boundary narrative.
- **Provides to BWS2:** ground-truth convention + the intended P1/P2/P3 mix to seed.
- **Provides to BWS4:** personas, demo story, honest-limits slide content.
- **Consumes from BWS2:** the synthetic portfolio to compute sizing/metrics.
- **Consumes from BWS3:** fairness-audit output for the fairness position (E9).

## Task breakdown

| # | Task | Size | Traces to | Feeds |
|---|---|---|---|---|
| T1 | Write the problem one-pager: P1/P2/P3 decomposition + "diagnose the mix" thesis | M | §1.1, K1/K2, D1 | BWS2, BWS4, deck |
| T2 | Root-cause & impacted-party summary (thin-file, stale-score, boundary, override, conservatism) | S | §1.2, §1.3 | BWS2 (cohorts to seed) |
| T3 | Define **policy ranges per segment** (approved limit/pricing bands) as machine-readable config | M | §4, A5, boundary | BWS3 (guard), BWS5 (config) |
| T4 | Co-author **ground-truth definition** ("deserved segment"), with limits documented | M | A2, E2, §6.2, K11 | BWS2 (labels), G0 gate |
| T5 | Success-metrics & baseline book: define O5 under-lending metric + risk-adjusted sizing formula | M | §8, O5, D9, K9 | BWS2, BWS5 (instrumentation) |
| T6 | Illustrative opportunity sizing (O1–O8 ranked; O5 headline) on synthetic data | M | §4, D5, A4/A10, A6-delta | BWS4, deck |
| T7 | Persona catalogue from §3 (Customer, Risk, Model Risk, Business, Compliance, DS, Product, Exec, Front line, Audit, Regulator) + assumption register | M | §3, D3, A9, review A2 | BWS4 (UX), boundary review |
| T8 | Regulatory-awareness write-up (fair lending, explainability, data protection, responsible lending, EU AI Act high-risk) — labelled not-legal-advice | L | §6.3, D7, A6, H13, review A3 | BWS3 (RAG corpus), deck |
| T9 | Map each regulatory obligation → an architectural control (explainability, guard, audit, fairness) | M | §6, D7, D10, review A3/R2 | BWS3, BWS5 |
| T10 | Refresh the risk register for build reality (mark sim-only vs real-world risks; keep vendor/data risks noted) | S | §6, D6, review A5 | boundary review, deck |
| T11 | Fairness position note (H14 as remediation-not-decoration; consume BWS3 audit output) | M | H14, E9, D7, review R4 | BWS3, deck |
| T12 | Shared Risk–Business metric one-pager (the §3 tension → one risk-adjusted screen) | S | §3 tension, E7, D9, K10 | BWS4 (screen), deck |
| T13 | Business case + jury narrative arc (problem → boundary → mechanism → proof → limits) | L | all above, review R1–R6 | BWS4 deck/script |
| T14 | Honest-limits register: "what our evidence does and does not support" (synthetic vs real) | M | review R1/R2/R3/R4/R6 | BWS4 (honesty slide) |
| T15 | Answer/track OQ-27…OQ-31 impact on business framing; keep deck assumptions labelled | S | OQ-27…31 | deck |

Sizes: S≈½ sprint-person, M≈1, L≈1.5–2.

## Definition of done
- Problem one-pager, policy-ranges config, and ground-truth definition are **frozen by G0** and consumed unchanged by BWS2/BWS3.
- Regulatory-awareness note + obligation→control map complete, clearly labelled as awareness not counsel.
- Success-metrics book defines O5 + risk-adjusted sizing with formulas; baselines computable from BWS2 data.
- Persona catalogue + assumption register complete; the Risk-vs-Business shared metric is expressed as one screen spec for BWS4.
- Honest-limits register complete; every jury claim is traceable to synthetic evidence or explicitly caveated.
- Zero statements that relax the hard boundary.

## Demo-day contribution
- The **opening narrative**: "here are three different causes of low offers (P1/P2/P3); here's the boundary that keeps us safe; here's the metric no bank has (O5)."
- The **honest-limits slide** that pre-empts "does this work in the real world?" (review R1).
- The **regulatory-awareness talk track** that turns the EU AI Act high-risk framing into a strength (our architecture answers it by construction).

## Suggested owner skill profile
Domain/product-minded generalist with strong writing and structured-thinking skills; comfortable with credit-risk concepts (PD, segments, risk-adjusted return) and regulatory literacy (fair lending, EU AI Act). The "storyteller-analyst." Pairs well with the BWS4 owner for the deck.
