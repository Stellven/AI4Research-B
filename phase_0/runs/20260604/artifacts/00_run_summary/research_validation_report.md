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

- Claim verdict status counts: `blocked=7, not_reproduced=2, partially_reproduced=3`
- Execution readiness status counts: `blocked_by_alfworld_ood_execution=1, partially_ready_full_matrix=2, ready_for_execution=2, ready_for_full_matrix_execution_after_dependencies=1, ready_for_full_scope_artifact_check=1, ready_for_full_token_cost_execution=1, ready_for_reconstructed_ablation_human_review=1, ready_for_reconstructed_alfworld_implementation=1, ready_for_reconstructed_baseline_comparison=1, ready_for_trace_generation_after_full_runs=1`
- Matrix: `artifacts/all_claim_verification_matrix.json`
- Catalog: `artifacts/all_claims.json`


## Status Explanations

- Overall status is `not_reproduced` because the held-out smoke result did not satisfy `skill_acc > baseline_acc and net_gain > 0`: baseline=25.0%, skill=25.0%, net_gain=0.
- Full paper claim status is `blocked`: The AIME smoke target is not the full SkillGen Table 1 benchmark setup.

### Claim-Level Status Summary

| Claim | Claim verdict | Execution readiness | Compared / required evidence | Reason for verdict | Next step |
| --- | --- | --- | --- | --- | --- |
| `claim_method_paired_intervention` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_full_matrix_execution_after_dependencies</span> | Official AIME smoke output fields for paired no-skill vs with-skill evaluation: baseline_acc, skill_acc, repair, regression, and net_gain. | Partially reproduced: the smoke run exercised the paired comparison mechanism, but it is only one low-cost target rather than the full paper setup. | Promote from smoke evidence to full-paper evidence only if the matching full contract is executed. |
| `claim_table1_average_gains_all_models` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">partially_ready_full_matrix</span> | Paper Table 1 average gains across 80 benchmark-split-model entries vs the current AIME smoke scope and official support inventory. | Blocked: Table 1 requires the full 80-entry matrix; the current run only evaluated the AIME smoke target, whose held-out delta was 0.0%; some external rows are now prepared, but structural row contracts still remain. | Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix. |
| `claim_table1_entry_counts` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">partially_ready_full_matrix</span> | Paper Table 1 count claim, 50 improved / 25 unchanged / 5 regressed, vs current run scope and missing-row inventory. | Blocked: the 50/25/5 entry counts cannot be computed until all Table 1 rows and structural row contracts are executable and then run. | Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix. |
| `claim_table1_alfworld_scienceworld_patterns` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_reconstructed_alfworld_implementation</span> | Paper ALFWorld and ScienceWorld per-model improvement pattern vs official bundled data and executable target availability. | Blocked: ScienceWorld is present, but ALFWorld still lacks a SkillGen-compatible adapter and IOD/OOD split contract, even though canonical ALFWorld source code has been fetched. | Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan. |
| `claim_baseline_generator_comparison` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dcfce7;color:#166534;border:1px solid #86efac;font-weight:600">ready_for_reconstructed_baseline_comparison</span> | Paper SkillGen-vs-baseline-generator comparison vs baseline runner implementations available in the official checkout. | Blocked pending execution: public baseline sources are pinned and human-approved, and the single-Markdown-skill adapter contract is ready, but Figure 2 comparison has not been run. | Execute baseline_single_skill_adapter_contract.json with the shared paired rollout harness, then aggregate Figure 2 deltas. |
| `claim_ablation_full_wins` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_reconstructed_ablation_human_review</span> | Paper Figure 3 ablation claim vs official ablation scripts plus the Group E reconstructed A1-A5 contract/config/deviation package. | Blocked pending reconstructed smoke execution: Group E defines A1-A5 behavior, config/patch paths, expected outputs, and deviation notes, but no ablation smoke result has been run or parsed. This is not exact Figure 3 reproduction until author-original configs are found. | Human-review reconstructed_ablation_contract.json, ablation_config_matrix.json, and ablation_deviation_note.md, then execute ablation_smoke_plan.json before any paper-target Figure 3 matrix. |
| `claim_cross_model_transfer` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked_by_alfworld_ood_execution</span> | Paper 120 off-diagonal transfer comparisons vs available transfer-run matrix support and model route mapping. | Blocked: the transfer matrix plan is available, but the ALFWorld OOD structural contract is still missing. | Execute the approved ALFWorld OOD reconstructed contract first (data download, adapter implementation, split JSONs, trace retention), then run transfer_runner_plan.json. |
| `claim_tau_bench_gate_activated` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dcfce7;color:#166534;border:1px solid #86efac;font-weight:600">ready_for_execution</span> | Paper tau-Bench retail claim vs official tau-Bench smoke execution, internal verification gate, and held-out no-skill/skill comparison. | Not reproduced in this limited run: tau-Bench generated a skill, but gate_passed=False, train_net_gain=-1, heldout_delta=0.0%; the official evaluator treats rejected/deprecated skills as skill==baseline. | Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim. |
| `claim_chemllmbench_useful_gains` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dcfce7;color:#166534;border:1px solid #86efac;font-weight:600">ready_for_execution</span> | Paper ChemLLMBench property/yield claim vs prepared ChemLLMBench smoke executions and held-out no-skill/skill comparison. | ChemLLMBench execution summary: chemllmbench_property_prediction: status=not_reproduced, delta=0.0%, gate_passed=False; chemllmbench_yield_prediction: status=not_reproduced, delta=0.0%, gate_passed=False. | Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim. |
| `claim_refinement_best_of_k` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_trace_generation_after_full_runs</span> | Paper Figure 7 Best-of-K aggregate vs available per-round verification traces from executed runs. | Blocked: the smoke run has construction verification traces, but not the full aggregate per-round traces needed for the paper's Figure 7 result. | Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan. |
| `claim_token_cost` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_full_token_cost_execution</span> | Paper Table 4 token-cost summary vs available token logs from AIME/tau/Chem/ScienceWorld/PubMedQA/Mind2Web/MCPBench smoke runs and the Table 4 token plan. | Partially reproduced: token logs exist (train=59226, eval=14396), and all ready Table 4 token groups were executed at reduced POC scale; this verifies token logging but not the paper's full-scale token totals. | Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required. |
| `claim_auditable_skill_artifact` | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span> | <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_full_scope_artifact_check</span> | Generated SkillGen skill output directory and skill JSON artifact vs paper's auditable-skill property. | Partially reproduced: the smoke run produced a skill artifact directory, but this only verifies the property for the smoke run. | Promote from smoke evidence to full-paper evidence only if the matching full contract is executed. |

