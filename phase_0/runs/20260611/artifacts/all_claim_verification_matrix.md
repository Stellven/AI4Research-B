# All-Claim Verification Matrix

This matrix separates paper-claim verdict status from next-step execution readiness.

## Claim Verdict Status Counts

- `blocked`: 12

## Execution Readiness Status Counts

- `blocked_by_alfworld_ood_execution`: 1
- `blocked_missing_paired_smoke_output`: 1
- `blocked_missing_skill_artifact_run`: 1
- `partially_ready_full_matrix`: 2
- `ready_for_execution`: 2
- `ready_for_full_token_cost_execution`: 1
- `ready_for_reconstructed_ablation_human_review`: 1
- `ready_for_reconstructed_alfworld_implementation`: 1
- `ready_for_source_identity_review`: 1
- `ready_for_trace_generation_after_full_runs`: 1

## Claims

### claim_method_paired_intervention

- Claim verdict status: `blocked`
- Execution readiness status: `blocked_missing_paired_smoke_output`
- Verification mode: `official_code_structure_and_smoke_output`
- Next step: No next step defined.
- Blockers:
  - Needs at least one official eval output with paired result fields.

### claim_table1_average_gains_all_models

- Claim verdict status: `blocked`
- Execution readiness status: `partially_ready_full_matrix`
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix.
- Planning/readiness evidence: External-source data has been prepared for rows: livecodebench, mcp_bench_all, socialmaze_upi. Benchmark execution plan has Table 1-ready rows with resolved model routes: livecodebench, mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi. Group A ALFWorld source/adapter/split/deviation contracts exist for reconstructed execution rows: alfworld_iod, alfworld_ood. Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- External source candidates:
  - `livecodebench`: livecodebench/code_generation_lite -> code/official/data/livecodebench
  - `mcp_bench_all`: Accenture/mcp-bench -> code/official/benchmarks/external/mcp-bench
  - `socialmaze_upi`: xzx34/SocialMaze -> code/official/benchmarks/external/social-maze or code/official/data/socialmaze/upi
- Blockers:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (ready_for_reconstructed_execution), alfworld_ood (ready_for_reconstructed_execution).
  - ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution.

### claim_table1_entry_counts

- Claim verdict status: `blocked`
- Execution readiness status: `partially_ready_full_matrix`
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood), then aggregate the full Table 1 matrix.
- Planning/readiness evidence: External-source data has been prepared for rows: livecodebench, mcp_bench_all, socialmaze_upi. Benchmark execution plan has Table 1-ready rows with resolved model routes: livecodebench, mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi. Group A ALFWorld source/adapter/split/deviation contracts exist for reconstructed execution rows: alfworld_iod, alfworld_ood. Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- External source candidates:
  - `livecodebench`: livecodebench/code_generation_lite -> code/official/data/livecodebench
  - `mcp_bench_all`: Accenture/mcp-bench -> code/official/benchmarks/external/mcp-bench
  - `socialmaze_upi`: xzx34/SocialMaze -> code/official/benchmarks/external/social-maze or code/official/data/socialmaze/upi
- Blockers:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (ready_for_reconstructed_execution), alfworld_ood (ready_for_reconstructed_execution).
  - ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution.

### claim_table1_alfworld_scienceworld_patterns

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_reconstructed_alfworld_implementation`
- Verification mode: `full_table1_subset`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Planning/readiness evidence: Canonical ALFWorld benchmark code is fetched at code/official/benchmarks/external/alfworld (commit aaba6870f86c5be6a08a491f32a50b906227bc3e). Group A ALFWorld reconstructed-execution contracts are present for IOD and OOD. ScienceWorld train/test JSON is bundled and can be planned for execution.
- Blockers:
  - ALFWorld IOD/OOD still need canonical data download, adapter implementation, generated split files, smoke logs, and human approval before result comparison.

### claim_baseline_generator_comparison

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_source_identity_review`
- Verification mode: `baseline_generator_matrix`
- Next step: write/approve baseline_source_identity_human_review.json, then approve reconstructed baseline adapter execution.
- Planning/readiness evidence: Group D baseline source identity review exists for: Trace2Skill, SkillX, EvoSkill, CoEvoSkills. Single-Markdown-skill adapter contract status is blocked_pending_baseline_source_identity_review.
- Blockers:
  - Official SkillGen checkout still does not include executable Figure 2 baseline runners.
  - Baseline source identity review is not complete or not human-approved.
  - Reconstructed comparison must use the single-Markdown-skill adapter contract before execution.

