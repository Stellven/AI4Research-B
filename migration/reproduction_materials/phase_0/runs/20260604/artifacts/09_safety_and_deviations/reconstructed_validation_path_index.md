# Reconstructed Validation Path Index

Date: 2026-06-04

Purpose: this index centralizes every validation path in the SkillGen Phase 0 run that is not an exact author-original reproduction path. It records what was reconstructed or substituted, why it was needed, where the evidence/deviation files live, and the strongest claim status such a path can support.

## Status Rule

Unless the author-original SkillGen benchmark runner, split, config, and model route are found and used, reconstructed paths can support at most:

```text
partially_reproduced
```

They must not be labeled `reproduced` for the paper-level claim unless the report also proves that the reconstructed path is equivalent to the author-original path.

Negative reconstructed evidence is still valid evidence. If a reconstructed run executes and the skill does not improve over baseline, the correct status for that executed entry can be `not_reproduced`.

## Summary Table

| Path | Reproduction class | Why this path exists | Current state | Strongest allowed status | Primary records |
| --- | --- | --- | --- | --- | --- |
| ALFWorld IOD/OOD adapter | Canonical data plus reconstructed offline-plan adapter | Official SkillGen checkout does not include author-original ALFWorld SkillGen runner/split files | Data, adapter, grader, split manifest, and loader smoke are present; authorized reconstructed execution; must label results and validate evidence after run | `partially_reproduced` if run results are positive | `artifacts/09_safety_and_deviations/alfworld_adapter_deviation_note.md`; `artifacts/06_plans_and_contracts/alfworld_split_manifest_seed42.md`; `artifacts/06_plans_and_contracts/alfworld_run_commands.md` |
| LiveCodeBench split | Reconstructed/inferred split from open release source | Paper split files are not bundled as author-original SkillGen artifacts | Split/source contract present; execution ready as a reconstructed/open split | `partially_reproduced` if run results are positive | `artifacts/09_safety_and_deviations/livecodebench_deviation_note.md`; `artifacts/livecodebench_source_review.md`; `artifacts/livecodebench_split_contract.md` |
| Baseline generator comparison | Public-code reconstructed baseline comparison | Paper Figure 2 baseline execution artifacts and single-skill adapters are not bundled | Source identity, license exception, and adapter contract are ready; adapters have not been executed | `partially_reproduced` if reconstructed baseline comparison runs and supports the claim | `artifacts/09_safety_and_deviations/baseline_deviation_note.md`; `artifacts/06_plans_and_contracts/baseline_source_identity_review.json`; `artifacts/06_plans_and_contracts/baseline_single_skill_adapter_contract.json` |
| Ablation claim | Reconstructed ablation from paper text | Author-original A1-A5 ablation configs/scripts are not bundled | Reconstructed contract/config/smoke plan present; execution not completed | `partially_reproduced` if reconstructed A1-A5 runs support the paper pattern | `artifacts/06_plans_and_contracts/reconstructed_ablation_contract.json`; `artifacts/09_safety_and_deviations/ablation_deviation_note.md`; `artifacts/06_plans_and_contracts/ablation_config_matrix.json`; `artifacts/06_plans_and_contracts/ablation_smoke_plan.json` |
| Full-matrix single entry: `mcp_bench_single::openai/gpt-5.4-nano` | Reconstructed low-cost single-entry full-matrix execution | No mature 80-entry runner existed; one entry was manually run to prove train/eval evidence flow | Executed; negative evidence | Entry status can be `not_reproduced`; cannot support aggregate Table 1 status | `artifacts/08_results/full_matrix/observed_entries.json`; `artifacts/08_results/full_matrix/observed_entries.md` |
| Direct OpenAI fallback | Provider fallback / route substitution for `openai/...` models | OpenRouter returned HTTP 402 insufficient credits | Confirmed direct OpenAI route works for `openai/gpt-5.4-nano`; authorized for planned `openai/...` entries when OpenRouter is unavailable | Can support execution evidence for OpenAI model routes only, with fallback disclosed | `logs/phase_0_overnight_20260604/operation_log.md`; `logs/phase_0_overnight_20260604/遇到的问题.md`; `artifacts/08_results/full_matrix/observed_entries.json` |
| Non-OpenAI provider-unavailable policy | Provider diagnosis, not reproduction evidence | Non-OpenAI paper routes currently depend on OpenRouter, and OpenRouter has captured 402 insufficient-credit evidence | Runner marks 60 non-OpenAI entries as `provider_unavailable`; OpenAI entries remain selectable | None by itself; this status must not be treated as `not_reproduced` or positive evidence | `artifacts/provider_resolution_status.json`; `artifacts/06_plans_and_contracts/provider_resolution_status.md`; `artifacts/08_results/full_matrix/full_matrix_runner_state.json` |
| AIME smoke validation | Reduced POC-scale official-code smoke | Full paper Table 1 matrix was too large for initial validation; smoke used reduced instances/rounds/workers | Executed; construction-time mechanism positive, held-out AIME smoke not positive | `partially_reproduced` only for mechanism/artifact claims, not full Table 1 | `artifacts/skillgen_aime_smoke_config.yaml`; `artifacts/benchmark_results.json`; `artifacts/claim_comparison.json` |
| Token-cost smoke executions | Reduced POC-scale token logging | Paper Table 4 token-cost exact totals require full runs; reduced runs validate logging/aggregation mechanics | Several targets executed at reduced scale | `partially_reproduced` for token logging mechanics, not exact paper totals | `artifacts/benchmark_results.json`; `artifacts/06_plans_and_contracts/token_log_plan.json` |

