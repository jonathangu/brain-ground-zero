# Proof Artifacts

Tracked, reproducible benchmark results for OpenClawBrain vs RAG baselines.

## Start here (publishable assets)

- [publishable/README.md](publishable/README.md) -- index for site/blog/paper-ready artifacts
- [publishable/tables/focus_evidence_table.md](publishable/tables/focus_evidence_table.md) -- compact cross-bundle evidence table
- [publishable/charts/focus_margin_context.png](publishable/charts/focus_margin_context.png) -- margins + context efficiency in one figure
- [publishable/charts/focus_ablation_ladder.png](publishable/charts/focus_ablation_ladder.png) -- ablation ladder across all focus bundles
- [recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png](recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
- [sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png](sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
- [recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png](recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)

## Families

| Family | Seeds | Status | Key result |
|---|---|---|---|
| [relational_drift_10seed](relational_drift_10seed/) | 10 | **Full proof run** | full_brain 97.2% vs best RAG 89.0% (+8.2 pp) |
| [recurring_workflows_10seed](recurring_workflows_10seed/) | 10 | **Full proof run** | full_brain 97.6% vs best RAG 70.6% (+26.9 pp) |
| [recurring_workflows_3seed](recurring_workflows_3seed/) | 3 | Legacy spot-check | Historical pre-proof check (superseded by 10-seed run) |
| [sparse_feedback_10seed](sparse_feedback_10seed/) | 10 | **Full proof run** | full_brain 92.0% vs best RAG 67.0% (+24.9 pp), feedback coverage ~19% |
| [sparse_feedback_3seed](sparse_feedback_3seed/) | 3 | Legacy spot-check | Historical pre-proof check (superseded by 10-seed run) |

**Start here:** `recorded_h2h_relational_drift_10seed/`, `relational_drift_10seed/`, `recurring_workflows_10seed/`, and `sparse_feedback_10seed/` are the strongest artifacts -- each is a 10-seed, 8-baseline proof run with full tables and worked traces.

## Recorded head-to-head

| Directory | Status | Description |
|---|---|---|
| [recorded_h2h_relational_drift_10seed](recorded_h2h_relational_drift_10seed/) | **Full proof run** | 10 seeds x 800 queries x 8 baselines -- full_brain 99.15% vs best RAG 89.44% (+9.71 pp), h2h 10-0-0 |
| [recorded_h2h_relational_drift_001](recorded_h2h_relational_drift_001/) | Legacy first bundle | 8 baselines, 800 queries, seed 42 -- full_brain 97.5% vs best RAG 89.6% (+7.9 pp) |
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
- `publishable_key_results.md` / `.csv` -- one-row publication table for fast copy into site/blog/paper

Generate/refresh the publishable pack with:

```bash
python3 scripts/generate_publishable_proof_assets.py
```
