# Recorded Head-to-Head: relational_drift_001

**Status: DRAFT** -- first end-to-end recorded head-to-head run.

This bundle contains a deterministic fixture and full traces for 8 baselines
run against the `relational_drift` family with seed 42.

## Key results

| Baseline | Accuracy |
|---|---|
| oracle | 1.0000 |
| full_brain | 0.9750 |
| vector_rag_rerank | 0.8962 |
| heuristic_stateful | 0.8163 |
| vector_rag | 0.7875 |
| graph_route_pg | 0.7850 |
| route_fn_only | 0.6438 |
| static_graph | 0.0000 |

**full_brain** achieves 97.5% accuracy vs the best RAG baseline (vector_rag_rerank) at 89.6%, a +7.9 pp advantage.

## Publishable assets

- `chart_accuracy_context_tradeoff.png` -- one-figure accuracy vs context/query comparison across all 8 baselines
- `publishable_key_results_compact.md` / `.csv` -- one-row compact scorecard for site/blog/paper
- `publishable_key_results.md` / `.csv` -- one-row publication scorecard for this bundle

## Bundle contents

```
fixture.yaml                     # 800 queries across 41 steps (seed=42)
metadata.yaml                    # run metadata, git SHA, baseline configs
traces/
  full_brain.jsonl               # per-event trace (query_response, correction_received)
  vector_rag_rerank.jsonl
  graph_route_pg.jsonl
  ... (8 baselines total)
scoring/
  summary_table.md / .csv        # per-baseline accuracy and metrics
  pairwise_accuracy_delta.md / .csv
  per_query_verdicts.csv         # every query verdict, spot-checkable
verification/
  fixture_hash.sha256            # SHA-256 of fixture.yaml
  trace_hashes.sha256            # SHA-256 of each trace file
  scoring_reproducibility.txt    # re-scoring from traces confirms match
```

## Reproduction

```bash
# one-command bundle build + validation + publishable refresh
./scripts/run_recorded_h2h_relational_drift_proof.sh

# 1. Generate the fixture (deterministic from seed)
python -m brain_ground_zero.cli generate_fixture \
  --family configs/families/relational_drift.yaml \
  --seed 42 \
  --output proof-results/recorded_h2h_relational_drift_001/fixture.yaml

# 2. Run all baselines against the fixture
python -m brain_ground_zero.cli recorded_h2h \
  --fixture proof-results/recorded_h2h_relational_drift_001/fixture.yaml \
  --baselines configs/baselines/all.yaml \
  --output proof-results/recorded_h2h_relational_drift_001/

# 3. Validate the bundle
python scripts/validate_recorded_h2h.py proof-results/recorded_h2h_relational_drift_001/
```

## Fairness

All fairness rules from `recorded_session_spec.md` apply:
- Fixture generated once, SHA-256 recorded; no baseline sees fixture before run.
- All baselines receive identical events in identical order.
- Baseline configs locked before run, recorded in metadata.yaml.
- Every query response appears in the trace (completeness verified).
- Scoring reproducible from traces alone (verification/scoring_reproducibility.txt).

See [`../../recorded_session_spec.md`](../../recorded_session_spec.md) for the full specification.
