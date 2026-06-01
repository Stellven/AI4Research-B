# Claim Comparison

Status: `blocked_for_table1_reproduction_smoke_not_reproduced`

## Paper Claim

SkillGen reports average held-out gains of `+3.27` to `+10.08` percentage points across eight evaluated base LLMs in Table 1, with 50 improved, 25 unchanged, and 5 regressed benchmark-split-model entries.

## Observed Result

No Table 1 reproduction was run. The completed run is an AIME smoke validation using official code, a reduced train subset, a reduced test subset, and a reduced config.

## Smoke Result

- Baseline accuracy: `50.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `-25.0` percentage points
- Repairs: `0`
- Regressions: `1`
- Net gain: `-1`

## Interpretation

The Table 1 paper claim remains `blocked` because this was not the paper's Table 1 benchmark setup. The AIME smoke validation itself is `not_reproduced` because the generated skill hurt held-out smoke performance.