### claim_ablation_full_wins

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_reconstructed_ablation_human_review`
- Verification mode: `ablation_matrix`
- Next step: Human-review reconstructed_ablation_contract.json, ablation_config_matrix.json, and ablation_deviation_note.md, then execute ablation_smoke_plan.json before any paper-target Figure 3 matrix.
- Planning/readiness evidence: Group E reconstructed ablation contract exists with arms: Full, A1, A2, A3, A4, A5. Config matrix status is ready_for_reconstructed_ablation_execution; reproduction class is deviation_backed_reconstructed_verification. Original author Figure 3 runner/configs are still absent, so this can only support reconstructed ablation evidence unless those artifacts are later found.
- Blockers:
  - Reconstructed ablation smoke execution has not been run or parsed yet.

### claim_cross_model_transfer

- Claim verdict status: `blocked`
- Execution readiness status: `blocked_by_alfworld_ood_execution`
- Verification mode: `transfer_matrix`
- Next step: Execute the approved ALFWorld OOD reconstructed contract first (data download, adapter implementation, split JSONs, trace retention), then run transfer_runner_plan.json.
- Planning/readiness evidence: Transfer runner plan has ready datasets for: scienceworld, mind2web, socialmaze_fts. Transfer runner plan has reconstructed-execution contracts for: alfworld_ood. Transfer runner plan encodes 120 off-diagonal comparisons before execution.
- Blockers:
  - Full 120-comparison transfer claim still requires executing the ALFWorld OOD reconstructed contract, including data download, adapter implementation, generated split files, and retained per-round traces.

### claim_tau_bench_gate_activated

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_execution`
- Verification mode: `tau_bench_matrix`
- Next step: Create/approve the benchmark execution contract, run the prepared benchmark, parse results, and compare to the paper claim.
- Planning/readiness evidence: tau-Bench external source and retail train/test JSONs have been prepared. No structural blocker remains for the prepared tau-Bench retail target.
- External source candidates:
  - `tau_bench`: sierra-research/tau-bench -> code/official/benchmarks/external/tau-bench
- Blockers:
  - Prepared tau-Bench target has not been executed and compared for this claim.

### claim_chemllmbench_useful_gains

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_execution`
- Verification mode: `chemllmbench_matrix`
- Next step: Create/approve the benchmark execution contract, run the prepared benchmark, parse results, and compare to the paper claim.
- Planning/readiness evidence: ChemLLMBench external source and task train/test JSONs have been prepared. No structural blocker remains for ChemLLMBench property/yield execution.
- External source candidates:
  - `chemllmbench`: ChemFoundationModels/ChemLLMBench -> code/official/external/chemllmbench
- Blockers:
  - Prepared ChemLLMBench targets have not been executed and compared for this claim.

### claim_refinement_best_of_k

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_trace_generation_after_full_runs`
- Verification mode: `refinement_trace_analysis`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Blockers:
  - Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.
  - Needs full per-round run logs across representative benchmark-model entries.

### claim_token_cost

- Claim verdict status: `blocked`
- Execution readiness status: `ready_for_full_token_cost_execution`
- Verification mode: `token_usage_aggregation`
- Next step: Run the Table 4 benchmark groups from token_log_plan.json, collect token logs, then compare grouped totals to the paper.
- Planning/readiness evidence: Token-log aggregation plan covers Table 4 groups: ScienceWorld, PubMedQA, Mind2Web, MCPBench, tau-Bench. No structural blocker remains for Table 4 token-log collection on the ready benchmark groups.
- Blockers:
  - Table 4 token-log collection has not been executed for the paper-scale grouped totals.

### claim_auditable_skill_artifact

- Claim verdict status: `blocked`
- Execution readiness status: `blocked_missing_skill_artifact_run`
- Verification mode: `official_code_output_inspection`
- Next step: No next step defined.
- Blockers:
  - Needs an official run that produces a SkillGen skill artifact.

## Executable Official-Code Targets

- `skillgen_aime`: data/aime/train.json -> data/aime/test.json (train_n=80, test_n=40)
- `skillgen_mcp_bench_single`: data/mcp_bench/train.json -> data/mcp_bench/test.json (train_n=40, test_n=16)
- `skillgen_mind2web`: data/mind2web/train.json -> data/mind2web/test.json (train_n=100, test_n=100)
- `skillgen_pubmedqa`: data/pubmedqa/train.json -> data/pubmedqa/test.json (train_n=150, test_n=100)
- `skillgen_scienceworld`: data/scienceworld/train.json -> data/scienceworld/test.json (train_n=150, test_n=100)
- `skillgen_socialmaze_fts`: data/socialmaze/train.json -> data/socialmaze/test.json (train_n=60, test_n=50)
- `skillgen_toolbench`: data/toolbench/train.json -> data/toolbench/test.json (train_n=120, test_n=50)
