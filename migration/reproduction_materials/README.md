# SkillGen Reproduction Materials

This directory is a migration copy of the Phase 0 materials needed to inspect and
reproduce the SkillGen paper-claim validation work.

## Copied Sources

- `phase_0/runs/20260602/`: initial SkillGen Phase 0 run package, including:
  - `input/paper.pdf`
  - extracted paper parse and claim artifacts
  - official code checkout under `code/official`
  - bundled benchmark data, baselines, and external source material
  - command, environment, review, output, integration, and playback artifacts
- `phase_0/runs/20260603/` through `phase_0/runs/20260610/`: follow-up artifacts,
  expanded claim matrices, benchmark contracts, validation outputs, and run logs.

## Key Entry Points

- Initial paper copy:
  `phase_0/runs/20260602/input/paper.pdf`
- Initial extracted claims:
  `phase_0/runs/20260602/artifacts/02_claims/claims.md`
  `phase_0/runs/20260602/artifacts/02_claims/claims.json`
  `phase_0/runs/20260602/artifacts/02_claims/benchmark_claims.json`
- Expanded all-claim catalog:
  `phase_0/runs/20260604/artifacts/02_claims/all_claims.md`
  `phase_0/runs/20260604/artifacts/02_claims/all_claims.json`
- Official code:
  `phase_0/runs/20260602/code/official`
- Official code manifest:
  `phase_0/runs/20260602/artifacts/03_code_and_sources/code_manifest.json`
- Command and environment records:
  `phase_0/runs/20260602/artifacts/04_commands_and_environment`
- Final validation report:
  `phase_0/runs/20260604/artifacts/00_run_summary/research_validation_report.md`

## Exclusions

The copy intentionally excludes rebuildable local runtime directories and caches:

- `.venv`
- `.uv-cache`
- `.hf-cache`
- `__pycache__`
- `.DS_Store`

These exclusions are not validation evidence. Dependencies should be reinstalled
inside the project directory when needed, following the command and environment
artifacts in the run package.
