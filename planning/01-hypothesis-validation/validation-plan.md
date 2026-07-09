# Hypothesis Validation Plan — Sequencing H1–H14
**Purpose:** sequence all 14 hypotheses by data dependency, protect the E1-critical path, and satisfy KPI §8.1: "Hypotheses H1–H14 tested or explicitly scheduled with data dependencies — ≥ 10 tested, remainder scheduled."
**Protocol governance (applies to every hypothesis):** protocols and thresholds are pre-registered with Risk **before** results are known; falsification conditions are honored verbatim; a falsified hypothesis is a valid, reportable result — no-go is a valid outcome.

## 1. Grouping by data dependency

| Group | Hypotheses | Data dependency | Ready when |
|---|---|---|---|
| **A — Mandatory-data backtests** | H1, H2, H3, H4, H8 | M1, M2, M4, M5, M6, M7 (+U6 for H2/H3/H8) | E2 ground truth signed (wk4) + M-tier delivery (wk3) |
| **B — Useful-data value analyses** | H5 (U1), H6 (M9, U8, M3, M7), H7 (U3, U2), H11 (U4) | U-tier delivery + legal basis for U1 | Wk5 onward, item by item |
| **C — Customer/qualitative** | H9 (M8, U5, interviews), H10 (U5, concept sessions) | M8 delivery + research clearance (OQ-20) | Taxonomy wk3; interviews wk5–6 |
| **D — Organizational/legal (no analytical data)** | H12 (interviews, mock review), H13 (legal opinion), H14 (M1, M4, **OPT5** via legal gate) | Interview calendar; counsel ToR; OPT5 clearance (wk5) | H12/H13 from wk1–3; H14 after clearance |

Group D starts **immediately** — it needs no data delivery and carries the longest external lead times (counsel, committee calendars). This is the source's Appendix A "parallel" legal & governance track.

## 2. Wave sequencing (aligned to `../00-program/workplan.md`)

| Wave | Weeks | Runs | Gate targets |
|---|---|---|---|
| 0 — Setup | 1–2 | Data request issued; ground-truth workshops (A2); protocol pre-registration begins; H13 ToR; H12 interviews scheduled; complaint taxonomy prep (H9) | E2 setup |
| 1 — First evidence | 3–5 | H1, H2 (first M-data); H9 taxonomy; H12 interviews + mock-review prep; H13 jurisdiction scan | E2 signed wk4 |
| 2 — Full evidence | 4–6 | H3, H4, H8; H5, H7, H11 as U-items land; H10 sessions; H14 after wk5 legal gate; H13 draft opinion wk6 | E1 evidence complete |
| 3 — Synthesis | 5–7 | H6 joint sizing (consumes H1–H4 preliminary P-mix); consolidation into D1/D4/D5 | E1, E3, E9 |

## 3. Master table — hypothesis → data items → deliverable(s) → exit criterion(-a)

| H | Statement (short) | Data items (§7) | Deliverable(s) | Exit criteria | Status |
|---|---|---|---|---|---|
| H1 | Boundary cohorts under-classified vs. outcomes | M1, M2, M4, M7 (+M3 context) | D1, D4, D5(O2) | E1 (consumes E2) | TODO |
| H2 | Stale scores drive under-performing offers (>X%) | M1, M5, U6 | D1, D4, D5(O3) | E1 | TODO |
| H3 | Thin-file placed low, migrate up | M1, M5, M4, U6 | D1, D4 | E1 | TODO |
| H4 | Overrides asymmetric, downgrades miscalibrated | M6, M1, M4 | D1, D4, D5(O2), D10 | E1 | TODO |
| H5 | Within-segment signals separate risk (existence only) | U1, M1, M4 | D4, D5(O1, O8) | E3 | TODO |
| H6 | Under-lending forgoes risk-adjusted revenue | M9, U8, M3, M7 | D1, D4, D5, D9 | E1 (value floor), E3 | TODO |
| H7 | Past limit increases: utilization ↑ without proportional delinquency | U3, U2, M4 | D4, D5(O1, O6), D9 | E3 | TODO |
| H8 | Earlier re-scoring moves meaningful population | M1, M5, U6 | D1, D4, D5(O3) | E1, E3 | TODO |
| H9 | Dissatisfaction = explanation/path, not amount | M8, U5 (+interviews) | D1, D4, D5(O4), D9 | E3, E7 (baselines) | TODO |
| H10 | Explainability raises acceptance/trust | U5 (+qual sessions) | D4, D5(O4), D9, D10 | E7 (baselines) | TODO |
| H11 | Boundary cohorts attrite more within 12m | U4, M1, M2 (OPT2 context) | D4, D5 | E3 | TODO |
| H12 | Governance accepts bounded, auditable layer | — (M7 input; interviews, mock review) | D3, D4, D10 | E8 | TODO |
| H13 | Classification stays "offer optimization" | — (policy docs, contracts via D2; legal work) | D4, D7, D5 (viability flags), D11 | E4 | TODO |
| H14 | Under-classification uncorrelated with protected attributes (or correction reduces disparity) | M1, M4, OPT5 (legal-gated) | D4, D7, D9 | E9 | TODO |

