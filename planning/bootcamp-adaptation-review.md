> **⚠️ Superseded on priorities (2026-07-10).** This review's "LIFT" argument — that AI/agentic architecture is now in-scope and high-value for jury scoring — is **partially overridden** by `RESEARCH_STRATEGY.md`, which subordinates AI to priority #9 (below statistical validity, calibration, robustness, and engineering quality) and found that only 1 of the 5 named "agents" survives a justification audit. This document remains valid for the KEEP/ADAPT/RISK analysis and the synthetic-data/persona/regulatory-awareness reasoning; treat its AI-enthusiasm framing as historical. Read `RESEARCH_STRATEGY.md` for current priorities.

# Bootcamp-Lens Adaptation Review
## Re-reading the Early Phase Working Package for an AI & Technology Bootcamp

**Status:** Delta layer over the original planning package. **Nothing in this file edits the source of truth** (`early-phase-plan-credit-offer-optimization.md`) or the 50 planning artifacts. It records how each is re-interpreted for a bootcamp context where evaluation rewards agentic AI architecture, state-of-the-art technique, novel technology, and a working, demonstrable product.

**Context shift (confirmed):** This is a bootcamp capstone, not a real bank engagement. There is no real bank, no real customers, no real regulator, no real credit bureau, and no procurement/legal function. The original package was written under real-consulting scope discipline — *"no solution design, no algorithms, no ML models, no architecture"* (source line 7). That discipline was correct for a bank client whose production model is a regulated asset. It is **not** the winning posture for a bootcamp jury, which explicitly rewards building.

**What does NOT change (binding on this review and every workstream):**
- **The hard domain boundary stays intact.** The bridge layer optimizes offers *within* policy; it **never re-scores customers, never overrides the bank model's segment automatically, never adjusts the engine's inputs, never auto-approves above-policy limits** (source §4, §6). In the bootcamp we *build* the layer, so this boundary moves from a promise-on-paper to a **hard-coded architectural constraint** (a policy-guard agent + audit trail that make override structurally impossible). This is simultaneously our domain integrity and our strongest jury narrative.
- **"No-go is a valid outcome"** (source §10) survives as intellectual honesty in the demo: we show what the evidence supports and what it does not.
- **Data minimization discipline** survives conceptually: every synthetic field exists to make a specific hypothesis testable.
- **Traceability discipline** survives and is extended: every build task still traces to a source ID or to this review.

---

## How to read this document

Each item below is a **delta**: `ORIGINAL → BOOTCAMP`. Deltas are grouped into the four requested lenses:

- **§1 KEEP** — valuable as-is; carry forward unchanged.
- **§2 ADAPT** — reinterpret for bootcamp reality (no real data / stakeholders / legal / timeline).
- **§3 LIFT** — prohibitions removed; now in scope and strategically important for scoring.
- **§4 RISK** — what adaptation costs us, and how to present it honestly to the jury.
- **§5** — open decisions routed to `00-program/open-questions.md` (OQ-27+).
- **§6** — how the deltas feed the five bootcamp workstreams.

---

## 1. KEEP — valuable as-is

These are the intellectual assets of the package. They cost real analytical effort, they are what makes the project sound rather than a toy, and a jury reads them as evidence of rigor. **Carry them forward unchanged.**

