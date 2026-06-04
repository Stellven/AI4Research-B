# ALFWorld Deviation Note

Group: A - ALFWorld Contract / Adapter.

Status: `deviation_disclosed_pending_human_approval`

## Deviation Summary

The canonical ALFWorld source is public and present locally, but the current SkillGen official checkout does not include a native ALFWorld SkillGen adapter or a paper-matching ALFWorld train/test split artifact.

Any next ALFWorld execution is therefore a reconstructed validation path unless the paper authors' exact ALFWorld adapter and split config are found.

## What Is Canonical

- ALFWorld repository: `alfworld/alfworld`
- Local commit: `aaba6870f86c5be6a08a491f32a50b906227bc3e`
- Local package version: `0.5.0`
- License: MIT
- Data source: ALFWorld GitHub release downloads used by `scripts/alfworld-download`
- IOD/OOD source split mapping: `valid_seen` / `valid_unseen` from ALFWorld config
- Text environment: `AlfredTWEnv`

## What Is Reconstructed

- SkillGen `TaskInstance` conversion.
- SkillGen runner branch for interactive ALFWorld action loops.
- Exact action parsing prompt and invalid-action handling.
- Train/test allocation unless the paper's exact ALFWorld split rule is recovered.
- Any reduced smoke split.

## Required Report Label

Use one of these labels in downstream reports:

- `canonical-source reconstruction`: canonical ALFWorld data and source, reconstructed SkillGen adapter/split.
- `deviation-backed reconstructed verification`: adapter or split behavior is inferred and human-approved.
- `failed_to_run`: adapter/data execution fails, with logs preserved.
- `not_reproduced` or `partially_reproduced`: only after execution and claim comparison.

Do not use `reproduced` for ALFWorld Table 1 or transfer claims unless exact paper adapter/split evidence is found or the final report clearly scopes reproduction to a reconstructed contract.

## Approval Gate

Before running ALFWorld commands, record approval for:

- network data download,
- dependency install inside the project/run directory,
- runner code changes,
- reconstructed split rule,
- expected cost and model routes,
- trace retention requirements.
