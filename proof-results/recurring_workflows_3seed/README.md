# Proof Artifacts: recurring_workflows, 3-seed run

Run date: 2026-03-06
Seeds: 11, 22, 33
Queries per seed: 1,280 (8 workflows x 4 slots x 40 steps)
World: 50 workflows, 6 step slots + 2 preference slots, 9 action types, 6 preference types
Updates: 3 workflows/step, 2 step updates + 1 preference update per workflow
Recurrence: bias 0.75 with recent window 14

## Notes

This is a **small multiseed spot-check** for the new recurring_workflows family, not a full proof run.
For proof-scale artifacts, see [`../recurring_workflows_10seed/`](../recurring_workflows_10seed/).

## Files

- `summary_table.md` / `.csv` -- per-baseline accuracy, stale rate, false rate, context used (mean +/- std across 3 seeds)
- `pairwise_accuracy_delta.md` / `.csv` -- accuracy difference between every pair of baselines
- `win_rate_matrix.md` / `.csv` -- how many seeds each baseline beats each other baseline
- `worked_example_trace.md` -- one workflow-slot pair traced across all baselines over time
- `learning_curve.png` -- accuracy over steps with std-deviation bands
- `seeds.json` -- the seed list used

## Reproduce

```bash
python -m brain_ground_zero.cli multiseed \
  --family configs/families/recurring_workflows.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 11,22,33 \
  --run-id recurring_workflows_3seed
```
