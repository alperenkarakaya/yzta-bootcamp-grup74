# Interview Guide — Data Science Team
**Stakeholder profile (source §3):** goals — meaningful problem, access to data, freedom to explore signals. Concerns — being handed an unsolvable brief (no ground truth); data access blocked; governance treating exploration as production. Their success metrics — validated hypotheses; approved data access; clear problem definition.
**Note:** whether this team is bank-side, vendor-side, or joint is OQ-16 — confirm at session start; it changes who executes the H-analyses and who requests data.
**Session:** 90 min (week 3); participants: DS lead + analyst(s) who know the credit data landscape.

## Objectives
1. Reality-check the §7 inventory: where M1–M9/U1–U8 actually live, in what shape, with what known traps.
2. Surface prior work: has anyone studied segment accuracy, overrides, or stale scores before (OQ-01 history)?
3. Pressure-test the ground-truth problem (A2) with the people who will feel it first.
4. Agree the working protocol so exploration isn't treated as production (their §3 concern; H12 adjacency).

## Questions (11)
1. Has anyone here analyzed segment accuracy against realized outcomes — formally or as a side analysis? What happened to it? *(OQ-01; buried prior evidence accelerates or redirects H1)*
2. Where do decision-engine outputs (M1) live, at what grain and history depth — and are model version and timestamp reliable fields? *(H1/H2/H8 feasibility)*
3. Is segment migration (M5) directly historized, or must it be reconstructed from snapshots? Known gaps? *(H2/H3 effort)*
4. How complete are override logs (M6) — are reasons captured, and honestly? *(H4 feasibility)*
5. Do we hold 24–36 months of outcome data (M4) at customer level? Where does survivorship bite? *(OQ-19; R-DAT-05)*
6. What's your candid view of defining "deserved segment" — what convention could Risk actually sign, and where would it mislead? *(A2/E2; their "unsolvable brief" fear becomes protocol input)*
7. Which behavioral data (U1) is analytically usable today vs. folklore — coverage, noise, consistency across systems? *(H5 feasibility; R-DAT-02)*
8. What data-access requests have been blocked before, by whom, and why? *(A7; predicts tracker blocking issues)*
9. Is there any existing feedback loop from outcomes back into scoring/segmentation/offers — and at what lag? *(§2.1 step 9 discovery)*
10. What do you need so that Phase 1 exploration is not treated as production modeling by governance? *(their §3 concern; the H5 "no model building" guard protects them too — confirm they'll honor it)*
11. What is your capacity to support extracts and analysis in weeks 3–7 — named people, competing priorities? *(workplan resourcing reality)*

## Evidence to collect
- Data dictionaries / catalog entries for M-tier items; known-quality dashboards or profiling results.
- Prior analyses (reports, decks) on segmentation accuracy, overrides, campaigns (feeds H1/H4/H7 directly).
- A candid data-trap list (fields that lie, migrations that are artifacts, outcome definitions that changed mid-history) — gold for protocol design.

## Tensions to probe
- **Ground-truth honesty:** will they push back on convenient conventions? Encourage it — E2's definition must survive Model Risk scrutiny, and documented limits are part of the deliverable (§6.2: "document its limits").
- **Exploration-vs-production governance:** if governance forces production controls onto discovery analysis, the timeline breaks — surface now, align with Model Risk (their guide Q-tension mirrors this).
- **Scope discipline:** DS instinct is to build a model that "shows" the signal (H5 temptation). The source forbids it in Phase 1 — confirm explicit agreement and what evidence-of-separation form they'll produce instead.

## Feed into D3 (and beyond)
- Position summary; capability/capacity notes; tension log (ground truth, governance friction).
- Direct feeds: tracker pre-population (exists?/quality columns), H1–H8 protocol realism, D8 drafting, OQ-19/OQ-25 answers.
