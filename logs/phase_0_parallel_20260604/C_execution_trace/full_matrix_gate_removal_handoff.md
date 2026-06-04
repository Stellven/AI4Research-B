# Full Matrix Gate Removal Handoff

Date: 2026-06-04

Handled group: Group C - full matrix execution runner and execution preparation.

## Pre-Execution Gates Removed

- Removed the remaining pre-execution human gate for planned full-matrix entries.
- Authorized API spending for planned entries.
- Authorized external code execution inside the run/project directory.
- Authorized per-target/per-model config generation.
- Authorized direct OpenAI fallback for `openai/...` routes when OpenRouter is unavailable.
- Authorized Group A's ALFWorld reconstructed offline-plan adapter for runner execution.
- Authorized low-cost, staged, and partial runs as partial evidence only.

Authorization artifacts:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/05_reviews_and_approval/full_matrix_execution_authorization.md
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/full_matrix_execution_authorization.md
```

## Gates That Remain

Post-run evidence validation remains mandatory for every entry. The runner must validate:

- train stdout/stderr retention
- eval stdout/stderr retention
- parseable `eval_results.json`
- `eval_results.token_usage.json`
- `eval_results_trajectories/`
- training run artifacts
- `verification/round_*` traces
- recorded config path
- recorded provider route
- recorded reconstructed/fallback/deviation labels
- entry verdict based only on executed evidence

This gate was not removed.

## ALFWorld Runner Readiness

ALFWorld IOD/OOD are executable from the runner perspective for reconstructed execution.

Required label for every ALFWorld result:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

This does not make the result author-original live ALFWorld evidence. Positive ALFWorld reconstructed results can support at most `partially_reproduced`.

## Entries Immediately Attemptable

Immediate attempt path is OpenAI-first with direct fallback enabled by default:

- `alfworld_iod::GPT-5.4-Nano`
- `alfworld_iod::GPT-5.4-Mini`
- `alfworld_ood::GPT-5.4-Nano`
- `alfworld_ood::GPT-5.4-Mini`
- remaining `openai/...` routes across ready Table 1 rows after the first batch

Latest dry-run state:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/full_matrix_runner_state.json
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/full_matrix_runner_state.md
```

Dry-run counts:

```text
not_started: 4
budget_stopped: 15
completed_invalid_evidence: 1
provider_unavailable: 60
```

The existing `completed_invalid_evidence` entry is historical single-entry evidence that does not satisfy the new mandatory evidence checklist.

## Still Technically Blocked

Non-OpenAI routes are not blocked by human approval anymore. They are marked `provider_unavailable` until a technically working provider route is available:

- Anthropic route entries
- Google/Gemma route entries
- xAI/Grok route entries
- Meta/Llama route entries
- Mistral route entries
- Qwen route entries

If a route is already listed in `model_route_mapping.template.json`, no additional human approval is required once it works technically.

## Updated Plan Artifacts

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/benchmark_execution_plan.json
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/benchmark_execution_plan.md
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_contract.json
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_contract.md
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/alfworld_run_commands.md
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/reconstructed_validation_path_index.md
```

Root-level mirrors were also updated where the run already uses root mirrors.

## Runner Implementation

Runner code:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/ai4research_b/phase0/skillgen_automation.py
```

Supported behavior:

- per-entry execution
- resume/skip already completed entries
- dry-run mode
- `--max-entries`
- repeated `--target`
- repeated `--model`
- direct OpenAI fallback for `openai/...`
- stdout/stderr capture
- train/eval result capture
- token usage capture
- trajectory retention validation
- per-round verification trace validation
- required runner statuses: `not_started`, `running`, `completed_valid_evidence`, `completed_invalid_evidence`, `failed_to_run`, `provider_unavailable`, `budget_stopped`
- per-entry deviation label retention

## First Command For Next Agent

Run one bounded OpenAI ALFWorld entry first. This is an execution command, not a full 80-entry matrix:

```bash
python3 -m ai4research_b.phase0.skillgen_automation run-full-matrix \
  --run-dir phase_0/runs/skillgen_phase0_thorough_20260602 \
  --max-entries 1 \
  --target alfworld_iod \
  --model GPT-5.4-Nano \
  --max-workers 1 \
  --max-refine-rounds 1 \
  --verification-sample-size 4
```

Direct OpenAI fallback is enabled by default. Do not add `--include-non-openai` until non-OpenAI provider route execution is technically working.

## Verification Performed

Commands run:

```bash
python3 -m ai4research_b.phase0.skillgen_automation run-full-matrix --run-dir phase_0/runs/skillgen_phase0_thorough_20260602 --dry-run --max-entries 4
python3 -m unittest discover tests
```

Result:

```text
dry_run_completed
11 tests passed
```

No full 80-entry matrix execution was run.
