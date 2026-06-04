# Phase 0 SkillGen Supervisor Repair Plan

Date: 2026-06-04

Role: supervisor / integration owner

Purpose:

This document repairs the parallel-group repair plan after reviewing
`logs/phase_0_parallel_20260604/repair log.md` and the generated artifacts.
It is the coordination layer that future agents should use before executing
large API runs or changing claim statuses.

## 1. Supervisor Finding

The parallel work was useful, but it did not finish claim verification.

The main improvement is:

```text
Before: several claims looked impossible or undefined.
After: most claims have a proposed verification path, contracts, and deviation language.
```

The main remaining problem is:

```text
The project now mixes claim verdict status with execution readiness status.
```

This is causing inconsistent artifacts. For example:

- `all_claim_verification_matrix` says some claims are `ready_for_execution`.
- `research_validation_report` still reports older verdicts for the same claims.
- `automation_state.json` has status counts that do not match the latest matrix.
- Some historical executed evidence was effectively downgraded to planning status.

This must be fixed before spending a large API budget.

## 2. Required Status Model Repair

From now on, every claim row must separate two fields:

```text
claim_verdict_status
execution_readiness_status
```

Do not use one field to mean both.

### 2.1 Claim Verdict Status

This answers:

```text
What does existing evidence currently prove about the paper claim?
```

Allowed values:

```text
reproduced
partially_reproduced
not_reproduced
failed_to_run
blocked
not_testable
out_of_scope
```

These statuses require evidence. A plan alone cannot produce `reproduced`,
`partially_reproduced`, or `not_reproduced`.

### 2.2 Execution Readiness Status

This answers:

```text
Can we run the next validation attempt, and what kind of run would it be?
```

Allowed values:

```text
not_ready
contract_ready
ready_for_human_review
ready_for_execution
ready_for_reconstructed_execution
ready_for_smoke_execution
ready_for_source_identity_review
executed
```

Execution readiness does not replace the claim verdict.

Example:

```text
claim_tau_bench_gate_activated:
  claim_verdict_status: not_reproduced
  execution_readiness_status: ready_for_execution
```

This means:

```text
The existing smoke evidence failed to support the claim,
but the target can be rerun at larger scale.
```

## 3. Corrected Current State

This section is the supervisor's corrected interpretation of the current state.

| Claim | Correct current verdict | Correct readiness | Notes |
| --- | --- | --- | --- |
| `claim_method_paired_intervention` | `partially_reproduced` | `ready_for_full_matrix_execution_after_dependencies` | Existing AIME smoke output has paired fields. Do not downgrade to `blocked`. |
| `claim_table1_average_gains_all_models` | `blocked` | `partially_ready_full_matrix` | LiveCodeBench is ready; ALFWorld IOD/OOD still need data, adapter, split files, smoke logs, and approval. |
| `claim_table1_entry_counts` | `blocked` | `partially_ready_full_matrix` | Same dependency as Table 1 average gains. Needs all 80 deltas. |
| `claim_table1_alfworld_scienceworld_patterns` | `blocked` | `ready_for_reconstructed_alfworld_implementation` | Group A contract exists. No ALFWorld execution yet. |
| `claim_baseline_generator_comparison` | `blocked` | `ready_for_source_identity_review` | No longer a dead-end `not_testable`, but still no baseline repos cloned/pinned/approved. |
| `claim_ablation_full_wins` | `blocked` | `ready_for_reconstructed_ablation_human_review` | Group E has a reconstructed plan. No ablation smoke run yet. |
| `claim_cross_model_transfer` | `blocked` | `blocked_by_alfworld_ood_execution` | Transfer contract exists. Still needs ALFWorld OOD executable data/adapter/split. |
| `claim_tau_bench_gate_activated` | `not_reproduced` | `ready_for_execution` | Preserve existing negative smoke evidence. Rerun does not erase it. |
| `claim_chemllmbench_useful_gains` | `not_reproduced` | `ready_for_execution` | Preserve existing negative smoke evidence. |
| `claim_refinement_best_of_k` | `blocked` | `ready_for_trace_generation_after_full_runs` | Trace contract exists. Needs full/reconstructed runs with per-round traces. |
| `claim_token_cost` | `partially_reproduced` | `ready_for_full_token_cost_execution` | Token logging mechanics were shown at POC scale. Do not mark only `ready_for_execution`. |
| `claim_auditable_skill_artifact` | `partially_reproduced` | `ready_for_full_scope_artifact_check` | Smoke skill artifact exists. Do not downgrade to `blocked`. |

