# Baseline Single-Skill Adapter Contract

Status: `blocked_pending_baseline_source_identity_review`

This contract defines how the four baseline generators can be adapted into the
controlled single Markdown skill setting described for the SkillGen baseline
comparison. It is a reconstructed-comparison contract, not proof that the
SkillGen authors used the same runner.

## Shared Input Contract

- Use the same SkillGen construction split, base model, seed, and saved baseline
  trajectories as the SkillGen run being compared.
- Provide each baseline only construction-split information available before
  held-out evaluation.
- Preserve each baseline's construction stdout, stderr, configs, prompts,
  generated artifacts, and exit codes inside the run directory.
- Do not expose held-out labels or held-out trajectories during baseline skill
  construction.

## Shared Output Contract

- Each baseline adapter must emit exactly one Markdown skill.
- The final with-skill intervention must point to that Markdown skill only.
- Each adapter must also write `adapter_metadata.json` with source repo, commit,
  license, input split, model route, seed, native artifacts used, and dropped
  capabilities.
- Held-out evaluation must use the same paired rollout harness as SkillGen:
  same test split, same evaluator model, same judge model, same seed, and same
  BASE vs with-skill paired comparison.

## Forbidden Capabilities

- No executable helper scripts in the final skill.
- No generated tools.
- No reference bundles or retrieval documents.
- No `skill_load_reference` behavior.
- No multi-skill routing.
- No test-time skill selection.
- No held-out feedback during construction.

## Per-Baseline Adapter Rule

### Trace2Skill

- Native form: evolved skill directory and patch/consolidation outputs.
- Adapter: run Trace2Skill on construction trajectories, select the validated
  evolved skill, and flatten the selected directory plus relevant changelog into
  one Markdown instruction artifact.
- Deviation risk: Trace2Skill may expect a spreadsheet-oriented skill tree, so
  non-spreadsheet SkillGen tasks need a documented prompt/interface mapping.

### SkillX

- Native form: skill knowledge base with planning, functional, and atomic skill
  hierarchy.
- Adapter: construct the knowledge base on construction trajectories, select or
  merge the relevant hierarchy, and render it into one static Markdown skill.
- Deviation risk: disabling retrieval and test-time skill selection changes the
  native SkillX operating mode.

### EvoSkill

- Native form: evolved agent program containing prompt and skill mutations.
- Adapter: run the evolution loop on the construction split, select the best
  validation program, and export only the behavior that can be represented as one
  Markdown skill.
- Deviation risk: native EvoSkill may optimize a whole agent program, so the
  single-skill projection may understate or alter native performance.

### CoEvoSkills

- Native form: structured multi-file skill package with co-evolutionary
  verification.
- Adapter: run generator/verifier evolution on the construction split, select the
  validated package, and render instructions into one Markdown artifact while
  dropping scripts, assets, and references.
- Deviation risk: the single Markdown export removes the multi-file package
  structure that CoEvoSkills is designed to use.

## Aggregation Contract

- Parse each held-out run into `baseline_acc`, `baseline_skill_acc`,
  `delta_acc`, `repair`, `regression`, and `net_gain`.
- Compare each reconstructed baseline skill against the same no-skill baseline
  used for SkillGen.
- Aggregate deltas by benchmark-model setting, then compare average improvement
  against SkillGen's Figure 2 result.
- If a baseline fails to run, preserve logs and mark that baseline
  `failed_to_run`; do not silently drop it from the aggregate.