| # | Asset (source ref) | Why it stays valuable in a bootcamp | Where it lands |
|---|---|---|---|
| K1 | **Problem decomposition P1/P2/P3** (§1.1) — misclassification vs. coarse segmentation vs. conservative offer mapping | This is the intellectual spine of the whole project. It proves we understand that "customers get low offers" has three different causes with three different fixes. A jury sees a team that framed the problem, not just coded a demo. | WS1 owns it; every other WS references it. |
| K2 | **The "diagnose the mix" insight** (§1.1 critical framing) — the value proposition changes depending on whether P1, P2, or P3 dominates | Elevates the demo from "we built a thing" to "we built the *right* thing and can prove why." | WS1 narrative; WS2 encodes a known P1/P2/P3 mix into synthetic data so the diagnosis is demonstrable. |
| K3 | **Hypotheses H1–H14 as an evaluation narrative** (§5) | Reframed from "things we'd test with bank data" to "the claims our product makes, each with a demonstration." Falsifiability is a rigor signal. See §2 for the data-adaptation. | WS1 curates the narrative; WS2 makes each testable; WS3/WS4 demonstrate. |
| K4 | **Opportunity catalogue O1–O8** (§4) | A ready-made, pre-prioritized feature backlog ordered by governance friction. O1/O2/O4/O6 become the actual product surface. O5 (under-lending measurement) becomes our headline metric. | WS4 builds O1/O2/O4/O6; WS1/WS5 instrument O5. |
| K5 | **The bright-line boundary** (§4 out-of-scope list, §6) | The single most defensible design decision. In a field of teams that "let the AI decide," we are the team whose AI provably *cannot* override the bank. | Enforced by WS3 (policy-guard agent) + WS5 (audit trail); narrated by WS1. |
| K6 | **Risk register structure** (§6, `05-risk-and-compliance/risk-register.md`) — Business / AI / Regulatory / Operational / Data | A build project needs a risk register too. Several risks (ground-truth ambiguity, feedback loops, bias amplification, opacity, silent scope creep) are *more* relevant once we actually build. | WS1 maintains; WS3 mitigates AI risks in architecture. |
| K7 | **Exit criteria E1–E10 as sprint/demo gates** (§10) | Repurposed as internal gates: E1→"is the modelled problem material in our synthetic world?", E2→"is our ground-truth definition explicit?", E6→"is there a working insertion point?" (now literally true — we build it), E10→"go/no-go on demo readiness." | WS-level DoDs and `workstreams.md` sprint gates. |
| K8 | **Traceability discipline** (`TRACEABILITY.md`) | Rare in a bootcamp; a strong execution-quality signal. Extended with a workstream column. | Cross-cutting; owned jointly, checked weekly. |
| K9 | **Success-metrics thinking** (§8) — especially "a KPI without a baseline is a story, not a metric" | We *can* measure baselines now, because we generate the data and thus know ground truth. This turns a Phase-1 weakness (no baseline) into a bootcamp strength (perfect baseline). | WS1 defines; WS2 provides ground truth; WS5 instruments. |
| K10 | **Stakeholder tension analysis** (§3) — Risk vs. Business shared-metric problem | Becomes the *story* behind our product: the bridge layer exists to give Risk and Business a shared, risk-adjusted metric. Personas (see A3) dramatize it in the demo. | WS1 → personas; WS4 → demo script. |
| K11 | **Ground-truth / selective-labels awareness** (§6.2, §2.4 counterfactual note) | Knowing *why* "deserved segment" is hard is exactly what lets us design honest synthetic data — and lets us pre-empt the jury question "how do you know you're right?" | WS2 implements a defensible ground-truth; §4-R1 frames the honesty. |

**KEEP principle:** the analytical package is the moat. Teams that only build a demo cannot retrofit this depth. We lead with it.

---

## 2. ADAPT — reinterpret for bootcamp reality

Each adaptation is a delta. The left side is what the source assumed; the right side is the bootcamp substitute. The **intent** of each original artifact is preserved; only its *mechanism* changes.

