# Trace Inventory

## Run Scope

- Benchmark: `mcp_bench_single`
- Model: `gemma3:12b`
- Successful training run timestamp: `20260604-225535`
- Successful skill output timestamp: `2026-06-04_22-55-35`
- Status: `inconclusive` for SkillGen improvement because no skill was generated.

## Config

- Local Ollama config:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_12b.yaml`

## Probes

- Ollama API probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/ollama_probe_stdout.txt`
- OpenAI-compatible chat probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/chat_probe_stdout.txt`
- SkillGen wrapper probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/skillgen_wrapper_probe_stdout.txt`
- Hash embedding probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/embedding_probe_stdout.txt`

## Successful Training Evidence

- Train stdout:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/train_stdout.txt`
- Train stderr:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/train_stderr.txt`
- Train command status:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/train_command_status.json`
- Run metadata:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/artifacts/runs/20260604-225535/run_metadata.json`
- All baseline trajectories:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/artifacts/runs/20260604-225535/baseline_trajectories.jsonl`
- Baseline successes:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/artifacts/runs/20260604-225535/baseline_successes.jsonl`
- Baseline failures:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/artifacts/runs/20260604-225535/baseline_failures.jsonl`
- Trajectory checkpoint:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/artifacts/runs/20260604-225535/checkpoint_trajectories.jsonl`

## Skill And Verification Traces

- Expected skill repository:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/skill_output/2026-06-04_22-55-35`
- Skill repository status: directory exists but contains zero files.
- Verification summary: unavailable. Stage 2 and Stage 3 did not run because Stage 1 found 0 baseline failures.
- Candidate skill files: unavailable. No skill was generated.
- Per-round verification traces: unavailable. No verification round ran.

## Held-Out Eval Traces

- Eval stdout placeholder:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/eval_stdout.txt`
- Eval stderr placeholder:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/eval_stderr.txt`
- Eval result placeholder:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/eval_results.json`

## Interrupted Or Superseded Attempts

- First `gemma3:12b` attempt:
  - `train_timeout_180s_stdout.txt`
  - `train_timeout_180s_stderr.txt`
  - `train_timeout_180s_command_status.json`
  - `train_timeout_180s_attempt_note.md`
- Earlier pre-rerun artifact directory with metadata only:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/artifacts/runs/20260604-165912`

## Counts Verified

- `baseline_trajectories.jsonl`: 40 rows
- `baseline_successes.jsonl`: 40 rows
- `baseline_failures.jsonl`: 0 rows
