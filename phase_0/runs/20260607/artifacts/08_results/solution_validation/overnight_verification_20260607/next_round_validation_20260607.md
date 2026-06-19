# Next Round Validation: 2026-06-07

Date: 2026-06-07 13:25:57 EDT -0400

## Summary

Additional solutions were validated after the first overnight audit:

- local OpenAI-compatible routing now has an offline unit test;
- candidate-to-persisted-skill traceability now has a code fix and test;
- generation is hardened against non-string JSON fields returned by local
  models;
- a bounded local `gemma3:1b` train/eval smoke run completed and produced
  durable artifacts.

Generated skill effectiveness remains not validated.

## New Tests

Added:

```text
tests/test_skillgen_local_routing_and_traceability.py
tests/test_skillgen_generation_robustness.py
```

Full suite:

```text
python3 -m unittest discover -s tests
Ran 18 tests in 3.854s
OK
```

## Code Changes Validated

### Local Routing Test

The routing test proves that with `SKILLGEN_LOCAL_OPENAI_COMPAT=1`, `chat()`
uses the local OpenAI-compatible client, uses `SKILLGEN_LOCAL_MODEL`, passes
`SKILLGEN_LOCAL_NUM_CTX`, and does not require external OpenAI/OpenRouter API
keys even when `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1`.

### Source Candidate Traceability

`SkillItem` now includes:

```text
source_candidate_id
```

`candidate_to_skill(...)` sets it from `CandidateSkill.candidate_id`.

The smoke run confirmed this in a persisted skill:

```json
{
  "candidate_id": "d3ee4895-eb51-4ca6-b53f-885c6440af9f",
  "skill_id": "d0f2da35-08f1-4bc8-af8a-ed2322c5f402",
  "source_candidate_id": "d3ee4895-eb51-4ca6-b53f-885c6440af9f"
}
```

### Generation Robustness

The first `gemma3:1b` smoke attempt failed because local model output returned
`dedup_notes` as a list and `generation.py` assumed string fields. The patch
adds deterministic text coercion for list, dict, scalar, and string JSON
fields used in generation/refinement prompts.

The rerun completed after this patch.

## Smoke Run

Result directory:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_1b_smoke_trace_20260607
```

Status:

```text
not_solution_validated
```

Important files:

```text
parsed_metrics.json
solution_validation_result.md
solution_validation_result.json
trace_inventory.md
train_command_status.json
eval_command_status.json
eval_results.json
```

Train:

- exit code: 0
- runtime: 914 seconds
- baseline failures: 4
- baseline successes: 0
- construction sample: 2 target failures, 0 success guards
- construction net gain: 0
- skill status: deprecated

Eval:

- exit code: 0
- runtime: 48 seconds
- baseline accuracy: 0.0%
- skill accuracy: 0.0%
- net gain: 0
- skill condition skipped because skill was deprecated

## Updated Validation Status

Newly validated:

- local routing behavior at unit-test level;
- source candidate id persistence at unit-test and real-run level;
- generation robustness against list/dict JSON field drift;
- all-failure sampler case in real smoke run;
- deprecated-skill eval handling in real smoke eval.

Still not validated:

- generated skill effectiveness.

Minimum remaining work:

- run a stronger bounded confirmation where baseline has both failures and
  successes, construction verification repairs at least one failure, and
  held-out eval contains repair opportunity with positive net gain.
