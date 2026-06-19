# Per-Round Trace Retention Checklist

Minimum per-round trace retention checklist for future SkillGen full/refinement runs

Status: `ready_for_execution`

## Retention Policy

- Do not delete or overwrite verification/round_* directories after selecting the final skill.
- Store round artifacts under target/model/run-specific directories so retries cannot replace earlier evidence.
- Every future full-matrix or Figure 7 run must fail validation if a required trace file is missing.
- A parsed aggregate may be regenerated from raw traces, but raw traces must remain the primary evidence.

## Required Files

| Check | Required | Current count | Purpose |
| --- | --- | --- | --- |
| `verification_baseline` | `True` | `0` | Recompute baseline outcomes and identify cases repaired by candidate skills. |
| `verification_with_skill` | `True` | `0` | Recompute with-skill outcomes and identify regressions. |
| `verification_summary` | `True` | `0` | Read paired_n, accuracy, repair, regression, net_gain, and gate pass/fail per round. |
| `verification_case_analyses` | `True` | `0` | Preserve per-case repair/regression explanations for audit and Figure 7 debugging. |
| `candidate_skill_artifact` | `True` | `0` | Link each round's result to the candidate skill that was evaluated. |
| `run_metadata` | `True` | `0` | Preserve benchmark, model, dataset, config, route, and execution metadata for grouping. |
| `token_usage` | `False` | `0` | Support token-cost and runtime diagnostics without mixing them into Figure 7 accuracy. |
