# All-Claim Verification Matrix

This matrix separates executable claims from claims that are blocked or not testable with the current official release.

## Status Counts

- `blocked`: 5
- `not_reproduced`: 2
- `not_testable`: 2
- `partially_reproduced`: 3

## Claims

### claim_method_paired_intervention

- Status: `partially_reproduced`
- Verification mode: `official_code_structure_and_smoke_output`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Evidence: Existing AIME smoke eval output contains baseline_acc, skill_acc, repair, regression, and net_gain fields.

### claim_table1_average_gains_all_models

- Status: `blocked`
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood, livecodebench), then aggregate the full Table 1 matrix.
- Evidence: External-source data has been prepared for rows: livecodebench, mcp_bench_all, socialmaze_upi. Benchmark execution plan has Table 1-ready rows with resolved model routes: mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi. Canonical ALFWorld code has been fetched, but these rows still need a SkillGen-compatible adapter and IOD/OOD split contract: alfworld_iod, alfworld_ood. Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- External source candidates:
  - `livecodebench`: livecodebench/code_generation_lite -> code/official/data/livecodebench
  - `mcp_bench_all`: Accenture/mcp-bench -> code/official/benchmarks/external/mcp-bench
  - `socialmaze_upi`: xzx34/SocialMaze -> code/official/benchmarks/external/social-maze or code/official/data/socialmaze/upi
- Blockers:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (blocked_canonical_code_fetched_missing_skillgen_contract), alfworld_ood (blocked_canonical_code_fetched_missing_skillgen_contract), livecodebench (blocked_pending_train_test_split_contract).

### claim_table1_entry_counts

- Status: `blocked`
- Verification mode: `full_table1_matrix`
- Next step: Resolve structurally non-ready Table 1 rows (alfworld_iod, alfworld_ood, livecodebench), then aggregate the full Table 1 matrix.
- Evidence: External-source data has been prepared for rows: livecodebench, mcp_bench_all, socialmaze_upi. Benchmark execution plan has Table 1-ready rows with resolved model routes: mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi. Canonical ALFWorld code has been fetched, but these rows still need a SkillGen-compatible adapter and IOD/OOD split contract: alfworld_iod, alfworld_ood. Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- External source candidates:
  - `livecodebench`: livecodebench/code_generation_lite -> code/official/data/livecodebench
  - `mcp_bench_all`: Accenture/mcp-bench -> code/official/benchmarks/external/mcp-bench
  - `socialmaze_upi`: xzx34/SocialMaze -> code/official/benchmarks/external/social-maze or code/official/data/socialmaze/upi
- Blockers:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Rows not yet Table 1 execution-ready: alfworld_iod (blocked_canonical_code_fetched_missing_skillgen_contract), alfworld_ood (blocked_canonical_code_fetched_missing_skillgen_contract), livecodebench (blocked_pending_train_test_split_contract).

### claim_table1_alfworld_scienceworld_patterns

- Status: `blocked`
- Verification mode: `full_table1_subset`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Evidence: Canonical ALFWorld benchmark code is fetched at code/official/benchmarks/external/alfworld (commit aaba6870f86c5be6a08a491f32a50b906227bc3e). ScienceWorld train/test JSON is bundled and can be planned for execution.
- Blockers:
  - ALFWorld IOD/OOD data is not bundled and no SkillGen-compatible ALFWorld adapter/split contract exists yet.

### claim_baseline_generator_comparison

- Status: `not_testable`
- Verification mode: `baseline_generator_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Blockers:
  - Official checkout does not include Trace2Skill, SkillX, EvoSkill, or CoEvoSkills runner implementations.
  - README describes baseline adaptation details in the paper, but no executable baseline-comparison command is present.
  - A public baseline project would still need identity review and a SkillGen-compatible runner before it can count as an identical reproduction source.

### claim_ablation_full_wins

- Status: `not_testable`
- Verification mode: `ablation_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Blockers:
  - Official checkout does not include an ablation runner or named ablated configs.
  - Cannot reproduce Figure 3 without reconstructing unprovided ablation variants.

### claim_cross_model_transfer

