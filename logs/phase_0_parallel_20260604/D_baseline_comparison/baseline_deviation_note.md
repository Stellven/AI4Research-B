# Baseline Deviation Note

Status: `blocked_pending_baseline_source_identity_review`

The Group D path is a public-code reconstructed baseline comparison. It should
not be described as an exact SkillGen Figure 2 reproduction until the original
SkillGen baseline runner identities are known or the public repos are proven to
match the authors' implementation and adaptation.

## Disclosure Text

Use the following disclosure in future validation reports if this path is run:

```text
The baseline generator comparison uses public source repositories for
Trace2Skill, SkillX, EvoSkill, and CoEvoSkills and adapts each method into the
controlled single Markdown skill interface used by the SkillGen comparison. This
is a reconstructed comparison, because the official SkillGen checkout does not
include the authors' executable Figure 2 baseline runners. Results can support a
partial reproduction if they match the paper trend, but they should not be
reported as exact reproduction evidence without source-identity proof.
```

## Deviation Labels

- `public_code_reconstruction`: baseline code comes from public repos outside
  the SkillGen official checkout.
- `single_markdown_skill_projection`: native baseline outputs are constrained to
  one Markdown skill.
- `disabled_native_runtime_features`: scripts, tools, references, retrieval,
  multi-skill routing, and test-time skill selection are disabled.
- `shared_harness_reexecution`: all methods are re-run through the SkillGen
  paired rollout harness instead of a baseline-native evaluator.

## Safety And Review Notes

- Clone and dependency installation require a separate human approval gate.
- All cloned repos, caches, generated artifacts, and dependencies must stay
  inside the project or Phase 0 run directory.
- No baseline code should be patched before the original native command and
  failure mode are recorded.
- Any adapter patch must be listed in `adapter_metadata.json` and summarized in
  the final validation report.
- If a baseline requires Docker, external services, model API keys, or large
  datasets, the run must stop at a human-visible command review gate.
