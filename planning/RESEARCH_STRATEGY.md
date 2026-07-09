# Research Strategy & Operating Charter

**Status:** Active, supersedes prior "bootcamp demo" framing wherever the two conflict. This document records (1) the operating mandate this project is now held to, (2) a code-grounded critical assessment of the current system against that bar, and (3) the re-prioritized research/engineering roadmap. It does not edit `/planning`'s original Early Phase package or `TECHSTACK.md`/`ROADMAP.md` — it sits above them as the quality bar those documents' execution is now measured against.

---

## 1. Operating mandate (condensed)

The project's long-term objective is a venture-fundable fintech decision layer, not a bootcamp submission — the bootcamp is the first validation milestone, not the target. Condensed rules:

- **Mission:** discover repayment capacity the traditional pipeline misses (thin-file, students, interns, freelancers, gig workers) — *not* replace the bank's model, *not* predict default in general, *not* generate a new universal credit score.
- **Statistical validity > AI.** Classical/deterministic methods win by default; an AI/LLM/agent component must clear five questions before it's allowed to exist: what exact problem does it solve · why can't classical ML solve it · why does it need an LLM/agent specifically · how is its value measured · how is its improvement validated. Fails any → remove or rename it.
- **Priority order (binding on every decision):** 1) prediction accuracy → 2) generalization → 3) calibration → 4) robustness → 5) interpretability → 6) business value → 7) regulatory compliance → 8) engineering quality → 9) AI → 10) UI.
- **Research mindset:** challenge assumptions, reject weak ideas, never agree by default. Every model needs a stated baseline, expected gain, evaluation metrics, failure modes, ablation strategy, CV strategy, calibration strategy, confidence estimation, robustness analysis, business impact — decided *before* implementation, not after.
- **Agents must own real responsibility** (clear inputs/outputs/authority/limitations, deterministic validation, audit trail, failure handling, success metrics) or they get removed.
- **Engineering:** modular, reproducible, deterministic pipelines, typed interfaces, experiment tracking, auditability, explainability, observability.

## 2. Critical assessment of the current system

### 2.1 Fatal finding: the headline benchmark is circular

Traced directly in code (not inferred):

**`aks_core/model/etiketleme.py`** — the default label is generated as:
```python
z = 4.0*(gider_gelir_orani - 0.85) - 0.7*clip(bakiye_trendi, -3, 3) - 1.2*gelir_duzenliligi - 0.7*fatura_odeme_duzeni
p = sigmoid(intercept + z + N(0, 0.9))      # intercept binary-searched to hit target default rate
temerrut = Bernoulli(p)
```
Only 4 of the 9 engineered features causally drive the label. There *is* injected Gaussian noise (std 0.9) representing unobserved factors, and the final draw is stochastic (not a hard threshold) — this is better than a naive deterministic rule, but does not fix the core issue below.

**`aks_core/model/egitim.py::klasik_risk_skoru`** — the "classical" baseline:
```python
skor = base_by_persona + 0.001 * toplam_gelir_hacmi   # persona (income-status proxy) + income volume only
```
This baseline is structurally barred from seeing any of the 4 variables the label depends on.

**The XGBoost/LightGBM model** is trained on all 9 features, which includes the exact 4 causal variables, unperturbed, verbatim.

**Consequence:** the comparison "behavioral model AUC 0.829 vs classical AUC 0.729" is not evidence that alternative/behavioral data reveals hidden repayment capacity. It is a restatement of "a model that observes a variable's causal drivers outperforms a model that cannot observe them" — true by construction, for any model class, on any dataset, in any domain. A plain logistic regression on the same 4 features would score at or near XGBoost's AUC, because the data-generating process is linear-in-logit over exactly those inputs — there is no nonlinear interaction structure for a tree ensemble to exploit that a correctly-specified GLM wouldn't already capture. **XGBoost's complexity is not currently earning its keep; this is testable and should be tested (§4, action A2).**

