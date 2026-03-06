# Benchmark Specification

## Purpose
This benchmark evaluates whether the **full OpenClawBrain (OCB) method** outperforms strong RAG and stateful-memory baselines in long-lived memory settings under bounded context and bounded cost.

**Core thesis elements under test**
- Runtime `route_fn` as the served local policy
- Async teacher feedback
- Background labeling for dense supervision
- Policy-gradient updates to routing
- Structural graph memory
- Hebbian co-firing
- Decay
- Structural edits: connect / split / merge / prune

## Benchmark contract
All systems are evaluated on identical:
- World state
- Task stream
- Context budget
- Teacher budget and correction stream
- Scoring rubric

Baselines must declare what they update online. The benchmark records updates to ensure fairness.

## Families (designed to be supported)
1. **pointer + relation retrieval**
2. **drift + contradiction**
3. **recurring workflows**
4. **sparse feedback / teacher-assisted learning**
5. **memory compaction / structural plasticity**

**Implemented now:** `relational_drift` (drift + contradiction)

## Relational drift family
A long-lived world of entities and relations where relations change over time. The task stream asks for the **current** relation for entity pairs. Systems must adapt to drift, avoid stale recall, and minimize false recall under a bounded context window and teacher budget.

## Key metrics
- **Task success** (accuracy)
- **Stale recall rate** (returns old relation)
- **False recall rate** (returns incorrect non-stale relation)
- **Correction count** (teacher usage)
- **Context used** (retrieval/memory reads proxy)
- **Traversal/latency proxy** (edges or hops)
- **Learning curve over time** (accuracy by step)
- **Ablation table output**

## Fairness rules
- Same world and task stream
- Same context budget
- Same teacher budget when applicable
- Same correction stream
- Same scoring rubric
- Explicit statement of allowed online updates per baseline

