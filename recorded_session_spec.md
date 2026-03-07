# Recorded-Session Head-to-Head Evaluation Spec

## Purpose

Evaluate OpenClawBrain (OCB) routing and memory against ablated baselines
on **real product traces** captured from live OpenClaw sessions.

This is the next proof rung beyond simulation.
Simulations (relational_drift, recurring_workflows) prove the **mechanism**.
Recorded-session head-to-head proves the mechanism **transfers to real product data**.

### Proof boundary

- **In scope:** Given a fixed, recorded session trace, replay it against each
  evaluation mode and compare scored outputs.
- **Out of scope:** Live/online evaluation, production latency SLAs, user-facing
  A/B tests. These are future rungs.

## Required inputs

Each evaluation takes a **session fixture** -- a self-contained JSON file
containing everything needed to replay one session deterministically.

### Fixture format

See [`recorded_sessions/schema/session_fixture.schema.json`](recorded_sessions/schema/session_fixture.schema.json)
for the machine-readable fixture schema.
The normalized OpenClaw trace input schema is
[`recorded_sessions/schema/openclaw_session_trace.schema.json`](recorded_sessions/schema/openclaw_session_trace.schema.json).

Examples:
- manual fixture example: [`recorded_sessions/fixtures/example_minimal.json`](recorded_sessions/fixtures/example_minimal.json)
- redacted trace example: [`recorded_sessions/traces/redacted_sample_trace.json`](recorded_sessions/traces/redacted_sample_trace.json)
- converted fixture example: [`recorded_sessions/fixtures/redacted-sample-trace-001.json`](recorded_sessions/fixtures/redacted-sample-trace-001.json)

A fixture contains:

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Fixture schema contract version (`recorded_session_fixture.v2`) |
| `fixture_id` | string | Unique identifier for this fixture |
| `source` | object | Provenance: product version, trace ID, export format, capture date, trace hash |
| `session_context` | object | Initial state: matter type, workspace config, user role |
| `turns` | array | Ordered list of session turns (see below) |
| `ground_truth` | object | Session-level labeling metadata and review status |
| `held_fixed` | object | What must not vary across modes (see Fairness Rules) |
| `redaction` | object | PII handling declaration |
| `conversion` | object | Converter metadata (tool/version/time/command) |

Each **turn** contains:

| Field | Type | Description |
|---|---|---|
| `turn_id` | int | 0-indexed position in the session |
| `user_input` | string | The user's query or action |
| `available_documents` | array | Document IDs / chunks available at this point |
| `graph_snapshot` | object or null | Graph state at turn start (null for no_brain) |
| `expected_output` | string | Ground-truth ideal response |
| `rubric` | object | Per-turn scoring fields, including ground-truth source |
| `trace_ref` | object | Provenance link back to original trace turn/event IDs |

## Evaluation modes

### Required modes (must be present in every head-to-head)

| Mode | Description | What it uses |
|---|---|---|
| `no_brain` | Baseline: raw retrieval, no graph, no route_fn | Vector search only, no memory layer |
| `vector_only` | Vector RAG with reranking, no graph memory | Vector index + reranker |
| `graph_prior_only` | Graph memory provides prior, but no learned routing | Static graph traversal, no route_fn updates |
| `learned_route` | Full route_fn with policy-gradient updates, graph memory | Graph + route_fn + PG, no structural plasticity |

### Optional modes (clearly separated, not required for core proof)

| Mode | Description | What it adds |
|---|---|---|
| `full_brain` | Complete OCB with structural plasticity | Adds Hebbian co-firing, decay, connect/split/merge/prune |
| `online` | Live model calls instead of recorded outputs | Measures actual LLM latency and cost; requires API access |

Optional modes are reported in separate columns/sections and never mixed into
the core head-to-head comparison unless all fairness rules are met.

## Scoring rubric

Every turn produces a **score row** with these fields:

| Field | Type | Description |
|---|---|---|
| `success` | bool | Did the output match expected_output (exact or rubric-pass)? |
| `rubric_score` | float 0-1 | Graded quality score (1.0 = perfect, 0.0 = wrong) |
| `corrections_needed` | int | Number of teacher/user corrections required |
| `prompt_context_size` | int | Tokens of context injected into the prompt |
| `latency_proxy` | float | Milliseconds (recorded) or graph-hops (simulated) |
| `cost_proxy` | float | Estimated API cost in USD (0.0 if not applicable) |
| `notes` | string | Free-text annotation (e.g., "stale recall", "hallucination") |

