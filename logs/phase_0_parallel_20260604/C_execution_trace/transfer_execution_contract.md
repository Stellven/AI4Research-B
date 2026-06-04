# Transfer Execution Contract

Status: `blocked_pending_ALFWorld_OOD_contract`

This contract defines how SkillGen Phase 0 should execute and aggregate the
cross-model transfer claim for Figure 4.

## Matrix Shape

- Benchmarks: `alfworld_ood`, `scienceworld`, `mind2web`, `socialmaze_fts`.
- Source models: `Qwen-2.5-7B`, `Llama-3.1-8B`, `GPT-OSS-20B`, `GPT-5.4-Nano`, `GPT-5.4-Mini`, `Grok-4-Fast`.
- Evaluator models: same six-model set.
- Counted pairs: source model and evaluator model must be different.
- Off-diagonal pairs per benchmark: `6 * 5 = 30`.
- Required comparisons: `4 benchmarks * 30 pairs = 120`.

## Execution Manifest

Each transfer comparison should be represented by one manifest row:

```json
{
  "comparison_id": "{benchmark_row}::{source_model}::{evaluator_model}",
  "benchmark_row": "{benchmark_row}",
  "source_model": "{source_model}",
  "evaluator_model": "{evaluator_model}",
  "source_skill_dir": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/{source_model_slug}/skill_output",
  "evaluator_baseline": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/baselines/{evaluator_model_slug}/eval_results.json",
  "transferred_eval": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/{source_model_slug}/{evaluator_model_slug}/eval_results.json",
  "transferred_trajectories": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/{source_model_slug}/{evaluator_model_slug}/eval_results_trajectories"
}
```

## Comparison Rules

- Count only off-diagonal source/evaluator pairs.
- Evaluate each transferred skill on the same held-out instances used by the evaluator baseline.
- Compare transferred-skill accuracy against the evaluator model's no-skill baseline accuracy.
- Record verification-gate-deprecated source skills explicitly; do not silently skip those pairs.
- Keep source skill generation logs separate from transferred evaluator logs.

## Aggregation Rules

- `delta_acc = transferred_skill_acc - evaluator_baseline_acc`.
- `non_negative_rate = count(delta_acc >= 0) / 120`.
- `exceed_5pp_rate = count(delta_acc > 0.05) / 120`.
- Compare those rates to the paper's `70% non-negative` and `42% exceed +5 pp` only after all 120 comparisons are parsed.

## Current Blocker

`alfworld_ood` is still blocked until Group A provides a SkillGen-compatible
ALFWorld OOD adapter and split contract. Without it, 30 of the 120 comparisons
are missing and Figure 4 cannot be fully reproduced.
