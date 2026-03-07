# Brain-vs-RAG Ground-Zero Benchmark

**The full OpenClawBrain (OCB) method beats every RAG and stateful-memory baseline on both relational drift and recurring workflows -- by clear margins across 10 seeds.**

## Next proof rung (publish-first)

| Artifact | full_brain | Best RAG | Margin | Head-to-head | Context/query |
|---|---|---|---|---|---|
| recurring_workflows_10seed | 97.6% +/- 0.4 | 70.6% +/- 1.2 | +26.9 pp | 10-0-0 | 1.0 vs 5.0 |
| sparse_feedback_10seed | 92.0% +/- 18.3 | 67.0% +/- 1.4 | +24.9 pp | 9-1-0 | 1.0 vs 5.0 |
| recorded_h2h_relational_drift_001 (first artifact) | 97.5% | 89.6% | +7.9 pp | n/a (single seed) | 1.0 vs 5.0 |

Use this lift order for site/blog/paper: [`proof-results/publishable/site_blog_paper_starter.md`](proof-results/publishable/site_blog_paper_starter.md).

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

Full results, pairwise deltas, win-rate matrix, and worked examples are in [`proof-results/`](proof-results/) (start with [`relational_drift_10seed/`](proof-results/relational_drift_10seed/)).

## Headline numbers (recurring_workflows, 10-seed mean)

| System | Accuracy | vs Best RAG | Win-rate vs field |
|---|---|---|---|
| **full_brain** | **97.6% +/- 0.4** | **+26.9 pp over vector_rag_rerank** | **10/10 vs every non-oracle baseline** |
| vector_rag_rerank | 70.6% +/- 1.2 | (best RAG baseline) | 10/10 vs plain RAG |
| vector_rag | 63.4% +/- 1.6 | -- | |
| heuristic_stateful | 61.4% +/- 1.2 | -- | |
| graph_route_pg (no plasticity) | 60.4% +/- 1.7 | -- | |
| route_fn_only | 34.1% +/- 9.0 | -- | |
| oracle (ceiling) | 100% | -- | |

See [`proof-results/recurring_workflows_10seed/`](proof-results/recurring_workflows_10seed/) for the full artifact set.

## Headline numbers (sparse_feedback, 10-seed mean)

| System | Accuracy | vs Best RAG | Win-rate vs field |
|---|---|---|---|
| **full_brain** | **92.0% +/- 18.3** | **+24.9 pp over vector_rag_rerank** | **9/10 vs every non-oracle baseline** |
| vector_rag_rerank | 67.0% +/- 1.4 | (best RAG baseline) | 10/10 vs plain RAG |
| vector_rag | 60.5% +/- 1.6 | -- | |
| heuristic_stateful | 51.4% +/- 2.2 | -- | |
| graph_route_pg (no plasticity) | 49.4% +/- 13.8 | -- | |
| route_fn_only | 37.0% +/- 1.7 | -- | |
| oracle (ceiling) | 100% | -- | |

Sparse feedback tests teacher-assisted learning where explicit signals arrive on only ~19% of queries. See [`proof-results/sparse_feedback_10seed/`](proof-results/sparse_feedback_10seed/) for the full artifact set.

## Publishable chart/table pack (drop-in)

For immediate site/blog/paper usage, start with:
- [`proof-results/publishable/README.md`](proof-results/publishable/README.md)
- [`proof-results/publishable/site_blog_paper_starter.md`](proof-results/publishable/site_blog_paper_starter.md)
- [`proof-results/publishable/tables/focus_evidence_table_compact.md`](proof-results/publishable/tables/focus_evidence_table_compact.md)
- [`proof-results/publishable/charts/focus_margin_context.png`](proof-results/publishable/charts/focus_margin_context.png)
- [`proof-results/publishable/charts/focus_ablation_ladder.png`](proof-results/publishable/charts/focus_ablation_ladder.png)
- [`proof-results/recorded_h2h_relational_drift_001/chart_accuracy_context_tradeoff.png`](proof-results/recorded_h2h_relational_drift_001/chart_accuracy_context_tradeoff.png)
- [`proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
- [`proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)

