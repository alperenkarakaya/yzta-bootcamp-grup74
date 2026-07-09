# D4 — Assumption & Hypothesis Validation Report (template)
**Source §9:** "disposition of A1–A10 and H1–H14 with evidence" · **Owner:** Data Science · **Sign-off:** Risk (for analytical rigor) · **Feeds gates:** E1, E2 (evidence), and every gate that consumes hypothesis results

## 1. Method and protocol governance
> Guidance: state the discipline that makes results acceptable: all protocols and thresholds pre-registered with Risk before results were known (charter §3); ground truth per the E2-signed convention; falsification conditions applied verbatim from source §5. Reference protocol files `../01-hypothesis-validation/h01.md`–`h14.md`.

## 2. Assumption dispositions A1–A10
> Guidance: KPI §8.1 requires 100% dispositioned as **validated / falsified / deferred with reason**. One row per assumption: disposition, evidence pointer, validation vehicle used (per `../01-hypothesis-validation/validation-plan.md` §4), consequence of the disposition (e.g., A1 falsified → value case shifts to P2/P3 per §1.4).
> Required evidence: each disposition traceable to an analysis, interview set, document review, or workshop output — no disposition by assertion.

## 3. Hypothesis results H1–H14
> Guidance: KPI §8.1: "≥ 10 tested, remainder scheduled." Summary table: H / result (supported / falsified / inconclusive / SCHEDULED) / evidence / threshold vs. outcome / exit criterion fed. A SCHEDULED entry must carry blocking data item(s), earliest feasible date, and owner — that is what "explicitly scheduled with data dependencies" means.

## 4. Per-hypothesis result notes
> Guidance: one short subsection per hypothesis: pre-registered protocol reference, what was run (business terms), result against the falsification condition (quote it), caveats specific to the result. Falsified hypotheses get equal typographical prominence — a discovery phase that buries falsifications has failed (§10 principle).

## 5. Cross-cutting caveats
> Guidance: the standing caveats from `../01-hypothesis-validation/validation-plan.md` §6 — selective labels/survivorship (R-DAT-05), counterfactual absence (§2.4), feedback-loop flag for Mid Phase (R-AI-02) — stated once, referenced by all results.

## 6. Data lineage
> Guidance: which tracker items (M/U/OPT) each result consumed, with extract dates and known quality issues (link D8). Analyses on data later found defective must be flagged here and re-dispositioned.

## 7. Implications
> Guidance: strictly evidence → scope implications: which opportunities the results energize/kill (input to D5), which assumptions' falsification changes the Mid Phase question. No solution design.

## Sign-off block
| Role | Name | Date | Signature |
|---|---|---|---|
| Owner — Data Science | TODO | | |
| Sign-off — Risk (analytical rigor) | TODO | | |
