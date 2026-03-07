# Recorded-Session Proof Artifacts

Scored head-to-head results from replaying real OpenClaw session traces against multiple evaluation modes.

## Current status

- `redacted-sample-trace-001/` exists as a **scaffold bundle** only.
- No scored real-session proof bundle is published yet.

## Expected per-session layout

```
recorded_sessions/
  <fixture_id>/
    README.md
    metadata.yaml
    fixture.json
    score_card.json
    score_card.md
    verification/
      fixture_hash.sha256
      README.md
```

## Generate a scaffold bundle

```bash
python3 scripts/init_recorded_session_bundle.py \
  --fixture recorded_sessions/fixtures/<fixture_id>.json
```

## Validate bundle layout

```bash
python3 scripts/validate_recorded_session_bundle.py proof-results/recorded_sessions/<fixture_id>
```

## Promotion criteria for publishable status

1. Required modes scored: `no_brain`, `vector_only`, `graph_prior_only`, `learned_route`
2. Per-turn rows completed in `score_card.json` for each required mode
3. Aggregates populated for each required mode
4. `metadata.yaml` status moved from `scaffold` to `draft`/`publishable`
5. Validation passes: `python3 scripts/validate_recorded_session_bundle.py ...`

## Source pipeline

Trace and fixture generation contracts live in [`recorded_sessions/`](../../recorded_sessions/).
Use [`recorded_session_spec.md`](../../recorded_session_spec.md) for the full evaluation protocol.
