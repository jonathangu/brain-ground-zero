# Proof Artifacts

Tracked, reproducible benchmark results for OpenClawBrain vs RAG baselines.

## Families

| Family | Seeds | Status | Key result |
|---|---|---|---|
| [relational_drift_10seed](relational_drift_10seed/) | 10 | **Full proof run** | full_brain 97.2% vs best RAG 89.0% (+8.2 pp) |
| [recurring_workflows_10seed](recurring_workflows_10seed/) | 10 | **Full proof run** | full_brain 97.6% vs best RAG 70.6% (+26.9 pp) |
| [recurring_workflows_3seed](recurring_workflows_3seed/) | 3 | Legacy spot-check | Historical pre-proof check (superseded by 10-seed run) |
| [sparse_feedback_10seed](sparse_feedback_10seed/) | 10 | **Full proof run** | full_brain 92.0% vs best RAG 67.0% (+24.9 pp), feedback coverage ~19% |
| [sparse_feedback_3seed](sparse_feedback_3seed/) | 3 | Legacy spot-check | Historical pre-proof check (superseded by 10-seed run) |

**Start here:** `relational_drift_10seed/`, `recurring_workflows_10seed/`, and `sparse_feedback_10seed/` are the strongest artifacts -- each is a 10-seed, 8-baseline proof run with full tables and worked traces.

## Recorded head-to-head

| Directory | Status | Description |
|---|---|---|
| [recorded_h2h_relational_drift_001](recorded_h2h_relational_drift_001/) | **Draft (first bundle)** | 8 baselines, 800 queries, seed 42 -- full_brain 97.5% vs best RAG 89.6% (+7.9 pp) |
| [recorded_sessions/](recorded_sessions/) | **Placeholder** | Real product session head-to-head results (none yet) |

The recorded-h2h lane replays a deterministic fixture against all baselines with full JSONL trace logging and verification hashes. See [`recorded_session_spec.md`](../recorded_session_spec.md) for the evaluation protocol.

## Scope

These results prove the full-brain **mechanism** (graph memory + learned routing + policy-gradient updates + structural plasticity) dominates RAG and partial-brain ablations on long-lived memory with entity-relation drift, recurring workflows, and sparse teacher-assisted learning. This is a mechanism proof, not a production proof. The recorded-session head-to-head is the next step toward a real-product proof. See [CLAIMS.md](../CLAIMS.md) for precise scope.

## Each family directory contains

- `summary_table.md` / `.csv` -- per-baseline accuracy with mean +/- std
- `pairwise_accuracy_delta.md` / `.csv` -- accuracy deltas between all pairs
- `win_rate_matrix.md` / `.csv` -- per-seed win counts
- `worked_example_trace.md` -- single query traced across all baselines
- `learning_curve.png` -- accuracy over steps with std-deviation bands
- `seeds.json` -- seed list used
