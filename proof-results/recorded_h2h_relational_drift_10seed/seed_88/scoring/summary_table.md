# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.7913 | 0.4551 | 0.5449 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8988 | 0.9753 | 0.0247 | 0.0000 | 72 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8113 | 0.9868 | 0.0132 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6200 | 0.0757 | 0.9243 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7812 | 0.3543 | 0.4514 | 0.1943 | 80 | 766 | 834 | 800 |
| full_brain | 0.9950 | 0.5000 | 0.5000 | 0.0000 | 3 | 800 | 800 | 800 |
