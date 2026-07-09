# Early Phase Risk Register (living document)
**Source basis:** every risk from source §6, one register entry each (26 entries). The source assigns no risk IDs; this register declares the convention **R-BUS / R-AI / R-REG / R-OPS / R-DAT** + sequence, used across the package. Descriptions and Early Phase mitigations are the source's own (condensed where needed, never contradicted). Likelihood/impact are placeholders to be scored at the week-7 review workshop (scale agreed there). The signed snapshot of this register becomes deliverable D6.

**Columns:** L = likelihood (TODO: score 1–5), I = impact (TODO: score 1–5).

## 6.1 Business risks

| ID | Risk | Description (source) | L | I | Owner (role) | Early Phase mitigation (source) | Trigger indicators (watch for) | Status |
|---|---|---|---|---|---|---|---|---|
| R-BUS-01 | Value overestimation | Gross revenue uplift ignores expected loss, capital, funding cost | TODO | TODO | Finance (with Product) | Mandate risk-adjusted (not gross) sizing from day one | Any sizing draft or stakeholder deck quoting gross uplift without net counterpart; H6 method session skipped | OPEN |
| R-BUS-02 | Risk–Business deadlock | Structural KPI conflict stalls the program | TODO | TODO | Sponsor | Establish shared metric and joint steering committee in Early Phase | D9 negotiation exceeds two sessions without a shared draft; either party re-opens "raw volume" vs "raw loss" framing; E7 date slips | OPEN |
| R-BUS-03 | Overshoot into over-lending | "Fixing" under-classification pushes some customers into unaffordable credit | TODO | TODO | Risk (with Compliance) | Frame objective as *right-sizing*, not maximizing; embed affordability as a hard constraint in all sizing | Sizing scenarios lacking an affordability exclusion step; H7 evidence showing past increases created hardship complaints; "maximize" language appearing in drafts | OPEN |
| R-BUS-04 | Cannibalization/ripple | Better offers change behavior in pricing, collections, capital models downstream | TODO | TODO | Product (with IT SMEs) | Map downstream dependencies in current-state analysis | D2 walkthrough finds segment values hard-coded downstream (§2.4); pricing/collections owners surprised by the initiative in interviews | OPEN |
| R-BUS-05 | Sunk-cost momentum | Program continues into Mid Phase despite weak evidence | TODO | TODO | Sponsor (with Steering Committee) | Hard exit criteria with a "no-go is a valid outcome" charter clause (§10) | Pressure to soften pre-registered thresholds after seeing results; steering language dismissing falsified hypotheses; board material pre-announcing the product | OPEN |

## 6.2 AI risks

| ID | Risk | Description (source) | L | I | Owner (role) | Early Phase mitigation (source) | Trigger indicators | Status |
|---|---|---|---|---|---|---|---|---|
| R-AI-01 | Ground-truth ambiguity | "Deserved segment" is not observable; only defaults are, and only for credit actually granted (selective labels problem) | TODO | TODO | Data Science (with Risk) | Define ground-truth convention with Risk before any analysis; document its limits | E2 slips past week 4; competing definitions still circulating after workshop #2; analyses starting before the convention is signed | OPEN |
| R-AI-02 | Feedback loops | Adjusted offers change the very outcomes future assessments learn from | TODO | TODO | Product (flag-carrier; Mid Phase owner TBD) | Flag as a Mid Phase design requirement; note in hypothesis validation caveats | Any Phase-1 claim or KPI that assumes post-intervention data behaves like historical data; the caveat missing from D4 drafts | OPEN |
| R-AI-03 | Bias amplification | Supplementary signals may encode socio-economic proxies | TODO | TODO | Compliance (with Data Science) | Fairness review (H14) is mandatory, not optional | H5 candidate signals correlating with proxy attributes on the Compliance screen; pressure to skip the proxy screen for speed; OPT5 gate decision drifting past week 5 | OPEN |
| R-AI-04 | Opacity | Unexplainable adjustments destroy trust with Risk, customers, and regulators alike | TODO | TODO | Product | Set explainability as a non-negotiable requirement in the Phase 1 requirements document | H10 staff sessions show concepts unusable at first contact; interviewees unable to restate the concept's rationale in their own words | OPEN |
| R-AI-05 | Silent scope creep | "Advisory" layer drifts into de facto decisioning through habit | TODO | TODO | Model Risk (boundary keeper) + Product | Define bright-line boundaries of the layer's authority in the charter | Meeting notes proposing auto-actions "just for efficiency"; requests to pilot offer changes during Phase 1; D5 scope text describing mechanisms rather than scope | OPEN |

## 6.3 Regulatory risks