### Claim-Level Non-Success Details

#### claim_method_paired_intervention

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_full_matrix_execution_after_dependencies</span>
- Verification mode: `official_code_structure_and_smoke_output`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Reason:
  - Only partial/smoke evidence is available.
- Validation evidence:
  - Existing AIME smoke eval output contains baseline_acc, skill_acc, repair, regression, and net_gain fields.

#### claim_table1_average_gains_all_models

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">partially_ready_full_matrix</span>
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix.
- Reason:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (ready_for_reconstructed_execution), alfworld_ood (ready_for_reconstructed_execution).
  - ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution.
- Planning/readiness evidence:
  - External-source data has been prepared for rows: livecodebench, mcp_bench_all, socialmaze_upi.
  - Benchmark execution plan has Table 1-ready rows with resolved model routes: livecodebench, mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi.
  - Group A ALFWorld source/adapter/split/deviation contracts exist for reconstructed execution rows: alfworld_iod, alfworld_ood.
  - Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- External intake candidates:
  - livecodebench via livecodebench/code_generation_lite (Use code/official/scripts/prepare_benchmarks.py with --benchmark livecodebench and the paper-matching version tag.)
  - mcp_bench_all via Accenture/mcp-bench (Clone under code/official/benchmarks/external/mcp-bench, then run code/official/scripts/prepare_mcp_bench.py --split all with paper-matching train/test sizes.)
  - socialmaze_upi via xzx34/SocialMaze (Use code/official/scripts/prepare_socialmaze.py upi. The script can use shipped SocialMaze material or generate/cache a UPI pool under the requested output directory.)

#### claim_table1_entry_counts

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">partially_ready_full_matrix</span>
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix.
- Reason:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (ready_for_reconstructed_execution), alfworld_ood (ready_for_reconstructed_execution).
  - ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution.
- Planning/readiness evidence:
  - External-source data has been prepared for rows: livecodebench, mcp_bench_all, socialmaze_upi.
  - Benchmark execution plan has Table 1-ready rows with resolved model routes: livecodebench, mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi.
  - Group A ALFWorld source/adapter/split/deviation contracts exist for reconstructed execution rows: alfworld_iod, alfworld_ood.
  - Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- External intake candidates:
  - livecodebench via livecodebench/code_generation_lite (Use code/official/scripts/prepare_benchmarks.py with --benchmark livecodebench and the paper-matching version tag.)
  - mcp_bench_all via Accenture/mcp-bench (Clone under code/official/benchmarks/external/mcp-bench, then run code/official/scripts/prepare_mcp_bench.py --split all with paper-matching train/test sizes.)
  - socialmaze_upi via xzx34/SocialMaze (Use code/official/scripts/prepare_socialmaze.py upi. The script can use shipped SocialMaze material or generate/cache a UPI pool under the requested output directory.)

