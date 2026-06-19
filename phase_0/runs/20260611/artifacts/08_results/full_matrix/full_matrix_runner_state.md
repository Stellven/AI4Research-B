# Full Matrix Runner State

Status: `dry_run_completed`

## Policy

- `openai_routes_first`: `True`
- `include_non_openai`: `False`
- `direct_openai_fallback`: `True`
- `allow_openrouter_after_402`: `False`
- `max_entries`: `None`
- `dry_run`: `True`
- `judge_model_route`: `openai/gpt-5.4-mini`
- `max_workers`: `1`
- `max_refine_rounds`: `1`
- `verification_sample_size`: `2`
- `max_eval_instances`: `1`
- `target_subset`: `None`
- `model_subset`: `None`

## Provider Resolution

- `status`: `openai_ready_non_openai_waiting_route_resolution`
- `openai_candidate_ready_models`: `2`
- `non_openai_provider_unavailable_models`: `0`
- `non_openai_waiting_route_resolution_models`: `6`

## Counts

- `not_started`: `20`
- `waiting_provider_route_resolution`: `60`

## Selected Entries

- `alfworld_iod::GPT-5.4-Nano`
- `alfworld_iod::GPT-5.4-Mini`
- `alfworld_ood::GPT-5.4-Nano`
- `alfworld_ood::GPT-5.4-Mini`
- `livecodebench::GPT-5.4-Nano`
- `livecodebench::GPT-5.4-Mini`
- `mcp_bench_all::GPT-5.4-Nano`
- `mcp_bench_all::GPT-5.4-Mini`
- `mcp_bench_single::GPT-5.4-Nano`
- `mcp_bench_single::GPT-5.4-Mini`
- `mind2web::GPT-5.4-Nano`
- `mind2web::GPT-5.4-Mini`
- `pubmedqa::GPT-5.4-Nano`
- `pubmedqa::GPT-5.4-Mini`
- `scienceworld::GPT-5.4-Nano`
- `scienceworld::GPT-5.4-Mini`
- `socialmaze_fts::GPT-5.4-Nano`
- `socialmaze_fts::GPT-5.4-Mini`
- `socialmaze_upi::GPT-5.4-Nano`
- `socialmaze_upi::GPT-5.4-Mini`

## Provider Unavailable

- None.
