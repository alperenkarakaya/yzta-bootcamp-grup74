# BWS2 — Data & Simulation
### Synthetic portfolio, ground truth, data quality & bias

**One-line mission:** generate a synthetic credit portfolio whose data-generating process we control, so that hypotheses **H1–H14** are testable, ground truth is knowable, and the P1/P2/P3 mix is *demonstrably present*.

**Why this is a bootcamp superpower (review A1, K11):** a real bank can never hand us clean ground truth — you only observe defaults for credit actually granted (selective-labels/counterfactual problem, source §6.2, §2.4). Because *we author* each customer's true risk and deserved segment, we can prove the product finds under-classification we deliberately planted — and prove the guard never lets it overshoot.

---

## Objective
Deliver a realistic-but-honest synthetic dataset (portfolio + time series) plus a data dictionary, ground-truth labels, and a data-quality/bias report. The data must contain the *hard* cases (thin-file, stale-score, boundary, asymmetric overrides) so the product is not solving a trivial world (review R4).

## In scope
- **Synthetic schema** mapping every §7 Mandatory item (M1–M9) to fields; Useful items (U1–U8) as additional signals; OPT items only if a hypothesis is attached (minimization, source §7 rule; review A1).
- **Data-generating process** that seeds a known P1/P2/P3 mix and known boundary/thin-file/stale-score/override effects (source §1.1, §1.2).
- **Ground-truth implementation**: each synthetic customer carries a "true" risk and "deserved segment" per the BWS1 definition (source A2, E2).
- **Cohorts** required by hypotheses: boundary cohorts (H1), stale-score cohorts (H2/H8), thin-file (H3), override logs with outcomes (H4), within-segment signal variance (H5), past limit-increase campaign (H7), attrition with destination (H11), protected/proxy attributes for fairness (H14/OPT5).
- **Data dictionary**, **data-quality checks**, and a **bias/representativeness report** (source §6.5, §8.2 fairness).
- A **reproducible generator** (seeded) + a small "wow-case" curated subset for the demo.

## Out of scope
- Defining ground truth *conceptually* (that is BWS1 T4 — BWS2 *implements* it).
- Building models/agents on the data (→ BWS3); displaying it (→ BWS4); storage infra (→ BWS5).
- Claiming real-world effect sizes — all outputs labelled synthetic (review R1).

## Inputs from the planning package
- **Data inventory §7:** M1–M9 (mandatory → schema), U1–U8 (useful → signals), OPT1–OPT5 (gated; OPT1/OPT4 remain DO-NOT-COLLECT unless a hypothesis is attached — OQ-22).
- **Hypotheses needing data:** H1, H2, H3, H4, H5, H6, H7, H8, H11, H14.
- **Assumptions:** A1 (systematic under-classification — seed it), A2 (ground truth — implement it), A7 (data existence — trivially true, we generate).
- **Deliverables:** D8 (data inventory & disposition → data dictionary), feeds D1/D4/D5/D9.
- **Exit criteria:** E5 (mandatory data dispositioned → "schema covers 100% of M-items + DQ/bias report").
- **Deltas:** A1 (synthetic strategy), K9 (perfect baseline), K11 (selective-labels honesty), R1/R4 (honesty hooks).

## Dependencies on other workstreams
- **Consumes from BWS1:** ground-truth definition (T4), intended P1/P2/P3 mix (T1/T2), policy ranges (T3), success-metric definitions (T5).
- **Provides to BWS3:** labelled data, cohorts, signals, train/eval splits with ground truth.
- **Provides to BWS4:** display-ready customer/portfolio records and example cases.
- **Provides to BWS5:** schema + generator to wire behind the sim engine; fixtures for tests.
- **Provides to BWS1:** the portfolio to compute O5 metric and sizing.

## Task breakdown