## 4. Immediate Repair Tasks Before Any Large API Run

These are required before executing expensive benchmarks.

### R0: Reconcile Status Artifacts

Owner: integration agent

Status: completed on 2026-06-04.

Goal:

```text
Make matrix, report, and automation_state agree.
```

Tasks:

1. Add or emulate separate fields for `claim_verdict_status` and
   `execution_readiness_status`.
2. Regenerate or patch:
   - `artifacts/02_claims/all_claim_verification_matrix.json`
   - `artifacts/02_claims/all_claim_verification_matrix.md`
   - `artifacts/00_run_summary/research_validation_report.md`
   - `artifacts/00_run_summary/automation_state.json`
3. Preserve all prior negative and partial evidence.
4. Do not let a `ready_for_*` readiness status replace an evidence verdict.

Acceptance:

```text
The same claim has the same verdict everywhere.
The same claim has the same readiness everywhere.
Status counts are computed from verdict status, not readiness status.
```

Implementation result:

- `all_claim_verification_matrix.json` now uses schema `0.3`.
- `status` is retained only as a backward-compatible alias for
  `claim_verdict_status`.
- `status_counts` and `claim_verdict_status_counts` are computed from verdicts
  only.
- `readiness_status_counts` is separate and contains the `ready_for_*` /
  next-execution states.
- `automation_state.json` now records both
  `all_claim_verdict_status_counts` and `all_claim_readiness_status_counts`.
- Root artifact copies and categorized copies are synchronized for the matrix,
  report, and automation state.

### R1: Fix Report Language For Planning-Only Claims

Owner: report integration agent

Status: completed on 2026-06-04.

Planning-only artifacts must not be described as validation evidence.

Specifically:

```text
Group A ALFWorld contract = planning/contract evidence, not benchmark evidence.
Group C matrix/trace contracts = planning/aggregation evidence, not result evidence.
Group D baseline source review = planning/source-identity evidence, not Figure 2 evidence.
Group E ablation contract = planning/deviation evidence, not Figure 3 evidence.
Group F policy = integration governance, not scientific evidence.
```

Acceptance:

```text
Final report uses phrases like:
"execution path defined"
"reconstructed contract ready for review"
"execution pending"

It must not imply:
"claim reproduced"
"paper result verified"
"full benchmark completed"
```

Implementation result:

- The research validation report now labels claim-level columns as
  `Claim verdict` and `Execution readiness`.
- Report details separate `Validation evidence` from
  `Planning/readiness evidence`.
- The former all-purpose `Evidence Files` section is split into:
  `Validation Evidence Files`, `Planning And Readiness Artifacts`, and
  `Raw Output Files`.
- Planning-only Group A/C/D/E artifacts no longer upgrade a claim verdict to
  `ready_for_*`; those states now live only in execution readiness.

### R2: Freeze Original Agent Repair Log

Owner: supervisor

`logs/phase_0_parallel_20260604/repair log.md` should remain as an organized
historical record. Do not paraphrase or edit original group report blocks.

Future corrections should go into this supervisor plan or new integration
artifacts, not into the original repair log.

## 5. Corrected Group-by-Group Maturity

### Group A - ALFWorld

Current maturity:

```text
contract mature
implementation immature
execution not started
```

What is solid:

- Source identity is reviewed.
- IOD/OOD mapping is documented.
- Adapter/split/deviation contracts exist.
- Automation detects the contract state.

What is missing:

- ALFWorld canonical data downloaded inside run directory.
- Actual SkillGen ALFWorld adapter implementation.
- Generated IOD/OOD `TaskInstance` train/test JSON files.
- Smoke run proving the adapter works.
- Human approval for reconstructed execution.

