# Proof Artifacts: relational_drift, 10-seed run

Run date: 2026-03-06
Seeds: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
Queries per seed: 800 (20 entity pairs x 40 steps)
World: 50 entities, 5 relation types, drift probability 0.1/step

## Files

- `summary_table.md` / `.csv` -- per-baseline accuracy, stale rate, false rate, context used (mean +/- std across 10 seeds)
- `pairwise_accuracy_delta.md` / `.csv` -- accuracy difference between every pair of baselines
- `win_rate_matrix.md` / `.csv` -- how many seeds each baseline beats each other baseline
- `worked_example_trace.md` -- one entity pair traced across all baselines over time
- `learning_curve.png` -- accuracy over steps with std-deviation bands
- `seeds.json` -- the seed list used

## Reproduce

```bash
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50,60,70,80,90,100
```
