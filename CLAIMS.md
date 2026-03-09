# Claims

## Claim tiers

This document separates claims into three tiers:

- **Headline** -- directly supported by proof-scale artifacts, safe for paper/site/blog without hedging.
- **Supporting** -- backed by proof artifacts but require context or qualification; not standalone headline material.
- **Not-safe** -- cannot be made; either unmeasured, untested, or contradicted by evidence.

> **Conflation warning:** The relational_drift family has two evaluation modes with different numbers. *Recorded H2H* uses deterministic fixture replay (99.15%). *Simulation* uses simulated policy functions (97.2%). These must never be conflated. Every claim below specifies which mode applies.

---

## Fast citation map (publishable artifacts)

- Starter pack: [`proof-results/publishable/site_blog_paper_starter.md`](proof-results/publishable/site_blog_paper_starter.md)
- Cross-bundle compact evidence table: [`proof-results/publishable/tables/focus_evidence_table_compact.md`](proof-results/publishable/tables/focus_evidence_table_compact.md)
- Cross-bundle full evidence table: [`proof-results/publishable/tables/focus_evidence_table.md`](proof-results/publishable/tables/focus_evidence_table.md)
- Cross-bundle charts:
  - [`proof-results/publishable/charts/focus_margin_context.png`](proof-results/publishable/charts/focus_margin_context.png)
  - [`proof-results/publishable/charts/focus_ablation_ladder.png`](proof-results/publishable/charts/focus_ablation_ladder.png)
