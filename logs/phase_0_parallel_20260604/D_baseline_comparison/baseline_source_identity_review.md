# Baseline Source Identity Review

Status: `blocked_pending_baseline_source_identity_review`

Group D moves `claim_baseline_generator_comparison` out of a plain `not_testable`
state by defining the public-code source identity work needed before a
reconstructed Figure 2 comparison can run.

This is not yet an exact SkillGen Figure 2 reproduction. The SkillGen official
checkout does not include executable baseline-comparison runners for
Trace2Skill, SkillX, EvoSkill, or CoEvoSkills. The repos below are public source
candidates that must be cloned inside the run directory, pinned to commits, and
human-reviewed before execution.

## Candidate Sources

| Baseline | Candidate repo | Expected license | Native output | Current decision |
| --- | --- | --- | --- | --- |
| Trace2Skill | `Qwen-Applications/Trace2Skill` | `Apache-2.0` | Skill directory evolved from trajectory analyses | Candidate public implementation, pending local commit/license review |
| SkillX | `zjunlp/SkillX` | `MIT` | Hierarchical skill knowledge base | Candidate public implementation, pending local commit/license review |
| EvoSkill | `sentient-agi/EvoSkill` | `Apache-2.0` | Evolved agent program with prompt and skill mutations | Candidate public implementation, pending local commit/license review |
| CoEvoSkills | `Zhang-Henry/CoEvoSkills` | `MIT` | Structured multi-file skill package | Candidate public implementation, pending local commit/license review |

## Required Local Identity Checks

- Clone every baseline repository under `code/official/baselines/` inside the
  Phase 0 run directory.
- Record `git rev-parse HEAD` for each cloned repo.
- Record the local license file path and SPDX interpretation.
- Confirm the repo matches the baseline method named in SkillGen Appendix C.6.
- Record whether the repo is official author code, project reference code, or a
  best-available public implementation.
- Record native entrypoints and their required datasets, models, API keys,
  network access, Docker needs, and file writes.

## Status Transition Rule

- Stay `blocked_pending_baseline_source_identity_review` until all four repos
  have local commit hashes, local license evidence, and a human identity review.
- Move to `ready_for_reconstructed_baseline_comparison` only after
  `artifacts/baseline_source_identity_human_review.json` approves the source
  identities and the single-skill adapter contract.
- If any repo cannot be identified or licensed clearly, keep that baseline
  blocked and report the Figure 2 aggregate as incomplete.

## Evidence Basis

- Trace2Skill public repo: https://github.com/Qwen-Applications/Trace2Skill
- SkillX public repo: https://github.com/zjunlp/SkillX
- EvoSkill public repo: https://github.com/sentient-agi/EvoSkill
- CoEvoSkills public repo: https://github.com/Zhang-Henry/CoEvoSkills