Per-focus, one-row publication tables are also tracked in:
- `proof-results/recorded_h2h_relational_drift_001/publishable_key_results.{md,csv}`
- `proof-results/recorded_h2h_relational_drift_001/publishable_key_results_compact.{md,csv}`
- `proof-results/sparse_feedback_10seed/publishable_key_results.{md,csv}`
- `proof-results/sparse_feedback_10seed/publishable_key_results_compact.{md,csv}`
- `proof-results/recurring_workflows_10seed/publishable_key_results.{md,csv}`
- `proof-results/recurring_workflows_10seed/publishable_key_results_compact.{md,csv}`

Refresh all publishable assets with:

```bash
python3 scripts/generate_publishable_proof_assets.py
```

## What this proves (and what it doesn't)

This benchmark now includes three proof-scale families:
- `relational_drift` (10 seeds)
- `recurring_workflows` (10 seeds)
- `sparse_feedback` (10 seeds)

Together they show that the full-brain mechanism -- graph memory + learned route_fn + policy-gradient updates + structural plasticity (Hebbian co-firing, decay, connect/split/merge/prune) -- dominates RAG and partial-brain ablations on long-lived memory with drift, repeated workflow tasks, and sparse teacher-assisted learning.

**Recorded head-to-head (first artifact shipped):** The first scored recorded-h2h bundle replays a deterministic fixture (800 queries, seed 42) against all 8 baselines with full JSONL traces and verification hashes. full_brain achieves 97.5% vs best RAG 89.6% (+7.9 pp). See [`proof-results/recorded_h2h_relational_drift_001/`](proof-results/recorded_h2h_relational_drift_001/). The full evaluation spec is in [`recorded_session_spec.md`](recorded_session_spec.md).

It does **not** yet prove the thesis across all designed families; `memory_compaction` is designed but not yet implemented. See [CLAIMS.md](CLAIMS.md) for precise scope.

## How this connects to the real implementation

