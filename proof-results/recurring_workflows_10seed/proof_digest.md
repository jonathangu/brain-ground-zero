# Proof Digest

- Family: `recurring_workflows`
- Seeds: 10 (11, 22, 33, 44, 55, 66, 77, 88, 99, 111)
- Queries per seed: 3522
- Top non-oracle baseline: `full_brain` (97.57%)
- Best RAG baseline: `vector_rag_rerank` (70.64%)
- full_brain margin vs best RAG: +26.92 pp
- Context/query: full_brain 1.00 vs vector_rag_rerank 5.00 (5.00x lower for full_brain)
- full_brain accuracy: 97.57% +/- 0.37%
- full_brain vs vector_rag_rerank head-to-head: 10-0-0
- Ablation chain:
  - route_fn_only: 34.10%
  - graph_route_pg: 60.39% (+26.29 pp vs route_fn_only)
  - full_brain: 97.57% (+37.17 pp vs graph_route_pg)
