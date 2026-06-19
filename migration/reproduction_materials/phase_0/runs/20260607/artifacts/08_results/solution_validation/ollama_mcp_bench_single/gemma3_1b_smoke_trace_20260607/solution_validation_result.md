# Solution Validation Result: gemma3_1b_smoke_trace_20260607

Date completed: 2026-06-07 13:25:57 EDT -0400

Status: `not_solution_validated`

This is a bounded smoke validation run. It is not paper reproduction.

## What This Validated

This run validated more local solution behavior than the prior offline-only
audit:

- local Ollama routing works for a bounded train/eval smoke command;
- deterministic hash embeddings work in the real command path;
- the generation parser fix handled a local-model schema drift that previously
  crashed on list-valued `dedup_notes`;
- persisted skills now record `source_candidate_id`;
- the verification sampler handles an all-failure training sample by selecting
  target failures;
- eval handles deprecated skills by reporting skill equals baseline with
  `net_gain=0`.

## Attempt 1

The first smoke train attempt failed:

- exit code: `1`
- runtime: `78` seconds
- failure: `AttributeError: 'list' object has no attribute 'strip'`
- cause: local `gemma3:1b` returned `dedup_notes` as a JSON list, while
  `generation.py` assumed a string.

Evidence:

```text
train_attempt1_stdout.txt
train_attempt1_stderr.txt
train_attempt1_command_status.json
```

## Rerun After Fix

The rerun completed:

- train exit code: `0`
- train runtime: `914` seconds
- eval exit code: `0`
- eval runtime: `48` seconds

Training dataset:

```text
../../artifacts/07_configs_and_inputs/smoke_data/mcp_bench_single_train_n4_seed42.json
```

Training result:

- instances: 4
- baseline failures: 4
- baseline successes: 0
- failure clusters: 2
- success clusters: 0
- contrastive pairs: 0

Construction verification:

- target failures: `fruityvice_001`, `medical_calculator_001`
- success guards: none
- baseline accuracy: 0.0%
- skill accuracy: 0.0%
- repair count: 0
- regression count: 0
- net gain: 0
- passed: false

The generated skill was marked `deprecated`.

## Traceability

Candidate id:

```text
d3ee4895-eb51-4ca6-b53f-885c6440af9f
```

Persisted skill id:

```text
d0f2da35-08f1-4bc8-af8a-ed2322c5f402
```

Persisted skill field:

```json
{
  "source_candidate_id": "d3ee4895-eb51-4ca6-b53f-885c6440af9f"
}
```

This closes the prior machine-checkability gap for future runs.

## Held-Out Smoke Eval

Eval dataset:

```text
../../artifacts/07_configs_and_inputs/smoke_data/mcp_bench_single_test_n4_seed42.json
```

Eval result:

- instances: 4
- skill rejected: true
- baseline accuracy: 0.0%
- skill accuracy: 0.0%
- repairs: 0
- regressions: 0
- net gain: 0

Because the skill was deprecated, eval reused baseline for the skill condition.

## Conclusion

This run validates additional infrastructure, robustness, and traceability
solutions. It does not validate generated skill effectiveness. The correct
classification for this smoke target is `not_solution_validated`.
