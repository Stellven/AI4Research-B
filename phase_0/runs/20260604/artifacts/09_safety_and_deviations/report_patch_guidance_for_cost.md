# Report Patch Guidance For Full Matrix Cost

Date: 2026-06-04

Group: F - Evidence / Report Integration

Scope: how future `research_validation_report.md` updates should describe
full-matrix cost, time, provider fallback, partial execution, and budget stops.
This guidance does not change claim status and does not run benchmarks.

## Source Artifacts To Cite

Every report patch about cost or time should cite the relevant subset of:

- `logs/phase_0_overnight_20260604/遇到的问题.md`
- `logs/phase_0_overnight_20260604/operation_log.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/reconstructed_validation_path_index.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/observed_entries.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_contract.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/benchmark_execution_plan.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/model_route_mapping.template.json`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_budget_policy.json`

## General Report Rules

- Do not describe a partial matrix as the full 80-entry matrix.
- Do not promote a claim to `reproduced` or `partially_reproduced` because a run
  was expensive, long, or governance-complete.
- Cost being too high is not a claim failure. It limits reproduction
  completeness unless the executed result itself is negative.
- A stopped or budget-limited run should be reported as incomplete, not as
  evidence for or against unrun entries.
- Negative executed entries are valid negative evidence for those entries.
- Reconstructed paths must stay labeled reconstructed even if they are
  full-scale.
- Provider fallback must be disclosed separately from benchmark result.

## If Only A Partial Matrix Ran

Use wording like:

```text
The run covers <N> of 80 Table 1 entries. It is a partial matrix, not a full
Table 1 reproduction. Aggregate Table 1 claims remain blocked until all required
entries are executed and parsed, or until the report explicitly scopes a partial
matrix claim.
```

If the partial matrix contains negative entries:

```text
The negative entries are valid entry-level evidence. They do not by themselves
settle the paper-level aggregate Table 1 claims.
```

## If Cost Or Time Stops The Runner

Use wording like:

```text
Execution stopped because the approved budget or time window was reached. This
is a reproduction-completeness limitation, not a claim failure for unrun entries.
Executed entries retain their entry-level verdicts; unrun entries remain
incomplete.
```

The report should list:

- approved tier
- entries completed
- entries stopped before launch
- total observed tokens
- total estimated dollar cost if available
- stop condition
- approval artifact
- missing metadata

## If Only OpenAI Routes Ran

Use wording like:

```text
This run is limited to `openai/...` provider routes using the direct OpenAI
fallback. It does not cover the non-OpenAI paper model routes in the Table 1
matrix. The evidence is therefore provider-scoped and must be labeled
`partial_matrix` plus `provider_fallback`.
```

Context to cite:

- The overnight operation log records OpenRouter HTTP 402 insufficient credits.
- The direct OpenAI probe succeeded for `openai/gpt-5.4-nano`.
- `model_route_mapping.template.json` lists non-OpenAI routes that are not
  solved by direct OpenAI fallback.

## If Non-OpenAI Routes Are Provider-Unavailable

Use wording like:

```text
Non-OpenAI paper model routes were not executed because the configured provider
path was unavailable or unapproved. This prevents full matrix completeness, but
does not indicate that the SkillGen claim failed for those unrun routes.
```

The report should list each unavailable route, provider error, and attempted
fallback. If no attempted execution happened for a route, say that plainly.

## If Reconstructed ALFWorld Is Expensive

Use wording like:

```text
ALFWorld entries use a canonical-source reconstructed SkillGen adapter path,
not an author-original SkillGen ALFWorld runner. High cost or long wall time on
this path limits reconstructed validation coverage. Positive results can support
at most partial reconstructed evidence unless the author-original ALFWorld
runner/split is found.
```

The report should cite:

- `reconstructed_validation_path_index.md`
- `benchmark_execution_plan.json`
- ALFWorld deviation note and split manifest, if the run used them
- the per-entry cost report produced from `full_matrix_cost_report_template.md`

## If A Specific Entry Is Negative

Use wording like:

```text
Entry `<entry_id>` completed and is negative entry-level evidence:
baseline=<baseline_acc>, skill=<skill_acc>, delta=<delta_acc>,
net_gain=<net_gain>. This entry-level verdict is `not_reproduced`. Aggregate
Table 1 claims are unchanged unless the full aggregation rule is satisfied.
```

For the existing observed entry, cite:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/observed_entries.json
```

## If Skills Are Repeatedly Deprecated

Use wording like:

```text
Several entries produced deprecated or failed-gate skills. Completed entries
with held-out results are negative or neutral evidence as parsed. Unrun entries
remain incomplete. The runner paused to avoid spending more budget on a pattern
that may indicate a config, dataset, or verification-gate issue.
```

This is both a cost governance issue and an evidence-quality issue. It should
not be hidden as merely a runtime failure.

## If Token Usage Is Missing

Use wording like:

```text
The entry produced benchmark outputs but is missing token usage metadata. The
entry may still be useful for claim comparison if result and trajectory evidence
are complete, but it cannot be included in cost aggregation until token usage is
recovered or the missing metadata is disclosed.
```

## If Trajectory Artifacts Are Missing

Use wording like:

```text
The entry is missing required trajectory artifacts. It should not be treated as
complete full-matrix evidence until C group either recovers the trajectories or
records an approved deviation explaining why the missing traces do not affect
the specific claim comparison.
```

## Missing Metadata / Needed From C Group

Future report patches need C group to produce:

- one cost report per entry attempt
- run-tier summary with completed, stopped, failed, and skipped entries
- per-entry start/end timestamps
- per-entry token usage and pricing basis
- route/provider error summaries
- stop reasons
- trajectory retention checks
- links between retries and original failed attempts

Without these, the report should include a "cost metadata incomplete" limitation
instead of implying full cost governance is complete.
