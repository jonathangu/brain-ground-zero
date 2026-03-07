# Worked Example: E053 -> E043

Representative seed: `77`

How each baseline answers the same query as the ground-truth relation changes over time.

| step | truth | explicit_feedback | oracle | full_brain | route_fn_only | heuristic_stateful | vector_rag_rerank | graph_route_pg | static_graph | vector_rag |
|---|---|---|---|---|---|---|---|---|---|---|
| 21 | owns | yes | owns (ok) | owns (ok) | depends_on (WRONG) | owns (ok) | owns (ok) | depends_on (WRONG) | null (WRONG) | depends_on (WRONG) |
| 22 | manages | yes | manages (ok) | manages (ok) | manages (ok) | owns (STALE) | owns (STALE) | owns (STALE) | null (WRONG) | depends_on (WRONG) |
| 31 | reports_to | yes | reports_to (ok) | reports_to (ok) | reports_to (ok) | owns (WRONG) | manages (STALE) | depends_on (WRONG) | null (WRONG) | depends_on (WRONG) |

*Source: `metrics.jsonl`, family `relational_drift`, query pair `E053::E043`*
