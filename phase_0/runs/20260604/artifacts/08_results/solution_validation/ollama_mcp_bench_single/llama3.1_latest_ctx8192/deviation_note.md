# Ollama Local Solution-Validation Deviation Note

Date: 2026-06-04
Model: llama3.1:latest
Local context limit: 8192

This run is not an original-paper reproduction. It does not attempt to reproduce
the paper's exact model suite, API backend, embedding model, benchmark matrix, or
reported numerical claims.

For this solution-validation run, the official SkillGen LLM API path is being
redirected to a local Ollama OpenAI-compatible endpoint:

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY=ollama`
- `SKILLGEN_LOCAL_MODEL=llama3.1:latest`
- `SKILLGEN_LOCAL_NUM_CTX=8192`

External OpenAI and OpenRouter chat APIs are disabled for this run. The direct
OpenAI fallback for `openai/...` model names is disabled with
`SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.

OpenAI embeddings are replaced by a local deterministic hash embedding fallback
using `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`. This fallback is a reconstructed
local component, not the paper's original embedding method.

The context limit is a local execution deviation added after an unconstrained
`llama3.1:latest` run loaded with a 131072-token context and an approximately
22 GB footprint, leaving too little memory headroom on the 24 GB machine. The
purpose is to preserve the same local model while reducing resource pressure.

The purpose of this run is to validate whether previously blocked or
not-testable SkillGen-style verification paths can be made executable and
evidence-producing under an explicit local execution strategy.
