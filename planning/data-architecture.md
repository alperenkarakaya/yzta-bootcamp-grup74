# AKS — Data Architecture Plan

**Scope:** the data structure required to run AKS at its best while staying inside the project's boundary and rigor mandate. This is a **detailed working spec**, subordinate to the three root source-of-truth docs — [`../overview.md`](../overview.md), [`../architecture.md`](../architecture.md), [`../execution.md`](../execution.md). Where this doc and a root doc disagree, the root doc wins. This folder exists because column-level data-engineering detail is too fine-grained for the root docs; it feeds `execution.md` tasks (product folders 01–05) and `architecture.md` §5/§7.

Companion files:
- [`feature-schema.md`](feature-schema.md) — concrete column-by-column schema (raw, features, target, persistence).
- [`data-pipeline-steps.md`](data-pipeline-steps.md) — the ordered pipeline steps + how they map to product folders and tasks.

> **Origin note:** this plan was produced from a research brief on next-generation alternative-data credit optimization. The brief is **critically filtered**, not transcribed — see §5 (what we adopt) and §6 (what we reject or defer, and why). Adopting it wholesale would violate our boundary and our evidence bar.

---

## 1. Design principles (binding — from the root mandate)

1. **Statistical validity > data volume.** More columns is not the goal; *calibratable, non-leaking* signal is. Priority order (overview.md §5) governs every column decision.
2. **Data minimization.** No column enters the schema without a **cited hypothesis** (05-business registry). Columns that no hypothesis needs are `DO-NOT-COLLECT`.
3. **No label leakage.** The circularity finding (architecture.md §5.1) is a data-architecture failure: the label was generated from features the model then trained on. The schema below **physically separates** the target from the feature space and forbids any feature derived from the outcome.
4. **Boundary is a data invariant.** AKS emits a *supplementary* capacity signal + PD-gap and a *within-policy* limit suggestion. The bank's classic score is a **read-only input column** that no pipeline stage may write. Every scoring writes an immutable audit row.
5. **Point-in-time correctness.** Every feature must be computable from data available *strictly before* the outcome window. No future information in any training row.
6. **Privacy by construction.** Each column carries a KVKK/PII class and a lawful basis *in the schema itself* (§4), not as an afterthought.

## 2. The data model in four tiers

Columns are organized by **data-source tier**, ordered by how soon we can responsibly use them. Full column lists live in [`feature-schema.md`](feature-schema.md); this is the map.

| Tier | Source | Status | Rationale |
|---|---|---|---|
| **T0 — Transaction-derived** | Account transactions (synthetic now; real via OQ-36) | **NOW** — this is today's product | The 9 behavioral features already extracted; the safe, explainable core. Extend with a few well-justified cash-flow columns. |
| **T1 — Open-banking cash-flow** | PSD2/BKM-permissioned bank APIs | **NEXT** (real-data path, OQ-36; licensing-gated) | Directly measures *Capacity* — gross vs net income, income volatility, essential vs discretionary split, overdraft behavior. This is the research brief's strongest, best-evidenced layer and maps 1:1 to Formulation B. |
| **T2 — Behavioral / engagement** | App/clickstream telemetry (zero-PII signals) | **GUARDED / RESEARCH** | Potentially predictive (early-warning: hardship-page access) but gaming-prone, consent-heavy, DPIA-mandatory, and a leakage risk. Admitted only per-column with an adversarial-robustness review (RQ-3). Not near-term. |
| **T3 — Alternative proxies** | Educational data (students), cross-border credit passport (immigrants) | **GUARDED / FUTURE** | Students are our primary target, so academic/institution proxies are tempting — but they are high fair-lending risk (can proxy for protected class). Requires fairness sign-off before any use. Immigrant cross-border = later. |

**One-line reading:** build T0 well now, design the schema so T1 slots in when real data lands, keep T2/T3 behind explicit governance gates.

