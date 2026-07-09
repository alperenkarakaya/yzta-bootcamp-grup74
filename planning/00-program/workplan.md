# Early Phase Workplan — Week-by-Week
**Expands:** source Appendix A (indicative 8–10 weeks) into an execution plan.
**Role codes:** SP Sponsor · SC Steering Committee · EL Engagement Lead · PRD Product · DS Data Science · CR Credit Risk · MR Model Risk/Validation · BUS Business/Commercial · CL Compliance/Legal · FIN Finance · DO Data Office/CDO · IT IT & engine SMEs · FL Front line/Customer Service · IA Internal Audit · EXE Executives · CUS Customers (governed research only).
**Data item codes:** M1–M9 / U1–U8 / OPT1–OPT5 per `../03-data/data-inventory-tracker.md`.

## 1. Workstreams (from Appendix A, verbatim mapping)

| WS | Name (Appendix A) | Weeks | Primary outputs | Gates served |
|---|---|---|---|---|
| WS1 | Mobilize & map | 1–2 | Charter signed; interviews launched; D2 walkthrough started; data requests issued | E2 (setup), E5 (setup), E6 |
| WS2 | Legal & governance track (parallel) | 2–4 | H13 opinion commissioned; jurisdiction scan; data legal bases; governance pre-alignment (H12) | E4, E8, E9 (setup) |
| WS3 | Evidence track | 3–6 | H1–H8 backtests/cohort analyses; H9–H11 complaint/NPS/attrition analyses | E1, E2 (consumes) |
| WS4 | Sizing & synthesis | 5–7 | P1/P2/P3 quantification (D1); risk-adjusted sizing O1–O8 (D5); fairness audit (H14) | E1, E3, E9 |
| WS5 | Alignment | 7–8 | KPI book negotiation (D9); risk register review (D6); governance proposal (D10) | E7, E8 |
| WS6 | Close | 8–10 | Deliverable finalization; steering committee; Go/No-Go | E10 |

## 2. Week-by-week plan

