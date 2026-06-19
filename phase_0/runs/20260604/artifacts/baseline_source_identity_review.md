# Baseline Source Identity Review

Group D baseline source identity review for SkillGen Figure 2 reconstruction

Status: `ready_for_reconstructed_baseline_comparison`
Storage rule: All baseline repositories must be cloned under code/official/baselines inside this run directory before execution.
Human review approved: `True`

## Status Counts

- `source_identity_human_approved`: 4

## Baseline Repositories

| Baseline | Repository | Status | Target | Commit | License | License evidence | Human decision | Main blockers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Trace2Skill` | `Qwen-Applications/Trace2Skill` | `source_identity_human_approved` | `code/official/baselines/Trace2Skill` | `3d0b52a140f002a512930252b613c49048f7d5ac` | `Apache-2.0` | `nested_only` | `approved` |  |
| `SkillX` | `zjunlp/SkillX` | `source_identity_human_approved` | `code/official/baselines/SkillX` | `0137cb8c2f9e69d5cc499e562dea789b2c5a8e35` | `MIT` | `top_level` | `approved` |  |
| `EvoSkill` | `sentient-agi/EvoSkill` | `source_identity_human_approved` | `code/official/baselines/EvoSkill` | `925229680ac4ceebedb44bc548dfb82631c66525` | `Apache-2.0` | `top_level` | `approved` |  |
| `CoEvoSkills` | `Zhang-Henry/CoEvoSkills` | `source_identity_human_approved` | `code/official/baselines/CoEvoSkills` | `3171de28cc8d3c3bbbec0ef5445e59faca46815b` | `MIT` | `top_level` | `approved` |  |

## Ready Conditions

- All four repositories exist under code/official/baselines.
- Each repository has an immutable commit recorded in this artifact.
- Each repository license is present locally and reviewed.
- A human review artifact approves the repository identity for reconstructed comparison use.
