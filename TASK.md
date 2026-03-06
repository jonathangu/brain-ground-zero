# TASK — Brain-vs-RAG Ground-Zero Benchmark

This project must stay **outside** the `openclawbrain` repo.

## Mission
Build a publication-grade benchmark harness and spec that can prove or falsify the full OpenClawBrain thesis against strong RAG and stateful-memory baselines.

We are **not** trying to prove "graph > vector" in isolation.
We are trying to test whether the **full strategy** wins in long-lived agent-memory environments under bounded context and bounded cost.

## The method under test
The benchmark must support evaluating these ingredients directly:
- learned runtime `route_fn`
- background labeling
- async teacher
- policy-gradient updates
- structural graph memory
- Hebbian co-firing
- decay
- structural edits: connect / split / merge / prune

## Deliverables
Create a clean standalone project with at least:
- `README.md`
- `benchmark_spec.md`
- `world_schema.md`
- `task_schema.md`
- `baseline_matrix.md`
- `scoring.md`
- `execution_plan.md`
- `milestones.md`
- runnable Python harness skeleton
- config files for benchmark families and baselines
- one implemented benchmark family: `relational_drift`
- plotting/report script(s)
- smoke tests or validation scripts

## Required benchmark families
Design the harness to support at least these families:
1. pointer + relation retrieval
2. drift + contradiction
3. recurring workflows
4. sparse feedback / teacher-assisted learning
5. memory compaction / structural plasticity

Implement the first family now as the initial concrete benchmark: **relational drift**.

## Required systems/baselines
- oracle / ceiling
- plain vector RAG
- vector RAG + rerank
- heuristic stateful memory
- static graph traversal
- learned `route_fn` only
- graph + learned `route_fn` + PG, but without structural plasticity
- full brain

## Fairness rules
Keep the benchmark honest:
- same world state
- same task stream
- same context budget
- same teacher budget when applicable
- same correction stream
- same scoring rubric
- explicit statement of what each baseline may update online

## Key metrics
- task success
- stale recall rate
- false recall rate
- correction count
- context used
- traversal/latency proxy
- learning curve over time
- ablation table output

## Project shape
Preferred stack: Python + JSON/YAML configs + simple plotting.
Make it easy to reproduce and publish.
Do **not** put anything in the `openclawbrain` repo.

## Working style
- Commit early and often.
- Keep docs and code aligned in the same commits.
- Build the benchmark contract first, then the harness, then the first family.
- Do not deploy anything.

## Completion criterion
When this initial push is done, the repo should let us:
1. understand the benchmark contract,
2. run the first family end-to-end,
3. compare baseline outputs in a reproducible way,
4. generate at least one report/figure/table artifact.

## Notify on completion
When completely finished, run this command:
openclaw system event --text "Done: built the standalone brain-vs-RAG ground-zero benchmark scaffold with relational-drift family, docs, harness, configs, and reporting" --mode now
