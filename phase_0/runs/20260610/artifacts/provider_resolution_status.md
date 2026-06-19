# Provider Resolution Status

Provider availability policy for SkillGen full-matrix execution.

Status: `openai_ready_non_openai_provider_unavailable`

## Policy

- `direct_openai_fallback`: `True`
- `include_non_openai`: `False`
- `allow_openrouter_after_402`: `False`
- `model_substitution_allowed`: `False`
- `non_openai_direct_provider_runner_status`: `not_integrated_by_current_runner`
- `matrix_behavior`: `Run executable entries; record provider-unavailable entries without treating provider failure as benchmark evidence.`

## Provider Summary

- `openai_candidate_ready_models`: `2`
- `non_openai_provider_unavailable_models`: `6`
- `non_openai_waiting_route_resolution_models`: `0`

## OpenRouter Billing Evidence

- `detected`: `True`
- `evidence_file`: `artifacts/08_results/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/train_stderr.txt`
- `evidence_file`: `outputs/tau_bench_train_stderr.txt`

## Key Inventory

| Key | Present | Sources |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | `True` | `process_env, project_root_dotenv` |
| `OPENAI_API_KEY` | `True` | `process_env, project_root_dotenv` |
| `ANTHROPIC_API_KEY` | `False` | `none` |
| `GOOGLE_API_KEY` | `False` | `none` |
| `GEMINI_API_KEY` | `False` | `none` |
| `MISTRAL_API_KEY` | `False` | `none` |
| `XAI_API_KEY` | `False` | `none` |
| `GROQ_API_KEY` | `False` | `none` |
| `TOGETHER_API_KEY` | `False` | `none` |
| `FIREWORKS_API_KEY` | `False` | `none` |
| `DEEPINFRA_API_KEY` | `False` | `none` |

## Routes

| Paper model | Provider route | Execution status | Runner status |
| --- | --- | --- | --- |
| `Gemma-4-26B` | `google/gemma-4-26b-a4b-it` | `provider_unavailable_openrouter_402` | `provider_unavailable` |
| `Llama-3.1-8B` | `meta-llama/llama-3.1-8b-instruct` | `provider_unavailable_openrouter_402` | `provider_unavailable` |
| `Mistral-Nemo` | `mistralai/mistral-nemo` | `provider_unavailable_openrouter_402` | `provider_unavailable` |
| `Qwen-2.5-7B` | `qwen/qwen-2.5-7b-instruct` | `provider_unavailable_openrouter_402` | `provider_unavailable` |
| `Claude-Haiku-4.5` | `anthropic/claude-haiku-4.5` | `provider_unavailable_openrouter_402` | `provider_unavailable` |
| `GPT-5.4-Nano` | `openai/gpt-5.4-nano` | `executable_via_direct_openai` | `candidate_ready` |
| `GPT-5.4-Mini` | `openai/gpt-5.4-mini` | `executable_via_direct_openai` | `candidate_ready` |
| `Grok-4-Fast` | `x-ai/grok-4.3` | `provider_unavailable_openrouter_402` | `provider_unavailable` |

## Operational Decision

- Continue full-matrix execution for openai/* routes with direct OpenAI fallback enabled.
- Do not attempt non-OpenAI routes while OpenRouter 402 evidence is present unless OpenRouter credits/key are repaired or a reviewed direct-provider integration is added.
- Do not substitute non-OpenAI paper models with OpenAI models for Table 1 reproduction; any substitute-model run must be marked as an extended/deviation-backed experiment.
