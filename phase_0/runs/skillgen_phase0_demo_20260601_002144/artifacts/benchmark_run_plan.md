# Benchmark Run Plan

Status: `requires_human_approval`

## Chosen Cheapest Target

Use the official repo's AIME quick-start path as a low-cost smoke validation:

- training subset: `artifacts/smoke_data/aime_train_n8_seed42.json`
- eval subset: `artifacts/smoke_data/aime_test_n4_seed42.json`
- smoke config: `artifacts/skillgen_aime_smoke_config.yaml`

This is deliberately **not** a Table 1 reproduction. It validates that the official SkillGen pipeline can run end-to-end under recorded conditions at minimal cost.

## Why AIME

- README uses AIME in Quick Start.
- Bundled data is available in the official repo.
- AIME has short inputs relative to bundled MCP, Mind2Web, PubMedQA, ScienceWorld, SocialMaze, and ToolBench splits.
- `benchmarks/aime_grader.py` uses deterministic integer extraction and exact match, reducing judge cost/noise.

## Planned Steps After Approval

1. Create repo-local official-code venv.
2. Install `requirements.txt` into that venv using repo-local uv cache.
3. Verify API key names are visible without printing values.
4. Run the AIME smoke train command.
5. Locate the generated skill output directory.
6. Run the corrected eval command using `--skill-repo` and the 4-instance smoke test subset.
7. Parse `eval_results.json`, token usage, trajectories, repairs, regressions, and net gain.
8. Write `benchmark_results.json`, `claim_comparison.json`, and update the validation report.
