# ALFWorld Source Review

Group: A - ALFWorld Contract / Adapter.

Status: `source_identity_reviewed_canonical_public_source`

## Reviewed Local Evidence

- SkillGen run: `phase_0/runs/skillgen_phase0_thorough_20260602`
- Local ALFWorld source: `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/external/alfworld`
- Upstream repository recorded by local source: `https://github.com/alfworld/alfworld.git`
- Local commit: `aaba6870f86c5be6a08a491f32a50b906227bc3e`
- Package version from `alfworld/info.py`: `0.5.0`
- License file: MIT license
- Data README states: 3,553 training games, 140 seen validation games, 134 unseen validation games.

## Data Source Identity

The canonical download command is provided by the local ALFWorld source:

```text
python scripts/alfworld-download --data-dir <run_dir>/code/official/data/alfworld
```

The script downloads official release artifacts from GitHub releases:

- `json_2.1.1_json.zip`
- `json_2.1.1_pddl.zip`
- `json_2.1.3_tw-pddl.zip`
- `mrcnn_alfred_objects_sep13_004.pth`

The data must be downloaded inside the run directory. Do not use the ALFWorld default `~/.cache/alfworld` location for Phase 0 evidence.

## IOD / OOD Mapping Evidence

The local ALFWorld config contains:

```text
dataset.data_path: $ALFWORLD_DATA/json_2.1.1/train
dataset.eval_id_data_path: $ALFWORLD_DATA/json_2.1.1/valid_seen
dataset.eval_ood_data_path: $ALFWORLD_DATA/json_2.1.1/valid_unseen
env.type: AlfredTWEnv
general.random_seed: 42
```

For SkillGen Phase 0, use:

- IOD pool: `$ALFWORLD_DATA/json_2.1.1/valid_seen`
- OOD pool: `$ALFWORLD_DATA/json_2.1.1/valid_unseen`
- Text environment: `AlfredTWEnv`

This is canonical ALFWorld source evidence. It is not evidence that SkillGen official code already contains a native ALFWorld adapter.

## Current Integration Finding

The SkillGen official checkout does not expose an ALFWorld-specific SkillGen adapter. The existing SkillGen `TaskInstance` runner handles generic static tasks and has a special branch for `tau_bench`, but no equivalent branch for `metadata.benchmark == "alfworld"`.

Therefore the next execution must be recorded as one of:

- `canonical-source reconstruction`: using canonical ALFWorld source/data plus a new SkillGen-compatible adapter.
- `deviation-backed reconstruction`: if any split, prompt, action parsing, or environment-loop behavior cannot be tied to official SkillGen paper artifacts.

It must not be described as exact original-paper reproduction unless a matching SkillGen ALFWorld adapter/split config from the paper authors is found.