Everything downstream inherits this circularity:
- **Business impact (973/1084 "rescued", 90%)** — same tautology: the model recovers customers whose true noisy default probability was constructed, by design, to be low for behavioral reasons the classical score can't see.
- **Fairness result (0.4% → 97.8% approval, gap 1.00 → 0.39)** — persona is a confounder correlated with the label's causal features (by generator design); the "fairness improvement" is the same circularity viewed through a demographic lens, not an independent finding.

None of these numbers are *false* — they correctly demonstrate the pipeline's mechanics work end-to-end (feature extraction → calibrated probabilistic labels → model recovers signal under noise → API → audit trail). But **none of them currently support the business thesis**, and presenting them as if they do is exactly the kind of claim priority #1 (prediction accuracy) exists to prevent. This must be fixed before any further claims are made in the product README, the pitch narrative, or the jury deck.

**Empirical confirmation, with an important refinement:** §4 (A1) ran the ablation this section predicts. The core prediction held (XGBoost ≈ logistic regression ≈ logistic-on-4-causal-features-only, within noise). But the "other 5 features carry ~zero signal" sub-claim was *wrong* — they alone reach 0.82 AUC — which reveals the confounding is structural (via persona-conditioned generation of the whole feature vector), not limited to the 4 literally-causal columns. Read §4 before drawing conclusions from this section alone.

### 2.2 Secondary statistical gaps (real, but subordinate to §2.1)

| Priority | Gap | Current state |
|---|---|---|
| Generalization | No k-fold/repeated CV; single 70/30 split, no CI on AUC/AP | One `train_test_split(random_state=42)` |
| Generalization | No out-of-persona generalization test (train on 3 personas, test on held-out 4th) | Not attempted |
| Calibration | No Brier score, ECE, or reliability diagram; no per-segment calibration check | Not measured at all |
| Robustness | No small-sample / sparse-history behavior test — exactly the thin-file regime this product targets | Not tested |
| Robustness | No adversarial/gaming resistance check (can a user structure transactions to inflate `gelir_duzenliligi`?) | Not considered |
| Robustness | No drift/PSI monitoring despite `Orkestrator` tracking score-over-time | Not built |
| Interpretability | SHAP exists (good) but no monotonicity constraints — a feature's effect on score can flip sign in ways that are hard to defend to a regulator | Not constrained |
| Engineering quality | Fixed hyperparameters (`n_estimators=300, max_depth=4`), no search, no experiment tracking | Hardcoded |
| Engineering quality | `random.seed(7)` is a *global* seed reused identically on every label-generation call — fine for demo reproducibility, but means any bootstrap/resampling analysis using this generator will silently understate uncertainty unless seeding is handled per-resample | Confirmed in code |

### 2.3 AI-component audit (five-question test)

| Component | Real responsibility? | Verdict |
|---|---|---|
| `VeriAgent` | Deterministic feature extraction, pure function | **Not an agent.** Rename to a pipeline stage in any jury-facing material; keep the code as-is. |
| `SkorlamaAgent` | `model.predict_proba()` + scaling | **Not an agent.** Scoring service. |
| `DanismanAgent` | Template-fills SHAP into advice text | **Not an agent — and that's correct.** Should stay deterministic; do not add an LLM here without a specific justification, since templated NLG is more auditable and this is a regulated-adjacent explanation surface. |
| `Orkestrator` | Sequential coordinator + in-memory log | **Not an agent.** Orchestration code. |
| `AsistanAgent` | Gemini Q&A grounded in precomputed context; deterministic fallback | **The one genuine agent.** Passes all five questions: solves open-ended NL interface over fixed facts, classical code can't do that, LLM is the right tool, value = user comprehension/trust (measurable via task success + hallucination rate), validated by grounding checks. **Needs hardening**: must never be allowed to state a number not present in `baglam`; needs a hallucination-rate eval harness before it can be trusted in a compliance-adjacent surface. |
| Fairness audit (`adalet.py`) | Deterministic equal-opportunity statistics | **Not an agent — correct as-is.** Do not wrap it in agent framing even though `TECHSTACK.md`/`ROADMAP.md` call it a "fairness-audit agent." |

