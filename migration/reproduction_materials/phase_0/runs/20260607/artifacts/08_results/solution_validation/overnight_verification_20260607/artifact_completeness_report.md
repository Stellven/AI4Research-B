# Artifact Completeness Report

Date: 2026-06-07 01:20:07 EDT -0400

Root:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single
```

## Summary

| Directory | Completeness | Result status | Missing required artifacts | Notes |
|---|---:|---|---:|---|
| `gemma3_12b` | partial | `inconclusive` | 1 | Training completed, but train baseline was 40/40, so no skill was generated and held-out skill eval was not meaningful. |
| `gemma3_4b` | complete | `not_solution_validated` | 0 | Complete pre-fix package. It exposed that construction verification sampled zero baseline failures. |
| `gemma3_4b_stratified` | complete | `partially_solution_validated` | 0 | Complete post-fix package. Sampler and construction verification worked; held-out eval regressed by one case. |
| `llama3.1_latest` | partial | `failed_to_run` | 11 | Probe files and aborted/stalled notes exist, but no canonical train/eval result package exists. |
| `llama3.1_latest_ctx8192` | partial | `failed_to_run` | 8 | Training started and exited 143 after 605 seconds; no held-out eval package exists. |
| `qwen3_8b` | partial | `failed_to_run` | 8 | Training started and exited 143 after 1629 seconds; no held-out eval package exists. |

An additional directory, `gemma3_1b_smoke`, exists but was not in the requested checklist. It contains only `deviation_note.md` and is not treated as a complete validation package.

## Required Artifact Checklist

Expected files:

```text
environment_manifest.md
deviation_note.md
ollama_probe_stdout.txt
chat_probe_stdout.txt
embedding_probe_stdout.txt
skillgen_wrapper_probe_stdout.txt
train_stdout.txt
train_stderr.txt
train_command_status.json
eval_stdout.txt
eval_stderr.txt
eval_command_status.json
eval_results.json
parsed_metrics.json
solution_validation_result.md
solution_validation_result.json
trace_inventory.md
```

## Directory Details

### `gemma3_12b`

Missing:

```text
eval_command_status.json
```

Classification: `partial` / `inconclusive`

Evidence: `solution_validation_result.json` reports training exit code `0`,
runtime `5105` seconds, `40` baseline successes, `0` baseline failures, and no
generated skill. `eval_results.json` exists as a placeholder because held-out
skill eval had no skill repository to test.

### `gemma3_4b`

Missing: none

Classification: `complete` / `not_solution_validated`

Evidence: `solution_validation_result.json` reports train and held-out eval exit
code `0`, but the generated skill was deprecated. Construction verification had
`target_fail_count=0`, `net_gain=0`, and `passed=false`, which is the sampling
bug fixed by the stratified rerun.

### `gemma3_4b_stratified`

Missing: none

Classification: `complete` / `partially_solution_validated`

Evidence: `solution_validation_result.json` reports successful train and eval.
Construction verification selected two baseline failures and two success guards,
passed with `net_gain=1`, and held-out eval completed with `net_gain=-1`.

### `llama3.1_latest`

Missing:

```text
train_stdout.txt
train_stderr.txt
train_command_status.json
eval_stdout.txt
eval_stderr.txt
eval_command_status.json
eval_results.json
parsed_metrics.json
solution_validation_result.md
solution_validation_result.json
trace_inventory.md
```

Classification: `partial` / `failed_to_run`

Evidence: the directory contains `train_resource_stalled_*`,
`train_aborted_*`, `resource_stalled_attempt_note.md`, and
`aborted_attempt_note.md`, but no canonical completed train/eval package.

### `llama3.1_latest_ctx8192`

Missing:

```text
eval_stdout.txt
eval_stderr.txt
eval_command_status.json
eval_results.json
parsed_metrics.json
solution_validation_result.md
solution_validation_result.json
trace_inventory.md
```

Classification: `partial` / `failed_to_run`

Evidence: `train_command_status.json` reports exit code `143` and runtime `605`
seconds. Logs show baseline collection reached only 5/40 before shutdown.

### `qwen3_8b`

Missing:

```text
eval_stdout.txt
eval_stderr.txt
eval_command_status.json
eval_results.json
parsed_metrics.json
solution_validation_result.md
solution_validation_result.json
trace_inventory.md
```

Classification: `partial` / `failed_to_run`

Evidence: `train_command_status.json` reports exit code `143` and runtime
`1629` seconds. Logs show baseline collection reached only 1/40 before
shutdown.
