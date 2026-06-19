# Benchmark Execution Plan

Execution contract for actionable SkillGen blocked benchmark tests

Status: `ready_for_execution_where_structural_contract_exists`
Storage rule: All generated configs, outputs, cloned sources, caches, and logs must remain inside this run directory.

## Status Counts

- `ready_for_execution`: 11
- `ready_for_reconstructed_execution`: 2

## Table 1 Coverage

- Structurally ready rows: `livecodebench, mcp_bench_all, mcp_bench_single, mind2web, pubmedqa, scienceworld, socialmaze_fts, socialmaze_upi`
- Structurally ready entries: `64` of `80`

## Targets

| Target | Status | Train/Test | Main blockers |
| --- | --- | --- | --- |
| `alfworld_iod` | `ready_for_reconstructed_execution` | `data/alfworld_iod/train.json / data/alfworld_iod/test.json` | Reconstructed ALFWorld offline-plan adapter data is present and load-smoked; full execution still requires human approval of the deviation label, model route, cost, and trace-retention policy. |
| `alfworld_ood` | `ready_for_reconstructed_execution` | `data/alfworld_ood/train.json / data/alfworld_ood/test.json` | Reconstructed ALFWorld offline-plan adapter data is present and load-smoked; full execution still requires human approval of the deviation label, model route, cost, and trace-retention policy. |
| `livecodebench` | `ready_for_execution` | `data/livecodebench/train_release_v6_n50_seed42.json / data/livecodebench/test_release_v6_n150_seed42.json` | none |
| `mcp_bench_all` | `ready_for_execution` | `data/mcp_bench_all/train_all_n40_seed42.json / data/mcp_bench_all/test_all_n16_seed42.json` | none |
| `mcp_bench_single` | `ready_for_execution` | `data/mcp_bench/train.json / data/mcp_bench/test.json` | none |
| `mind2web` | `ready_for_execution` | `data/mind2web/train.json / data/mind2web/test.json` | none |
| `pubmedqa` | `ready_for_execution` | `data/pubmedqa/train.json / data/pubmedqa/test.json` | none |
| `scienceworld` | `ready_for_execution` | `data/scienceworld/train.json / data/scienceworld/test.json` | none |
| `socialmaze_fts` | `ready_for_execution` | `data/socialmaze/train.json / data/socialmaze/test.json` | none |
| `socialmaze_upi` | `ready_for_execution` | `data/socialmaze_upi/train_n60_seed42.json / data/socialmaze_upi/test_n50_seed42.json` | none |
| `tau_bench_retail` | `ready_for_execution` | `data/tau_bench/train_retail_n30_seed42.json / data/tau_bench/test_retail_n30_seed42.json` | none |
| `chemllmbench_property_prediction` | `ready_for_execution` | `data/chemllmbench/property_prediction_train.json / data/chemllmbench/property_prediction_test.json` | none |
| `chemllmbench_yield_prediction` | `ready_for_execution` | `data/chemllmbench/yield_prediction_train.json / data/chemllmbench/yield_prediction_test.json` | none |
