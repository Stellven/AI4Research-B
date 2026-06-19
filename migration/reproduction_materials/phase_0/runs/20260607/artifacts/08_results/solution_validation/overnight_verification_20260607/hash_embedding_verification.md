# Hash Embedding Verification

Date: 2026-06-07

## Purpose

Verify the deterministic local hash embedding fallback without contacting
OpenAI, OpenRouter, Ollama, or any network endpoint.

Implementation under test:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/llm.py
```

Relevant behavior:

- `SKILLGEN_LOCAL_EMBEDDING_MODE=hash` routes `embed(...)` to local
  `_hash_embeddings(...)`.
- Hash vectors use `_HASH_EMBED_DIM = 256`.
- The hash path returns before `_get_openai_client()` is called.

## Added Test

```text
tests/test_skillgen_hash_embedding.py
```

The test stubs the `openai.OpenAI` constructor so any accidental OpenAI client
construction fails the test. It then unsets `OPENAI_API_KEY` and
`OPENROUTER_API_KEY`, sets `SKILLGEN_LOCAL_EMBEDDING_MODE=hash`, and verifies:

- the same text gives the same vector across calls;
- different text gives a different deterministic vector;
- batch and single-item outputs agree;
- vector shape is stable at 256 dimensions;
- non-empty vectors are normalized;
- no API key is required.

## Commands Run

```bash
python3 -m unittest tests.test_skillgen_hash_embedding
```

Result:

```text
Ran 1 test in 0.006s
OK
```

```bash
python3 -m unittest discover -s tests
```

Result:

```text
Ran 15 tests in 4.123s
OK
```

## Status

Status: `validated`

The deterministic hash embedding fallback is covered by a local offline test
and does not require external API credentials for the verified path.
