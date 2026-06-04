# ALFWorld Adapter Contract

Group: A - ALFWorld Contract / Adapter.

Status: `ready_for_reconstructed_adapter_implementation`

## Objective

Bridge canonical ALFWorld TextWorld tasks into SkillGen without pretending that the official SkillGen checkout already supports ALFWorld natively.

The adapter must produce auditable SkillGen artifacts and preserve full interactive trajectories.

## Data Inputs

Required canonical ALFWorld files under the run directory:

```text
code/official/data/alfworld/json_2.1.1/train
code/official/data/alfworld/json_2.1.1/valid_seen
code/official/data/alfworld/json_2.1.1/valid_unseen
code/official/data/alfworld/logic/alfred.pddl
code/official/data/alfworld/logic/alfred.twl2
```

Source command must be human-approved before network use:

```text
workdir: code/official/benchmarks/external/alfworld
env:
  ALFWORLD_DATA: <absolute run_dir>/code/official/data/alfworld
argv:
  - <run_dir>/code/official/.venv/bin/python
  - scripts/alfworld-download
  - --data-dir
  - <absolute run_dir>/code/official/data/alfworld
```

## TaskInstance Shape

Each ALFWorld game becomes one SkillGen `TaskInstance` with:

```json
{
  "instance_id": "alfworld::<split>::<task_type>::<task_id>",
  "input": "<goal instruction plus initial observation and interaction rules>",
  "ground_truth": {"success": true},
  "metadata": {
    "benchmark": "alfworld",
    "environment": "AlfredTWEnv",
    "source_split": "valid_seen | valid_unseen | train",
    "paper_split": "iod | ood | construction",
    "task_type": "<ALFWorld task_type>",
    "task_id": "<traj_data task_id>",
    "game_dir": "<path relative to ALFWORLD_DATA>",
    "game_file": "<path relative to ALFWORLD_DATA>/game.tw-pddl",
    "traj_data": "<path relative to ALFWORLD_DATA>/traj_data.json",
    "max_steps": 50
  }
}
```

The adapter may include the initial observation in `input`, but the runner must not rely on a single static prompt. ALFWorld is interactive.

## Runner Contract

Add a SkillGen runner branch equivalent in shape to the existing `tau_bench` branch:

```text
if instance.metadata["benchmark"] == "alfworld":
    run_alfworld_agent(instance, skill_bundle, config)
```

The runner must:

1. Load ALFWorld config with `AlfredTWEnv`.
2. Force `ALFWORLD_DATA` to the run-local data directory.
3. Reset exactly one game instance at a time.
4. Send the goal, current observation, and admissible commands to the LLM.
5. Parse one action per step.
6. Step the environment with that action.
7. Repeat until `done`, max steps, or runner error.
8. Set `Trajectory.success` from the ALFWorld environment result.
9. Preserve every message/action/observation/reward/done value in `Trajectory.metadata`.

## Scoring Contract

Primary score:

```text
success = bool(done and final_score > 0)
score = float(final_score)
```

The adapter must store raw ALFWorld `scores`, `dones`, and final `infos` so this mapping can be audited later. If ALFWorld exposes an explicit task success field in `infos`, keep that field and prefer it only after documenting the exact key.

SkillGen accuracy for ALFWorld is:

```text
successful_trajectories / evaluated_trajectories
```

## Trajectory Retention

Every run must preserve:

```text
artifacts/raw_benchmark_outputs/full_matrix/alfworld_<iod|ood>/<model_slug>/baseline_trajectories.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_<iod|ood>/<model_slug>/with_skill_trajectories.jsonl
artifacts/raw_benchmark_outputs/full_matrix/alfworld_<iod|ood>/<model_slug>/eval_results.json
artifacts/raw_benchmark_outputs/full_matrix/alfworld_<iod|ood>/<model_slug>/eval_results.token_usage.json
```

For Figure 7 or transfer work, also preserve:

```text
verification/round_*/verification_baseline.jsonl
verification/round_*/verification_with_skill.jsonl
verification/round_*/verification_summary.json
verification/round_*/verification_case_analyses.json
```

## Human Gate

Before execution, a human must approve:

- ALFWorld data download command.
- Python dependency install scope.
- Any modification to SkillGen runner code.
- Any non-paper split decision.
- Any reduced-scale smoke run used before full execution.
