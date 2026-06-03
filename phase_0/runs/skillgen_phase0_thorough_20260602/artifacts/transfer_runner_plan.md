# Cross-Model Transfer Runner Plan

Cross-model transfer runner plan for SkillGen Figure 4

Paper claim: 120 off-diagonal comparisons; 70% non-negative and 42% exceed +5 percentage points.

Planned off-diagonal comparisons: `120`

## Benchmarks

| Benchmark | Dataset status | Train/Test | Blockers |
| --- | --- | --- | --- |
| `alfworld_ood` | `blocked_canonical_code_fetched_missing_skillgen_contract` | `missing / missing` | Canonical ALFWorld code is fetched, but no SkillGen-compatible ALFWorld adapter and paper-matching IOD/OOD train/test split contract exists. |
| `scienceworld` | `ready_for_execution` | `data/scienceworld/train.json / data/scienceworld/test.json` |  |
| `mind2web` | `ready_for_execution` | `data/mind2web/train.json / data/mind2web/test.json` |  |
| `socialmaze_fts` | `ready_for_execution` | `data/socialmaze/train.json / data/socialmaze/test.json` |  |

## Remaining Blockers

- ALFWorld OOD data is not available in the current official checkout.
- ALFWorld OOD canonical code is fetched but still lacks a SkillGen-compatible adapter/split contract.
