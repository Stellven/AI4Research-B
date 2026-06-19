# Full Matrix Cost Report Template

Date filled: `<YYYY-MM-DD>`

Filled by: `<agent or human>`

Purpose: one report per full-matrix entry attempt. C group should copy this
template after each runner execution and fill it from raw logs, token usage
files, trajectory paths, and parsed results. This template is a governance
artifact; it does not by itself change claim status.

## Entry Identity

- Entry ID: `<table1_row::provider_route_or_model_slug>`
- Benchmark row: `<alfworld_iod | alfworld_ood | livecodebench | mcp_bench_all | mcp_bench_single | mind2web | pubmedqa | scienceworld | socialmaze_fts | socialmaze_upi>`
- Paper model display name: `<paper display name>`
- Model route: `<provider route id>`
- Provider path: `<OpenRouter | direct OpenAI | other provider>`
- Route execution mode: `<openrouter | direct_openai_for_openai_models | provider_specific | failed_before_call>`
- Route resolution status: `<route_resolved_exact | route_resolved_equivalent | unresolved | fallback>`
- Judge model route: `<judge route>`

## Config And Dataset

- Config path: `<artifacts/generated_configs/...yaml>`
- Config deviation: `<exact_author_original | reconstructed_low_cost | reconstructed_full_scale | other>`
- Benchmark execution plan source:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/benchmark_execution_plan.json`
- Full matrix contract source:
  `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_contract.json`
- Train dataset: `<code/official/data/.../train.json>`
- Test dataset: `<code/official/data/.../test.json>`
- Train n: `<integer>`
- Test n: `<integer>`
- Max workers: `<integer>`
- Refinement rounds: `<integer or config reference>`
- Verification sample size: `<integer or config reference>`

## Timing

- Train start time: `<ISO 8601>`
- Train end time: `<ISO 8601>`
- Eval start time: `<ISO 8601>`
- Eval end time: `<ISO 8601>`
- Combined start time: `<ISO 8601>`
- Combined end time: `<ISO 8601>`
- Train wall time seconds: `<number>`
- Eval wall time seconds: `<number>`
- Combined wall time seconds: `<number>`

## Token And Cost

- Training token usage: `<integer or missing>`
- Held-out eval token usage: `<integer or missing>`
- Total token usage: `<integer or missing>`
- Token usage source, training: `<path>`
- Token usage source, eval: `<path>`
- Estimated dollar cost: `<number or unavailable>`
- Currency: `USD`
- Pricing basis: `<provider pricing URL/file, price snapshot date, or unavailable>`
- Cost notes: `<rate limits, retries, failed partial attempts, missing prices>`

## Outputs

- Train stdout path: `<path>`
- Train stderr path: `<path>`
- Eval stdout path: `<path>`
- Eval stderr path: `<path>`
- Run artifacts path: `<path>`
- Skill output path: `<path>`
- Eval results path: `<path>`
- Eval token usage path: `<path>`
- Candidate skill artifact paths: `<paths>`
- Checkpoint path: `<path or missing>`
- Run metadata path: `<path or missing>`

## Trajectories And Trace Retention

- Baseline train trajectories: `<path or missing>`
- Checkpoint train trajectories: `<path or missing>`
- Verification baseline trajectories: `<path(s) or missing>`
- Verification with-skill trajectories: `<path(s) or missing>`
- Verification summary paths: `<path(s) or missing>`
- Verification case analyses paths: `<path(s) or missing>`
- Held-out baseline trajectories: `<path or missing>`
- Held-out with-skill trajectories: `<path or missing>`
- Trace retention status: `<complete | incomplete | missing | not_checked>`
- Missing trajectory details: `<list>`

## Result Summary

- Skill ID: `<id or missing>`
- Skill status: `<accepted | deprecated | missing | unknown>`
- Skill rejected: `<true | false | unknown>`
- Construction paired n: `<integer>`
- Construction baseline accuracy: `<number>`
- Construction skill accuracy: `<number>`
- Construction delta accuracy: `<number>`
- Construction repair count: `<integer>`
- Construction regression count: `<integer>`
- Construction net gain: `<integer>`
- Construction gate passed: `<true | false | unknown>`
- Held-out n: `<integer>`
- Held-out baseline accuracy: `<number>`
- Held-out skill accuracy: `<number>`
- Held-out delta accuracy: `<number>`
- Held-out repair count: `<integer>`
- Held-out regression count: `<integer>`
- Held-out net gain: `<integer>`
- Entry verdict: `<reproduced | partially_reproduced | not_reproduced | failed_to_run | stopped | incomplete>`

## Disclosure And Claim Impact

- Deviation label: `<exact_author_original | reconstructed_low_cost | reconstructed_full_scale | provider_fallback | partial_matrix>`
- Deviation artifacts:
  - `<path>`
- Human approval artifact:
  - `<path>`
- Claim impact:
  - `claim_table1_average_gains_all_models`: `<still_blocked_incomplete_matrix | no_change | contributes_to_full_matrix_when_80_complete>`
  - `claim_table1_entry_counts`: `<still_blocked_incomplete_matrix | no_change | contributes_to_full_matrix_when_80_complete>`
  - `claim_table1_alfworld_scienceworld_patterns`: `<if applicable>`
- Report wording required:
  `<one sentence that final report should use>`

## Stop Or Retry

- Stop reason: `<none | provider_error | token_budget_exceeded | repeated_deprecated_skills | missing_trajectory_artifacts | missing_token_usage | unexpected_cost_spike | human_stopped | other>`
- Stop details: `<free text>`
- Retry of entry ID: `<entry id or none>`
- Retry approval artifact: `<path or none>`
- Previous failed attempt logs:
  - `<path>`
- Next allowed action:
  `<continue | retry_with_approval | inspect_config | inspect_provider | stop_tier | stop_full_matrix>`

## Missing Metadata / Needed From C Group

Fill this section whenever a field above is unavailable.

- Missing metadata:
  - `<field name>`
- Why missing:
  - `<reason>`
- Required C group fix:
  - `<runner metadata addition, token parser fix, trajectory retention fix, provider pricing source, etc.>`