### Session-level aggregates

- **accuracy**: fraction of turns where `success == true`
- **mean_rubric_score**: mean of `rubric_score` across turns
- **total_corrections**: sum of `corrections_needed`
- **mean_context_size**: mean of `prompt_context_size`
- **mean_latency_proxy**: mean of `latency_proxy`
- **total_cost_proxy**: sum of `cost_proxy`

### Batch-level aggregates (across sessions)

- Per-mode mean and std of each session-level aggregate
- Pairwise delta table (mode A - mode B) for accuracy and rubric_score
- Win-rate matrix (which mode wins per session)

## Artifact outputs

### Per session

Published to `proof-results/recorded_sessions/<fixture_id>/`:

| Artifact | Format | Description |
|---|---|---|
| `metadata.yaml` | YAML | Bundle metadata (`status`, `fixture_sha256`, required modes) |
| `score_card.json` | JSON | Full per-turn scores for every mode |
| `score_card.md` | Markdown | Human-readable summary table |
| `fixture.json` | JSON | Copy of the input fixture (for reproducibility) |
| `verification/fixture_hash.sha256` | text | Fixture integrity hash |

### Per batch

Published to `proof-results/recorded_sessions/batch_<batch_id>/`:

| Artifact | Format | Description |
|---|---|---|
| `summary_table.csv` | CSV | Per-mode aggregates across all sessions |
| `summary_table.md` | Markdown | Same, human-readable |
| `pairwise_delta.csv` | CSV | Mode-vs-mode accuracy/rubric deltas |
| `win_rate_matrix.csv` | CSV | Per-session win counts |
| `win_rate_matrix.md` | Markdown | Same, human-readable |

## Fairness rules

The following must be **held fixed** across all evaluation modes within a
single head-to-head comparison:

1. **Session fixture**: identical `turns`, `available_documents`, and
   `session_context` for every mode.
2. **Prompt template**: same system prompt and user-turn formatting.
3. **Document corpus**: same set of retrievable chunks at each turn.
4. **Teacher/correction budget**: same maximum corrections allowed.
5. **Context budget**: same maximum prompt-context token limit.
6. **Scoring rubric**: same rubric applied identically to all outputs.
7. **Random seeds**: any stochastic components use the same seed.

The fixture's `held_fixed` object records the concrete values of items 2-5
so reviewers can verify compliance.

## Operator workflow

Minimal path from a real product session to a scored, publishable artifact:

```
Step 1: Capture
  - Record a live OpenClaw session (or export from session logs).
  - Anonymize PII (tenant name, user details, document contents if needed).
  - Save normalized trace JSON under recorded_sessions/traces/.
  - Validate trace:
      python scripts/validate_openclaw_trace.py recorded_sessions/traces/<trace>.json

Step 2: Convert to fixture
  - Convert trace to fixture:
      python scripts/convert_openclaw_trace_to_fixture.py \
        --trace recorded_sessions/traces/<trace>.json \
        --output recorded_sessions/fixtures/<fixture>.json
  - Validate fixture (including trace hash check):
      python scripts/validate_fixture.py \
        recorded_sessions/fixtures/<fixture>.json \
        --check-trace-hash
  - Fix any schema violations.

Step 3: Replay and score
  - For each required mode, replay the fixture through the mode's pipeline.
  - Collect per-turn score rows.
  - Initialize publishable scaffold bundle:
      python scripts/init_recorded_session_bundle.py \
        --fixture recorded_sessions/fixtures/<fixture>.json

Step 4: Generate artifacts
  - Fill score_card.json and score_card.md per session.
  - If running a batch, generate batch-level summary/delta/win-rate artifacts.
  - Validate bundle:
      python scripts/validate_recorded_session_bundle.py \
        proof-results/recorded_sessions/<fixture_id>/

Step 5: Review and publish
  - Review score cards for correctness.
  - Commit artifacts to proof-results/recorded_sessions/.
  - Update CLAIMS.md with new proof scope.
```

### Checklist for a valid head-to-head

- [ ] Fixture passes schema validation
- [ ] All required modes (no_brain, vector_only, graph_prior_only, learned_route) are scored
- [ ] Fairness rules verified (held_fixed values match across modes)
- [ ] Score card includes all rubric fields for every turn
- [ ] Artifacts committed to proof-results/recorded_sessions/
- [ ] CLAIMS.md updated to reflect new proof scope
