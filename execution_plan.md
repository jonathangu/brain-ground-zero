# Execution Plan

## Standard run protocol
1. Pick a family config (e.g., `configs/families/relational_drift.yaml`, `configs/families/sparse_feedback.yaml`).
2. Pick a baseline set (e.g., `configs/baselines/all.yaml`).
3. Fix seed(s) and budgets.
4. Run the harness to produce `runs/<run_id>/` output.
5. Generate a report/plot.

## Reproducibility rules
- All configs are committed.
- Each run directory contains a resolved config snapshot.
- Seed recorded in `summary.json`.

## Example
```bash
python -m brain_ground_zero.cli run \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --run-id demo_relational_drift

python -m brain_ground_zero.cli report --run-dir runs/demo_relational_drift
```

## Budgets
- `context_budget`: max items a baseline may read per query
- `teacher_budget`: max corrections per run
- `teacher_delay`: step delay for corrections
