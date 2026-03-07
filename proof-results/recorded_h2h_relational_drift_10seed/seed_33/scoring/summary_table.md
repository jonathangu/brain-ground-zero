# Summary Table

| baseline | accuracy | stale_rate | false_rate | unknown_rate | corrections_delivered | context_used | traversal_cost | total_queries |
|---|---|---|---|---|---|---|---|---|
| oracle | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 800 | 800 | 800 |
| vector_rag | 0.8263 | 0.5108 | 0.4892 | 0.0000 | 80 | 800 | 800 | 800 |
| vector_rag_rerank | 0.8825 | 0.9787 | 0.0213 | 0.0000 | 80 | 4000 | 6400 | 800 |
| heuristic_stateful | 0.8175 | 0.9932 | 0.0068 | 0.0000 | 80 | 800 | 800 | 800 |
| static_graph | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 80 | 0 | 1600 | 800 |
| route_fn_only | 0.6775 | 0.0310 | 0.9690 | 0.0000 | 80 | 800 | 800 | 800 |
| graph_route_pg | 0.7200 | 0.2188 | 0.2143 | 0.5670 | 80 | 673 | 927 | 800 |
| full_brain | 0.9950 | 0.5000 | 0.5000 | 0.0000 | 3 | 800 | 800 | 800 |