**Bottom line:** of the "3–5 agent architecture" used in the bootcamp narrative so far, exactly one component (`AsistanAgent`) is agentic under this bar. This creates tension with the earlier session's `TECHSTACK.md`/`ROADMAP.md` framing of BWS3 as "★ highest jury weight, multi-agent architecture." That framing is not being silently walked back — it's flagged here for a decision (§5).

## 3. Re-prioritized roadmap

Ordered per §1's priority list, not per bootcamp sprint convenience:

1. **Prediction accuracy (validity first).** Fix the circular benchmark (§4 A1/A2) before reporting any AUC/business number as evidence of anything beyond pipeline correctness.
2. **Generalization.** Repeated stratified k-fold with bootstrap CIs on AUC/AP; out-of-persona holdout; if/when real data is available, out-of-time split.
3. **Calibration.** Brier score, ECE, reliability diagrams, globally and per-persona; consider isotonic/Platt on top of XGBoost's raw output; calibration is not optional given the product recommends a specific credit limit number.
4. **Robustness.** Small-sample/sparse-history stress test (thin-file *is* the target segment — the model must degrade gracefully, not confidently, when data is sparse); basic gaming-resistance review of the 4 causal features; PSI-based drift monitoring hook.
5. **Interpretability.** Add monotonic constraints to XGBoost aligned with domain priors (e.g. `gider_gelir_orani` ↑ ⇒ risk ↑ monotonically); standardize SHAP output into adverse-action-style reason codes.
6. **Business value.** Rebuild the revenue/loss estimate on a RAROC-consistent basis (expected loss + capital/funding cost, not a flat loss-rate heuristic) — matches what the original planning package's H6 already specifies; only recompute headline numbers once §4 A1/A2 is resolved.
7. **Regulatory compliance.** Carry forward the existing regulatory-awareness posture (`bootcamp-adaptation-review.md` ADAPT A3); add monotonicity + reason codes as concrete technical answers to explainability obligations.
8. **Engineering quality.** Hyperparameter search (not hardcoded), lightweight experiment tracking (even a logged JSON manifest is better than nothing), per-resample seeding discipline, finish porting the test suite (already flagged as a known gap in `PRODUCT_TECH_README.md` §11).
9. **AI.** Apply §2.3's verdicts: rename non-agentic components in jury-facing material, hard-guard `AsistanAgent` against hallucinated numbers, decide (§5) whether to invest in one more *genuinely* justified agent or lean into "one real agent, honestly described" as the stronger research story.
10. **UI.** Continue, but never let UI/Stitch-integration work block items 1–8. This was already de-prioritized correctly in the current build sequencing; no change needed, just confirming it stays last.

## 4. Immediate action items

### A1 — Ablation proof (DONE — results below, findings refine §2.1)

Implemented as `product/02-ai-agents/aks_core/model/circularity_ablation.py` (5-fold stratified CV, bootstrap 95% CI, run against the live `sentetik_islemler.csv`). Reproducible via `python -m aks_core.model.circularity_ablation`.

| Model | AUC (mean) | std | 95% CI |
|---|---|---|---|
| Oracle (Bayes-optimal — true generating probability vs. realized label) | 0.9006 | — | theoretical ceiling |
| XGBoost, 9 features (current production model) | 0.8525 | 0.0257 | [0.833, 0.879] |
| Logistic regression, same 9 features | 0.8529 | 0.0359 | [0.825, 0.889] |
| Logistic regression, **only the 4 label-causal features** | 0.8547 | 0.0351 | [0.828, 0.890] |
| Logistic regression, **only the 5 "non-causal" features** | 0.8235 | 0.0361 | [0.795, 0.860] |

