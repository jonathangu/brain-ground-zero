# Scoring

## Metrics

### Task success (accuracy)
`accuracy = correct / total`

### Stale recall rate
Fraction of incorrect answers that match the *previous* relation for the pair.

`stale_rate = stale_incorrect / incorrect`

### False recall rate
Incorrect answers that are neither stale nor unknown.

`false_rate = false_incorrect / incorrect`

### Correction count
Number of teacher corrections delivered (bounded by teacher budget).

### Feedback coverage
Number/fraction of queries with explicit feedback available.

`feedback_rate = feedback_events / total_queries`

### Context used
Total number of memory items retrieved or read (proxy for prompt/context usage).

### Traversal/latency proxy
Total graph hops, vector search ops, or lookup ops (baseline-specific proxy).

### Learning curve
Accuracy by step (time-series).

## Aggregate score (optional)
The harness reports raw metrics; composite scores are **not** imposed by default. A suggested composite (for ablation tables only):

```
score = accuracy
      - 0.2 * stale_rate
      - 0.1 * false_rate
      - 0.05 * (corrections / total_queries)
      - 0.0001 * context_used
```

Composite weights are explicitly documented when used.
