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

**Implemented now:** `relational_drift`, `recurring_workflows`, `sparse_feedback`

## Relational drift family
A long-lived world of entities and relations where relations change over time. The task stream asks for the **current** relation for entity pairs. Systems must adapt to drift, avoid stale recall, and minimize false recall under a bounded context window and teacher budget.

## Recurring workflows family
A world of workflow templates that recur over time. Each workflow has multiple **step slots** plus **preference slots** (e.g., channel or template). The task stream repeatedly “runs” workflows: queries ask for the **current action or preference** for each slot. Workflows are revised over time (steps and preferences change, sometimes reverting to older variants), and runs are drawn with a **recency bias** to simulate long-lived repeated tasks. The system must keep the latest workflow variant while avoiding stale recall under bounded context.

Key parameters:
- `num_workflows`, `steps_per_workflow`, `prefs_per_workflow`
- `action_types`, `preference_types`
- `workflows_per_step`, `query_steps_per_workflow`, `query_prefs_per_workflow`
- `workflow_updates_per_step`, `step_updates_per_workflow`, `pref_updates_per_workflow`
- `recurrence_bias`, `recent_window`, `update_query_ratio`, `contradiction_rate`

## Sparse feedback family
A recurring-workflow world with bursty revisions, but where only a small subset of queries receives explicit feedback. Each step emits a per-query `feedback_mask`; only masked queries can drive policy-gradient updates and teacher-correction scheduling. This stresses the intended mechanism:
- learned hot-path routing under limited supervision
- async teacher corrections delayed and budgeted
- full-brain background labels amplifying sparse corrections into denser offline signal

Key parameters:
- all recurring-workflow controls above
- `revision_burst_rate`, `burst_extra_step_updates`, `burst_extra_pref_updates`
- `explicit_feedback_rate`, `focused_feedback_rate`, `feedback_focus_recent_steps`
- `min_feedback_per_step`

## Key metrics
- **Task success** (accuracy)
- **Stale recall rate** (returns old relation)
- **False recall rate** (returns incorrect non-stale relation)
- **Correction count** (teacher usage)
- **Feedback coverage** (`feedback_events`, `feedback_rate`)
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

## Recorded-session head-to-head (next proof rung)

The simulation families above prove the mechanism in isolation.
The **recorded-session head-to-head** evaluation replays real OpenClaw
session traces against ablated baselines to prove the mechanism transfers
to real product data.

- **Spec:** [`recorded_session_spec.md`](recorded_session_spec.md)
- **Fixture schema:** [`recorded_sessions/schema/session_fixture.schema.json`](recorded_sessions/schema/session_fixture.schema.json)
- **Example fixture:** [`recorded_sessions/fixtures/example_minimal.json`](recorded_sessions/fixtures/example_minimal.json)
- **Validation:** `python scripts/validate_fixture.py --all`
- **Results (placeholder):** [`proof-results/recorded_sessions/`](proof-results/recorded_sessions/)

Required evaluation modes: `no_brain`, `vector_only`, `graph_prior_only`, `learned_route`.
Optional: `full_brain`, `online`. See the spec for full details.
