# Full Matrix Execution Contract

Status: `blocked_pending_A_B_ready_contracts`

This contract defines how SkillGen Phase 0 should execute and aggregate the full
Table 1 matrix once Group A and Group B provide ready contracts.

## Dependencies

- Group A must provide an ALFWorld IOD/OOD SkillGen adapter and split contract.
- Group B must provide a LiveCodeBench release v6 train/test split contract.
- `artifacts/model_route_mapping.template.json` must resolve the eight Table 1 model routes.
- `artifacts/benchmark_execution_plan.json` must mark every Table 1 row `ready_for_execution`.

## Matrix Shape

- Rows: `alfworld_iod`, `alfworld_ood`, `livecodebench`, `mcp_bench_all`, `mcp_bench_single`, `mind2web`, `pubmedqa`, `scienceworld`, `socialmaze_fts`, `socialmaze_upi`.
- Models: `Gemma-4-26B`, `Llama-3.1-8B`, `Mistral-Nemo`, `Qwen-2.5-7B`, `Claude-Haiku-4.5`, `GPT-5.4-Nano`, `GPT-5.4-Mini`, `Grok-4-Fast`.
- Required entries: `10 rows * 8 models = 80`.

## Execution Manifest

Each Table 1 entry should be represented by one manifest row:

```json
{
  "entry_id": "{table1_row}::{paper_model}",
  "table1_row": "{table1_row}",
  "paper_model": "{paper_model}",
  "provider_route_id": "{provider_route_id}",
  "train_dataset": "code/official/{train_path}",
  "test_dataset": "code/official/{test_path}",
  "config_path": "artifacts/generated_configs/{table1_row}/{model_slug}.yaml",
  "skill_output_dir": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/skill_output",
  "eval_results": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/eval_results.json",
  "eval_trajectories_dir": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/eval_results_trajectories",
  "token_usage": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/eval_results.token_usage.json"
}
```

## Required Result Fields

Every parsed entry must expose:

- `n_instances`
- `baseline_acc`
- `skill_acc`
- `delta_acc`
- `repair`
- `regression`
- `net_gain`

## Aggregation Rules

`claim_table1_average_gains_all_models`:

- Group parsed entries by `paper_model`.
- Average `delta_acc` across all 10 Table 1 rows for each model.
- Compare model-level gains to the paper's reported +3.27 to +10.08 pp range only after all 80 entries are present.

`claim_table1_entry_counts`:

- Classify each `delta_acc` as improved if `> 0`, unchanged if `== 0`, regressed if `< 0`.
- Compare aggregate counts to `50 improved / 25 unchanged / 5 regressed`.
- Do not fill missing rows with smoke-scale or reconstructed-only substitutes.

`claim_table1_alfworld_scienceworld_patterns`:

- ALFWorld count uses `alfworld_iod` and `alfworld_ood` across all eight models, for 16 entries.
- ScienceWorld count uses `scienceworld` across all eight models.
- Compare to `ALFWorld 14/16 improved` and `ScienceWorld 8/8 improved`.

## Completion Standard

This contract is ready to generate or update the execution plan when:

- Group A marks ALFWorld IOD/OOD `ready_for_execution`.
- Group B marks LiveCodeBench `ready_for_execution`.
- All eight model routes are resolved or recorded as explicit deviations.
- The execution manifest has 80 entries with unique output paths.
