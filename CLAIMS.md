# Claims

## What is proven

**Family: relational_drift** | **10 seeds** | **800 queries per seed** | **8 baselines**

1. **The full-brain method achieves 97.2% accuracy** (+/- 5.8% std) on relational drift, where entity-relation pairs change over time and the system must track the current ground truth.

2. **full_brain beats every non-oracle baseline on accuracy**, including:
   - +8.2 pp over the best RAG baseline (vector_rag_rerank, 89.0%)
   - +17.6 pp over plain vector RAG (79.7%)
   - +17.8 pp over heuristic stateful memory (79.4%)
   - +20.8 pp over graph+route+PG without structural plasticity (76.5%)
   - +32.5 pp over route_fn alone (64.7%)

3. **The win is consistent across seeds.** full_brain wins 10/10 seeds against every non-oracle baseline except vector_rag_rerank (9/10).

4. **Ablation ordering makes sense.** Each layer of the full method adds measurable value:
   - route_fn_only (64.7%) < graph_route_pg (76.5%) < full_brain (97.2%)
   - Structural plasticity (the jump from graph_route_pg to full_brain) is the single largest contributor: +20.8 pp.

5. **full_brain uses 5x less context than vector_rag_rerank** (800 vs 4000 tokens) while achieving higher accuracy. The mechanism is more efficient.

## What is not yet proven

- Performance on **recurring workflows** (family designed, not yet run)
- Performance on **sparse feedback / teacher-assisted learning** (family designed, not yet run)
- Performance on **memory compaction / structural plasticity stress tests** (family designed, not yet run)
- Behavior at **larger world sizes** (current world: 50 entities, 5 relation types)
- Performance with **real LLM routing** (current harness uses simulated policy functions, not live model calls)
- **Latency and cost** under production load

## Fairness guarantees

All baselines in every run receive:
- The same world state and entity set
- The same task/query stream in the same order
- The same context budget (except where a baseline's design inherently requires more, which is measured)
- The same correction stream and teacher budget
- The same scoring rubric

See [baseline_matrix.md](baseline_matrix.md) for what each baseline is allowed to update online.

## Reproducing

```bash
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50,60,70,80,90,100
```

The verified proof artifacts are tracked in [`proof-results/relational_drift_10seed/`](proof-results/relational_drift_10seed/).
