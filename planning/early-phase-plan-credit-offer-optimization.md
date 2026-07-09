# Early Phase Plan
## Intelligent Offer Optimization Bridge Layer for Credit Segmentation

**Document type:** Phase 1 (Early Phase) Planning & Discovery Document
**Prepared by:** AI Solution Architecture / Product Strategy / Credit Risk Advisory
**Status:** Draft for stakeholder review
**Scope discipline:** This document deliberately excludes solution design, algorithms, models, and architecture. It covers business understanding, discovery, assumptions, and validation planning only.

---

## Executive Summary

The bank's credit decision engine is believed to systematically assign a meaningful share of customers to lower-than-optimal credit segments. The consequence is a dual loss: customers receive weaker offers than their true risk profile justifies (dissatisfaction, attrition, competitor switching), and the bank under-lends relative to its risk appetite (foregone interest income, lower share of wallet).

The proposed product concept is a **bridge layer** that sits between the existing decision engine and the final customer offer, optimizing the offer within bank risk policy — **without replacing or overriding the bank's scoring model**.

Before any solution work begins, the Early Phase must answer three questions:

1. **Is the problem real and material?** Does under-classification actually occur at a scale and value that justifies investment?
2. **Is it addressable within constraints?** Can offers be optimized within existing risk appetite, regulatory boundaries, and model governance?
3. **Is the organization ready?** Will Risk, Compliance, and Model Governance accept an AI-assisted layer influencing offers?

Everything below is structured to answer these three questions with evidence, not assumptions.

---

## 1. Problem Definition

### 1.1 The Real Business Problem

The surface framing is "customers get lower segments than they deserve." The underlying business problem is more precise:

> **The bank's decision engine converts a continuous risk reality into coarse segments, and the offer logic attached to those segments is conservative by design. The combined effect is a systematic gap between the offer a customer receives and the offer the bank could profitably and safely extend.**

This decomposes into three distinct sub-problems that must be kept separate, because they have different owners, different evidence, and different fixes:

| # | Sub-problem | Nature | Owner today |
|---|---|---|---|
| P1 | **Misclassification** — the engine places a customer in the wrong segment relative to their true risk | Model accuracy / calibration issue | Credit Risk / Model Validation |
| P2 | **Coarse segmentation** — even correctly classified customers near segment boundaries get the same offer as much riskier peers in the same segment | Segmentation design issue | Credit Risk Policy |
| P3 | **Conservative offer mapping** — the offer assigned per segment is below what risk appetite would permit | Commercial policy issue | Business / Product |

> **Critical framing challenge:** The brief assumes the problem is P1 (misclassification). It is entirely possible — and in mature banks, common — that the model is well-calibrated and the real problem is P2 and P3. The bridge layer value proposition differs materially depending on which sub-problem dominates. **Diagnosing the mix of P1/P2/P3 is the single most important output of the Early Phase.**

### 1.2 Why Does It Happen? (Candidate Root Causes)

| Category | Candidate root cause | Evidence needed to confirm |
|---|---|---|
| Model design | Scoring model optimized for default discrimination, not offer optimization; trained to minimize bad debt, not maximize risk-adjusted revenue | Model documentation, objective function, validation reports |
| Data limitations | Thin-file customers (young, new-to-bank, gig economy) lack traditional bureau data → default to conservative segment | Segment composition analysis by data-richness |
| Stale data | Scores based on outdated snapshots; customer circumstances improved since last assessment | Score refresh frequency, vintage analysis |
| Segment granularity | Few, wide segments; boundary customers penalized | Score distribution vs. segment cut-offs |
| Policy conservatism | Cut-offs and limits set during a past crisis or under old capital constraints, never recalibrated | Policy change history, cut-off rationale docs |
| Asymmetric error costs | Institutional culture punishes over-lending errors visibly (write-offs) but under-lending losses are invisible (no line item for foregone revenue) | Interviews; incentive/KPI review |
| Override behavior | Manual overrides skew conservative; officers face no cost for downgrading | Override logs and outcomes |
| Regulatory buffer stacking | Multiple teams each add a "safety margin," compounding conservatism | End-to-end decision flow walkthrough |

### 1.3 Who Is Impacted?

