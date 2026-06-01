# SkillGen Phase 0 Preliminary Validation Report

Run ID: `skillgen_phase0_demo_20260601_002144`

## Overall Status

`blocked_for_table1_reproduction_smoke_not_reproduced`

The original Table 1 claim was not reproduced because this run intentionally used a cheapest official-code AIME smoke target rather than the paper's full benchmark suite. The official code did run end to end on the smoke target, but the held-out smoke result did not support a positive SkillGen effect.

## Selected Paper Claim

SkillGen reports average held-out accuracy gains for all eight evaluated base LLMs, with gains ranging from `+3.27` to `+10.08` percentage points and 50/80 benchmark-split-model entries improving.

## Official Code Used

- Repository: `https://github.com/yccm/SkillGen`
- Commit: `3c4537bb12ac287ceb1b5d410b491206089fdcb7`
- Local snapshot: `phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official`

## Cheapest Validation Target

AIME smoke validation was selected because the official README uses AIME in Quick Start, the bundled AIME data is available locally, AIME prompts are short, and AIME grading is deterministic.

This is a recorded deviation from the full paper benchmark:

- train subset: `artifacts/smoke_data/aime_train_n8_seed42.json`
- test subset: `artifacts/smoke_data/aime_test_n4_seed42.json`
- smoke config: `artifacts/skillgen_aime_smoke_config.yaml`

## Execution Summary

### Construction-Time Training / Verification

- Exit code: `0`
- Generated skill ID: `a700933b-e133-43ed-b41e-d75a2192736b`
- Construction paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `75.0%`
- Repairs: `2`
- Regressions: `1`
- Net gain: `+1`
- Verification gate: `passed`
- Token usage: `56529` total tokens

### Held-Out Smoke Evaluation

- Exit code: `0`
- Paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `-25.0` percentage points
- Repairs: `0`
- Regressions: `1`
- Net gain: `-1`
- Token usage: `14118` total tokens

## Verdicts

- Table 1 paper claim: `blocked`
- AIME smoke validation: `not_reproduced`

The smoke result should not be used to reject the paper's Table 1 claim, because it is not the same benchmark setup. It does show that under this cheapest AIME smoke setup, the generated skill regressed on held-out paired evaluation.

## Notable Issues

- A first attempted run failed with `AuthenticationError: Missing Authentication header` because the copied `.env` values had literal wrapper quotes. This was fixed by normalizing `.env`; the failed run is preserved under `artifacts/raw_benchmark_outputs/skillgen_aime_smoke/artifacts/runs/20260601-152909`.
- The README eval example uses flags that do not match the current `eval_skill.py`; the eval command used the actual CLI's `--skill-repo` and `--dataset` flags.
- Full Table 1 reproduction still requires the paper's benchmark rows, larger splits, and additional API spend.
