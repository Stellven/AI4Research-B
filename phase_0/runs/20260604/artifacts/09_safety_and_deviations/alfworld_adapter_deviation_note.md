# ALFWorld Adapter Deviation Note

Date: 2026-06-04

Status: `reconstructed_offline_plan_adapter_ready_for_json_loading_smoke`

## Scope

This note applies to:

- `code/official/data/alfworld_iod/train.json`
- `code/official/data/alfworld_iod/test.json`
- `code/official/data/alfworld_ood/train.json`
- `code/official/data/alfworld_ood/test.json`
- `code/official/benchmarks/alfworld_adapter.py`
- `code/official/benchmarks/alfworld_grader.py`
- `code/official/scripts/prepare_alfworld.py`

## What Is Canonical

Canonical ALFWorld source and data are used:

- Repository: `alfworld/alfworld`
- URL: `https://github.com/alfworld/alfworld.git`
- Local commit: `aaba6870f86c5be6a08a491f32a50b906227bc3e`
- Package version: `0.5.0`
- Environment named by canonical config: `AlfredTWEnv`
- Data release URLs:
  - `https://github.com/alfworld/alfworld/releases/download/0.2.2/json_2.1.1_json.zip`
  - `https://github.com/alfworld/alfworld/releases/download/0.2.2/json_2.1.1_pddl.zip`
  - `https://github.com/alfworld/alfworld/releases/download/0.4.2/json_2.1.3_tw-pddl.zip`
  - `https://github.com/alfworld/alfworld/releases/download/0.2.2/mrcnn_alfred_objects_sep13_004.pth`

Canonical local data path:

```text
code/official/data/alfworld
```

## Paper Split Definition Confirmed

The SkillGen paper's Appendix C.2 / Table 3 defines:

| Row | Construction source | Construction n | Held-out source | Held-out n | Paper meaning |
| --- | --- | ---: | --- | ---: | --- |
| `alfworld_iod` | ALFWorld `train` | 500 | `valid_seen` | 150 | In-distribution |
| `alfworld_ood` | ALFWorld `train` | 500 | `valid_unseen` | 255 | Out-of-distribution |

Actual downloaded source counts:

| Canonical split | Observed tasks |
| --- | ---: |
| `train` | 6374 |
| `valid_seen` | 251 |
| `valid_unseen` | 255 |

The generated files use seed 42 and stratified sampling by `task_type`.

## What Is Reconstructed

The official SkillGen checkout does not contain an author-original ALFWorld
runner or author-original ALFWorld SkillGen split files. The delivered adapter is
therefore reconstructed.

Reconstructed parts:

- Conversion from ALFWorld `traj_data.json` into SkillGen `TaskInstance` JSON.
- Offline high-level planning prompt in place of live TextWorld interaction.
- Lightweight reconstructed plan grader in `benchmarks/alfworld_grader.py`.
- Seed-42 stratified train/test JSON generation.

This does not execute ALFWorld's live `AlfredTWEnv` environment during
`main.py` or `eval_skill.py`; it prepares a SkillGen-compatible offline-plan
variant so the current SkillGen pipeline can load and run the ALFWorld rows.

## Required Label

Any future result from these files must be labeled:

```text
canonical ALFWorld data + reconstructed SkillGen offline-plan adapter
```

Do not label future results as exact ALFWorld reproduction unless author-original
SkillGen ALFWorld adapter/split code is found and substituted.

## Trace Retention Requirement

Future ALFWorld full-matrix runs must preserve all per-round traces:

```text
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results.json
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results.token_usage.json
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/eval_results_trajectories/
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/skill_output/
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/baseline_trajectories.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/checkpoint_trajectories.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/
```

Deleting or summarizing away these traces invalidates the Phase 0 evidence chain.

