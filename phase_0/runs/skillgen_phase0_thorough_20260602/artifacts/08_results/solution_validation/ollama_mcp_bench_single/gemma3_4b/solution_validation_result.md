# Ollama MCP Bench Single Solution Validation

## Verdict

Status: not_solution_validated

One-sentence reason: The local run completed train and held-out eval, but the generated skill was deprecated after construction verification produced net_gain 0, and held-out eval reported no improvement.

## What Was Tested

- Benchmark: `mcp_bench_single`
- Model: `gemma3:4b`
- Dataset: `data/mcp_bench/train.json` for training; `data/mcp_bench/test.json` for held-out eval.
- Train size: 40
- Test size: 16
- SkillGen rounds: 1 configured and 1 executed.
- Embedding mode: local deterministic hash fallback.
- External API usage: OpenAI and OpenRouter keys were explicitly unset for probes, training, and eval; chat was routed to local Ollama.

## Deviations From Paper Reproduction

- This was not an original-paper reproduction and does not test the paper's original model suite, embedding model, full benchmark matrix, or reported numerical claims.
- Official chat routing was redirected to local Ollama through the OpenAI-compatible endpoint at `http://127.0.0.1:11434/v1`.
- External OpenAI/OpenRouter chat was disabled with `env -u OPENAI_API_KEY -u OPENROUTER_API_KEY` and `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.
- OpenAI embeddings were replaced by an env-gated deterministic hash embedding fallback.
- `OPENROUTER_HTTP_TIMEOUT=600` was used for local long generations.
- `gemma3:4b` was used after `gemma3:12b` solved all 40 training items and produced no skill.

## Commands Run

### Probe

```bash
curl http://127.0.0.1:11434/api/tags
```

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:4b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python <chat_probe>
```

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:4b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python <skillgen_wrapper_and_embedding_probes>
```

### Train

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY OPENROUTER_HTTP_TIMEOUT=600 SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:4b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python main.py data/mcp_bench/train.json --config "../../artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_4b.yaml"
```

### Eval

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY OPENROUTER_HTTP_TIMEOUT=600 SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:4b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python eval_skill.py --skill-repo "../../artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/skill_output/2026-06-05_09-26-22" --dataset data/mcp_bench/test.json --n 16 --seed 42 --models "gemma3:4b" --judge-model "gemma3:4b" --max-workers 1 --output "../../artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/eval_results.json"
```

## Results

| Split | Baseline acc | Skill acc | Delta | Net gain |
| --- | ---: | ---: | ---: | ---: |
| Construction | 1.000 | 1.000 | 0.000 | 0 |
| Held-out | 1.000 | 1.000 | 0.000 | 0 |

Additional training baseline: 35/40 passed before skill generation, leaving 5 failures for induction.

## Trace Preservation

- Config: `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_4b.yaml`
- Raw logs: `train_stdout.txt`, `train_stderr.txt`, `eval_stdout.txt`, `eval_stderr.txt`, and probe logs in this directory.
- Skill repo: `skill_output/2026-06-05_09-26-22`
- Verification summary: `artifacts/runs/20260605-092622/verification/round_1/verification_summary.json`
- Eval result: `eval_results.json`
- Per-round traces: `artifacts/runs/20260605-092622/verification/round_1/`

## Interpretation

This run validates that the local Ollama execution path can exercise the full SkillGen loop: baseline collection, induction, candidate generation, verification, skill artifact preservation, held-out eval, and trace preservation all completed without external LLM APIs.

It does not validate the solution's effectiveness on this run. The generated skill was rejected/deprecated because construction verification had no positive net gain. Held-out eval then skipped true skill-condition execution and reported skill equal to baseline, yielding net_gain 0.

One important limitation is that construction verification sampled 0 baseline failures and 4 success guards even though the training baseline had 5 failures. That means the verification gate did not test repair behavior on the observed failures.

## Remaining Issues

- Fix or inspect verification sampling so observed baseline failures are included in the construction verification target set.
- Re-run `gemma3:4b` after sampling is fixed, or run another seed/model where verification target failures are selected.
- Hash embeddings remain a reconstructed deviation from the paper setup.
- Full-matrix and cross-benchmark validation remain untested.
