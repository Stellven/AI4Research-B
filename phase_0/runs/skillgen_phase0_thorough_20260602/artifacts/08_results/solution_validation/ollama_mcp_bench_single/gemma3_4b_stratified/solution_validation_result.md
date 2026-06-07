# Solution Validation Result: gemma3_4b_stratified

Date completed: 2026-06-06 12:18:48 EDT -0400

Status: `partially_solution_validated`

This run is solution validation only. It is not an original-paper reproduction and does not validate the paper's numerical claims. The run validates that the local Ollama/hash-embedding path and the patched stratified verification sampler can execute end to end and produce durable evidence. The generated skill did not improve held-out evaluation.

## Environment

- Model: `gemma3:4b`
- Local endpoint: `http://127.0.0.1:11434/v1`
- Embeddings: deterministic local hash embeddings
- External OpenAI/OpenRouter API keys: explicitly unset for train and eval commands
- Direct OpenAI fallback: disabled with `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`
- Web search during eval: disabled
- Script execution during eval: disabled/mock

## Command Outcomes

The first non-escalated training attempt failed after 2873 seconds because sandboxed local HTTP access to the Ollama OpenAI-compatible endpoint was denied with `Operation not permitted`. Evidence was preserved in `train_attempt1_stdout.txt`, `train_attempt1_stderr.txt`, and `train_attempt1_command_status.json`.

The primary rerun completed successfully:

- `train_command_status.json`: exit code `0`, runtime `2682` seconds
- `eval_command_status.json`: exit code `0`, runtime `1961` seconds

No unrelated processes were stopped. Post-run `ollama ps` showed `gemma3:4b` loaded at `3.2 GB`, `100% GPU`, context `131072`; `memory_pressure` reported `24%` system-wide memory free.

## Training And Construction Verification

Training dataset: `data/mcp_bench/train.json`

- Instances: 40
- Baseline failures: 5
- Baseline successes: 35
- Failure clusters: 2
- Success clusters: 2
- Contrastive pairs: 4
- Active skill id: `bd029056-5133-4626-b151-3a21e8e67ea2`
- Active skill path: `skill_output/2026-06-06_10-55-11/bd029056-5133-4626-b151-3a21e8e67ea2.json`

Key sampler acceptance criterion passed. The verification sample included baseline failures instead of only success guards:

- Target failures: `call_for_papers_001`, `movie_recommender_001`
- Success guards: `medical_calculator_001`, `nasa_data_000`

Construction verification result:

- Paired cases: 4
- Baseline accuracy: 50.0%
- Skill accuracy: 75.0%
- Repairs: 2
- Regressions: 1
- Net gain: +1
- Passed: true

Trace note: `verification_summary.json` records candidate skill id `8358dd90-a6d9-4306-a03d-51d6c0b0972e`, while the persisted active skill used in held-out eval is `bd029056-5133-4626-b151-3a21e8e67ea2`.

## Held-Out Evaluation

Held-out dataset: `data/mcp_bench/test.json`

- Sample size: 16
- Seed: 42
- Baseline pass count: 16/16
- Skill pass count: 15/16
- Baseline accuracy: 100.0%
- Skill accuracy: 93.8%
- Accuracy delta: -6.2 percentage points
- Repairs: 0
- Regressions: 1
- Net gain: -1
- Regression case: `car_price_evaluator_000` (`baseline_score=0.6833333333333332`, `skill_score=0.10000000000000002`)

Mean judge score also declined on the held-out sample:

- Baseline mean score: 0.6991815476190476
- Skill mean score: 0.6739583333333333
- Score delta: -0.0252232142857143

## Conclusion

The solution-validation infrastructure and sampler fix are validated for this target run: training completed, the sampler selected target failures, construction verification passed, and held-out eval ran with preserved logs and trajectories.

The generated skill is not validated as beneficial on held-out evaluation. The appropriate final status is `partially_solution_validated`, not `solution_validated`.

