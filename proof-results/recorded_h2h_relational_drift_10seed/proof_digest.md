# Proof Digest

- Family: `relational_drift`
- Seeds: 10 (11, 22, 33, 44, 55, 66, 77, 88, 99, 111)
- Queries per seed: 800
- Top non-oracle baseline: `full_brain` (99.15%)
- Best RAG baseline: `vector_rag_rerank` (89.44%)
- full_brain margin vs best RAG: +9.71 pp
- Context/query: full_brain 1.00 vs vector_rag_rerank 5.00 (5.00x lower for full_brain)
- full_brain accuracy: 99.15% +/- 0.27%
- full_brain vs vector_rag_rerank head-to-head: 10-0-0
- Ablation chain:
  - route_fn_only: 63.84%
  - graph_route_pg: 75.86% (+12.02 pp vs route_fn_only)
  - full_brain: 99.15% (+23.29 pp vs graph_route_pg)