| # | Task | Size | Traces to | Feeds |
|---|---|---|---|---|
| T1 | Design synthetic schema: map M1–M9 → fields (scores, segments, timestamps, model version, cut-offs+history, offers, outcomes, migration, override logs, policy ranges, per-segment financials) | L | §7.1 M1–M9, D8, A1 | BWS5 (engine), BWS3 |
| T2 | Define data-generating process with **seeded P1/P2/P3 mix** (misclassification noise, coarse-segment boundary effect, conservative offer mapping) | L | §1.1, A1, K2 | BWS3, BWS1 sizing |
| T3 | Implement **ground-truth labels** ("true" risk + deserved segment) per BWS1 definition | M | A2, E2, K11 | BWS3 (eval), G0 gate |
| T4 | Generate **boundary cohorts** (customers near cut-offs, under-classified vs realized) | M | H1, O2 | BWS3 (H1 demo) |
| T5 | Generate **stale-score / migration** time series (score age vs. later migration) | M | H2, H8, U6 | BWS3 (H2/H8) |
| T6 | Generate **thin-file / new-to-bank** cohort with sparse bureau data | M | H3, §1.2 | BWS3 (H3) |
| T7 | Generate **override logs** with reasons + outcomes, asymmetric (downgrades ≫ upgrades) | M | H4, M6 | BWS3 (H4), BWS1 (D10) |
| T8 | Generate **within-segment behavioral signals** (transaction stability, deposit trends, utilization) with real separation to find | M | H5, U1, U2, O1 | BWS3 (signal analysis) |
| T9 | Generate **past limit-increase campaign** results (utilization uplift vs delinquency) | M | H7, U3, O6 | BWS3, BWS1 (O6) |
| T10 | Generate **attrition/closure** data with destination indicators for boundary cohorts | S | H11, U4 | BWS3 (H11) |
| T11 | Generate **complaint verbatims + NPS** (LLM-authored) tagged to limits/offers | M | H9, H10, M8, U5 | BWS3 (explanation eval), BWS4 |
| T12 | Generate **protected/proxy attributes** + seed a *correctable* disparity for H14 | M | H14, OPT5, E9, review R4 | BWS3 (fairness agent) |
| T13 | Generate **per-segment financials** (revenue, EL, provisioning, capital/funding proxy) for risk-adjusted sizing | M | H6, M9, U8, O5 | BWS1 (sizing), BWS3 |
| T14 | Write the **data dictionary** (every field: meaning, source hypothesis, distribution) | M | §7 rule, D8 | all, deck |
| T15 | **Data-quality checks** (nulls, ranges, referential integrity, drift across time slices) | S | §6.5, E5 | BWS5 (tests) |
| T16 | **Bias/representativeness report** (distribution across protected groups; document seeded disparity) | M | §6.3, §8.2, H14 | BWS1 (fairness), deck |
| T17 | **Reproducible seeded generator** + curated demo subset ("wow cases") | M | demo, review R5 | BWS4, BWS5 |
| T18 | **Ground-truth honesty appendix** (assumptions of the generator; what it can/can't prove) | S | review R1/R4, K11 | BWS1 (honest-limits) |

## Definition of done
- Schema covers **100% of M1–M9** (E5-equivalent gate G1) and all hypothesis cohorts H1–H8/H11/H14 exist.
- Ground-truth labels implemented and frozen by G0; generator is seeded/reproducible.
- Data dictionary, DQ report, and bias report complete; seeded correctable disparity documented (H14).
- Hard cases (thin-file, stale, boundary, asymmetric overrides) present and non-trivial (review R4).
- Every field traces to a hypothesis (minimization); OPT1/OPT4 excluded unless OQ-22 attaches one.

## Demo-day contribution
- The **"we control ground truth" credibility moment**: show that the product recovers an under-classification we planted, and that the guard blocks overshoot.
- The **fairness story**: a disparity we seeded, detected and corrected by the fairness agent (H14 as remediation, review R4).
- The **data dictionary + honesty appendix** as execution-quality evidence.

## Suggested owner skill profile
Data engineer / quantitative analyst comfortable with statistical simulation (distributions, seeded generators), pandas/Polars or equivalent, and basic credit metrics (PD, segments, EL). Cares about reproducibility and honest data. Pairs with BWS3 owner on train/eval splits.
