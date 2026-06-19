# Skill Traceability Audit

Date: 2026-06-07

## Scope

Audit the id mismatch noted in the `gemma3_4b_stratified` result package:

- construction verification summary records candidate id
  `8358dd90-a6d9-4306-a03d-51d6c0b0972e`;
- persisted active skill and held-out eval record skill id
  `bd029056-5133-4626-b151-3a21e8e67ea2`.

## Evidence

Construction verification summary:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b_stratified/artifacts/runs/20260606-105511/verification/round_1/verification_summary.json
```

Relevant fields:

```json
{
  "verification_summary_skill_id": "8358dd90-a6d9-4306-a03d-51d6c0b0972e",
  "target_failure_ids": [
    "call_for_papers_001",
    "movie_recommender_001"
  ],
  "boundary_success_ids": [
    "medical_calculator_001",
    "nasa_data_000"
  ],
  "result": {
    "passed": true,
    "net_gain": 1,
    "repaired_ids": [
      "call_for_papers_001",
      "movie_recommender_001"
    ],
    "regression_ids": [
      "medical_calculator_001"
    ]
  }
}
```

Candidate artifact:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b_stratified/candidates/8358dd90-a6d9-4306-a03d-51d6c0b0972e_gen.json
```

Relevant fields:

```json
{
  "candidate_id": "8358dd90-a6d9-4306-a03d-51d6c0b0972e",
  "analysis_id": "fd7320a8-5d77-455a-abf5-20384ea02fef",
  "body_length": 5347
}
```

Persisted active skill:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b_stratified/skill_output/2026-06-06_10-55-11/bd029056-5133-4626-b151-3a21e8e67ea2.json
```

Relevant fields:

```json
{
  "skill_id": "bd029056-5133-4626-b151-3a21e8e67ea2",
  "status": "active",
  "version": 1,
  "token_count": 738,
  "verification_history": [
    {
      "round_idx": 0,
      "passed": true,
      "net_gain": 1,
      "repair_count": 2,
      "regression_count": 1,
      "baseline_acc": 0.5,
      "skill_acc": 0.75
    }
  ]
}
```

Held-out eval:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b_stratified/eval_results.json
```

Relevant fields:

```json
{
  "skill_id": "bd029056-5133-4626-b151-3a21e8e67ea2",
  "skill_status": "active",
  "skill_rejected": false,
  "results": [
    {
      "model": "gemma3:4b",
      "skill_id": "bd029056-5133-4626-b151-3a21e8e67ea2",
      "baseline_acc": 1.0,
      "skill_acc": 0.9375,
      "net_gain": -1
    }
  ]
}
```

## Assessment

Status: `partially_validated`

The mismatch is explainable: construction verification ran on a generated
candidate artifact, while held-out eval ran on the finalized persisted skill.
The active skill preserves verification metrics in `verification_history`, and
the candidate artifact preserves `candidate_id`, so the trace can be followed
manually.

This is not evidence that the wrong skill was evaluated. It is, however, a
traceability issue because the persisted skill does not record the source
`candidate_id`, and the verification summary uses `skill_id` for what is
actually a candidate id.

## Recommended Fix

Add explicit fields during finalization:

- `source_candidate_id` on the persisted skill;
- `persisted_skill_id` in `verification_summary.json` after finalization, or a
  separate finalization trace artifact mapping candidate id to skill id.

This would make the trace machine-checkable instead of relying on manual
comparison of files.