- Status: `blocked`
- Verification mode: `transfer_matrix`
- Next step: Fill the ALFWorld OOD SkillGen contract gap, then execute transfer_runner_plan.json.
- Evidence: Transfer runner plan has ready datasets for: scienceworld, mind2web, socialmaze_fts. Transfer runner plan encodes 120 off-diagonal comparisons before execution.
- Blockers:
  - Full 120-comparison transfer claim still requires the ALFWorld OOD SkillGen adapter/split contract.

### claim_tau_bench_gate_activated

- Status: `not_reproduced`
- Verification mode: `tau_bench_matrix`
- Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.
- Evidence: tau-Bench official smoke execution completed with skill_status=deprecated, verification_passed=False, train_net_gain=-1. Held-out tau-Bench eval observed baseline=23.3%, skill=23.3%, delta=0.0%, net_gain=0.
- External source candidates:
  - `tau_bench`: sierra-research/tau-bench -> code/official/benchmarks/external/tau-bench
- Blockers:
  - Executed tau-Bench smoke did not support the paper claim: the generated skill failed the internal verification gate or produced no positive held-out skill delta.

### claim_chemllmbench_useful_gains

- Status: `not_reproduced`
- Verification mode: `chemllmbench_matrix`
- Next step: Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; the current executed smoke evidence does not support the claim.
- Evidence: chemllmbench_property_prediction execution status=official_code_eval_completed, verification_passed=False, train_net_gain=0, heldout_delta=0.0%. chemllmbench_yield_prediction execution status=official_code_eval_completed, verification_passed=False, train_net_gain=0, heldout_delta=0.0%.
- External source candidates:
  - `chemllmbench`: ChemFoundationModels/ChemLLMBench -> code/official/external/chemllmbench
- Blockers:
  - Executed ChemLLMBench smoke targets did not show positive skill gains for all prepared subtasks.

### claim_refinement_best_of_k

- Status: `blocked`
- Verification mode: `refinement_trace_analysis`
- Next step: Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan.
- Blockers:
  - Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.
  - Needs full per-round run logs across representative benchmark-model entries.

### claim_token_cost

- Status: `partially_reproduced`
- Verification mode: `token_usage_aggregation`
- Next step: Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required.
- Evidence: Existing smoke token evidence: train=59226, eval=14396. chemllmbench_property_prediction token evidence: train=46661, eval=1514. chemllmbench_yield_prediction token evidence: train=60179, eval=2931. mcp_bench_token token evidence: train=448252, eval=120830. mind2web_token token evidence: train=674323, eval=265899. pubmedqa_token token evidence: train=280169, eval=167834. scienceworld_token token evidence: train=588035, eval=476046. tau_bench_retail token evidence: train=1629346, eval=1569988. Token-log aggregation plan covers Table 4 groups: ScienceWorld, PubMedQA, Mind2Web, MCPBench, tau-Bench. All Table 4 ready token groups were executed at reduced POC scale: mcp_bench_token, mind2web_token, pubmedqa_token, scienceworld_token, tau_bench_retail.
- Blockers:
  - The run uses reduced POC-scale configs, so token-log mechanics are reproduced but the paper's full-scale token totals are not.

### claim_auditable_skill_artifact

- Status: `partially_reproduced`
- Verification mode: `official_code_output_inspection`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Evidence: Existing smoke run produced a skill output directory: artifacts/raw_benchmark_outputs/skillgen_aime_smoke/skill_output/2026-06-02_02-03-02.

## Executable Official-Code Targets

- `skillgen_aime`: data/aime/train.json -> data/aime/test.json (train_n=80, test_n=40)
- `skillgen_mcp_bench_single`: data/mcp_bench/train.json -> data/mcp_bench/test.json (train_n=40, test_n=16)
- `skillgen_mind2web`: data/mind2web/train.json -> data/mind2web/test.json (train_n=100, test_n=100)
- `skillgen_pubmedqa`: data/pubmedqa/train.json -> data/pubmedqa/test.json (train_n=150, test_n=100)
- `skillgen_scienceworld`: data/scienceworld/train.json -> data/scienceworld/test.json (train_n=150, test_n=100)
- `skillgen_socialmaze_fts`: data/socialmaze/train.json -> data/socialmaze/test.json (train_n=60, test_n=50)
- `skillgen_toolbench`: data/toolbench/train.json -> data/toolbench/test.json (train_n=120, test_n=50)
