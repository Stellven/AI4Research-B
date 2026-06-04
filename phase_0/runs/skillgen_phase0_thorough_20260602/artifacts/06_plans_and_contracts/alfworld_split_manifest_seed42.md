# ALFWorld Split And Provenance Manifest Summary

Date: 2026-06-04

Machine-readable manifest:

```text
code/official/data/alfworld_split_manifest_seed42.json
```

## Produced Datasets

| Row | Split | Path | Instances | Source split |
| --- | --- | --- | ---: | --- |
| `alfworld_iod` | train | `code/official/data/alfworld_iod/train.json` | 500 | `train` |
| `alfworld_iod` | test | `code/official/data/alfworld_iod/test.json` | 150 | `valid_seen` |
| `alfworld_ood` | train | `code/official/data/alfworld_ood/train.json` | 500 | `train` |
| `alfworld_ood` | test | `code/official/data/alfworld_ood/test.json` | 255 | `valid_unseen` |

## Source

- Source repository: `alfworld/alfworld`
- Local commit: `aaba6870f86c5be6a08a491f32a50b906227bc3e`
- Local package version: `0.5.0`
- Canonical data path: `code/official/data/alfworld`
- Canonical text environment named by config: `AlfredTWEnv`

## Sampling Rule

- Stable enumerate `traj_data.json`.
- Deduplicate by `task_id`.
- Stratify by ALFWorld `task_type`.
- Round-robin sample across task types.
- Shuffle final selected order with seed 42.
- Use the same construction sample for IOD and OOD; the row difference is the
  held-out split, matching the paper's Table 3 construction/test protocol.

## Paper Definition

| Row | Construction source | Construction n | Held-out source | Held-out n |
| --- | --- | ---: | --- | ---: |
| `alfworld_iod` | `train` | 500 | `valid_seen` | 150 |
| `alfworld_ood` | `train` | 500 | `valid_unseen` | 255 |

## Observed Source Counts

| Canonical split | Tasks |
| --- | ---: |
| `train` | 6374 |
| `valid_seen` | 251 |
| `valid_unseen` | 255 |

## Deviation

The generated JSON files are SkillGen-compatible reconstructed offline-plan
datasets. They do not imply that the current SkillGen checkout contains a live
ALFWorld TextWorld runner.

