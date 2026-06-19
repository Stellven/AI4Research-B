# Trace Inventory: gemma3_4b_stratified

Date completed: 2026-06-06 12:18:48 EDT -0400

## Required Top-Level Artifacts

- `environment_manifest.md`: present; includes pre-run and post-run environment notes.
- `deviation_note.md`: present; records local Ollama/hash-embedding deviations from paper reproduction.
- `ollama_probe_stdout.txt`: present.
- `chat_probe_stdout.txt`: present.
- `embedding_probe_stdout.txt`: present.
- `skillgen_wrapper_probe_stdout.txt`: present.
- `sampling_fix_verification_note.md`: present.
- `train_stdout.txt`: present; successful escalated primary training rerun.
- `train_stderr.txt`: present; successful escalated primary training rerun progress output.
- `train_command_status.json`: present; exit code `0`, runtime `2682` seconds.
- `eval_stdout.txt`: present; held-out A/B evaluation report.
- `eval_stderr.txt`: present; held-out eval progress output.
- `eval_command_status.json`: present; exit code `0`, runtime `1961` seconds.
- `eval_results.json`: present; held-out summary metrics.
- `eval_results.token_usage.json`: present; held-out token accounting.
- `parsed_metrics.json`: present; consolidated parsed metrics and classification.
- `solution_validation_result.md`: present; narrative result.
- `solution_validation_result.json`: present; machine-readable result.
- `trace_inventory.md`: present; this inventory.

## Preserved Failed Attempt Evidence

- `train_attempt1_stdout.txt`: first training attempt stdout.
- `train_attempt1_stderr.txt`: first training attempt stderr.
- `train_attempt1_command_status.json`: first training attempt exit code `1`, runtime `2873` seconds.

The first attempt is preserved because it is evidence of sandboxed local HTTP restrictions. The successful rerun used the same local Ollama configuration outside that sandbox restriction.

## Training Run Artifacts

Base run path:

```text
artifacts/runs/20260606-105511
```

Files:

- `run_metadata.json`: dataset, model, and pipeline metadata.
- `checkpoint.json`: final pipeline checkpoint.
- `baseline_failures.jsonl`: 5 baseline failure trajectories.
- `baseline_successes.jsonl`: 35 baseline success trajectories.
- `baseline_trajectories.jsonl`: baseline trajectory set.
- `checkpoint_trajectories.jsonl`: checkpoint trajectory set.
- `analysis/skill_analysis.json`: full induction analysis.
- `analysis/skill_analysis_summary.json`: summarized induction analysis.
- `verification/round_1/verification_baseline.jsonl`: construction verification baseline outputs.
- `verification/round_1/verification_with_skill.jsonl`: construction verification skill outputs.
- `verification/round_1/verification_summary.json`: construction verification metrics and case outcomes.
- `verification/round_1/verification_case_analyses.json`: verification case analyst output.
- `token_usage.json`: training token accounting.

## Skill Artifacts

Candidate generated during round 1:

```text
candidates/8358dd90-a6d9-4306-a03d-51d6c0b0972e_gen.json
```

Persisted active skill repo:

```text
skill_output/2026-06-06_10-55-11
```

Files:

- `skill_output/2026-06-06_10-55-11/bd029056-5133-4626-b151-3a21e8e67ea2.json`: active skill used by held-out eval.
- `skill_output/2026-06-06_10-55-11/skill_analysis.json`: copied skill analysis.
- `skill_output/2026-06-06_10-55-11/skill_analysis_summary.json`: copied skill analysis summary.

Trace note: `verification_summary.json` records the candidate id `8358dd90-a6d9-4306-a03d-51d6c0b0972e`; `eval_results.json` records the persisted active id `bd029056-5133-4626-b151-3a21e8e67ea2`.

## Held-Out Eval Artifacts

Top-level files:

- `eval_results.json`: held-out A/B summary.
- `eval_results.token_usage.json`: held-out token usage.
- `eval_stdout.txt`: report text.
- `eval_stderr.txt`: progress output.
- `eval_command_status.json`: command status.

Trajectory files:

```text
eval_results_trajectories/gemma3:4b_baseline.jsonl
eval_results_trajectories/gemma3:4b_with_skill.jsonl
```

Held-out result summary:

- Baseline accuracy: 100.0% over 16/16
- Skill accuracy: 93.8% over 15/16
- Repairs: 0
- Regressions: 1
- Net gain: -1

## Classification

Final status: `partially_solution_validated`

Reason: local execution, sampler behavior, construction verification, and held-out evaluation all produced durable artifacts. The generated skill did not improve held-out performance, so this cannot be classified as `solution_validated`.
