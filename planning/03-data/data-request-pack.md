# Data Request Pack — Early Phase Diagnostic
**To:** Bank Data Office / CDO
**From:** Early Phase working group (Data Science lead, on behalf of the Program Sponsor)
**Date issued:** Week 1 (workplan MS1) · **Response requested by:** end of Week 2 (per-item status), first delivery target Week 3
**Reference documents:** Early Phase Charter (`../00-program/charter.md`); Data Inventory Tracker (`../03-data/data-inventory-tracker.md`)

---

## 1. Purpose of this request

The Early Phase must test defined hypotheses (H1–H14) about credit segmentation and offer assignment before any product decision is taken. This request covers only the data those hypotheses require. Per the source plan's inventory rule, **every requested item cites the hypothesis it serves; data with no hypothesis attached is not requested** — this discipline is itself a compliance safeguard (data minimization).

This is a **diagnostic** request: analysis of historical data only. No production system, no scoring logic, and no customer-facing process is involved or planned in this phase.

## 2. Handling and minimization principles

1. **Pseudonymization at source** where feasible: a consistent pseudonymous customer key across extracts (required to join segments, offers, migrations, and outcomes per customer); no direct identifiers unless a specific analysis lawfully requires them.
2. **Aggregates where sufficient:** M9 and U8 are requested at segment-aggregate level, not customer level.
3. **Protected attributes (OPT5) are NOT extracted under this request.** They move only after Compliance approves the governed fairness-audit protocol (separate authorization, expected decision Week 5).
4. **Legal basis confirmation requested per item** — the tracker's legal-basis column must be completed by the Data Office with Compliance before delivery of any item flagged conditional.
5. **Retention:** diagnostic extracts are held in the agreed analysis environment for the phase duration + the bank's retention standard, then deleted/archived per Data Office instruction.
6. **Not requested at all (minimization rule applied):** OPT1 open-banking data and OPT4 web/app engagement data carry no Phase-1 hypothesis and are excluded (OQ-22).

## 3. Requested items — Priority 1: Mandatory (gate E5; phase cannot proceed without)

| Ref | Item | Grain & window requested | Serves (cited hypothesis/assumption) |
|---|---|---|---|
| M1 | Decision engine outputs: score, assigned segment, timestamp, model version — all scoring events | Customer-event level; full available history (target ≥ 36 months) | H1, H2, H3, H8; H11 cohorts; H14 audit base |
| M2 | Segment cut-off definitions + change history (values, dates, approver) | Reference data; full history | H1 (boundary definitions per regime); D2 |
| M3 | Offers actually extended: limit, pricing, product tier per customer | Customer level; 24–36 months | H6 (offer-vs-policy gap); H1 context; A4 |
| M4 | Credit performance outcomes: delinquency, default, loss events | Customer-month or event level; 24–36 months (OQ-19) | H1, H3, H4, H5, H7 (ground-truth side); H14 |
| M5 | Segment migration history (customer-level segment over time) | Customer-period level; 24–36 months | H2, H3, H8; A1 |
| M6 | Manual override logs: direction, reason, authority, linked outcome | Event level; 24–36 months | H4; D10 lineage evidence |
| M7 | Risk appetite statement; credit policy documents; per-segment policy ranges (limits, pricing bands, expected PD bands) | Documents + reference tables; current + last material revision | A5; H1 (PD bands); H6 (headroom); H12/H13 inputs |
| M8 | Complaints tagged to credit limits/offers, with verbatims where held | Case level; 24 months | H9; A3; D9 complaint baseline |
| M9 | Portfolio financials per segment: revenue, loss, provisioning | Segment-aggregate; 24–36 months | H6; A4; O5 baseline |

## 4. Requested items — Priority 2: Useful (materially strengthens validation; does not gate the phase)

| Ref | Item | Grain & window requested | Serves |
|---|---|---|---|
| U1 | Transaction/behavioral banking data: inflows, balances, payment behavior | Customer-month level, pseudonymized; 12–24 months; **deliver only after legal-basis confirmation (purpose limitation)** | H5 |
| U2 | Credit utilization and limit-usage patterns | Customer-month level; 24 months | H7; O1 sizing |
| U3 | Historical limit-increase campaign results: selection rules, increases granted, outcome reports | Campaign + customer level; all campaigns in outcome window | H7 (A10 evidence) |
| U4 | Attrition/closure data, with destination indicators where known | Customer-event level; 24 months | H11 |
| U5 | NPS/CSAT with credit-journey linkage, incl. verbatims where held | Response level; 24 months | H9, H10; D9 baselines |
| U6 | Bureau data snapshots and refresh dates | Customer-event level (refresh metadata may suffice — advise); 24–36 months; **subject to bureau-license confirmation (OQ-24)** | H2, H3, H8 |
| U7 | Front-line exception request logs (volumes, turnaround, outcomes) | Case level; 24 months | O2 demand sizing (mapping nuance logged as OQ-21) |
| U8 | Capital and funding cost allocation per segment | Segment-aggregate; current methodology + 24 months | H6 (risk-adjusted precision) |

## 5. Requested items — Priority 3: Optional (never gates the phase)

| Ref | Item | Grain & window | Serves | Condition |
|---|---|---|---|---|
| OPT2 | Competitor offer intelligence (rates, limits by profile), if held | Whatever exists | H11 (context only) | Only if already held — do not procure |
| OPT3 | Macro-economic overlays used in provisioning | Aggregate; outcome window | H1–H4 outcome-period contextualization | Only if already produced for provisioning |
| OPT5 | Customer demographic data beyond regulatory minimum | **Placeholder only — do not extract** | H14 fairness audit | Moves only under the Compliance-approved governed protocol (separate authorization) |

## 6. Response requested from the Data Office (per item, by end of Week 2)

For each Ref above: **exists?** (yes/no/partial) · **accessible?** (path + environment) · **legal basis** (confirmed basis or blocker) · **quality notes** (known gaps, definition changes mid-history) · **data owner** (named) · **earliest delivery date** · **constraints** (contractual, e.g., bureau license; technical).

These responses populate the tracker and become D8 (Data Inventory & Access Disposition, CDO sign-off). Items answered "blocked" need a named blocker so a workaround can be assessed — an unresolved Mandatory item triggers the E5 consequence ("Phase extended; Mid Phase not started on hoped-for data").

## 7. Contacts and escalation

- Working-level: Data Science lead (named TODO) — clarifications, delivery logistics.
- Escalation: Engagement Lead → Program Sponsor (charter §4) for unowned blockers on Mandatory items after one week.
