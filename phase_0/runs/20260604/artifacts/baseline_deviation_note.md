# Baseline Deviation Note

Status: `ready_for_reconstructed_baseline_comparison`

This comparison is a public-code reconstructed verification path, not an exact SkillGen Figure 2 reproduction yet.

## Required Disclosure

- Source: public baseline repositories named in the Group D source identity review.
- Adaptation: each baseline is constrained to emit one Markdown skill and then uses the SkillGen paired rollout harness.
- Deviation: the SkillGen official checkout does not include the authors' executable Figure 2 baseline runners.
- Limitation: even after repository identity, commit, license evidence, and adapter deviation are human-reviewed, the claim remains blocked rather than reproduced until reconstructed baseline execution produces parsed comparison results.

## License Evidence Notes

- Human review approved a license-evidence exception for nested-only local license files: Trace2Skill.

## Status Transition

- Current source identity status: `ready_for_reconstructed_baseline_comparison`
- Current adapter contract status: `ready_for_reconstructed_baseline_comparison`
- If the reconstructed comparison supports SkillGen's largest average improvement, mark the claim `partially_reproduced` unless the exact author runner is later identified.
- If it contradicts the paper result, mark the claim `not_reproduced` with raw logs preserved.
- If any baseline cannot run after approved setup, mark the affected comparison `failed_to_run` and keep the aggregate clearly incomplete.
