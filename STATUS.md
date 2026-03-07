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
- Current milestone: M8 — Sparse feedback family
- Next step: scale `sparse_feedback` to proof-grade runs.

## 2026-03-06 (recorded-session head-to-head scaffold)
- What changed: added recorded-session / fixed-session head-to-head evaluation scaffold.
  - `recorded_session_spec.md` — full spec: purpose, proof boundary, modes, scoring rubric, fairness rules, operator workflow.
  - `recorded_sessions/schema/session_fixture.schema.json` — JSON Schema for session fixtures.
  - `recorded_sessions/fixtures/example_minimal.json` — minimal 2-turn example fixture.
  - `scripts/validate_fixture.py` — validates fixtures against the schema and prints a checklist summary.
  - `proof-results/recorded_sessions/README.md` — placeholder for scored artifacts.
  - Updated README.md, benchmark_spec.md, CLAIMS.md, proof-results/README.md.
- Validation: `python3 scripts/validate_fixture.py --all` (ok, all fixtures valid)
- Current milestone: M9 — Recorded-session head-to-head spec and scaffold
- Next step: capture real session traces, convert to fixtures, and produce first scored head-to-head artifacts.

## 2026-03-07 (recorded head-to-head: first scored artifact)
- What changed: shipped first scored recorded-h2h bundle and implementation code.
  - `src/brain_ground_zero/recorded_h2h.py` — fixture generation + deterministic replay harness with full JSONL trace logging.
  - `scripts/validate_recorded_h2h.py` — 8-criterion bundle validator (fixture hash, trace hashes, completeness, reproducibility, metadata, baselines, summary).
  - CLI: `generate_fixture` and `recorded_h2h` commands wired into `cli.py`.
  - `proof-results/recorded_h2h_relational_drift_001/` — first artifact bundle:
    - 800 queries across 41 steps, seed 42, 8 baselines.
    - full_brain 97.5% vs vector_rag_rerank 89.6% (+7.9 pp).
    - Full traces, scoring tables, pairwise deltas, per-query verdicts, SHA-256 verification, reproducibility check.
  - Updated README.md, STATUS.md, CLAIMS.md, proof-results/README.md.
- Validation:
  - `PYTHONPATH=src python3 scripts/validate_configs.py` (ok)
  - `python3 scripts/validate_fixture.py --all` (ok)
  - `python3 scripts/validate_recorded_h2h.py` (ok)
- Current milestone: M10 — Recorded head-to-head first artifact
- Next step: scale recorded h2h to multi-seed proof bundles; capture real product session traces.

## 2026-03-07 (sparse_feedback proof packaging)
- What changed: added sparse_feedback 10-seed proof packaging — matching the recurring_workflows proof pattern.
  - `configs/families/sparse_feedback_proof.yaml` — proof-scale config (same params as sparse_feedback.yaml).
  - `scripts/run_sparse_feedback_proof.sh` — one-command sweep/publish script.
  - `proof-results/sparse_feedback_10seed/README.md` — scaffolding with actual 10-seed run numbers.
  - Updated README.md, CLAIMS.md, proof-results/README.md with sparse_feedback proof-scale results.
  - Actual numbers from completed run: full_brain 91.96% vs vector_rag_rerank 67.05% (+24.91 pp), h2h 9-1-0, context 1.00 vs 5.00.
- Validation: `PYTHONPATH=src python3 scripts/validate_configs.py` (ok)
- Current milestone: M11 — Sparse feedback proof packaging
- Next step: run full proof sweep to populate all artifacts; scale recorded h2h to multi-seed.
