# Phase 0 SkillGen Handoff - 2026-06-03

This document summarizes the current progress on the SkillGen Phase 0 automated claim-verification POC and the issues that remain unresolved. It is intended as the first document to read in a new session.

## Current Run

- Main run directory: `phase_0/runs/skillgen_phase0_thorough_20260602/`
- Final report: `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/research_validation_report.md`
- Claim matrix: `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/all_claim_verification_matrix.json`
- Benchmark results: `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/benchmark_results.json`
- Hardcoding/deviation disclosures: `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/hardcoding_disclosures.md`
- Official code copy: `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/`
- Automation code: `ai4research_b/phase0/skillgen_automation.py`
- Relevant tests: `tests/test_skillgen_demo.py`, `tests/test_skillgen_automation.py`

Current claim status counts:

```text
partially_reproduced: 3
not_reproduced:       2
not_testable:         2
blocked:              5
```

There are no remaining claim statuses whose only reason is API cost, API permission, model-route mapping, or "we have not tried to run it yet." Remaining unresolved items are either structural missing, not testable from the official checkout, or executed negative evidence.

## What Has Been Built

The Phase 0 POC now automates the paper-specific SkillGen verification path:

```text
paper/code intake
  -> claim catalog and benchmark claim extraction
  -> verification contract generation
  -> command plan generation
  -> approval-aware/gated execution
  -> official code execution
  -> result parsing
  -> claim comparison
  -> all-claim matrix generation
  -> final research validation report
  -> hardcoding/deviation disclosures
```

The implementation is still paper-specific. It is not yet a general arbitrary-paper claim-verification machine. The current automation understands SkillGen-specific claims, SkillGen output files, SkillGen Table 1/Table 4 row names, and the SkillGen official-code conventions.

## What Has Been Executed

The following benchmark targets have actual raw execution evidence under `artifacts/raw_benchmark_outputs/`.

| Target | Execution status | Held-out baseline | Held-out skill | Delta | Net gain | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| AIME smoke | completed | 25.0% | 25.0% | 0.0% | 0 | Executed smoke target; does not reproduce a positive held-out gain. |
| tau-Bench retail | completed | 23.3% | 23.3% | 0.0% | 0 | Executed; generated skill failed gate/deprecated, eval reports skill == baseline. |
| ChemLLMBench property | completed | 60.0% | 60.0% | 0.0% | 0 | Executed; generated skill failed gate/deprecated. |
| ChemLLMBench yield | completed | 70.0% | 70.0% | 0.0% | 0 | Executed; generated skill failed gate/deprecated. |
| ScienceWorld token smoke | completed | 31.0% | 35.0% | +4.0% | +4 | Executed positive smoke evidence at reduced POC scale. |
| PubMedQA token smoke | completed | 74.0% | 70.0% | -4.0% | -4 | Executed negative evidence at reduced POC scale. |
| Mind2Web token smoke | completed | 54.0% | 54.0% | 0.0% | 0 | First attempt hit OpenAI TPM 429; retried at lower concurrency; skill rejected/deprecated. |
| MCPBench token smoke | completed | 93.8% | 93.8% | 0.0% | 0 | Executed; skill rejected/deprecated. |

Token logs now exist for the ready Table 4 POC-scale groups: AIME, tau-Bench, ChemLLMBench property/yield, ScienceWorld, PubMedQA, Mind2Web, and MCPBench. This verifies token-log mechanics at reduced POC scale. It does not reproduce the paper's full-scale Table 4 numeric token totals.

## What Problems Were Solved

### 1. API and Cost Permission

Previously, many claims were effectively blocked because running them required paid API calls. The user explicitly allowed API use and allowed the automation to continue through non-structural cost blockers. The ready benchmark targets were executed rather than left as "blocked by cost."

This is solved for the current POC scope. Full paper-scale execution would still need an explicit budget decision because the full Table 1 matrix is much larger than this run.

### 2. Model Route Mapping

Paper model display names were mapped to runnable provider routes. OpenRouter did not have every exact display name, so equivalent route decisions were recorded. For `openai/*` models, OpenRouter credit was insufficient, so the official run used a recorded fallback that routes OpenAI model names directly to the OpenAI API.

Important deviation:

