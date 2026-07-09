# Regulatory Workplan — Producing D7
**Objective:** deliver D7 (Regulatory & Legal Position Paper, CCO sign-off) so that E4 (regulatory path viable) and E9 (fairness position established) can be judged at week 8. Everything here is process-level: opinions, scans, protocols, and mappings — no control design, no system design.
**Owner:** Compliance/Legal · **Coordination:** Engagement Lead · **Template:** `../04-deliverables/d07-regulatory-legal-position-paper.md`

## Workstream 1 — Layer classification opinion (H13 → E4)

| Step | Week | Activity | Output |
|---|---|---|---|
| 1.1 | 1 | Terms of reference agreed with CL: questions presented (classification per opportunity type O1–O8; conditions that hold/flip it), jurisdiction set (OQ-17), counsel (internal/external) and budget | Signed ToR |
| 1.2 | 2–3 | Factual basis fixed: the concept boundary statement (charter §2 "shall never" list, verbatim) + within-policy-range operation + M7 policy definitions; vendor-contract findings fed in as they land from D2 (OQ-07) | Agreed factual basis memo |
| 1.3 | 2–5 | Precedent review: internal classifications of adjacent overlays (from Model Risk interview); supervisory precedent where public | Precedent register |
| 1.4 | 5 (optional) | Informal regulator dialogue per `../02-stakeholders/guide-regulator-dialogue.md` — only if the CCO elects it ("(if available)" per source H13) | Minuted dialogue note |
| 1.5 | 6 | Draft opinion received; per-opportunity viability flags extracted and handed to D5 sizing (before week-7 ranking) | Draft opinion + viability table |
| 1.6 | 7–8 | Finalization; CCO signature within D7 | Signed opinion (E4 evidence) |

**Decision points:** a draft trending toward "the layer is a credit decision model" (H13 falsified) triggers the E4 consequence path immediately — "Restrict scope to compliant opportunities or stop" — with O5 (analytics only) and O4/O7 as the designed fallback scope (§6.3 mitigation names O1–O5 as the within-policy design set). This goes to the mid-point steering check (week 5) if visible by then, not held for week 10.

## Workstream 2 — Jurisdiction scan (→ D7 §4; R-REG-06 mitigation, "an explicit Early Phase deliverable" per §6.3)

| Step | Week | Activity |
|---|---|---|
| 2.1 | 1 | Jurisdiction set confirmed (OQ-17) |
| 2.2 | 2–4 | Scan per jurisdiction across the §6.3 risk set: consumer-credit rules on offer differentiation; model-governance expectations; data protection / purpose limitation; responsible lending & affordability duties (bounds all upward sizing — R-REG-04); explainability rights (R-REG-05); AI-specific regulation (R-REG-06 — e.g., EU AI Act high-risk treatment of creditworthiness AI, applicability concluded per jurisdiction, "regardless of internal classification") |
| 2.3 | 4 | Scan results workshop with working group: constraints handed to H6/D5 sizing (affordability), H10 (explanation concept constraints), D9 (fairness/explainability indicators) |
| 2.4 | 6–8 | Scan finalized into D7 §4 |

## Workstream 3 — Fairness audit protocol (H14 → E9), process level

1. **Legal gate (weeks 2–5):** Compliance determines whether protected attributes (OPT5) may be accessed for testing purposes — the source is explicit that this "requires its own legal review" (§7.3). Output by week 5: **approved governed protocol** or **formal block**.
2. **Governed protocol contents (if approved):** purpose limitation to the audit; access control and logging in an agreed environment; pseudonymization; results-only egress; disparity metrics **chosen with Compliance** (§8.2) and pre-registered; proxy-attribute set and its documented limits; privilege/handling instructions from counsel.
3. **Execution (week 6):** audit run by Data Science under the protocol, reusing the E2 ground truth and H1–H3 cohorts; direction test included (would correcting evidenced under-classification narrow or widen disparity — the §5 "compliance remediation" reframing if it narrows).
4. **Blocked path (equally valid per E9):** formal block documentation — reason, what was attempted, residual risk statement — and executive acceptance of the residual risk, recorded in D7 §5 and the E9 gate. Escalation if neither path completes: E9's consequence, "Compliance escalation."
5. **Interlock:** any H5 signal family showing separation is screened against H14 findings before appearing in D5 narratives (R-AI-03 trigger).

## Workstream 4 — Data legal-basis mapping (→ D7 §6, D8; A7/E5 support)

| Step | Week | Activity |
|---|---|---|
| 4.1 | 2 | Method agreed with DPO: basis assessment per tracker category; DPIA-threshold check for the diagnostic itself |
| 4.2 | 2–4 | Item-by-item basis mapping as Data Office responses land: purpose-limitation analysis for repurposed servicing data (U1 — R-REG-03/R-DAT-03); bureau license scope for U6 (OQ-24 — R-DAT-04) with Procurement; consent-gap register with remediation stance |
| 4.3 | 4–6 | Conditional items resolved or marked BLOCKED with workaround assessment (feeds E5) |
| 4.4 | 8 | Legal-basis register finalized — co-signed into D7 §6 and D8 §6 |

## RACI snapshot (this workplan only)

| Activity | R | A | C | I |
|---|---|---|---|---|
| Classification opinion | Compliance/Legal (+ external counsel) | CCO | Model Risk, Product, Risk | Sponsor, SteerCo |
| Jurisdiction scan | Compliance/Legal | CCO | Engagement Lead | Working group |
| Fairness audit protocol & execution | Compliance (protocol), Data Science (execution) | CCO (protocol); Executives (residual risk if blocked) | Risk | Sponsor, SteerCo |
| Legal-basis mapping | Compliance (DPO) + Data Office | CCO / CDO jointly | Data Science, Procurement | Working group |

## Risks carried by this workplan
R-REG-01 (reclassification — WS1's subject), R-REG-02 (fair lending — WS3), R-REG-03 (purpose limitation — WS4), R-REG-04 (responsible lending — WS2 duty scan), R-REG-05 (explainability rights — WS2), R-REG-06 (AI-specific regulation — WS2), R-DAT-03/R-DAT-04 (consent/bureau — WS4), R-AI-03 (bias amplification — WS3 is its mandatory mitigation). Trigger indicators per `risk-register.md`.
