# Baseline Native Feasibility Verification

Date: 2026-06-10

Scope: stricter verification of the open-source baseline-code solution. This checks whether each native baseline repository is locally present and probe-runnable, and whether it has actually been adapted to consume SkillGen trajectories and export the single Markdown skill required by the shared evaluator.

## Status Counts

- `library_import_or_compile_verified_no_cli_adapter`: 1
- `native_cli_or_compile_verified_benchmark_adapter_missing`: 1
- `native_entrypoints_help_verified_domain_mismatch`: 1
- `source_page_only_no_native_code`: 1

## Verdict Table

| Method | Probe status | Source identity solved | Native SkillGen adapter verified | Interpretation |
| --- | --- | --- | --- | --- |
| `Trace2Skill` | `native_entrypoints_help_verified_domain_mismatch` | `True` | `False` | Trace2Skill has runnable native entrypoints, but they target SpreadsheetBench logs/skills. This verifies source-code availability, not a SkillGen-trajectory adapter. |
| `SkillX` | `library_import_or_compile_verified_no_cli_adapter` | `True` | `False` | SkillX source can be compiled/imported locally, but the repo has no verified CLI that consumes SkillGen trajectories and exports one static Markdown skill. |
| `EvoSkill` | `native_cli_or_compile_verified_benchmark_adapter_missing` | `True` | `False` | EvoSkill has native code/CLI surfaces, but no verified project/config adapter maps SkillGen trajectories into EvoSkill and exports a single Markdown skill. |
| `CoEvoSkills` | `source_page_only_no_native_code` | `False` | `False` | The local CoEvoSkills repository is a project page/assets repository, not an executable baseline implementation. |

## Method Details

### Trace2Skill

- Probe status: `native_entrypoints_help_verified_domain_mismatch`
- Local commit: `3d0b52a140f002a512930252b613c49048f7d5ac`
- Remote HEAD: `3d0b52a140f002a512930252b613c49048f7d5ac`
- Python files: `38`
- Source identity solved: `True`
- Native SkillGen adapter verified: `False`
- Interpretation: Trace2Skill has runnable native entrypoints, but they target SpreadsheetBench logs/skills. This verifies source-code availability, not a SkillGen-trajectory adapter.
- Evidence:
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/trace2skill/repo_identity_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/trace2skill/py_compile_core_entrypoints_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/trace2skill/analyze_results_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/trace2skill/error_analysis_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/trace2skill/success_analysis_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/trace2skill/skill_evolution_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/baselines/Trace2Skill/README.md`
- Missing or failed:
  - None from bounded probes.

### SkillX

- Probe status: `library_import_or_compile_verified_no_cli_adapter`
- Local commit: `0137cb8c2f9e69d5cc499e562dea789b2c5a8e35`
- Remote HEAD: `0137cb8c2f9e69d5cc499e562dea789b2c5a8e35`
- Python files: `90`
- Source identity solved: `True`
- Native SkillGen adapter verified: `False`
- Interpretation: SkillX source can be compiled/imported locally, but the repo has no verified CLI that consumes SkillGen trajectories and exports one static Markdown skill.
- Evidence:
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/skillx/repo_identity_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/skillx/py_compile_pipeline_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/skillx/package_import_pipeline_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/skillx/pipeline_script_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/baselines/SkillX/README.md`
- Missing or failed:
  - pipeline_script_help exited 1

### EvoSkill

- Probe status: `native_cli_or_compile_verified_benchmark_adapter_missing`
- Local commit: `925229680ac4ceebedb44bc548dfb82631c66525`
- Remote HEAD: `925229680ac4ceebedb44bc548dfb82631c66525`
- Python files: `151`
- Source identity solved: `True`
- Native SkillGen adapter verified: `False`
- Interpretation: EvoSkill has native code/CLI surfaces, but no verified project/config adapter maps SkillGen trajectories into EvoSkill and exports a single Markdown skill.
- Evidence:
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/evoskill/repo_identity_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/evoskill/py_compile_cli_and_scripts_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/evoskill/cli_module_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/evoskill/run_loop_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/evoskill/run_eval_help_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/baselines/EvoSkill/README.md`
- Missing or failed:
  - run_loop_help exited 1
  - run_eval_help exited 1

### CoEvoSkills

- Probe status: `source_page_only_no_native_code`
- Local commit: `3171de28cc8d3c3bbbec0ef5445e59faca46815b`
- Remote HEAD: `3171de28cc8d3c3bbbec0ef5445e59faca46815b`
- Python files: `0`
- Source identity solved: `False`
- Native SkillGen adapter verified: `False`
- Interpretation: The local CoEvoSkills repository is a project page/assets repository, not an executable baseline implementation.
- Evidence:
  - `phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/coevoskills/repo_identity_status.json`
  - `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/baselines/CoEvoSkills/README.md`
- Missing or failed:
  - No Python/source implementation files were found in the local CoEvoSkills repository.

## Bottom Line

The baseline-code solution is now verified for source identity for Trace2Skill, SkillX, and EvoSkill, and those repos have at least some local executable or importable surfaces. CoEvoSkills is not verified as executable code because the local repository contains only project-page assets and states that code is coming soon. None of the four native algorithms is yet verified as a SkillGen-compatible adapter that consumes SkillGen trajectories and exports exactly one Markdown skill. Therefore the earlier mechanical baseline-comparison smoke solves the evaluator-output-contract issue, but not the stricter native-baseline-execution issue.
