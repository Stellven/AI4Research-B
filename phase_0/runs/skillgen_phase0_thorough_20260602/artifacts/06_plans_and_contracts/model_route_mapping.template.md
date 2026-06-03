# Model Route Mapping Template

Resolved SkillGen paper model display names to executable provider route IDs

Status: `route_resolved_with_equivalent_deviations`

Provider policy: OpenRouter can be used for chat routes, but it is not required by the paper. OpenAI is currently required by the official code for embeddings unless that dependency is patched and approved.

Unresolved models: `none`
Equivalent route deviations: `Gemma-4-26B, Grok-4-Fast`

## Table 1 Models

| Paper display name | Provider route ID | Status |
| --- | --- | --- |
| `Gemma-4-26B` | `google/gemma-4-26b-a4b-it` | `route_resolved_equivalent` |
| `Llama-3.1-8B` | `meta-llama/llama-3.1-8b-instruct` | `route_resolved_exact` |
| `Mistral-Nemo` | `mistralai/mistral-nemo` | `route_resolved_exact` |
| `Qwen-2.5-7B` | `qwen/qwen-2.5-7b-instruct` | `route_resolved_exact` |
| `Claude-Haiku-4.5` | `anthropic/claude-haiku-4.5` | `route_resolved_exact` |
| `GPT-5.4-Nano` | `openai/gpt-5.4-nano` | `route_resolved_exact` |
| `GPT-5.4-Mini` | `openai/gpt-5.4-mini` | `route_resolved_exact` |
| `Grok-4-Fast` | `x-ai/grok-4.3` | `route_resolved_equivalent` |

## Transfer Models

| Paper display name | Provider route ID | Status |
| --- | --- | --- |
| `Qwen-2.5-7B` | `qwen/qwen-2.5-7b-instruct` | `route_resolved_exact` |
| `Llama-3.1-8B` | `meta-llama/llama-3.1-8b-instruct` | `route_resolved_exact` |
| `GPT-OSS-20B` | `openai/gpt-oss-20b` | `route_resolved_exact` |
| `GPT-5.4-Nano` | `openai/gpt-5.4-nano` | `route_resolved_exact` |
| `GPT-5.4-Mini` | `openai/gpt-5.4-mini` | `route_resolved_exact` |
| `Grok-4-Fast` | `x-ai/grok-4.3` | `route_resolved_equivalent` |
