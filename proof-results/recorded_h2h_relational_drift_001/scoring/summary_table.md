# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.7875 | 0.4706 | 0.5294 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8962 | 0.9880 | 0.0120 | 0.0000 | 78 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8163 | 0.9796 | 0.0204 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6438 | 0.0456 | 0.9544 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7850 | 0.4012 | 0.4709 | 0.1279 | 80 | 778 | 822 | 800 |
| full_brain | 0.9750 | 0.3500 | 0.6500 | 0.0000 | 20 | 800 | 800 | 800 |
