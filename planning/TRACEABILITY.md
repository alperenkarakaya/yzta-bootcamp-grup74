# TRACEABILITY — Source IDs → Working-Package Artifacts
**Rule:** every A, H, O, D, E and §7 data item from `early-phase-plan-credit-offer-optimization.md` must appear in at least one artifact, with its chain: validation artifact → data items → deliverable(s) → exit criteria. Orphans are defects (§7 Orphan/defect log).
**ID conventions declared by this package** (the source assigns none for these): data items **M1–M9 / U1–U8 / OPT1–OPT5** (`03-data/data-inventory-tracker.md`); risks **R-BUS / R-AI / R-REG / R-OPS / R-DAT** (`05-risk-and-compliance/risk-register.md`). All other IDs are the source's own, used verbatim.

## 1. Assumptions A1–A10

| A | Validation artifact(s) | Data items | Deliverable(s) | Exit criteria |
|---|---|---|---|---|
| A1 | `01-hypothesis-validation/h01–h04.md` (backtests/cohorts) | M1, M2, M4, M5, M6 | D1, D4 | E1 |
| A2 | Ground-truth workshop (workplan wk2–4; charter decision rights; validation-plan §4) | M7, M1, M4 | D1 §3, D4, D9 (KPI 1) | E2 |
| A3 | `h09.md` + customer research guide | M8, U5 | D1 §7, D4, D5 (O4), D9 | E3, E7 (baselines) |
| A4 | `h06.md` (RAROC-style, business level) | M9, U8, M3 | D4, D5 | E3 |
| A5 | Risk-appetite review with CRO office (workplan wk2; exec + credit-risk guides, OQ-06) | M7 | D4, D5 §2 (constraints) | E3 |
| A6 | `h12.md` (internal) + `h13.md` (external) | — (M7, policy/contract docs) | D4, D7, D10 | E4, E8 |
| A7 | Data inventory + legal-basis review (`03-data/`, regulatory-workplan WS4) | all §7 items | D8 | E5 |
| A8 | D2 technical walkthrough (workplan wk2–4; OQ-07) | — (systems/contract discovery) | D2 | E6 |
| A9 | Stakeholder interviews (all `02-stakeholders/` guides) + h12 governance pre-alignment | — (interview evidence) | D3 §4, D4, D10 | E8 |
| A10 | Per-segment win-win scenario analysis in D5 (via h06/h07 evidence) | M9, U8, U3, U2 | D5 §4, D4 | E3 |

## 2. Hypotheses H1–H14

| H | Validation artifact | Data items | Deliverable(s) | Exit criteria |
|---|---|---|---|---|
| H1 | `h01.md` | M1, M2, M4, M7 (+M3 context) | D1, D4, D5(O2) | E1 (consumes E2) |
| H2 | `h02.md` | M1, M5, U6 | D1, D4, D5(O3) | E1 |
| H3 | `h03.md` | M1, M5, M4, U6 | D1, D4 | E1 |
| H4 | `h04.md` | M6, M1, M4 | D1, D4, D5(O2), D10 | E1 |
| H5 | `h05.md` (signal existence only — no model building) | U1, M1, M4 | D4, D5(O1, O8) | E3 |
| H6 | `h06.md` | M9, U8, M3, M7 | D1, D4, D5, D9 | E1 (value floor), E3 |
| H7 | `h07.md` | U3, U2, M4 | D4, D5(O1, O6), D9 | E3 |
| H8 | `h08.md` | M1, M5, U6 | D1, D4, D5(O3) | E1, E3 |
| H9 | `h09.md` + customer guide | M8, U5 | D1, D4, D5(O4), D9 | E3, E7 |
| H10 | `h10.md` + customer & front-line guides | U5 (+qualitative sessions) | D4, D5(O4), D9, D10 | E7 |
| H11 | `h11.md` | U4, M1, M2 (OPT2 context) | D4, D5 | E3 |
| H12 | `h12.md` (interviews + mock governance review) | — (M7 input) | D3, D4, D10 | E8 |
| H13 | `h13.md` + regulatory-workplan WS1 | — (policy/contract docs, legal work) | D4, D7, D5 (viability flags), D11 | E4 |
| H14 | `h14.md` + regulatory-workplan WS3 | M1, M4, OPT5 (legal-gated) | D4, D7, D9 | E9 |

## 3. Opportunities O1–O8 (all sized in D5; all filtered through E4 viability)

