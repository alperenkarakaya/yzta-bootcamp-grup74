# Interview Guide — Internal Audit
**Stakeholder profile (source §3, "added"):** goals — auditable, controlled processes. Concerns — untracked overrides; unclear decision lineage. Their success metric — complete audit trail of every offer adjustment.
**Why they matter here:** joint sign-off (with Model Risk) on D10 — the E8 hard gate.
**Session:** 60 min (week 3); participants: audit lead for credit processes + IT audit if separate.

## Objectives
1. Learn what "auditable" concretely means in this bank — the standard D10 must meet (E8).
2. Assess today's decision lineage: are current overrides and offer decisions traceable (M6 quality; H4 feasibility)?
3. Capture their in-principle acceptance criteria for a future layer's audit-trail requirements.
4. Mine past audit findings for evidence the Early Phase can reuse.

## Questions (10)
1. What have your audits found about the credit decision and override process — anything on traceability, authority, or reversals? *(prior findings = free evidence for D1/D2/H4)*
2. Are today's manual overrides fully tracked — actor, reason, authority, outcome? Where does lineage break? *(their §3 concern verbatim; M6 quality check for H4)*
3. If an offer were influenced by an additional layer, what would a complete audit trail contain, end to end? *(their §3 success metric, made concrete → D10 requirements)*
4. Who would be accountable if an "optimized" offer defaults — and what would you expect the accountability documentation to look like? *(Appendix B-9, verbatim; OQ-09; D10)*
5. What controls would you require to prevent an "advisory" layer drifting into de facto decisioning? *(R-AI-05; §6.2 silent scope creep; mirrors the Model Risk probe — compare answers)*
6. What would "accept in principle" mean from your side at this phase — and what formal audit steps follow in later phases? *(E8's exact wording: "accept the accountability proposal (D10) in principle")*
7. How should exception/escalation paths be evidenced (O2's human-review route) so that a future audit passes them? *(D10 escalation-path section)*
8. What retention and reproducibility standards apply to analyses that inform credit-relevant decisions — do our Phase 1 backtests fall under them? *(D4 evidence standards; exploration-vs-production boundary)*
9. Will you join the mock governance review (H12) as a panel member? *(commitment)*
10. What audit calendar constraints exist — when could a real review of a future layer earliest be scheduled? *(D11 timeline realism; R-OPS-05 adjacency)*

## Evidence to collect
- Past audit reports on credit decisioning/overrides (with remediation status).
- The bank's audit-trail/controls standards for decision systems (the concrete bar for D10).
- Their written in-principle acceptance criteria (verbatim → D10 acceptance section).

## Tensions to probe
- **"In principle" vs. formal:** E8 needs in-principle acceptance now; auditors may resist pre-commitment. Clarify the difference explicitly — what they accept is the *proposal's shape*, not a completed audit.
- **Lineage skepticism:** if today's overrides are already poorly tracked (their concern), they may doubt the bank can evidence a new layer — this doubt is data for D10's gap list, not an obstacle to hide.
- **Independence:** Audit advises and accepts criteria; it does not co-design. Keep their role clean or their sign-off loses value.

## Feed into D3 (and beyond)
- Position summary; acceptance-criteria register (→ D10); prior-findings evidence register (→ D1, D2, H4 caveats).
- Direct feeds: E8 gate design, mock-review panel (H12), M6 quality assessment in the tracker.
