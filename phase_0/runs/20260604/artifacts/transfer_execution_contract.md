# Transfer Execution Contract

Cross-model transfer execution and aggregation contract for SkillGen Figure 4

Status: `blocked`
Planned comparisons: `120` of `120`

## Benchmark Readiness

- Ready: `scienceworld, mind2web, socialmaze_fts`
- Blocked: `alfworld_ood`

## Comparison Contract

- Only source_model != evaluator_model pairs count toward the 120 off-diagonal comparisons.
- Compare transferred_eval skill_acc against the same evaluator model's no-skill baseline_acc on the same held-out instances.
- Use the same benchmark split for source skill construction, evaluator baseline, and transferred-skill evaluation.
- Record gate-deprecated source skills explicitly; do not silently drop those source/evaluator pairs.

## Aggregation Rules

- non_negative_rate = count(delta_acc >= 0) / 120 after all off-diagonal comparisons are parsed.
- exceed_5pp_rate = count(delta_acc > 0.05) / 120 after all off-diagonal comparisons are parsed.
- A partial transfer matrix can be reported only as incomplete evidence and must not be compared as the paper Figure 4 result.
