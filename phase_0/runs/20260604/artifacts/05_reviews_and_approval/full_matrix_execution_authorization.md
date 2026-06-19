# Full Matrix Execution Authorization

Date: 2026-06-04

Human authorization is granted for SkillGen Phase 0 full matrix preparation and execution.

No further pre-execution human gate is required for planned entries. This authorization covers per-target/per-model config generation, staged or batched runner execution, stdout/stderr capture, result capture, token-usage capture, and trajectory retention for the planned full-matrix entries.

API spending is authorized for planned entries. External code execution is authorized when it runs inside the SkillGen Phase 0 run directory or this project directory and preserves evidence under the run artifacts tree.

The ALFWorld reconstructed offline-plan adapter delivered by Group A is authorized for execution. Every ALFWorld IOD/OOD result produced through this path must be labeled exactly:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

This authorization does not make reconstructed ALFWorld evidence author-original live ALFWorld evidence. Positive reconstructed ALFWorld results can support at most `partially_reproduced` unless the author-original SkillGen ALFWorld path is found and used.

Direct OpenAI fallback is authorized for `openai/...` routes when OpenRouter is unavailable. Those entries must disclose the fallback label and must not be reported as all-provider/all-model evidence.

Non-OpenAI routes still require a technically working provider route. If a non-OpenAI route is already listed in `model_route_mapping.template.json`, it does not require another human approval before execution once the route is technically available.

Low-cost, staged, or partial runs are authorized only as partial evidence. They cannot be reported as full Table 1 reproduction. Table 1 remains 10 benchmark rows x 8 paper models = 80 entries, and partial runs cannot satisfy full-matrix aggregate claims.

Post-run evidence validation remains mandatory for every entry. A completed entry is valid evidence only if the runner verifies retained train stdout/stderr, eval stdout/stderr, parseable `eval_results.json`, `eval_results.token_usage.json`, `eval_results_trajectories/`, training run artifacts, per-round verification traces, config path, provider route, reconstructed/fallback/deviation labels, and an entry verdict based only on executed evidence.
