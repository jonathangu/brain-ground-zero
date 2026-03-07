# Proof Artifacts: sparse_feedback, 3-seed run

Run date: 2026-03-06
Seeds: 13, 23, 33
Queries per seed: 1,800 (10 workflows x 4 slots x 45 steps)
World: 70 workflows, 6 step slots + 2 preference slots, bursty revisions
Feedback coverage: 19.8% +/- 0.8% of queries carry explicit feedback
Teacher budget: 70 corrections/run, delay 2 steps

## Key result

In sparse explicit feedback settings, `full_brain` reaches **97.96% +/- 0.29%** accuracy.
Best RAG baseline (`vector_rag_rerank`) reaches **67.70% +/- 0.82%**.
Delta: **+30.26 pp** in favor of `full_brain`.

`full_brain` also uses 5x less retrieval context than `vector_rag_rerank` (1,800 vs 9,000).

## Notes

This is a **lightweight multiseed spot-check** for the new `sparse_feedback` family, not a proof-scale run.

## Files

- `summary_table.md` / `.csv` -- per-baseline accuracy, stale rate, false rate, feedback coverage, context used (mean +/- std across 3 seeds)
- `pairwise_accuracy_delta.md` / `.csv` -- accuracy difference between every pair of baselines
- `win_rate_matrix.md` / `.csv` -- how many seeds each baseline beats each other baseline
- `worked_example_trace.md` -- one workflow-slot pair traced across all baselines over time
- `learning_curve.png` -- accuracy over steps with std-deviation bands
- `seeds.json` -- the seed list used

## Reproduce

```bash
python -m brain_ground_zero.cli multiseed \
  --family configs/families/sparse_feedback.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 13,23,33 \
  --run-id sparse_feedback_3seed
```
