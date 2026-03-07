# Task Schema

A task stream is a sequence of steps. Each step has updates, queries, and optional corrections delivered by the teacher.

## Step
```json
{
  "step": 12,
  "updates": [
    {"subject": "E42", "object": "E07", "relation": "reports_to", "time": 12, "source": "update"}
  ],
  "queries": [
    {"subject": "E42", "object": "E07"}
  ],
  "answers": [
    {"relation": "reports_to"}
  ],
  "feedback_mask": [true],
  "corrections": [
    {"subject": "E42", "object": "E07", "relation": "reports_to", "time": 12, "source": "teacher"}
  ]
}
```

## Query
A query asks for the **current** relation for a subject-object pair.

```json
{"subject": "E42", "object": "E07"}
```

## Answer
```json
{"relation": "reports_to"}
```

## Correction
Teacher feedback is delivered asynchronously and may be delayed.

```json
{"subject": "E42", "object": "E07", "relation": "reports_to", "time": 12, "source": "teacher"}
```

## Feedback mask
Optional per-query mask for explicit supervision availability.
If absent, all queries are treated as feedback-eligible.

```json
[true, false, false, true]
```
