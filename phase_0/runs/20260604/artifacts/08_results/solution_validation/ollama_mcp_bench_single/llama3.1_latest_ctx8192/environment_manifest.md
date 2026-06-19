# Environment Manifest

Date: 2026-06-04 16:24:43 EDT -0400
Repository: `/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B`
Git branch: `main`
Git commit: `0af0b0661b302408d47c4c448d04d1f5df2c0a64`

## Runtime

- Working directory for benchmark commands:
  `/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official`
- Python virtualenv:
  `/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/.venv`
- Python version: `Python 3.14.2`
- Ollama client version: `0.30.0`
- Ollama API probe: `http://127.0.0.1:11434/api/tags` succeeded.

## Selected Local Model

- Model name: `llama3.1:latest`
- Ollama model ID: `46e0c10c039e`
- Digest:
  `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`
- Parameter size: `8.0B`
- Quantization: `Q4_K_M`
- Capabilities reported by Ollama: `completion`, `tools`
- Local context limit requested through OpenAI-compatible `extra_body`:
  `num_ctx=8192`

## Local SkillGen Environment

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY` set to a non-secret local placeholder.
- `SKILLGEN_LOCAL_MODEL=llama3.1:latest`
- `SKILLGEN_LOCAL_NUM_CTX=8192`
- `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`
- `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`

## External API Key Handling

The ambient shell has `OPENAI_API_KEY` and `OPENROUTER_API_KEY` present. The
probe, train, and eval commands explicitly unset both variables with
`env -u OPENAI_API_KEY -u OPENROUTER_API_KEY` so external OpenAI/OpenRouter
chat and embedding APIs are bypassed for this run.

## Machine Notes

The machine is a MacBook Pro with 24 GB RAM. An unconstrained
`llama3.1:latest` attempt loaded with a 131072-token context and an
approximately 22 GB footprint, then stalled after 7 of 40 baseline trajectories.
This run requests an 8192-token local context to reduce memory pressure without
downloading a new model or using an external API.
