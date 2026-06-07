# Ollama Local Solution-Validation Deviation Note

Date: 2026-06-04
Model: gemma3:1b
Scope: MCP-Bench single smoke subset

This run is not an original-paper reproduction. It does not attempt to reproduce
the paper's exact model suite, API backend, embedding model, benchmark matrix, or
reported numerical claims.

For this solution-validation smoke run, the official SkillGen LLM API path is
redirected to a local Ollama OpenAI-compatible endpoint:

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY=ollama`
- `SKILLGEN_LOCAL_MODEL=gemma3:1b`

External OpenAI and OpenRouter chat APIs are disabled for this run. The direct
OpenAI fallback for `openai/...` model names is disabled with
`SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.

OpenAI embeddings are replaced by a local deterministic hash embedding fallback
using `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`. This fallback is a reconstructed
local component, not the paper's original embedding method.

Runtime-bounded deviations from the recommended first benchmark:

- The train input is a deterministic `n=4` smoke subset of MCP-Bench single,
  stored as `artifacts/07_configs_and_inputs/smoke_data/mcp_bench_single_train_n4_seed42.json`.
- The held-out input is a deterministic `n=4` smoke subset, stored as
  `artifacts/07_configs_and_inputs/smoke_data/mcp_bench_single_test_n4_seed42.json`.
- The model is `gemma3:1b`, selected because full-size local 8B attempts with
  `qwen3:8b` and `llama3.1:latest` were too slow for an interactive first pass.

The purpose of this smoke run is to validate whether the blocked/not-testable
path can be made executable and evidence-producing with local infrastructure.
It should not be treated as a full MCP-Bench validation.
