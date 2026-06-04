# ALFWorld Reconstructed Adapter Handoff Checklist For Group C

Date: 2026-06-04

Status: `complete_for_reconstructed_execution_handoff`

Owner of completed package: Group A / ALFWorld adapter.

Receiving group: Group C / Full Matrix, Transfer, Trace Orchestration.

## Confirmation

The ALFWorld reconstructed adapter package is complete enough for Group C to
schedule `alfworld_iod` and `alfworld_ood` in the SkillGen full matrix after
human execution approval.

This package is not exact author-original ALFWorld reproduction. It is:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

Do not remove this deviation label from downstream reports.

## Data Paths

Workdir for SkillGen execution:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official
```

Canonical ALFWorld data:

```text
data/alfworld
```

Generated SkillGen-compatible datasets:

| Row | Train path | Train n | Test path | Test n | Source split definition |
| --- | --- | ---: | --- | ---: | --- |
| `alfworld_iod` | `data/alfworld_iod/train.json` | 500 | `data/alfworld_iod/test.json` | 150 | train -> construction; `valid_seen` -> held-out IOD |
| `alfworld_ood` | `data/alfworld_ood/train.json` | 500 | `data/alfworld_ood/test.json` | 255 | train -> construction; `valid_unseen` -> held-out OOD |

Absolute paths:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld_iod/train.json
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld_iod/test.json
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld_ood/train.json
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld_ood/test.json
```

## Config Template

Use these templates and replace `<model_route>`, `<judge_model_route>`, and
`<model_slug>` before execution:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/alfworld_iod/template.yaml
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/alfworld_ood/template.yaml
```

Concrete per-model config paths should be:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/alfworld_iod/{model_slug}.yaml
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/alfworld_ood/{model_slug}.yaml
```

The template writes all candidates, skill output, run artifacts, verification
rounds, and raw traces under:

```text
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/
```

## Run Commands

Run from:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official
```

IOD train:

```text
.venv/bin/python main.py data/alfworld_iod/train.json \
  --config ../../artifacts/07_configs_and_inputs/generated_configs/alfworld_iod/{model_slug}.yaml
```

IOD eval:

```text
.venv/bin/python eval_skill.py \
  --skill-repo ../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_iod/{model_slug}/skill_output \
  --dataset data/alfworld_iod/test.json \
  --n 150 \
  --seed 42 \
  --models {model_route} \
  --judge-model {judge_model_route} \
  --max-workers {max_workers} \
  --output ../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_iod/{model_slug}/eval_results.json
```

OOD train:

```text
.venv/bin/python main.py data/alfworld_ood/train.json \
  --config ../../artifacts/07_configs_and_inputs/generated_configs/alfworld_ood/{model_slug}.yaml
```

OOD eval:

```text
.venv/bin/python eval_skill.py \
  --skill-repo ../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_ood/{model_slug}/skill_output \
  --dataset data/alfworld_ood/test.json \
  --n 255 \
  --seed 42 \
  --models {model_route} \
  --judge-model {judge_model_route} \
  --max-workers {max_workers} \
  --output ../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_ood/{model_slug}/eval_results.json
```

Do not pass `--no-save-trajectories`.

## Deviation Label

Required label for every downstream ALFWorld result:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

Use this status in execution tracking before actual LLM/full-matrix execution:

```text
ready_for_reconstructed_execution
```

Do not report `reproduced` for ALFWorld from this package alone. After execution,
valid statuses are `partially_reproduced`, `not_reproduced`, or `failed_to_run`,
unless exact author-original SkillGen ALFWorld adapter/split evidence is found.

## Trace Retention Requirements

Group C must retain these files for every `{row}/{model_slug}` run:

```text
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/train_stdout.txt
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/train_stderr.txt
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_stdout.txt
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_stderr.txt
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results.json
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results.token_usage.json
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results_trajectories/
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/skill_output/
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/baseline_trajectories.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/checkpoint_trajectories.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_baseline.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_with_skill.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_summary.json
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_case_analyses.json
```

If a command fails, preserve stdout/stderr and partial artifact directories.

## Smoke Evidence

Smoke evidence directory:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/raw_benchmark_outputs/alfworld_adapter_smoke
```

Files:

```text
main_eval_loader_smoke_stdout.txt
main_eval_loader_smoke_stderr.txt
py_compile_stdout.txt
py_compile_stderr.txt
smoke_summary.json
```

Smoke status:

```text
passed
```

What smoke proves:

- `main.py` can load all four ALFWorld JSON files.
- `eval_skill.py` can load all four ALFWorld JSON files.
- ALFWorld adapter/grader/prepare scripts compile.

What smoke does not prove:

- No full `main.py` training run was executed.
- No `eval_skill.py` LLM evaluation was executed.
- No live ALFWorld TextWorld rollout was executed.

## Provenance And Support Artifacts

Machine-readable split/provenance manifest:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld_split_manifest_seed42.json
```

Human-readable split summary:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/alfworld_split_manifest_seed42.md
```

Run commands:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/06_plans_and_contracts/alfworld_run_commands.md
```

Deviation note:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/09_safety_and_deviations/alfworld_adapter_deviation_note.md
```

Adapter code:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/alfworld_adapter.py
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/alfworld_grader.py
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/scripts/prepare_alfworld.py
```

## C Group Checklist

- [ ] Confirm human approval for reconstructed ALFWorld execution.
- [ ] Generate one concrete config per `{row}/{model_slug}` from the template.
- [ ] Record `{model_route}` and `{judge_model_route}` from the approved model mapping.
- [ ] Run IOD/OOD train commands from `code/official`.
- [ ] Run IOD/OOD eval commands from `code/official`.
- [ ] Preserve all stdout/stderr files.
- [ ] Preserve `eval_results.json` and `eval_results.token_usage.json`.
- [ ] Preserve `eval_results_trajectories/`.
- [ ] Preserve every `verification/round_*` directory.
- [ ] Carry the required deviation label into observed-entry aggregation.