| Wk | WS | Activity | Owner (role) | Inputs | Outputs | Depends on |
|---|---|---|---|---|---|---|
| 1 | WS1 | Kickoff; charter review; confirm sponsor, SteerCo composition (OQ-23) | EL, SP | Charter draft | Signed charter; governance calendar | — |
| 1 | WS1 | Issue Appendix B questions to bank (OQ-01…OQ-10); open the open-questions log | EL, PRD | `open-questions.md` | Assigned owners + due dates per question | Kickoff |
| 1 | WS1 | Issue data request pack to Data Office (M1–M9 gating; U-tier; OPT5 flagged conditional) | DS, DO | `../03-data/data-request-pack.md` | Acknowledged request; ETA per item | Kickoff |
| 1 | WS1 | Schedule all stakeholder interviews (11 groups) + D2 walkthrough sessions | PRD | `../02-stakeholders/` guides | Interview calendar | Kickoff |
| 1 | WS2 | Brief Compliance/Legal on H13 opinion need; commission counsel; confirm jurisdiction set (OQ-17) | CL, EL | Source §5 H13, §6.3 | Opinion terms of reference | Kickoff |
| 2 | WS1 | Interviews wave 1: Credit Risk, Business, Front line | PRD, EL | Guides | Interview notes → D3 log | Calendar |
| 2 | WS1 | Ground-truth workshop #1 with Risk (A2): candidate definitions of "deserved segment" | DS, CR | M7 policy docs; source §1.4 A2, §6.2 | Candidate ground-truth conventions + limits documented | M7 received |
| 2 | WS1 | D2 decision-flow walkthrough sessions (steps 1–9 per source §2.1); vendor contract review starts (OQ-24, Q7) | PRD, IT, CL | System docs; vendor contracts | Draft flow map; contract findings | Session scheduling |
| 2 | WS2 | Jurisdiction scan starts; data legal-basis mapping method agreed | CL | Tracker categories | Scan checklist; legal-basis column plan | ToR |
| 3 | WS1 | Interviews wave 2: Model Risk, Compliance, Internal Audit, Data Science, Product | PRD, EL | Guides | Notes → D3; H12 early signals | Calendar |
| 3 | WS3 | First data deliveries (target: M1–M6); quality profiling; tracker statuses updated | DS, DO | Data request pack | Tracker: exists/accessible/quality per item | Wk1 request |
| 3 | WS3 | Complaint taxonomy analysis starts (H9, uses M8); protocol pre-registration for H1–H4 with Risk (cohorts + thresholds) | DS, CR | M8; h01–h04 protocols | Signed analysis protocols; taxonomy draft | GT workshop #1 |
| 4 | WS1 | **Ground truth signed by Risk (E2)**; thresholds pre-registered (H2 X%, E1 materiality/value floor with SC) | CR, SC | Workshop outputs | Signed ground-truth convention (feeds D1, D4, D9) | Workshop #1–2 |
| 4 | WS3 | H1 boundary backtest + H2 vintage analysis run | DS | M1, M2, M4, M5, U6, M7 | Preliminary H1/H2 results | E2; M-data delivered |
| 4 | WS2 | Governance pre-alignment session with MR (H12 prep); mock-review format agreed | PRD, MR | h12 protocol | Mock governance review plan | Wave 2 interviews |
| 4 | WS2 | Customer research clearance: consent route, recruitment, incentives (OQ-20) | CL, PRD | Customer guide | Approved research protocol | Compliance interview |
| 5 | WS3 | H3 thin-file cohorts; H4 override analysis; H8 re-scoring cadence replay spec (OQ-25) | DS | M1, M5, M6, M4, U6 | Preliminary H3/H4 results; H8 spec | E2; M-data |
| 5 | WS3 | H5 within-segment signal-existence analysis (if U1 available); H7 campaign analysis (U3, U2); H11 attrition (U4) | DS | U1, U2, U3, U4, M1, M4 | Preliminary H5/H7/H11 results or "scheduled" status | U-data delivery |
| 5 | WS4 | H6 joint sizing kickoff with Finance + Risk (RAROC method agreed) | FIN, CR, DS | M9, U8, M3, M7 | Sizing method note (feeds D5) | M9 delivered |
| 5 | WS2 | Fairness audit legal decision: OPT5 access approved under governed protocol, or formally blocked (E9 path) | CL, EXE | `../05-risk-and-compliance/regulatory-workplan.md` | Go/blocked decision for H14 | Legal-basis mapping |
| 5 | — | **Mid-point steering check** (early warning on E1 direction; no-go remains a valid outcome) | SC, EL | Preliminary evidence | Steer notes; threshold confirmations | Prelim H1–H4 |
| 6 | WS3 | Evidence track first pass closes: H1–H8 results consolidated; H9 complaint/NPS analysis done; H10 concept tests run (CUS, FL); H11 done | DS, PRD | All above | Evidence pack for D1/D4 | Wks 4–5 analyses |
| 6 | WS4 | H14 fairness audit executed under governed protocol (if cleared wk5) | DS, CL | M1, M4, OPT5 | Fairness findings (feeds D7, D9, E9) | Wk5 clearance |
| 6 | WS2 | Draft H13 legal opinion received; implications mapped to O1–O8 viability | CL, PRD | Opinion draft | Per-opportunity legal viability flags (feeds D5, E4) | Wk1 ToR |
| 7 | WS4 | P1/P2/P3 quantification with Risk review (D1 core) | DS, PRD, CR | H1–H8 + H9 evidence | D1 draft incl. quantified mix | Wk6 evidence |
| 7 | WS4 | Opportunity sizing O1–O8: population × value per customer × risk cost; downside scenarios; per-segment win-win test (A10); affordability constraint applied | PRD, FIN, CR | D1 draft; H5–H8, H11 results; legal flags | D5 draft with ranking + MVP candidate scope (scope only) | D1 draft; H6 method |
| 7 | WS5 | D9 KPI book drafting: shared metric one-pager, product KPI definitions + baselines (§8.2); D10 governance proposal draft; risk register review workshop (D6) | PRD, FIN, CR, BUS | Evidence pack; `../05-risk-and-compliance/risk-register.md` | D9/D10/D6 drafts | Wk6 evidence |
| 8 | WS5 | KPI negotiation sessions Risk + Business → joint signature (**E7**); escalate to SP if deadlocked | CR, BUS, SP | D9 draft | Signed KPI book incl. tolerance band | D9 draft |
| 8 | WS5 | D10 review with MR + IA → acceptance in principle (**E8**) | MR, IA, PRD | D10 draft | Accepted governance proposal | D10 draft; H12 |
| 8 | WS6 | D7 finalized + CCO signature (**E4**; fairness position → **E9**); D8 disposition complete (**E5**); D2 finalized (**E6**); D3 finalized; D4 compiled | CL, DS, DO, PRD | All track outputs | Signed D7; D8 100% dispositioned; D2 with ≥1 viable insertion point or documented absence | Tracks close |
| 9 | WS6 | Steering pack assembly (per `../06-gates/steering-committee-pack-outline.md`); D11 draft charter with proceed/pivot/stop options; pre-wire with CRO office and EXE | EL, PRD | D1–D10 | Steering pack + D11 draft | Wk8 closures |
| 9 | — | Buffer / remediation: close gate shortfalls (E1–E9), re-run contested analyses, finish "scheduled" hypotheses documentation | All | Gate checklist | Gate checklist statuses | Wk8 review |
| 10 | WS6 | **Steering committee: Go/No-Go (E10)** — decision minuted (proceed / pivot / stop); close-out, lessons, archive or handover | SC, SP, EL | Steering pack | Minuted decision per E10 template | Full pack |

Weeks 9–10 are the source's 8–10 week flexibility band: the plan targets substance-complete at week 8; the buffer absorbs data-delivery slips and negotiation cycles without moving E10.