## Detailed Records

### ALFWorld IOD/OOD

Reproduction class:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

What is canonical:

- ALFWorld repository: `https://github.com/alfworld/alfworld.git`
- Local commit recorded by A group: `aaba6870f86c5be6a08a491f32a50b906227bc3e`
- Canonical ALFWorld data release URLs are recorded in the deviation note and split manifest.
- Paper split mapping is recorded as:
  - `alfworld_iod`: train source `train`, held-out source `valid_seen`
  - `alfworld_ood`: train source `train`, held-out source `valid_unseen`

What is reconstructed:

- Conversion from ALFWorld `traj_data.json` into SkillGen `TaskInstance` JSON.
- Offline high-level planning prompt instead of live TextWorld interaction.
- Lightweight plan grader in `benchmarks/alfworld_grader.py`.
- Seed-42 stratified train/test generation.

Current delivered files:

- `code/official/data/alfworld_iod/train.json`
- `code/official/data/alfworld_iod/test.json`
- `code/official/data/alfworld_ood/train.json`
- `code/official/data/alfworld_ood/test.json`
- `code/official/scripts/prepare_alfworld.py`
- `code/official/benchmarks/alfworld_adapter.py`
- `code/official/benchmarks/alfworld_grader.py`

Load smoke evidence:

- `artifacts/08_results/raw_benchmark_outputs/alfworld_adapter_smoke/smoke_summary.json`
- `artifacts/08_results/raw_benchmark_outputs/alfworld_adapter_smoke/main_eval_loader_smoke_stdout.txt`
- `artifacts/08_results/raw_benchmark_outputs/alfworld_adapter_smoke/main_eval_loader_smoke_stderr.txt`

Execution readiness:

- `artifacts/05_reviews_and_approval/full_matrix_execution_authorization.md` authorizes reconstructed ALFWorld execution without another pre-execution human gate.
- Execution note: authorized reconstructed execution; must label results and validate evidence after run.
- Required result label: `canonical ALFWorld data + reconstructed SkillGen offline-plan adapter`.

Allowed conclusion:

- If future ALFWorld runs are positive, they can support `partially_reproduced` for ALFWorld-related claims.
- They must be disclosed as reconstructed offline-plan evidence.
- They cannot be called exact ALFWorld reproduction unless author-original SkillGen ALFWorld code is found and used.

### LiveCodeBench

Reproduction class:

```text
open-source/reconstructed split verification input
```

What is reconstructed:

- The split contract and generated split files are inferred from available open release data rather than author-bundled SkillGen split artifacts.

Primary records:

- `artifacts/09_safety_and_deviations/livecodebench_deviation_note.md`
- `artifacts/livecodebench_source_review.md`
- `artifacts/livecodebench_split_contract.md`
- `artifacts/06_plans_and_contracts/livecodebench_split_contract.md`

