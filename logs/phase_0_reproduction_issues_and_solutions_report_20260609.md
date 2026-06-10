# Phase 0 Reproduction Issues And Solutions Report

Date: 2026-06-09

Scope: SkillGen Phase 0 reproduction and later solution-validation work in
`phase_0/runs/skillgen_phase0_thorough_20260602`.

This report summarizes the main issues encountered while trying to reproduce
the SkillGen paper results, the solutions or repair paths we used, and the
current maturity of each solution.

## Executive Summary

The paper-level results have not been fully reproduced.

Current reproduction state, based on the research validation report:

- Overall Phase 0 status: `not_reproduced`.
- Full paper claim status: `blocked`.
- Claim verdict counts: `blocked=7`, `not_reproduced=2`,
  `partially_reproduced=3`.
- Only one Table 1-like full-matrix entry was actually executed:
  `mcp_bench_single::openai/gpt-5.4-nano`.
- That executed entry was negative evidence, not partial reproduction:
  construction net gain was `-2`, held-out delta was `0.0`, and the generated
  skill was rejected/deprecated.

The main practical achievement is different:

```text
Before repair: several claims looked impossible or undefined.
After repair: most claims have a visible execution path, deviation policy,
artifact contract, or local solution-validation route.
```

Several paths are now execution-ready or partially validated, but most are not
yet scientific evidence for the original paper's exact claims. Reconstructed
paths can support at most `partially_reproduced` unless author-original configs,
splits, runners, and model routes are later found or equivalence is proven.

## Status Language We Settled On

One early source of confusion was that a single `status` field mixed two
different meanings.

We split it into:

- `claim_verdict_status`: what existing evidence proves about the paper claim.
- `execution_readiness_status`: whether the next validation attempt is ready to
  run, and what type of run it would be.

This matters because a claim can be `blocked` as a verdict while being
`ready_for_reconstructed_execution` operationally. A plan, adapter, contract, or
downloaded repo does not by itself make a claim `partially_reproduced`.

## Issue And Solution Matrix

