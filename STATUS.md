# Status

## 2026-03-06 08:55 PST
- What changed: drafted benchmark contract docs (spec, schemas, scoring, baselines, execution plan, milestones) and README.
- Current milestone: M1 — Benchmark contract
- Next step: build the Python harness scaffold and baseline interfaces.

## 2026-03-06 08:58 PST
- What changed: created Python package scaffold, baseline interfaces/stubs, configs, and project layout scaffolding.
- Current milestone: M2 — Harness scaffold
- Next step: implement relational_drift family, runner, and baseline logic.

## 2026-03-06 09:06 PST
- What changed: implemented relational_drift family, runner, baseline logic, memory/policy utilities, and reporting hooks.
- Current milestone: M3 — Relational drift family
- Next step: add reporting artifacts and smoke/validation scripts, then run smoke checks.

## 2026-03-06 09:07 PST
- What changed: ran smoke test and config validation.
- Smoke checks: `PYTHONPATH=src python3 -m brain_ground_zero.cli smoke` (ok), `PYTHONPATH=src python3 scripts/validate_configs.py` (ok)
- Current milestone: M4 — Reporting and validation
- Next step: finalize docs/code alignment and ensure clean committed state.

## 2026-03-06 10:05 PST
- What changed: added publication-ready reporting enhancements.
  - Multi-seed aggregation via `multiseed` CLI command (mean +/- std across N seeds)
  - Pairwise accuracy delta table (row - column)
  - Win-rate matrix (per-seed head-to-head counts, multiseed only)
  - Worked-example trace artifact (single query pair traced across all baselines over time)
  - Learning curve plot now shows std-deviation bands for multiseed runs
  - Summary table includes std columns when aggregated
  - Updated README.md with new commands and artifact listing
- Smoke checks: smoke (ok), validate_configs (ok), multiseed --seeds 10,20,30 (ok)
- Current milestone: M5 — Publication-ready reporting
- Next step: run larger multiseed experiments (5-10 seeds), add confidence intervals or bootstrap, consider additional families.

## 2026-03-06 15:11 PST
- What changed: implemented `recurring_workflows` family (world/task generation), added config, registry wiring, and reporting updates.
  - CLI smoke now runs all families by default; config validation covers both families.
  - Reporting now derives family name for titles and worked examples.
- Smoke checks: `PYTHONPATH=src python3 -m brain_ground_zero.cli smoke` (ok), `PYTHONPATH=src python3 scripts/validate_configs.py` (ok)
- Proof-style run: `recurring_workflows` 3-seed spot-check recorded in `proof-results/recurring_workflows_3seed/`.
- Current milestone: M6 — Recurring workflows family
- Next step: scale recurring_workflows to 5-10 seeds and add sparse feedback family.

## 2026-03-06 20:40 PST
- What changed: implemented `sparse_feedback` family end-to-end (world/task generation + sparse per-query feedback masks), and wired sparse feedback gating into runner/scoring/reporting.
  - Runner now honors step-level `feedback_mask` for PG updates and teacher scheduling.
  - Metrics/reporting now include `feedback_events` and `feedback_rate`.
  - Added `configs/families/sparse_feedback.yaml`; wired family into registry, CLI smoke, and config validation.
  - Improved `full_brain` background labels to use latest related facts, making sparse teacher signals usable for offline label amplification.
- Validation checks:
  - `PYTHONPATH=src python3 scripts/validate_configs.py` (ok)
  - `PYTHONPATH=src python3 -m brain_ground_zero.cli smoke --family configs/families/sparse_feedback.yaml --run-id smoke_sparse_feedback` (ok)
- Proof-style run: `sparse_feedback` 3-seed spot-check recorded in `proof-results/sparse_feedback_3seed/`.
- Current milestone: M7 — Sparse feedback family
- Next step: scale `sparse_feedback` and `recurring_workflows` to 5-10 seed proof-grade runs.
