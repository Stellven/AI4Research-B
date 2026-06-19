# Environment Manifest

Date: 2026-06-07 13:25:57 EDT -0400

Repository:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B
```

## Scope

This is solution validation only. It is not paper reproduction.

## Runtime

- Working directory for benchmark commands:
  `phase_0/runs/skillgen_phase0_thorough_20260602/code/official`
- Model: `gemma3:1b`
- Local endpoint: `http://127.0.0.1:11434/v1`
- Embeddings: deterministic local hash embeddings
- External OpenAI/OpenRouter API keys: explicitly unset for train and eval
- Direct OpenAI fallback: disabled with
  `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`
- Web search: disabled
- Router: disabled
- Max workers: 1

## Local Model Inventory

`ollama list` was blocked in the sandbox but succeeded with approval. Installed
models included `gemma3:1b`, `gemma3:4b`, `gemma3:12b`, `qwen3:4b`,
`qwen3:8b`, and `llama3.1:latest`.

During the run, `ollama ps` reported:

```text
gemma3:1b  1.9 GB  100% GPU  context 32768
```

## Commands

Training command:

```text
.venv/bin/python main.py ../../artifacts/07_configs_and_inputs/smoke_data/mcp_bench_single_train_n4_seed42.json --config ../../artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_1b_smoke_trace_20260607.yaml
```

Eval command:

```text
.venv/bin/python eval_skill.py --skill-repo ../../artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_1b_smoke_trace_20260607/skill_output/2026-06-07_11-36-17 --dataset ../../artifacts/07_configs_and_inputs/smoke_data/mcp_bench_single_test_n4_seed42.json --n 4 --seed 42 --models gemma3:1b --judge-model gemma3:1b --max-workers 1
```

No dependencies were installed. No models were downloaded. No unrelated
processes were stopped.
