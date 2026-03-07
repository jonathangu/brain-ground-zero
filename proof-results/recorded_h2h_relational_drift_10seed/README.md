# Proof Artifacts: recorded_h2h relational_drift, 10-seed run

Run date: 2026-03-07
Seeds: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111
Queries per seed: 800
Steps per seed: 40 (+ fixture step 0)
Updates/query stream: 6 updates/step, 20 queries/step

## Headline

- full_brain accuracy: **99.15% +/- 0.27%**
- best RAG (`vector_rag_rerank`) accuracy: **89.44% +/- 1.68%**
- margin: **+9.71 pp**

## Files

- `summary_table.md` / `.csv` -- aggregate metrics for each baseline
- `leaderboard.md` / `.csv` -- ranked publication table with baseline deltas
- `pairwise_accuracy_delta.md` / `.csv` -- pairwise accuracy differences
- `win_rate_matrix.md` / `.csv` -- seed-level head-to-head wins
- `per_seed_breakdown.md` / `.csv` -- long-form per-seed metrics
- `per_seed_accuracy_matrix.md` / `.csv` -- per-seed accuracy matrix
- `proof_digest.md` -- compact narrative summary for paper/blog usage
- `worked_example_trace.md` -- representative relation trace from a recorded seed
- `learning_curve.png` -- mean per-step accuracy over seeds with std bands
- `seed_bundle_index.md` / `.csv` -- index linking each seed to its deterministic replay bundle
- `seed_bundle_validation.txt` -- per-seed validator output
- `multiseed_validation.txt` -- aggregate validator output
- `seed_<N>/` -- full recorded bundle for each seed (fixture, traces, scoring, verification)

## Reproduce

```bash
./scripts/run_recorded_h2h_proof.sh
```
