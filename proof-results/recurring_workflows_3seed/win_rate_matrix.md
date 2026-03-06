# Win-Rate Matrix (3 seeds)

Cell = number of seeds where row baseline beats column baseline on accuracy.

| baseline | full_brain | graph_route_pg | heuristic_stateful | oracle | route_fn_only | static_graph | vector_rag | vector_rag_rerank |
|---|---|---|---|---|---|---|---|---|
| full_brain | - | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| graph_route_pg | 0/3 | - | 1/3 | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| heuristic_stateful | 0/3 | 2/3 | - | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| oracle | 3/3 | 3/3 | 3/3 | - | 3/3 | 3/3 | 3/3 | 3/3 |
| route_fn_only | 0/3 | 0/3 | 0/3 | 0/3 | - | 3/3 | 0/3 | 0/3 |
| static_graph | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | - | 0/3 | 0/3 |
| vector_rag | 0/3 | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 | - | 0/3 |
| vector_rag_rerank | 0/3 | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 | 3/3 | - |
