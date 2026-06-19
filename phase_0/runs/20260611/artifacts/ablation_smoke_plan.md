# Ablation Smoke Plan

Smoke execution plan for reconstructed SkillGen Figure 3 ablation arms

Status: `ready_for_reconstructed_ablation_execution`
Approval required before execution: `True`

## Recommended Target

- Target: `skillgen_aime_smoke`
- Train: `artifacts/smoke_data/aime_train_n8_seed42.json`
- Test: `artifacts/smoke_data/aime_test_n4_seed42.json`
- Model: `openai/gpt-5.4-nano`
- Judge: `openai/gpt-5.4-mini`

## Arm Sequence

- `Full`
- `A1`
- `A2`
- `A3`
- `A4`
- `A5`

## Preflight Checks

- Write one config/patch/deviation artifact per arm before execution.
- Verify A1 demonstration ids come only from construction successes.
- Verify A3 gate override is scoped only to A3 and records original gate result.
- Verify A4 records whether prompt-level or fallback post-process ablation was used.
- Verify A5 Full comparison is meaningful only when Full has scripts/references enabled.
