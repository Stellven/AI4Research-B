# Full Matrix Cost Governance

Date: 2026-06-04

Group: F - Evidence / Report Integration

Scope: governance, reporting, deviation disclosure, and stop policy for future
SkillGen Table 1 full-matrix execution. This artifact does not implement a
runner, does not run benchmarks, and does not change any claim status.

## Source Artifacts Used

All conclusions below are based on these existing artifacts:

- `logs/phase_0_overnight_20260604/遇到的问题.md`
- `logs/phase_0_overnight_20260604/operation_log.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/reconstructed_validation_path_index.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/observed_entries.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_contract.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/benchmark_execution_plan.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/model_route_mapping.template.json`

## Why Blind 80-Entry Execution Is Not Acceptable

The Table 1 full matrix is 10 benchmark rows times 8 paper models, or 80
entries. The full-matrix contract records `paper_required = 80` and currently
shows the matrix as incomplete, with ALFWorld rows still requiring reconstructed
execution governance and human approval in
`artifacts/06_plans_and_contracts/full_matrix_execution_contract.json`.

The overnight run completed only one reconstructed low-cost entry:

```text
mcp_bench_single::openai/gpt-5.4-nano
```

That one entry is recorded in
`artifacts/08_results/full_matrix/observed_entries.json` as
`incomplete_single_entry_observed`, with `observed = 1`, `remaining = 79`, and
entry-level verdict `not_reproduced`.

Blindly launching all 80 entries would be unsafe for four reasons:

1. Cost is already non-trivial for one reduced entry.
2. Wall-clock time is material even at low-cost settings.
3. Provider availability differs by model route.
4. Reconstructed rows and exact rows require different report labels and
   approval gates.

The overnight operation log also records an OpenRouter HTTP 402 insufficient
credits failure before the successful direct OpenAI fallback run. That means
provider errors are not hypothetical; they already occurred and must be part of
the stop policy.

## Known Single-Entry Cost Evidence

Observed entry:

```text
entry_id: mcp_bench_single::openai/gpt-5.4-nano
reproduction class: reconstructed low-cost single-entry full-matrix execution
config: artifacts/generated_configs/mcp_bench_single/openai_gpt-5.4-nano.yaml
train_n: 40
test_n: 16
route_execution_mode: direct_openai_for_openai_models
entry verdict: not_reproduced
```

Token usage from `artifacts/08_results/full_matrix/observed_entries.json`:

```text
training token usage: 446,895
held-out eval token usage: 110,982
combined token usage: 557,877
```

The operation log states that the train and eval execution took on the order of
tens of minutes. This entry was not full paper scale; it used reduced
rounds/workers/verification sample for overnight cost control.

## Why 557,877 Tokens Must Not Be Linearly Extrapolated

The observed 557,877 tokens are enough to prove that full-matrix execution needs
budget governance. They are not enough to produce a reliable full-80 cost
estimate.

Do not multiply `557,877 * 80` and treat that as a forecast. That would ignore:

- Benchmark row differences. The benchmark execution plan shows different
  `train_n` and `test_n` values, such as ALFWorld IOD `train_n=500`,
  `test_n=150`, ALFWorld OOD `train_n=500`, `test_n=255`, LiveCodeBench
  `train_n=50`, `test_n=150`, and MCP-Bench single `train_n=40`, `test_n=16`.
- Task-shape differences. Interactive or long-context tasks can produce larger
  prompts, more turns, more verification traces, or larger model responses than
  compact binary tasks.
- Model-route differences. `model_route_mapping.template.json` maps paper model
  display names to different provider routes, including OpenAI and non-OpenAI
  routes. Pricing, rate limits, throughput, and tokenization may differ.
- Reconstructed path differences. The observed entry used a low-cost generated
  config. Full-scale or exact author-original settings may use different
  refinement rounds, verification sample size, workers, and task counts.
- Failure-path cost. The operation log shows an OpenRouter failure and a failed
  resume attempt before the successful direct OpenAI run. Failed attempts can
  consume time and partial token budget.

The correct use of the 557,877-token observation is as a governance trigger: it
proves every future full-matrix run needs explicit budget tiering, per-entry
metadata, stop conditions, and report labels.

## Benchmark And Model Cost Difference Sources

Expected cost and time can vary by:

- `train_n` and `test_n`.
- Average prompt size per instance.
- Average trajectory length per instance.
- Number of induction, refinement, and verification rounds.
- Verification sample size.
- Whether a skill is deprecated early or repeatedly.
- Whether baseline trajectories can be reused safely.
- Whether held-out eval saves full trajectories.
- Judge model route and evaluator model route.
- Provider pricing and rate limits.
- Provider retry behavior and concurrency limits.
- Reconstructed adapters such as ALFWorld offline-plan conversion.
- Exact author-original paths versus reconstructed low-cost configs.

