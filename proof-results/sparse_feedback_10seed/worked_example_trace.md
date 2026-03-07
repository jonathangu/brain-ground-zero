# Worked Example: S061 -> pref_00

Representative seed: `111`

How each baseline answers the same query as the ground-truth relation changes over time.

| step | truth | explicit_feedback | oracle | full_brain | heuristic_stateful | vector_rag_rerank | route_fn_only | vector_rag | graph_route_pg | static_graph |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ticket | yes | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | sheet (WRONG) | ticket (ok) | null (WRONG) | null (WRONG) |
| 3 | ticket | no | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | null (WRONG) | null (WRONG) |
| 4 | ticket | no | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | null (WRONG) |
| 5 | ticket | no | ticket (ok) | ticket (ok) | ticket (ok) | ticket (ok) | slack (WRONG) | ticket (ok) | ticket (ok) | null (WRONG) |
| 9 | email | yes | email (ok) | email (ok) | ticket (STALE) | ticket (STALE) | email (ok) | email (ok) | email (ok) | null (WRONG) |
| 22 | jira | no | jira (ok) | jira (ok) | email (STALE) | ticket (WRONG) | jira (ok) | ticket (WRONG) | ticket (WRONG) | null (WRONG) |
| 23 | email | no | email (ok) | email (ok) | email (ok) | email (ok) | jira (STALE) | email (ok) | email (ok) | null (WRONG) |
| 27 | email | no | email (ok) | email (ok) | email (ok) | email (ok) | sheet (WRONG) | jira (STALE) | email (ok) | null (WRONG) |
| 36 | jira | yes | jira (ok) | jira (ok) | jira (ok) | docs (STALE) | jira (ok) | ticket (WRONG) | email (WRONG) | null (WRONG) |
| 37 | jira | yes | jira (ok) | jira (ok) | jira (ok) | jira (ok) | jira (ok) | email (WRONG) | email (WRONG) | null (WRONG) |

*Source: `metrics.jsonl`, family `sparse_feedback`, query pair `S061::pref_00`*
