# ALFWorld Reconstructed Run Commands

Date: 2026-06-04

Workdir for all SkillGen commands:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official
```

## Execution Authorization

Full-matrix preparation and planned execution are authorized by:

```text
artifacts/05_reviews_and_approval/full_matrix_execution_authorization.md
```

No further pre-execution human gate is required for ALFWorld IOD/OOD planned
entries. Runner execution is authorized, including API spending, per-entry
config generation, stdout/stderr capture, token logging, and trajectory
retention.

Every ALFWorld result produced through this path must be labeled exactly:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

This is authorized reconstructed execution; results must be labeled and
validated after the run. The label does not convert reconstructed offline-plan
evidence into author-original live ALFWorld evidence.

## Canonical Data Download

This command was used to download canonical ALFWorld data into the run
directory:

```text
ALFWORLD_DATA="/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld" \
PYTHONPATH="/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/external/alfworld" \
"/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/.venv/bin/python" \
scripts/alfworld-download \
--data-dir "/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B/phase_0/runs/skillgen_phase0_thorough_20260602/code/official/data/alfworld"
```

## Dataset Generation

```text
.venv/bin/python scripts/prepare_alfworld.py \
  --alfworld-data-dir data/alfworld \
  --out-root data \
  --seed 42 \
  --train-n 500 \
  --iod-test-n 150 \
  --ood-test-n 255 \
  --manifest data/alfworld_split_manifest_seed42.json
```

## Full-Matrix Train Commands

The concrete model config path must be generated per model before execution.

```text
.venv/bin/python main.py data/alfworld_iod/train.json \
  --config ../../artifacts/07_configs_and_inputs/generated_configs/alfworld_iod/{model_slug}.yaml
```

```text
.venv/bin/python main.py data/alfworld_ood/train.json \
  --config ../../artifacts/07_configs_and_inputs/generated_configs/alfworld_ood/{model_slug}.yaml
```

## Full-Matrix Eval Commands

IOD:

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

OOD:

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

## Required Retained Outputs

For every future ALFWorld full-matrix run, keep:

```text
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/train_stdout.txt
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/train_stderr.txt
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_stdout.txt
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_stderr.txt
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results.json
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results.token_usage.json
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results_trajectories/
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/skill_output/
../../artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/
```

The `eval_skill.py` default keeps `--save-trajectories` enabled. Do not pass
`--no-save-trajectories` for Phase 0 ALFWorld evidence.
