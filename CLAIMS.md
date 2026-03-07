# Claims

## Fast citation map (publishable artifacts)

- Cross-bundle evidence table: [`proof-results/publishable/tables/focus_evidence_table.md`](proof-results/publishable/tables/focus_evidence_table.md)
- Cross-bundle charts:
  - [`proof-results/publishable/charts/focus_margin_context.png`](proof-results/publishable/charts/focus_margin_context.png)
  - [`proof-results/publishable/charts/focus_ablation_ladder.png`](proof-results/publishable/charts/focus_ablation_ladder.png)
- Recorded H2H chart + scorecard:
  - [`proof-results/recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
  - [`proof-results/recorded_h2h_relational_drift_10seed/publishable_key_results.md`](proof-results/recorded_h2h_relational_drift_10seed/publishable_key_results.md)
- Sparse-feedback chart + scorecard:
  - [`proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
  - [`proof-results/sparse_feedback_10seed/publishable_key_results.md`](proof-results/sparse_feedback_10seed/publishable_key_results.md)
- Recurring-workflows chart + scorecard:
  - [`proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
  - [`proof-results/recurring_workflows_10seed/publishable_key_results.md`](proof-results/recurring_workflows_10seed/publishable_key_results.md)

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

---

**Family: recurring_workflows** | **10 seeds** | **3,522 queries per seed** | **8 baselines**

1. **The full-brain method achieves 97.6% accuracy** (+/- 0.4% std) on recurring workflows with repeated task families, workflow-step updates, preference updates, and contradiction/reversion events.

2. **full_brain beats every non-oracle baseline by a wide margin**, including:
   - +26.9 pp over the best RAG baseline (vector_rag_rerank, 70.6%)
   - +34.2 pp over plain vector RAG (63.4%)
   - +37.2 pp over graph+route+PG without structural plasticity (60.4%)
   - +63.5 pp over route_fn alone (34.1%)

3. **The win is perfectly consistent across seeds.** full_brain wins 10/10 seeds against every non-oracle baseline.

4. **Ablation ordering is consistent and strong.**
   - route_fn_only (34.1%) < graph_route_pg (60.4%) < full_brain (97.6%)
   - Structural plasticity contributes the largest jump: +37.2 pp from graph_route_pg to full_brain.

5. **full_brain uses 5x less context than vector_rag_rerank** (1.0 vs 5.0 context/query) while achieving much higher accuracy.

## Recorded head-to-head: proof-scale bundle

**Recorded head-to-head: relational_drift_10seed** | **10 seeds** | **800 queries per seed** | **8 baselines**

1. **The full-brain method achieves 99.15% accuracy** (+/- 0.27% std) on recorded deterministic fixtures generated from the relational drift stream.

2. **full_brain beats every non-oracle baseline on accuracy**, including:
   - +9.71 pp over the best RAG baseline (vector_rag_rerank, 89.44%)
   - +17.10 pp over plain vector RAG (82.05%)
   - +23.29 pp over graph+route+PG without structural plasticity (75.86%)
   - +35.31 pp over route_fn alone (63.84%)

3. **The win is consistent across seeds.** full_brain beats vector_rag_rerank 10/10 seeds (10-0-0) and 10/10 against every other non-oracle baseline.

4. **Ablation ordering remains strong in recorded replay.**
   - route_fn_only (63.84%) < graph_route_pg (75.86%) < full_brain (99.15%)
   - Structural plasticity contributes the largest jump: +23.29 pp from graph_route_pg to full_brain.

5. **full_brain uses 5x less context than vector_rag_rerank** (1.0 vs 5.0 context/query) while achieving higher accuracy.

See [`proof-results/recorded_h2h_relational_drift_10seed/`](proof-results/recorded_h2h_relational_drift_10seed/).

## Historical first artifact (preserved headline)

**Recorded head-to-head: relational_drift_001** | **1 seed (42)** | **800 queries** | **8 baselines**

- First scored recorded-h2h bundle with deterministic fixture, full JSONL traces, and SHA-256 verification.
- full_brain 97.5% vs best RAG (vector_rag_rerank) 89.6% (+7.9 pp). Directionally consistent with both simulation and the new proof-scale recorded run.
- See [`proof-results/recorded_h2h_relational_drift_001/`](proof-results/recorded_h2h_relational_drift_001/).

---

**Family: sparse_feedback** | **10 seeds** | **1,800 queries per seed** | **8 baselines**

1. **The full-brain method achieves 92.0% accuracy** (+/- 18.3% std) on sparse feedback, where the system receives explicit teacher signals on only ~19% of queries and must generalize from sparse corrections.

2. **full_brain beats every non-oracle baseline by a wide margin**, including:
   - +24.9 pp over the best RAG baseline (vector_rag_rerank, 67.0%)
   - +31.5 pp over plain vector RAG (60.5%)
   - +40.6 pp over heuristic stateful memory (51.4%)
   - +42.6 pp over graph+route+PG without structural plasticity (49.4%)
   - +55.0 pp over route_fn alone (37.0%)

3. **The win is consistent across seeds.** full_brain wins 9/10 seeds against the best RAG baseline (vector_rag_rerank) and 10/10 against all other non-oracle baselines.

4. **Ablation ordering is consistent and strong.**
   - route_fn_only (37.0%) < graph_route_pg (49.4%) < full_brain (92.0%)
   - Structural plasticity contributes the largest jump: +42.6 pp from graph_route_pg to full_brain.

5. **full_brain uses 5x less context than vector_rag_rerank** (1.0 vs 5.0 context/query) while achieving much higher accuracy.

## What is not yet proven

- **Recorded-session head-to-head on real product traces.** The spec, fixture schema, and example are defined ([`recorded_session_spec.md`](recorded_session_spec.md)), but no scored results from real sessions exist yet.
- Performance on **memory compaction / structural plasticity stress tests** (family designed, not yet run)
- Behavior at **larger world sizes** (current proof scales are modest: relational uses 50 entities/5 relation types; recurring uses 80 workflows/11 slots)
- Performance with **real LLM routing** (current harness uses simulated policy functions, not live model calls)
- **Latency and cost** under production load

## Spot-check evidence (not proof-scale)

- **Recurring workflows, 3 seeds:** directionally consistent with the relational-drift ordering. See [`proof-results/recurring_workflows_3seed/`](proof-results/recurring_workflows_3seed/). (Superseded by 10-seed proof run.)
- **Sparse feedback, 3 seeds:** directionally consistent with the 10-seed proof. See [`proof-results/sparse_feedback_3seed/`](proof-results/sparse_feedback_3seed/). (Superseded by 10-seed proof run.)

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

./scripts/run_recorded_h2h_proof.sh
```

The verified proof artifacts are tracked in [`proof-results/relational_drift_10seed/`](proof-results/relational_drift_10seed/).
Recurring-workflow proof artifacts are tracked in [`proof-results/recurring_workflows_10seed/`](proof-results/recurring_workflows_10seed/).
Sparse-feedback proof artifacts are tracked in [`proof-results/sparse_feedback_10seed/`](proof-results/sparse_feedback_10seed/).
Recorded head-to-head proof artifacts are tracked in [`proof-results/recorded_h2h_relational_drift_10seed/`](proof-results/recorded_h2h_relational_drift_10seed/).
