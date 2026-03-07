# Recorded Session Inputs

This directory contains the real-session input contracts and examples used to build publishable recorded-session proof bundles.

## Contents

- `schema/openclaw_session_trace.schema.json` - normalized OpenClaw trace export contract
- `schema/session_fixture.schema.json` - replay fixture contract (`recorded_session_fixture.v2`)
- `traces/redacted_sample_trace.json` - redacted example trace input
- `fixtures/example_minimal.json` - minimal hand-authored fixture example
- `fixtures/redacted-sample-trace-001.json` - fixture generated from the redacted sample trace

## Pipeline commands

```bash
# 1) Validate input trace export
python3 scripts/validate_openclaw_trace.py recorded_sessions/traces/redacted_sample_trace.json

# 2) Convert trace -> fixture
python3 scripts/convert_openclaw_trace_to_fixture.py \
  --trace recorded_sessions/traces/redacted_sample_trace.json \
  --output recorded_sessions/fixtures/redacted-sample-trace-001.json \
  --fixture-id redacted-sample-trace-001

# 3) Validate fixture (including trace hash)
python3 scripts/validate_fixture.py \
  recorded_sessions/fixtures/redacted-sample-trace-001.json \
  --check-trace-hash

# 4) Initialize proof-results scaffold bundle
python3 scripts/init_recorded_session_bundle.py \
  --fixture recorded_sessions/fixtures/redacted-sample-trace-001.json

# 5) Validate scaffold bundle layout
python3 scripts/validate_recorded_session_bundle.py \
  proof-results/recorded_sessions/redacted-sample-trace-001
```

## Notes

- `--strict-ground-truth` on the converter requires explicit `expected_output` and rubric criteria for every turn.
- `--strip-doc-content` on the converter replaces `content` with `content_sha256` + excerpt.
- Scaffold bundles intentionally contain no scored claims; they are templates for the next replay/scoring step.
