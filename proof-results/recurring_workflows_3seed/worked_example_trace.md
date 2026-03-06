# Worked Example: W042 -> step_05

How each baseline answers the same query as the ground-truth relation changes over time.

| step | truth | full_brain | graph_route_pg | heuristic_stateful | oracle | route_fn_only | static_graph | vector_rag | vector_rag_rerank |
|---|---|---|---|---|---|---|---|---|---|
| 1 | send | send (ok) | null (WRONG) | send (ok) | send (ok) | email (WRONG) | null (WRONG) | send (ok) | send (ok) |
| 2 | send | send (ok) | send (ok) | send (ok) | send (ok) | draft (WRONG) | null (WRONG) | send (ok) | send (ok) |
| 10 | send | send (ok) | send (ok) | send (ok) | send (ok) | reconcile (WRONG) | null (WRONG) | send (ok) | send (ok) |
| 20 | send | send (ok) | send (ok) | send (ok) | send (ok) | notify (WRONG) | null (WRONG) | send (ok) | send (ok) |
| 21 | send | send (ok) | send (ok) | send (ok) | send (ok) | file (WRONG) | null (WRONG) | send (ok) | send (ok) |
| 25 | send | send (ok) | send (ok) | send (ok) | send (ok) | email (WRONG) | null (WRONG) | send (ok) | send (ok) |
| 26 | send | send (ok) | send (ok) | send (ok) | send (ok) | send (ok) | null (WRONG) | send (ok) | send (ok) |
| 27 | file | file (ok) | file (ok) | send (STALE) | file (ok) | file (ok) | null (WRONG) | file (ok) | file (ok) |
| 30 | file | file (ok) | send (STALE) | send (STALE) | file (ok) | file (ok) | null (WRONG) | file (ok) | file (ok) |
| 31 | draft | draft (ok) | send (WRONG) | send (WRONG) | draft (ok) | draft (ok) | null (WRONG) | send (WRONG) | send (WRONG) |
| 34 | file | file (ok) | file (ok) | file (ok) | file (ok) | draft (STALE) | null (WRONG) | file (ok) | draft (STALE) |

*Source: metrics.jsonl, family `recurring_workflows`, query pair `W042::step_05`*