These sources must be recorded per entry rather than hidden in a global summary.

## Direct OpenAI Fallback Versus Non-OpenAI Provider Routes

The overnight operation log records:

- OpenRouter returned HTTP 402 insufficient credits during the first
  `mcp_bench_single` attempt.
- `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1` allowed `openai/...` routes to
  call OpenAI directly.
- A direct route probe for `openai/gpt-5.4-nano` returned `OK`.

This fallback applies only to `openai/...` routes. It does not solve execution
for non-OpenAI routes such as:

- `google/gemma-4-26b-a4b-it`
- `meta-llama/llama-3.1-8b-instruct`
- `mistralai/mistral-nemo`
- `qwen/qwen-2.5-7b-instruct`
- `anthropic/claude-haiku-4.5`
- `x-ai/grok-4.3`

The route mapping artifact records equivalent-deviation routes for
`Gemma-4-26B` and `Grok-4-Fast`. Any execution using those routes needs explicit
provider/deviation reporting. If non-OpenAI provider routes cannot run because
OpenRouter billing or provider access is unavailable, the report must say that
provider availability limited matrix completeness. It must not treat that as a
paper claim failure.

## Reconstructed Versus Exact Path Cost Disclosure

The reconstructed validation path index states that reconstructed paths can
support at most `partially_reproduced` unless author-original runners, splits,
configs, and model routes are found and used.

Cost reporting must preserve the same distinction:

- `exact_author_original`: author-original code, split, config, route, and
  comparison rule. Cost and time are still disclosed, but exactness is not
  limited by reconstruction.
- `reconstructed_low_cost`: reduced config, reduced rounds/workers/sample size,
  inferred split, fallback provider, or single-entry probe. This is cost-control
  evidence, not full-paper reproduction.
- `reconstructed_full_scale`: reconstructed path run at full target size. This
  can improve completeness but remains reconstructed unless author-original
  artifacts are found.
- `provider_fallback`: provider route differs from the primary route because
  OpenRouter, billing, or route availability required a fallback.
- `partial_matrix`: only some entries ran. This must never be described as the
  complete Table 1 matrix.

## Required Cost And Time Metadata Per Entry

Every full-matrix entry run must preserve:

- `entry_id`
- `table1_row`
- `paper_model_display_name`
- `provider_route_id`
- `provider_path`
- `route_execution_mode`
- `route_resolution_status`
- `config_path`
- `config_deviation`
- `train_dataset`
- `test_dataset`
- `train_n`
- `test_n`
- `judge_model_route`
- `max_workers`
- `start_time`
- `end_time`
- `wall_time_seconds`
- `train_token_usage_total`
- `eval_token_usage_total`
- `combined_token_usage_total`
- `estimated_dollar_cost`
- `pricing_basis`
- `stdout_path`
- `stderr_path`
- `run_artifacts_path`
- `skill_output_path`
- `eval_results_path`
- `eval_token_usage_path`
- `train_trajectory_paths`
- `eval_trajectory_paths`
- `verification_round_paths`
- `skill_id`
- `skill_status`
- `skill_rejected`
- `construction_verification_summary`
- `held_out_eval_summary`
- `entry_verdict`
- `paper_claim_impact`
- `deviation_label`
- `human_approval_artifact`
- `stop_reason`
- `retry_of_entry_id`

## Stop Governance

The runner should stop or require human re-approval when any of these conditions
occur:

- Provider error: authentication, billing, model unavailable, OpenRouter 402, or
  repeated 429/rate-limit failures.
- Token budget exceeded: per-entry, per-tier, or whole-run budget limit reached.
- Repeated deprecated skills: multiple entries for the same benchmark/model tier
  finish construction with deprecated or failed-gate skills.
- Missing trajectory artifacts: required per-round or held-out trajectories are
  missing.
- Missing token usage: train or eval token usage files are absent.
- Unexpected cost spike: observed token usage exceeds the tier threshold or a
  configured multiplier over the current baseline.
- Missing raw logs: stdout/stderr are missing for train, eval, failed attempt,
  or retry.

Stopping for budget or provider limits is not a claim failure. It limits
reproduction completeness and must be reported as such.

## Missing Metadata / Needed From C Group

C group should provide the following before any multi-entry execution:

- Per-tier token and dollar budgets approved by a human.
- Per-entry pricing source and timestamp for each provider route.
- Expected token envelope per benchmark row and model route.
- A unique `entry_id` and output directory policy that never overwrites prior
  attempts.
- Per-entry start/end timestamps and wall-clock duration.
- Retry policy that links failed attempts to successful attempts.
- Stop-reason enum written to entry metadata.
- A complete trajectory-retention check before parsing an entry as valid.
- A cost summary artifact that can be consumed by the final report.

Until these exist, F group should label future full-matrix execution as
governance-incomplete.
