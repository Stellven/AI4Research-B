# Ollama Local Solution-Validation Deviation Note

Date: 2026-06-04
Model: gemma3:12b

This run is not an original-paper reproduction. It does not attempt to reproduce
the paper's exact model suite, API backend, embedding model, benchmark matrix, or
reported numerical claims.

For this solution-validation run, the official SkillGen LLM API path is being
redirected to a local Ollama OpenAI-compatible endpoint:

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY=ollama`
- `SKILLGEN_LOCAL_MODEL=gemma3:12b`

External OpenAI and OpenRouter chat APIs are disabled for this run. The direct
OpenAI fallback for `openai/...` model names is disabled with
`SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`.

OpenAI embeddings are replaced by a local deterministic hash embedding fallback
using `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`. This fallback is a reconstructed
local component, not the paper's original embedding method.

Earlier local attempts are preserved under their own model directories:

- `qwen3_8b`: stopped after slow baseline throughput during initial bounded-run
  planning.
- `llama3.1_latest`: stopped after a 131072-token context produced an
  approximately 22 GB runtime footprint and stalled after 7/40 baseline items.
- `llama3.1_latest_ctx8192`: stopped after Ollama still reported the same
  131072-token context through the OpenAI-compatible route.

`gemma3:12b` was selected because it is already installed, is larger than the
8B-class models, and is expected to have a lower practical runtime footprint
than the `llama3.1:latest` OpenAI-compatible load on this 24 GB machine.

The first `gemma3:12b` training attempt used the wrapper default
`OPENROUTER_HTTP_TIMEOUT=180`. One baseline prompt repeatedly decoded more than
2,300 tokens and was canceled at the 180-second local client timeout before it
could finish. That attempt was terminated and preserved as
`train_timeout_180s_*`. The successful training rerun used
`OPENROUTER_HTTP_TIMEOUT=600` while keeping the same local model, same config,
same external API key unsets, and same hash embedding mode.

The purpose of this run is to validate whether previously blocked or
not-testable SkillGen-style verification paths can be made executable and
evidence-producing under an explicit local execution strategy.