**Confirmed as predicted:** XGBoost vs. 9-feature logistic regression differ by **0.0004 AUC** — statistically indistinguishable given the fold std (~0.03). The 4-causal-only model matches the 9-feature model within **0.0018 AUC**. This is clean, direct evidence that (a) XGBoost's ensemble complexity is buying nothing on this data-generating process, and (b) the model's entire AUC advantage is explained by the 4 features that literally construct the label. Per the mandate's own rule ("if a classical statistical method performs better, always choose it") — **logistic regression on 4 features should replace XGBoost on 9 as the reported baseline until a real generalization test says otherwise.**

**Not predicted, and more important:** the 5 "non-causal" features alone still reach **0.8235 AUC** — far above chance (0.50), not near it. This means the circularity is *not* limited to the 4 features that literally appear in the label formula. The simulator's persona-conditioning shapes the joint distribution of **all 9 features simultaneously**, so every feature subset carries confounded signal about the label through shared dependence on persona/archetype — not through any genuine causal or even correlational financial-behavior mechanism. **This is a stronger, more structural version of the circularity finding than §2.1 originally stated**, and it means the fix (§2.1 Option A) cannot be "just hide the 4 causal columns from the model" — the confounding is baked into the generator's joint distribution itself, not isolated to specific columns. Any redesign must decouple *persona-conditioned feature generation* from *label generation* at the generator level (e.g., draw a customer-level latent capacity independently within each persona's plausible range, rather than letting persona tightly determine the whole feature vector which then near-deterministically implies the label via any reasonable functional form).

XGBoost reaches 94.7% of the oracle AUC (0.8525 / 0.9006) — consistent with "recovering a known, roughly-linear generating rule reasonably well," not "discovering hidden nonlinear structure via ML."

### Remaining items (not yet done)

- **A3 — CV + CI in production training.** Port the k-fold + bootstrap-CI methodology from `circularity_ablation.py` into `aks_core/model/egitim.py` itself, replacing the single holdout. Cheap, no design change, immediately more defensible.
- **A4 — Calibration report.** Add Brier/ECE/reliability-diagram reporting to `egitim.py` output.
- **A2 — Simulator redesign** (structural fix). Blocked on **OQ-36** (real data access) — if real data exists, prefer it over redesigning the simulator; if not, redesign per the corrected diagnosis above (decouple persona-conditioned feature generation from label generation, not just from the 4 causal columns).

## 5. Decisions requiring your input (not guessed)

- **OQ-36 — Real benchmark data access.** Is there access to any real dataset with genuine repayment outcomes (Home Credit Default Risk / Kaggle, LendingClub loan-level data, an open-banking sandbox, a university/industry dataset)? This determines whether we can validate the actual business thesis against real outcomes (the gold-standard fix) versus being limited to redesigning the simulator to remove circularity (a weaker but still-honest fallback, §2.1). This is the single highest-leverage decision in the whole roadmap.
- **OQ-37 — Sequencing vs. bootcamp deadline.** The circularity fix (§4 + a simulator redesign) will change the headline AUC/business/fairness numbers currently published in `product/PRODUCT_TECH_README.md` and `planning/README.md`. Do you want this done now (before further UI/agent work, per the priority order), or sequenced to land right after the current bootcamp deadline, with the existing numbers kept but explicitly caveated in the meantime?
- **OQ-38 — Agent narrative.** Given §2.3's finding (1 real agent, not 3–5), do you want the jury-facing narrative corrected to "one well-justified agent, honestly scoped" now, or do you want to invest in making one additional component (most plausible candidate: an explanation/recommendation *ranker* that does genuine constrained optimization over candidate interventions, not just a template lookup) into something that actually passes the five-question test before demo day?

These are logged as OQ-36…OQ-38 in `00-program/open-questions.md` for traceability with the rest of the project's open-questions discipline.
