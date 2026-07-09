# Early Phase Charter
## Intelligent Offer Optimization Bridge Layer for Credit Segmentation — Phase 1

**Source of truth:** `../early-phase-plan-credit-offer-optimization.md` (all IDs — P, A, H, O, D, E — refer to that document)
**Status:** Draft for sponsor and steering committee signature
**Duration:** 8–10 weeks (see `workplan.md`)

---

## 1. Purpose and objectives

The Early Phase exists to answer three questions with evidence, not assumptions (source: Executive Summary):

1. **Is the problem real and material?** Does under-classification actually occur at a scale and value that justifies investment? (Gates: E1, E2, E3)
2. **Is it addressable within constraints?** Can offers be optimized within existing risk appetite, regulatory boundaries, and model governance? (Gates: E4, E5, E6)
3. **Is the organization ready?** Will Risk, Compliance, and Model Governance accept an AI-assisted layer influencing offers? (Gates: E7, E8, E9)

Concretely, the phase must:

- Diagnose the **P1/P2/P3 mix** (misclassification vs. coarse segmentation vs. conservative offer mapping) — per source §1.1 this is "the single most important output of the Early Phase" (→ D1, E1).
- Disposition **all assumptions A1–A10** and test or explicitly schedule **all hypotheses H1–H14** (→ D4; KPI §8.1).
- Size and rank **opportunities O1–O8** on a risk-adjusted basis (→ D5, E3).
- Produce deliverables **D1–D11** and pass exit criteria **E1–E10**, ending in a minuted Go/No-Go decision (E10).

## 2. Scope

**In scope (Phase 1 only):** business understanding, discovery, current-state mapping, assumption/hypothesis validation, stakeholder engagement, data inventory and legal-basis work, risk-adjusted opportunity sizing, regulatory positioning, governance and accountability proposal, KPI definitions and baselines, Mid Phase charter drafting.

**Out of scope for Phase 1** — quoted from the source document's scope discipline:

> "This document deliberately excludes solution design, algorithms, models, and architecture. It covers business understanding, discovery, assumptions, and validation planning only."

No activity in this phase may produce solution designs, algorithm or model choices, product code, or system architecture. Hypothesis analyses are evidence analyses (e.g., H5 is explicitly "analysis of signal existence only — no model building").

**Out of scope for the bridge layer itself ("the layer shall never…" boundaries)** — quoted verbatim from source §4:

> "**Deliberately out of scope for the bridge layer:** re-scoring customers, overriding segments automatically, adjusting the engine's inputs, or auto-approving above-policy limits. Any of these would make the layer a de facto credit decision model and trigger the full regulatory weight the concept is designed to avoid."

These bright-line boundaries are stated here per the §6.2 "Silent scope creep" mitigation ("Define bright-line boundaries of the layer's authority in the charter") and are restated in D10 and D11. Any Phase 1 artifact that implies crossing them is defective and must be corrected.

## 3. Charter principles

1. **No-go is a valid outcome.** Quoted from source §10:
   > "the Early Phase is successful if it produces a *correct* decision — including 'the model is fine, invest in offer policy instead' or 'stop.' A phase that only ever recommends proceeding has failed as a discovery phase."
   This clause is the §6.1 mitigation for sunk-cost momentum (R-BUS-05) and is binding on every decision artifact (D5, D11, E10, steering pack).