| Impacted party | How |
|---|---|
| **Customers** (esp. near-boundary, thin-file, improving-profile) | Lower limits, worse pricing, weaker product access; perceived unfairness; churn |
| **Bank revenue lines** | Foregone interest income, lower utilization, lost cross-sell |
| **Relationship managers / branches** | Handle complaints, escalate exceptions, lose sales they sourced |
| **Credit Risk team** | Reputational tension — accused of being a "growth blocker" without data to defend or adjust |
| **Bank competitively** | Under-served good customers are exactly the ones competitors and fintechs poach with pre-approved offers |
| **Society/regulator lens** | If under-classification correlates with protected attributes, it is a fair-lending exposure even though no one is rejected |

### 1.4 Assumptions Requiring Validation

These are currently **beliefs, not facts**. Each must be tested before Mid Phase.

| # | Assumption (as stated or implied in the brief) | Challenge / risk if wrong | Validation method |
|---|---|---|---|
| A1 | Under-classification is systematic and material (not random noise) | If the model is well-calibrated, the bridge layer has no misclassification to fix — value case collapses to P2/P3 | Backtest: compare assigned segments vs. realized default outcomes by cohort |
| A2 | "Deserved segment" is objectively definable | Without an agreed ground-truth definition, "under-classification" is unmeasurable | Workshop with Risk to define ground truth (e.g., realized PD vs. segment PD band) |
| A3 | Customer dissatisfaction is driven by segment/limit outcomes | Dissatisfaction may stem from communication, process speed, or opacity — not the offer amount | Complaint taxonomy analysis; NPS verbatims; customer interviews |
| A4 | The bank loses net revenue by under-lending | Higher limits also raise expected loss, capital consumption, and funding cost; net effect may be smaller than gross | Risk-adjusted revenue analysis (RAROC-style, at business level, not model level) |
| A5 | Risk appetite has genuine headroom to lend more | If the bank is at its capital/appetite ceiling, no optimization is permissible | Review risk appetite statement, capital and provisioning constraints with CRO office |
| A6 | A bridge layer can influence offers without constituting a "credit decision model" in regulatory terms | Regulators may classify any offer-influencing logic as part of the decisioning system, triggering full model governance | Early Compliance & Model Risk consultation (see Risks §6) |
| A7 | Additional data signals exist, are accessible, and are permissible for offer optimization | Data may exist but be barred by consent, purpose limitation (GDPR/local equivalents), or bureau contracts | Data inventory + legal basis review (§7) |
| A8 | The existing engine's output can be intercepted before the offer is finalized | Some engines are hard-coded end-to-end; no insertion point exists without core change | Technical walkthrough of decision flow (current-state analysis §2) |
| A9 | Stakeholders will trust AI-assisted offer adjustments | Risk teams may veto anything that "second-guesses" their model | Stakeholder interviews; governance pre-alignment |
| A10 | The lose-lose framing is symmetric — fixing it helps both sides | Some fixes help revenue but raise portfolio risk; "win-win" must be proven per segment, not asserted | Scenario analysis in opportunity assessment (§4) |

---

## 2. Current State Analysis

*(To be completed with bank inputs; the structure below defines what Early Phase discovery must document.)*

### 2.1 Existing Decision Flow (to be mapped)

A full end-to-end walkthrough must produce a documented flow covering:

1. **Application / trigger** — new application, limit review, campaign pre-approval, periodic re-scoring
2. **Data assembly** — internal data, bureau pull, income verification
3. **Scoring** — score generation by the decision engine (frequency, inputs, version)
4. **Segmentation** — score-to-segment mapping (cut-offs, who owns them, how often reviewed)
5. **Policy rules** — knock-out rules, exposure caps, product eligibility overlays
6. **Offer assignment** — segment-to-offer mapping (limit, pricing, product tier)
7. **Manual review / overrides** — when triggered, by whom, with what authority
8. **Offer delivery** — channel, wording, explanation given to customer
9. **Feedback loop** — whether outcomes (utilization, delinquency, complaints, attrition) feed back into any of the above — and if so, with what lag

**Key discovery questions per step:** Who owns it? What system executes it? How often does it change? Where is discretion applied? Where could a bridge layer legally and technically insert?

### 2.2 Existing Classification Process (to be documented)

- Number of segments and rationale for their boundaries
- Population distribution across segments and density near boundaries
- Refresh cadence (real-time, monthly batch, annual review?)
- Historical stability: how often do customers migrate segments, and in which direction?
- Override rates and direction (upgrade vs. downgrade)
- Whether "deserved segment" has ever been retro-analyzed against realized outcomes

