# Per-Round Trace Retention Checklist

Status: `ready_for_future_runs`

This checklist defines the minimum evidence that future full-matrix, transfer,
and Figure 7 runs must retain.

## Required Artifacts

| Artifact | Required | Purpose |
| --- | --- | --- |
| `verification/round_*/verification_baseline.jsonl` | yes | Recompute baseline outcomes and identify repaired cases. |
| `verification/round_*/verification_with_skill.jsonl` | yes | Recompute with-skill outcomes and identify regressions. |
| `verification/round_*/verification_summary.json` | yes | Read paired count, accuracy, repair, regression, net gain, and gate fields. |
| `verification/round_*/verification_case_analyses.json` | yes | Preserve per-case repair/regression explanations for audit. |
| `candidates/*_gen.json` | yes | Link each evaluated round to the candidate skill artifact. |
| `run_metadata.json` | yes | Preserve benchmark, model, dataset, route, config, and execution metadata. |
| `token_usage.json` | optional for Figure 7 | Support token/cost diagnostics without mixing them into accuracy aggregation. |

## Retention Rules

- Do not delete `verification/round_*` directories after selecting the final skill.
- Do not overwrite previous retry artifacts; retries need unique run directories or retry ids.
- Keep raw traces as primary evidence. Parsed summaries can be regenerated from them.
- Full-matrix and Figure 7 validation should fail if any required per-round file is missing.
- Store output paths under target/model/run-specific directories so parallel runs cannot collide.

## Next Run Gate

Before executing a paper-scale run, the command plan must explicitly state that
all required per-round artifacts will be retained in the run directory and
included in the final artifact index.