2. **Evidence over assumption.** A1–A10 are "beliefs, not facts" (source §1.4) until dispositioned in D4.
3. **Falsifiability is honored.** Each hypothesis file carries its falsification condition verbatim; analyses are run to test, not to confirm. Thresholds (H2's X%, E1's materiality threshold and value floor, D9's tolerance band) are agreed with Risk **before** results are known, to prevent goal-seeking.
4. **Right-sizing, not maximizing.** Per §6.1 (overshoot risk): the objective is the right offer, with affordability as a hard constraint in all sizing.
5. **Data minimization.** Per §7 rule: every Useful/Optional data item must carry a stated hypothesis; data with no hypothesis attached is not collected.
6. **Shared metric discipline.** Per §3: Business and Risk have structurally opposed near-term metrics; the phase must produce a shared risk-adjusted metric both sign (D9, E7), or the project stalls.

## 4. Governance

| Body | Composition | Cadence | Authority |
|---|---|---|---|
| **Program Sponsor** | Executive sponsor — name TODO (see OQ-23) | Weekly check-in | Charter owner; resolves escalations (incl. E7 deadlock); signs D3 |
| **Steering Committee** | Joint Risk–Business chairs + Compliance, Finance, Model Risk, Product; composition TODO (OQ-23). Joint Risk–Business membership is mandated by §6.1 (deadlock mitigation) | Kickoff, mid-point (~week 5), Go/No-Go (~week 10) | Decides E10: proceed / pivot / stop — minuted |
| **Working group** | Product, Data Science, Risk Advisory, Bank SMEs | Weekly | Runs workplan; maintains open-questions log and risk register |

## 5. Decision rights

| Decision | Decided by | Consulted | Gate |
|---|---|---|---|
| Ground-truth definition ("deserved segment / right-sized offer") | Credit Risk (signs) | Model Risk, Data Science, Finance | E2 |
| Analysis thresholds (H2 "X%", E1 materiality threshold and value floor, risk-stability tolerance band) | Risk (+ Steering Committee for the value floor) — pre-registered before analyses run | Data Science, Finance, Business | E1, E7 |
| Data access & legal-basis disposition | CDO / Data Office with Compliance | Data Science, IT | E5 |
| Layer legal classification | Chief Compliance Officer (signs D7) | Model Risk, external counsel as needed | E4 |
| Fairness audit execution or formal block | Compliance (protocol), Executives (residual-risk acceptance if blocked) | Risk, Data Science | E9 |
| Governance & accountability model | Model Risk + Internal Audit (accept D10 in principle) | Risk, Business, Compliance | E8 |
| KPI book incl. tolerance band | Risk + Business joint signature; deadlock escalates to Sponsor | Finance, Data Science, Compliance | E7 |
| Go/No-Go | Steering Committee, rationale minuted | All | E10 |
| Scope change to Phase 1 | Sponsor via change control | Working group | — Any change expanding into solution design is auto-rejected |

## 6. Deliverables and owners (per source §9)

D1 Problem Definition & Diagnosis (Product + Data Science → Risk + Business) · D2 Current-State Decision Flow Map (Product + Bank SMEs → Risk + IT) · D3 Stakeholder Analysis & Engagement Log (Product → Sponsor) · D4 Assumption & Hypothesis Validation Report (Data Science → Risk) · D5 Opportunity Assessment & Prioritization (Product + Finance → Executives) · D6 Risk Register (Product + Risk → CRO office) · D7 Regulatory & Legal Position Paper (Compliance/Legal → CCO) · D8 Data Inventory & Access Disposition (Data Science + Data Office → CDO) · D9 Success Metrics & Baseline Book (Product + Finance → Risk + Business joint) · D10 Governance & Accountability Proposal (Product + Risk → Model Risk + Audit) · D11 Mid Phase Charter draft (Product → Steering Committee).

Templates: `../04-deliverables/`. Accountability detail: `raci.md`.

## 7. Phase KPIs (source §8.1 — measuring the planning phase itself)

| KPI | Target |
|---|---|
| Assumptions A1–A10 dispositioned (validated / falsified / deferred with reason) | 100% |
| Hypotheses H1–H14 tested or explicitly scheduled with data dependencies | ≥ 10 tested, remainder scheduled |
| P1/P2/P3 problem mix quantified | Quantified with Risk sign-off |
| Opportunity value sized risk-adjusted, with ranges | Board-presentable sizing document |
| Mandatory data categories confirmed available + legally usable | 100% dispositioned (available / blocked / conditional) |
| Stakeholder interviews completed across all mapped groups | 100% of groups, incl. front line and Model Risk |
| Legal/Compliance opinion on layer classification obtained | Written opinion delivered |
| Shared Risk–Business success metric agreed and signed | Signed one-pager |

## 8. Signature block

| Role | Name | Date | Signature |
|---|---|---|---|
| Program Sponsor | TODO | | |
| Steering Committee co-chair (Risk) | TODO | | |
| Steering Committee co-chair (Business) | TODO | | |
| Engagement Lead | TODO | | |
