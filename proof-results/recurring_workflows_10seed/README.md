# Proof Artifacts: recurring_workflows, 10-seed run

Run date: 2026-03-06
Seeds: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111
Queries per seed: 3522
World: 80 workflows, 8 step slots + 3 preference slots
Stream: 60 steps, 12 workflows/step, replay queries/workflow 1
Updates: 5 workflows/step, 2 step updates + 1 preference updates

## Headline

- full_brain accuracy: **97.57% +/- 0.37%**
- best RAG (`vector_rag_rerank`) accuracy: **70.64% +/- 1.18%**
- margin: **+26.92 pp**

## Publishable assets

- `chart_seed_h2h_full_brain_vs_best_rag.png` -- seed-by-seed dumbbell chart (full_brain vs vector_rag_rerank), showing the 10-0 head-to-head sweep directly
- `publishable_key_results.md` / `.csv` -- one-row publication scorecard for this bundle

## Files

- `summary_table.md` / `.csv` -- aggregate metrics for each baseline
- `leaderboard.md` / `.csv` -- ranked publication table with baseline deltas
- `pairwise_accuracy_delta.md` / `.csv` -- pairwise accuracy differences
- `win_rate_matrix.md` / `.csv` -- seed-level head-to-head wins
- `per_seed_breakdown.md` / `.csv` -- long-form per-seed metrics
- `per_seed_accuracy_matrix.md` / `.csv` -- per-seed accuracy matrix
- `proof_digest.md` -- compact narrative summary for paper/blog usage
- `worked_example_trace.md` -- representative workflow-slot trace
- `learning_curve.png` -- mean accuracy over steps with std bands
- `seeds.json` -- exact seed list

## Reproduce

```bash
./scripts/run_recurring_workflows_proof.sh
```
