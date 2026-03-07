# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8275 | 0.4783 | 0.5217 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.9075 | 0.7703 | 0.2297 | 0.0000 | 68 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8125 | 0.9533 | 0.0467 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6150 | 0.0519 | 0.9481 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7963 | 0.3865 | 0.3436 | 0.2699 | 80 | 756 | 844 | 800 |
| full_brain | 0.9912 | 0.1429 | 0.8571 | 0.0000 | 7 | 800 | 800 | 800 |
