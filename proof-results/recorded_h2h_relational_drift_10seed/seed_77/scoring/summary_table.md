# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.7688 | 0.5622 | 0.4378 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8712 | 0.9223 | 0.0777 | 0.0000 | 80 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.7850 | 0.9826 | 0.0174 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6188 | 0.0459 | 0.9541 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.6987 | 0.3568 | 0.3278 | 0.3154 | 80 | 724 | 876 | 800 |
| full_brain | 0.9938 | 0.0000 | 1.0000 | 0.0000 | 5 | 800 | 800 | 800 |
