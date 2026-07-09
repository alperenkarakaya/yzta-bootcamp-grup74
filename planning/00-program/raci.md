# RACI Matrix — Early Phase Deliverables D1–D11
**Source basis:** owners and sign-offs from source §9; stakeholder set from source §3 (all groups covered, incl. Model Risk, Front line, Internal Audit).

## Legend and conventions

- **R** Responsible (does the work) · **A** Accountable (sign-off authority) · **C** Consulted · **I** Informed.
- Where the source names a **joint sign-off** (e.g., D1 "Risk + Business", D9 joint, D10 "Model Risk + Audit"), both parties hold **A jointly** — a deliberate deviation from single-A convention, required by the source document. Deadlocks escalate to the Sponsor (charter §5).
- **Customers** are engaged only through governed research with consent (never as project members). The **Regulator** is external and indirect (source §3); it is never engaged directly except optional informal dialogue via Compliance per H13.
- Finance, IT/Bank SMEs, and the CRO office are not rows in the §3 stakeholder map but are named owners/sign-offs in §9 — included here; confirmation of representatives is tracked as OQ-14 / OQ-15.

**Column codes:** SP Sponsor · SC Steering Committee · PRD Product · DS Data Science · CR Credit Risk · MR Model Risk/Validation · BUS Business/Commercial · CL Compliance/Legal (A on D7 = Chief Compliance Officer) · FIN Finance · DO Data Office (A on D8 = CDO) · IT IT & engine SMEs · FL Customer Service/Front line · IA Internal Audit · EXE Executives (CEO/CFO/CRO/CBO) · CRO CRO office · CUS Customer · REG Regulator (indirect).

## Matrix

| # | Deliverable (source §9) | SP | SC | PRD | DS | CR | MR | BUS | CL | FIN | DO | IT | FL | IA | EXE | CRO | CUS | REG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | Problem Definition & Diagnosis Report | I | I | **R** | **R** | **A** | C | **A** | I | C | I | I | C | I | I | I | — | — |
| D2 | Current-State Decision Flow Map | I | I | **R** | C | **A** | C | I | C | I | I | **R/A** | C | I | I | I | — | — |
| D3 | Stakeholder Analysis & Engagement Log | **A** | I | **R** | C | C | C | C | C | C | C | C | C | C | C | I | C | — |
| D4 | Assumption & Hypothesis Validation Report | I | I | C | **R** | **A** | C | I | C | C | I | I | I | I | I | I | — | — |
| D5 | Opportunity Assessment & Prioritization | I | I | **R** | C | C | I | C | C | **R** | I | I | I | I | **A** | C | — | — |
| D6 | Risk Register | I | I | **R** | C | **R** | C | C | C | C | C | C | C | C | I | **A** | — | — |
| D7 | Regulatory & Legal Position Paper | I | I | C | C | C | C | I | **R/A** | I | C | I | I | I | I | I | — | I* |
| D8 | Data Inventory & Access Disposition | I | I | C | **R** | C | I | I | C | I | **R/A** | C | I | I | I | I | — | — |
| D9 | Success Metrics & Baseline Book | I | I | **R** | C | **A** | C | **A** | C | **R** | I | I | C | I | C | I | C | — |
| D10 | Governance & Accountability Proposal | I | I | **R** | C | **R** | **A** | C | C | I | I | C | C | **A** | I | C | — | — |
| D11 | Mid Phase Charter (draft) | C | **A** | **R** | C | C | C | C | C | C | I | I | I | I | I† | I | — | — |

\* REG "Informed" on D7 only if the bank pursues the optional informal regulator dialogue per H13 — via CL, never directly.
† Executives are represented within the Steering Committee for the D11/E10 decision.

**Row notes (why the C/I placements):**

- **D1:** FL consulted for complaint-side materiality (M8/H9); MR consulted so the diagnostic method (ground truth, backtests) is defensible under model-risk scrutiny; FIN consulted on value framing.
- **D2:** IT/Bank SMEs are co-owner (source: "Product + Bank SMEs") and joint sign-off with Risk (source: "Risk + IT"); CL consulted on vendor-contract findings (Q7, R-OPS-04); FL consulted on the offer-delivery step (§2.1 step 8).
- **D3:** every mapped stakeholder group is C by definition (they are the interview subjects), including CUS via governed research.
- **D4:** CR is A "for analytical rigor" (source wording); MR consulted on method; CL consulted on the H14 protocol; FIN on H6.
- **D5:** joint R Product + Finance per source; CR consulted for risk costs and appetite constraints (A5); CL provides per-opportunity legal viability flags from D7; CRO office consulted pre-steering. Template preserves "no-go is a valid outcome."
- **D6:** register co-built by PRD + CR (source owners), signed by CRO office; every function is C on its own risk entries.
- **D7:** R and A within Compliance/Legal; A specifically the Chief Compliance Officer per source.
- **D8:** joint R Data Science + Data Office; A = CDO "or equivalent" per source.
- **D9:** joint A Risk + Business is the E7 gate itself; FL and CUS consulted for trust/NPS baselines (§8.2); CL consulted on fairness indicators.
- **D10:** joint A Model Risk + Audit is the E8 gate; CR co-responsible per source ("Product + Risk").
- **D11:** A = Steering Committee (E10); Sponsor consulted in drafting, decision minuted per gate template.

## Key activities beyond D1–D11

| Activity | SP | SC | PRD | DS | CR | MR | BUS | CL | FIN | DO | IT | FL | IA | EXE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ground-truth workshop & signature (A2 → E2) | I | I | C | **R** | **R/A** | C | I | I | C | I | I | — | I | I |
| Threshold pre-registration (H2 X%, E1 floor, D9 band) | I | **A** (value floor) | C | **R** | **A** | C | C | I | C | — | — | — | I | I |
| Fairness audit clearance & execution (H14 → E9) | I | I | C | **R** | C | C | I | **R/A** (protocol) | I | C | I | — | I | **A** (residual-risk acceptance if blocked) |
| Go/No-Go decision (E10) | C | **A** | **R** (pack) | C | C | C | C | C | C | I | I | I | I | C |
