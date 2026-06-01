# Benchmark Results

Status: `official_code_smoke_completed_not_reproduced`

## Scope

This is an official-code AIME smoke validation using a reduced subset and reduced config. It is **not** a reproduction of the SkillGen Table 1 claim.

## Official Code

- Repository: `https://github.com/yccm/SkillGen`
- Commit: `3c4537bb12ac287ceb1b5d410b491206089fdcb7`
- Local path: `runs/skillgen_phase0_demo_20260601_002144/code/official`

## Training / Construction-Time Verification

- Train subset: `phase_0/smoke_data/aime_train_n8_seed42.json`
- Skill output: `phase_0/raw_benchmark_outputs/skillgen_aime_smoke/skill_output/2026-06-01_15-32-00`
- Skill ID: `a700933b-e133-43ed-b41e-d75a2192736b`
- Construction paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `75.0%`
- Repairs: `2`
- Regressions: `1`
- Net gain: `+1`
- Verification gate: `passed`
- Training token usage: `56529` total tokens

## Held-Out Smoke Evaluation

- Test subset: `phase_0/smoke_data/aime_test_n4_seed42.json`
- Model: `openai/gpt-5.4-nano`
- Paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `-25.0%`
- Repairs: `0`
- Regressions: `1`
- Net gain: `-1`
- Eval token usage: `14118` total tokens

## Smoke Verdict

`not_reproduced`

On this 4-instance AIME smoke test, the generated skill hurt held-out performance: baseline `50.0%`, skill `25.0%`, net gain `-1`.
