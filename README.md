# Brain-vs-RAG Ground-Zero Benchmark

This repository is a **standalone** benchmark harness for testing the full OpenClawBrain (OCB) thesis against strong RAG and stateful-memory baselines in long-lived agent-memory environments under bounded context and bounded cost.

Key intent: this is **not** a graph-vs-vector toy. It measures whether the full strategy (runtime route_fn + async teacher + background labels + policy-gradient updates + structural graph memory with Hebbian co-firing, decay, connect/split/merge/prune) wins on realistic memory drift, contradiction, and recurrence.

## What’s included
- Publication-grade benchmark spec and schemas
- Reproducible configs for families and baselines
- A runnable Python harness
- The first implemented family: `relational_drift`
- Reporting with summary tables, learning curves, pairwise deltas, win-rate matrices, and worked-example traces
- Multi-seed aggregation for stable comparisons (mean +/- std)
- Smoke checks for validation

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Run a small smoke trial
python -m brain_ground_zero.cli smoke

# Run relational_drift for all baselines
python -m brain_ground_zero.cli run \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml

# Multi-seed run (aggregated stats, win-rate matrix)
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50

# Generate a report/plot from the latest run
python -m brain_ground_zero.cli report --run-dir runs/latest
```

## Smoke checks
```bash
PYTHONPATH=src python3 -m brain_ground_zero.cli smoke
PYTHONPATH=src python3 scripts/validate_configs.py
```

## Repository layout
- `benchmark_spec.md` – benchmark contract and families
- `world_schema.md`, `task_schema.md` – world/task definitions
- `baseline_matrix.md` – baseline capabilities and allowed updates
- `scoring.md` – metrics and scoring rubric
- `execution_plan.md` – reproducible run protocol
- `milestones.md` – roadmap
- `src/brain_ground_zero/` – harness implementation
- `configs/` – family and baseline configs
- `runs/` – outputs (gitignored)

## Outputs
Each run writes:
- `runs/<run_id>/metrics.jsonl` — per-query record log
- `runs/<run_id>/summary.json` — aggregated metrics per baseline
- `runs/<run_id>/artifacts/summary_table.{csv,md}` — summary table
- `runs/<run_id>/artifacts/learning_curve.png` — accuracy over steps (with std bands for multiseed)
- `runs/<run_id>/artifacts/pairwise_accuracy_delta.{csv,md}` — row-minus-column accuracy delta
- `runs/<run_id>/artifacts/win_rate_matrix.{csv,md}` — per-seed win counts (multiseed only)
- `runs/<run_id>/artifacts/worked_example_trace.md` — single query traced across all baselines

Multi-seed runs additionally write:
- `runs/<run_id>/per_seed_summaries.json` — per-seed raw summaries
- `runs/<run_id>/seeds.json` — seed list used
- `runs/<run_id>/seed_<N>/` — individual seed run directories

## Status
See `STATUS.md` for milestone progress, smoke checks, and next steps.

## Non-goals
- No deployment
- No heavy model dependencies
