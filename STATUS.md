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

## 2026-03-06 20:34 PST
- What changed: pushed recurring_workflows to full proof-sweep readiness and shipped a 10-seed proof artifact set.
  - Family hardening: added recurring-workflow controls for hot-workflow bias, update-revisit bias, replay queries, and burst updates, plus explicit parameter validation.
  - Reporting upgrade: added publication artifacts (`leaderboard`, `per_seed_breakdown`, `per_seed_accuracy_matrix`, `proof_digest`), ordered baseline tables, and improved representative worked-example selection.
  - Proof workflow: added `configs/families/recurring_workflows_proof.yaml` and one-command sweep/publish script `scripts/run_recurring_workflows_proof.sh`.
  - Proof run committed: `proof-results/recurring_workflows_10seed/` with 10 seeds and full artifact bundle.
- Validation checks:
  - `PYTHONPATH=src python3 scripts/validate_configs.py` (ok)
  - `PYTHONPATH=src python3 -m brain_ground_zero.cli smoke --family configs/families/recurring_workflows.yaml --run-id smoke_recurring_upgrade` (ok)
  - `PYTHONPATH=src python3 -m brain_ground_zero.cli multiseed --family configs/families/recurring_workflows.yaml --baselines configs/baselines/all.yaml --seeds 1,2,3 --run-id recurring_workflows_reporting_check` (ok)
  - `./scripts/run_recurring_workflows_proof.sh` (ok)
- Current milestone: M7 — Recurring workflows proof sweep
- Next step: carry the same proof-scale packaging to sparse feedback / teacher-assisted family.

## 2026-03-06 (recorded-session head-to-head scaffold)
- What changed: added recorded-session / fixed-session head-to-head evaluation scaffold.
  - `recorded_session_spec.md` — full spec: purpose, proof boundary, modes, scoring rubric, fairness rules, operator workflow.
  - `recorded_sessions/schema/session_fixture.schema.json` — JSON Schema for session fixtures.
  - `recorded_sessions/fixtures/example_minimal.json` — minimal 2-turn example fixture.
  - `scripts/validate_fixture.py` — validates fixtures against the schema and prints a checklist summary.
  - `proof-results/recorded_sessions/README.md` — placeholder for scored artifacts.
  - Updated README.md, benchmark_spec.md, CLAIMS.md, proof-results/README.md.
- Validation: `python3 scripts/validate_fixture.py --all` (ok, all fixtures valid)
- Current milestone: M8 — Recorded-session head-to-head spec and scaffold
- Next step: capture real session traces, convert to fixtures, and produce first scored head-to-head artifacts.
