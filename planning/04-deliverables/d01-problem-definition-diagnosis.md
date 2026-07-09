# D1 — Problem Definition & Diagnosis Report (template)
**Source §9:** "quantified P1/P2/P3 mix, root-cause evidence" · **Owner:** Product + Data Science · **Sign-off:** Risk + Business · **Feeds gates:** E1 (primary), E2 (consumes)

> Guidance: this is the phase's most important deliverable (§1.1: "Diagnosing the mix of P1/P2/P3 is the single most important output of the Early Phase"). It reports diagnosis only — no solution, no design implications beyond scope input to D5.

## 1. Executive summary
> Guidance: one page. The quantified P1/P2/P3 mix, the E1 verdict it implies, and the honest confidence level. If the evidence says "the model is fine," say it here in the first paragraph — that outcome is a success (§10 charter principle; no-go is a valid outcome).

## 2. Problem statement and diagnostic frame
> Guidance: restate the §1.1 decomposition verbatim (P1 misclassification / P2 coarse segmentation / P3 conservative offer mapping) with owners. State the ground-truth convention used (§3 below) — nothing in this report is interpretable without it.

## 3. Ground-truth definition (E2)
> Required evidence: the Risk-signed ground-truth convention (A2), including its documented limits (§6.2: selective-labels problem). Include the signature reference and date. If E2 is unmet, this report cannot be issued — E2's consequence: "Analyses are not accepted; phase not closed."

## 4. Evidence by sub-problem
### 4.1 P1 — Misclassification
> Required evidence: H1 boundary backtest, H3 thin-file cohorts, H4 override calibration, H2/H8 stale-score share (the P1-subset that the bank's own model would fix if invoked earlier). Report against pre-registered thresholds; falsified results reported with equal prominence.
### 4.2 P2 — Coarse segmentation
> Required evidence: boundary-density facts (from M1/M2, per §2.2), H5 within-segment outcome-variance findings (signal existence only — no model claims).
### 4.3 P3 — Conservative offer mapping
> Required evidence: offer-vs-policy-range headroom (M3 vs M7), H6 risk-adjusted foregone-revenue estimate, policy conservatism history (M2 change log, OQ-02 answers).

## 5. Quantified P1/P2/P3 mix
> Guidance: the KPI §8.1 requirement — "P1/P2/P3 problem mix quantified (share of opportunity by sub-problem), with Risk sign-off." Present as ranges with method notes; reconcile to the H-evidence above. State which sub-problem dominates and what that means for the bridge-layer value proposition (§1.1: it "differs materially depending on which sub-problem dominates").

## 6. Root-cause disposition (§1.2 table)
> Guidance: disposition each of the eight candidate root causes (model design; data limitations; stale data; segment granularity; policy conservatism; asymmetric error costs; override behavior; regulatory buffer stacking) as confirmed / refuted / undetermined, each with its evidence pointer (analysis or interview source per the §1.2 "evidence needed" column).

## 7. Customer-side materiality
> Required evidence: complaint taxonomy results (M8/H9), impacted-party analysis vs. §1.3 (near-boundary, thin-file, improving-profile customers), attrition findings (H11) where available.

## 8. Caveats and claim limits
> Guidance: mandatory section. Selective labels / survivorship (R-DAT-05), counterfactual absence (§2.4), campaign-selection bias (H7), any "scheduled" hypotheses whose absence bounds the claims. These caveats travel with every downstream use of this report.

## 9. Implications for opportunity assessment (input to D5)
> Guidance: which opportunities (O1–O8) the evidence energizes or kills — as scope input only. No design, no solution recommendations.

## 10. Annexes
> Cohort definitions (pre-registered protocol references to h01–h04), data lineage (tracker items used), analysis review notes (Risk review per D4).

## Sign-off block
| Role | Name | Date | Signature |
|---|---|---|---|
| Owner — Product | TODO | | |
| Owner — Data Science | TODO | | |
| Sign-off — Risk | TODO | | |
| Sign-off — Business | TODO | | |
