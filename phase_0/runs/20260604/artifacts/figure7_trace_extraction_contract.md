# Figure 7 Trace Extraction Contract

Figure 7 per-round refinement trace extraction and aggregation contract

Status: `blocked`
Current complete rounds: `1` of `1` with summaries

## Required Trace Globs

- `verification_baseline`: `artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_baseline.jsonl`
- `verification_with_skill`: `artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_with_skill.jsonl`
- `verification_summary`: `artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_summary.json`
- `verification_case_analyses`: `artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_case_analyses.json`
- `candidate_skill`: `artifacts/raw_benchmark_outputs/**/candidates/*_gen.json`

## Extraction Steps

- Inventory every verification/round_* directory for each benchmark-model run.
- Reject a round record unless baseline traces, with-skill traces, summary, and case analyses are all present.
- Parse verification_summary.json as the source of accuracy, repair, regression, net_gain, and gate fields.
- Link each round to its candidate skill artifact before calculating best-of-K.
- Compute best_of_k_skill_acc as the cumulative max skill_acc over ordered rounds within a run.
- Aggregate per-round and best-of-K curves across representative runs only after the full paper-scale trace set is available.

## Aggregation Rules

- per_round_skill_accuracy[K] = mean(skill_acc for round K across included runs).
- best_of_k_skill_accuracy[K] = mean(max(skill_acc for rounds <= K) across included runs).
- Confidence intervals must be computed over run-level curves, not over individual cases pooled across runs.
