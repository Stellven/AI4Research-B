# Trace Inventory

## Run Scope

- Benchmark: `mcp_bench_single`
- Model: `gemma3:4b`
- Training run timestamp: `20260605-092622`
- Skill output timestamp: `2026-06-05_09-26-22`
- Status: `not_solution_validated`

## Config

- Local Ollama config:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_4b.yaml`

## Probes

- Ollama API probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/ollama_probe_stdout.txt`
- OpenAI-compatible chat probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/chat_probe_stdout.txt`
- SkillGen wrapper probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/skillgen_wrapper_probe_stdout.txt`
- Hash embedding probe:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/embedding_probe_stdout.txt`

## Training Evidence

- Train stdout:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/train_stdout.txt`
- Train stderr:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/train_stderr.txt`
- Train command status:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/train_command_status.json`
- Run metadata:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/run_metadata.json`
- Baseline trajectories:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/baseline_trajectories.jsonl`
- Baseline successes:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/baseline_successes.jsonl`
- Baseline failures:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/baseline_failures.jsonl`
- Token usage:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/token_usage.json`

## Induction And Candidate Traces

- Skill analysis:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/analysis/skill_analysis.json`
- Skill analysis summary:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/analysis/skill_analysis_summary.json`
- Candidate skill generation artifact:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/candidates/79992cc8-a239-457d-be69-d994181b213e_gen.json`

## Skill And Verification Traces

- Skill repo:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/skill_output/2026-06-05_09-26-22`
- Skill artifact:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/skill_output/2026-06-05_09-26-22/795eee49-f44e-4d43-bd1b-af1406f7a3bc.json`
- Verification baseline trajectories:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/verification/round_1/verification_baseline.jsonl`
- Verification with-skill trajectories:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/verification/round_1/verification_with_skill.jsonl`
- Verification summary:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/artifacts/runs/20260605-092622/verification/round_1/verification_summary.json`
- Verification outcome: failed gate, skill deprecated, net_gain 0.

## Held-Out Eval Traces

- Eval stdout:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_stdout.txt`
- Eval stderr:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_stderr.txt`
- Eval command status:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_command_status.json`
- Eval result:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_results.json`
- Eval token usage:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_results.token_usage.json`
- Eval trajectories:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_results_trajectories/`

## Counts Verified

- `baseline_trajectories.jsonl`: 40 rows
- `baseline_successes.jsonl`: 35 rows
- `baseline_failures.jsonl`: 5 rows
- Construction verification paired rows: 4
- Held-out paired rows: 16
