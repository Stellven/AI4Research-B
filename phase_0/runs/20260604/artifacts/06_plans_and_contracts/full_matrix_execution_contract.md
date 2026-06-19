# Full Matrix Execution Contract

Full Table 1 execution and aggregation contract for SkillGen Phase 0

Status: `authorized_for_planned_execution_openai_first_waiting_non_openai_provider_routes`
Pre-execution human gate: `not_required_for_planned_entries`
Authorization artifact: `artifacts/05_reviews_and_approval/full_matrix_execution_authorization.md`
Post-run evidence validation required: `True`
Ready entries: `80` of `80`
OpenAI routes immediately attemptable: `20`
Non-OpenAI routes require technical provider availability: `60`

## Dependencies

- Group `A`: `logs/phase_0_parallel_20260604/A_alfworld/alfworld_adapter_contract.md` - ALFWorld IOD/OOD rows need a SkillGen adapter and paper-matching split before the 80-entry matrix is complete.
- Group `B`: `logs/phase_0_parallel_20260604/B_livecodebench/livecodebench_split_contract.md` - LiveCodeBench needs an approved train/test split contract before its eight model entries can be counted.

## Table 1 Rows

| Row | Dataset status | Train/Test | Execution notes |
| --- | --- | --- | --- |
| `alfworld_iod` | `ready_for_reconstructed_execution` | `data/alfworld_iod/train.json / data/alfworld_iod/test.json` | authorized reconstructed execution; must label results and validate evidence after run.; Required label: canonical ALFWorld data + reconstructed SkillGen offline-plan adapter. |
| `alfworld_ood` | `ready_for_reconstructed_execution` | `data/alfworld_ood/train.json / data/alfworld_ood/test.json` | authorized reconstructed execution; must label results and validate evidence after run.; Required label: canonical ALFWorld data + reconstructed SkillGen offline-plan adapter. |
| `livecodebench` | `ready_for_execution` | `data/livecodebench/train_release_v6_n50_seed42.json / data/livecodebench/test_release_v6_n150_seed42.json` | No benchmark target plan exists for this Table 1 row. |
| `mcp_bench_all` | `ready_for_execution` | `data/mcp_bench_all/train_all_n40_seed42.json / data/mcp_bench_all/test_all_n16_seed42.json` | No benchmark target plan exists for this Table 1 row. |
| `mcp_bench_single` | `ready_for_execution` | `data/mcp_bench/train.json / data/mcp_bench/test.json` | No benchmark target plan exists for this Table 1 row. |
| `mind2web` | `ready_for_execution` | `data/mind2web/train.json / data/mind2web/test.json` | No benchmark target plan exists for this Table 1 row. |
| `pubmedqa` | `ready_for_execution` | `data/pubmedqa/train.json / data/pubmedqa/test.json` | No benchmark target plan exists for this Table 1 row. |
| `scienceworld` | `ready_for_execution` | `data/scienceworld/train.json / data/scienceworld/test.json` | No benchmark target plan exists for this Table 1 row. |
| `socialmaze_fts` | `ready_for_execution` | `data/socialmaze/train.json / data/socialmaze/test.json` | No benchmark target plan exists for this Table 1 row. |
| `socialmaze_upi` | `ready_for_execution` | `data/socialmaze_upi/train_n60_seed42.json / data/socialmaze_upi/test_n50_seed42.json` | No benchmark target plan exists for this Table 1 row. |

## Aggregation Rules

- `claim_table1_average_gains_all_models`: For each paper model, average delta_acc across the 10 Table 1 rows after all 80 entries are present.
- `claim_table1_entry_counts`: Classify each of the 80 delta_acc values as improved if > 0, unchanged if == 0, and regressed if < 0; compare counts to 50/25/5.
- `claim_table1_alfworld_scienceworld_patterns`: Count positive delta_acc for ALFWorld IOD/OOD across 16 entries and ScienceWorld across 8 entries; compare to 14/16 and 8/8.

## Required Result Fields

- `n_instances`
- `baseline_acc`
- `skill_acc`
- `delta_acc`
- `repair`
- `regression`
- `net_gain`
