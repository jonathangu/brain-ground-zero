# Worked Example: W004 -> pref_01

Representative seed: `22`

How each baseline answers the same query as the ground-truth relation changes over time.

| step | truth | oracle | full_brain | route_fn_only | graph_route_pg | vector_rag | vector_rag_rerank | heuristic_stateful | static_graph |
|---|---|---|---|---|---|---|---|---|---|
| 8 | email | email (ok) | email (ok) | email (ok) | email (ok) | slack (WRONG) | email (ok) | email (ok) | null (WRONG) |
| 10 | ticket | ticket (ok) | ticket (ok) | ticket (ok) | jira (STALE) | email (WRONG) | jira (STALE) | jira (STALE) | null (WRONG) |
| 17 | email | email (ok) | email (ok) | file (WRONG) | email (ok) | ticket (STALE) | jira (WRONG) | ticket (STALE) | null (WRONG) |
| 20 | jira | jira (ok) | jira (ok) | jira (ok) | jira (ok) | jira (ok) | ticket (WRONG) | email (STALE) | null (WRONG) |
| 21 | jira | jira (ok) | jira (ok) | jira (ok) | ticket (WRONG) | email (STALE) | email (STALE) | email (STALE) | null (WRONG) |
| 26 | jira | jira (ok) | jira (ok) | jira (ok) | slack (WRONG) | slack (WRONG) | email (STALE) | email (STALE) | null (WRONG) |
| 27 | jira | jira (ok) | jira (ok) | calendar (WRONG) | ticket (WRONG) | email (STALE) | jira (ok) | email (STALE) | null (WRONG) |
| 36 | jira | jira (ok) | jira (ok) | ticket (WRONG) | ticket (WRONG) | email (STALE) | email (STALE) | email (STALE) | null (WRONG) |
| 37 | jira | jira (ok) | jira (ok) | calendar (WRONG) | email (STALE) | email (STALE) | email (STALE) | email (STALE) | null (WRONG) |
| 41 | jira | jira (ok) | jira (ok) | slack (WRONG) | jira (ok) | jira (ok) | jira (ok) | email (STALE) | null (WRONG) |
| 42 | jira | jira (ok) | jira (ok) | docs (WRONG) | jira (ok) | slack (WRONG) | email (STALE) | email (STALE) | null (WRONG) |
| 43 | sheet | sheet (ok) | sheet (ok) | sheet (ok) | email (WRONG) | ticket (WRONG) | email (WRONG) | email (WRONG) | null (WRONG) |
| 46 | sheet | sheet (ok) | sheet (ok) | review (WRONG) | ticket (WRONG) | email (WRONG) | jira (STALE) | email (WRONG) | null (WRONG) |
| 51 | sheet | sheet (ok) | sheet (ok) | jira (STALE) | slack (WRONG) | email (WRONG) | email (WRONG) | email (WRONG) | null (WRONG) |
| 52 | sheet | sheet (ok) | sheet (ok) | jira (STALE) | ticket (WRONG) | email (WRONG) | email (WRONG) | email (WRONG) | null (WRONG) |
| 53 | sheet | sheet (ok) | sheet (ok) | docs (WRONG) | jira (STALE) | jira (STALE) | email (WRONG) | email (WRONG) | null (WRONG) |
| 54 | sheet | sheet (ok) | sheet (ok) | email (WRONG) | ticket (WRONG) | sheet (ok) | jira (STALE) | email (WRONG) | null (WRONG) |
| 58 | ticket | ticket (ok) | ticket (ok) | ticket (ok) | jira (WRONG) | ticket (ok) | jira (WRONG) | email (WRONG) | null (WRONG) |
| 59 | ticket | ticket (ok) | ticket (ok) | ticket (ok) | jira (WRONG) | email (WRONG) | ticket (ok) | email (WRONG) | null (WRONG) |

*Source: `metrics.jsonl`, family `recurring_workflows`, query pair `W004::pref_01`*
