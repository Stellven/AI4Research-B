# Environment Manifest

Date: 2026-06-05 17:09:02 EDT -0400
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

- Model name: `gemma3:4b`
- Ollama model ID: `a2af6cc3eb7f`
- Digest:
  `a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a`
- Parameter size: `4.3B`
- Quantization: `Q4_K_M`
- Capabilities reported by Ollama: `completion`
- Loaded footprint observed by `ollama ps` after probes: `3.2 GB`
- Processor placement observed by `ollama ps` after probes: `100% GPU`
- Context reported by `ollama ps` after probes: `131072`

## Local SkillGen Environment

- `SKILLGEN_LOCAL_OPENAI_COMPAT=1`
- `SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1`
- `SKILLGEN_LOCAL_API_KEY` set to a non-secret local placeholder.
- `SKILLGEN_LOCAL_MODEL=gemma3:4b`
- `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`
- `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0`
- `OPENROUTER_HTTP_TIMEOUT=600` for benchmark training/eval commands.

## Code Deviation Under Test

`phase_0/runs/skillgen_phase0_thorough_20260602/code/official/pipeline.py`
was patched so `_build_verification_sample` includes baseline failures when
failures exist, then fills remaining slots with success guards.

## External API Key Handling

The ambient shell has `OPENAI_API_KEY` and `OPENROUTER_API_KEY` present. The
probe, train, and eval commands explicitly unset both variables with
`env -u OPENAI_API_KEY -u OPENROUTER_API_KEY` so external OpenAI/OpenRouter
chat and embedding APIs are bypassed for this run.

## Machine Notes

The machine is a MacBook Pro with 24 GB RAM. `gemma3:4b` is already installed
and loaded with a small observed footprint relative to available memory.

## Pre-Run Check: 2026-06-06 03:49:42 EDT

- Repository preflight working directory:
  `/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B`
- `git status --short` showed existing untracked validation artifacts and
  tests from the solution-validation work; no cleanup was performed.
- `python3 -m unittest discover -s tests` completed successfully:
  `Ran 13 tests` / `OK`.
- `ollama ps` completed successfully and reported no currently loaded model at
  preflight time.
- Selected model remains `gemma3:4b`.
- The training command will explicitly unset `OPENAI_API_KEY` and
  `OPENROUTER_API_KEY`.
- `memory_pressure` reported system-wide memory free percentage of `70%`.
- No unrelated processes were stopped.

## Post-Run Check: 2026-06-06 12:18:48 EDT

- The first non-escalated training attempt failed because sandboxed local
  Ollama/OpenAI-compatible HTTP access returned `Operation not permitted`.
  Evidence was preserved in `train_attempt1_stdout.txt`,
  `train_attempt1_stderr.txt`, and `train_attempt1_command_status.json`.
- The primary training rerun completed successfully with local Ollama:
  `train_command_status.json` reports exit code `0` and runtime `2682`
  seconds.
- Held-out evaluation completed successfully:
  `eval_command_status.json` reports exit code `0` and runtime `1961`
  seconds.
- `ollama ps` after the run reported `gemma3:4b` loaded with `3.2 GB`,
  `100% GPU`, and context `131072`.
- `memory_pressure` after the run reported system-wide memory free percentage
  of `24%`.
- No unrelated processes were stopped and no models were downloaded.
- External OpenAI/OpenRouter API routing remained disabled for both successful
  train and eval commands via explicit `env -u OPENAI_API_KEY -u
  OPENROUTER_API_KEY` command prefixes.