#### claim_table1_alfworld_scienceworld_patterns

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_reconstructed_alfworld_implementation</span>
- Verification mode: `full_table1_subset`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Reason:
  - ALFWorld IOD/OOD still need canonical data download, adapter implementation, generated split files, smoke logs, and human approval before result comparison.
- Planning/readiness evidence:
  - Canonical ALFWorld benchmark code is fetched at code/official/benchmarks/external/alfworld (commit aaba6870f86c5be6a08a491f32a50b906227bc3e).
  - Group A ALFWorld reconstructed-execution contracts are present for IOD and OOD.
  - ScienceWorld train/test JSON is bundled and can be planned for execution.

#### claim_baseline_generator_comparison

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dcfce7;color:#166534;border:1px solid #86efac;font-weight:600">ready_for_reconstructed_baseline_comparison</span>
- Verification mode: `baseline_generator_matrix`
- Next step: Execute baseline_single_skill_adapter_contract.json with the shared paired rollout harness, then aggregate Figure 2 deltas.
- Reason:
  - Reconstructed Figure 2 baseline comparison has not been executed yet.
- Planning/readiness evidence:
  - Group D baseline source identity review exists for: Trace2Skill, SkillX, EvoSkill, CoEvoSkills.
  - Single-Markdown-skill adapter contract status is ready_for_reconstructed_baseline_comparison.
  - All public baseline sources are pinned and human-approved for reconstructed comparison.

#### claim_ablation_full_wins

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_reconstructed_ablation_human_review</span>
- Verification mode: `ablation_matrix`
- Next step: Human-review reconstructed_ablation_contract.json, ablation_config_matrix.json, and ablation_deviation_note.md, then execute ablation_smoke_plan.json before any paper-target Figure 3 matrix.
- Reason:
  - Reconstructed ablation smoke execution has not been run or parsed yet.
- Planning/readiness evidence:
  - Group E reconstructed ablation contract exists with arms: Full, A1, A2, A3, A4, A5.
  - Config matrix status is ready_for_reconstructed_ablation_execution; reproduction class is deviation_backed_reconstructed_verification.
  - Original author Figure 3 runner/configs are still absent, so this can only support reconstructed ablation evidence unless those artifacts are later found.

#### claim_cross_model_transfer

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked_by_alfworld_ood_execution</span>
- Verification mode: `transfer_matrix`
- Next step: Execute the approved ALFWorld OOD reconstructed contract first (data download, adapter implementation, split JSONs, trace retention), then run transfer_runner_plan.json.
- Reason:
  - Full 120-comparison transfer claim still requires executing the ALFWorld OOD reconstructed contract, including data download, adapter implementation, generated split files, and retained per-round traces.
- Planning/readiness evidence:
  - Transfer runner plan has ready datasets for: scienceworld, mind2web, socialmaze_fts.
  - Transfer runner plan has reconstructed-execution contracts for: alfworld_ood.
  - Transfer runner plan encodes 120 off-diagonal comparisons before execution.

#### claim_tau_bench_gate_activated

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dcfce7;color:#166534;border:1px solid #86efac;font-weight:600">ready_for_execution</span>
- Verification mode: `tau_bench_matrix`
- Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.
- Reason:
  - Executed tau-Bench smoke did not support the paper claim: the generated skill failed the internal verification gate or produced no positive held-out skill delta.
- Validation evidence:
  - tau-Bench official smoke execution completed with skill_status=deprecated, verification_passed=False, train_net_gain=-1.
  - Held-out tau-Bench eval observed baseline=23.3%, skill=23.3%, delta=0.0%, net_gain=0.
- External intake candidates:
  - tau_bench via sierra-research/tau-bench (Place tau-bench under code/official/benchmarks/external/tau-bench, then run code/official/scripts/prepare_tau_bench.py for the paper-matching domain and split.)

#### claim_chemllmbench_useful_gains

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fee2e2;color:#991b1b;border:1px solid #f87171;font-weight:600">not_reproduced</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dcfce7;color:#166534;border:1px solid #86efac;font-weight:600">ready_for_execution</span>
- Verification mode: `chemllmbench_matrix`
- Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.
- Reason:
  - Executed ChemLLMBench smoke targets did not show positive skill gains for all prepared subtasks.
- Validation evidence:
  - chemllmbench_property_prediction execution status=official_code_eval_completed, verification_passed=False, train_net_gain=0, heldout_delta=0.0%.
  - chemllmbench_yield_prediction execution status=official_code_eval_completed, verification_passed=False, train_net_gain=0, heldout_delta=0.0%.
- External intake candidates:
  - chemllmbench via ChemFoundationModels/ChemLLMBench (Clone under code/official/external/chemllmbench, then run code/official/scripts/prepare_chemllmbench.py for the paper-matching tasks.)

