# Environment Manifest

Date: 2026-06-04 16:58:30 EDT -0400
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

- Model name: `gemma3:12b`
- Ollama model ID: `f4031aab637d`
- Digest:
  `f4031aab637d1ffa37b42570452ae0e4fad0314754d17ded67322e4b95836f8a`
- Parameter size: `12.2B`
- Quantization: `Q4_K_M`
- Capabilities reported by Ollama: `completion`
- Loaded footprint observed by `ollama ps` after probes: `8.3 GB`
- Processor placement observed by `ollama ps` after probes: `100% GPU`
- Context reported by `ollama ps` after probes: `131072`

## Local SkillGen Environment

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY` set to a non-secret local placeholder.
- `SKILLGEN_LOCAL_MODEL=gemma3:12b`
- `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`
- `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`

## External API Key Handling

The ambient shell has `OPENAI_API_KEY` and `OPENROUTER_API_KEY` present. The
probe, train, and eval commands explicitly unset both variables with
`env -u OPENAI_API_KEY -u OPENROUTER_API_KEY` so external OpenAI/OpenRouter
chat and embedding APIs are bypassed for this run.

## Machine Notes

The machine is a MacBook Pro with 24 GB RAM. `gemma3:12b` was selected after
`llama3.1:latest` loaded with an approximately 22 GB footprint and stalled.
The observed `gemma3:12b` footprint leaves materially more memory headroom.
