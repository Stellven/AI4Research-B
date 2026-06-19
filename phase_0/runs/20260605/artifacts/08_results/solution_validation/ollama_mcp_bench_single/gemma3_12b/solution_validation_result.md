# Ollama MCP Bench Single Solution Validation

## Verdict

Status: inconclusive

One-sentence reason: The local Ollama run completed training and produced parseable evidence, but `gemma3:12b` achieved 40/40 baseline successes, so SkillGen produced no skill and held-out skill evaluation could not be run.

## What Was Tested

- Benchmark: `mcp_bench_single`
- Model: `gemma3:12b`
- Dataset: `data/mcp_bench/train.json` for training; `data/mcp_bench/test.json` was reserved for held-out eval but not executed.
- Train size: 40
- Test size: 16 requested, 0 executed
- SkillGen rounds: configured `max_refine_rounds=1`, but 0 generation/refinement rounds executed because there were no baseline failures.
- Embedding mode: local deterministic hash fallback, configured but not exercised by induction because Stage 2 did not run.
- External API usage: OpenAI and OpenRouter keys were explicitly unset for probes and training; chat was routed to local Ollama.

## Deviations From Paper Reproduction

- This was not an original-paper reproduction and does not test the paper's original model suite, embedding model, full benchmark matrix, or reported numerical claims.
- Official chat routing was redirected to local Ollama through the OpenAI-compatible endpoint at `http://127.0.0.1:11434/v1`.
- External OpenAI/OpenRouter chat was disabled with `env -u OPENAI_API_KEY -u OPENROUTER_API_KEY` and `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.
- OpenAI embeddings were replaced by an env-gated deterministic hash embedding fallback.
- The successful training rerun used `OPENROUTER_HTTP_TIMEOUT=600` after the first `gemma3:12b` attempt repeatedly hit the 180-second local client timeout.

## Commands Run

### Probe

```bash
curl http://127.0.0.1:11434/api/tags
```

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:12b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python <chat_probe>
```

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:12b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python <skillgen_wrapper_and_embedding_probes>
```

### Train

```bash
env -u OPENAI_API_KEY -u OPENROUTER_API_KEY OPENROUTER_HTTP_TIMEOUT=600 SKILLGEN_LOCAL_OPENAI_COMPAT=1 SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1 SKILLGEN_LOCAL_API_KEY=ollama SKILLGEN_LOCAL_MODEL=gemma3:12b SKILLGEN_LOCAL_EMBEDDING_MODE=hash SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0 .venv/bin/python main.py data/mcp_bench/train.json --config "../../artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_12b.yaml"
```

### Eval

Not executed. `eval_skill.py` requires a generated skill repository, and the successful training run produced none because baseline collection had 40 successes and 0 failures.

## Results

| Split | Baseline acc | Skill acc | Delta | Net gain |
| --- | ---: | ---: | ---: | ---: |
| Construction | 1.000 | n/a | n/a | n/a |
| Held-out | n/a | n/a | n/a | n/a |

## Trace Preservation

- Config: `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/gemma3_12b.yaml`
- Raw logs: `train_stdout.txt`, `train_stderr.txt`, `train_timeout_180s_*`, probe logs, and placeholder eval logs in this directory.
- Skill repo: expected path exists but is empty: `skill_output/2026-06-04_22-55-35`
- Verification summary: unavailable because Stage 2/3 did not run.
- Eval result: `eval_results.json` placeholder explaining why held-out eval was not run.
- Per-round traces: unavailable because no generation/refinement/verification round ran.

## Interpretation

This run supports part of the local execution strategy: the Ollama endpoint worked, the SkillGen LLM wrapper routed to local `gemma3:12b`, external APIs were bypassed, and the benchmark runner produced durable, parseable Stage 1 evidence. It does not validate SkillGen skill generation or held-out skill improvement, because the selected local model solved every training item in the 40-instance sample and left no failures for SkillGen to learn from.

The result moves the local MCP-Bench execution path from blocked/not-testable to testable for baseline collection, but not yet for the full generate-skill-then-evaluate loop.

## Remaining Issues

- A model/subset combination with baseline failures is still needed to exercise induction, generation, verification, and held-out skill evaluation.
- Hash embeddings remain a reconstructed deviation from the paper setup and need separate sensitivity checks once induction is exercised.
- The Ollama OpenAI-compatible route still loads `gemma3:12b` with a 131072-token context; this was manageable for `gemma3:12b` but caused resource trouble for `llama3.1:latest`.
- The successful run required `OPENROUTER_HTTP_TIMEOUT=600` for local long generations.
- Full-matrix and cross-benchmark validation remain untested.
