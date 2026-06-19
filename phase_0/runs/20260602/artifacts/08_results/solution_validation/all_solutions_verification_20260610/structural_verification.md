# All-Solutions Structural Verification

Date: 2026-06-10

This is solution validation, not paper reproduction.

| Solution | Verification type | Status | Summary |
| --- | --- | --- | --- |
| `alfworld_reconstructed_adapter` | `dataset_contract` | `verified` | Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances. |
| `alfworld_ood_reconstructed_adapter` | `dataset_contract` | `verified` | Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances. |
| `alfworld_reconstructed_adapter` | `adapter_contract_and_code` | `blocked_missing_artifacts` | ALFWorld reconstructed adapter has code, split manifest, run commands, and deviation note. Some required artifacts are missing. |
| `livecodebench_reconstructed_split` | `dataset_contract` | `verified` | Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances. |
| `livecodebench_reconstructed_split` | `split_contract_and_adapter` | `blocked_missing_artifacts` | LiveCodeBench reconstructed split has adapter, manifest, source review, contract, and deviation note. Some required artifacts are missing. |
| `baseline_generator_comparison` | `source_identity_and_adapter_contract` | `blocked_missing_artifacts` | Baseline comparison has public repos, identity review, adapter contract, deviation note, and human approval artifact. Some required artifacts are missing. |
| `reconstructed_ablation` | `ablation_contract` | `blocked_missing_artifacts` | Reconstructed ablation has contract, config matrix, smoke plan, and deviation note. Some required artifacts are missing. |
| `cross_model_transfer` | `transfer_contract` | `blocked_missing_artifacts` | Transfer has runner plan and execution contract. Some required artifacts are missing. |
| `full_matrix_runner` | `full_matrix_contract_and_state` | `blocked_missing_artifacts` | Full-matrix solution has execution contract, runner state, and observed-entry accounting. Some required artifacts are missing. |
| `trace_retention` | `trace_contract_and_existing_evidence` | `blocked_missing_artifacts` | Trace-retention solution has checklist, Figure 7 contract, and existing traceability audit. Some required artifacts are missing. |
| `provider_and_cost_governance` | `provider_cost_policy` | `blocked_missing_artifacts` | Provider/cost solution has provider resolution status, budget policy, and cost governance note. Some required artifacts are missing. |
| `alfworld_iod_local_llm_smoke` | `local_llm_smoke_preparation` | `prepared_for_local_llm_smoke` | Prepared local Ollama smoke assets for alfworld_iod with model gemma3:1b. |
| `alfworld_ood_local_llm_smoke` | `local_llm_smoke_preparation` | `prepared_for_local_llm_smoke` | Prepared local Ollama smoke assets for alfworld_ood with model gemma3:1b. |
| `livecodebench_local_llm_smoke` | `local_llm_smoke_preparation` | `prepared_for_local_llm_smoke` | Prepared local Ollama smoke assets for livecodebench with model gemma3:1b. |

## Evidence Details

### alfworld_reconstructed_adapter / dataset_contract

- Status: `verified`
- Summary: Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances.
- Evidence:
  - `phase_0/runs/20260602/code/official/data/alfworld_iod/train.json (500 instances)`
  - `phase_0/runs/20260602/code/official/data/alfworld_iod/test.json (150 instances)`

### alfworld_ood_reconstructed_adapter / dataset_contract

- Status: `verified`
- Summary: Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances.
- Evidence:
  - `phase_0/runs/20260602/code/official/data/alfworld_ood/train.json (500 instances)`
  - `phase_0/runs/20260602/code/official/data/alfworld_ood/test.json (255 instances)`

### alfworld_reconstructed_adapter / adapter_contract_and_code

- Status: `blocked_missing_artifacts`
- Summary: ALFWorld reconstructed adapter has code, split manifest, run commands, and deviation note. Some required artifacts are missing.
- Evidence:
  - `phase_0/runs/20260602/code/official/benchmarks/alfworld_adapter.py`
  - `phase_0/runs/20260602/code/official/benchmarks/alfworld_grader.py`
  - `phase_0/runs/20260602/code/official/scripts/prepare_alfworld.py`
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/alfworld_split_manifest_seed42.md`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/alfworld_run_commands.md`
  - `phase_0/runs/20260602/artifacts/09_safety_and_deviations/alfworld_adapter_deviation_note.md`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### livecodebench_reconstructed_split / dataset_contract

- Status: `verified`
- Summary: Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances.
- Evidence:
  - `phase_0/runs/20260602/code/official/data/livecodebench/train_release_v6_n50_seed42.json (50 instances)`
  - `phase_0/runs/20260602/code/official/data/livecodebench/test_release_v6_n150_seed42.json (150 instances)`

### livecodebench_reconstructed_split / split_contract_and_adapter

- Status: `blocked_missing_artifacts`
- Summary: LiveCodeBench reconstructed split has adapter, manifest, source review, contract, and deviation note. Some required artifacts are missing.
- Evidence:
  - `phase_0/runs/20260602/code/official/benchmarks/livecodebench_adapter.py`
  - `phase_0/runs/20260602/code/official/data/livecodebench/split_release_v6_n50_n150_seed42_manifest.json`
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/03_code_and_sources/livecodebench_source_review.md`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/livecodebench_split_contract.md`
  - `phase_0/runs/20260602/artifacts/09_safety_and_deviations/livecodebench_deviation_note.md`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### baseline_generator_comparison / source_identity_and_adapter_contract

