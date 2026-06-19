# Ablation Deviation Note

The Figure 3 ablation package is a deviation-backed reconstructed verification plan.

It is not an exact original-paper reproduction because the current official checkout does not provide an author-supplied Figure 3 runner or named A1-A5 configs.

## Arm-Level Deviations

| Arm | Deviation label | Safety / review note |
| --- | --- | --- |
| `Full` | `reference_full_system` | Full must use the same split, model route, judge route, and seed as every ablation arm. |
| `A1` | `reconstructed_icl_k3_demo_selection` | Demonstrations must come only from construction trajectories; held-out test instances must not leak into the skill text. |
| `A2` | `reconstructed_no_refinement_config` | Keep verification output for round 1 so failures and regressions remain auditable. |
| `A3` | `safety_gate_disabled_reconstructed_ablation` | This arm intentionally disables a safety/quality gate; raw failed-gate evidence must be preserved before held-out evaluation. |
| `A4` | `reconstructed_no_failure_lessons_prompt` | If the fallback post-process path is used, record that the generator still saw failure evidence during construction. |
| `A5` | `reconstructed_plain_text_skill_config` | Only compare A5 against Full on dataset-model pairs where Full actually enables script/reference bundles. |

## Reporting Rule

Any result produced from this package must be reported as reconstructed ablation evidence. Use `partially_reproduced`, `not_reproduced`, or `failed_to_run` after execution; reserve `reproduced` for a future run that uses verified author-original Figure 3 configs.