- Recorded H2H chart + scorecard:
  - [`proof-results/recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
  - [`proof-results/recorded_h2h_relational_drift_10seed/publishable_key_results_compact.md`](proof-results/recorded_h2h_relational_drift_10seed/publishable_key_results_compact.md)
  - [`proof-results/recorded_h2h_relational_drift_10seed/publishable_key_results.md`](proof-results/recorded_h2h_relational_drift_10seed/publishable_key_results.md)
- Sparse-feedback chart + scorecard:
  - [`proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
  - [`proof-results/sparse_feedback_10seed/publishable_key_results_compact.md`](proof-results/sparse_feedback_10seed/publishable_key_results_compact.md)
  - [`proof-results/sparse_feedback_10seed/publishable_key_results.md`](proof-results/sparse_feedback_10seed/publishable_key_results.md)
- Recurring-workflows chart + scorecard:
  - [`proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`](proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png)
  - [`proof-results/recurring_workflows_10seed/publishable_key_results_compact.md`](proof-results/recurring_workflows_10seed/publishable_key_results_compact.md)
  - [`proof-results/recurring_workflows_10seed/publishable_key_results.md`](proof-results/recurring_workflows_10seed/publishable_key_results.md)

---

## Headline claims

### H1. Recorded H2H -- relational_drift (10-seed, deterministic replay)

**Evaluation mode: recorded head-to-head with deterministic fixture replay and SHA-256 verification.**

| Metric | Value |
|---|---|
| full_brain accuracy | 99.15% +/- 0.27% |
| best RAG (vector_rag_rerank) | 89.44% +/- 1.68% |
| margin | +9.71 pp |
| head-to-head | 10-0-0 |
| context efficiency | 5.0x lower (1.0 vs 5.0 per query) |
| seeds | 10 |
| queries per seed | 800 |
| baselines | 8 |

Proof artifacts: [`proof-results/recorded_h2h_relational_drift_10seed/`](proof-results/recorded_h2h_relational_drift_10seed/)

The seed-42 single-seed artifact at [`proof-results/recorded_h2h_relational_drift_001/`](proof-results/recorded_h2h_relational_drift_001/) is superseded. Do not cite as headline.

### H2. Recurring workflows (10-seed, simulation)

**Evaluation mode: simulated policy functions, deterministic given seed.**

| Metric | Value |
|---|---|
| full_brain accuracy | 97.6% +/- 0.4% |
| best RAG (vector_rag_rerank) | 70.6% +/- 1.2% |
| margin | +26.9 pp |
| head-to-head | 10-0-0 |
| context efficiency | 5.0x lower (1.0 vs 5.0 per query) |
| seeds | 10 |
| queries per seed | 3,522 |
| baselines | 8 |

Proof artifacts: [`proof-results/recurring_workflows_10seed/`](proof-results/recurring_workflows_10seed/)

### H3. Sparse feedback (10-seed, simulation)

**Evaluation mode: simulated policy functions, deterministic given seed. Explicit feedback on ~19% of queries.**

| Metric | Value |
|---|---|
| full_brain accuracy | 92.0% +/- 18.3% |
| best RAG (vector_rag_rerank) | 67.0% +/- 1.4% |
| margin | +24.9 pp |
| head-to-head | 9-1-0 |
| context efficiency | 5.0x lower (1.0 vs 5.0 per query) |
| seeds | 10 |
| queries per seed | 1,800 |
| baselines | 8 |

**Variance disclosure:** The 18.3% std reflects high seed-level variance under sparse signal (~19% explicit feedback coverage). Any headline use of this result must include the +/- 18.3% figure. The 9-1-0 head-to-head record prevents claiming "always wins" across families.

Proof artifacts: [`proof-results/sparse_feedback_10seed/`](proof-results/sparse_feedback_10seed/)

### H4. Relational drift -- simulation (10-seed)

**Evaluation mode: simulated policy functions, deterministic given seed. This is NOT the recorded H2H; see H1 for that.**

| Metric | Value |
|---|---|
| full_brain accuracy | 97.2% +/- 5.8% |
| best RAG (vector_rag_rerank) | 89.0% +/- 2.3% |
| margin | +8.2 pp |
| head-to-head | 9/10 vs vector_rag_rerank; 10/10 vs all other non-oracle baselines |
| context efficiency | 5.0x lower (800 vs 4,000 tokens) |
| seeds | 10 |
| queries per seed | 800 |
| baselines | 8 |

Proof artifacts: [`proof-results/relational_drift_10seed/`](proof-results/relational_drift_10seed/)

### H5. Cross-family summary (tightest honest wording)

full_brain achieves +9.7 to +26.9 pp over the best RAG baseline (vector_rag_rerank) across three proof-scale families (relational drift recorded H2H, recurring workflows, sparse feedback), each at 10 seeds with 8 baselines, while using 5x less context per query. Cross-family head-to-head record: 29-1-0 across 30 seed-level comparisons.

Weakest link: sparse_feedback std is 18.3%; the 9-1-0 record there prevents claiming a perfect sweep.

---

## Supporting claims

### S1. Ablation ordering is consistent across all families

In every family, the ablation ladder holds without reversal:

route_fn_only < graph_route_pg < full_brain

Structural plasticity (the jump from graph_route_pg to full_brain) is the single largest contributor in every family:

| Family | Structural plasticity delta |
|---|---|
| Recorded H2H relational_drift | +23.3 pp (full_brain 99.15% vs graph_route_pg 75.86%) |
| Recurring workflows | +37.2 pp (full_brain 97.6% vs graph_route_pg 60.4%) |
| Sparse feedback | +42.6 pp (full_brain 92.0% vs graph_route_pg 49.4%) |
| Simulation relational_drift | +20.8 pp (full_brain 97.2% vs graph_route_pg 76.5%) |

### S2. Policy-gradient routing adds measurable value over route_fn alone

| Family | graph_route_pg minus route_fn_only |
|---|---|
| Recorded H2H relational_drift | +12.0 pp |
| Recurring workflows | +26.3 pp |
| Sparse feedback | +12.4 pp |
| Simulation relational_drift | +11.8 pp |

### S3. Per-baseline accuracy ladder (simulation relational_drift, 10-seed)

| Baseline | Accuracy | Std |
|---|---|---|
| oracle | 100% | 0.0% |
| full_brain | 97.2% | 5.8% |
| vector_rag_rerank | 89.0% | 2.3% |
| vector_rag | 79.7% | 2.0% |
| heuristic_stateful | 79.4% | 2.2% |
| graph_route_pg | 76.5% | 2.5% |
| route_fn_only | 64.7% | 1.6% |

### S4. Pairwise deltas vs non-RAG baselines

**Simulation relational_drift (10-seed):**

| Comparison | Delta |
|---|---|
| full_brain vs vector_rag | +17.6 pp |
| full_brain vs heuristic_stateful | +17.8 pp |
| full_brain vs graph_route_pg | +20.8 pp |
| full_brain vs route_fn_only | +32.5 pp |

**Recurring workflows (10-seed):**

| Comparison | Delta |
|---|---|
| full_brain vs vector_rag | +34.2 pp |
| full_brain vs graph_route_pg | +37.2 pp |
| full_brain vs route_fn_only | +63.5 pp |

**Sparse feedback (10-seed):**

| Comparison | Delta |
|---|---|
| full_brain vs vector_rag | +31.5 pp |
| full_brain vs heuristic_stateful | +40.6 pp |
| full_brain vs graph_route_pg | +42.6 pp |
| full_brain vs route_fn_only | +55.0 pp |

---

## Not-safe claims (do not make)

| Claim | Why it is not safe |
|---|---|
| Performance on memory compaction / structural plasticity stress tests | Family designed but not run |
| Performance at larger world sizes | Current proof uses modest scales (50 entities / 80 workflows / 3,522 max queries per seed) |
| Performance with real LLM routing | Harness uses simulated policy functions, not live model calls |
| Latency and cost under production load | Not measured at proof scale |
| Real-session head-to-head on product traces | Spec defined ([`recorded_session_spec.md`](recorded_session_spec.md)), no scored results |
| "Always wins across all families" | sparse_feedback h2h is 9-1-0 |
| Legacy single-seed numbers as headline | recorded_h2h_001 is superseded by 10-seed bundle |
| Cross-family accuracy without specifying evaluation mode | Simulation relational_drift (97.2%) and recorded H2H relational_drift (99.15%) are different evaluation modes |

---

## Honest gaps

**Simulation-only evaluation.** Ground Zero uses simulated policy functions with deterministic outcomes, not live LLM calls. The benchmark validates the retrieval-routing mechanism in isolation; end-to-end performance with live model inference is not measured at proof scale.

**Moderate world sizes.** The largest family uses 80 workflows and 3,522 queries per seed. Scaling behavior at 10x-100x is unknown; graph traversal cost, plasticity convergence, and homeostatic stability at larger scales are untested.

**Seed sensitivity under sparse feedback.** The sparse feedback family shows +/- 18.3% std across seeds. Accuracy depends on which 19% of queries receive explicit feedback. This variance is reported but not resolved.

**Custom benchmark, not community standard.** Ground Zero is purpose-built. It tests specific failure modes well but does not establish generality. Results do not directly compare to other systems on community benchmarks.

**No ablation of teacher supervision.** The teacher signal is part of the full system but is not ablated independently. The relative contribution of teacher vs outcome-only learning is not isolated.

**Embedding dependency.** Retrieval quality is bounded by embedding quality at the seeding stage. If the correct node is never seeded by embedding similarity, the system cannot learn a route to it.

---

## Fairness guarantees

All baselines in every run receive:
- The same world state and entity set
- The same task/query stream in the same order
- The same context budget (except where a baseline's design inherently requires more, which is measured)
- The same correction stream and teacher budget
- The same scoring rubric

See [baseline_matrix.md](baseline_matrix.md) for what each baseline is allowed to update online.

---

## Spot-check evidence (not proof-scale)

- **Recurring workflows, 3 seeds:** directionally consistent with the 10-seed proof. See [`proof-results/recurring_workflows_3seed/`](proof-results/recurring_workflows_3seed/). (Superseded by 10-seed proof run.)
- **Sparse feedback, 3 seeds:** directionally consistent with the 10-seed proof. See [`proof-results/sparse_feedback_3seed/`](proof-results/sparse_feedback_3seed/). (Superseded by 10-seed proof run.)

---

## Reproducing

```bash
python -m brain_ground_zero.cli multiseed \
  --family configs/families/relational_drift.yaml \
  --baselines configs/baselines/all.yaml \
  --seeds 10,20,30,40,50,60,70,80,90,100

./scripts/run_recurring_workflows_proof.sh
./scripts/run_sparse_feedback_proof.sh
./scripts/run_recorded_h2h_proof.sh
```

Verified proof artifacts:
- [`proof-results/relational_drift_10seed/`](proof-results/relational_drift_10seed/)
- [`proof-results/recurring_workflows_10seed/`](proof-results/recurring_workflows_10seed/)
- [`proof-results/sparse_feedback_10seed/`](proof-results/sparse_feedback_10seed/)
- [`proof-results/recorded_h2h_relational_drift_10seed/`](proof-results/recorded_h2h_relational_drift_10seed/)
