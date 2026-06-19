# Reconstructed Ablation Contract

Deviation-backed reconstructed execution contract for SkillGen Figure 3 ablations

Status: `ready_for_reconstructed_ablation_execution`
Reproduction class: `deviation_backed_reconstructed_verification`

## Exact Reproduction Blockers

- The current official checkout does not include an author-provided Figure 3 ablation runner.
- The current official checkout does not include named A1-A5 ablated config files.
- Any execution from this contract must be reported as reconstructed unless original author configs are later found.

## Shared Execution Contract

- `paired_harness`: Use the same no-skill baseline, held-out instances, model route, judge route, seed, and evaluator for Full and every ablation arm.
- `primary_metric`: delta_acc = skill_acc - baseline_acc on held-out paired evaluation.
- `claim_rule`: Full wins only if Full has higher held-out skill_acc or delta_acc than each A1-A5 arm for every executed dataset-model pair.
- `human_gate`: Human approval is required before executing reconstructed ablations, especially A3 because it disables the verification gate.
- `storage_rule`: All configs, patches, generated skills, raw logs, trajectories, and caches must remain inside the run directory.
- `trace_retention`:
  - Retain construction baseline and checkpoint trajectories.
  - Retain verification/round_* baseline, with-skill, summary, and case-analysis files.
  - Retain held-out eval_results.json and eval_results_trajectories for every arm.

## Arms

| Arm | Name | Implementation | Deviation label | Safety note |
| --- | --- | --- | --- | --- |
| `Full` | Complete SkillGen | `full_config` | `reference_full_system` | Full must use the same split, model route, judge route, and seed as every ablation arm. |
| `A1` | ICL k=3 instead of induced skill | `wrapper_generated_skill` | `reconstructed_icl_k3_demo_selection` | Demonstrations must come only from construction trajectories; held-out test instances must not leak into the skill text. |
| `A2` | No refinement | `config_only` | `reconstructed_no_refinement_config` | Keep verification output for round 1 so failures and regressions remain auditable. |
| `A3` | No verification gate | `behavioral_config_or_runner_patch` | `safety_gate_disabled_reconstructed_ablation` | This arm intentionally disables a safety/quality gate; raw failed-gate evidence must be preserved before held-out evaluation. |
| `A4` | No Failure Lessons | `prompt_patch_preferred` | `reconstructed_no_failure_lessons_prompt` | If the fallback post-process path is used, record that the generator still saw failure evidence during construction. |
| `A5` | Plain-text skill, no script/reference bundle | `config_only` | `reconstructed_plain_text_skill_config` | Only compare A5 against Full on dataset-model pairs where Full actually enables script/reference bundles. |

## Execution Layers

- `smoke_reconstructed_ablation`: `ready_for_reconstructed_ablation_execution` - Exercise Full and A1-A5 mechanics on one cheap approved dataset-model pair before paper-target matrix execution.
- `paper_target_reconstructed_ablation`: `blocked` - Run the reconstructed ablation matrix on the Figure 3 dataset-model pairs after those pairs are explicitly reviewed.
