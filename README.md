# Brain-vs-RAG Ground-Zero Benchmark

**OpenClawBrain's full-brain mechanism achieves +9.7 to +26.9 pp over the best RAG baseline across three proof-scale families, while using 5x less context per query. Head-to-head record: 29-1-0 across 30 seed-level comparisons.**

## Proof results

| Family | Eval mode | full_brain | Best RAG | Margin | H2H | Context |
|---|---|---|---|---|---|---|
| relational_drift | recorded H2H (10 seeds, 800 q/seed) | 99.15% ± 0.27 | 89.44% ± 1.68 | +9.71 pp | 10-0-0 | 5× lower |
| recurring_workflows | simulation (10 seeds, 3522 q/seed) | 97.6% ± 0.4 | 70.6% ± 1.2 | +26.9 pp | 10-0-0 | 5× lower |
| sparse_feedback | simulation (10 seeds, 1800 q/seed) | 92.0% ± 18.3 | 67.0% ± 1.4 | +24.9 pp | 9-1-0 | 5× lower |

**Sparse-feedback variance note:** The ±18.3% std on sparse_feedback reflects high seed variance under ~19% explicit feedback coverage. One seed loss (9-1-0) prevents an unqualified "always wins" claim.

All evaluations run 8 baselines per family with fixed seeds. Results are deterministic given a seed.

## Context efficiency

full_brain uses 1 context unit per query vs 5 for vector_rag_rerank across all families — a consistent **5× context advantage**. In the relational_drift family, this translates to 800 vs 4,000 context tokens per query.

## Ablation ladder

Structural plasticity (Hebbian co-firing, decay, connect/split/merge/prune) is the single largest contributor in every family. The ablation ordering is consistent: route_fn_only < graph_route_pg < full_brain with no reversals.

| Family | route_fn_only | graph_route_pg | full_brain | Plasticity delta |
|---|---|---|---|---|
| relational_drift (sim) | 64.7% ± 1.6 | 76.5% ± 2.5 | 97.2% ± 5.8 | +20.8 pp |
| recurring_workflows | 34.1% ± 9.0 | 60.4% ± 1.7 | 97.6% ± 0.4 | +37.2 pp |
| sparse_feedback | 37.0% ± 1.7 | 49.4% ± 13.8 | 92.0% ± 18.3 | +42.6 pp |

## Recorded H2H vs simulation: two evaluation modes

The relational_drift family has two evaluation modes that must not be conflated:

- **Recorded H2H** (99.15% ± 0.27%): Deterministic fixture replay with hash verification. 10 seeds, 800 queries/seed. This is the stronger evidence — fully reproducible and verifiable.
- **Simulation** (97.2% ± 5.8%): Live simulation with the harness policy function. 10 seeds, 800 queries/seed.

The recorded H2H is preferred for headline claims on relational_drift. See [`proof-results/recorded_h2h_relational_drift_10seed/`](proof-results/recorded_h2h_relational_drift_10seed/) for the proof bundle and [`recorded_session_spec.md`](recorded_session_spec.md) for the evaluation spec.

## What this proves (and what it doesn't)

**Proven:** The full-brain mechanism — graph memory + learned route_fn + policy-gradient updates + structural plasticity — dominates RAG and partial-brain ablations on three distinct long-lived memory tasks (relational drift, recurring workflows, sparse teacher-assisted learning), each at 10-seed scale with 8 baselines, while using 5× less context.

**Not proven:**
- Performance on `memory_compaction` (designed but not run)
- Behavior at larger world sizes (current: 50 entities / 80 workflows)
- End-to-end performance with live LLM routing (harness uses simulated policy functions)
- Production latency or cost
- Real-session head-to-head (spec defined, no scored results)

See [CLAIMS.md](CLAIMS.md) for precise scope.

## How this connects to the real implementation

This benchmark validates the mechanism. The production architecture for OpenClawBrain is described in the [canonical rearchitecture plan](https://github.com/jonathangu/openclawbrain/blob/main/docs/openclawbrain-openclaw-rearchitecture-plan.md). See [IMPLEMENTATION_STRATEGY.md](IMPLEMENTATION_STRATEGY.md) for how the benchmark maps to that design.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Run a small smoke trial
python -m brain_ground_zero.cli smoke

# Run a family for all baselines
python -m brain_ground_zero.cli run \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml

# Multi-seed run (aggregated stats, win-rate matrix)
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50,60,70,80,90,100

# Proof sweeps (one-command bundle build + validation)
./scripts/run_recorded_h2h_proof.sh
./scripts/run_recurring_workflows_proof.sh
./scripts/run_sparse_feedback_proof.sh

# Refresh cross-bundle publishable assets
python3 scripts/generate_publishable_proof_assets.py
```

## Smoke checks

```bash
PYTHONPATH=src python3 -m brain_ground_zero.cli smoke
PYTHONPATH=src python3 scripts/validate_configs.py
python3 scripts/validate_fixture.py --all
python3 scripts/validate_recorded_h2h.py
```

## Repository layout

```
proof-results/                  <- tracked proof artifacts
  publishable/                  <- cross-bundle chart/table pack
  relational_drift_10seed/      <- 10-seed simulation proof
  recurring_workflows_10seed/   <- 10-seed proof (recurring workflows)
  sparse_feedback_10seed/       <- 10-seed proof (sparse feedback)
  recorded_h2h_relational_drift_10seed/ <- recorded head-to-head proof bundle
  recorded_h2h_relational_drift_001/    <- legacy single-seed (superseded)

recorded_session_spec.md        <- spec for recorded-session evaluation
CLAIMS.md                       <- precise claim scope
IMPLEMENTATION_STRATEGY.md      <- bridge to production architecture

benchmark_spec.md       <- benchmark contract and families
world_schema.md         <- world/task definitions
task_schema.md
baseline_matrix.md      <- baseline capabilities
scoring.md              <- metrics and scoring rubric
execution_plan.md       <- reproducible run protocol

src/brain_ground_zero/  <- harness implementation
configs/                <- family and baseline configs
scripts/                <- validation and proof scripts
runs/                   <- local run outputs (gitignored)
```

## Outputs

Each run writes:
- `runs/<run_id>/artifacts/summary_table.{csv,md}` — summary table
- `runs/<run_id>/artifacts/leaderboard.{csv,md}` — ranked table with deltas
- `runs/<run_id>/artifacts/learning_curve.png` — accuracy over steps
- `runs/<run_id>/artifacts/pairwise_accuracy_delta.{csv,md}` — pairwise deltas
- `runs/<run_id>/artifacts/win_rate_matrix.{csv,md}` — per-seed win counts (multiseed)
- `runs/<run_id>/artifacts/proof_digest.md` — publication-ready summary
- `proof-results/*/publishable_key_results.{csv,md}` — per-bundle scorecard
- `proof-results/*/chart_*.png` — publication-ready charts

## Further reading

- [Project home](https://openclawbrain.ai/)
- [Proof page](https://openclawbrain.ai/proof/)
- [Technical paper (PDF)](https://openclawbrain.ai/openclawbrain.pdf)
- [Reproduce this eval](https://openclawbrain.ai/docs/reproduce-eval.md)

## Non-goals

- No deployment — this is a mechanism proof, not a production system
- No heavy model dependencies
- Harness uses simulated policy functions, not live LLM calls