| ID | Risk | Description (source) | L | I | Owner (role) | Early Phase mitigation (source) | Trigger indicators | Status |
|---|---|---|---|---|---|---|---|---|
| R-REG-01 | Reclassification as credit decision model | Triggers full model governance, validation, possibly supervisory approval | TODO | TODO | Compliance/Legal | Legal opinion in Early Phase (H13); design opportunities O1–O5 to stay within approved policy ranges | H13 draft reasoning trending negative; Model Risk interview signaling "influence = model" (H12 falsifier); precedent review finding adverse classifications | OPEN |
| R-REG-02 | Fair lending / disparate impact | Differential offers within a segment invite discrimination scrutiny | TODO | TODO | Compliance | Fairness audit; documented, attribute-safe rationale for any differentiation | H14 showing correction would widen disparity; OQ-08 answer revealing past unaddressed findings | OPEN |
| R-REG-03 | Data protection / purpose limitation | Behavioral data collected for servicing used for offer optimization without valid basis | TODO | TODO | Compliance (DPO) | Legal basis mapping for every data category (§7) | Data Office flags consent gaps on U1; legal-basis column still incomplete at week 4; DPIA threshold triggered without process started | OPEN |
| R-REG-04 | Responsible lending | Higher limits must pass affordability rules in most jurisdictions | TODO | TODO | Compliance (with Risk) | Affordability constraints included in every opportunity sizing | D5 drafts without the affordability exclusion; jurisdiction scan finding stricter affordability duties than assumed | OPEN |
| R-REG-05 | Explainability rights | Customers may have statutory rights to explanation of credit terms | TODO | TODO | Compliance | Include in Compliance requirements gathering | Jurisdiction scan finding statutory explanation duties; complaint data (M8) showing explanation-rights complaints | OPEN |
| R-REG-06 | AI-specific regulation | Depending on jurisdiction (e.g., EU AI Act treats creditworthiness AI as high-risk), the layer may face specific obligations regardless of internal classification | TODO | TODO | Compliance/Legal | Jurisdiction-specific regulatory scan as an explicit Early Phase deliverable | OQ-17 confirming an in-scope jurisdiction with AI-specific duties; scan finding obligations that bind regardless of H13's classification outcome | OPEN |

## 6.4 Operational risks

| ID | Risk | Description (source) | L | I | Owner (role) | Early Phase mitigation (source) | Trigger indicators | Status |
|---|---|---|---|---|---|---|---|---|
| R-OPS-01 | No viable insertion point | Decision engine and offer delivery are technically inseparable | TODO | TODO | IT SMEs (with Product) | Technical flow walkthrough (A8) before any commitment | D2 walkthrough finding end-to-end hard-coding; every candidate insertion point failing the vendor-compliance check — escalate to mid-point steering (week 5), not week 10 | OPEN |
| R-OPS-02 | Ownership vacuum | No one owns the layer's decisions when losses occur | TODO | TODO | Sponsor (until D10 assigns) | Define accountability model as an Early Phase deliverable | OQ-09 still unanswered at week 6; no owner candidate named in D10 draft; interviews producing mutually exclusive ownership views | OPEN |
| R-OPS-03 | Front-line confusion | Staff cannot explain a two-layer outcome to customers | TODO | TODO | Business (front-line lead) | Include front-line staff in stakeholder interviews | Front-line interview evidence of explanation failure today; H10 staff-side concept tests failing | OPEN |
| R-OPS-04 | Vendor/contract constraints | Engine vendor terms prohibit output interception | TODO | TODO | IT (with Legal/Procurement) | Contract review in current-state analysis | OQ-07 answer revealing prohibition/exclusivity clauses; vendor requiring commercial renegotiation for any augmentation | OPEN |
| R-OPS-05 | Change management underestimation | Credit policy processes have long approval cycles | TODO | TODO | Product (with Risk governance office) | Map governance calendar; align Phase timeline to real approval windows | OQ-10 answer showing cycles longer than the plan assumes; policy governance calendar conflicting with the 8–10 week window | OPEN |

## 6.5 Data risks

| ID | Risk | Description (source) | L | I | Owner (role) | Early Phase mitigation (source) | Trigger indicators | Status |
|---|---|---|---|---|---|---|---|---|
| R-DAT-01 | Data unavailability | Needed signals not captured or not historized | TODO | TODO | Data Office | Data inventory with availability status (§7) | Tracker "exists = no" on any Mandatory item; M5 migration history reconstructable only partially | OPEN |
| R-DAT-02 | Data quality | Behavioral data noisy, gapped, or inconsistent across systems | TODO | TODO | Data Office (with Data Science) | Quality profiling included in feasibility assessment | Profiling showing coverage gaps or mid-history definition changes; U1 inconsistencies across source systems | OPEN |
| R-DAT-03 | Consent gaps | Customers never consented to this use | TODO | TODO | Compliance (DPO) | Legal basis column mandatory in the inventory | Legal-basis review flagging servicing-only consent on U1; customer research (guide prompt 7) revealing strong social-license objections | OPEN |
| R-DAT-04 | Bureau contract restrictions | Bureau data licensed for decisioning only, not "optimization" | TODO | TODO | Legal/Procurement | Contract review with procurement/legal | OQ-24 finding restrictive license scope; bureau requiring consent/fees for diagnostic use of U6 | OPEN |
| R-DAT-05 | Survivorship / selection bias | Historical data only shows outcomes for credit actually granted at actually offered levels | TODO | TODO | Data Science | Document as a permanent analytical caveat; shapes what claims can honestly be validated | The caveat missing from any analysis writeup; claims about rejected/never-offered populations appearing in drafts | OPEN |

## Register operating rules
1. Reviewed weekly at the working group; scored (L/I) and formally reviewed at the week-7 workshop; snapshot + Phase-2 mitigations signed as D6.
2. A fired trigger is logged with date and evidence, and the mitigation's adequacy is reassessed — fired triggers are discovery output, not failure.
3. New risks get the next ID in their category and an evidence pointer; they are additions, not renames — source §6 entries are never deleted, only dispositioned.
4. R-BUS-05 has a structural safeguard beyond this register: the charter's quoted "no-go is a valid outcome" clause and pre-registered thresholds (charter §3).
