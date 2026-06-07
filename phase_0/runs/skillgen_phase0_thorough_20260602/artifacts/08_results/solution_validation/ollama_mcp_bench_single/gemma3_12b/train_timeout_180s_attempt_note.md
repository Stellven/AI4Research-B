# Training Attempt Terminated After Repeated 180s Local Timeouts

- Date: 2026-06-04
- Model: `gemma3:12b`
- Scope: local Ollama SkillGen solution validation, not paper reproduction.
- Attempt status: terminated by operator with `SIGTERM` after repeated local OpenAI-compatible chat requests hit the 180-second client timeout.
- Preserved logs:
  - `train_timeout_180s_stdout.txt`
  - `train_timeout_180s_stderr.txt`
  - `train_timeout_180s_command_status.json`

## Reason

The run reached Stage 1 baseline collection and completed 25 of 40 visible tqdm items, but no Stage 1 checkpoint had been written yet. Ollama server logs showed repeated `/v1/chat/completions` requests for the same local prompt being canceled at exactly 180 seconds after decoding roughly 2.3k to 2.4k tokens. Because the local wrapper request timeout was 180 seconds and baseline agent calls can request up to 4096 completion tokens, the same long response pattern was likely to continue failing before completion.

## Next Action

Restart the same `gemma3:12b` local validation run with external API keys unset, hash embeddings enabled, and `OPENROUTER_HTTP_TIMEOUT=600`. This changes only the local client timeout budget; it does not switch model providers or enable external APIs.