## 4. Assumption coverage (A1–A10 → validation vehicle)

KPI §8.1 requires 100% of assumptions dispositioned. Each assumption's validation method is the source's own (§1.4); dispositions land in D4.

| A | Assumption (short) | Validation vehicle | Feeds |
|---|---|---|---|
| A1 | Under-classification systematic & material | H1–H4 backtests/cohorts | D1, E1 |
| A2 | "Deserved segment" definable | Ground-truth workshop with Risk (wk2–4) | E2; prerequisite to H1–H4, H14 |
| A3 | Dissatisfaction driven by segment/limit outcomes | H9 (complaint taxonomy, NPS verbatims, customer interviews) | D1, D5(O4), D9 |
| A4 | Bank loses net revenue by under-lending | H6 (RAROC-style, business level) | D5, E3 |
| A5 | Risk appetite has headroom | M7 review with CRO office (workplan wk2; OQ-06) | D5 constraints, E3 |
| A6 | Layer ≠ "credit decision model" | H12 (internal governance) + H13 (external classification) | D7, D10, E4, E8 |
| A7 | Signals exist, accessible, permissible | Data inventory + legal-basis review (`../03-data/`) | D8, E5 |
| A8 | Engine output can be intercepted pre-offer | D2 technical walkthrough (workplan wk2–4) | D2, E6 |
| A9 | Stakeholders will trust AI-assisted adjustments | Stakeholder interviews (all guides) + governance pre-alignment (H12) | D3, D10, E8 |
| A10 | Fix helps both sides symmetrically | Per-segment scenario analysis in D5 (H6/H7 evidence) | D5, E3 |

## 5. "≥10 tested" protection — deferral priority if data slips (OQ-26)

If delivery failures force hypotheses from "tested" to "scheduled," defer in this order (last = never defer):

1. **H11** (needs U4 destination quality; value case survives without it, with wider ranges)
2. **H5** (needs U1 + legal basis; O1/O8 sizing degrades to qualitative)
3. **H7** (if U3 doesn't exist — OQ-03 tells us by wk2)
4. **H8** (if the OQ-25 re-run path is infeasible in-window)
5. **H10** (if recruitment slips; H9 complaint-side still runs)
6. **H14** may move to the formally-blocked path only via the E9 procedure — never silently deferred.
7. **Never defer:** H1–H4 (E1 depends on them), H6 (E3), H9 complaint-side (M8 is Mandatory), H12, H13 (E8/E4 gates).

A "scheduled" hypothesis must carry: the blocking data item(s), the tracker blocking-issue entry, the earliest feasible date, and an owner — that is what "explicitly scheduled with data dependencies" means in KPI §8.1.

## 6. Standing caveats (attach to every analytical result)

- **Selective labels / survivorship (R-DAT-05, §2.4):** outcomes exist only for credit actually granted at actually offered levels — a permanent, documented limit on what claims can honestly be validated.
- **Counterfactual absence (§2.4):** "what would have happened with a better offer" does not exist in historical data; H7's natural experiment is the closest available evidence.
- **Feedback loops (R-AI-02):** flagged as a Mid Phase design requirement; noted in validation caveats per §6.2 — no Phase 1 claim may assume post-intervention data behaves like historical data.
