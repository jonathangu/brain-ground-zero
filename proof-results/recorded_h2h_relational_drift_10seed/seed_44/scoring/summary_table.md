# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8512 | 0.6387 | 0.3613 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.9000 | 0.9000 | 0.1000 | 0.0000 | 78 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8150 | 0.9932 | 0.0068 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6450 | 0.0423 | 0.9577 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7625 | 0.3895 | 0.2105 | 0.4000 | 80 | 724 | 876 | 800 |
| full_brain | 0.9925 | 0.3333 | 0.6667 | 0.0000 | 5 | 800 | 800 | 800 |
