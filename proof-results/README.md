# Proof Artifacts

Tracked, reproducible benchmark results for OpenClawBrain vs RAG baselines.

## Families

| Family | Seeds | Status | Key result |
|---|---|---|---|
| [relational_drift_10seed](relational_drift_10seed/) | 10 | **Full proof run** | full_brain 97.2% vs best RAG 89.0% (+8.2 pp) |
| [recurring_workflows_10seed](recurring_workflows_10seed/) | 10 | **Full proof run** | full_brain 97.6% vs best RAG 70.6% (+26.9 pp) |
| [recurring_workflows_3seed](recurring_workflows_3seed/) | 3 | Legacy spot-check | Historical pre-proof check (superseded by 10-seed run) |
| [sparse_feedback_3seed](sparse_feedback_3seed/) | 3 | Spot-check | full_brain 98.0% vs best RAG 67.7% (+30.3 pp), feedback coverage ~19.8% |

**Start here:** `relational_drift_10seed/` and `recurring_workflows_10seed/` are the strongest artifacts -- each is a 10-seed, 8-baseline proof run with full tables and worked traces.

## Recorded-session head-to-head (next rung)

| Directory | Status | Description |
|---|---|---|
| [recorded_sessions/](recorded_sessions/) | **Placeholder** | Real product session head-to-head results (none yet) |

The spec, fixture schema, and example fixture are in [`recorded_sessions/`](../recorded_sessions/) at the repo root. See [`recorded_session_spec.md`](../recorded_session_spec.md) for the full evaluation protocol.

## Scope

These results prove the full-brain **mechanism** (graph memory + learned routing + policy-gradient updates + structural plasticity) dominates RAG and partial-brain ablations on long-lived memory with entity-relation drift. This is a mechanism proof, not a production proof. The recorded-session head-to-head is the next step toward a real-product proof. See [CLAIMS.md](../CLAIMS.md) for precise scope.

## Each family directory contains

- `summary_table.md` / `.csv` -- per-baseline accuracy with mean +/- std
- `pairwise_accuracy_delta.md` / `.csv` -- accuracy deltas between all pairs
- `win_rate_matrix.md` / `.csv` -- per-seed win counts
- `worked_example_trace.md` -- single query traced across all baselines
- `learning_curve.png` -- accuracy over steps with std-deviation bands
- `seeds.json` -- seed list used