## 3. Inter-workstream dependencies

- **E2 gates the evidence track's acceptance:** H1–H4 can be *prepared* before ground truth is signed, but per E2 "analyses are not accepted" without it. Protocol pre-registration (wk3) and signature (wk4) sit immediately before the H1/H2 runs.
- **Data gates everything analytical:** M1–M6 (wk3 delivery) gate H1–H4, H8; M8 gates H9; M9+U8 gate H6; U1/U2/U3/U4 gate H5/H7/H11. Any Mandatory-item slip consumes the wk9 buffer first, then triggers E5's consequence ("Phase extended; Mid Phase not started on hoped-for data").
- **Legal track feeds sizing:** the H13 draft opinion (wk6) supplies per-opportunity viability flags consumed by D5 (wk7). A negative draft narrows D5 to compliant opportunities (E4 consequence) rather than stopping the plan.
- **OPT5 clearance gates H14:** blocked path is legitimate but must be formally documented with executive acceptance of residual risk (E9).
- **Evidence gates alignment:** D9 baselines (§8.2 discipline: "A KPI without a baseline is a story, not a metric") come from H9/H10/H14 and the evidence pack — D9 negotiation cannot start before week 7.
- **Everything gates E10:** the steering pack requires D1–D10 substantially complete and E1–E9 statuses known.

## 4. Critical path analysis (activities → exit criteria)

**Critical path (zero slack):**
Kickoff (wk1) → data request issued (wk1) → M1–M6 delivered (wk3) → ground truth signed **E2** (wk4) → H1–H4 backtests (wk4–6) → P1/P2/P3 quantification, D1 (wk7) → risk-adjusted sizing, D5 (wk7–8) → **E1/E3** evidence → KPI negotiation **E7** (wk8) → steering pack (wk9) → **E10** (wk10).

Two single points of failure on this path: **Mandatory data delivery** (wk3) and **ground-truth signature** (wk4). Both get named owners on day 1 and weekly sponsor visibility.

**Parallel paths and their slack:**

| Path | Activities | Gates | Slack |
|---|---|---|---|
| Legal | ToR wk1 → jurisdiction scan wk2–4 → draft opinion wk6 → D7 signed wk8 | E4 | ~2 wks vs. E10, **but zero** if the draft trends negative (rescope loop into D5 needed before wk7 sizing) |
| Fairness | Legal-basis mapping wk2–4 → OPT5 decision wk5 → audit wk6 → position in D7 wk8 | E9 | 1–2 wks; blocked path is faster but needs EXE acceptance |
| Insertion feasibility | D2 walkthrough wk2–4 → contract findings → D2 final wk8 | E6 | ~3 wks; pull earlier if R-OPS-01/R-OPS-04 triggers fire — a "no viable insertion point" finding should reach SC at the wk5 mid-point, not wk10 |
| Governance | H12 interviews wk3 → mock review wk4–6 → D10 wk7–8 | E8 | ~1 wk; MR calendar is the constraint |
| Customer/qualitative | Clearance wk4 → interviews + concept tests wk5–6 → D9 baselines wk7 | E7 (baselines) | ~1 wk; recruitment is the constraint (OQ-20) |

**Gate-to-activity map:**

| Gate | Gated by (critical inputs) | Earliest credible week |
|---|---|---|
| E1 | E2 + H1–H4 (+H6/H8 for P2/P3 value floor) → D1 | 7 |
| E2 | Ground-truth workshops + M7 + Risk signature | 4 |
| E3 | D5 sizing reviewed by FIN + CR, incl. downside | 8 |
| E4 | H13 written opinion → D7 signed by CCO | 8 |
| E5 | 100% of M1–M9 dispositioned in D8 | 8 |
| E6 | D2 walkthrough finds ≥1 viable, vendor-compliant insertion point | 8 |
| E7 | D9 joint signature incl. risk-stability tolerance band | 8 |
| E8 | D10 accepted in principle by MR + IA | 8 |
| E9 | H14 executed, or formally blocked + documented + EXE acceptance | 8 |
| E10 | All above + steering pack + D11 → minuted decision | 10 |

## 5. Milestones

| MS | Week | Milestone | Evidence |
|---|---|---|---|
| MS1 | 1 | Charter signed; data requests issued; Appendix B questions assigned | Charter signature block; DO acknowledgment |
| MS2 | 3 | Mandatory data first delivery; interview coverage ≥ 60% | Tracker statuses; D3 log |
| MS3 | 4 | **E2 met** — ground truth signed; thresholds pre-registered | Signed convention |
| MS4 | 6 | Evidence first pass complete (H1–H11 tested or formally "scheduled") | Evidence pack |
| MS5 | 8 | E4–E9 substantially met; D1–D10 in review | Gate checklist |
| MS6 | 10 | **E10 decision minuted** (proceed / pivot / stop — no-go is a valid outcome) | E10 minutes per `../06-gates/exit-criteria-checklist.md` |
