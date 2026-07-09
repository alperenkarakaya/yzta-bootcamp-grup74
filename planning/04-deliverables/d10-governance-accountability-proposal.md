# D10 — Governance & Accountability Proposal (template)
**Source §9:** "who owns the layer's recommendations, escalation paths, audit-trail requirements" · **Owner:** Product + Risk · **Sign-off:** Model Risk + Audit · **Feeds gates:** E8 (primary — "this is a hard gate")

> Guidance: a governance *proposal* accepted in principle — not an implemented control framework and not a system design. Requirements are stated at process level; their implementation belongs to later phases.

## 1. Purpose and the accountability question
> Guidance: open with the question the proposal answers — OQ-09 / Appendix B-9: "Who would be accountable if an 'optimized' offer defaults?" §6.4 names the risk this kills: "Ownership vacuum — no one owns the layer's decisions when losses occur." The E8 test: Model Risk and Audit accept this proposal in principle.

## 2. Bright-line boundaries of the layer's authority
> Guidance: quote the §4 list verbatim — the layer shall never: "re-scoring customers, overriding segments automatically, adjusting the engine's inputs, or auto-approving above-policy limits." Add the positive statement: the engine's segment remains the anchor; the layer optimizes only within approved policy ranges. Per §6.2, these bright lines are the charter-level defense against silent scope creep (R-AI-05) — include the drift-control expectations captured from Model Risk (guide Q6) and Audit (guide Q5).

## 3. Accountability model
> Guidance: who owns the layer's recommendations (role, not name), who owns outcomes of accepted recommendations, how human decision authority is preserved where it exists today (O2's "human remains decision-maker"), and how accountability transfers at each step. Built from OQ-09 answers, H12 mock-review conditions, and the D3 RACI proposal.

## 4. Escalation paths
> Guidance: recommendation-level escalation (boundary cases → existing review authority), portfolio-level escalation (tolerance-band breach per D9 → whom, then what), and governance escalation (classification drift → Model Risk). Process descriptions only.

## 5. Audit-trail requirements
> Guidance: what a complete trail of every offer adjustment must contain — captured as *requirements* from Internal Audit's own standard (their guide Q3): inputs seen, recommendation made, bounds checked, human action taken, outcome linked. Internal Audit's §3 success metric verbatim: "Complete audit trail of every offer adjustment." No logging-system design.

## 6. Classification and review expectations
> Guidance: the layer's expected classification under model-risk policy (from H12 mock review + H13 opinion), documentation/monitoring/revalidation expectations under that classification, and the triggers that would force re-classification (the H12 conditions register).

## 7. Explainability commitment
> Guidance: per §6.2 opacity mitigation, explainability is "a non-negotiable requirement in the Phase 1 requirements document" — state it here as a standing requirement (staff-facing and customer-facing rationale must exist for any adjustment), evidenced by H10 findings. Requirement only; no explanation-generation design.

## 8. Acceptance record
> Guidance: the in-principle acceptance statements from Model Risk and Internal Audit, verbatim, with their stated conditions and what "in principle" excludes (per the Internal Audit guide tension: acceptance of the proposal's shape, not a completed audit).

## Sign-off block
| Role | Name | Date | Signature |
|---|---|---|---|
| Owner — Product | TODO | | |
| Owner — Risk | TODO | | |
| Sign-off — Model Risk | TODO | | |
| Sign-off — Internal Audit | TODO | | |
