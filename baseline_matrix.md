# Baseline Matrix

All baselines share the same world, task stream, context budget, and teacher budget. Each baseline declares what it may update online.

| Baseline | route_fn | async teacher | background labels | PG updates | graph memory | structural edits | Online updates allowed |
|---|---|---|---|---|---|---|---|
| Oracle / Ceiling | n/a | n/a | n/a | n/a | n/a | n/a | none (perfect answers) |
| Plain Vector RAG | no | optional | no | no | no | no | vector index updates from observations |
| Vector RAG + Rerank | no | optional | no | no | no | no | vector index updates from observations |
| Heuristic Stateful Memory | no | optional | no | no | no | no | key-value state updates from observations |
| Static Graph Traversal | no | optional | no | no | yes (static) | no | none after init |
| Learned route_fn only | yes | optional | no | yes | no | no | route_fn weights only |
| Graph + route_fn + PG (no structure) | yes | optional | no | yes | yes (static) | no | route_fn weights only |
| Full Brain | yes | yes | yes | yes | yes | yes | route_fn + graph structure + weights + decay |

Notes:
- "Optional" teacher indicates the baseline can use teacher corrections if enabled in the run config.
- Structural edits include connect/split/merge/prune.