#### claim_refinement_best_of_k

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;font-weight:600">blocked</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_trace_generation_after_full_runs</span>
- Verification mode: `refinement_trace_analysis`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Reason:
  - Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.
  - Needs full per-round run logs across representative benchmark-model entries.

#### claim_token_cost

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_full_token_cost_execution</span>
- Verification mode: `token_usage_aggregation`
- Next step: Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required.
- Reason:
  - The run uses reduced POC-scale configs, so token-log mechanics are reproduced but the paper's full-scale token totals are not.
- Validation evidence:
  - Existing smoke token evidence: train=59226, eval=14396.
  - chemllmbench_property_prediction token evidence: train=46661, eval=1514.
  - chemllmbench_yield_prediction token evidence: train=60179, eval=2931.
  - mcp_bench_token token evidence: train=448252, eval=120830.
  - mind2web_token token evidence: train=674323, eval=265899.
  - pubmedqa_token token evidence: train=280169, eval=167834.
  - scienceworld_token token evidence: train=588035, eval=476046.
  - tau_bench_retail token evidence: train=1629346, eval=1569988.
  - All Table 4 ready token groups were executed at reduced POC scale: mcp_bench_token, mind2web_token, pubmedqa_token, scienceworld_token, tau_bench_retail.
- Planning/readiness evidence:
  - Token-log aggregation plan covers Table 4 groups: ScienceWorld, PubMedQA, Mind2Web, MCPBench, tau-Bench.

#### claim_auditable_skill_artifact

- Claim verdict status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;font-weight:600">partially_reproduced</span>
- Execution readiness status: <span style="display:inline-block;padding:2px 8px;border-radius:4px;background:#fef9c3;color:#854d0e;border:1px solid #fde047;font-weight:600">ready_for_full_scope_artifact_check</span>
- Verification mode: `official_code_output_inspection`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Reason:
  - Only partial/smoke evidence is available.
- Validation evidence:
  - Existing smoke run produced a skill output directory: artifacts/08_results/raw_benchmark_outputs/skillgen_aime_smoke/skill_output/2026-06-02_02-03-02.


## Provider Resolution Addendum

- Current provider status: `openai_ready_non_openai_provider_unavailable`.
- OpenAI paper routes remain executable through `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1`.
- Non-OpenAI paper routes are currently marked `provider_unavailable` because captured stderr contains OpenRouter 402 insufficient-credit evidence and the current runner does not implement direct non-OpenAI provider routing.
- `provider_unavailable` is an execution availability status, not positive or negative benchmark evidence for the affected non-OpenAI entries.
- Model substitution is not allowed for Table 1 reproduction; substitute-model runs must be reported only as extension/deviation-backed experiments.
- Primary records:
  - `artifacts/provider_resolution_status.json`
  - `artifacts/06_plans_and_contracts/provider_resolution_status.md`
  - `artifacts/08_results/full_matrix/full_matrix_runner_state.json`

## Validation Evidence Files

- `artifacts/benchmark_results.json`
- `artifacts/claim_comparison.json`

## Planning And Readiness Artifacts

- `artifacts/verification_contract.json`
- `artifacts/command_plan.json`
- `artifacts/all_claims.json`
- `artifacts/all_claim_verification_matrix.json`
- `artifacts/external_source_intake_status.json`
- `artifacts/canonical_benchmark_source_status.json`
- `artifacts/model_route_mapping.template.json`
- `artifacts/provider_resolution_status.json`
- `artifacts/benchmark_execution_plan.json`
- `artifacts/transfer_runner_plan.json`
- `artifacts/full_matrix_execution_contract.json`
- `artifacts/transfer_execution_contract.json`
- `artifacts/figure7_trace_extraction_contract.json`
- `artifacts/per_round_trace_retention_checklist.json`
- `artifacts/token_log_plan.json`
- `artifacts/baseline_source_identity_review.json`
- `artifacts/baseline_single_skill_adapter_contract.json`
- `artifacts/baseline_deviation_note.md`
- `artifacts/reconstructed_ablation_contract.json`
- `artifacts/ablation_config_matrix.json`
- `artifacts/ablation_smoke_plan.json`
- `artifacts/ablation_deviation_note.md`

## Raw Output Files

- `outputs/install_stdout.txt`
- `outputs/install_stderr.txt`
- `outputs/benchmark_stdout.txt`
- `outputs/benchmark_stderr.txt`

## Limitations

- This is a paper-specific automation POC.
- The selected target is a low-cost AIME smoke validation, not the paper's full Table 1 benchmark matrix.
- Live install and benchmark execution require `artifacts/approval.json` plus API keys.
- Additional target executions may include recorded deviations, especially the direct OpenAI fallback used when OpenRouter credits were unavailable.