| Issue | Why it blocked reproduction | Solution used | Current maturity |
| --- | --- | --- | --- |
| Status semantics were conflated | Planning readiness was being confused with validation evidence. | Added separate `claim_verdict_status` and `execution_readiness_status`; kept legacy `status` only as verdict alias. | Solved as reporting policy. Future updates must preserve the split. |
| Full Table 1 requires 80 entries | Table 1 is `10 benchmark rows x 8 paper models`; one smoke run cannot support aggregate claims. | Added full-matrix execution contract, runner state, observed-entry artifacts, and policy that single-entry evidence cannot update aggregate claims. | Partially solved. Runner/plans exist; full 80-entry execution is not complete. |
| Only 1/80 matrix entry was executed | The first real matrix-like entry proved the pipeline could run, but not the paper matrix. | Recorded `mcp_bench_single::openai/gpt-5.4-nano` as observed negative evidence. | Solved for that entry only; aggregate Table 1 remains blocked. |
| ALFWorld was not SkillGen-executable | ALFWorld is interactive; SkillGen needs `TaskInstance` JSON, an action/eval bridge, split rules, and trajectory preservation. | Used canonical ALFWorld data/code plus a reconstructed offline-plan adapter, grader, split manifest, run commands, loader smoke, and deviation note. | Structurally prepared for reconstructed execution; actual paper-scale ALFWorld results still pending. |
| LiveCodeBench split was missing | Available local data was an all-instances release file, not an author-provided construction/test split. | Created deterministic inferred split from release v6, source review, split contract, generated split files, and deviation note. | Ready for reconstructed/open-source execution; exact author split still not proven. |
| Baseline comparison was not executable | Official SkillGen checkout lacked ready runners for Trace2Skill, SkillX, EvoSkill, and CoEvoSkills. | Added public-source identity review, license/human approval, and a single-Markdown-skill adapter contract. | Ready for reconstructed baseline comparison; adapters have not been executed. |
| Ablation configs were absent | Paper Figure 3 arms A1-A5 were described but not bundled as exact executable configs/scripts. | Defined reconstructed A1-A5 contract, config matrix, smoke plan, and deviation note. | Ready for human-reviewed reconstructed smoke; no ablation result yet. |
| Cross-model transfer depended on ALFWorld OOD | Figure 4 needs 120 off-diagonal comparisons, including ALFWorld OOD. | Wrote transfer execution contract and tied ALFWorld OOD to the ALFWorld reconstructed path. | Still blocked until ALFWorld OOD execution and source-skill/evaluator runs exist. |
| Figure 7 needed complete per-round traces | Final eval summaries are insufficient for best-of-K/refinement analysis. | Added per-round trace retention checklist and evidence requirements for verification JSONL, summaries, candidate skills, token logs, and held-out trajectories. | Contract exists; full trace-producing runs still required. |
| OpenRouter failed with 402 | Official path defaulted to OpenRouter; first run hit insufficient credits. | Used official direct OpenAI fallback for `openai/...` models and wrote provider resolution artifacts. | Solved for OpenAI routes only. Non-OpenAI paper routes remain provider-unavailable unless OpenRouter/direct providers are repaired. |
| Non-OpenAI model routes were unavailable | Six of eight paper models relied on OpenRouter or missing direct-provider integrations. | Added provider policy: mark entries `provider_unavailable`, do not treat provider failure as benchmark failure, and do not substitute models for paper reproduction. | Partially solved as accounting. Execution still blocked for those routes. |
| API cost/time was high | One low-cost entry used 557,877 tokens; blind 80-entry execution could be expensive and slow. | Added cost governance, stop conditions, budget policy, per-entry cost reporting, and small first-entry validation. | Solved as governance; full execution still requires budgeted run decisions. |
| `main.py --resume` could not reuse partial failed runs | Failed runs had trajectory JSONL but no `checkpoint.json`, so official resume failed. | Preserved failed/resume logs and reran fresh. Documented possible checkpoint-converter wrapper as future deviation. | Not solved in official behavior. Evidence preserved. |
| Negative results could be mislabeled | There was pressure to move blocked claims toward partial even when evidence was negative. | Recorded negative outcomes explicitly: `not_reproduced` for tau-Bench/ChemLLMBench smoke and the matrix single entry. | Solved as evidence policy. Negative evidence is valid evidence. |
| Artifact mirrors could drift | Some artifacts exist both at top level and in categorized folders. | Synced report/matrix copies and noted mirror-aware update requirement. | Partially solved. Future agents must keep mirrors synchronized. |
| External APIs were not desired for solution validation | Claim reproduction via external APIs was costly and route-dependent. | Added local Ollama OpenAI-compatible routing and deterministic hash embeddings as a recorded solution-validation deviation. | Infrastructure partially validated; not paper reproduction. |
| Local Ollama access hit sandbox/permission limits | Localhost HTTP was sometimes denied by sandbox without escalation. | Recorded permission behavior, blocked notes, and requirement for bounded pre-approval for local Ollama runs. | Operationally understood; future confirmation runs need pre-approved local access. |
| Local model behavior created new validation problems | `gemma3:12b` solved all train cases, producing no failures or skill; `gemma3:4b` produced a skill but no held-out gain. | Switched model/subset, then patched verification sampling to include baseline failures. | Infrastructure validated; skill effectiveness not validated. |
| Verification sampling missed failures | `gemma3:4b` had 5 train failures, but construction verification sampled 0 failures and 4 success guards. | Patched sampler to reserve failure-target slots and added unit test coverage. | Validated by tests and the `gemma3_4b_stratified` run. |
| Held-out sample was saturated | In `gemma3_4b_stratified`, baseline was 16/16 on held-out, so out-of-sample repair opportunity was absent; skill regressed one case. | Labeled run `partially_solution_validated`, not `solution_validated`; recommended harder held-out slice or second seed. | Skill effectiveness remains not validated. |
| Candidate skill traceability had a gap | Verification summary candidate id differed from persisted active skill id. | Documented the mismatch and recommended adding `source_candidate_id` or finalization trace. | Not fully solved. Trace evidence exists, but mapping should be made explicit. |

