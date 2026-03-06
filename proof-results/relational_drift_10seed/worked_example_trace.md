# Worked Example: E048 -> E001

How each baseline answers the same query as the ground-truth relation drifts over time.

| step | truth | full_brain | graph_route_pg | heuristic_stateful | oracle | route_fn_only | static_graph | vector_rag | vector_rag_rerank |
|---|---|---|---|---|---|---|---|---|---|
| 13 | manages | manages (ok) | manages (ok) | manages (ok) | manages (ok) | manages (ok) | null (WRONG) | owns (WRONG) | manages (ok) |
| 14 | manages | manages (ok) | owns (WRONG) | manages (ok) | manages (ok) | owns (WRONG) | null (WRONG) | manages (ok) | owns (WRONG) |
| 17 | manages | manages (ok) | owns (WRONG) | manages (ok) | manages (ok) | manages (ok) | null (WRONG) | owns (WRONG) | manages (ok) |
| 19 | manages | manages (ok) | owns (WRONG) | manages (ok) | manages (ok) | owns (WRONG) | null (WRONG) | owns (WRONG) | owns (WRONG) |
| 22 | depends_on | depends_on (ok) | manages (STALE) | manages (STALE) | depends_on (ok) | depends_on (ok) | null (WRONG) | manages (STALE) | manages (STALE) |
| 38 | depends_on | depends_on (ok) | owns (WRONG) | manages (STALE) | depends_on (ok) | owns (WRONG) | null (WRONG) | owns (WRONG) | depends_on (ok) |

*Source: metrics.jsonl, query pair `E048::E001`*