## 3. The target (label) — the part the circularity finding forces us to redesign

This is the highest-leverage section. Full schema in [`feature-schema.md`](feature-schema.md) §3.

- **The outcome column `temerrut_gerceklesen`** (realized default) must come from a **real repayment outcome** (OQ-36 real dataset, e.g. Home Credit) **or**, if we stay synthetic, from a **decoupled generator** where a customer-level latent capacity is drawn *independently* within each persona's plausible range — persona must **not** determine both the features and the label (architecture.md §5.1).
- **Formulation B outputs** (the productized target — architecture.md §5.3), stored as distinct columns:
  - `pd_davranissal` — calibrated behavioral PD from the AKS model.
  - `pd_geleneksel_bant` — the traditional-band-implied PD (from the bank's classic score band).
  - `pd_fark` (PD-gap) = `pd_geleneksel_bant − pd_davranissal` — **the core product signal**: positive gap = behavioral evidence says more capacity than the thin file implies.
  - `kapasite_sinyali` — the supplementary capacity signal exposed to the bank.
- **Headline metric is calibration + incremental-approval-at-fixed-bad-rate on the thin-file subpopulation**, not aggregate AUC. The schema therefore stores per-segment calibration metadata (`calibration_ece_segment`, `calibration_version`).
- **Hard rule:** no column used to *compute* an outcome may be reused as a *feature*. The pipeline enforces this with an explicit deny-list (data-pipeline-steps.md §4).

## 4. Governance columns (every record carries these)

Privacy/compliance is embedded in the schema, per the research brief's KVKK/PSD2 section (this part of the brief *is* directly applicable to Turkey):

| Column | Purpose |
|---|---|
| `kvkk_sinifi` | PII class: `none` / `financial` / `sensitive` (behavioral/psychometric would be sensitive → highest bar) |
| `yasal_dayanak` | Lawful basis: `sozlesme` (contractual necessity) / `mesru_menfaat` (legitimate interest) / `acik_riza` (explicit consent) |
| `riza_id` | FK to a consent record (required for any `acik_riza` column); null → column must not be populated |
| `kaynak` | Provenance: `demo` / `api` / `csv` / `open_banking` / `bureau` |
| `alindigi_zaman` | Ingest timestamp (point-in-time correctness + retention/erasure) |
| `saklama_bitis` | Retention deadline (KVKK erasure) |

**Human-oversight invariant (KVKK Art. 11 / GDPR Art. 22):** an adverse automated decision must be contestable and route to a human underwriter who can override. The audit schema stores `karar_kaynagi` (`otomatik` / `insan_gozden_gecirme`) and `itiraz_durumu`.

## 5. What we ADOPT from the research (and why it survives the bar)

- **Open-banking cash-flow underwriting (T1).** Directly measures Capacity, is calibratable, and *is* Formulation B. Strong evidence, clear hypothesis. → primary near-term extension.
- **Essential-vs-discretionary expenditure split, income volatility/trajectory, overdraft behavior.** Concrete, verifiable cash-flow columns with obvious repayment hypotheses. → added to the feature schema (T1).
- **Through-the-Cycle vs Point-in-Time PD framing.** Legitimate; informs the labeling/eval design (out-of-time split, execution.md R8).
- **Early-warning behavioral signal (hardship-page access) for pre-delinquency.** Kept as a **monitoring** signal (drift/early-warning), *not* an origination feature, to avoid leakage and gaming. → T2, guarded, monitoring-only.
- **KVKK / PSD2 / BKM / VERBIS / DPIA / human-oversight architecture.** Directly applicable to a Turkey-based product. → §4 governance columns + 05-business governance task.
- **Zero-knowledge / consent-permissioned data access as a privacy posture.** Adopted as a *design intent* (minimize data liability), not a near-term build.

## 6. What we REJECT or DEFER (mandate + boundary filter)

- **Autonomous RL / Double-DQN / Actor-Critic credit-limit optimization — REJECTED as an autonomous actor.** This is the research brief's centerpiece and it **violates our hard boundary**: AKS must never auto-adjust limits or auto-approve above policy. We only *suggest* a within-policy limit that a human/bank applies. RL limit optimization may live as a *north-star research note* (a policy the bank could run on our calibrated PD-gap), never as a shipped autonomous decision engine. Also: it needs experimental champion/challenger data we do not have (Formulation C, architecture.md §5.3).
- **Psychometric / gamified character scoring — REJECTED (for now).** Weak evidence, highly gameable, and character/psychological profiling is KVKK *sensitive* data with serious fair-lending exposure. Fails the evidence bar and the minimization rule.
- **Smartphone metadata / dense behavioral fingerprinting (Credolab-style "+45%") — DEFERRED, guarded.** The cited uplift is vendor-marketing, not something we've validated; it is consent-heavy, gaming-prone, and a leakage magnet. Admit individual signals only after an adversarial-robustness review (RQ-3) and a DPIA. Not near-term.
- **Educational proxies (adjusted GPA, institution ranking) — DEFERRED, fairness-gated.** Attractive for our student segment but a textbook proxy-discrimination risk. No use without an explicit fair-lending sign-off.
- **Blockchain / decentralized scoring / on-chain financial passport — DEFERRED.** Architecture novelty with no bearing on our current evidence problem. Note only.

**Why this filtering matters:** the mandate says reject weak ideas and never let AI-impressiveness substitute for validity. Half of the brief is exactly the kind of impressive-sounding, weakly-evidenced, boundary-crossing capability we are required to decline.

## 7. Performance & storage design

- **Feature store.** Precompute per-customer feature vectors into a versioned `feature_store` table (`musteri_id`, `feature_version`, the feature columns, `hesaplandigi_zaman`) so scoring is an **O(1) lookup**, not a re-extraction. Today `/portfoy` and `/adalet` re-score *all* customers per call — the feature store removes that cost.
- **Caching (already in place).** Portfolio/fairness aggregates cached in Redis (TTL 600s); keep. Add cache invalidation keyed on `feature_version`/`calibration_version`.
- **Indexing / partitioning.** Index on `(persona, feature_version)` for per-segment evaluation and on `alindigi_zaman` for out-of-time splits. Partition transactions by customer for range scans.
- **Immutability & separation.** Raw ingest, feature store, labels, and audit log are **separate stores** — never mutate raw or audit in place; recompute features into a new version. This is both a performance choice (append-only, cache-friendly) and the leakage/boundary guarantee.
- **Model artifacts** stay versioned (`aks_model.joblib` + `metrikler.json` + a calibration manifest), pinned `numpy<2`.

## 8. How this maps to the product folders (task index)

| Product folder | Task | What it owns in this plan |
|---|---|---|
| `product/01-data` | #19 | Raw transaction schema + T1 columns; **non-circular label generation**; data dictionary + validation/PII-tagging |
| `product/02-ai-agents` | #20 | Feature extraction for new columns; **Formulation B target** (`pd_davranissal`, `pd_geleneksel_bant`, `pd_fark`, `kapasite_sinyali`) + per-segment calibration |
| `product/04-backend` | #21 | `feature_store`, `data_provenance`, `consent` tables; extend `Customer/Assessment/AuditLog`; migrations; API fields; point-in-time correctness |
| `product/03-frontend` | #22 | Surface PD-gap / capacity / calibration + provenance/consent state in the 5 pages |
| `product/05-business` | #23 | Hypothesis registry, KVKK classification, lawful-basis mapping, DPIA + human-oversight posture, out-of-scope register |

Sequencing: **19 → 20 → 21 → 22**, with **23 (governance) running in parallel** and gating any T1/T2/T3 column before it may be populated. All modeling work remains gated on the non-circular benchmark (execution.md **M4** / OQ-36).