- File patched inside the run copy: `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/llm.py`
- Behavior: when `SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1`, `openai/*` chat calls go directly to OpenAI.
- Reason: OpenRouter returned insufficient-credit errors, while the OpenAI key could execute the needed model routes.
- This is disclosed in `hardcoding_disclosures.md`.

### 3. External Source Intake

The automation now distinguishes between:

- sources already bundled in the SkillGen checkout,
- paper-indicated sources that can be prepared or fetched,
- canonical external code that exists but lacks a SkillGen-compatible adapter,
- missing official runner/config support.

Prepared or executed source areas include tau-Bench, ChemLLMBench, SocialMaze UPI preparation, MCPBench-style data, ScienceWorld, PubMedQA, and Mind2Web.

This is partially solved. ALFWorld and LiveCodeBench still need structural work before they can count as runnable SkillGen reproduction targets.

### 4. Non-Structural Runtime Failures

Mind2Web initially failed because OpenAI returned a tokens-per-minute 429 rate-limit error during concurrent summarization. That was not structural. The failed logs were preserved, concurrency was reduced, and the target was rerun successfully.

Recorded deviation:

- Some generated Table 4 configs used `max_workers=4` for speed.
- Mind2Web was retried with `max_workers=1` to avoid TPM limits.
- The failed attempt logs were preserved as `train_attempt1_stdout.txt` and `train_attempt1_stderr.txt`.

### 5. Reporting and Human Readability

The final report now has:

- colored claim-level status labels,
- per-claim "compared evidence" descriptions,
- status reasons,
- next steps,
- detailed non-success explanations,
- distinction between structural blockers and executed negative evidence.

This matters because many claims are not simply "not done"; some have been run and failed to support the paper claim, while others truly cannot be run from available official-compatible artifacts.

## The Seven Issues: Current Status

| # | Issue | Current status | Detail |
| --- | --- | --- | --- |
| 1 | Need permission to run Table 1/costly commands | Solved for non-structural POC targets | The user approved API use. Ready targets were executed. Full Table 1 still depends on structural missing rows. |
| 2 | Need to find official/paper-indicated code | Mostly solved | Official SkillGen is cloned. Several paper-indicated sources were identified/prepared. ALFWorld/LiveCodeBench still need compatible contracts. |
| 3 | Need to map paper model names to runnable IDs | Solved | Model route mapping is resolved for current POC. Some route equivalences are recorded deviations. |
| 4 | Need to pull external resources/interface files | Partially solved | tau/Chem/SocialMaze/MCPBench-style resources were prepared or run. ALFWorld and LiveCodeBench remain structurally incomplete. |
| 5 | Missing official support/key structural data | Not solved | Main remaining blocker: missing adapters, split contracts, baseline runners, ablation configs, Figure 7 traces. |
| 6 | Need larger-scale testing | Partially solved | We expanded from AIME to tau, Chem, ScienceWorld, PubMedQA, Mind2Web, MCPBench. Still not full paper-scale Table 1. |
| 7 | Need all runnable tests completed | Solved for ready POC targets | Ready non-structural targets have been executed. Remaining unverified claims are structural missing/not-testable or already executed negative evidence. |

Short version: issues 1, 3, and 7 are solved for the current POC scope; issue 2 is mostly solved; issues 4 and 6 are partially solved; issue 5 remains the real wall.

## Current Claim Status

