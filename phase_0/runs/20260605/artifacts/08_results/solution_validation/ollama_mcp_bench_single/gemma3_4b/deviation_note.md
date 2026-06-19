# Ollama Local Solution-Validation Deviation Note

Date: 2026-06-05
Model: gemma3:4b

This run is not an original-paper reproduction. It does not attempt to reproduce
the paper's exact model suite, API backend, embedding model, benchmark matrix, or
reported numerical claims.

For this solution-validation run, the official SkillGen LLM API path is being
redirected to a local Ollama OpenAI-compatible endpoint:

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY=ollama`
- `SKILLGEN_LOCAL_MODEL=gemma3:4b`

External OpenAI and OpenRouter chat APIs are disabled for this run. The direct
OpenAI fallback for `openai/...` model names is disabled with
`SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.

OpenAI embeddings are replaced by a local deterministic hash embedding fallback
using `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`. This fallback is a reconstructed
local component, not the paper's original embedding method.

This second local model run was started because the `gemma3:12b` run completed
Stage 1 with 40/40 baseline successes and therefore produced no skill. The
purpose of this run is to use an installed smaller local model that is more
likely to expose baseline failures and exercise induction, skill generation,
verification, and held-out evaluation.

The successful training command will use `OPENROUTER_HTTP_TIMEOUT=600`, matching
the corrected local timeout used for the completed `gemma3:12b` rerun.
