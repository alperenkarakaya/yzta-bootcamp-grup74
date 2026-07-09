# Interview Guide — Compliance / Legal
**Stakeholder profile (source §3):** goals — fair lending, responsible lending, data protection, explainability obligations. Concerns — disparate impact from AI adjustments; data use beyond consented purpose; inability to explain adverse-relative outcomes; regulator perception. Their success metrics — zero regulatory findings; documented legal basis for every data element; explainability standard met.
**Session:** 2 × 60 min (week 3); participants: compliance lead for retail credit + data protection officer + (if separate) legal counsel owner for the H13 opinion.

## Objectives
1. Commission and scope the H13 classification opinion (ToR confirmation; jurisdiction set, OQ-17).
2. Map the legal-basis process for every §7 data category (D8 legal-basis column; A7).
3. Open the H14 fairness-audit gate: can protected attributes (OPT5) be accessed for testing, and under what protocol (E9)?
4. Establish explainability and responsible-lending constraints that bound all sizing (affordability as hard constraint).

## Questions (12)
1. Has Compliance ever assessed segment assignments for disparate impact? *(Appendix B-8, verbatim; H14 starting point)*
2. In our jurisdiction(s), what turns offer logic into regulated "credit decisioning"? Which of O1–O8 look classifiable as "offer optimization within approved policy"? *(H13; E4)*
3. Is there any applicable AI-specific regulation (e.g., EU AI Act treatment of creditworthiness AI as high-risk) — and does it apply regardless of our internal classification? *(§6.3, verbatim risk; OQ-17)*
4. What legal basis covers using transaction/behavioral data (collected for servicing) in offer-optimization **analysis** — and does the basis differ between Phase 1 diagnosis and any future operation? *(R-REG-03, R-DAT-03; U1 gate)*
5. What do our bureau contracts permit — is analysis for this purpose within license, and who can confirm? *(OQ-24; R-DAT-04; U6)*
6. Can protected attributes be accessed for fairness-testing purposes? Under what governed process, and who approves it? *(OPT5; H14; E9 — the "audit itself is legally blocked" branch must be established now, not discovered in week 6)*
7. Which disparity metrics would you accept for the fairness audit — and will you co-own the choice? *(§8.2: "Disparity metrics chosen with Compliance")*
8. What statutory or supervisory explanation rights do customers have over credit terms today? *(§6.3 explainability rights; O4 constraints; H10 concept review)*
9. What affordability/responsible-lending rules bound any upward offer movement? *(§6.1 overshoot mitigation; §6.3; hard constraint in H6/D5 sizing)*
10. What complaint categories in our M8 data carry regulatory reporting duties — anything we must handle specially in the taxonomy work? *(H9 protocol safety)*
11. Would informal regulator dialogue on the layer's classification be wise in this jurisdiction — and would you lead it? *(H13 optional step, "(if available)" per source; guide-regulator-dialogue.md)*
12. What would make you veto this concept outright? *(surface the red lines now)*

## Evidence to collect
- Prior opinions/precedents on decisioning-adjacent tools; DPIA/records-of-processing templates and thresholds.
- Bureau contract clauses (with Procurement); consent language inventory for behavioral data.
- Regulatory correspondence norms (does the bank pre-clear novel credit processes?).
- Named approver + process for OPT5 access (or the written reason it's impossible).

## Tensions to probe
- **Fairness audit as risk vs. remediation:** the H14 design intent — under-classification correlating with protected groups would make correction a *fairness improvement*. Do they see the audit as exposure or as opportunity? Their stance shapes E9's path.
- **Purpose-limitation strictness vs. evidence needs:** if U1 analysis is blocked, H5 (and O1/O8 value) degrade — do they offer a lawful route (aggregation, pseudonymization at source) rather than a flat no?
- **Risk-vs-Business metric (their seat):** compliance indicators (fairness, explainability) must sit inside D9 — will they contribute baselines rather than veto at the end?

## Feed into D3 (and beyond)
- Position summary; red-line register; commitments (opinion ToR, OPT5 decision date — workplan wk5).
- Direct feeds: D7 (whole), D8 legal-basis column, H14 protocol, H9/H10 protocol safety, `../05-risk-and-compliance/regulatory-workplan.md` execution.