| Claim | Status | Meaning |
| --- | --- | --- |
| `claim_method_paired_intervention` | `partially_reproduced` | Official outputs show paired no-skill/with-skill fields. Evidence is smoke-scale, not full paper-scale. |
| `claim_table1_average_gains_all_models` | `blocked` | Full Table 1 needs 80 benchmark-split-model entries; ALFWorld IOD/OOD and LiveCodeBench are not execution-ready. |
| `claim_table1_entry_counts` | `blocked` | Cannot compute 50 improved / 25 unchanged / 5 regressed without the full 80-entry matrix. |
| `claim_table1_alfworld_scienceworld_patterns` | `blocked` | ScienceWorld was run, but ALFWorld still lacks a SkillGen-compatible adapter and IOD/OOD split contract. |
| `claim_baseline_generator_comparison` | `not_testable` | Official checkout lacks executable Trace2Skill, SkillX, EvoSkill, and CoEvoSkills comparison runners. |
| `claim_ablation_full_wins` | `not_testable` | Official checkout lacks ablation runner and named ablated configs. |
| `claim_cross_model_transfer` | `blocked` | Transfer plan exists, but full 120-comparison matrix still depends on ALFWorld OOD support. |
| `claim_tau_bench_gate_activated` | `not_reproduced` | tau-Bench was executed; generated skill failed gate or produced no positive held-out delta. |
| `claim_chemllmbench_useful_gains` | `not_reproduced` | ChemLLMBench property/yield were executed; both failed to show positive skill gains. |
| `claim_refinement_best_of_k` | `blocked` | Full Figure 7 aggregate per-round traces are not bundled. |
| `claim_token_cost` | `partially_reproduced` | Token logging works for ready POC-scale groups, but full paper-scale Table 4 totals are not reproduced. |
| `claim_auditable_skill_artifact` | `partially_reproduced` | Skill JSON artifacts are produced, but evidence is smoke/POC-scale. |

## Remaining Unsolved Issues In Detail

### A. ALFWorld IOD/OOD SkillGen Contract

This is the largest structural blocker. The canonical ALFWorld code can be located/fetched, but the current SkillGen run still lacks a SkillGen-compatible adapter and IOD/OOD split contract.

What is missing:

- A deterministic conversion from ALFWorld tasks to SkillGen `TaskInstance` JSON.
- A paper-matching IOD split.
- A paper-matching OOD split.
- A clear train/test split contract.
- A command plan that runs SkillGen on those converted files.
- Evidence that this adapter is official, paper-indicated, or a justified recorded deviation.

Claims affected:

- `claim_table1_average_gains_all_models`
- `claim_table1_entry_counts`
- `claim_table1_alfworld_scienceworld_patterns`
- `claim_cross_model_transfer`

Recommended next-session approach:

1. Inspect SkillGen README/scripts for any ALFWorld references.
2. Inspect canonical ALFWorld task format.
3. Decide whether a SkillGen adapter can be built as a recorded deviation or whether official support is genuinely missing.
4. If building an adapter, write an explicit contract artifact before running it.

### B. LiveCodeBench Split Contract

The current run has `data/livecodebench/release_v6_all.json`, but it does not yet have a paper-matching SkillGen train/test split contract.

What is missing:

- Which LiveCodeBench version/date/tag matches the paper.
- How paper train/test examples were selected.
- Whether the official SkillGen code expects code-generation tasks in a specific JSON shape.
- A deterministic split artifact and command plan.

Claims affected:

- `claim_table1_average_gains_all_models`
- `claim_table1_entry_counts`

Recommended next-session approach:

1. Read `code/official/scripts/prepare_benchmarks.py` and any LiveCodeBench preparation logic.
2. Inspect `data/livecodebench/release_v6_all.json`.
3. Build `official_instructions.md`/contract notes explaining whether the split can be official, inferred, or must remain blocked.

### C. Baseline Generator Comparison Runners

The paper compares SkillGen against baseline skill generators such as Trace2Skill, SkillX, EvoSkill, and CoEvoSkills. The official SkillGen checkout does not include executable comparison runners for these baselines.

What is missing:

- Runnable baseline implementations inside the official checkout.
- Commands that adapt those baselines to the same benchmark splits.
- Evidence that any public GitHub project is the exact implementation used by the paper.
- A compatibility wrapper that produces comparable outputs under the same evaluation harness.

Current status: `not_testable`, not merely `blocked`. Pulling public repos is not enough unless identity and compatibility are established.

Recommended next-session approach:

1. Search official README/paper references for baseline implementation links.
2. If public repos exist, classify each as exact official implementation, related but not exact, or unusable.
3. Only run them if a comparable runner can be defined and recorded as official or as a human-approved deviation.

### D. Ablation Runner and Named Ablated Configs

The paper's ablation claim cannot currently be reproduced because the official checkout lacks an ablation runner and named configs corresponding to the paper's ablated variants.

What is missing:

- Script or command that runs the ablation matrix.
- Config files for each ablated setting.
- Mapping from paper Figure 3 labels to runnable config changes.
- Expected result files or output parsing contract.

