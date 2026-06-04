# Group F Status Transition Policy

Date: 2026-06-04

Scope: SkillGen Phase 0 evidence and report integration. This policy defines how
new work from groups A-E may change claim status in the Phase 0 validation
package.

## Status Meanings

Use these terminal or report-facing statuses only when the required evidence is
present.

| Status | Meaning | Minimum evidence |
| --- | --- | --- |
| `reproduced` | Observed official or approved exact-equivalent execution matches the paper claim within the accepted comparison rule. | Raw logs, parsed results, comparison artifact, no unresolved deviation affecting the claim. |
| `partially_reproduced` | Execution supports part of the claim, uses smoke scale, subset scale, or shows only one part of a multi-part claim. | Raw logs, parsed results, explicit scope limitation, comparison artifact. |
| `not_reproduced` | Execution completed and observed results do not support the claim. | Raw logs, parsed results, comparison artifact, preserved failure or negative evidence. |
| `failed_to_run` | Approved command ran but install, preparation, benchmark, or parsing failed. | Command, exit code, stdout/stderr, environment metadata, failure explanation. |
| `blocked` | The validation target is clear, but a recoverable contract, data bridge, data file, route, approval, or execution artifact is missing. | Named missing artifact or approval and next action. |
| `not_testable` | Current official materials are insufficient to define a faithful validation task. Running would require reconstructing an experiment that is not yet specified. | Missing official identity, runner, config, split, or metric definition. |
| `ready_for_execution` | All structural contracts for the target are present and a command plan can be reviewed. | Data/split contract, adapter/runner contract, model route mapping, command plan, expected outputs. |

Intermediate statuses may appear inside planning artifacts, but the final report
must map them to the report-facing statuses above or explain why they are
pre-execution planning states.

## Allowed Transitions

The following transitions are allowed when the listed artifact evidence exists.

| From | To | Required artifact trigger |
| --- | --- | --- |
| `not_testable` | `blocked_pending_source_identity_review` | Public or paper-indicated source candidate found, but identity/commit/license/harness compatibility are not reviewed. |
| `not_testable` | `blocked_pending_reconstructed_contract` | Official exact path is missing, but a reconstruction path can be defined and needs human review. |
| `blocked_pending_source_identity_review` | `ready_for_reconstructed_execution` | Source identity review, adapter contract, deviation note, command plan, and human approval exist. |
| `blocked_pending_reconstructed_contract` | `ready_for_reconstructed_execution` | Reconstructed contract and deviation disclosure exist, and the report will not call it exact reproduction. |
| `blocked` | `ready_for_execution` | Missing official-compatible adapter/split/data/route contract has been written and command plan is ready for human review. |
| `ready_for_execution` | `failed_to_run` | Approved command attempted and failed, with stdout/stderr/exit code captured. |
| `ready_for_execution` | `reproduced` | Approved execution completed and comparison matches the full paper claim. |
| `ready_for_execution` | `partially_reproduced` | Approved execution completed but scope is subset/smoke/reconstructed or only part of the claim is supported. |
| `ready_for_execution` | `not_reproduced` | Approved execution completed and comparison contradicts or falls short of the claim. |
| `failed_to_run` | `ready_for_execution` | Failure cause has been fixed without deleting old logs, and a new command plan or retry approval exists. |

## Disallowed Shortcuts

- Do not move `not_testable` directly to `reproduced`.
- Do not move `blocked` directly to `reproduced` just because a contract was
  written. Contracts make execution possible; they are not validation evidence.
- Do not replace `not_reproduced` with `blocked` after negative execution
  evidence exists. Add a new row, attempt, or limitation note instead.
- Do not describe a reconstructed or inferred benchmark as exact reproduction.
- Do not delete or overwrite old raw logs, parsed results, or comparison files
  when a later attempt improves the status.

## Evidence Classes

Use these labels in claim rows, deviation notes, and final report language.

| Evidence class | Use when |
| --- | --- |
| `exact_reproduction` | Official paper code, data, split, model route, command, and comparison rule are all identified and executed. |
| `official_code_reproduction` | Official code is executed, but there are provider route or environment differences that do not affect the benchmark contract. |
| `canonical_source_reconstruction` | A canonical benchmark/data source is used to rebuild a missing SkillGen-compatible bridge. |
| `deviation_backed_reconstruction` | A human-approved adapter, split, config, or runner is reconstructed because the official checkout lacks it. |
| `smoke_scale_execution` | The run exercises the official path on reduced sample size or reduced model scope. |
| `executed_negative_evidence` | Execution completed and observed result failed to support the claim. |
| `failed_execution_evidence` | Execution failed, and logs are preserved as evidence. |
| `planning_only` | Artifact is a contract or plan, not an execution result. |

## Transition Record

Every status-changing update to `all_claim_verification_matrix` must be backed by
a transition record, either embedded in the claim row or stored in a companion
integration artifact.

Required fields:

```json
{
  "claim_id": "claim_table1_average_gains_all_models",
  "previous_status": "blocked",
  "proposed_status": "ready_for_execution",
  "evidence_class": "canonical_source_reconstruction",
  "artifact_inputs": [
    "logs/phase_0_parallel_20260604/A_alfworld/alfworld_adapter_contract.md"
  ],
  "raw_log_inputs": [],
  "deviation_ids": [
    "alfworld_skillgen_adapter_reconstruction"
  ],
  "human_review_artifact": "artifacts/05_reviews_and_approval/human_command_review.md",
  "reason": "ALFWorld adapter and split contracts are now defined, but no benchmark execution has run yet.",
  "updated_at": "2026-06-04"
}
```

## Claim-Specific Transition Notes

| Claim | Current barrier | First valid promotion |
| --- | --- | --- |
| `claim_table1_average_gains_all_models` | ALFWorld IOD/OOD and LiveCodeBench split contracts, full matrix execution | `ready_for_execution` after A/B/C contracts are present; result status only after full matrix logs are parsed. |
| `claim_table1_entry_counts` | Complete 80-entry delta matrix | Same as above; counts must be computed from parsed deltas, not manually asserted. |
| `claim_table1_alfworld_scienceworld_patterns` | ALFWorld adapter/split and ScienceWorld paired rows | `ready_for_execution` after ALFWorld and ScienceWorld rows have command plans. |
| `claim_cross_model_transfer` | ALFWorld OOD transfer row and transfer aggregation | `ready_for_execution` after transfer manifest covers all 120 off-diagonal comparisons. |
| `claim_refinement_best_of_k` | Per-round trace extraction and Figure 7 aggregation contract | `ready_for_execution` after trace retention and aggregation schema are in place. |
| `claim_baseline_generator_comparison` | Baseline source identity and single-skill adapter | `ready_for_reconstructed_execution` only after source review and deviation-backed adapter are approved. |
| `claim_ablation_full_wins` | Figure 3 A1-A5 reconstructed configs | `ready_for_reconstructed_execution` only after ablation config matrix and deviation note are approved. |

## Merge Rule

When multiple attempts exist for one claim, preserve all attempts and make the
report-facing status the strongest status supported by the most relevant
approved evidence:

1. Exact full-paper execution outranks reconstructed execution.
2. Full-scale execution outranks smoke-scale execution.
3. Later successful execution does not erase earlier failed or negative logs.
4. If evidence conflicts, the report must show both and explain why one governs
   the current status.
