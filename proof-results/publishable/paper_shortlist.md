# Paper Shortlist: Figures and Tables

Authoritative placement guide for the Brain-vs-RAG Ground-Zero paper.
Source of truth: phase0 figure-ledger.md and table-ledger.md.

---

## Main Paper Figures

### F1. Margin and context efficiency (two-panel)
- **File:** `proof-results/publishable/charts/focus_margin_context.png`
- **Caption:** Accuracy margin of full_brain over the best RAG baseline (left) and context cost ratio (right) across three benchmark families. full_brain achieves +9.7 to +26.9 pp margins while consuming 5x less context per query.

### F2. Ablation ladder across families
- **File:** `proof-results/publishable/charts/focus_ablation_ladder.png`
- **Caption:** Ablation ladder showing accuracy at each mechanism stage (route function only, graph + route + policy gradient, full brain) across three benchmark families. Structural plasticity contributes the largest accuracy jump in every family.

### F3. Recorded H2H seed-by-seed head-to-head
- **File:** `proof-results/recorded_h2h_relational_drift_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`
- **Caption:** Per-seed accuracy comparison between full_brain and vector_rag_rerank on the recorded head-to-head relational-drift benchmark (10 seeds, 800 queries each). full_brain wins every seed (10-0-0).

### F4. Recurring workflows seed-by-seed head-to-head (include if space allows)
- **File:** `proof-results/recurring_workflows_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`
- **Caption:** Per-seed accuracy comparison on the recurring-workflows benchmark (10 seeds, 3,522 queries each). full_brain wins every seed (10-0-0) with margins exceeding 25 pp.

### F5. Sparse feedback seed-by-seed head-to-head (include if space allows)
- **File:** `proof-results/sparse_feedback_10seed/chart_seed_h2h_full_brain_vs_best_rag.png`
- **Caption:** Per-seed accuracy comparison on the sparse-feedback benchmark (10 seeds, 1,800 queries each, ~19% feedback coverage). full_brain wins 9 of 10 seeds (9-1-0).
- **Note:** Acknowledge the seed-77 loss and high full_brain std (18.3%) in text.

## Main Paper Table

### T1. Cross-bundle evidence table (compact)
- **File:** `proof-results/publishable/tables/focus_evidence_table_compact.md`
- **CSV:** `proof-results/publishable/tables/focus_evidence_table_compact.csv`
- **Caption:** Summary of benchmark results across three proof families. Each row reports full_brain and best-RAG accuracy (mean +/- std over 10 seeds), the margin, head-to-head win record, context cost ratio, and ablation delta from structural plasticity.

---

## Appendix Figures

### F6. Recorded H2H learning curve
- **File:** `proof-results/recorded_h2h_relational_drift_10seed/learning_curve.png`
- **Caption:** Mean accuracy over evaluation steps for all baselines on the recorded H2H relational-drift benchmark (10 seeds, shaded bands = 1 std). full_brain sustains near-ceiling accuracy throughout.

### F7. Recurring workflows learning curve
- **File:** `proof-results/recurring_workflows_10seed/learning_curve.png`
- **Caption:** Mean accuracy over evaluation steps for all baselines on the recurring-workflows benchmark (10 seeds). full_brain maintains ~97% while non-oracle methods decline.

### F8. Relational drift learning curve (simulation)
- **File:** `proof-results/relational_drift_10seed/learning_curve.png`
- **Caption:** Mean accuracy over evaluation steps for all baselines on the relational-drift simulation benchmark (10 seeds).
- **Note:** Include only if distinguishing simulation vs recorded modes in discussion.

### F9. Sparse feedback learning curve
- **File:** `proof-results/sparse_feedback_10seed/learning_curve.png`
- **Caption:** Mean accuracy over evaluation steps for all baselines on the sparse-feedback benchmark (10 seeds, ~19% feedback coverage). Wide confidence bands reflect seed-level variance.

## Appendix Tables

### T2. Cross-bundle evidence table (full)
- **File:** `proof-results/publishable/tables/focus_evidence_table.md`
- **CSV:** `proof-results/publishable/tables/focus_evidence_table.csv`
- **Caption:** Extended evidence table with per-stage ablation accuracies and experiment scale for all three benchmark families.

