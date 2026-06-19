# Deviation Note

Date: 2026-06-07

This run is a bounded smoke validation of local SkillGen solution fixes. It is
not paper reproduction.

Intent:

- validate local Ollama routing on an already-installed small model;
- validate deterministic hash embeddings in a real benchmark command;
- validate the generator robustness patch after a local model returned a list
  for `dedup_notes`;
- validate persisted candidate-to-skill traceability through
  `source_candidate_id`;
- collect train/eval evidence without overwriting prior result directories.

Deviations from paper reproduction:

- Model is local `gemma3:1b`, not the paper's model suite.
- Dataset is a 4-case MCP-Bench smoke sample, not a full benchmark matrix.
- Embeddings use deterministic local hash embeddings.
- External OpenAI/OpenRouter APIs are disabled.
- The result status is about local solution behavior, not paper claims.
