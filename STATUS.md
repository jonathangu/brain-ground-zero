# Status

## Current state (2026-03-06)

**The 10-seed relational_drift proof is complete and published.**

- Proof artifacts: [`proof-results/relational_drift_10seed/`](proof-results/relational_drift_10seed/)
- Claims: [CLAIMS.md](CLAIMS.md)
- Headline: full_brain 97.2% vs best-RAG 89.0% (+8.2 pp), consistent across 10 seeds

The harness, baselines, reporting pipeline, and multi-seed aggregation are all working. Smoke tests and config validation pass.

## What is done

- Benchmark contract and spec docs (families, schemas, scoring, baselines, execution plan)
- Python harness with CLI (`smoke`, `run`, `multiseed` commands)
- 8 baselines implemented (oracle, full_brain, graph_route_pg, heuristic_stateful, vector_rag, vector_rag_rerank, route_fn_only, random)
- relational_drift family: 10-seed run, all reporting artifacts generated and tracked
- Publication-ready reporting: summary tables, pairwise deltas, win-rate matrix, worked-example trace, learning curves with std bands

## Next steps

1. **Stronger proof variants** -- fixed-session head-to-head runs, bootstrap confidence intervals, or larger seed counts to tighten error bars.
2. **Next benchmark family** -- recurring workflows or sparse feedback (both designed in harness, not yet run).
3. **Larger world sizes** -- scale beyond 50 entities / 5 relation types.
4. **Real LLM routing** -- replace simulated policy functions with live model calls.

## Build log (historical)

| Milestone | Description | Status |
|---|---|---|
| M1 | Benchmark contract docs | Done |
| M2 | Harness scaffold | Done |
| M3 | relational_drift family + baselines | Done |
| M4 | Reporting and validation | Done |
| M5 | Publication-ready reporting + 10-seed proof | Done |