## Details By Reproduction Area

### 1. Full Table 1 Matrix

Problem:

The paper's Table 1 claims need 80 benchmark-model entries:

```text
10 benchmark/split rows x 8 paper models = 80 entries
```

The initial automation and smoke runs did not execute that matrix. The first
matrix-like attempt completed only one low-cost reconstructed entry:

```text
mcp_bench_single::openai/gpt-5.4-nano
```

Result:

- Construction baseline accuracy: `0.75`
- Construction skill accuracy: `0.25`
- Construction net gain: `-2`
- Held-out baseline accuracy: `0.8125`
- Held-out skill accuracy: `0.8125`
- Held-out delta: `0.0`
- Verdict for this entry: `not_reproduced`

Solution used:

- Created full-matrix execution contract and runner state artifacts.
- Recorded observed entries separately from aggregate claim status.
- Explicitly prevented a single entry from upgrading aggregate Table 1 claims.

Current conclusion:

The full Table 1 claims remain `blocked`. The executed single entry is useful
negative evidence and pipeline evidence, but not aggregate reproduction.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/observed_entries.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/full_matrix/full_matrix_runner_state.md`

### 2. Benchmark Input And Adapter Gaps

#### ALFWorld

Problem:

ALFWorld is open-source, but it was not directly usable by the SkillGen
pipeline. The missing part was not just data; it was the bridge from an
interactive environment into SkillGen's task/evaluation format.

Missing pieces included:

- canonical data source confirmation;
- IOD/OOD mapping;
- conversion into SkillGen `TaskInstance` JSON;
- action/evaluation protocol;
- success/failure grading;
- construction/test split;
- trace preservation;
- deviation disclosure.

Solution used:

- Used canonical ALFWorld code/data as the source.
- Built a reconstructed offline-plan adapter and lightweight grader.
- Generated IOD/OOD train/test JSON.
- Wrote split manifest, run commands, loader smoke, and deviation note.
- Marked the path as reconstructed, not exact author-original reproduction.

Current conclusion:

ALFWorld is structurally prepared for reconstructed execution. Positive results
from this path can support partial evidence only unless the author-original
SkillGen ALFWorld runner/split is found or equivalence is proven.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/alfworld_adapter_deviation_note.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/alfworld_split_manifest_seed42.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/alfworld_run_commands.md`

#### LiveCodeBench

Problem:

The local material had a LiveCodeBench release file, but not an exact
author-bundled construction/test split.

Solution used:

- Reviewed open-source LiveCodeBench source.
- Defined deterministic inferred split from release v6.
- Wrote split contract, source review, generated split files, and deviation
  note.

Current conclusion:

LiveCodeBench is ready for reconstructed/open-source execution, but exact
paper-equivalent split identity is not proven.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/livecodebench_source_review.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/livecodebench_split_contract.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/livecodebench_deviation_note.md`

### 3. Baseline Generator Comparison

Problem:

The paper compares SkillGen against Trace2Skill, SkillX, EvoSkill, and
CoEvoSkills, but the official SkillGen checkout did not contain a ready,
author-original baseline comparison runner for these systems.

Solution used:

- Identified public baseline source candidates.
- Added source identity review and license/human approval artifacts.
- Defined a single-Markdown-skill adapter contract so baselines can be compared
  through one shared evaluation harness.
- Marked the path as public-code reconstructed comparison.

Current conclusion:

This issue moved from `not_testable` to a reconstructed comparison path, but it
has not produced validation results. It should remain `blocked` as a claim
verdict until adapters are executed and results are parsed.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/baseline_source_identity_review.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/baseline_single_skill_adapter_contract.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/baseline_deviation_note.md`

### 4. Ablation Claim

Problem:

The paper's Figure 3 ablation claim depends on A1-A5 variants, but exact
author-provided ablation configs/scripts were not bundled.

Solution used:

- Defined reconstructed arms:
  - Full;
  - A1 ICL `k=3`;
  - A2 no refinement;
  - A3 no verification gate;
  - A4 no Failure Lessons;
  - A5 plain-text skill.
