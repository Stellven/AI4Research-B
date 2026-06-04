# Figure 7 Trace Extraction Contract

Status: `blocked_pending_full_per_round_trace_inventory`

This contract defines how to extract Figure 7 evidence from SkillGen refinement
round traces. It does not claim reproduction until the paper-scale trace set is
available.

## Required Files Per Round

For every benchmark-model run and every refinement round:

```text
verification/round_*/verification_baseline.jsonl
verification/round_*/verification_with_skill.jsonl
verification/round_*/verification_summary.json
verification/round_*/verification_case_analyses.json
```

Each round also needs a link to the candidate skill artifact evaluated in that
round, normally under:

```text
artifacts/raw_benchmark_outputs/**/candidates/*_gen.json
```

## Round Record Schema

Each extracted round should produce one normalized record:

```json
{
  "run_id": "string",
  "benchmark_row": "string",
  "paper_model": "string",
  "round_index": 1,
  "candidate_skill_id": "string",
  "candidate_skill_artifact": "path",
  "baseline_trace_path": "path",
  "with_skill_trace_path": "path",
  "case_analyses_path": "path",
  "paired_n": 0,
  "baseline_acc": 0.0,
  "skill_acc": 0.0,
  "delta_acc": 0.0,
  "repair_count": 0,
  "regression_count": 0,
  "net_gain": 0,
  "gate_passed": false
}
```

## Extraction Steps

1. Inventory every `verification/round_*` directory for each benchmark-model run.
2. Reject a round record unless baseline traces, with-skill traces, summary, and case analyses are all present.
3. Parse `verification_summary.json` as the source of accuracy, repair, regression, net gain, and gate pass/fail fields.
4. Link each round to its candidate skill artifact before calculating best-of-K.
5. Sort rounds by numeric `round_index`.
6. Compute `best_of_k_skill_acc` as the cumulative max `skill_acc` over rounds within a run.

## Aggregation Rules

- `per_round_skill_accuracy[K] = mean(skill_acc for round K across included runs)`.
- `best_of_k_skill_accuracy[K] = mean(max(skill_acc for rounds <= K) across included runs)`.
- Confidence intervals must be computed over run-level curves, not pooled individual cases.
- Missing round traces make the run incomplete for Figure 7, even if a final skill artifact exists.

## Completion Standard

Figure 7 can move out of blocked only when the run package contains the full
representative per-round trace inventory needed to recompute individual-round
and best-of-K aggregate curves.
