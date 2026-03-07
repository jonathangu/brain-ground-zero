# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8213 | 0.5035 | 0.4965 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8800 | 0.8438 | 0.1562 | 0.0000 | 80 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8175 | 0.9932 | 0.0068 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6350 | 0.0411 | 0.9589 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7913 | 0.3413 | 0.4611 | 0.1976 | 80 | 767 | 833 | 800 |
| full_brain | 0.9912 | 0.1429 | 0.8571 | 0.0000 | 7 | 800 | 800 | 800 |