- Wrote reconstructed ablation contract, config matrix, smoke plan, and
  deviation note.

Current conclusion:

The ablation path is defined but not executed. It is not exact Figure 3
reproduction unless author-original A1-A5 configs are found. A3 and A4 are
safety/semantic-sensitive deviations and need careful labeling.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/reconstructed_ablation_contract.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/ablation_config_matrix.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/ablation_deviation_note.md`

### 5. Cross-Model Transfer

Problem:

The transfer claim needs off-diagonal source/evaluator comparisons:

```text
source model generates skill
different evaluator model uses that skill
same evaluator no-skill baseline is measured
same held-out instances are compared
```

The planned matrix includes 120 off-diagonal comparisons. ALFWorld OOD is a
dependency, so missing ALFWorld execution blocks the transfer claim.

Solution used:

- Wrote transfer execution contract.
- Defined dependency on ALFWorld OOD reconstructed execution.
- Required retained source-skill artifacts and evaluator baselines.

Current conclusion:

The transfer claim remains blocked until ALFWorld OOD, model routes, generated
source skills, evaluator baselines, and all off-diagonal outputs exist.

Primary records:

- `logs/phase_0_parallel_20260604/C_execution_trace/transfer_execution_contract.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/00_run_summary/research_validation_report.md`

### 6. Per-Round Trace And Figure 7 Evidence

Problem:

Figure 7/refinement claims cannot be verified from final accuracy alone. They
need per-round traces:

- candidate skill per round;
- verification baseline outcome;
- with-skill outcome;
- repairs;
- regressions;
- net gain;
- gate result;
- best-so-far aggregation.

Solution used:

- Added trace retention checklist and evidence checks.
- Required preservation of verification JSONL, summaries, candidate skill
  artifacts, token logs, held-out trajectories, and run metadata.

Current conclusion:

Trace preservation is now a requirement and was partially validated in local
solution-validation runs. Full Figure 7 reproduction still needs representative
full/reconstructed runs with those traces present.

Primary records:

- `logs/phase_0_parallel_20260604/C_execution_trace/per_round_trace_retention_checklist.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/overnight_verification_20260607/skill_traceability_audit.md`

### 7. Provider Routing And API Access

Problem:

The official code defaulted to OpenRouter. OpenRouter returned HTTP 402
insufficient credits during reproduction attempts. This blocked non-OpenAI
paper model routes and initially blocked even OpenAI routes when routed through
OpenRouter.

Solution used:

- Used the official direct OpenAI fallback for `openai/...` routes:

```text
SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1
```

- Added provider resolution artifacts.
- Marked non-OpenAI routes as `provider_unavailable` rather than benchmark
  failures.
- For later solution validation, added local Ollama routing:

```text
SKILLGEN_LOCAL_OPENAI_COMPAT=1
SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1
SKILLGEN_LOCAL_API_KEY=ollama
SKILLGEN_LOCAL_MODEL=<ollama model>
SKILLGEN_LOCAL_EMBEDDING_MODE=hash
SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0
```

Current conclusion:

Direct OpenAI fallback solves only OpenAI paper routes. Non-OpenAI paper routes
still require repaired OpenRouter billing/key or reviewed direct-provider
integrations. Ollama is useful for local solution validation, not paper-model
reproduction.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/provider_resolution_status.md`
- `logs/ollama_solution_validation_execution_manual_20260604.md`

### 8. Cost, Runtime, And Governance

Problem:

Even the low-cost reconstructed entry was expensive:

```text
training tokens: 446,895
eval tokens:     110,982
combined:        557,877
```

Blindly executing all 80 Table 1 entries would have high and uneven cost/time
risk.

Solution used:

- Ran one low-risk entry first.
- Added full-matrix cost governance, budget gates, stop conditions, per-entry
  cost report template, and policy that partial runs remain incomplete.

Current conclusion:

