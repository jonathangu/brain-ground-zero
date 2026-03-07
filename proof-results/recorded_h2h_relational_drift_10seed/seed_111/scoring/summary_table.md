# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8200 | 0.6111 | 0.3889 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8912 | 0.8621 | 0.1379 | 0.0000 | 80 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.7800 | 0.9830 | 0.0170 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6575 | 0.0511 | 0.9489 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7000 | 0.3208 | 0.2292 | 0.4500 | 80 | 692 | 908 | 800 |
| full_brain | 0.9862 | 0.3636 | 0.6364 | 0.0000 | 9 | 800 | 800 | 800 |