Allowed conclusion:

- Positive results can support partial evidence for LiveCodeBench rows.
- They should be disclosed as open-source/reconstructed split evidence unless exact author-original split artifacts are found.

### Baseline Generator Comparison

Reproduction class:

```text
public-code reconstructed baseline comparison
```

Why needed:

- The paper-level baseline comparison needs baseline systems such as Trace2Skill, SkillX, EvoSkill, and CoEvoSkills.
- The official SkillGen checkout does not bundle an author-original, already-adapted single-skill comparison runner for those baselines.

Primary records:

- `artifacts/09_safety_and_deviations/baseline_deviation_note.md`
- `artifacts/06_plans_and_contracts/baseline_source_identity_review.json`
- `artifacts/06_plans_and_contracts/baseline_source_identity_review.md`
- `artifacts/06_plans_and_contracts/baseline_single_skill_adapter_contract.json`
- `artifacts/06_plans_and_contracts/baseline_single_skill_adapter_contract.md`
- `artifacts/baseline_source_identity_human_review.json`

Current state:

- Source identity and license review are ready.
- Human approval was recorded for source identity, license exception, and adapter deviation.
- Baseline adapters have not yet been executed.

Allowed conclusion:

- Current state supports only `ready_for_reconstructed_baseline_comparison`.
- It does not yet support `partially_reproduced`.

### Reconstructed Ablation

Reproduction class:

```text
deviation-backed reconstructed ablation verification
```

Why needed:

- The paper describes ablation arms, but author-original A1-A5 configs/scripts are not bundled as directly executable artifacts.

Primary records:

- `artifacts/06_plans_and_contracts/reconstructed_ablation_contract.json`
- `artifacts/06_plans_and_contracts/reconstructed_ablation_contract.md`
- `artifacts/06_plans_and_contracts/ablation_config_matrix.json`
- `artifacts/06_plans_and_contracts/ablation_config_matrix.md`
- `artifacts/06_plans_and_contracts/ablation_smoke_plan.json`
- `artifacts/06_plans_and_contracts/ablation_smoke_plan.md`
- `artifacts/09_safety_and_deviations/ablation_deviation_note.md`

Current state:

- Reconstructed ablation execution plan exists.
- A1-A5 arms have definitions and expected outputs.
- Execution has not yet produced ablation results.

Allowed conclusion:

- Current state supports readiness only.
- Positive future execution can support `partially_reproduced`, not exact `reproduced`.

### Full-Matrix Single Entry

Reproduction class:

```text
reconstructed low-cost full-matrix single-entry execution
```

Executed entry:

```text
mcp_bench_single::openai/gpt-5.4-nano
```

Why this path exists:

- The run did not have a mature 80-entry full matrix runner.
- A single entry was manually executed to prove that train/eval commands can leave complete raw evidence.

Deviation:

- Used a low-cost generated config.
- Reduced rounds/workers/verification sample.
- Used direct OpenAI routing because OpenRouter returned 402 insufficient credits.

Primary records:

- `artifacts/08_results/full_matrix/observed_entries.json`
- `artifacts/08_results/full_matrix/observed_entries.md`
- `artifacts/raw_benchmark_outputs/full_matrix/mcp_bench_single/openai_gpt-5.4-nano/`
- `logs/phase_0_overnight_20260604/operation_log.md`

Observed result:

- Construction verification failed.
- Skill was marked `DEPRECATED`.
- Held-out eval reported `delta_acc = 0.0`.
- Entry-level verdict is `not_reproduced`.

Allowed conclusion:

- This is valid negative evidence for that one entry.
- It does not support aggregate Table 1 claims because the full matrix still requires 80 entries.

### Direct OpenAI Fallback

Reproduction class:

```text
provider fallback for openai/... routes
```

Why needed:

- OpenRouter returned:

```text
HTTP 402 insufficient credits
```

What was used:

```text
SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1
```

This makes official `llm.py` call OpenAI directly for `openai/...` routes.

Primary records:

