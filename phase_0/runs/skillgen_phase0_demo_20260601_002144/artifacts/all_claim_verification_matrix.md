# All-Claim Verification Matrix

This matrix separates executable claims from claims that are blocked or not testable with the current official release.

## Status Counts

- `blocked`: 6
- `not_testable`: 4
- `partially_reproduced`: 2

## Claims

### claim_method_paired_intervention

- Status: `partially_reproduced`
- Verification mode: `official_code_structure_and_smoke_output`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Evidence: Existing AIME smoke eval output contains baseline_acc, skill_acc, repair, regression, and net_gain fields.

### claim_table1_average_gains_all_models

- Status: `blocked`
- Verification mode: `full_table1_matrix`
- Next step: Create or approve the required full-run contract, model-route mapping, and API/token budget.
- Evidence: Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- Blockers:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Missing bundled official data for rows: alfworld_iod, alfworld_ood, livecodebench, mcp_bench_all, socialmaze_upi
  - Paper model display names still need exact provider route IDs before unattended execution.
  - Requires API/network/token-spend approval.

### claim_table1_entry_counts

- Status: `blocked`
- Verification mode: `full_table1_matrix`
- Next step: Create or approve the required full-run contract, model-route mapping, and API/token budget.
- Evidence: Official release currently has bundled data for these Table 1 rows: mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts.
- Blockers:
  - Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.
  - Missing bundled official data for rows: alfworld_iod, alfworld_ood, livecodebench, mcp_bench_all, socialmaze_upi
  - Paper model display names still need exact provider route IDs before unattended execution.
  - Requires API/network/token-spend approval.

### claim_table1_alfworld_scienceworld_patterns

- Status: `blocked`
- Verification mode: `full_table1_subset`
- Next step: Create or approve the required full-run contract, model-route mapping, and API/token budget.
- Evidence: ScienceWorld train/test JSON is bundled and can be planned for execution.
- Blockers:
  - ALFWorld IOD/OOD data is not bundled in code/official/data.
  - Requires all eight model routes and API/token-spend approval.

### claim_baseline_generator_comparison

- Status: `not_testable`
- Verification mode: `baseline_generator_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Blockers:
  - Official checkout does not include Trace2Skill, SkillX, EvoSkill, or CoEvoSkills runner implementations.
  - README describes baseline adaptation details in the paper, but no executable baseline-comparison command is present.

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
- Next step: Create or approve the required full-run contract, model-route mapping, and API/token budget.
- Blockers:
  - Official eval_skill.py can evaluate a skill across multiple models, but no transfer-run matrix script is provided.
  - Requires generated source-model skills plus exact provider route IDs for source and evaluator models.
  - Requires API/network/token-spend approval.

### claim_tau_bench_gate_activated

- Status: `not_testable`
- Verification mode: `tau_bench_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Blockers:
  - tau-Bench train/test data is not bundled in code/official/data.
  - README says additional preparation is required.
  - Requires user-simulator setup and API/token-spend approval.

### claim_chemllmbench_useful_gains

- Status: `not_testable`
- Verification mode: `chemllmbench_matrix`
- Next step: Obtain missing official code, data, or scripts; otherwise keep this claim not_testable.
- Blockers:
  - ChemLLMBench train/test data is not bundled in code/official/data.
  - README says additional preparation is required.
  - Requires property/yield split generation and API/token-spend approval.

### claim_refinement_best_of_k

- Status: `blocked`
- Verification mode: `refinement_trace_analysis`
- Next step: Create or approve the required full-run contract, model-route mapping, and API/token budget.
- Blockers:
  - Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.
  - Needs full per-round run logs across representative benchmark-model entries.

### claim_token_cost

- Status: `blocked`
- Verification mode: `token_usage_aggregation`
- Next step: Create or approve the required full-run contract, model-route mapping, and API/token budget.
- Evidence: Existing smoke token evidence: train=56529, eval=14118.
- Blockers:
  - Table 4 requires full token usage logs grouped by benchmark, not the current AIME smoke run.
  - Requires reproducing or obtaining complete training/evaluation token logs.

### claim_auditable_skill_artifact

- Status: `partially_reproduced`
- Verification mode: `official_code_output_inspection`
- Next step: Promote from smoke evidence to full-paper evidence only if the matching full contract is executed.
- Evidence: Existing smoke run produced a skill output directory: artifacts/raw_benchmark_outputs/skillgen_aime_smoke/skill_output/2026-06-01_15-32-00.

## Executable Official-Code Targets

- `skillgen_aime`: data/aime/train.json -> data/aime/test.json (train_n=80, test_n=40)
- `skillgen_mcp_bench_single`: data/mcp_bench/train.json -> data/mcp_bench/test.json (train_n=40, test_n=16)
- `skillgen_mind2web`: data/mind2web/train.json -> data/mind2web/test.json (train_n=100, test_n=100)
- `skillgen_pubmedqa`: data/pubmedqa/train.json -> data/pubmedqa/test.json (train_n=150, test_n=100)
- `skillgen_scienceworld`: data/scienceworld/train.json -> data/scienceworld/test.json (train_n=150, test_n=100)
- `skillgen_socialmaze_fts`: data/socialmaze/train.json -> data/socialmaze/test.json (train_n=60, test_n=50)
- `skillgen_toolbench`: data/toolbench/train.json -> data/toolbench/test.json (train_n=120, test_n=50)