The cost-control policy is in place. It does not reduce the scientific need for
full execution if exact reproduction is required.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/full_matrix_cost_governance.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/full_matrix_execution_budget_policy.json`

### 9. Resume And Failure Recovery

Problem:

The first failed run left trajectories but no `checkpoint.json`. Official
`main.py --resume` could not resume from that partial state.

Solution used:

- Preserved failed run logs and resume-failure logs.
- Reran the entry fresh through direct OpenAI fallback.
- Documented a possible future checkpoint converter as a deviation-backed
  improvement, not official behavior.

Current conclusion:

Resume is not fixed in official behavior. The reproduction process now treats
failed runs as evidence rather than hiding them.

Primary record:

- `logs/phase_0_overnight_20260604/遇到的问题.md`

### 10. Local Solution Validation With Ollama

Problem:

We later changed the goal from exact paper claim verification to validating
whether our repair solutions make previously blocked/not-testable paths
executable without external APIs.

Solution used:

- Patched local official-code copy for Ollama OpenAI-compatible chat routing.
- Added deterministic local hash embeddings.
- Disabled OpenAI/OpenRouter keys in completed local runs.
- Preserved probes, train/eval logs, configs, skill outputs, eval outputs, and
  trajectories.

Key local outcomes:

- `gemma3:12b`: `inconclusive`; baseline solved 40/40 training cases, so no
  failures remained and no skill was generated.
- `gemma3:4b`: `not_solution_validated`; train/eval completed, but skill did not
  improve and verification sampled no failures.
- `gemma3:4b_stratified`: `partially_solution_validated`; local route, hash
  embeddings, sampler fix, train/eval, and traces worked, but held-out eval
  regressed one case.

Current conclusion:

Local infrastructure is partially validated. Generated skill effectiveness is
not validated.

Primary records:

- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_12b/solution_validation_result.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b/solution_validation_result.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/gemma3_4b_stratified/solution_validation_result.md`
- `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/overnight_verification_20260607/final_verification_summary.md`

## Metric Calculation Rules Used

The core per-entry calculations are:

```text
baseline_acc = baseline_correct / n
skill_acc    = skill_correct / n
delta_acc    = skill_acc - baseline_acc
```

For entry-count claims:

```text
delta_acc > 0 -> improved
delta_acc = 0 -> unchanged
delta_acc < 0 -> regressed
```

For paired repair/regression:

```text
repair     = baseline failed, skill succeeded
regression = baseline succeeded, skill failed
net_gain   = repair - regression
```

These calculations only become paper-claim evidence when they are computed on
the correct benchmark/model/split scope. The same formulas on smoke or
reconstructed reduced runs are useful, but they do not automatically reproduce
paper-scale percentages.

## Current Remaining Gaps

The biggest remaining gaps are:

1. Full 80-entry Table 1 execution has not completed.
2. Non-OpenAI paper model routes are still unavailable through current provider
   setup.
3. ALFWorld reconstructed execution still needs actual benchmark results.
4. LiveCodeBench reconstructed split needs execution and aggregation.
5. Baseline comparison adapters have not been executed.
6. Reconstructed ablation smoke and paper-target ablation matrix have not been
   executed.
7. Cross-model transfer remains blocked by ALFWorld OOD and model-route
   dependencies.
8. Figure 7 still needs full per-round traces at representative scale.
9. Local solution validation shows infrastructure works, but does not yet show
   positive held-out skill effectiveness.
10. Candidate-to-persisted-skill traceability should be made explicit in future
    runs.

## Bottom Line

The reproduction effort did not fully reproduce the paper results. It did,
however, convert many unclear or impossible-looking claims into structured
execution paths:

- exact official-code smoke evidence where available;
- reconstructed/deviation-backed execution paths where official materials were
  incomplete;
- provider accounting for unavailable model routes;
- cost governance for large matrix runs;
- trace retention requirements;
- local no-external-API solution validation.

The correct next scientific step depends on the desired standard:

- For exact paper reproduction: repair provider routes, execute the full matrix,
  and avoid treating reconstructed paths as exact.
- For Phase 0 solution validation: continue local/reconstructed runs, preserve
  evidence, and label outcomes as solution validation rather than paper
  reproduction.
