# Full Matrix Observed Entries

Status: `incomplete_single_entry_observed`

This artifact records executed Table 1 full-matrix entries only. It is not the complete 80-entry SkillGen Table 1 matrix.

## Limitations

- The observed entry used a reconstructed low-cost config rather than the paper's full official config.
- The config reduced `max_refine_rounds`, workers, clustering breadth, and verification sample size for overnight cost control.
- A positive result here could support partial evidence only.
- This observed entry is negative, so it does not advance the aggregate Table 1 claims.

## Observed Entries

| Entry | Status | Train/Test N | Construction Result | Held-Out Result | Evidence |
| --- | --- | ---: | --- | --- | --- |
| `mcp_bench_single::openai/gpt-5.4-nano` | `not_reproduced` | 40 / 16 | baseline `0.75`, skill `0.25`, net gain `-2`, gate passed `false` | baseline `0.8125`, skill `0.8125`, delta `0.0`, net gain `0` | `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/eval_results.json` |

## Claim Impact

- `claim_table1_average_gains_all_models`: remains `blocked` because only 1 of 80 required entries is observed.
- `claim_table1_entry_counts`: remains `blocked` because the paper count claim requires all 80 entries.
- This single entry is negative evidence for `mcp_bench_single::GPT-5.4-Nano`, not evidence for full Table 1 reproduction.

## Raw Evidence

- Training stdout: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/train_direct_stdout.txt`
- Training stderr: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/train_direct_stderr.txt`
- Run artifacts: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/artifacts/runs/20260604-092116/`
- Skill output: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/skill_output/2026-06-04_09-21-16/`
- Eval results: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/eval_results.json`
- Eval token usage: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/eval_results.token_usage.json`
- Eval trajectories: `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/eval_results_trajectories/`
