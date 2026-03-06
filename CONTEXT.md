# Context

This project exists because we need an iron-solid proof story that the full OpenClawBrain method beats RAG and other stateful-memory systems in long-lived agent-memory settings.

Key product/research thesis to preserve:
- Query-time must stay fast and local.
- `async_route_fn` produces dense background labels.
- `runtime_route_fn` is the served local policy.
- Human feedback is highest weight; then self-learning; then harvester; then async teacher.
- Policy-gradient updates improve the served routing policy over time.
- Structural graph operations, Hebbian co-firing, and decay are first-class parts of the method.

The benchmark should be impossible to dismiss as a toy retrieval demo.
It should center long-lived memory with drift, contradictions, recurrence, and bounded prompt budget.
