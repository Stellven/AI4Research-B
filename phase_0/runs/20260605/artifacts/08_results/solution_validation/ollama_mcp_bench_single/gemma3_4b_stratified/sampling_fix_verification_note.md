# Verification-Sampling Fix Note

Date: 2026-06-05

## Scope

This artifact records verification of the local fix for the SkillGen
construction-verification sampler. It is solution-validation evidence only; it
is not an original-paper reproduction result.

## Issue Fixed

The previous `gemma3_4b` run produced 5 baseline failures and 35 baseline
successes, but `_build_verification_sample` sampled uniformly from all 40
baseline outcomes. With `sample_size=4` and `seed=42`, the verification sample
contained 0 target failures and 4 success guards. That prevented construction
verification from testing whether a generated skill repaired observed baseline
failures.

## Code Change

`phase_0/runs/skillgen_phase0_thorough_20260602/code/official/pipeline.py`
now builds a stratified verification sample:

- reserve failure-target slots when baseline failures exist;
- fill the remaining sample slots with baseline successes as regression guards;
- if not enough successes exist, use additional failures so the requested sample
  budget is still used when possible.

## Lightweight Verification Completed

The following checks passed on 2026-06-05:

- `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/.venv/bin/python -m py_compile phase_0/runs/skillgen_phase0_thorough_20260602/code/official/pipeline.py`
- `python3 -m unittest tests.test_skillgen_verification_sampling`
- `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/.venv/bin/python -m unittest tests.test_skillgen_verification_sampling`

The regression test constructs the same relevant shape as the failed case:
5 baseline failures, 35 baseline successes, `sample_size=4`, `min_sample=2`,
and `seed=42`. The patched sampler returns 2 target failures and 2 success
guards.

## Full Benchmark Rerun Status

The `gemma3_4b_stratified` benchmark rerun was prepared, including local Ollama
probe artifacts, environment notes, and a config that writes to a separate
result directory. The full rerun was not executed in this session because it
requires localhost Ollama access and should not be started during a short
pack-up window.

The previous `gemma3_4b` benchmark result therefore remains the latest complete
end-to-end run. The fixed sampler has been verified locally, but the full
post-fix SkillGen solution-validation evidence is still pending a rerun.