Correct next step:

```text
Implement and smoke-test ALFWorld before any full Table 1 or transfer run.
```

Recommended label:

```text
execution_readiness_status: ready_for_reconstructed_implementation
```

Do not label:

```text
ready_for_execution
```

until smoke data, adapter, split files, and command plan exist.

### Group B - LiveCodeBench

Current maturity:

```text
input mature
execution not started
```

What is solid:

- `release_v6_all.json` exists.
- SkillGen LiveCodeBench adapter exists.
- A deterministic 50/150 seed-42 split was generated.
- Split manifest records source indices and instance IDs.
- Execution plan marks LiveCodeBench as ready.

Risks:

- The split is inferred, not author-published exact instance IDs.
- The generated split files are large:
  - train: about 144 MB
  - test: about 766 MB
  - all source: about 4.2 GB

Correct next step:

```text
Human-review inferred split and run a LiveCodeBench smoke/limited execution before full matrix.
```

Recommended labels:

```text
claim_verdict_status: blocked for Table 1 claims until execution
execution_readiness_status: ready_for_execution
evidence_class: paper_matching_inferred_split
```

### Group C - Matrix / Transfer / Trace

Current maturity:

```text
contract mature
execution orchestration pending
```

What is solid:

- Full matrix contract defines 80 entries.
- Transfer contract defines 120 off-diagonal comparisons.
- Figure 7 trace contract defines per-round extraction needs.
- Retention checklist prevents losing trace evidence.

What is missing:

- Actual full matrix execution manifest populated with all final train/test paths.
- Transfer execution commands using generated source skills and evaluator baselines.
- Trace extraction code or script that reads run artifacts and emits Figure 7 records.
- Parsed result aggregators wired into final claim comparison artifacts.

Correct next step:

```text
After A/B readiness is reconciled, generate command plans and dry-run artifact paths.
```

Do not run full API matrix until R0/R1 status reconciliation and ALFWorld smoke pass.

### Group D - Baseline Comparison

Current maturity:

```text
planning mature
source identity not complete
execution not ready
```

What is solid:

- Four candidate public repos are identified.
- Single-Markdown-skill adapter constraints are defined.
- Deviation language exists.
- Automation has planning artifacts.

What is missing:

- Repos cloned inside run directory.
- Commit hashes pinned.
- Licenses inspected locally.
- Human identity review.
- Actual adapters from each native baseline to one Markdown skill.
- Any baseline execution.

Correct next step:

```text
Clone/pin/license-review the four repos inside the run directory, then human-review identity.
```

Recommended labels:

```text
claim_verdict_status: blocked
execution_readiness_status: ready_for_source_identity_review
```

Do not label:

```text
ready_for_reconstructed_baseline_comparison
```

until source identity and adapter feasibility are approved.

### Group E - Reconstructed Ablation

Current maturity:

```text
contract moderate
execution risky
smoke not run
```

What is solid:

- A1-A5 arms are defined.
- Config matrix and smoke plan exist.
- Deviation note exists.

Major risks:

- A3 intentionally disables the verification gate; this is a safety-relevant deviation.
- A4 may require prompt/code patching; post-processing is weaker evidence.
- A1 demonstration selection may materially affect results.
- No smoke run has validated mechanical feasibility.

Correct next step:

```text
Human-review A1-A5, especially A3/A4, then run ablation smoke only.
```

Recommended labels:

```text
claim_verdict_status: blocked
execution_readiness_status: ready_for_reconstructed_ablation_human_review
```

Do not label:

```text
claim_ablation_full_wins: ready_for_reconstructed_ablation_execution
```

until human review approves A1-A5 and the smoke command plan.

### Group F - Evidence / Report Integration

Current maturity:

```text
policy useful
integration not yet applied correctly
```

What is solid:

- Status transition policy exists.
- Deviation template exists.
- Matrix update plan exists.
- Report patch plan exists.

What is missing:

- Policy has not been fully applied to current artifacts.
- Current matrix/report/automation_state disagree.
- Policy still needs the verdict/readiness split formalized.

Correct next step:

