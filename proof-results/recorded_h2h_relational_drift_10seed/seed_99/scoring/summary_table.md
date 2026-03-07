# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8500 | 0.6250 | 0.3750 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.9100 | 0.9861 | 0.0139 | 0.0000 | 65 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8200 | 0.9861 | 0.0139 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6238 | 0.0797 | 0.9203 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7812 | 0.3486 | 0.1886 | 0.4629 | 80 | 719 | 881 | 800 |
| full_brain | 0.9875 | 0.3000 | 0.7000 | 0.0000 | 8 | 800 | 800 | 800 |
