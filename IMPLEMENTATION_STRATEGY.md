# Implementation Strategy

## This benchmark validates the mechanism. The architecture proposal describes the production system.

**Architecture proposal:** [openclawbrain/docs/architecture-proposal-openclawbrain-vnext.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/architecture-proposal-openclawbrain-vnext.md)

## How the benchmark maps to the real design

| Benchmark concept | Production equivalent |
|---|---|
| `full_brain` baseline | The complete OCB system with all subsystems active |
| `runtime_route_fn` | The served local routing policy (`runtime_route_fn`) |
| Policy-gradient updates | Online PG updates to improve routing over time |
| Structural graph memory | The core graph store with Hebbian co-firing, decay, and structural edits |
| Background labeling | `async_route_fn` producing dense labels offline |
| Correction stream | Human feedback (highest weight), self-learning, harvester, async teacher |
| Context budget | Bounded prompt window -- the system must route efficiently, not dump everything |

## What the benchmark tests directly

The benchmark's `relational_drift` family tests the ingredients that matter most for long-lived agent memory:

- **Drift tracking**: Entity relations change over time. The system must notice and update.
- **Contradiction handling**: Old facts become stale. The system must not serve stale data.
- **Bounded context**: Systems can't just stuff everything into the prompt.
- **Online learning**: The system receives corrections and must improve its routing.
- **Structural plasticity**: Connect, split, merge, prune -- the graph reorganizes itself.

## What comes next

The harness supports additional benchmark families (designed but not yet run):
1. Recurring workflows -- can the system learn and accelerate repeated patterns?
2. Sparse feedback -- does the async teacher fill in gaps when human feedback is rare?
3. Memory compaction -- can structural edits keep the graph efficient as it grows?

These will extend the proof story from "the mechanism works on drift" to "the mechanism works across the full problem space."