- `logs/phase_0_overnight_20260604/operation_log.md`
- `logs/phase_0_overnight_20260604/遇到的问题.md`
- `artifacts/provider_resolution_status.json`
- `artifacts/06_plans_and_contracts/provider_resolution_status.md`
- `artifacts/08_results/full_matrix/observed_entries.json`
- `artifacts/00_run_summary/research_validation_report.md`

Allowed conclusion:

- It can support execution evidence for `openai/...` model routes when disclosed.
- It does not solve non-OpenAI model routes such as Gemma, Llama, Mistral, Qwen, Claude, or Grok.

Current provider policy:

- `openai/...` routes are selectable with `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1`.
- Non-OpenAI routes are marked `provider_unavailable` while OpenRouter 402 evidence is present.
- `provider_unavailable` is an execution availability status, not a benchmark result.
- Non-OpenAI paper models must not be replaced by OpenAI models for Table 1 reproduction.

### Non-OpenAI Provider-Unavailable Policy

Reproduction class:

```text
provider diagnosis, not reproduction evidence
```

Current diagnosis:

- `OPENROUTER_API_KEY` exists, but captured stderr includes OpenRouter 402 insufficient-credit evidence.
- `OPENAI_API_KEY` exists, so OpenAI paper routes can use direct OpenAI fallback.
- Direct provider keys for Anthropic, Google/Gemini, Mistral, xAI, Groq, Together, Fireworks, and DeepInfra were not detected in the current key inventory.
- The current runner only has direct fallback for `openai/...`; it does not yet implement direct non-OpenAI provider routing.

Primary records:

- `artifacts/provider_resolution_status.json`
- `artifacts/provider_resolution_status.md`
- `artifacts/06_plans_and_contracts/provider_resolution_status.json`
- `artifacts/06_plans_and_contracts/provider_resolution_status.md`
- `artifacts/08_results/full_matrix/full_matrix_runner_state.json`
- `artifacts/08_results/full_matrix/full_matrix_runner_state.md`

Allowed conclusion:

- This diagnosis allows the full-matrix runner to continue with executable OpenAI entries instead of blocking the entire matrix.
- It does not provide positive or negative benchmark evidence for non-OpenAI paper models.
- If OpenRouter credits/key are repaired, or if reviewed direct provider integrations are added, the same entries can move out of `provider_unavailable` and be executed.

### AIME Smoke / Reduced POC-Scale Config

Reproduction class:

```text
official-code reduced smoke validation
```

Why needed:

- Initial Phase 0 validation needed a low-cost executable target before attempting the full paper matrix.

Primary records:

- `artifacts/skillgen_aime_smoke_config.yaml`
- `artifacts/benchmark_results.json`
- `artifacts/benchmark_results.md`
- `artifacts/claim_comparison.json`
- `artifacts/claim_comparison.md`

Allowed conclusion:

- Can support partial evidence for paired-comparison mechanics and auditable skill artifact mechanics.
- Cannot support full Table 1 reproduction.

### Token-Cost Smoke Executions

Reproduction class:

```text
reduced POC-scale token logging and aggregation evidence
```

Why needed:

- Exact Table 4 token-cost reproduction requires full benchmark-scale runs.
- Reduced runs validate whether official code records token usage in parseable files.

Primary records:

- `artifacts/benchmark_results.json`
- `artifacts/benchmark_results.md`
- `artifacts/06_plans_and_contracts/token_log_plan.json`
- `artifacts/06_plans_and_contracts/token_log_plan.md`
- Raw target outputs under `artifacts/08_results/raw_benchmark_outputs/`

Allowed conclusion:

- Can support `partially_reproduced` for token logging mechanics.
- Cannot support exact paper token totals until full Table 4-scale runs are executed.

## Reporting Requirements For Future Runs

Every future result produced through one of these paths must include:

- reproduction class,
- exact command or runner used,
- config path,
- model route and provider path,
- dataset source and split manifest,
- stdout/stderr paths,
- raw result JSON paths,
- token usage files,
- per-round training traces,
- held-out eval trajectories,
- claim impact,
- strongest allowed status.

If a run uses a reconstructed path and produces positive results, report:

```text
partially_reproduced, with reconstructed-path disclosure
```

If a run uses a reconstructed path and produces negative results, report:

```text
not_reproduced for the executed reconstructed scope
```

Do not silently merge reconstructed results with author-original reproduction results.