### 2.3 Pain Points (hypothesized — to be evidenced in interviews)

| Pain point | Felt by | Evidence to collect |
|---|---|---|
| Boundary customers treated identically to worst-in-segment | Customer, Business | Score distribution vs. offer table |
| No mechanism to lift a good customer without full re-underwrite | RM/Branch, Business | Exception request volumes and turnaround times |
| No measurement of under-lending cost | Executives, Finance | Absence of a "foregone revenue" metric anywhere in MI |
| Complaints about limits with no explainable answer | Customer service | Complaint logs tagged to credit limits |
| Risk team blamed for growth drag without shared data | Risk | Interview themes |
| Slow policy change cycle (cut-offs revisited rarely) | All | Policy governance calendar |

### 2.4 Known Limitations (structural)

- Scoring model is a regulated, validated asset — cannot be casually modified (this is precisely why a bridge layer is proposed, but it also constrains what the bridge may touch)
- Segment cut-offs may be embedded in downstream systems (pricing engines, collections strategies, capital models) — changing effective offers may ripple further than expected
- Historical data on "what would have happened with a better offer" does not exist (counterfactual problem) — this will constrain how any future value claims can be validated
- Decision engine vendor contracts may restrict interception or augmentation of outputs

---

## 3. Stakeholder Mapping

| Stakeholder | Goals | Concerns | Success Metrics (from their seat) |
|---|---|---|---|
| **Customer** | Fair offer matching their real profile; transparency; fast decisions | Opaque decisions; feeling penalized despite good behavior; data privacy ("what are you using about me?") | Higher/right-sized limit; understandable rationale; no new friction |
| **Credit Risk Team** | Portfolio loss within appetite; model integrity; defensible decisions | Bridge layer erodes their model's authority; risk creep via "optimized" offers; accountability if losses rise ("whose decision was it?") | Stable/predicted default rates; no breach of risk appetite; clear governance over the layer |
| **Model Risk / Validation** *(often merged with Risk but distinct — added deliberately)* | Every model in production is validated, monitored, documented | An unvalidated AI layer influencing credit outcomes; scope creep from "advisory" to "decisioning" | Bridge layer classified, documented, and validated per model risk policy before go-live |
| **Business / Commercial Team** | Revenue growth, utilization, cross-sell, competitive offers | Slow governance killing the initiative; solution too constrained to move numbers | Approved credit volume uplift; utilization; revenue per customer |
| **Compliance / Legal** | Fair lending, responsible lending, data protection, explainability obligations | Disparate impact from AI adjustments; use of data beyond consented purpose; inability to explain adverse-relative outcomes; regulator perception | Zero regulatory findings; documented legal basis for every data element; explainability standard met |
| **Data Science Team** | Meaningful problem, access to data, freedom to explore signals | Being handed an unsolvable brief (no ground truth); data access blocked; governance treating exploration as production | Validated hypotheses; approved data access; clear problem definition |
| **Product Team** | A shippable product with clear value narrative; scalability beyond one bank | Over-customization to one bank's quirks; unclear ownership between product and risk logic | Defined MVP scope; documented requirements; stakeholder sign-off |
| **Executives (CEO/CFO/CRO/CBO)** | Profitable growth within risk appetite; strategic differentiation; no headline risk | Reputational damage from "AI decides your credit" stories; investment without measurable return; internal conflict between Risk and Business | Risk-adjusted revenue uplift; NPS movement; cost of the program vs. quantified opportunity |
| **Customer Service / Front Line** *(added — brief omitted them)* | Fewer complaint escalations; ability to explain outcomes | New layer makes explanations harder ("the AI adjusted it") | Complaint volume on limits; first-contact resolution |
| **Internal Audit** *(added)* | Auditable, controlled processes | Untracked overrides; unclear decision lineage | Complete audit trail of every offer adjustment |
| **Regulator (external, indirect)** *(added)* | Consumer protection, financial stability, model governance | AI opacity; discrimination; responsible lending breaches (over-lending is also a regulatory issue — the fix must not overshoot) | N/A — but their expectations shape every internal metric |

> **Tension to manage explicitly:** Business and Risk have structurally opposed near-term metrics. The Early Phase must produce a **shared metric** (risk-adjusted value, not raw volume) that both sign, or the project will stall at Mid Phase regardless of technical merit.

