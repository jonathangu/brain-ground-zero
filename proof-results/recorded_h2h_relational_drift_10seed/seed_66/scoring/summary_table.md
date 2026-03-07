# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8225 | 0.4930 | 0.5070 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.9275 | 0.8966 | 0.1034 | 0.0000 | 56 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8300 | 0.9118 | 0.0882 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6700 | 0.0227 | 0.9773 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.8087 | 0.3987 | 0.4052 | 0.1961 | 80 | 770 | 830 | 800 |
| full_brain | 0.9912 | 0.4286 | 0.5714 | 0.0000 | 7 | 800 | 800 | 800 |
