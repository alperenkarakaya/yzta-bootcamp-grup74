# Interview Guide — Product Team
**Stakeholder profile (source §3):** goals — a shippable product with clear value narrative; scalability beyond one bank. Concerns — over-customization to one bank's quirks; unclear ownership between product and risk logic. Their success metrics — defined MVP scope; documented requirements; stakeholder sign-off.
**Note:** the "scalability beyond one bank" goal suggests this is the vendor/product organization rather than a bank team — confirm (OQ-16). If vendor-side, this session is an internal alignment interview and is logged as such in D3.
**Session:** 60 min (week 3).

## Objectives
1. Align on scope discipline: MVP candidates come from the D5 ranking, "not from what is technically most interesting" (§4, verbatim task).
2. Clarify ownership boundaries between product logic and risk logic (their §3 concern; feeds D10).
3. Set expectations for D11: boundaries ("the layer shall never…") are product commitments, not marketing caveats.

## Questions (9)
1. Which of O1–O8 do you *assume* is the product — and are you prepared for the evidence to rank a different one first? *(sunk-cost inoculation, R-BUS-05; §4 ranking rule)*
2. If the diagnosis shows P3 (offer policy) dominates over P1 (misclassification), what does the product become — and is that still a product you'd build? *(§1.1 framing challenge; pivot readiness)*
3. Where does product logic end and risk logic begin in your view — who owns an offer recommendation? *(their §3 ownership concern; OQ-09; D10)*
4. Which §4 boundary ("never re-score, never auto-override segments, never adjust engine inputs, never auto-approve above policy") would the product roadmap be most tempted to cross later — and how do we make that structurally hard? *(R-AI-05 silent scope creep; D10/D11 bright lines)*
5. What would over-customization to this bank look like, concretely — and which Phase 1 findings would you treat as bank-specific vs. general? *(their §3 concern; shapes how D5 findings are written)*
6. What does the value narrative need from Phase 1 evidence to be credible to a second bank — and does that change what we must measure now (D9 baselines)? *(scalability without scope invention)*
7. What requirements-gathering do you need from stakeholder interviews that we should collect on your behalf? *(efficiency; D3 completeness — noting requirements documentation belongs to Phase 1 outputs, design does not)*
8. If the steering committee says pivot-to-O5 (measurement only) or stop, what does the product organization do with the Phase 1 assets? *(no-go realism; steering pack "preserved value" section)*
9. Who from Product signs which artifacts — D1, D3, D5, D10, D11 all carry Product ownership? *(RACI confirmation; capacity check)*

## Evidence to collect
- Product strategy notes on the bridge-layer concept (to check for pre-committed design that would bias discovery — flag any found).
- Prior MVP definitions/processes (how scope discipline is normally enforced).
- Their draft value narrative — logged as a *hypothesis-shaped claim list* to be tested, not adopted.

## Tensions to probe
- **Evidence-led vs. roadmap-led:** will Product accept the D5 ranking even if it demotes the "interesting" opportunity? Get it on record.
- **Ownership vacuum (R-OPS-02):** "unclear ownership between product and risk logic" is their own stated concern — push for a concrete proposal to take into D10.
- **Risk-vs-Business metric (their seat):** the product value narrative must be written in the shared risk-adjusted metric (D9), not gross uplift — confirm they'll market it that way.

## Feed into D3 (and beyond)
- Position summary; ownership-boundary proposals (→ D10); scope-discipline commitments on record (→ D5, D11).
- Flag to open-questions log: any pre-committed design found (defect vs. discovery discipline).
