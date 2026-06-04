# Group F Claim Matrix Update Plan

Date: 2026-06-04

Scope: Rules for updating `all_claim_verification_matrix` when groups A-E
produce new contracts, data splits, execution plans, raw logs, parsed results,
or deviation notes.

## Matrix Inputs

The claim matrix may only be updated from visible artifacts. Chat-only
assertions are not valid evidence.

Accepted input artifact classes:

| Class | Examples |
| --- | --- |
| Source review | `A_alfworld/alfworld_source_review.md`, `D_baseline_comparison/baseline_source_identity_review.md` |
| Contract | adapter contract, split contract, ablation config matrix, transfer execution contract |
| Deviation disclosure | group-local deviation note or merged run deviation disclosure |
| Command plan | reviewed install, preparation, benchmark, aggregation command plan |
| Raw execution evidence | stdout, stderr, exit code, generated files, raw benchmark outputs |
| Parsed result | `benchmark_results.json`, target result JSON, aggregate table, trace summary |
| Claim comparison | `claim_comparison.json`, all-claim comparison rows, Figure/Table aggregate comparison |
| Human review | claim review, command review, result review, final review |

## Row Schema

Each claim row should contain or derive the following fields:

```json
{
  "claim_id": "claim_table1_entry_counts",
  "claim_type": "main_result",
  "verification_mode": "full_table1_matrix",
  "status": "blocked",
  "evidence_class": "planning_only",
  "blockers": [
    "LiveCodeBench split contract is missing."
  ],
  "evidence": [
    "ScienceWorld train/test JSON exists and can be planned."
  ],
  "artifact_inputs": [
    "artifacts/benchmark_execution_plan.json"
  ],
  "raw_log_inputs": [],
  "deviation_ids": [],
  "next_step": "Resolve structurally non-ready Table 1 rows, then aggregate the full Table 1 matrix.",
  "transition_record": {
    "previous_status": "blocked",
    "proposed_status": "blocked",
    "reason": "Planning artifacts changed, but no executable evidence changed the claim result."
  }
}
```

If the implementation cannot add all fields immediately, the integration note
beside the matrix must contain the missing values.

## Update Workflow

1. Read the current claim row and preserve its existing evidence.
2. Classify each new artifact as planning, execution, parsed result, comparison,
   or human review evidence.
3. Apply `status_transition_policy.md`.
4. Add new evidence without deleting old negative evidence or failed attempts.
5. Add or reference every relevant deviation id.
6. Recompute status counts from rows.
7. Regenerate the Markdown matrix from the JSON matrix.
8. Patch the final report only after matrix JSON and Markdown agree.

## Group Output Mapping

| Group output | Matrix effect |
| --- | --- |
| A ALFWorld adapter/split contracts | May move ALFWorld-dependent claims from `blocked` to `ready_for_execution` or `ready_for_reconstructed_execution`; cannot mark reproduced. |
| B LiveCodeBench split contract | May move Table 1 average and entry-count claims toward `ready_for_execution`; cannot mark reproduced. |
| C full matrix execution contract | May add aggregation rules and ready targets; result status changes only after execution logs and parsed deltas exist. |
| C transfer/trace contracts | May move transfer and Figure 7 claims toward ready states; no reproduction without parsed transfer or trace aggregates. |
| D baseline source identity review | May move baseline comparison from `not_testable` to `blocked_pending_source_identity_review`, `blocked_pending_reconstructed_contract`, or `ready_for_reconstructed_execution`. |
| E ablation config matrix | May move Figure 3 ablation from `not_testable` to `ready_for_reconstructed_execution` only with deviation approval. |
| F policy/report artifacts | Do not change scientific claim status by themselves; they define how future changes are integrated. |

## Claim-Specific Update Rules

### `claim_table1_average_gains_all_models`

Do not mark this claim `reproduced` until all 80 Table 1 entries have parsed
BASE/SKILL deltas for the eight paper models and ten benchmark rows.

Allowed partial evidence:

- `partially_reproduced` only if a clearly labeled subset or smoke-scale matrix
  supports average gains and the report states the missing rows.
- `not_reproduced` if a full or approved representative execution fails the
  stated gain criterion.

### `claim_table1_entry_counts`

The `50/25/5` claim must be computed from parsed per-entry deltas.

Required aggregate fields:

```json
{
  "paper_entry_count": 80,
  "observed_entry_count": 80,
  "improved_count": 50,
  "unchanged_count": 25,
  "regressed_count": 5,
  "delta_threshold_rule": "delta > 0 improved; delta = 0 unchanged; delta < 0 regressed"
}
```

### `claim_table1_alfworld_scienceworld_patterns`

ScienceWorld evidence cannot stand in for ALFWorld. The row must separately
track:

- ALFWorld IOD entries.
- ALFWorld OOD entries.
- ScienceWorld entries.
- Whether ALFWorld is exact, canonical-source reconstruction, or
  deviation-backed reconstruction.

### `claim_cross_model_transfer`

Require a transfer matrix artifact with one row per off-diagonal comparison:

```json
{
  "benchmark": "alfworld_ood",
  "source_model": "Qwen-2.5-7B",
  "evaluator_model": "GPT-5.4-Nano",
  "baseline_acc": 0.0,
  "transferred_skill_acc": 0.0,
  "delta_acc": 0.0,
  "status": "computed"
}
```

The 70% non-negative and 42% > +5 pp claims must be recomputed from this table.

### `claim_refinement_best_of_k`

Require per-round records before any status improvement:

- candidate skill id.
- baseline accuracy.
- with-skill accuracy.
- repair count.
- regression count.
- net gain.
- gate decision.
- best-so-far at K.

The Figure 7 aggregate must be derived from these records, not manually copied
from the paper.

### `claim_baseline_generator_comparison`

This claim may leave `not_testable` only after all compared baselines have:

- source identity classification.
- license and commit/tag notes.
- single-skill adapter contract.
- shared paired evaluation harness.
- deviation disclosure.

If some baselines are still missing, keep the claim `not_testable` or mark only
a separate subclaim as reconstructed-ready.

### `claim_ablation_full_wins`

This claim may leave `not_testable` only after A1-A5 and Full each have:

- intended behavior.
- implementation path.
- config or patch artifact.
- rollback/safety note.
- report wording that says reconstructed ablation unless official configs are
  found.

## Output Files

When updating the run package, write new or patched artifacts in this order:

1. group contract/deviation files.
2. `artifacts/deviation_disclosures.json` or merged
   `artifacts/hardcoding_disclosures.json`.
3. `artifacts/benchmark_execution_plan.json` if execution readiness changed.
4. `artifacts/benchmark_results.json` if raw execution output was parsed.
5. `artifacts/claim_comparison.json` if claim comparison changed.
6. `artifacts/all_claim_verification_matrix.json`.
7. `artifacts/all_claim_verification_matrix.md`.
8. `artifacts/research_validation_report.md`.

## Audit Checks

Before accepting a matrix update, check:

- Every non-terminal planning status has a concrete next step.
- Every `ready_for_execution` row has a command plan and expected outputs.
- Every `reproduced`, `partially_reproduced`, or `not_reproduced` row has raw
  execution evidence and parsed comparison.
- Every reconstructed row has a deviation disclosure.
- Status counts match the rows.
- Old negative or failed evidence is still linked.
