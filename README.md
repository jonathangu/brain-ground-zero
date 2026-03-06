# Brain-vs-RAG Ground-Zero Benchmark

**The full OpenClawBrain (OCB) method beats every RAG and stateful-memory baseline on relational drift -- by a wide margin, across 10 seeds.**

## Headline numbers (relational_drift, 10-seed mean)

| System | Accuracy | vs Best RAG | Win-rate vs field |
|---|---|---|---|
| **full_brain** | **97.2% +/- 5.8** | **+8.2 pp over vector_rag_rerank** | **beats every non-oracle system 9/10 or 10/10 seeds** |
| vector_rag_rerank | 89.0% +/- 2.3 | (best RAG baseline) | 10/10 vs plain RAG |
| vector_rag | 79.7% +/- 2.0 | -- | |
| heuristic_stateful | 79.4% +/- 2.2 | -- | |
| graph_route_pg (no plasticity) | 76.5% +/- 2.5 | -- | |
| route_fn_only | 64.7% +/- 1.6 | -- | |
| oracle (ceiling) | 100% | -- | |

Full results, pairwise deltas, win-rate matrix, and worked examples are in [`proof-results/`](proof-results/relational_drift_10seed/).

## What this proves (and what it doesn't)

This is the **first ground-zero benchmark family** (relational drift). It proves the full-brain mechanism -- graph memory + learned route_fn + policy-gradient updates + structural plasticity (Hebbian co-firing, decay, connect/split/merge/prune) -- dominates RAG and partial-brain ablations on long-lived memory with entity-relation drift.

It does **not** yet prove the thesis across all families (recurring workflows, sparse feedback, memory compaction). Those are designed in the harness and ready to implement. See [CLAIMS.md](CLAIMS.md) for precise scope.

## How this connects to the real implementation

This benchmark validates the mechanism. The production architecture for OpenClawBrain is described in the [architecture proposal](https://github.com/jonathangu/openclawbrain/blob/main/docs/architecture-proposal-openclawbrain-vnext.md). See [IMPLEMENTATION_STRATEGY.md](IMPLEMENTATION_STRATEGY.md) for how the benchmark maps to that design.

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
  --seeds 10,20,30,40,50,60,70,80,90,100
```

## Smoke checks

```bash
PYTHONPATH=src python3 -m brain_ground_zero.cli smoke
PYTHONPATH=src python3 scripts/validate_configs.py
```

## Repository layout

```
proof-results/          <- tracked 10-seed proof artifacts (the real numbers)
CLAIMS.md               <- what is proven and what is not
IMPLEMENTATION_STRATEGY.md <- bridge to the production architecture
SHARE_MESSAGE.md        <- copy/paste message for sharing

benchmark_spec.md       <- benchmark contract and families
world_schema.md         <- world/task definitions
task_schema.md
baseline_matrix.md      <- baseline capabilities and allowed updates
scoring.md              <- metrics and scoring rubric
execution_plan.md       <- reproducible run protocol

src/brain_ground_zero/  <- harness implementation
configs/                <- family and baseline configs
runs/                   <- local run outputs (gitignored)
```

## Outputs

Each run writes:
- `runs/<run_id>/artifacts/summary_table.{csv,md}` -- summary table
- `runs/<run_id>/artifacts/learning_curve.png` -- accuracy over steps (with std bands for multiseed)
- `runs/<run_id>/artifacts/pairwise_accuracy_delta.{csv,md}` -- row-minus-column accuracy delta
- `runs/<run_id>/artifacts/win_rate_matrix.{csv,md}` -- per-seed win counts (multiseed only)
- `runs/<run_id>/artifacts/worked_example_trace.md` -- single query traced across all baselines

## Non-goals

- No deployment
- No heavy model dependencies
- This is a mechanism proof, not a production system
