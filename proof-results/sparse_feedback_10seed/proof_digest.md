# Proof Digest

- Family: `sparse_feedback`
- Seeds: 10 (11, 22, 33, 44, 55, 66, 77, 88, 99, 111)
- Queries per seed: 1800
- Top non-oracle baseline: `full_brain` (91.96%)
- Best RAG baseline: `vector_rag_rerank` (67.05%)
- full_brain margin vs best RAG: +24.91 pp
- Context/query: full_brain 1.00 vs vector_rag_rerank 5.00 (5.00x lower for full_brain)
- full_brain accuracy: 91.96% +/- 18.30%
- full_brain vs vector_rag_rerank head-to-head: 9-1-0
- Ablation chain:
  - route_fn_only: 37.03%
  - graph_route_pg: 49.39% (+12.36 pp vs route_fn_only)
  - full_brain: 91.96% (+42.56 pp vs graph_route_pg)
