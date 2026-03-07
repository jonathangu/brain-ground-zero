# Proof Artifacts: sparse_feedback, 10-seed run

Run date: 2026-03-07
Seeds: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111
Queries per seed: 1800
World: 70 workflows, 6 step slots + 2 preference slots
Stream: 45 steps, 10 workflows/step, explicit feedback rate 6%, focused feedback rate 45%
Updates: 4 workflows/step, 2 step updates + 1 preference updates, contradiction rate 20%

## Headline

- full_brain accuracy: **91.96% +/- 18.30%**
- best RAG (`vector_rag_rerank`) accuracy: **67.05% +/- 8.66%**
- margin: **+24.91 pp**
- context/query: full_brain 1.00 vs vector_rag_rerank 5.00 (5x lower for full_brain)
- full_brain vs vector_rag_rerank head-to-head: **9-1-0**

## What this tests

Sparse feedback simulates a teacher-assisted learning scenario where the system receives explicit correctness signals on only ~19% of queries. The full-brain mechanism must amplify these sparse signals via its graph memory and structural plasticity to maintain high accuracy across the remaining ~81% of unlabeled queries.

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