```text
Apply R0/R1, then update policy files to explicitly require separate verdict and readiness fields.
```

## 6. Large API Spend Gate

The user has granted permission to spend a large API budget. That permission
does not mean every large run should start immediately.

Large API execution is allowed only after the relevant gate below is satisfied.

### Gate For Full Table 1

Required before spending:

```text
1. R0/R1 status reconciliation completed.
2. LiveCodeBench split human-reviewed.
3. ALFWorld canonical data downloaded inside run directory.
4. ALFWorld adapter implemented.
5. ALFWorld IOD/OOD split files generated.
6. ALFWorld smoke run passed and logs preserved.
7. Full matrix command plan generated.
8. Model routes and API budget approved.
9. Per-round trace retention enabled.
```

### Gate For Figure 4 Transfer

Required before spending:

```text
1. ALFWorld OOD execution path smoke-tested.
2. Transfer execution contract populated with actual source skill paths.
3. Evaluator no-skill baselines planned.
4. All 120 comparison outputs have expected paths.
5. Per-round/source skill artifacts retained.
```

### Gate For Figure 7

Required before spending:

```text
1. Full/reconstructed runs configured to retain verification/round_* files.
2. Candidate skill artifacts retained per round.
3. Trace extraction script/contract tested on existing smoke traces.
4. Aggregation formula approved.
```

### Gate For Figure 2 Baseline Comparison

Required before spending:

```text
1. Four public baseline repos cloned inside run directory.
2. Commit and license recorded.
3. Human identity review complete.
4. Single-Markdown-skill adapters implemented or proven feasible.
5. Smoke run for one baseline succeeds.
```

### Gate For Figure 3 Ablation

Required before spending:

```text
1. Human review approves A1-A5 reconstructed behavior.
2. A3 safety-gate disable is explicitly approved.
3. A4 prompt/code patch approach is selected.
4. Ablation smoke plan runs successfully.
5. Paper-target matrix is defined.
```

## 7. Repaired Execution Order

Use this order from here.

### Step 1 - Reconcile Artifacts

Do R0/R1 before anything expensive.

Deliverables:

```text
consistent all_claim_verification_matrix
consistent research_validation_report
consistent automation_state
status model patch note
```

### Step 2 - ALFWorld Implementation Smoke

Do not start full Table 1 until ALFWorld smoke passes.

Deliverables:

```text
downloaded ALFWorld data manifest
ALFWorld adapter implementation note
IOD/OOD split manifest
smoke stdout/stderr
smoke eval_results.json
claim readiness update
```

### Step 3 - LiveCodeBench Smoke

Verify the inferred split can execute.

Deliverables:

```text
human split review note
smoke command plan
smoke logs
parsed result
```

### Step 4 - Full Matrix Dry Run Plan

Generate command plan and expected output paths for all 80 entries.

Deliverables:

```text
full_matrix_command_plan.json
full_matrix_expected_outputs.md
per_round_trace_retention_enabled.md
```

### Step 5 - Execute Paid Full Matrix / Transfer / Trace Runs

Only after gates are satisfied.

### Step 6 - Baseline Source Identity

Can proceed in parallel with Steps 2-4, but do not execute baselines before
identity review and adapter smoke.

### Step 7 - Ablation Smoke

Can proceed after human review, but not before A3/A4 are explicitly approved.

### Step 8 - Final Integration

After execution:

```text
parse raw results
compute comparisons
preserve failed/negative attempts
update matrix with verdict + readiness
patch final report
write deviation summary
```

## 8. Supervisor Acceptance Standard

A repaired plan is acceptable when:

```text
1. No claim is left as unexplained not_testable.
2. Every claim has either existing evidence or a documented execution path.
3. Planning artifacts are not treated as result evidence.
4. Reconstructed paths are visibly labeled.
5. Matrix/report/automation_state agree.
6. Large API runs have command plans and approval gates.
7. Raw logs and per-round traces cannot be accidentally discarded.
```

Current state after this supervisor review:

```text
The repair plan is directionally good but not execution-ready.
The next required action is status/artifact reconciliation, not a large API run.
```
