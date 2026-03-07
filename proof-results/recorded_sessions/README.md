# Recorded-Session Proof Artifacts

Scored head-to-head results from replaying real OpenClaw session traces
against multiple evaluation modes.

## Status

**No results yet.** This directory is the target for artifacts produced by
the recorded-session evaluation workflow described in
[`recorded_session_spec.md`](../../recorded_session_spec.md).

## Expected layout

```
recorded_sessions/
  <fixture_id>/
    score_card.json     # per-turn scores for every mode
    score_card.md       # human-readable summary
    fixture.json        # copy of the input fixture
  batch_<batch_id>/
    summary_table.csv   # per-mode aggregates
    summary_table.md
    pairwise_delta.csv  # mode-vs-mode deltas
    win_rate_matrix.csv
    win_rate_matrix.md
```

## How to contribute results

1. Create or obtain a session fixture (see `recorded_sessions/fixtures/`).
2. Validate it: `python scripts/validate_fixture.py <fixture.json>`
3. Replay through each evaluation mode and collect scores.
4. Place artifacts here following the layout above.
5. Update `CLAIMS.md` with the new proof scope.
