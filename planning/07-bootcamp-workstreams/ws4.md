# BWS4 — Product, UX & Explainability
### The demoable surface + the story the jury sees

**One-line mission:** turn the intelligence into a product a jury can watch work — offer screens, a staff-facing evidence pack, customer-facing explanations and improvement paths, the graduated-offer concept, and the end-to-end demo script.

**Boundary reminder:** the UI makes the boundary *visible* — the segment is rendered **fixed / read-only** (it comes from the bank engine and is never changed); only the within-policy offer is shown as optimized, and every adjustment shows its audit entry (source §4; review K5, L5).

---

## Objective
Deliver the product surface and the demo experience that convert BWS3's structured outputs and BWS2's data into a clear, honest, and compelling story: the customer/portfolio flows through the simulated engine, the bridge layer optimizes the offer within policy, staff and customers see explanations, and the audit + fairness views update live. Own the demo script end to end.

## In scope
- **Offer screen(s):** show the engine's segment (read-only) + the optimized within-policy offer + the policy band it sits inside (O1).
- **Staff-facing evidence pack (O2):** the boundary-case flag + supporting evidence a human reviewer would use; "route to review" action (human stays the decision-maker).
- **Customer-facing explanation + improvement path (O4, H9/H10):** why this offer, and the concrete path to a better one — the satisfaction lever the source identifies even when the offer is "correct."
- **Graduated / staged offer UI (O6):** "limit increases to X after 6 months of behavior Y" presented as a path, not a wall.
- **Fairness & audit views:** surface the fairness-audit result and the audit trail entry for an adjustment (trust/transparency).
- **Persona-driven flows:** the Risk persona and Business persona both viewing the same **shared risk-adjusted metric** (source §3 tension → one screen).
- **End-to-end demo script** + recorded backup, including the **honest-limits slide** (with BWS1).

## Out of scope
- The intelligence/agents (→ BWS3 — BWS4 renders their structured outputs).
- Data generation (→ BWS2), infra/deploy/audit store (→ BWS5).
- Inventing offer numbers — all values come from BWS3/BWS2; UI never computes an out-of-policy offer.

## Inputs from the planning package
- **Opportunities:** O1 (within-segment differentiation), O2 (boundary flagging / evidence pack), O4 (explanation & transparency), O6 (graduated offers).
- **Hypotheses:** H9 (explanation drives satisfaction), H10 (explainability → acceptance/trust).
- **Assumptions:** A3 (dissatisfaction driven by explanation/path, not just amount), A9 (stakeholder trust).
- **Deliverables:** D9 (trust/explainability baselines), supports D1/D5 narrative, D3 personas.
- **Exit criteria:** E7 (shared metric on screen), supports E3/E9 presentation.
- **Stakeholders:** Customer, Front line, Risk, Business personas (source §3).
- **Deltas:** L5 (working product), A2 (personas → screens), K10 (tension → shared screen), R1/R3/R5 (honest framing, deferred features labelled).

## Dependencies on other workstreams
- **Consumes from BWS1:** personas, demo story, shared-metric spec, honest-limits content, policy-range display rules.
- **Consumes from BWS2:** display-ready records + curated demo cases.
- **Consumes from BWS3:** structured optimized offers, explanations, evidence packs, fairness results.
- **Consumes from BWS5:** the API to call, hosting, and the audit entries to display.
- **Provides to all:** the demo script and the integration "happy path" everyone rehearses against.

## Task breakdown

| # | Task | Size | Traces to | Feeds |
|---|---|---|---|---|
| T1 | UX flows + wireframes for the four surfaces (offer, evidence pack, customer explanation, graduated offer) | M | O1/O2/O4/O6, personas | all BWS4 build |
| T2 | Demo story arc with BWS1 (problem → boundary → optimize → explain → audit/fairness → limits) | M | review R1/R5, D1 | script, deck |
| T3 | App skeleton + routing + design system (theme, accessible components) | M | L5 | all screens |
| T4 | **Offer screen:** segment **read-only** + optimized within-policy offer + visible policy band | L | O1, §4 boundary, K5 | demo |
| T5 | **Staff evidence pack (O2):** boundary flag + supporting signals + "route to human review" action | L | O2, H1/H4 | demo |
| T6 | **Customer explanation + improvement path (O4):** plain-language why + path to better offer | L | O4, H9/H10, A3 | demo, D9 |
| T7 | **Graduated/staged offer UI (O6):** conditional path presentation | M | O6, H7 | demo |
| T8 | **Fairness view:** render disparity metric + the corrected result (H14) | M | H14, E9 | demo |
| T9 | **Audit view:** show the lineage of one adjustment (segment unchanged, base→optimized, policy checked, agent) | M | D10, K5 | demo, boundary review |
| T10 | **Shared risk-adjusted metric screen** (Risk + Business personas see the same number) | M | §3 tension, E7, O5 | demo, deck |
| T11 | Wire screens to BWS5 API + BWS3 structured outputs (real data path) | L | integration | G2/G3 |
| T12 | Empty/error/latency states + LLM-timeout fallback UX (base offer unchanged, labelled) | S | R6 | robustness |
| T13 | Accessibility + explainability polish (readable, no jargon, protected-attribute-safe copy) | M | H10, §6.3, review R4 | demo |
| T14 | Curate the demo dataset walkthrough (thin-file, boundary, seeded-disparity "wow" cases) with BWS2 | S | review R4/R5 | demo |
| T15 | **End-to-end demo script** (timed, live) + presenter notes incl. honest-limits slide | L | review R1–R6 | demo day |
| T16 | **Record backup demo video**; rehearse; contingency for live failure | M | program DoD | demo day |

## Definition of done
- All four product surfaces render **from real BWS3 outputs over the BWS5 API** (not mocks) by G3.
- The segment is visibly **read-only** everywhere; no UI path can present an out-of-policy offer; each adjustment links to its audit entry.
- Customer explanation includes a concrete improvement path (O4); graduated-offer path renders (O6) or is labelled "designed, not built" if descoped (review R5).
- Shared risk-adjusted metric screen exists; fairness + audit views render live.
- Timed live demo script rehearsed; recorded backup exists; honest-limits slide integrated.

## Demo-day contribution
- **This workstream IS most of the visible demo.** It drives the on-screen narrative and owns timing/flow.
- The **"segment is read-only, offer is optimized within the band"** visual — the boundary made obvious.
- The **customer explanation + improvement path** — the empathy/trust beat that lands the responsible-AI story.

## Suggested owner skill profile
Product/frontend engineer with UX sensibility; can build a clean, accessible web UI quickly and has taste for information design and plain-language explanation. Comfortable presenting. Pairs tightly with BWS1 (story) and BWS3 (data contracts). If a pair: one frontend builder + one UX/presentation lead.
