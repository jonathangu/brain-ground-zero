# Share Message

Copy/paste the version that fits:

---

## Short version

I built a benchmark proving the OpenClawBrain memory architecture beats RAG. Full-brain method hits 97.2% accuracy on relational drift (entity facts that change over time), vs 89% for the best RAG baseline -- and uses 5x less context. Wins 10/10 seeds against every baseline except one (9/10). The full results, harness code, and reproduction instructions are all in the repo:

https://github.com/jonathangu/brain-ground-zero

---

## Longer version

Been working on proving out the OpenClawBrain thesis -- that a structural graph memory with learned routing, policy-gradient updates, and online plasticity (Hebbian co-firing, decay, structural edits) beats RAG for long-lived agent memory.

Built a standalone benchmark harness and ran the first family: relational drift (entity-relation pairs that change over time, 50 entities, 800 queries, 10 random seeds, 8 baselines from oracle ceiling down to plain vector RAG).

Results:
- full_brain: 97.2% accuracy (+/- 5.8)
- best RAG (vector_rag_rerank): 89.0% (+/- 2.3) -- but uses 5x more context
- plain vector RAG: 79.7%
- graph+route+PG without structural plasticity: 76.5%

The ablation tells a clean story: each layer adds value, and structural plasticity is the single biggest contributor (+20.8 pp). Win-rate matrix shows the full brain wins 9/10 or 10/10 seeds against every non-oracle baseline.

This is the first benchmark family (mechanism proof on drift). More families are designed (recurring workflows, sparse feedback, memory compaction). Repo has the full harness, configs, reproduction commands, and tracked proof artifacts:

https://github.com/jonathangu/brain-ground-zero

Architecture proposal for the production system: https://github.com/jonathangu/openclawbrain/blob/main/docs/architecture-proposal-openclawbrain-vnext.md
