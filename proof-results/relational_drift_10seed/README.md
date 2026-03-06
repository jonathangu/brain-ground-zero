# Proof Artifacts: relational_drift, 10-seed run

Run date: 2026-03-06
Seeds: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
Queries per seed: 800 (20 entity pairs x 40 steps)
World: 50 entities, 5 relation types, drift probability 0.1/step

## Headline numbers to quote

- **full_brain accuracy: 97.2% +/- 5.8** (10-seed mean +/- std)
- **Best RAG baseline (vector_rag_rerank): 89.0% +/- 2.3**
- **Gap: +8.2 percentage points over best RAG**
- **Seed consistency: full_brain wins 10/10 seeds vs all baselines except vector_rag_rerank (9/10)**

See `summary_table.md` for the complete table and `win_rate_matrix.md` for pairwise seed counts.

## What this artifact proves

- The full-brain mechanism (graph memory + route_fn + PG updates + structural plasticity) dominates RAG and partial-brain ablations on the **relational drift** task family.
- Structural plasticity is the single largest contributor: +20.8 pp from graph_route_pg to full_brain.
- full_brain uses 5x less context than vector_rag_rerank (800 vs 4000 tokens) while achieving higher accuracy.

## What this artifact does NOT prove

- Performance on other benchmark families (recurring workflows, sparse feedback, memory compaction) -- not yet run.
- Behavior at larger world sizes -- current world is 50 entities, 5 relation types.
- Performance with real LLM routing -- this harness uses simulated policy functions, not live model calls.
- Latency or cost under production load.
- That the advantage holds under different drift rates, query distributions, or correction budgets.

See [CLAIMS.md](../../CLAIMS.md) for the full scope statement.

## Files

| File | What it contains | When to use it |
|---|---|---|
| `summary_table.md` / `.csv` | Per-baseline accuracy, stale rate, false rate, context used (mean +/- std across 10 seeds) | Primary results table; quote numbers from here |
| `pairwise_accuracy_delta.md` / `.csv` | Accuracy difference between every pair of baselines (row minus column) | Comparing any two baselines head-to-head |
| `win_rate_matrix.md` / `.csv` | How many of the 10 seeds each baseline beats each other baseline | Demonstrating consistency across seeds |
| `worked_example_trace.md` | One entity pair traced across all baselines over time | Understanding *why* baselines differ |
| `learning_curve.png` | Accuracy over steps with std-deviation bands | Visual summary of learning dynamics |
| `seeds.json` | The seed list used | Exact reproduction |

## Reproduce

```bash
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50,60,70,80,90,100
```

Output lands in `runs/<run_id>/artifacts/`. Compare against the tracked files in this directory.
