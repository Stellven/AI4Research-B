# Stratified Sampler Verification

Date: 2026-06-07

## Purpose

Verify the patched SkillGen construction verification sampler:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/pipeline.py
```

The sampler should include observed baseline failures when failures exist, then
fill remaining slots with success guards. This prevents the previous
`gemma3_4b` failure mode where construction verification sampled only success
guards despite known baseline failures.

## Existing Test

```text
tests/test_skillgen_verification_sampling.py
```

Existing coverage recreates the previous failure shape:

- 5 baseline failures
- 35 baseline successes
- `sample_size=4`
- `min_sample=2`
- `seed=42`

Expected result:

- 2 target failures
- 2 success guards

## Added Edge-Case Test

The overnight verification added coverage for a narrower edge case:

- 1 baseline failure
- 10 baseline successes
- `sample_size=4`
- `min_sample=2`
- `seed=42`

Expected result:

- the single failure is included once;
- remaining slots are filled with 3 success guards;
- no duplicate or impossible failure reservation occurs.

## Commands Run

```bash
python3 -m unittest tests.test_skillgen_verification_sampling
```

Result:

```text
Ran 2 tests in 0.003s
OK
```

```bash
python3 -m unittest discover -s tests
```

Result:

```text
Ran 15 tests in 4.123s
OK
```

## Run Evidence

The post-fix `gemma3_4b_stratified` run also exercised the sampler in the real
pipeline:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b_stratified/artifacts/runs/20260606-105511/verification/round_1/verification_summary.json
```

Observed sample:

- target failures: `call_for_papers_001`, `movie_recommender_001`
- success guards: `medical_calculator_001`, `nasa_data_000`

## Status

Status: `validated`

The sampler fix is validated by unit tests and by the real
`gemma3_4b_stratified` pipeline run.