### T7. Recorded H2H full summary
- **File:** `proof-results/recorded_h2h_relational_drift_10seed/summary_table.md`
- **Caption:** Accuracy for all baselines on the recorded H2H relational-drift benchmark (10 seeds, mean +/- std). Oracle ceiling included.

### T8. Recurring workflows full summary
- **File:** `proof-results/recurring_workflows_10seed/summary_table.md`
- **Caption:** Accuracy for all baselines on the recurring-workflows benchmark (10 seeds, 3,522 queries/seed).

### T10. Sparse feedback full summary
- **File:** `proof-results/sparse_feedback_10seed/summary_table.md`
- **Caption:** Accuracy for all baselines on the sparse-feedback benchmark (10 seeds, 1,800 queries/seed, ~19% feedback coverage).

### T11. Pairwise accuracy delta matrix (recorded H2H only)
- **File:** `proof-results/recorded_h2h_relational_drift_10seed/pairwise_accuracy_delta.csv`
- **Caption:** Pairwise accuracy deltas (row minus column) for all baseline pairs on the recorded H2H relational-drift benchmark. Positive values indicate row advantage.

### T12. Win-rate matrix (recorded H2H only)
- **File:** `proof-results/recorded_h2h_relational_drift_10seed/win_rate_matrix.csv`
- **Caption:** Win-rate matrix (seeds won out of 10) for all baseline pairs on the recorded H2H relational-drift benchmark.

### T18. Worked example trace (recorded H2H)
- **File:** `proof-results/recorded_h2h_relational_drift_10seed/worked_example_trace.md`
- **Caption:** Worked trace showing how each baseline responds as the ground-truth relation for a single entity pair changes over time.
- **Note:** Format as prose with inline tables, not a standalone table.

---

## Exclusions

| ID | Title | Reason |
|---|---|---|
| F10 | Accuracy-context scatter (1 seed) | Superseded by F1 (10-seed data). Single-seed only. |
| F11 | Recurring workflows LC (3 seed) | Superseded by F7 (10-seed proof). |
| F12 | Sparse feedback LC (3 seed) | Superseded by F9 (10-seed proof). |
| T3 | Recorded H2H scorecard | Redundant with T1 cross-bundle table. |
| T4 | Recorded H2H compact scorecard | Subsumed by T1. Blog/site format. |
| T5 | Recurring workflows scorecard | Subsumed by T1. Blog/site format. |
| T6 | Sparse feedback scorecard | Subsumed by T1. Blog/site format. |
| T9 | Relational drift full summary (sim) | Overlaps T7 (recorded H2H is stronger evidence). |
| T13 | Per-seed accuracy matrices | Raw data only. Supplementary material if needed. |
| T14 | Leaderboard tables | Redundant with summary tables T7-T10. |
| T15 | Legacy single-seed scorecard | Superseded by 10-seed bundle. |
| T16 | Legacy single-seed summary | Superseded by 10-seed bundle. |
| T17 | Compact per-bundle scorecards | Blog/site format. All data in T1. |

---

## Counts

- **Main paper:** 3 mandatory figures (F1-F3) + 2 conditional (F4-F5) + 1 table (T1)
- **Appendix:** 4 learning curves (F6-F9) + 7 tables (T2, T7-T8, T10-T12, T18)
- **Excluded:** 3 figures (F10-F12) + 10 tables (T3-T6, T9, T13-T17)

## Notes for paper-writing agent

1. F1-F3 and T1 are mandatory. They carry all top-level claims.
2. F4-F5 strengthen the story if page budget allows; demote to appendix otherwise.
3. Sparse feedback (F5, T10) must acknowledge 18.3% std and the 9-1-0 record.
4. F8 (relational drift sim LC) is optional -- include only if the paper distinguishes simulation vs recorded replay.
5. Appendix learning curves (F6-F9) have 8 overlapping lines; note readability at small sizes.
6. T11-T12: include only for recorded H2H family. Other families' matrices are supplementary-only.
7. T18: use one worked trace (recorded H2H) in appendix; others are supplementary.
8. Never cite 3-seed bundles or single-seed legacy artifacts.