| O | Opportunity (short) | Evidence chain (hypotheses → data) | Deliverable | Exit criteria |
|---|---|---|---|---|
| O1 | Within-segment offer differentiation | H5 (U1) + H7 (U3, U2) | D5 §3 | E3, E4 |
| O2 | Boundary-case flagging for review | H1 (M1, M2, M4) + H4 (M6) + U7 demand evidence (OQ-21) | D5 §3 | E3, E4 |
| O3 | Offer timing & refresh optimization | H2 (M1, M5, U6) + H8 (M1, M5, U6) | D5 §3 | E3, E4 |
| O4 | Offer explanation & transparency layer | H9 (M8, U5) + H10 (qualitative) | D5 §3 | E3, E4 |
| O5 | Under-lending measurement & feedback | H6 (M9, U8) — "value even if no offer is ever changed"; fallback scope for E4 | D5 §3, steering pack §12 | E3, E4 |
| O6 | Graduated / staged offers | H7 (U3, U2, M4) + policy sign-off flag (§4 medium friction) | D5 §3 | E3, E4 |
| O7 | Counter-conservatism calibration input | H1 + H2 + H6 evidence routed to Risk (the P3 owner) | D5 §3; pivot option in steering pack | E3, E4 |
| O8 | Segment-adjacent signal enrichment (advisory) | H5 (U1) + H12 (trust/governance conditions) | D5 §3 | E3, E4, E8 (conditions) |

## 4. Deliverables D1–D11 → template → gate

| D | Template | Owner / Sign-off (source §9) | Exit criteria fed |
|---|---|---|---|
| D1 | `04-deliverables/d01-problem-definition-diagnosis.md` | Product + Data Science / Risk + Business | E1 |
| D2 | `04-deliverables/d02-current-state-decision-flow-map.md` | Product + Bank SMEs / Risk + IT | E6 |
| D3 | `04-deliverables/d03-stakeholder-analysis-engagement-log.md` | Product / Program sponsor | supports E7, E8; KPI coverage |
| D4 | `04-deliverables/d04-assumption-hypothesis-validation-report.md` | Data Science / Risk | E1, E2 evidence; feeds all H-gates |
| D5 | `04-deliverables/d05-opportunity-assessment-prioritization.md` | Product + Finance / Executives | E1, E3 (consumes E4 flags) |
| D6 | `04-deliverables/d06-risk-register.md` (+ living register `05-risk-and-compliance/risk-register.md`) | Product + Risk / CRO office | supports E10 |
| D7 | `04-deliverables/d07-regulatory-legal-position-paper.md` (+ `05-risk-and-compliance/regulatory-workplan.md`) | Compliance/Legal / CCO | E4, E9 |
| D8 | `04-deliverables/d08-data-inventory-access-disposition.md` (+ tracker) | Data Science + Data Office / CDO | E5 |
| D9 | `04-deliverables/d09-success-metrics-baseline-book.md` | Product + Finance / Risk + Business joint | E7 |
| D10 | `04-deliverables/d10-governance-accountability-proposal.md` | Product + Risk / Model Risk + Audit | E8 |
| D11 | `04-deliverables/d11-mid-phase-charter-draft.md` | Product / Steering committee | E10 |

## 5. Data items §7 → consumers

| Item | Consumed by | Appears in |
|---|---|---|
| M1 | H1, H2, H3, H8, H11, H14 | tracker, request pack, h-files |
| M2 | H1, H11; D2 | tracker, request pack, h01, h11, d02 |
| M3 | H6; H1 context; D1 | tracker, request pack, h01, h06 |
| M4 | H1, H3, H4, H5, H7, H14 (+H2/H8 checks) | tracker, request pack, h-files |
| M5 | H2, H3, H8 | tracker, request pack, h02, h03, h08 |
| M6 | H4; D10 evidence | tracker, request pack, h04, d10 |
| M7 | A5; H1 (PD bands), H6, H12, H13 | tracker, request pack, h01, h06, h12, h13, charter |
| M8 | H9; A3; D9 baseline | tracker, request pack, h09, d09 |
| M9 | H6; O5; D5 | tracker, request pack, h06 |
| U1 | H5 | tracker, request pack, h05 |
| U2 | H7; O1 sizing | tracker, request pack, h07 |
| U3 | H7 | tracker, request pack, h07 |
| U4 | H11 | tracker, request pack, h11 |
| U5 | H9, H10; D9 baselines | tracker, request pack, h09, h10, d09 |
| U6 | H2, H3, H8 | tracker, request pack, h02, h03, h08 |
| U7 | O2 demand sizing in D5 (rule nuance → OQ-21) | tracker, request pack, business & front-line guides |
| U8 | H6 precision | tracker, request pack, h06 |
| OPT1 | **none — DO-NOT-COLLECT** per §7 rule (OQ-22) | tracker (disposition), h03 note |
| OPT2 | H11 context only | tracker, request pack, h11 |
| OPT3 | H1–H4 outcome-period contextualization | tracker, request pack, h01 |
| OPT4 | **none — DO-NOT-COLLECT** per §7 rule (OQ-22) | tracker (disposition) |
| OPT5 | H14 (legal-gated) | tracker, request pack, h14, regulatory-workplan WS3 |

