# Ollama Local Solution-Validation Deviation Note

Date: 2026-06-04
Model: llama3.1:latest

This run is not an original-paper reproduction. It does not attempt to reproduce
the paper's exact model suite, API backend, embedding model, benchmark matrix, or
reported numerical claims.

For this solution-validation run, the official SkillGen LLM API path is being
redirected to a local Ollama OpenAI-compatible endpoint:

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY=ollama`
- `SKILLGEN_LOCAL_MODEL=llama3.1:latest`

External OpenAI and OpenRouter chat APIs are disabled for this run. The direct
OpenAI fallback for `openai/...` model names is disabled with
`SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.

OpenAI embeddings are replaced by a local deterministic hash embedding fallback
using `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`. This fallback is a reconstructed
local component, not the paper's original embedding method.

The first attempted local model, `qwen3:8b`, was stopped after it projected to
an impractical multi-hour run during baseline collection. `llama3.1:latest` is
an already installed 8B local model selected to keep the first end-to-end
solution-validation run bounded.

The purpose of this run is to validate whether previously blocked or
not-testable SkillGen-style verification paths can be made executable and
evidence-producing under an explicit local execution strategy.
