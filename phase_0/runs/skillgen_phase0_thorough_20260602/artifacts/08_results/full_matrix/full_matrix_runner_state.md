# Full Matrix Runner State

Status: `dry_run_completed`

## Policy

- `openai_routes_first`: `True`
- `include_non_openai`: `False`
- `direct_openai_fallback`: `True`
- `max_entries`: `4`
- `dry_run`: `True`
- `judge_model_route`: `openai/gpt-5.4-mini`
- `max_workers`: `1`
- `max_refine_rounds`: `1`
- `verification_sample_size`: `4`
- `max_eval_instances`: `None`
- `target_subset`: `None`
- `model_subset`: `None`

## Provider Resolution

- `status`: `openai_ready_non_openai_provider_unavailable`
- `openai_candidate_ready_models`: `2`
- `non_openai_provider_unavailable_models`: `6`
- `non_openai_waiting_route_resolution_models`: `0`

## Counts

- `budget_stopped`: `15`
- `completed_invalid_evidence`: `1`
- `not_started`: `4`
- `provider_unavailable`: `60`

## Selected Entries

- `alfworld_iod::GPT-5.4-Nano`
- `alfworld_iod::GPT-5.4-Mini`
- `alfworld_ood::GPT-5.4-Nano`
- `alfworld_ood::GPT-5.4-Mini`

## Provider Unavailable

- `alfworld_iod::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `alfworld_iod::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `alfworld_iod::Grok-4-Fast` via `x-ai/grok-4.3`
- `alfworld_iod::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `alfworld_iod::Mistral-Nemo` via `mistralai/mistral-nemo`
- `alfworld_iod::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `alfworld_ood::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `alfworld_ood::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `alfworld_ood::Grok-4-Fast` via `x-ai/grok-4.3`
- `alfworld_ood::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `alfworld_ood::Mistral-Nemo` via `mistralai/mistral-nemo`
- `alfworld_ood::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `livecodebench::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `livecodebench::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `livecodebench::Grok-4-Fast` via `x-ai/grok-4.3`
- `livecodebench::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `livecodebench::Mistral-Nemo` via `mistralai/mistral-nemo`
- `livecodebench::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `mcp_bench_all::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `mcp_bench_all::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `mcp_bench_all::Grok-4-Fast` via `x-ai/grok-4.3`
- `mcp_bench_all::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `mcp_bench_all::Mistral-Nemo` via `mistralai/mistral-nemo`
- `mcp_bench_all::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `mcp_bench_single::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `mcp_bench_single::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `mcp_bench_single::Grok-4-Fast` via `x-ai/grok-4.3`
- `mcp_bench_single::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `mcp_bench_single::Mistral-Nemo` via `mistralai/mistral-nemo`
- `mcp_bench_single::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `mind2web::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `mind2web::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `mind2web::Grok-4-Fast` via `x-ai/grok-4.3`
- `mind2web::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `mind2web::Mistral-Nemo` via `mistralai/mistral-nemo`
- `mind2web::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `pubmedqa::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `pubmedqa::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `pubmedqa::Grok-4-Fast` via `x-ai/grok-4.3`
- `pubmedqa::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `pubmedqa::Mistral-Nemo` via `mistralai/mistral-nemo`
- `pubmedqa::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `scienceworld::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `scienceworld::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `scienceworld::Grok-4-Fast` via `x-ai/grok-4.3`
- `scienceworld::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `scienceworld::Mistral-Nemo` via `mistralai/mistral-nemo`
- `scienceworld::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `socialmaze_fts::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `socialmaze_fts::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `socialmaze_fts::Grok-4-Fast` via `x-ai/grok-4.3`
- `socialmaze_fts::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `socialmaze_fts::Mistral-Nemo` via `mistralai/mistral-nemo`
- `socialmaze_fts::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
- `socialmaze_upi::Claude-Haiku-4.5` via `anthropic/claude-haiku-4.5`
- `socialmaze_upi::Gemma-4-26B` via `google/gemma-4-26b-a4b-it`
- `socialmaze_upi::Grok-4-Fast` via `x-ai/grok-4.3`
- `socialmaze_upi::Llama-3.1-8B` via `meta-llama/llama-3.1-8b-instruct`
- `socialmaze_upi::Mistral-Nemo` via `mistralai/mistral-nemo`
- `socialmaze_upi::Qwen-2.5-7B` via `qwen/qwen-2.5-7b-instruct`