## 6. Exit criteria E1–E10 ← feeding artifacts
Gate detail in `06-gates/exit-criteria-checklist.md`. Summary: E1←D1/D4 (H1–H4, H6, H8) · E2←ground-truth workshop (A2) · E3←D5 (H5–H11, A4/A5/A10) · E4←D7 (H13) · E5←D8 (A7, tracker) · E6←D2 (A8) · E7←D9 (H9/H10 baselines, shared metric) · E8←D10 (H12, A6/A9) · E9←D7 §5 (H14) · E10←D11 + steering pack + all above.

## 7. Orphan / defect log

| # | Item | Issue found | Resolution (fix applied) |
|---|---|---|---|
| 1 | U7 | §7 rule requires a *hypothesis* per Useful item, but the source's stated purpose for U7 is "Demand evidence for O2" — an opportunity, not a hypothesis. Strictly read, U7 would be an orphan under the source's own rule. | Kept collected, mapped to O2 sizing in D5 §3 (its source-stated purpose) and flagged as a rule nuance for Risk/DS confirmation — **OQ-21**. Not silently re-mapped. |
| 2 | OPT1, OPT4 | No stated Phase-1 hypothesis in the source ("future signal potential" / "possible early indicators") — under the §7 minimization rule they must not be collected, which would leave them without downstream artifacts. | Dispositioned **DO-NOT-COLLECT** in the tracker (their traceable disposition), excluded from the request pack §2.6, and routed to **OQ-22** for owners to attach a hypothesis if they want collection. Orphanhood is resolved by explicit disposition, not by inventing analyses. |
| 3 | Finance, IT/Bank SMEs, CRO office | Named owners/sign-offs in §9 but absent from the §3 stakeholder map — no interview guide "home" of their own. | Finance folded into the Executives guide (CFO seat) + named-delegate request (**OQ-14**); IT/SMEs engaged through D2 walkthrough sessions (workplan wk2) (**OQ-15**); CRO office covered in exec guide Q2 + D6 sign-off path. RACI includes all three columns with the flag noted. |
| 4 | §8.2 product KPIs | Risk of being defined without baselines (the source's "story, not a metric" failure). | All eight §8.2 KPIs templated in D9 §2 with mandatory baseline evidence register (D9 §3); baselines sourced from H6/H9/H10/H14 and tracker items. No orphan remains. |
| 5 | §1.2 root causes / §2.1 flow steps / §2.3 pain points | Structural source content that could have been left untraced. | §1.2 → D1 §6 disposition table + interview guides; §2.1 steps 1–9 → D2 §2 (verbatim structure); §2.3 → front-line/business guides evidence lists + D2 §7. |

**Coverage verdict:** all 10 A, 14 H, 8 O, 11 D, 10 E, and 22 §7 data items trace to at least one artifact; the two deliberate non-collections (OPT1, OPT4) are traceable dispositions per the source's own minimization rule. Self-review evidence: `README.md` §5.

---

## 8. Source IDs → Bootcamp Workstreams (BWS1–BWS5)

**Rule:** every source ID must map to at least one bootcamp workstream that carries it into the build, OR be an explicit, logged deferral. Added for the bootcamp restructure (`07-bootcamp-workstreams/`, driven by `bootcamp-adaptation-review.md`). BWS labels are the *bootcamp* partition; the source's Appendix-A "WS1…6" are a different partition (called **source-WS** to avoid collision — see review §6).

**Legend:** ●=primary owner, ○=contributes.

| Source item | BWS1 Business | BWS2 Data | BWS3 AI Core ★ | BWS4 Product | BWS5 Eng | Notes |
|---|---|---|---|---|---|---|
| **P1/P2/P3** | ● | ○ (seed mix) | ○ (detect) | ○ (narrate) | | Framing spine (review K1/K2) |
| A1 | ● | ● (seed) | ○ (detect) | | | Under-classification made demonstrable |
| A2 (ground truth) | ● (define) | ● (implement) | ○ (eval vs) | | | G0 gate item |
| A3 | ● | | | ● | | Explanation-driven satisfaction → O4 UI |
| A4 / A5 / A10 | ● | ○ (financials) | | | | Risk-adjusted sizing method (review A6) |
| A6 / A9 | ● | | ○ (bounded+auditable) | ○ | ○ (audit) | Governance-acceptance-by-architecture |
| A7 | ○ | ● (we generate) | | | ○ (store) | Trivially satisfied by simulation |
| A8 | | | | | ● (build seam) | Insertion point built, not discovered |
| **H1–H4** | ○ | ● (cohorts) | ● (detect vs GT) | ○ (evidence pack) | ○ (fixtures) | Problem existence — G2 |
| **H5** | | ● (signal data) | ● (signal separation) | ○ | | "signal existence only, no re-score" guard held |
| **H6** | ● (sizing) | ● (financials) | ○ | | ○ (instrument O5) | Risk-adjusted uplift metric |
| **H7** | ○ | ● (campaign data) | ○ | ● (O6 UI) | | Graduated offers |
| **H8** | | ● (stale/migration) | ● (signal) | | | Timing/refresh |
| **H9 / H10** | ○ | ● (verbatims/NPS) | ● (explanation + LLM-judge) | ● (explanation UI) | | Explainability/trust |
| **H11** | | ● (attrition) | ● (signal) | | | Attrition of boundary cohorts |
| **H12** | ● (persona/assumption) | | ○ | ○ | ○ (audit) | Governance acceptance (personas, review A2) |
| **H13** | ● (regulatory-awareness note) | | ○ (architecture argument) | | | D7-as-note (review A3) |
| **H14** | ● (fairness position) | ● (seed disparity) | ● (fairness agent) | ● (fairness view) | | Remediation, not decoration (review R4) |
| **O1** | ○ | ● (signals) | ● (optimize) | ● (offer screen) | ○ | Within-segment differentiation |
| **O2** | ○ | ● (boundary cohort) | ● (flag) | ● (evidence pack) | | Human stays decision-maker |
| **O3** | ○ | ● (stale data) | ● (signal) | ○ | | Timing/refresh optimization |
| **O4** | ○ | ● (verbatims) | ● (explanation agent) | ● (explanation UI) | | Transparency layer |
| **O5** | ● (define metric) | ● (financials) | | ○ (metric screen) | ● (instrument) | Headline under-lending metric |
| **O6** | ○ | ● (campaign) | ● (graduated logic) | ● (graduated UI) | | Policy-bounded staged offers |
| **O7** | ● (calibration narrative) | ○ | ○ (evidence) | | | Counter-conservatism input to Risk |
| **O8** | ○ | ○ | ● (advisory enrichment) | ○ | | Advisory only — never auto-acting |
| **D1** | ● | ○ | ○ | ○ | | Problem diagnosis |
| **D2** | | | | | ● (as-built architecture) | Decision-flow → running system (review A5) |
| **D3** | ● (personas) | | | ○ | | Personas + assumption register (review A2) |
| **D4** | ○ | ● | ● | | ○ | Hypothesis validation evidence |
| **D5** | ● (sizing) | ● (data) | ○ (evidence) | ○ | | Opportunity sizing (illustrative, review A6) |
| **D6** | ● (register) | ○ | ○ (AI risks) | | ○ | Risk register refreshed for build |
| **D7** | ● (regulatory-awareness) | | ○ (RAG corpus) | | ○ (audit export) | Awareness, not legal opinion (review A3) |
| **D8** | ○ | ● (data dictionary) | | | ○ (store) | Data inventory → synthetic schema |
| **D9** | ● (metrics book) | ● (baselines) | ○ | ● (trust baselines) | ● (instrument) | Perfect baselines (review K9) |
| **D10** | ● (governance narrative) | | ○ (guard/log) | ○ (audit view) | ● (audit trail) | Operationalized as running audit trail |
| **D11** | ● (charter/decision) | | | | ○ | Go/no-go → demo-readiness gate G4 |
| **E1** | ● | ● | ● | | | Materiality in synthetic world (G2) |
| **E2** | ● | ● | | | | Ground truth explicit (G0) |
| **E3** | ● | ○ | ○ | ○ | | Value case (illustrative) |
| **E4** | ● (awareness note) | | ○ (architecture) | | | Regulatory viability by construction |
| **E5** | | ● (schema+DQ report) | | | ○ | "100% M-items + DQ/bias report" |
| **E6** | | | ○ | | ● (seam) | Insertion point built (G1) |
| **E7** | ● (shared metric) | | | ● (shared-metric screen) | | Risk–Business shared number on screen |
| **E8** | ● (governance) | | ○ | ○ | ● (audit) | Accountability via audit trail |
| **E9** | ● (fairness position) | ● (seed) | ● (fairness agent) | ● (view) | | Fairness executed on synthetic data |
| **E10** | ● (go/no-go) | | | ○ | ○ | Demo-readiness gate (no-go allowed) |
| §7 M1–M9 | ○ | ● (schema) | ○ | ○ | ● (serve) | All mandatory items → synthetic fields |
| §7 U1–U8 | | ● (signals) | ● (consume) | ○ | ○ | All useful items → simulated signals |
| §7 OPT1/OPT4 | | ○ (DO-NOT-COLLECT unless OQ-22) | | | | Minimization discipline preserved |
| §7 OPT2/OPT3/OPT5 | | ● (gated generators) | ○ (OPT5→H14) | | | Only if hypothesis attached |
| §8 KPIs | ● (define) | ● (baseline) | | ○ | ● (instrument) | §8.1 reframed to demo evidence; §8.2 with synthetic baselines |

**Cross-cutting invariant (no single BWS owns it):** the **hard boundary** (source §4 — never re-score / override segment / change inputs / auto-approve above policy) is enforced in **BWS3** (deterministic policy-guard agent) + **BWS5** (append-only audit trail + boundary tests), rendered by **BWS4** (segment read-only), and narrated by **BWS1**. Tracked in every ws file's boundary reminder and in `workstreams.md`.

### 8.1 Bootcamp orphan / deferral log
| # | Item | Status under bootcamp restructure | Resolution |
|---|---|---|---|
| B1 | Source-WS labels (Appendix A: Mobilize/Legal/Evidence/Sizing/Alignment/Close) | Re-partitioned into BWS1–BWS5 (different partition) | Mapping in `bootcamp-adaptation-review.md` §6; labelled source-WS vs BWS to prevent ID collision — not an orphan |
| B2 | R-OPS-04 (vendor contract), R-DAT-04 (bureau license) | N/A in simulation | Kept in register with "sim: N/A, real-world: applies" note (review A5); BWS5 T-notes carry them for the real-deployment narrative |
| B3 | OPT1, OPT4 | Remain DO-NOT-COLLECT | Unchanged from §7 log entry 2 / OQ-22; no BWS generates them unless a hypothesis is attached |
| B4 | Bootcamp calendar / team / tech / rubric / demo format | Unknown — not guessed | OQ-27…OQ-31; sequencing uses relative sprints and inferred jury dimensions until answered |

**Bootcamp coverage verdict:** every P/A/H/O/D/E/§7/§8 source item maps to ≥1 bootcamp workstream above; the hard boundary has explicit multi-BWS owners; the only non-mappings are deliberate, logged deferrals (§8.1 B2/B3) and unanswered externalities (§8.1 B4 → OQ-27…31). No silent orphans.

### 8.2 BWS task IDs now also live in `../ROADMAP.md` (definition ↔ operation)
The `ws1.md`–`ws5.md` task tables remain the **definition source**; `../ROADMAP.md` is the **operational source** (story points, sprint, status). Task IDs (`BWS<n>-T<k>`) are identical in both; splits carry letter suffixes.

**Consolidation reconciliation (no task lost or duplicated):**

| Workstream | Tasks in ws file | Rows in ROADMAP | Delta | Story points |
|---|---|---|---|---|
| BWS1 (ws1.md) | 15 | 15 | 0 | 68 |
| BWS2 (ws2.md) | 18 | 18 | 0 | 87 |
| BWS3 (ws3.md) | 17 | 18 | +1 (T13→T13a/T13b split, §7.3) | 102 |
| BWS4 (ws4.md) | 16 | 16 | 0 | 89 |
| BWS5 (ws5.md) | 17 | 17 | 0 | 88 |
| **Total** | **83** | **84** | **+1 documented split** | **434** |

Reconciles: **83 ws tasks → 84 ROADMAP rows**, the +1 being the single documented split (`BWS3-T13a`/`BWS3-T13b`); every original T-number appears exactly once (or as its two suffixed halves). No task dropped, none duplicated.
