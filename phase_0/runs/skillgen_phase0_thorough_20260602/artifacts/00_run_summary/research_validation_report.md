# SkillGen Phase 0 Automated Validation Report

Run ID: `skillgen_phase0_thorough_20260602`

## Overall Status

`not_reproduced`

## Full Paper Claim Status

`blocked`

The current automation targets the SkillGen AIME smoke validation. It does not claim to reproduce the full Table 1 result unless a matching Table 1 contract is executed.

## Input

- Paper source: `meeting docs/SkillGen.pdf`
- Paper copy: `input/paper.pdf`

## Verification Contract

- Target: `skillgen_aime_smoke`
- Scope: `official-code smoke only; not full Table 1 reproduction`
- Dataset: `aime`
- Train subset: `artifacts/smoke_data/aime_train_n8_seed42.json`
- Test subset: `artifacts/smoke_data/aime_test_n4_seed42.json`

## Official Code

- Repository: `https://github.com/yccm/SkillGen`
- Local path: `code/official`
- Commit: `3c4537bb12ac287ceb1b5d410b491206089fdcb7`
- Intake status: `intake_complete`

## Benchmark Result

- Benchmark status: `official_code_smoke_completed`
- Baseline accuracy: `25.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `0.0%`
- Repairs: `0`
- Regressions: `0`
- Net gain: `0`

## All-Claim Verification

- Claim status counts: `blocked=5, not_reproduced=2, not_testable=2, partially_reproduced=3`
- Matrix: `artifacts/02_claims/all_claim_verification_matrix.json`
- Catalog: `artifacts/02_claims/all_claims.json`

## Status Explanations

- Overall status is `not_reproduced` because the held-out smoke result did not satisfy `skill_acc > baseline_acc and net_gain > 0`: baseline=25.0%, skill=25.0%, net_gain=0.
- Full paper claim status is `blocked`: The AIME smoke target is not the full SkillGen Table 1 benchmark setup.

### Claim-Level Status Summary

| Claim | Status | Compared / required evidence | Reason for status | Next step |
| --- | --- | --- | --- | --- |
| `claim_method_paired_intervention` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span> | Official AIME smoke output fields for paired no-skill vs with-skill evaluation: baseline_acc, skill_acc, repair, regression, and net_gain. | Partially reproduced: the smoke run exercised the paired comparison mechanism, but it is only one low-cost target rather than the full paper setup. | Promote from smoke evidence to full-paper evidence only if the matching full contract is executed. |
| `claim_table1_average_gains_all_models` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | Paper Table 1 average gains across 80 benchmark-split-model entries vs the current AIME smoke scope and official support inventory. | Blocked: Table 1 requires the full 80-entry matrix; the current run only evaluated the AIME smoke target, whose held-out delta was 0.0%; some external rows are now prepared, but structural row contracts still remain. | Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood, livecodebench), then aggregate the full Table 1 matrix. |
| `claim_table1_entry_counts` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | Paper Table 1 count claim, 50 improved / 25 unchanged / 5 regressed, vs current run scope and missing-row inventory. | Blocked: the 50/25/5 entry counts cannot be computed until all Table 1 rows and structural row contracts are executable and then run. | Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood, livecodebench), then aggregate the full Table 1 matrix. |
| `claim_table1_alfworld_scienceworld_patterns` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | Paper ALFWorld and ScienceWorld per-model improvement pattern vs official bundled data and executable target availability. | Blocked: ScienceWorld is present, but ALFWorld still lacks a SkillGen-compatible adapter and IOD/OOD split contract, even though canonical ALFWorld source code has been fetched. | Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan. |
| `claim_baseline_generator_comparison` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#e5e7eb;color:#374151;border:1px solid #9ca3af;font-weight:600">not_testable</span> | Paper SkillGen-vs-baseline-generator comparison vs baseline runner implementations available in the official checkout. | Not testable: the official checkout does not include executable Trace2Skill, SkillX, EvoSkill, or CoEvoSkills comparison runners. | Obtain missing official code, data, or scripts; otherwise keep this claim not_testable. |
| `claim_ablation_full_wins` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#e5e7eb;color:#374151;border:1px solid #9ca3af;font-weight:600">not_testable</span> | Paper Figure 3 ablation claim vs ablation scripts and named ablated configs in the official checkout. | Not testable: the official checkout does not include an ablation runner or named ablated configurations for Figure 3. | Obtain missing official code, data, or scripts; otherwise keep this claim not_testable. |
| `claim_cross_model_transfer` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | Paper 120 off-diagonal transfer comparisons vs available transfer-run matrix support and model route mapping. | Blocked: the transfer matrix plan is available, but the ALFWorld OOD structural contract is still missing. | Fill the ALFWorld OOD SkillGen contract gap, then execute transfer_runner_plan.json. |
| `claim_tau_bench_gate_activated` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span> | Paper tau-Bench retail claim vs official tau-Bench smoke execution, internal verification gate, and held-out no-skill/skill comparison. | Not reproduced in this limited run: tau-Bench generated a skill, but gate_passed=False, train_net_gain=-1, heldout_delta=0.0%; the official evaluator treats rejected/deprecated skills as skill==baseline. | Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim. |
| `claim_chemllmbench_useful_gains` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span> | Paper ChemLLMBench property/yield claim vs prepared ChemLLMBench smoke executions and held-out no-skill/skill comparison. | ChemLLMBench execution summary: chemllmbench_property_prediction: status=not_reproduced, delta=0.0%, gate_passed=False; chemllmbench_yield_prediction: status=not_reproduced, delta=0.0%, gate_passed=False. | Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim. |
| `claim_refinement_best_of_k` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | Paper Figure 7 Best-of-K aggregate vs available per-round verification traces from executed runs. | Blocked: the smoke run has construction verification traces, but not the full aggregate per-round traces needed for the paper's Figure 7 result. | Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan. |
| `claim_token_cost` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span> | Paper Table 4 token-cost summary vs available token logs from AIME/tau/Chem/ScienceWorld/PubMedQA/Mind2Web/MCPBench smoke runs and the Table 4 token plan. | Partially reproduced: token logs exist (train=59226, eval=14396), and all ready Table 4 token groups were executed at reduced POC scale; this verifies token logging but not the paper's full-scale token totals. | Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required. |
| `claim_auditable_skill_artifact` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span> | Generated SkillGen skill output directory and skill JSON artifact vs paper's auditable-skill property. | Partially reproduced: the smoke run produced a skill artifact directory, but this only verifies the property for the smoke run. | Promote from smoke evidence to full-paper evidence only if the matching full contract is executed. |

### Claim-Level Non-Success Details

#### claim_method_paired_intervention

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span>
- Verification mode: `official_code_structure_and_smoke_output`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Reason:
  - Only partial/smoke evidence is available.
- Evidence:
  - Existing AIME smoke eval output contains baseline_acc, skill_acc, repair, regression, and net_gain fields.

#### claim_table1_average_gains_all_models

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood, livecodebench), then aggregate the full Table 1 matrix.
- Reason:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (blocked_canonical_code_fetched_missing_skillgen_contract), alfworld_ood (blocked_canonical_code_fetched_missing_skillgen_contract), livecodebench (blocked_pending_train_test_split_contract).
- External intake candidates:
  - livecodebench via livecodebench/code_generation_lite (Use code/official/scripts/prepare_benchmarks.py with --benchmark livecodebench and the paper-matching version tag.)
  - mcp_bench_all via Accenture/mcp-bench (Clone under code/official/benchmarks/external/mcp-bench, then run code/official/scripts/prepare_mcp_bench.py --split all with paper-matching train/test sizes.)
  - socialmaze_upi via xzx34/SocialMaze (Use code/official/scripts/prepare_socialmaze.py upi. The script can use shipped SocialMaze material or generate/cache a UPI pool under the requested output directory.)

#### claim_table1_entry_counts

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood, livecodebench), then aggregate the full Table 1 matrix.
- Reason:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (blocked_canonical_code_fetched_missing_skillgen_contract), alfworld_ood (blocked_canonical_code_fetched_missing_skillgen_contract), livecodebench (blocked_pending_train_test_split_contract).
- External intake candidates:
  - livecodebench via livecodebench/code_generation_lite (Use code/official/scripts/prepare_benchmarks.py with --benchmark livecodebench and the paper-matching version tag.)
  - mcp_bench_all via Accenture/mcp-bench (Clone under code/official/benchmarks/external/mcp-bench, then run code/official/scripts/prepare_mcp_bench.py --split all with paper-matching train/test sizes.)
  - socialmaze_upi via xzx34/SocialMaze (Use code/official/scripts/prepare_socialmaze.py upi. The script can use shipped SocialMaze material or generate/cache a UPI pool under the requested output directory.)

#### claim_table1_alfworld_scienceworld_patterns

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Verification mode: `full_table1_subset`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Reason:
  - ALFWorld IOD/OOD data is not bundled and no SkillGen-compatible ALFWorld adapter/split contract exists yet.

#### claim_baseline_generator_comparison

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#e5e7eb;color:#374151;border:1px solid #9ca3af;font-weight:600">not_testable</span>
- Verification mode: `baseline_generator_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Reason:
  - Official checkout does not include Trace2Skill, SkillX, EvoSkill, or CoEvoSkills runner implementations.
  - README describes baseline adaptation details in the paper, but no executable baseline-comparison command is present.
  - A public baseline project would still need identity review and a SkillGen-compatible runner before it can count as an identical reproduction source.