---

## 4. Opportunity Assessment

Where could a bridge layer create value **without replacing the bank's model**? The engine's segment remains the anchor; the layer only optimizes the offer *within* policy. Candidate value pools, ordered by likely governance friction (low → high):

| # | Opportunity | Description | Value mechanism | Governance friction |
|---|---|---|---|---|
| O1 | **Within-segment offer differentiation** | Customers in the same segment receive differentiated offers (within the segment's approved limit/pricing range) based on additional insight | Captures value from coarse segmentation (P2) without touching classification | Low — segment and its risk bounds are respected |
| O2 | **Boundary-case flagging for review** | Layer identifies customers near segment boundaries whose supplementary signals suggest upgrade potential; routes to existing human review with an evidence pack | Converts invisible under-classification into a managed exception process using authority that already exists | Low–medium — human remains decision-maker |
| O3 | **Offer timing & refresh optimization** | Identify customers whose profile has improved since last scoring and trigger a re-score/limit review earlier than the standard cycle | Fixes stale-data under-classification (P1 subset) using the bank's own model, just invoked at a better time | Low — no new decision logic, only scheduling |
| O4 | **Offer explanation & transparency layer** | Generate customer-facing and staff-facing explanations of the offer and the path to improvement | Addresses satisfaction directly even where the offer is correct (tests A3) | Low |
| O5 | **Under-lending measurement & feedback** | Instrument the funnel to quantify foregone risk-adjusted revenue by segment — a metric the bank lacks today | Creates the business case evidence and an ongoing steering metric; value even if no offer is ever changed | Very low — analytics only |
| O6 | **Graduated / staged offers** | Instead of static limit, propose conditional paths ("limit increases to X after 6 months of behavior Y") within policy | Captures upside while containing risk; customer sees a path, not a wall | Medium — new offer constructs need policy sign-off |
| O7 | **Counter-conservatism calibration input** | Provide Risk with evidence on where cut-offs/margins are demonstrably over-conservative, as input to their own policy review | Fixes P3 through the legitimate owner (Risk), not around them | Medium — politically sensitive, but correctly routed |
| O8 | **Segment-adjacent signal enrichment (advisory)** | Supplementary AI insight shown alongside the engine's segment for human underwriters — never auto-acting | Improves manual review quality; builds trust before any automation is proposed | Medium |

> **Deliberately out of scope for the bridge layer:** re-scoring customers, overriding segments automatically, adjusting the engine's inputs, or auto-approving above-policy limits. Any of these would make the layer a de facto credit decision model and trigger the full regulatory weight the concept is designed to avoid.

**Early Phase task:** size each opportunity (population touched × plausible value per customer × risk cost) using bank data, and rank. The MVP candidate list for Mid Phase should come from this ranking — not from what is technically most interesting.

---

## 5. Hypotheses to Validate

Each hypothesis is falsifiable and mapped to a validation method. Numbering groups: **H1–H4 problem existence, H5–H8 value mechanisms, H9–H11 customer, H12–H14 organizational/regulatory.**

| # | Hypothesis | Validation method | Falsified if… |
|---|---|---|---|
| H1 | Customers near segment decision boundaries are systematically under-classified relative to realized outcomes | Backtest: realized default rates of boundary cohorts vs. their assigned segment's expected PD band | Boundary cohorts' realized risk matches assigned segment |
| H2 | A material share (>X%, threshold set with Risk) of "under-performing" offers stem from stale scores rather than model error | Vintage analysis: time-since-last-score vs. subsequent segment migration | Migration is uncorrelated with score age |
| H3 | Thin-file and new-to-bank customers are disproportionately placed in lower segments and disproportionately migrate upward later | Cohort analysis by data-richness at origination | Thin-file customers' initial segments prove accurate |
| H4 | Manual overrides are asymmetric (downgrades ≫ upgrades) and downgrades show worse calibration than the model itself | Override log analysis with outcome tracking | Overrides are symmetric or add accuracy |
| H5 | Within-segment behavioral signals (e.g., transaction stability, deposit trends) can distinguish materially different risk levels inside a single segment | Retrospective analysis: within-segment outcome variance explained by candidate signals *(analysis of signal existence only — no model building)* | Within-segment outcomes are homogeneous / signals add no separation |
| H6 | The bank forgoes measurable risk-adjusted revenue from under-lending, net of expected loss and capital cost | Finance + Risk joint sizing using existing RAROC methodology | Net risk-adjusted uplift is immaterial after loss/capital costs |
| H7 | Customers whose limits are increased within policy show utilization uplift without proportional delinquency increase (based on the bank's own historical limit-increase programs) | Analysis of past proactive limit-increase campaigns | Past increases produced delinquency growth ≥ revenue growth |
| H8 | Earlier re-scoring of improving customers would move a meaningful population upward using the existing model alone | Simulate re-scoring cadence change on historical data | Re-scoring frequency changes segment for a negligible population |
| H9 | Offer-related dissatisfaction is driven more by lack of explanation and path-to-improvement than by the absolute limit | Complaint verbatim analysis; small-sample customer interviews | Dissatisfaction verbatims are dominated by amount, indifferent to explanation |
| H10 | Explainability of offer rationale increases customer acceptance and trust in AI-assisted recommendations | Qualitative testing of explanation concepts with customers and front-line staff | Explanations do not change acceptance/trust indicators |
| H11 | Under-classified customers have measurably higher attrition to competitors within 12 months | Attrition analysis by segment-boundary cohort | Attrition is uncorrelated with boundary status |
| H12 | Risk and Model Governance will accept an offer-optimization layer if it is bounded within existing policy ranges and fully auditable | Structured governance interviews; mock governance review of the concept | Governance signals that any offer-influencing logic requires full credit-model treatment regardless of bounds |
| H13 | The regulatory classification of the bridge layer can remain "offer optimization within approved policy" rather than "credit decisioning," given the jurisdiction's rules | Legal/Compliance opinion; precedent review; (if available) informal regulator dialogue | Legal opinion concludes the layer is a credit decision model |
| H14 | Under-classification does not correlate with protected attributes — or if it does, correcting it *reduces* disparate impact (making the layer a fairness improvement, not a risk) | Fairness audit of current segment assignments vs. available protected/proxy attributes | Correction would widen disparity, or the audit itself is legally blocked |

> Note the design intent behind H14: if current under-classification disproportionately affects protected groups, the bridge layer flips from "compliance risk" to "compliance remediation" — a decisive argument in governance. This is worth testing early.

---

## 6. Risks

### 6.1 Business Risks

| Risk | Description | Early-phase mitigation |
|---|---|---|
| Value overestimation | Gross revenue uplift ignores expected loss, capital, funding cost | Mandate risk-adjusted (not gross) sizing from day one |
| Risk–Business deadlock | Structural KPI conflict stalls the program | Establish shared metric and joint steering committee in Early Phase |
| Overshoot into over-lending | "Fixing" under-classification pushes some customers into unaffordable credit | Frame objective as *right-sizing*, not maximizing; embed affordability as a hard constraint in all sizing |
| Cannibalization/ripple | Better offers change behavior in pricing, collections, capital models downstream | Map downstream dependencies in current-state analysis |
| Sunk-cost momentum | Program continues into Mid Phase despite weak evidence | Hard exit criteria with a "no-go is a valid outcome" charter clause (§10) |

### 6.2 AI Risks

| Risk | Description | Early-phase mitigation |
|---|---|---|
| Ground-truth ambiguity | "Deserved segment" is not observable; only defaults are, and only for credit actually granted (selective labels problem) | Define ground-truth convention with Risk before any analysis; document its limits |
| Feedback loops | Adjusted offers change the very outcomes future assessments learn from | Flag as a Mid Phase design requirement; note in hypothesis validation caveats |
| Bias amplification | Supplementary signals may encode socio-economic proxies | Fairness review (H14) is mandatory, not optional |
| Opacity | Unexplainable adjustments destroy trust with Risk, customers, and regulators alike | Set explainability as a non-negotiable requirement in the Phase 1 requirements document |
| Silent scope creep | "Advisory" layer drifts into de facto decisioning through habit | Define bright-line boundaries of the layer's authority in the charter |

### 6.3 Regulatory Risks

| Risk | Description | Early-phase mitigation |
|---|---|---|
| Reclassification as credit decision model | Triggers full model governance, validation, possibly supervisory approval | Legal opinion in Early Phase (H13); design opportunities O1–O5 to stay within approved policy ranges |
| Fair lending / disparate impact | Differential offers within a segment invite discrimination scrutiny | Fairness audit; documented, attribute-safe rationale for any differentiation |
| Data protection / purpose limitation | Behavioral data collected for servicing used for offer optimization without valid basis | Legal basis mapping for every data category (§7) |
| Responsible lending | Higher limits must pass affordability rules in most jurisdictions | Affordability constraints included in every opportunity sizing |
| Explainability rights | Customers may have statutory rights to explanation of credit terms | Include in Compliance requirements gathering |
| AI-specific regulation | Depending on jurisdiction (e.g., EU AI Act treats creditworthiness AI as high-risk), the layer may face specific obligations regardless of internal classification | Jurisdiction-specific regulatory scan as an explicit Early Phase deliverable |

### 6.4 Operational Risks

| Risk | Description | Early-phase mitigation |
|---|---|---|
| No viable insertion point | Decision engine and offer delivery are technically inseparable | Technical flow walkthrough (A8) before any commitment |
| Ownership vacuum | No one owns the layer's decisions when losses occur | Define accountability model as an Early Phase deliverable |
| Front-line confusion | Staff cannot explain a two-layer outcome to customers | Include front-line staff in stakeholder interviews |
| Vendor/contract constraints | Engine vendor terms prohibit output interception | Contract review in current-state analysis |
| Change management underestimation | Credit policy processes have long approval cycles | Map governance calendar; align Phase timeline to real approval windows |

### 6.5 Data Risks

| Risk | Description | Early-phase mitigation |
|---|---|---|
| Data unavailability | Needed signals not captured or not historized | Data inventory with availability status (§7) |
| Data quality | Behavioral data noisy, gapped, or inconsistent across systems | Quality profiling included in feasibility assessment |
| Consent gaps | Customers never consented to this use | Legal basis column mandatory in the inventory |
| Bureau contract restrictions | Bureau data licensed for decisioning only, not "optimization" | Contract review with procurement/legal |
| Survivorship / selection bias | Historical data only shows outcomes for credit actually granted at actually offered levels | Document as a permanent analytical caveat; shapes what claims can honestly be validated |

---

## 7. Required Data Inventory

Access is **not assumed**. For every category the Early Phase must record: exists? accessible? legal basis? quality? owner?

### 7.1 Mandatory (Early Phase cannot proceed without)

| Data category | Purpose in Early Phase |
|---|---|
| Decision engine outputs (scores, segments, timestamps, model version) — historical | Establish baseline; boundary analysis (H1) |
| Segment cut-off definitions and change history | Understand classification mechanics |
| Offer data (limit, pricing, product) actually extended per customer | Link segment → offer; quantify offer conservatism |
| Credit performance outcomes (delinquency, default, loss) with sufficient history (ideally 24–36 months) | Ground truth for calibration backtests (H1–H4) |
| Segment migration history (customer-level segment over time) | Stale-score and thin-file hypotheses (H2, H3) |
| Manual override logs with reasons and outcomes | H4 |
| Risk appetite statement, credit policy documents, policy ranges per segment | Define the boundaries any optimization must respect (A5) |
| Complaint data tagged to credit limits/offers | H9; problem materiality from the customer side |
| Portfolio financials per segment (revenue, loss, provisioning) at least at aggregate level | Risk-adjusted opportunity sizing (H6) |

### 7.2 Useful (materially strengthens validation)

| Data category | Purpose |
|---|---|
| Transaction/behavioral banking data (inflows, balances, payment behavior) | Within-segment separation hypothesis (H5) |
| Credit utilization and limit-usage patterns | H7; opportunity sizing for O1 |
| Historical limit-increase campaign results | Strongest available natural experiment (H7) |
| Attrition/closure data with destination indicators where known | H11 |
| NPS / CSAT with credit-journey linkage | H9, H10; baseline for success metrics |
| Bureau data snapshots and refresh dates | Stale-data analysis (H2) |
| Front-line exception request logs | Demand evidence for O2 |
| Capital and funding cost allocation per segment | Precision of risk-adjusted sizing |

### 7.3 Optional (nice-to-have; do not gate Phase 1 on these)

| Data category | Purpose |
|---|---|
| Open banking / external account data (where consented) | Future signal potential for thin-file customers |
| Competitor offer intelligence (rates, limits by profile) | Competitive context for attrition hypothesis |
| Macro-economic overlays used in provisioning | Contextualize outcome periods |
| Web/app engagement data | Possible early indicators of intent/attrition |
| Customer demographic data beyond regulatory minimum | Only via a governed fairness-audit process (H14) — access to protected attributes for testing purposes requires its own legal review |

> **Rule for the inventory exercise:** every "Useful" or "Optional" item must carry a stated hypothesis it serves. Data with no hypothesis attached is not collected — this discipline is itself a compliance safeguard (data minimization).

---

## 8. Success Metrics

### 8.1 Phase 1 (Early Phase) KPIs — measuring the *planning phase itself*

Because Phase 1 delivers understanding, not offers, its KPIs are evidence and alignment KPIs:

| KPI | Target |
|---|---|
| Assumptions A1–A10 dispositioned (validated / falsified / deferred with reason) | 100% |
| Hypotheses H1–H14 tested or explicitly scheduled with data dependencies | ≥ 10 tested, remainder scheduled |
| P1/P2/P3 problem mix quantified (share of opportunity by sub-problem) | Quantified with Risk sign-off |
| Opportunity value sized on a risk-adjusted basis, with ranges | Board-presentable sizing document |
| Mandatory data categories confirmed available + legally usable | 100% dispositioned (available / blocked / conditional) |
| Stakeholder interviews completed across all mapped groups | 100% of groups, incl. front line and Model Risk |
| Legal/Compliance opinion on layer classification obtained | Written opinion delivered |
| Shared Risk–Business success metric agreed and signed | Signed one-pager |

### 8.2 Product KPIs — defined now, measured in later phases

These are defined in Phase 1 (with baselines captured) so later phases have an agreed scoreboard:

| KPI | Definition discipline required in Phase 1 |
|---|---|
| Reduction in under-classification rate | Requires the agreed ground-truth definition (A2); baseline measured on historical data |
| Approved credit volume uplift (risk-adjusted) | Net of expected loss, capital, funding — formula agreed with Finance & Risk |
| Portfolio risk stability | Default/delinquency rates of touched cohorts within a pre-agreed tolerance band vs. control expectation |
| Customer satisfaction (NPS/CSAT on credit journey) | Baseline captured now; credit-journey-specific, not bank-wide NPS |
| Revenue uplift per optimized customer | Attribution method agreed before any pilot exists |
| Complaint rate on credit limits/offers | Baseline from complaint taxonomy work |
| Fairness indicators | Disparity metrics chosen with Compliance; baseline measured (H14) |
| Explainability/trust indicators | Staff and customer trust measures piloted qualitatively in Phase 1 |

> **Discipline note:** every later-phase KPI must have its **baseline measured during Phase 1**. A KPI without a baseline is a story, not a metric.

---

## 9. Deliverables of the Early Phase

The following artifacts must exist, be reviewed, and be signed off before Mid Phase begins:

| # | Deliverable | Owner | Sign-off |
|---|---|---|---|
| D1 | **Problem Definition & Diagnosis Report** — quantified P1/P2/P3 mix, root-cause evidence | Product + Data Science | Risk + Business |
| D2 | **Current-State Decision Flow Map** — end-to-end flow, systems, owners, discretion points, candidate insertion points, downstream dependencies | Product + Bank SMEs | Risk + IT |
| D3 | **Stakeholder Analysis & Engagement Log** — interviews completed, positions, tensions, RACI proposal for the future layer | Product | Program sponsor |
| D4 | **Assumption & Hypothesis Validation Report** — disposition of A1–A10 and H1–H14 with evidence | Data Science | Risk (for analytical rigor) |
| D5 | **Opportunity Assessment & Prioritization** — sized, risk-adjusted, ranked O1–O8; recommended MVP candidate scope (scope only — not design) | Product + Finance | Executives |
| D6 | **Risk Register** — business/AI/regulatory/operational/data risks with owners and Phase-2 mitigations | Product + Risk | CRO office |
| D7 | **Regulatory & Legal Position Paper** — layer classification opinion, jurisdiction scan, fair-lending position, data legal bases | Compliance/Legal | Chief Compliance Officer |
| D8 | **Data Inventory & Access Disposition** — every category: exists / accessible / legal basis / quality / owner | Data Science + Data Office | CDO or equivalent |
| D9 | **Success Metrics & Baseline Book** — agreed KPI definitions, formulas, and measured baselines | Product + Finance | Risk + Business (joint) |
| D10 | **Governance & Accountability Proposal** — who owns the layer's recommendations, escalation paths, audit-trail requirements | Product + Risk | Model Risk + Audit |
| D11 | **Mid Phase Charter (draft)** — scope, boundaries ("the layer shall never…"), timeline, resource ask, go/no-go recommendation | Product | Steering committee |

---

## 10. Exit Criteria

Early Phase is complete **only when all of the following objective conditions are met.** These are gates, not checkboxes; failing a gate has a defined consequence.

| # | Exit criterion | Objective test | If not met |
|---|---|---|---|
| E1 | Problem materiality confirmed | Under-classification (per agreed ground truth) affects ≥ an agreed threshold of the portfolio, or P2/P3 opportunity is sized above an agreed value floor | **Stop or pivot** — no-go is a legitimate outcome |
| E2 | Ground truth agreed | Risk has signed the definition of "deserved segment / right-sized offer" used in all analyses | Analyses are not accepted; phase not closed |
| E3 | Risk-adjusted value case exists | Opportunity sizing (D5) reviewed by Finance and Risk; net value range documented, including downside scenario | Return to sizing; do not enter Mid Phase on gross numbers |
| E4 | Regulatory path is viable | Written legal/compliance opinion (D7) confirms at least one opportunity (O1–O8) can proceed under an acceptable classification | Restrict scope to compliant opportunities or stop |
| E5 | Mandatory data dispositioned | 100% of §7.1 categories marked available-and-usable, or an approved workaround exists per gap | Phase extended; Mid Phase not started on hoped-for data |
| E6 | Insertion feasibility confirmed | Technical walkthrough (D2) identifies ≥ 1 viable, vendor-compliant point where offers can be influenced pre-delivery | Concept reworked or stopped |
| E7 | Shared success metric signed | Risk and Business have jointly signed the KPI book (D9) including the risk-stability tolerance band | Escalate to executive sponsor; do not proceed on divided metrics |
| E8 | Governance model accepted | Model Risk and Audit accept the accountability proposal (D10) in principle | Rework governance; this is a hard gate |
| E9 | Fairness position established | H14 audit executed (or formally blocked with documented reason and executive acceptance of the residual risk) | Compliance escalation |
| E10 | Go/No-Go decision taken | Steering committee formally decides: proceed to Mid Phase with charter D11, pivot scope, or stop — with rationale minuted | Phase is not closed until a decision is minuted |

> **Charter principle for E1/E10:** the Early Phase is successful if it produces a *correct* decision — including "the model is fine, invest in offer policy instead" or "stop." A phase that only ever recommends proceeding has failed as a discovery phase.

---

## Appendix A — Early Phase Working Plan (indicative, 8–10 weeks)

| Weeks | Workstream | Key activities |
|---|---|---|
| 1–2 | Mobilize & map | Kickoff, stakeholder interviews begin, decision-flow walkthrough, data inventory launch |
| 2–4 | Legal & governance track (parallel) | Layer-classification opinion, jurisdiction scan, data legal bases, governance pre-alignment |
| 3–6 | Evidence track | Backtests and cohort analyses for H1–H8; complaint/NPS analysis for H9–H11 |
| 5–7 | Sizing & synthesis | P1/P2/P3 quantification, risk-adjusted opportunity sizing, fairness audit |
| 7–8 | Alignment | KPI book negotiation (Risk + Business), risk register review, governance proposal |
| 8–10 | Close | Deliverable finalization, steering committee, Go/No-Go |

## Appendix B — Key Questions to Put to the Bank in Week 1

1. How do you currently define a "correct" segment assignment — and has anyone ever measured accuracy against outcomes?
2. When did segment cut-offs last change, why, and who decided?
3. What happened in your last proactive limit-increase campaign — volumes, losses, complaints?
4. What share of manual overrides are upgrades vs. downgrades?
5. Is there any metric, anywhere, for revenue foregone through conservative offers?
6. What is your risk appetite headroom today — capital, provisioning, concentration?
7. What does your engine vendor contract say about intercepting or augmenting outputs?
8. Has Compliance ever assessed segment assignments for disparate impact?
9. Who would be accountable if an "optimized" offer defaults?
10. What is the fastest a credit policy change has ever gone from proposal to production?

---

*End of Early Phase Plan. No solution design, model selection, or architecture is included by intent; those belong to Mid Phase and are gated on the exit criteria above.*
