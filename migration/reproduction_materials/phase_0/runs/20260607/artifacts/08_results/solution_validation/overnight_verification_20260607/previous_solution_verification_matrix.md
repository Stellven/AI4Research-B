# Previous Solution Verification Matrix

Date: 2026-06-07

Scope: solution validation only. This matrix does not claim paper
reproduction.

| Solution area | Status | Evidence path | Remaining gap | Next action |
|---|---|---|---|---|
| Local Ollama no-external-API routing | `partially_validated` | `gemma3_12b/solution_validation_result.json`, `gemma3_4b/solution_validation_result.json`, `gemma3_4b_stratified/solution_validation_result.json`, `preflight.md`, `confirmation_run_blocked.md` | Prior completed runs show local Ollama routing works when the local HTTP path is permitted, but this no-approval session cannot start a new local HTTP confirmation run. | Run a bounded confirmation only after local Ollama access is pre-approved or available without escalation. |
| OpenAI/OpenRouter key disabling | `validated` | `gemma3_4b_stratified/environment_manifest.md`, `gemma3_4b_stratified/solution_validation_result.json`, `hash_embedding_verification.md` | No observed gap for completed commands. | Keep explicit `env -u OPENAI_API_KEY -u OPENROUTER_API_KEY` in benchmark command templates. |
| Deterministic hash embeddings | `validated` | `tests/test_skillgen_hash_embedding.py`, `hash_embedding_verification.md` | No observed gap for deterministic local embedding behavior. | Keep test in suite to prevent accidental OpenAI embedding fallback in local mode. |
| Stratified verification sampling | `validated` | `tests/test_skillgen_verification_sampling.py`, `sampler_verification.md`, `gemma3_4b_stratified/artifacts/runs/20260606-105511/verification/round_1/verification_summary.json` | No observed gap for the covered sampling shapes. | Keep unit coverage and real-run verification summary. |
| SkillGen train path execution | `partially_validated` | `gemma3_12b/train_command_status.json`, `gemma3_4b/train_command_status.json`, `gemma3_4b_stratified/train_command_status.json`, `artifact_completeness_report.md` | Completed for `gemma3_12b`, `gemma3_4b`, and `gemma3_4b_stratified`; failed or partial for `llama3.1_latest`, `llama3.1_latest_ctx8192`, and `qwen3_8b`. | Treat larger-model runs as failed/blocked evidence unless resource and context issues are addressed. |
| Construction verification trace preservation | `partially_validated` | `gemma3_4b_stratified/artifacts/runs/20260606-105511/verification/round_1/verification_summary.json`, `skill_traceability_audit.md`, `trace_inventory.md` | Verification metrics and case ids are preserved, but candidate id to persisted skill id mapping is not machine-checkable. | Add `source_candidate_id` to persisted skills and/or a finalization mapping artifact. |
| Held-out eval execution | `partially_validated` | `gemma3_4b/eval_results.json`, `gemma3_4b_stratified/eval_results.json`, `artifact_completeness_report.md` | Held-out eval ran for `gemma3_4b` and `gemma3_4b_stratified`; not run for no-skill, failed, or partial runs. The stratified held-out sample had no baseline failures, so out-of-sample repair was not tested. | Run another bounded confirmation with a held-out sample that contains baseline failures. |
| Generated skill effectiveness | `not_validated` | `gemma3_4b/solution_validation_result.json`, `gemma3_4b_stratified/solution_validation_result.json`, `gemma3_4b_stratified/eval_results.json` | The post-fix active skill regressed one held-out case: baseline `16/16`, skill `15/16`, net gain `-1`. | Do not claim skill effectiveness until a held-out run shows positive net gain with preserved trajectories. |
| Permission/resource runbook | `partially_validated` | `preflight.md`, `confirmation_run_blocked.md`, `artifact_completeness_report.md`, larger-model aborted/stalled notes under `llama3.1_latest` | The runbook successfully avoided approvals and documented blocked local HTTP access, but cannot solve the permission/resource blockage itself. | Pre-approve local Ollama benchmark command or run from an environment where local HTTP is available without escalation. |
| Evidence completeness | `partially_validated` | `artifact_completeness_report.md`, `artifact_completeness_report.json`, `trace_inventory.md` | `gemma3_4b` and `gemma3_4b_stratified` are complete; `gemma3_12b` is missing eval command status because no skill eval ran; larger-model runs are partial/failed. | Backfill placeholders for missing artifacts only if useful, but do not reinterpret failed runs as completed evidence. |

## Bottom Line

Validated:

- deterministic hash embeddings;
- stratified verification sampling;
- explicit external API key disabling in completed command templates.

Partially validated:

- local Ollama routing;
- SkillGen train path;
- construction verification trace preservation;
- held-out eval execution;
- permission/resource evidence handling;
- artifact completeness across the broader result set.

Not validated:

- generated skill effectiveness on held-out MCP-Bench cases.

Blocked in this no-approval session:

- new independent confirmation benchmark requiring local Ollama HTTP access.
