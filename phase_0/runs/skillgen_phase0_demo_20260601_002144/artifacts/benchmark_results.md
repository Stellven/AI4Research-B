# Benchmark Results

Status: `official_code_smoke_completed`

## Scope

This is an official-code AIME smoke validation. It is not a reproduction of the full SkillGen Table 1 claim.

## Construction-Time Verification

- Skill ID: `a700933b-e133-43ed-b41e-d75a2192736b`
- Paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `75.0%`
- Repairs: `2`
- Regressions: `1`
- Net gain: `1`
- Verification passed: `True`
- Training token usage: `56529`

## Held-Out Smoke Evaluation

- Model: `openai/gpt-5.4-nano`
- Paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `-25.0%`
- Repairs: `0`
- Regressions: `1`
- Net gain: `-1`
- Eval token usage: `14118`
