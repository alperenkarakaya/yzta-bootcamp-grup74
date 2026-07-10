# AKS — Project Overview

**This is the single entry point for the entire project. Read this file first in any session.**
Two companion documents complete the source of truth:

- **[architecture.md](architecture.md)** — the engineering specification (how the system is built and *why* every component exists).
- **[execution.md](execution.md)** — the live plan (sprint, backlog, priorities, research tasks, risks, technical debt).

These three files are the *only* project-level documentation. If something is not written here, it is not decided. When a decision changes, the relevant file is updated in place — history is not archived.

> **Language note:** these docs are English (the working language for engineering and AI sessions). Code identifiers, personas, and the boundary thesis stay in their original Turkish because the codebase is Turkish. Both are authoritative.

---

## 1. Project & startup vision

**AKS (Alternatif Kapasite Skoru — "Alternative Capacity Score")** is a behavioral credit-decision *bridge layer*.

The long-term objective is a **venture-fundable fintech decision layer**, not a bootcamp submission. The bootcamp (YZTA Bootcamp Grup 74) is the first validation milestone, not the target. Every decision is made as if this will be operated at a real bank and audited by a real regulator.

The startup wedge: banks systematically **under-lend to behaviorally-strong, thin-file customers** (students, interns, freelancers, gig workers) because traditional pipelines read *formal declared income* and little else. That is foregone revenue for the bank and unfair rationing for the customer. AKS surfaces the repayment capacity the traditional pipeline **fails to recognize**, so the bank can safely approve more of those customers at a controlled bad rate.

## 2. Problem definition

Traditional credit/limit assessment is dominated by **formal income declaration**. A person who is high-volume, regular, and disciplined in their account activity but formally looks like a "student", "intern", or "freelancer" receives a credit limit far below their true repayment capacity.

- For the **customer**: under-served, pushed toward BNPL / P2P / informal credit.
- For the **bank**: an invisible-but-recoverable revenue loss — a large segment of low-risk-but-low-scored customers is either not lent to or lost to alternative channels. The loss concentrates in small-ticket credit but exists across the book.

## 3. Current solution

From account transactions we extract **9 behavioral features** (income volume, expense volume, income transaction count, income-source diversity, income regularity, expense/income ratio, balance trend, bill-payment discipline, account-activity intensity) and produce an **alternative capacity signal that is independent of formal income**.

The productized target is **not** a default predictor and **not** a new universal score. It is defined (see §7 and architecture.md §5) as a **calibrated behavioral capacity signal plus a PD-gap overlay** against the traditional-band-implied risk — i.e. *"where does behavioral evidence say there is more capacity than the thin file implies?"*

## 4. Business thesis

> Officially thin-file customers are under-classified by a system that only reads formal income. Behavioral transaction evidence reveals repayment capacity that the traditional file misses, letting the bank approve **materially more good thin-file customers at a fixed, controlled bad rate.**

The bank buys **incremental approvals of good thin-file customers at controlled risk** — the foregone-revenue recovery story. The headline metric is therefore *not* aggregate AUC; it is **incremental approval rate at a fixed bad-rate on the thin-file subpopulation, with a calibration guarantee** (see architecture.md §6).

## 5. Statistical philosophy (binding)

**Statistical validity outranks AI.** This is the governing rule of the whole project.

- **Priority order — binding on every decision:** 1) prediction accuracy → 2) generalization → 3) calibration → 4) robustness → 5) interpretability → 6) business value → 7) regulatory compliance → 8) engineering quality → 9) AI → 10) UI.
- **Classical/deterministic methods win by default.** If a classical statistical method performs at least as well, it is chosen. (This is not abstract: logistic regression currently equals-or-beats XGBoost on this data — see §14 and architecture.md §5.)
- **Evaluation-first.** Every model states its baseline, expected gain, evaluation metrics, failure modes, ablation strategy, CV strategy, calibration strategy, and business impact *before* implementation — not after.
- **Anti-goal-seeking.** Acceptance thresholds are fixed (with numbers) *before* results land.

## 6. AI philosophy (binding)

Every AI / LLM / agent component must pass a **five-question test** or be removed or renamed:
1. What exact problem does it solve?
2. Why can't classical ML solve it?
3. Why does it specifically need an LLM/agent?
4. How is its value measured?
5. How is its improvement validated?

**LLMs must never become the decision engine.** The result of applying this test honestly (architecture.md §4): of the components historically narrated as a "3–5 agent architecture", exactly **one** — `AsistanAgent` (a grounded Q&A assistant) — is genuinely agentic. The rest are deterministic pipeline stages and are named as such.

