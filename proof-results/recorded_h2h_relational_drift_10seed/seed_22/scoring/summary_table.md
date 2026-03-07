# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8263 | 0.4964 | 0.5036 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8750 | 0.9600 | 0.0400 | 0.0000 | 80 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.7975 | 0.9815 | 0.0185 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6212 | 0.0528 | 0.9472 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7462 | 0.3153 | 0.2857 | 0.3990 | 80 | 719 | 881 | 800 |
| full_brain | 0.9912 | 0.0000 | 1.0000 | 0.0000 | 6 | 800 | 800 | 800 |
