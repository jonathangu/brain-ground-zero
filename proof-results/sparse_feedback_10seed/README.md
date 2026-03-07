# Proof Artifacts: sparse_feedback, 10-seed run

Run date: 2026-03-07
Seeds: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111
World: 70 workflows, 6 step slots + 2 preference slots
Feedback: explicit_feedback_rate 0.06, focused_feedback_rate 0.45, teacher_budget 70

## Headline

- full_brain accuracy: **91.96%**
- best RAG (`vector_rag_rerank`) accuracy: **67.05%**
- margin: **+24.91 pp**
- full_brain vs vector_rag_rerank head-to-head: **9-1-0** (wins-losses-ties across 10 seeds)
- full_brain context/query: **1.00** vs vector_rag_rerank: **5.00**

## Notes

This README is scaffolding based on the completed 10-seed proof run.
Re-running `./scripts/run_sparse_feedback_proof.sh` will regenerate it from actual outputs.

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
./scripts/run_sparse_feedback_proof.sh
```
