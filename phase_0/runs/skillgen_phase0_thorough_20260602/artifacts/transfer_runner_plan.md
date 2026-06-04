# Cross-Model Transfer Runner Plan

Cross-model transfer runner plan for SkillGen Figure 4

Paper claim: 120 off-diagonal comparisons; 70% non-negative and 42% exceed +5 percentage points.

Planned off-diagonal comparisons: `120`

## Benchmarks

| Benchmark | Dataset status | Train/Test | Blockers |
| --- | --- | --- | --- |
| `alfworld_ood` | `ready_for_reconstructed_execution` | `data/alfworld_ood/train.json / data/alfworld_ood/test.json` | Reconstructed ALFWorld offline-plan adapter data is present and load-smoked; full execution still requires human approval of the deviation label, model route, cost, and trace-retention policy. |
| `scienceworld` | `ready_for_execution` | `data/scienceworld/train.json / data/scienceworld/test.json` |  |
| `mind2web` | `ready_for_execution` | `data/mind2web/train.json / data/mind2web/test.json` |  |
| `socialmaze_fts` | `ready_for_execution` | `data/socialmaze/train.json / data/socialmaze/test.json` |  |

## Remaining Blockers

- ALFWorld OOD has a Group A reconstructed-execution contract package.
- Transfer execution still needs approved canonical data download, adapter implementation, generated OOD train/test TaskInstance files, and per-round trace retention.
