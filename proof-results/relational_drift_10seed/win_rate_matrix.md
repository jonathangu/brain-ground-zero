# Win-Rate Matrix (10 seeds)

Cell = number of seeds where row baseline beats column baseline on accuracy.

| baseline | full_brain | graph_route_pg | heuristic_stateful | oracle | route_fn_only | static_graph | vector_rag | vector_rag_rerank |
|---|---|---|---|---|---|---|---|---|
| full_brain | - | 10/10 | 10/10 | 0/10 | 10/10 | 10/10 | 10/10 | 9/10 |
| graph_route_pg | 0/10 | - | 4/10 | 0/10 | 10/10 | 10/10 | 1/10 | 0/10 |
| heuristic_stateful | 0/10 | 6/10 | - | 0/10 | 10/10 | 10/10 | 6/10 | 0/10 |
| oracle | 10/10 | 10/10 | 10/10 | - | 10/10 | 10/10 | 10/10 | 10/10 |
| route_fn_only | 0/10 | 0/10 | 0/10 | 0/10 | - | 10/10 | 0/10 | 0/10 |
| static_graph | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 | - | 0/10 | 0/10 |
| vector_rag | 0/10 | 9/10 | 4/10 | 0/10 | 10/10 | 10/10 | - | 0/10 |
| vector_rag_rerank | 1/10 | 10/10 | 10/10 | 0/10 | 10/10 | 10/10 | 10/10 | - |