#### claim_ablation_full_wins

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#e5e7eb;color:#374151;border:1px solid #9ca3af;font-weight:600">not_testable</span>
- Verification mode: `ablation_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Reason:
  - Official checkout does not include an ablation runner or named ablated configs.
  - Cannot reproduce Figure 3 without reconstructing unprovided ablation variants.

#### claim_cross_model_transfer

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Verification mode: `transfer_matrix`
- Next step: Fill the ALFWorld OOD SkillGen contract gap, then execute transfer_runner_plan.json.
- Reason:
  - Full 120-comparison transfer claim still requires the ALFWorld OOD SkillGen adapter/split contract.

#### claim_tau_bench_gate_activated

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span>
- Verification mode: `tau_bench_matrix`
- Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.
- Reason:
  - Executed tau-Bench smoke did not support the paper claim: the generated skill failed the internal verification gate or produced no positive held-out skill delta.
- External intake candidates:
  - tau_bench via sierra-research/tau-bench (Place tau-bench under code/official/benchmarks/external/tau-bench, then run code/official/scripts/prepare_tau_bench.py for the paper-matching domain and split.)

#### claim_chemllmbench_useful_gains

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span>
- Verification mode: `chemllmbench_matrix`
- Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.
- Reason:
  - Executed ChemLLMBench smoke targets did not show positive skill gains for all prepared subtasks.
- External intake candidates:
  - chemllmbench via ChemFoundationModels/ChemLLMBench (Clone under code/official/external/chemllmbench, then run code/official/scripts/prepare_chemllmbench.py for the paper-matching tasks.)

#### claim_refinement_best_of_k

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Verification mode: `refinement_trace_analysis`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Reason:
  - Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.
  - Needs full per-round run logs across representative benchmark-model entries.

#### claim_token_cost

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span>
- Verification mode: `token_usage_aggregation`
- Next step: Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required.
- Reason:
  - The run uses reduced POC-scale configs, so token-log mechanics are reproduced but the paper's full-scale token totals are not.

#### claim_auditable_skill_artifact

- Status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span>
- Verification mode: `official_code_output_inspection`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Reason:
  - Only partial/smoke evidence is available.
- Evidence:
  - Existing smoke run produced a skill output directory: artifacts/raw_benchmark_outputs/skillgen_aime_smoke/skill_output/2026-06-02_02-03-02.


## Evidence Files

- `artifacts/06_plans_and_contracts/verification_contract.json`
- `artifacts/04_commands_and_environment/command_plan.json`
- `artifacts/02_claims/all_claims.json`
- `artifacts/02_claims/all_claim_verification_matrix.json`
- `artifacts/03_code_and_sources/external_source_intake_status.json`
- `artifacts/03_code_and_sources/canonical_benchmark_source_status.json`
- `artifacts/06_plans_and_contracts/model_route_mapping.template.json`
- `artifacts/06_plans_and_contracts/benchmark_execution_plan.json`
- `artifacts/06_plans_and_contracts/transfer_runner_plan.json`
- `artifacts/06_plans_and_contracts/token_log_plan.json`
- `outputs/install_stdout.txt`
- `outputs/install_stderr.txt`
- `outputs/benchmark_stdout.txt`
- `outputs/benchmark_stderr.txt`
- `artifacts/08_results/benchmark_results.json`
- `artifacts/08_results/claim_comparison.json`

## Limitations

- This is a paper-specific automation POC.
- The selected target is a low-cost AIME smoke validation, not the paper's full Table 1 benchmark matrix.
- Live install and benchmark execution require `artifacts/00_run_summary/approval.json` plus API keys.
- Additional target executions may include recorded deviations, especially the direct OpenAI fallback used when OpenRouter credits were unavailable.