This benchmark validates the mechanism. The production architecture for OpenClawBrain is described in the [canonical rearchitecture plan](https://github.com/jonathangu/openclawbrain/blob/main/docs/openclawbrain-openclaw-rearchitecture-plan.md). See [IMPLEMENTATION_STRATEGY.md](IMPLEMENTATION_STRATEGY.md) for how the benchmark maps to that design.

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

# Run recurring_workflows for all baselines
python -m brain_ground_zero.cli run \
  --family configs/families/recurring_workflows.yaml \
  --baselines configs/baselines/all.yaml

# Run sparse_feedback for all baselines
python -m brain_ground_zero.cli run \
  --family configs/families/sparse_feedback.yaml \
  --baselines configs/baselines/all.yaml

# Multi-seed run (aggregated stats, win-rate matrix)
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50,60,70,80,90,100

# Recurring-workflows proof sweep + publish to proof-results/
./scripts/run_recurring_workflows_proof.sh

# Sparse-feedback proof sweep + publish to proof-results/
./scripts/run_sparse_feedback_proof.sh

# Recorded head-to-head proof bundle + validation + publishable refresh
./scripts/run_recorded_h2h_relational_drift_proof.sh

# Refresh cross-bundle publishable chart/table pack
python3 scripts/generate_publishable_proof_assets.py

# Recorded head-to-head manual flow: generate fixture + run + validate
python -m brain_ground_zero.cli generate_fixture \
  --family configs/families/relational_drift.yaml \
  --seed 42 \
  --output /tmp/fixture.yaml

python -m brain_ground_zero.cli recorded_h2h \
  --fixture /tmp/fixture.yaml \
  --baselines configs/baselines/all.yaml \
  --output /tmp/h2h_output/

python scripts/validate_recorded_h2h.py /tmp/h2h_output/
```

## Smoke checks

```bash
# Runs smoke on all families
PYTHONPATH=src python3 -m brain_ground_zero.cli smoke

# Or target a single family
PYTHONPATH=src python3 -m brain_ground_zero.cli smoke \
  --family configs/families/sparse_feedback.yaml

PYTHONPATH=src python3 scripts/validate_configs.py

# Validate recorded-session fixtures
python3 scripts/validate_fixture.py --all

# Validate recorded h2h bundles
python3 scripts/validate_recorded_h2h.py
```

## Repository layout

```
proof-results/                  <- tracked proof artifacts
  publishable/                  <- cross-bundle chart/table pack for site/blog/paper
  relational_drift_10seed/      <- 10-seed simulation proof (the headline numbers)
  recurring_workflows_10seed/   <- 10-seed proof sweep (recurring workflows)
  sparse_feedback_10seed/       <- 10-seed proof sweep (sparse feedback)
  recurring_workflows_3seed/    <- 3-seed spot-check (superseded by 10-seed)
  sparse_feedback_3seed/        <- 3-seed spot-check (superseded by 10-seed)
  recorded_h2h_relational_drift_001/ <- first scored recorded head-to-head bundle
  recorded_sessions/            <- (placeholder) real-session head-to-head results

recorded_session_spec.md        <- spec for recorded-session head-to-head evaluation
recorded_sessions/              <- fixture schema, example fixtures, validation
  schema/session_fixture.schema.json
  fixtures/example_minimal.json

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
scripts/                <- validation and smoke scripts
  generate_publishable_proof_assets.py <- rebuilds publishable chart/table pack from tracked proof bundles
  run_recorded_h2h_relational_drift_proof.sh <- one-command recorded-h2h bundle build + validation
runs/                   <- local run outputs (gitignored)
```

## Outputs

Each run writes:
- `runs/<run_id>/artifacts/summary_table.{csv,md}` -- summary table
- `runs/<run_id>/artifacts/leaderboard.{csv,md}` -- ranked publication table with deltas vs best RAG/full_brain
- `runs/<run_id>/artifacts/learning_curve.png` -- accuracy over steps (with std bands for multiseed)
- `runs/<run_id>/artifacts/pairwise_accuracy_delta.{csv,md}` -- row-minus-column accuracy delta
- `runs/<run_id>/artifacts/win_rate_matrix.{csv,md}` -- per-seed win counts (multiseed only)
- `runs/<run_id>/artifacts/per_seed_breakdown.{csv,md}` -- long-form per-seed metrics
- `runs/<run_id>/artifacts/per_seed_accuracy_matrix.{csv,md}` -- seed-by-seed accuracy matrix
- `runs/<run_id>/artifacts/proof_digest.md` -- concise publication-ready summary
- `runs/<run_id>/artifacts/worked_example_trace.md` -- single query traced across all baselines
- `proof-results/*/publishable_key_results.{csv,md}` -- one-row, publication-ready key result table for a tracked bundle
- `proof-results/*/publishable_key_results_compact.{csv,md}` -- compact one-row scorecard for direct site/blog/paper lift
- `proof-results/*/chart_*.png` -- high-signal, publication-ready charts for tracked bundles

## Further reading on openclawbrain.ai

- [Project home](https://openclawbrain.ai/) -- overview of the OpenClawBrain system
- [Proof page](https://openclawbrain.ai/proof/) -- benchmark results and proof artifacts
- [Technical paper (PDF)](https://openclawbrain.ai/openclawbrain.pdf)
- [Reproduce this eval](https://openclawbrain.ai/docs/reproduce-eval.md) -- step-by-step reproduction guide
- [v12.2.6 series blog](https://openclawbrain.ai/blog/v12.2.6-series/) -- latest development notes
- [All materials](https://openclawbrain.ai/materials/)

## Non-goals

- No deployment
- No heavy model dependencies
- This is a mechanism proof, not a production system
