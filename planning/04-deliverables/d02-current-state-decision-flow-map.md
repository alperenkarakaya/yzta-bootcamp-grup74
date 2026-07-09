# D2 — Current-State Decision Flow Map (template)
**Source §9:** "end-to-end flow, systems, owners, discretion points, candidate insertion points, downstream dependencies" · **Owner:** Product + Bank SMEs · **Sign-off:** Risk + IT · **Feeds gates:** E6 (primary), supports A8

> Guidance: documentation of what exists — not design of what could be. "Candidate insertion points" are locations and authorities observed in the current flow, described as facts (where an offer is still changeable, by whom, under what constraint). No target architecture, no integration design.

## 1. Scope and method
> Guidance: walkthrough sessions held (dates, participants), systems observed, documents reviewed. Products covered (OQ-18).

## 2. End-to-end decision flow (§2.1 steps 1–9)
> Guidance: one subsection per source-defined step: 1 Application/trigger · 2 Data assembly · 3 Scoring · 4 Segmentation · 5 Policy rules · 6 Offer assignment · 7 Manual review/overrides · 8 Offer delivery · 9 Feedback loop. For each, answer the source's discovery questions verbatim: Who owns it? What system executes it? How often does it change? Where is discretion applied? Where could a bridge layer legally and technically insert?
> Required evidence per step: system names/versions, owner roles, change cadence, discretion points with authority levels; step 9 must state whether outcomes feed back at all, and with what lag.

## 3. Classification process facts (§2.2)
> Required evidence: number of segments and boundary rationale; population distribution and boundary density; refresh cadence; historical migration stability and direction; override rates and direction; whether "deserved segment" was ever retro-analyzed (OQ-01 answer).

## 4. Candidate insertion points (E6 evidence)
> Guidance: for each candidate: location in the flow, what is still changeable there (offer parameters within policy), whose authority already exists there (O2's "authority that already exists"), technical accessibility as observed, and vendor-contract compatibility (Q7/OQ-24 findings). E6 test: "≥ 1 viable, vendor-compliant point where offers can be influenced pre-delivery." If none exists, say so plainly — E6's consequence is "Concept reworked or stopped."

## 5. Downstream dependencies (§2.4, R-BUS-04)
> Required evidence: where segment/offer values are consumed downstream — pricing engines, collections strategies, capital models — and what would ripple if effective offers changed. Source warning: cut-offs "may be embedded in downstream systems."

## 6. Vendor and contract constraints
> Required evidence: engine vendor contract clauses on intercepting/augmenting outputs (OQ-07, R-OPS-04); bureau license scope notes relevant to flow (OQ-24). Reviewed with Legal/Procurement.

## 7. Pain points observed in the flow
> Guidance: evidence collected against the §2.3 hypothesized pain points (boundary treatment, no lift mechanism, no under-lending metric, unexplainable complaints, Risk blamed, slow policy cycle) — confirmed/not, with artifacts.

## 8. Structural limitations register
> Guidance: restate §2.4 items as verified facts or corrections: regulated scoring model untouchable; embedded cut-offs; counterfactual data absence; vendor restrictions.

## 9. Annexes
> Flow diagrams (descriptive, as-is only), session notes register, document inventory.

## Sign-off block
| Role | Name | Date | Signature |
|---|---|---|---|
| Owner — Product | TODO | | |
| Owner — Bank SMEs (lead SME) | TODO | | |
| Sign-off — Risk | TODO | | |
| Sign-off — IT | TODO | | |