### A1 — No real bank data → **synthetic / simulated data strategy**
- **ORIGINAL:** Mandatory data (§7.1) delivered by the bank; E5 gates on 100% of §7.1 categories "available and usable"; H1–H8 run as backtests on 24–36 months of real outcomes.
- **BOOTCAMP:** We **generate** a synthetic credit portfolio whose data-generating process we control. Because we author the ground truth (each simulated customer's "true" risk and "deserved" segment), we can make P1/P2/P3 all *demonstrably present* and measurable — something no real bank could hand us cleanly (the counterfactual/selective-labels problem, K11).
- **Delta mechanics:**
  - §7.1 Mandatory items M1–M9 → **fields in the synthetic schema** (scores, segments, timestamps, model version, cut-offs, offers, outcomes, migration history, override logs, policy ranges, per-segment financials). Owned by WS2.
  - §7.2 Useful items U1–U8 → **additional simulated signals** (transaction/behavioral streams, utilization, past limit-increase campaign, attrition with destination, NPS verbatims (LLM-generated), bureau snapshots + refresh dates, exception logs, capital/funding allocation).
  - §7.3 OPT items → **stretch generators**, still gated on a stated hypothesis (minimization discipline survives).
  - E5 "mandatory data dispositioned" → **"synthetic schema covers 100% of M-items and a data-quality/bias report exists."**
- **Honesty hook (feeds §4-R1):** synthetic ≠ real. We validate *mechanism and product behavior*, not real-world effect sizes. Stated up front in the demo.

### A2 — No real stakeholders → **personas + assumption logs**
- **ORIGINAL:** §3 stakeholder map drives 10 interview guides; D3 is an engagement log of *completed* interviews; A9/H12 depend on real governance interviews.
- **BOOTCAMP:** Stakeholders become **named personas** with goals, concerns, and success metrics lifted verbatim from §3 (Customer, Credit Risk, Model Risk, Business, Compliance, Data Science, Product, Executive, Front line, Internal Audit, Regulator). Interview guides become **persona briefs + assumption logs**: instead of "we asked and they said," we state "this is what this role would demand, this is our assumption, here is how the product answers it."
- **Delta mechanics:**
  - D3 "engagement log" → **persona catalogue + assumption register** (each assumption tagged validated-in-sim / assumed / open).
  - The Risk-vs-Business shared-metric tension (§3 tension line) → **dramatized in the demo** via the Risk persona and the Business persona both reading the same risk-adjusted screen.
  - Front-line and Customer personas → drive WS4 UX (staff evidence pack O2, customer explanation O4).
- **Honesty hook:** persona assumptions are labelled as such; we do not claim real validation.

### A3 — No legal/compliance function → **regulatory-awareness write-up (not a signed opinion)**
- **ORIGINAL:** D7 Regulatory & Legal Position Paper, signed by a Chief Compliance Officer; H13 needs a written legal opinion; E4 gates on it; regulatory-workplan assumes real counsel.
- **BOOTCAMP:** D7 becomes a **documented regulatory-awareness section** — a well-researched write-up, explicitly *not* legal advice and *not* signed. It demonstrates that we understand fair-lending, explainability rights, data-protection/purpose-limitation, responsible-lending, and the **EU AI Act high-risk classification of creditworthiness AI** (§6.3), and that our architecture responds to them (explainability by design, policy-bounded actions, audit trail, fairness audit).
- **Delta mechanics:**
  - H13 "legal opinion concludes it's a credit decision model" → **design argument**: we show the layer stays "offer optimization within approved policy" *because the architecture makes overriding impossible* — a stronger, demonstrable claim than a paper opinion.
  - E4 "regulatory path viable (written opinion)" → **"regulatory-awareness note complete + architecture maps each obligation to a control."**
  - H14 fairness audit → **actually executed on synthetic data** (we can, because we control protected-attribute generation) — turning a legally-gated Phase-1 item into a live product feature (WS3 fairness-audit agent).
- **Honesty hook:** flagged prominently as awareness, not counsel; "in a real deployment this requires qualified legal review."

### A4 — 10-week discovery timeline → **compressed bootcamp sprints**
- **ORIGINAL:** Appendix A, 8–10 weeks, six workstreams WS1–WS6 sequenced around real data delivery and governance calendars; critical path = data request → data delivery → ground-truth signature.
- **BOOTCAMP:** The critical path is no longer "wait for the bank"; it is **"generate data → build agents → integrate → demo."** The 10-week plan compresses into the actual bootcamp duration (**unknown — OQ-27**). Sequencing is expressed in `workstreams.md` as **relative sprints** that compress to whatever the real calendar is.
- **Delta mechanics:**
  - Source workstreams WS1–WS6 (Mobilize/Legal/Evidence/Sizing/Alignment/Close) are **re-partitioned** into the five *bootcamp* workstreams (Business, Data, AI Core, Product, Engineering). Note: the source's "WSn" labels and the bootcamp "WSn" labels are **different partitions of the work** — see the mapping in §6 to avoid ID collision.
  - Milestones MS1–MS6 → **sprint gates** tied to demo readiness rather than governance windows.
- **Honesty hook:** none needed; this is internal planning.

### A5 — "Insertion point in a real engine" → **simulated bank engine we build**
- **ORIGINAL:** A8/E6 ask whether the real vendor engine can be intercepted before offer delivery; D2 maps the real decision flow; vendor-contract risk (R-OPS-04).
- **BOOTCAMP:** We **build a simulated bank decision engine** (scores → segments → base offer) with a clean interception seam, and the bridge layer sits after it. E6 ("≥1 viable insertion point") becomes *trivially satisfied and demonstrable* because we design the seam. D2 becomes an **architecture/data-flow diagram of our own system** (still valuable: it shows the boundary and the audit points).
- **Delta mechanics:** vendor/contract risks (R-OPS-04, R-DAT-04) drop to N/A but are **retained in the register with a "sim: N/A, real-world: applies" note** so the demo can speak to real deployment.

### A6 — Real financial sizing (RAROC) → **modelled, illustrative sizing**
- **ORIGINAL:** D5 sizes O1–O8 on real risk-adjusted numbers with Finance; H6 uses the bank's RAROC; E1/E3 gate on real value floors.
- **BOOTCAMP:** Sizing runs on the **synthetic portfolio** with a transparent, simplified risk-adjusted model (revenue − expected loss − capital/funding proxy). Numbers are **illustrative of mechanism**, not forecasts. The *method* (risk-adjusted, not gross; affordability as a hard constraint; per-segment win-win) is preserved and is itself a rigor signal.
- **Honesty hook:** "these are figures from our simulation, chosen to illustrate how the metric behaves, not a market forecast."

### A7 — Sign-off blocks (real named approvers) → **role-tagged internal reviews**
- **ORIGINAL:** Each deliverable (§9) is signed by named bank roles (CRO, CCO, CDO, Steering Committee).
- **BOOTCAMP:** Sign-off blocks become **internal team review checkpoints tagged by the persona whose concern they represent** (e.g., "Risk-persona review passed"). Preserves the discipline of "someone with this concern reviewed this" without inventing real approvers.

**ADAPT summary:** every adaptation keeps the *intent* (rigor, honesty, risk-adjusted thinking, minimization, traceability) and swaps only the *mechanism* (real bank → simulation we control). In several cases (A1, A3, K9) the swap turns a Phase-1 limitation into a bootcamp advantage because we own the ground truth.

---

## 3. LIFT — prohibitions now removed and strategically important

The source's defining constraint (line 7; charter §2; §4 close; document footer) forbids solution design, algorithms, models, and architecture. **For the bootcamp these are lifted and become the highest-scoring work.** Each lift below states what was forbidden, what is now in scope, and the boundary that still holds.

| # | Originally forbidden (source ref) | Now IN SCOPE for the bootcamp | Boundary that still holds |
|---|---|---|---|
| L1 | **Solution design / architecture** ("deliberately excludes … architecture", line 7) | Full system architecture: simulated bank engine + bridge layer + agent orchestration + product UI + audit store. This is D2 turned into a real design. | The bridge layer sits *after* the engine's segment; the seam is one-directional (read segment, optimize offer within policy). |
| L2 | **Algorithms / models** ("excludes … algorithms, models") | Classical ML for within-segment signal separation (H5), stale-score / migration prediction (H2/H8), attrition (H11); LLMs for explanation (O4/H10), NPS verbatim analysis (H9), and agent reasoning. | Models inform *offers within policy* and *explanations/evidence for humans* — never a re-score or an automatic segment change. |
| L3 | **Agentic AI architecture** (not even conceived in source — highest jury weight) | A **multi-agent bridge layer**: analysis agent, policy-guard agent, offer-optimization agent, explanation agent, fairness-audit agent, with an orchestrator. Tool use, structured outputs, RAG over policy docs, an agent-evaluation harness. | The **policy-guard agent is a hard gate**: any proposed offer outside the segment's approved range is blocked and logged. Override is architecturally impossible, not merely discouraged. |
| L4 | **Model experimentation** ("no model building", H5 guard) | Real experimentation: signal-separation experiments within segments, explanation-quality evaluation, fairness metrics computed and compared pre/post. | Experiments demonstrate *mechanism*; results are labelled synthetic; no claim of real-world effect size. |
| L5 | **A working, demonstrable product** (Phase 1 delivered "understanding, not offers", §8.1) | An end-to-end demo: a customer/portfolio flows through the simulated engine, the bridge layer optimizes offers within policy, staff and customer explanations render, the audit trail and fairness dashboard update live. | The product visibly respects the boundary on screen (segment shown as fixed; only the within-policy offer is optimized; every adjustment is logged). |
| L6 | **Novel / state-of-the-art technology** (not in a discovery-only phase) | Modern agent patterns (structured tool-calling, RAG over the policy corpus, LLM-as-judge evaluation of explanations, guardrail agents). This is the "novel technology adoption" scoring axis. | Novelty serves the domain problem; we do not add tech that weakens the boundary or the auditability. |

> **Strategic note on L3/L5:** the agentic architecture (WS3) carries the highest evaluation weight, and its best feature is *also* our boundary story: **the guard agent that makes the bank-override structurally impossible is simultaneously our most advanced AI component and our strongest compliance narrative.** Innovation and integrity are the same artifact. Lead the demo with it.

---

## 4. RISK — what we lose by adapting, and how to present it honestly

Adapting to synthetic data and personas costs us **external validity**. A jury will (and should) ask "how do you know this works in the real world?" The honest answer, prepared in advance, is a strength — evasion is the only losing move.

| # | What we lose | Why it matters | Honest framing for the demo / jury |
|---|---|---|---|
| R1 | **Real-world validity of every effect size** (H1–H8, H11, D5 sizing) — synthetic data proves mechanism, not magnitude | We cannot claim "the bank forgoes $X" or "under-classification is Y% of the portfolio" as fact. | State plainly: *"We generate the data, so we control the ground truth and can prove the product behaves correctly and measurably. We are validating the mechanism and the safety properties, not forecasting a real bank's numbers. Real deployment requires backtesting on the bank's own 24–36 months of outcomes (the original plan's E-gates)."* This turns a weakness into evidence of understanding (K11). |
| R2 | **No real regulatory sign-off** (D7, H13, E4) | We cannot assert the layer is legally "offer optimization not decisioning." | Present the **architectural argument** instead: the layer is *structurally* incapable of overriding the segment or exceeding policy, and every action is auditable — so it maps to the low-friction opportunities (O1–O5) by construction. Label the write-up "regulatory awareness, not legal advice." |
| R3 | **No real stakeholder buy-in** (A9, H12, D3) | The Risk-vs-Business acceptance is asserted via personas, not earned. | Frame personas as *design requirements we engineered against*, and show the shared risk-adjusted metric on screen as the concrete answer to the §3 tension. Be explicit that real adoption needs real governance interviews. |
| R4 | **Selective-labels / counterfactual limits are baked into our own generator** | If we author the ground truth, a skeptic asks whether we made the problem easy for ourselves. | Pre-empt it: publish the data-generating assumptions (WS2 data dictionary), include *hard* cases (thin-file, stale-score, boundary cohorts, noisy overrides) so the product is not solving a trivial world, and show the fairness audit finding *and correcting* a disparity we deliberately seeded (H14 as remediation, not decoration). |
| R5 | **Compressed timeline drops depth somewhere** | We cannot build all of O1–O8 to production quality. | Prioritize O1/O2/O4/O6 for the surface and O5 for the headline metric (per K4); explicitly list deferred opportunities as "designed, not built" with the reasoning — mirrors the source's "no-go is a valid outcome" honesty. |
| R6 | **Agent non-determinism vs. credit-decision auditability** | LLM agents can be unpredictable; credit contexts demand reproducibility. | This is why the **policy-guard is deterministic code, not an LLM**, and why every agent action is logged with inputs/outputs (WS5 audit trail). We show that the *creative* parts (explanation, signal analysis) are AI while the *binding* parts (policy limits) are deterministic and audited. |

**RISK principle for the jury:** we are the team that knows exactly what our evidence does and does not support. That posture — *demonstrable mechanism + explicit limits + a clear real-world validation path* — reads as maturity, not weakness. It is the direct descendant of the source's "no-go is a valid outcome" charter clause.

---

## 5. Decisions routed to open-questions (not guessed)

Per the package rule (never resolve ambiguity by guessing), these bootcamp unknowns are logged as new OQ items in `00-program/open-questions.md`:

- **OQ-27** — Bootcamp duration (weeks/sprints)? Needed to compress the 10-week plan (delta A4) into concrete sprint sequencing in `workstreams.md`.
- **OQ-28** — Team size and composition? The five workstreams are sized for one owner or a pair each; the actual headcount sets how many WS a person carries.
- **OQ-29** — Mandatory / forbidden tech stack, model providers, or platform rules imposed by the bootcamp? Affects WS3/WS5 choices (LLM provider, orchestration framework, hosting).
- **OQ-30** — Official jury evaluation criteria and weights? The jury-scoring alignment table in `workstreams.md` currently uses inferred dimensions (AI/agents, innovation, business value, execution quality, presentation) and must be reconciled once the rubric is known.
- **OQ-31** — Demo-day format and constraints (live vs. recorded, time limit, data/privacy rules for any real data if introduced)? Shapes WS4 demo script and WS5 deployment target.

Until answered, `workstreams.md` uses **relative sprints** and **inferred jury dimensions**, both flagged as provisional.

---

## 6. How the deltas feed the five bootcamp workstreams

The original six source workstreams (Appendix A: Mobilize, Legal, Evidence, Sizing, Alignment, Close) are **re-partitioned** into five *ownership-based* bootcamp workstreams. To avoid ID collision, this review and `07-bootcamp-workstreams/` always write bootcamp streams as **BWS1–BWS5** in traceability, and label the source's as **source-WS1…6**.

| Bootcamp workstream | Absorbs (source workstreams / deltas) | Primary IDs owned |
|---|---|---|
| **BWS1 Business & Domain** | source-WS1 (map), source-WS4 (sizing), source-WS5 (alignment); deltas A2, A3, A6, A7; KEEP K1/K2/K10 | P1–P3, A1–A10 (framing), O5–O7, D1, D3, D5, D6, D7(awareness), D9, §8 KPIs |
| **BWS2 Data & Simulation** | source-WS3 (evidence) data layer; delta A1; KEEP K9/K11 | §7 M/U/OPT → synthetic schema, A2 ground truth, H1–H8/H11/H14 testability, D8 |
| **BWS3 AI Core & Agentic** ★ | LIFT L2/L3/L4/L6; the analytic engine behind source-WS3; KEEP K5 | H1–H8, H14, O1/O2/O8, boundary enforcement, agent-eval harness |
| **BWS4 Product, UX & Explainability** | LIFT L5; O2/O4/O6; H9/H10; delta A2 (personas → screens) | O1, O2, O4, O6, H9, H10, D9 (trust), demo script |
| **BWS5 Engineering, Integration & Quality** | LIFT L1; delta A5 (sim engine); KEEP K7/K8; operationalizes D10 audit trail | D2(as-built), D10, E6, audit trail, CI, deploy, agent monitoring |

The hard boundary (K5/L3) is a **cross-cutting invariant** owned by no single stream and enforced in BWS3 (guard agent) + BWS5 (audit trail) + narrated by BWS1.

---

## Self-review of this document
- **Four requested lenses present:** KEEP (§1), ADAPT (§2), LIFT (§3), RISK (§4). ✔
- **Every adaptation recorded as a delta** (ORIGINAL → BOOTCAMP), source line/section cited. ✔
- **Source file untouched:** this is a separate delta file; no edit to `early-phase-plan-credit-offer-optimization.md`. ✔
- **Hard boundary preserved in every lens** (KEEP K5, ADAPT A5, LIFT L3/L5, RISK R6). ✔
- **Unknowns not guessed:** timeline, team size, tech rules, jury rubric, demo format → OQ-27…OQ-31 (§5). ✔
- **Compressed-timeline requirement** (map 10-week plan to bootcamp duration): handled via delta A4 + OQ-27; concrete sequencing lives in `07-bootcamp-workstreams/workstreams.md`. ✔
