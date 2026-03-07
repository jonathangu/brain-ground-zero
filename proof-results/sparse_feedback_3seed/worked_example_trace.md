# Worked Example: S000 -> pref_00

How each baseline answers the same query as the ground-truth relation changes over time.

| step | truth | explicit_feedback | full_brain | graph_route_pg | heuristic_stateful | oracle | route_fn_only | static_graph | vector_rag | vector_rag_rerank |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 | jira | yes | jira (ok) | null (WRONG) | calendar (WRONG) | jira (ok) | docs (STALE) | null (WRONG) | docs (STALE) | calendar (WRONG) |
| 10 | jira | yes | jira (ok) | null (WRONG) | jira (ok) | jira (ok) | jira (ok) | null (WRONG) | docs (STALE) | docs (STALE) |
| 11 | calendar | no | calendar (ok) | calendar (ok) | jira (STALE) | calendar (ok) | calendar (ok) | null (WRONG) | docs (WRONG) | calendar (ok) |
| 25 | ticket | no | ticket (ok) | ticket (ok) | jira (WRONG) | ticket (ok) | ticket (ok) | null (WRONG) | ticket (ok) | calendar (STALE) |
| 26 | ticket | no | ticket (ok) | docs (WRONG) | jira (WRONG) | ticket (ok) | ticket (ok) | null (WRONG) | docs (WRONG) | ticket (ok) |
| 27 | ticket | no | ticket (ok) | docs (WRONG) | jira (WRONG) | ticket (ok) | ticket (ok) | null (WRONG) | docs (WRONG) | calendar (STALE) |
| 28 | ticket | no | ticket (ok) | docs (WRONG) | jira (WRONG) | ticket (ok) | docs (WRONG) | null (WRONG) | jira (WRONG) | docs (WRONG) |
| 29 | ticket | no | ticket (ok) | jira (WRONG) | jira (WRONG) | ticket (ok) | jira (WRONG) | null (WRONG) | calendar (STALE) | jira (WRONG) |
| 30 | ticket | no | ticket (ok) | docs (WRONG) | jira (WRONG) | ticket (ok) | ticket (ok) | null (WRONG) | docs (WRONG) | ticket (ok) |
| 31 | ticket | no | ticket (ok) | ticket (ok) | jira (WRONG) | ticket (ok) | slack (WRONG) | null (WRONG) | docs (WRONG) | ticket (ok) |
| 36 | ticket | no | ticket (ok) | null (WRONG) | jira (WRONG) | ticket (ok) | sheet (WRONG) | null (WRONG) | calendar (STALE) | calendar (STALE) |

*Source: metrics.jsonl, family `sparse_feedback`, query pair `S000::pref_00`*
