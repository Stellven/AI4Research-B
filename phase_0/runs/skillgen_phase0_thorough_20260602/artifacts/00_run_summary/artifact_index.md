# Artifact Index

This directory was reorganized into stage-based subdirectories so the Phase 0 run can be
read in workflow order.

## Directory Map

- `00_run_summary/`: final report, approval policy, automation state, and this index.
- `01_research_parse/`: parsed paper text and paper metadata.
- `02_claims/`: selected claims, benchmark claims, all-claim catalog, and claim verification matrix.
- `03_code_and_sources/`: official repository metadata plus external/canonical source intake plans and statuses.
- `04_commands_and_environment/`: official instruction extraction, command plan, and environment records.
- `05_reviews_and_approval/`: human review markers, approval template, and compatibility link to the approval policy.
- `06_plans_and_contracts/`: verification contract, benchmark plans, transfer/token plans, and model route mapping.
- `07_configs_and_inputs/`: generated benchmark configs and reduced smoke input data.
- `08_results/`: parsed benchmark results, claim comparison, and raw benchmark outputs.
- `09_safety_and_deviations/`: known blockers, failure modes, hardcoding disclosures, and recorded deviations.

## Compatibility Links

These legacy paths are preserved as symlinks because existing artifacts refer to them:

- `raw_benchmark_outputs -> 08_results/raw_benchmark_outputs`
- `generated_configs -> 07_configs_and_inputs/generated_configs`
- `smoke_data -> 07_configs_and_inputs/smoke_data`
- `approval.json -> 00_run_summary/approval.json`
- `05_reviews_and_approval/approval.json -> ../00_run_summary/approval.json`
