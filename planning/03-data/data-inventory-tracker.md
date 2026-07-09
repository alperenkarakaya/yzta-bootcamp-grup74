# Data Inventory Tracker — §7 Categories
**Source basis:** every category from source §7 (all three tiers). The source assigns no item IDs; this tracker declares the convention **M1–M9** (§7.1 Mandatory), **U1–U8** (§7.2 Useful), **OPT1–OPT5** (§7.3 Optional), used across the whole working package.
**Rule (source §7, verbatim):** "every 'Useful' or 'Optional' item must carry a stated hypothesis it serves. Data with no hypothesis attached is not collected — this discipline is itself a compliance safeguard (data minimization)."
**Gate:** E5 requires 100% of Mandatory categories dispositioned (available-and-usable, or approved workaround per gap). Optional items never gate Phase 1 (§7.3).
**Disposition values:** AVAILABLE-USABLE / CONDITIONAL (state condition) / BLOCKED (state blocker + workaround) / DO-NOT-COLLECT (minimization rule).

## Tier 1 — Mandatory (§7.1): "Early Phase cannot proceed without"

| ID | Data category (source) | Purpose (source) → serves | Exists? | Accessible? | Legal basis | Quality assessment | Owner | Blocking issue | Disposition |
|---|---|---|---|---|---|---|---|---|---|
| M1 | Decision engine outputs (scores, segments, timestamps, model version) — historical | Baseline; boundary analysis (H1) → H1, H2, H3, H8, H11, H14 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| M2 | Segment cut-off definitions and change history | Understand classification mechanics → H1, H11; D2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| M3 | Offer data (limit, pricing, product) actually extended per customer | Link segment → offer; quantify offer conservatism → H1 (context), H6; D1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| M4 | Credit performance outcomes (delinquency, default, loss), ideally 24–36 months | Ground truth for calibration backtests (H1–H4) → H1, H2*, H3, H4, H5, H7, H8*, H14 | TODO | TODO | TODO | TODO | TODO | TODO (OQ-19: history depth) | TODO |
| M5 | Segment migration history (customer-level segment over time) | Stale-score and thin-file hypotheses (H2, H3) → H2, H3, H8 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| M6 | Manual override logs with reasons and outcomes | H4 → H4; D10 evidence | TODO | TODO | TODO | TODO (IA lineage check) | TODO | TODO | TODO |
| M7 | Risk appetite statement, credit policy documents, policy ranges per segment | Boundaries any optimization must respect (A5) → A5, H1 (PD bands), H6, H12, H13 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| M8 | Complaint data tagged to credit limits/offers | H9; problem materiality from the customer side → H9; D1, D9 baseline | TODO | TODO | TODO | TODO (tagging quality) | TODO | TODO | TODO |
| M9 | Portfolio financials per segment (revenue, loss, provisioning), at least aggregate | Risk-adjusted opportunity sizing (H6) → H6; D5, O5 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

\* M4 supports H2/H8 indirectly via migration-outcome consistency checks; their primary drivers are M1/M5/U6.

## Tier 2 — Useful (§7.2): "materially strengthens validation"

| ID | Data category (source) | Purpose (source) → serves | Exists? | Accessible? | Legal basis | Quality assessment | Owner | Blocking issue | Disposition |
|---|---|---|---|---|---|---|---|---|---|
| U1 | Transaction/behavioral banking data (inflows, balances, payment behavior) | Within-segment separation hypothesis (H5) → H5 | TODO | TODO | TODO (purpose limitation — R-REG-03) | TODO | TODO | TODO | TODO |
| U2 | Credit utilization and limit-usage patterns | H7; opportunity sizing for O1 → H7, O1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| U3 | Historical limit-increase campaign results | Strongest available natural experiment (H7) → H7 | TODO (OQ-03) | TODO | TODO | TODO | TODO | TODO | TODO |
| U4 | Attrition/closure data with destination indicators where known | H11 → H11 | TODO | TODO | TODO | TODO (destination coverage) | TODO | TODO | TODO |
| U5 | NPS / CSAT with credit-journey linkage | H9, H10; baseline for success metrics → H9, H10; D9 | TODO | TODO | TODO | TODO (journey linkage) | TODO | TODO | TODO |
| U6 | Bureau data snapshots and refresh dates | Stale-data analysis (H2) → H2, H3, H8 | TODO | TODO | TODO (OQ-24: bureau license scope — R-DAT-04) | TODO | TODO | TODO | TODO |
| U7 | Front-line exception request logs | Demand evidence for O2 → O2 sizing in D5 (rule nuance: OQ-21) | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| U8 | Capital and funding cost allocation per segment | Precision of risk-adjusted sizing → H6 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

## Tier 3 — Optional (§7.3): "nice-to-have; do not gate Phase 1 on these"

| ID | Data category (source) | Purpose (source) → serves | Exists? | Accessible? | Legal basis | Quality assessment | Owner | Blocking issue | Disposition |
|---|---|---|---|---|---|---|---|---|---|
| OPT1 | Open banking / external account data (where consented) | Future signal potential for thin-file customers → **no Phase-1 hypothesis attached** | TODO | — | — | — | TODO | — | **DO-NOT-COLLECT** in Phase 1 per §7 minimization rule (OQ-22); revisit only if an owner attaches a hypothesis |
| OPT2 | Competitor offer intelligence (rates, limits by profile) | Competitive context for attrition hypothesis → H11 (context only) | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| OPT3 | Macro-economic overlays used in provisioning | Contextualize outcome periods → H1–H4 interpretation context | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| OPT4 | Web/app engagement data | Possible early indicators of intent/attrition → **no Phase-1 hypothesis attached** | TODO | — | — | — | TODO | — | **DO-NOT-COLLECT** in Phase 1 per §7 minimization rule (OQ-22); revisit only if an owner attaches a hypothesis |
| OPT5 | Customer demographic data beyond regulatory minimum | Only via a governed fairness-audit process (H14) — "access to protected attributes for testing purposes requires its own legal review" (source, verbatim) → H14 | TODO | TODO — **legal gate first** (workplan wk5) | TODO (own legal review) | TODO | TODO | TODO | TODO |

## Tracker operating rules
1. **Update cadence:** weekly at the working group; statuses feed D8 directly (this tracker *is* D8's data table in draft form).
2. **Every blocking issue gets an owner and a date** — an unowned blocker on an M-item is an E5 escalation.
3. **Legal basis column is mandatory** for every collected item (§6.5 consent-gaps mitigation, verbatim: "Legal basis column mandatory in the inventory").
4. **Workarounds:** a Mandatory gap can pass E5 only with an *approved* workaround, documented per gap ("Phase extended; Mid Phase not started on hoped-for data" otherwise).
5. **No new categories** may be added without a stated hypothesis/assumption and an open-questions entry — scope discipline runs through data too.