- Status: `blocked_missing_artifacts`
- Summary: Baseline comparison has public repos, identity review, adapter contract, deviation note, and human approval artifact. Some required artifacts are missing.
- Evidence:
  - `phase_0/runs/20260602/code/official/baselines/Trace2Skill/README.md`
  - `phase_0/runs/20260602/code/official/baselines/SkillX/README.md`
  - `phase_0/runs/20260602/code/official/baselines/EvoSkill/README.md`
  - `phase_0/runs/20260602/code/official/baselines/CoEvoSkills/README.md`
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/baseline_source_identity_review.json`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/baseline_single_skill_adapter_contract.json`
  - `phase_0/runs/20260602/artifacts/09_safety_and_deviations/baseline_deviation_note.md`
  - `phase_0/runs/20260602/artifacts/baseline_source_identity_human_review.json`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### reconstructed_ablation / ablation_contract

- Status: `blocked_missing_artifacts`
- Summary: Reconstructed ablation has contract, config matrix, smoke plan, and deviation note. Some required artifacts are missing.
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/reconstructed_ablation_contract.json`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/ablation_config_matrix.json`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/ablation_smoke_plan.json`
  - `phase_0/runs/20260602/artifacts/09_safety_and_deviations/ablation_deviation_note.md`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### cross_model_transfer / transfer_contract

- Status: `blocked_missing_artifacts`
- Summary: Transfer has runner plan and execution contract. Some required artifacts are missing.
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/transfer_runner_plan.json`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/transfer_execution_contract.json`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### full_matrix_runner / full_matrix_contract_and_state

- Status: `blocked_missing_artifacts`
- Summary: Full-matrix solution has execution contract, runner state, and observed-entry accounting. Some required artifacts are missing.
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/full_matrix_execution_contract.json`
  - `phase_0/runs/20260602/artifacts/08_results/full_matrix/full_matrix_runner_state.json`
  - `phase_0/runs/20260602/artifacts/08_results/full_matrix/observed_entries.json`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### trace_retention / trace_contract_and_existing_evidence

- Status: `blocked_missing_artifacts`
- Summary: Trace-retention solution has checklist, Figure 7 contract, and existing traceability audit. Some required artifacts are missing.
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/per_round_trace_retention_checklist.json`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/figure7_trace_extraction_contract.json`
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/overnight_verification_20260607/skill_traceability_audit.md`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### provider_and_cost_governance / provider_cost_policy

- Status: `blocked_missing_artifacts`
- Summary: Provider/cost solution has provider resolution status, budget policy, and cost governance note. Some required artifacts are missing.
- Missing/problems:
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/provider_resolution_status.json`
  - `phase_0/runs/20260602/artifacts/06_plans_and_contracts/full_matrix_execution_budget_policy.json`
  - `phase_0/runs/20260602/artifacts/09_safety_and_deviations/full_matrix_cost_governance.md`
- Next action: Create or restore missing artifacts, then rerun this verifier.

### alfworld_iod_local_llm_smoke / local_llm_smoke_preparation

- Status: `prepared_for_local_llm_smoke`
- Summary: Prepared local Ollama smoke assets for alfworld_iod with model gemma3:1b.
- Evidence:
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_iod_train_n4.json`
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_iod_test_n2.json`
  - `phase_0/runs/20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610/alfworld_iod_gemma3_1b.yaml`
- Next action: Run main.py with phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_iod_train_n4.json and phase_0/runs/20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610/alfworld_iod_gemma3_1b.yaml, then eval_skill.py on phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_iod_test_n2.json.

### alfworld_ood_local_llm_smoke / local_llm_smoke_preparation

- Status: `prepared_for_local_llm_smoke`
- Summary: Prepared local Ollama smoke assets for alfworld_ood with model gemma3:1b.
- Evidence:
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_ood_train_n4.json`
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_ood_test_n2.json`
  - `phase_0/runs/20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610/alfworld_ood_gemma3_1b.yaml`
- Next action: Run main.py with phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_ood_train_n4.json and phase_0/runs/20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610/alfworld_ood_gemma3_1b.yaml, then eval_skill.py on phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/alfworld_ood_test_n2.json.

### livecodebench_local_llm_smoke / local_llm_smoke_preparation

- Status: `prepared_for_local_llm_smoke`
- Summary: Prepared local Ollama smoke assets for livecodebench with model gemma3:1b.
- Evidence:
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/livecodebench_train_n3.json`
  - `phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/livecodebench_test_n1.json`
  - `phase_0/runs/20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610/livecodebench_gemma3_1b.yaml`
- Next action: Run main.py with phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/livecodebench_train_n3.json and phase_0/runs/20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610/livecodebench_gemma3_1b.yaml, then eval_skill.py on phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/smoke_data/livecodebench_test_n1.json.
