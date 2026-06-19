# Trace Inventory: gemma3_1b_smoke_trace_20260607

Date completed: 2026-06-07 13:25:57 EDT -0400

## Top-Level Files

- `environment_manifest.md`
- `deviation_note.md`
- `train_attempt1_stdout.txt`
- `train_attempt1_stderr.txt`
- `train_attempt1_command_status.json`
- `train_stdout.txt`
- `train_stderr.txt`
- `train_command_status.json`
- `eval_stdout.txt`
- `eval_stderr.txt`
- `eval_command_status.json`
- `eval_results.json`
- `eval_results.token_usage.json`
- `parsed_metrics.json`
- `solution_validation_result.md`
- `solution_validation_result.json`
- `trace_inventory.md`

## Config

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_1b_smoke_trace_20260607.yaml
```

## Attempt 1 Artifacts

Attempt 1 run id:

```text
artifacts/runs/20260607-113330
```

The attempt reached generation and failed on a non-string `dedup_notes` value.
Its stdout, stderr, and command status were copied to `train_attempt1_*`.

## Successful Rerun Artifacts

Run id:

```text
artifacts/runs/20260607-113617
```

Files:

- `run_metadata.json`
- `checkpoint.json`
- `baseline_failures.jsonl`
- `baseline_successes.jsonl`
- `baseline_trajectories.jsonl`
- `checkpoint_trajectories.jsonl`
- `analysis/skill_analysis.json`
- `analysis/skill_analysis_summary.json`
- `verification/round_1/verification_baseline.jsonl`
- `verification/round_1/verification_with_skill.jsonl`
- `verification/round_1/verification_summary.json`
- `verification/round_1/verification_case_analyses.json`
- `token_usage.json`

## Candidate And Skill

Candidate:

```text
candidates/d3ee4895-eb51-4ca6-b53f-885c6440af9f_gen.json
```

Persisted skill:

```text
skill_output/2026-06-07_11-36-17/d0f2da35-08f1-4bc8-af8a-ed2322c5f402.json
```

Trace link:

```json
{
  "candidate_id": "d3ee4895-eb51-4ca6-b53f-885c6440af9f",
  "skill_id": "d0f2da35-08f1-4bc8-af8a-ed2322c5f402",
  "source_candidate_id": "d3ee4895-eb51-4ca6-b53f-885c6440af9f"
}
```

## Eval Artifacts

- `eval_results.json`
- `eval_results.token_usage.json`
- `eval_results_trajectories/gemma3:1b_baseline.jsonl`
- `eval_results_trajectories/gemma3:1b_with_skill.jsonl`

## Classification

Status: `not_solution_validated`

Reason: train and eval completed, but construction verification failed with
`net_gain=0`, the skill was deprecated, and held-out smoke eval showed no
improvement.