Current status: `not_testable`.

Recommended next-session approach:

1. Inspect official config schema and pipeline options.
2. Determine whether ablations can be reconstructed from code flags.
3. If they must be reconstructed manually, treat that as a deviation and gate it through human review.

### E. Figure 7 Best-of-K / Refinement Traces

The official pipeline records verification/refinement traces for executed runs, but the paper's aggregate Figure 7 result requires full per-round traces across representative benchmark-model entries.

What is missing:

- Full paper-scale per-round logs.
- A mapping between Figure 7 plotted points and raw run artifacts.
- Enough executed runs across benchmark/model entries to aggregate Best-of-K behavior.

Current status: `blocked`.

Recommended next-session approach:

1. Inspect `artifacts/runs/**/verification/round_*` from executed targets.
2. Decide whether the claim can be approximated from newly run full matrix logs.
3. Keep it blocked unless enough full-scale traces exist.

### F. Full Table 1 Matrix

The paper's main result is not the same as the current POC smoke runs. Full Table 1 requires 80 benchmark-split-model entries.

What is missing:

- ALFWorld IOD.
- ALFWorld OOD.
- LiveCodeBench paper-matching split.
- Full execution across all paper rows and models.
- Aggregation to compute average gains and entry counts.

Current status: `blocked`, not because of cost anymore, but because some rows are not structurally execution-ready.

Recommended next-session approach:

1. Solve ALFWorld and LiveCodeBench first.
2. Recompute the benchmark execution plan.
3. Only then schedule full matrix execution.

### G. Cross-Model Transfer Matrix

The transfer runner plan exists, but full cross-model transfer depends on ALFWorld OOD.

What is missing:

- ALFWorld OOD SkillGen-compatible dataset.
- Confirmation of all model routes for transfer sender/receiver combinations.
- Execution of the 120 off-diagonal comparisons.

Current status: `blocked`.

Recommended next-session approach:

1. Do not start transfer execution until ALFWorld OOD is solved.
2. Once solved, use `transfer_runner_plan.json` as the entry artifact.

## Important Deviations Already Recorded

The run is not a pure, unmodified official-code reproduction. The following deviations are recorded and should remain visible:

1. The POC is SkillGen-specific.
2. The initial target is a reduced AIME smoke target.
3. Table 4 token groups were run at reduced POC scale.
4. Some model route names are equivalent route mappings rather than exact paper display names.
5. `openai/*` calls were routed directly to OpenAI via a local official-code patch after OpenRouter credit failure.
6. Some runs used increased concurrency for speed; Mind2Web was retried at lower concurrency after a rate limit.
7. Some external source mappings are hardcoded paper-specific catalog entries.

See `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/hardcoding_disclosures.md` for the current disclosure artifact.

## Recommended Start For The Next Session

The next session should read these files in order:

1. `AGENTS.md`
2. `meeting docs/phase_0_skillgen_handoff_20260603.md`
3. `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/research_validation_report.md`
4. `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/all_claim_verification_matrix.json`
5. `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/benchmark_results.json`
6. `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/hardcoding_disclosures.md`
7. `ai4research_b/phase0/skillgen_automation.py`

Recommended next work item:

```text
Resolve the structural benchmark-contract gaps, starting with LiveCodeBench or ALFWorld.
```

LiveCodeBench may be the smaller first target because a `release_v6_all.json` file already exists in the run. ALFWorld is more important because it blocks both Table 1 and cross-model transfer, but it is likely a larger adapter/split-contract task.

## Validation State

Tests passed after the latest automation/reporting changes:

```text
.venv/bin/python -m unittest tests.test_skillgen_demo tests.test_skillgen_automation

Ran 6 tests
OK
```

## Bottom Line

The current Phase 0 POC has moved past "we cannot run because of API/cost/model routing." It now has real execution evidence for all non-structural ready targets.

The remaining work is structural reproduction work:

- define missing benchmark contracts,
- locate or build official-compatible adapters,
- verify baseline/ablation runner identity,
- collect full-scale traces where the paper claim requires them,
- then rerun the automation so blocked/not-testable claims can move to reproduced, partially reproduced, not reproduced, or failed to run based on actual evidence.
