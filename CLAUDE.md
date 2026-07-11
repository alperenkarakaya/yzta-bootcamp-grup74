# AKS — Session Router

The project has exactly **three** source-of-truth documents. Read them in order; everything else is code under `product/`.

1. **[overview.md](overview.md)** — start here. Vision, problem, solution, business thesis, statistical & AI philosophy, boundary principle, current status, stack, decisions.
2. **[architecture.md](architecture.md)** — engineering spec. Every AI/ML/architectural component and *why* it exists.
3. **[execution.md](execution.md)** — the live plan: sprint, priorities, research/eng tasks, technical debt, risks, open decisions (OQ-xx).

## Binding rules (do not violate)

- **Statistical validity > AI.** Priority order: accuracy > generalization > calibration > robustness > interpretability > business value > regulatory > engineering > AI > UI. Classical methods win by default. UI/stack/agents (P8–P10) must never preempt validity work (P1–P4).
- **Every AI/agent component must pass the five-question test** (overview.md §6) or be removed/renamed. LLMs must never become the decision engine.
- **The headline numbers are circular** (architecture.md §5.1). Do **not** cite AUC 0.829, "973/1084 rescued," or the fairness-gap figures as validated. Caveat or fix first.
- **The boundary is absolute:** AKS complements, never overrides, the bank's classic score/segment — enforced by the immutable audit trail (architecture.md §9).
- **Never resolve an open question (OQ-xx) by guessing — ask the Product Owner.** Live decisions: OQ-36 (real data), OQ-37 (fix sequencing), OQ-38 (agent narrative), OQ-39 (target = Formulation B, proposed).
- **"No-go is a valid outcome."** If the thesis fails on a non-circular benchmark, report it.
- **Keep the three internal docs current and never create a fourth.** Edit `overview.md` / `architecture.md` / `execution.md` in place; do not archive history or spin up parallel planning docs.
- **`README.md` is a graded deliverable, not internal documentation — never delete it.** It is the bootcamp jury's entry point to the repo (project definition, product backlog, and the per-sprint evidence blocks required by YZTA Bootcamp 2026). It is exempt from the "no fourth doc" rule.
  - **The Sprint 1 block is frozen.** It has already been graded (full marks); do not edit its text or move the images it links (`sprints/docs/sprint1/*`).
  - Each sprint appends its own block under its own heading. Sprint evidence lives in `sprints/docs/sprint<N>/` (daily scrum notes, board screenshot, product screenshots).
  - Keep `README.md` in sync with reality: when a component ships or a claim changes, update the backlog table and the relevant sprint block.
