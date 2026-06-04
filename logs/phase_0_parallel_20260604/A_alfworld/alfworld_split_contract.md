# ALFWorld Split Contract

Group: A - ALFWorld Contract / Adapter.

Status: `ready_for_reconstructed_split_generation`

## Canonical Split Mapping

Use the ALFWorld canonical data paths as follows:

| SkillGen target | ALFWorld source split | Meaning |
| --- | --- | --- |
| `alfworld_iod` | `json_2.1.1/valid_seen` | In-domain / seen validation tasks |
| `alfworld_ood` | `json_2.1.1/valid_unseen` | Out-of-domain / unseen validation tasks |

This mapping is supported by ALFWorld config fields `eval_id_data_path` and `eval_ood_data_path`.

## Paper-Matching Mode

If the paper's exact Table 3 ALFWorld construction/test sizes and sampling rule are recovered, generate files using those values:

```text
code/official/data/alfworld/iod_train_n<PAPER_N>_seed42.json
code/official/data/alfworld/iod_test_n<PAPER_N>_seed42.json
code/official/data/alfworld/ood_train_n<PAPER_N>_seed42.json
code/official/data/alfworld/ood_test_n<PAPER_N>_seed42.json
```

Also write:

```text
code/official/data/alfworld/split_manifest_seed42.json
```

The manifest must include:

- source data root
- ALFWorld commit/version
- data release URLs
- seed
- task ordering rule
- stratification rule
- train instance ids
- test instance ids
- excluded/duplicate ids, if any

## Reconstructed Mode

If exact paper split details remain unavailable, use this deterministic reconstructed split:

1. Enumerate task directories containing `traj_data.json` under the target source split.
2. Load `traj_data.json`.
3. Build a stable row for each task using:
   - relative task directory
   - `task_id`
   - `task_type`
   - object/receptacle parameters
4. Deduplicate by `task_id`; if duplicates exist, keep the lexicographically first relative path and record discarded duplicates.
5. Stratify by `task_type`.
6. Shuffle inside each stratum with `random.Random(42)`.
7. Allocate construction and held-out test rows using the recovered paper sizes if available; otherwise use an explicitly named reduced or full-public reconstructed size.

Reconstructed outputs must include `reconstructed` in metadata and must not be reported as exact paper split reproduction.

## Recommended Smoke Split

Before full execution, generate a smoke split only to validate adapter mechanics:

```text
code/official/data/alfworld/iod_train_smoke_n2_seed42.json
code/official/data/alfworld/iod_test_smoke_n2_seed42.json
code/official/data/alfworld/ood_train_smoke_n2_seed42.json
code/official/data/alfworld/ood_test_smoke_n2_seed42.json
```

Smoke evidence can support `adapter_runs` or `failed_to_run`; it cannot support Table 1 reproduction claims.

## Completion Criteria

ALFWorld can move from `ready_for_reconstructed_execution` to benchmark execution only after:

- canonical data is downloaded into the run directory,
- adapter code exists and has a smoke log,
- split manifest exists,
- generated train/test JSON files exist,
- human approval artifact records the reconstruction/deviation.
