# Interview Guide — Model Risk / Validation
**Stakeholder profile (source §3):** distinct from Credit Risk ("often merged with Risk but distinct — added deliberately"). Goals — every model in production validated, monitored, documented. Concerns — an unvalidated AI layer influencing credit outcomes; scope creep from "advisory" to "decisioning." Their success metric — the layer classified, documented, and validated per model risk policy before go-live.
**Session:** 90 min (week 3); participants: head of model risk/validation + model inventory owner.

## Objectives
1. Learn precisely what triggers "model" treatment under the bank's model risk policy (A6 internal test; H12).
2. Find precedents: how are existing non-scoring overlays classified?
3. Agree the mock governance review format (H12 protocol step 2).
4. Capture their conditions for accepting D10 in principle (E8 — a hard gate).

## Questions (10)
1. How does your model risk policy define a "model" — and where have borderline cases landed? *(A6; the internal classification test)*
2. How are today's adjacent overlays classified — pricing engines, campaign eligibility tools, pre-approval logic? *(precedent; H12/H13 triangulation)*
3. If a layer only differentiated offers **within approved policy ranges** and never touched scores, segments, or engine inputs — where does it sit under your policy? *(the concept's §4 boundary statement, tested directly)*
4. Is there any construction under which an offer-influencing layer stays outside full credit-model treatment — or is influence itself the trigger? *(H12 falsification probe, verbatim-adjacent)*
5. What documentation, monitoring, and revalidation cadence would an "advisory" classification still require? *(D10 requirements; O8's trust-building path)*
6. What controls would you require against advisory-to-decisioning drift — the "silent scope creep" problem? *(R-AI-05; §6.2; D10)*
7. What audit-trail and decision-lineage standard would you expect for every offer adjustment? *(D10; Internal Audit alignment; §3 their success metric)*
8. What would you need to see in our H1–H4 backtest protocols to consider the diagnosis methodologically sound? *(D4 defensibility; they are C on method per RACI)*
9. Who should own the layer's recommendations when losses occur — and would you accept that proposal in principle this phase? *(OQ-09; E8's actual test)*
10. Would you participate in a mock governance review of the concept in weeks 4–6, using your real review format? *(H12 protocol commitment)*

## Evidence to collect
- Model risk policy (model definition criteria, tiering); model inventory classification criteria and precedent decisions.
- Validation/monitoring requirements per tier (what "advisory" would still owe).
- Their verbatim conditions for E8 acceptance — these become D10 sections.

## Tensions to probe
- **"Advisory" skepticism:** they have seen advisory drift before; do they treat the word as camouflage? Their concern is legitimate — capture what *structural* boundary (not promise) would satisfy them.
- **Risk-vs-Business shared metric (secondary seat):** would they accept monitoring the tolerance band (D9) as the layer's risk-stability control, or demand a separate regime?
- **Exploration vs. production:** Phase 1 analyses are discovery, not production models — confirm they agree H1–H8 analysis does not itself enter the model inventory (Data Science's §3 concern: "governance treating exploration as production").

## Feed into D3 (and beyond)
- Position summary; tension log (classification stance, drift concerns); commitment log (mock review date).
- Direct feeds: H12 protocol, D10 requirement list, E8 acceptance conditions, D4 method review expectations.
