# Interview Guide — Credit Risk Team
**Stakeholder profile (source §3):** goals — portfolio loss within appetite, model integrity, defensible decisions. Concerns — bridge layer erodes model authority; risk creep via "optimized" offers; accountability if losses rise. Their success metrics — stable/predicted default rates; no appetite breach; clear governance over the layer.
**Session:** 2 × 90 min (week 2); participants: head of credit risk + policy owner + portfolio analytics lead.

## Objectives
1. Open the ground-truth conversation (A2 → E2) and identify prior accuracy work (OQ-01).
2. Establish the facts of segmentation mechanics (M2, M7) and override governance (H4 context).
3. Pre-register analytical thresholds: H2's X% (OQ-12), boundary-cohort conventions (H1), tolerance band candidates (D9).
4. Test organizational readiness (A9, H12) and surface the Risk-vs-Business tension honestly.

## Questions (12)
1. How do you currently define a "correct" segment assignment — and has anyone ever measured accuracy against outcomes? *(Appendix B-1, verbatim)*
2. When did segment cut-offs last change, why, and who decided? *(Appendix B-2, verbatim)*
3. Where are the expected PD bands and policy ranges per segment documented, and how are they governed? *(M7; the bounds any optimization must respect)*
4. What share of manual overrides are upgrades vs. downgrades? *(Appendix B-4, verbatim; H4)*
5. What evidence standard would convince you that under-classification exists — what would you need to see to sign a ground-truth definition? *(A2/E2; make them author it, not receive it)*
6. What is your risk appetite headroom today — capital, provisioning, concentration? *(Appendix B-6, verbatim; A5 — coordinate with CRO office)*
7. Where is conservatism in the current cut-offs deliberate policy, and where is it accumulated habit — margins added and never revisited? *(P3 vs P1; §1.2 "regulatory buffer stacking" and "policy conservatism")*
8. What threshold of stale-score-driven misplacement (X%) would you consider material? *(H2 pre-registration, OQ-12)*
9. What risk-stability tolerance band would you accept for cohorts touched by any future optimization — and measured how? *(D9/E7 — the number they must eventually co-sign)*
10. Under what bounds would an offer-optimization layer be acceptable to you — and what would make you veto it regardless of bounds? *(H12/A9; listen for the falsification signal: "any offer-influencing logic requires full model treatment")*
11. Your team is described as being blamed as a "growth blocker" without data to defend or adjust — is that fair, and what shared metric with Business would change it? *(§1.3, §3 tension; E7)*
12. What is the fastest a credit policy change has ever gone from proposal to production? *(Appendix B-10, verbatim; R-OPS-05)*

## Evidence to collect
- M7: risk appetite statement, credit policy docs, per-segment policy ranges (Mandatory data — walk out with pointers/owners).
- M2: cut-off definitions + change history; policy governance calendar (§2.3 pain point "slow policy change cycle").
- Override policy and authority matrix (M6 context); any prior calibration/retro-analysis reports (OQ-01).
- Their candidate ground-truth conventions, verbatim.

## Tensions to probe
- **Risk-vs-Business shared metric (primary):** do they accept that under-lending is a loss? Would they sign a risk-adjusted value metric jointly with Business, and what would it need to contain (tolerance band, control expectations)? If they insist on raw-loss metrics only, E7 is at risk — surface early, escalate per charter.
- **Authority erosion:** does "the segment remains the anchor; the layer only optimizes within policy" actually reassure them, or do they hear "second-guessing the model" (A9 falsifier)?
- **Accountability:** their §3 concern "whose decision was it?" — connect to OQ-09 and D10.

## Feed into D3 (and beyond)
- Position summary vs. the §3 map (confirmed / shifted); tension-log entries (shared metric, authority); named commitments (workshop dates, data pointers).
- Direct feeds: E2 workshop input, H1/H2 protocol thresholds, D9 tolerance-band candidates, D10 accountability views, M2/M7 acquisition.