## 7. Boundary principles (the one rule that shapes the whole architecture)

> **AKS bankanın klasik skorunu/segmentini asla ezmez veya değiştirmez — yalnızca tamamlar.**
> *(AKS never overrides or changes the bank's classic score/segment — it only complements it.)*

The bridge layer shall **never**: re-score the customer inside the bank's model, override the segment automatically, adjust the engine's inputs, or auto-approve above policy. This is not a paper promise — it is enforced in code: every scoring writes an **immutable audit row** that records the bank's classic score *unchanged*. See architecture.md §9 (policy + audit layer).

## 8. Current architecture summary

```
React (Vite + TS)  →  Django + DRF API  →  aks_core (pipeline + the one real agent, ML, SHAP, fairness)
                                              │
                                              ├─ Supabase (Postgres): customers · assessments · immutable audit_log
                                              └─ Upstash Redis: cache for portfolio/fairness aggregates
```

The AI/ML core (`aks_core`) is an installable Python package imported identically by the API and by CLI/research scripts. All external services (Supabase, Upstash, Gemini) are **optional** — absent credentials, the system degrades gracefully to SQLite + in-memory cache + rule-based assistant, so the demo always runs. Full detail: architecture.md.

## 9. Technology stack summary

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + Vite 5 + TypeScript | Polished multi-view bank panel; hosts the Google Stitch design |
| Backend / API | Django 5.2 + Django REST Framework 3.17 | Batteries-included ORM + migrations + read-only admin (free audit browser) + auth; pairs with Supabase Postgres |
| AI core | `aks_core` installable package (pipeline + `AsistanAgent`) | One clean import for both API and research scripts |
| ML | scikit-learn (logistic regression — **preferred**), XGBoost / LightGBM (under review, see §14) | Simplest model that wins; complexity must be earned |
| Explainability | SHAP → adverse-action-style reason codes | Regulatory-adjacent explanation surface |
| LLM | Google Gemini (optional), deterministic rule-based fallback | The single justified agent; never the decision engine |
| Database | Supabase (Postgres) via Django ORM; SQLite fallback | Assessments, per-customer history, immutable audit trail |
| Cache | Upstash Redis (`django-redis`); LocMem fallback | Cache heavy portfolio/fairness aggregates |
| Deploy (target) | Docker + Render; Supabase + Upstash hosted | One web service |

**Verified toolchain:** Python 3.11.9 · Node 18.14.0 · npm 9.3.1 · Django 5.2.16 · DRF 3.17.1 · Vite 5.4.21. **`numpy<2` is pinned** (model artifacts built against NumPy 1.x).

## 10. Directory structure

```
credit-calc/
├── overview.md              ← this file (entry point)
├── architecture.md          ← engineering specification
├── execution.md             ← live plan / backlog / risks
├── CLAUDE.md                ← thin session router (points here)
└── product/                 ← the actual build, 5 sections
    ├── 01-data/             synthetic transaction generator, datasets, EDA
    │   └── generator/veri/uretici.py, datasets/*.csv
    ├── 02-ai-agents/        aks_core installable package (pyproject.toml)
    │   └── aks_core/{ozellik, model, agents, artifacts}
    ├── 03-frontend/         React + Vite + TS + Tailwind, 5 pages (Google Stitch UI, integrated)
    ├── 04-backend/          Django + DRF, audit app, settings, requirements
    │   └── {config, api, audit}/   (+ _legacy_fastapi/ reference only)
    └── 05-business/         domain docs, sprint evidence (screenshots, scrum notes)
```

The five product sections map 1:1 to five workstreams: 01-data, 02-ai-agents (highest weight), 03-frontend, 04-backend, 05-business.

## 11. Completed components

- Synthetic transaction generator + 9-feature extraction pipeline (`aks_core.ozellik`).
- Trained model artifact + baseline comparison (`aks_core.model.egitim`, `etiketleme`).
- SHAP explainability, equal-opportunity fairness report, business-impact analysis.
- Deterministic pipeline (`VeriAgent → SkorlamaAgent → DanismanAgent`, `Orkestrator`) + `AsistanAgent` (Gemini/rule-based).
- Django + DRF backend: **11 endpoints**, verified at parity with the retired FastAPI backend.
- Immutable audit trail (`Customer`, `Assessment`, `AuditLog`) with read-only Django admin.
- Supabase + Upstash integration code (graceful fallback) + `check_connections` diagnostic.
- React + Vite + TS + Tailwind frontend: 5 pages (Intelligence, Portfolio, Audit, Customers, Customer Detail) implementing the Google Stitch design, wired live to every real `/api/*` endpoint — no fabricated data or invented compliance claims.
- **Statistical evaluation harness** (`degerlendirme.py`) and **circularity diagnostic** (`circularity_ablation.py`) — reproducible.

## 12. Current limitations

1. **The headline benchmark is circular** (see §14). Published numbers (AUC 0.829, "973/1084 rescued", fairness gap 1.00→0.39) prove the *pipeline works end-to-end*, **not** the business thesis. Do not cite them as validated. This is the top blocker.
2. **XGBoost is unjustified.** Logistic regression equals/beats it on AUC, PR-AUC, and calibration; the model swap is gated on the benchmark fix.
3. **Target segment performance is weak.** Within the primary target (`ogrenci_yuksek_hacim`) AUC is only 0.61–0.68 — weakest exactly where the product claims value.
4. **No real data yet.** Everything runs on synthetic data (OQ-36).
5. **Test suite not ported.** The 22 Sprint-2 tests still import FastAPI/`src.*`; not migrated to Django/`aks_core`.
6. **Deploy config not updated.** Docker/Render still targets the retired FastAPI single-service setup; needs to serve the React build via Django (E12).

## 13. Future roadmap summary

Ordered by the §5 priority list, not sprint convenience (full task table: execution.md):

1. **Fix the circular benchmark** — either validate against real data (Home Credit, OQ-36) or redesign the simulator to decouple persona-conditioned feature generation from label generation.
2. **Generalization** — repeated stratified k-fold + bootstrap CIs, out-of-persona holdout, out-of-time split when real data exists.
3. **Calibration** — Brier/ECE/reliability, global and per-segment; isotonic/Platt if needed.
4. **Robustness** — thin-file small-sample stress test, gaming-resistance review, PSI drift monitoring.
5. **Interpretability** — monotonic constraints + adverse-action reason codes.
6. **Business value** — rebuild the revenue/loss estimate on a RAROC-consistent basis; report the decision-curve metric.
7–10. Regulatory posture, engineering quality (hyperparameter search, experiment tracking, port tests), agent-narrative honesty, then UI.

## 14. Important engineering decisions

- **Circularity finding (fatal, code-grounded).** The default label in `etiketleme.py` is generated from 4 of the 9 features the model then trains on; the "classical baseline" is structurally barred from those 4. So "behavioral 0.829 vs classical 0.729" is true *by construction* for any model class — not evidence of hidden capacity. Ablation confirmed: XGBoost vs 9-feature logistic regression differ by **0.0004 AUC**; and the confounding is *structural* (the 5 "non-causal" features alone still reach 0.82 AUC via persona-conditioning), so the fix cannot be "hide the 4 columns" — it must decouple feature generation from label generation at the generator level, or move to real data.
- **Target definition = Formulation B** (calibrated behavioral capacity + PD-gap overlay), engineered to graduate into C (uplift/reject-inference) once a design-partner bank provides champion/challenger data. Rejected A (within-segment risk ranking) because it *is* default prediction, which the mission forbids, and carries the heaviest regulatory load. This makes **calibration, not raw AUC, the headline metric.** Full comparison: architecture.md §5.
- **Prefer logistic regression over XGBoost** until a non-circular benchmark says otherwise (mandate: classical wins by default).
- **One real agent, honestly scoped.** `AsistanAgent` passes the five-question test; the other "agents" are renamed to pipeline stages in any jury-facing material.
- **Django replaced FastAPI** for the free admin/ORM/migrations/auth that the audit-trail and Supabase requirements need. Old FastAPI kept in `_legacy_fastapi/` for reference only.
- **All external services optional** — the product must run offline for the demo.

### Live open decisions (owner: Product Owner Alperen Karakaya)

- **OQ-36** — Real benchmark dataset access (Home Credit / LendingClub / open-banking sandbox)? *Highest-leverage decision in the project.*
- **OQ-37** — Fix the circular numbers now (changes published figures) or after demo day (keep + caveat)?
- **OQ-38** — Correct the agent narrative to "one real agent" now, or invest in making a second component genuinely agentic first?
- **OQ-39** — Ratify Formulation B (proposed; proceeding unless the founder objects).

Team: Product Owner **Alperen Karakaya**; Scrum Master Ahmet Özdoğan; Developers Zeynep Salkaya, Havva Balta, Begüm Bakan.
