# SkillGen Phase 0 Automated Validation Report

Run ID: `skillgen_phase0_demo_20260601_002144`

## Overall Status

`not_reproduced`

## Full Paper Claim Status

`blocked`

The current automation targets the SkillGen AIME smoke validation. It does not claim to reproduce the full Table 1 result unless a matching Table 1 contract is executed.

## Input

- Paper source: `meeting docs/SkillGen.pdf`
- Paper copy: `input/paper.pdf`

## Verification Contract

- Target: `skillgen_aime_smoke`
- Scope: `official-code smoke only; not full Table 1 reproduction`
- Dataset: `aime`
- Train subset: `artifacts/smoke_data/aime_train_n8_seed42.json`
- Test subset: `artifacts/smoke_data/aime_test_n4_seed42.json`

## Official Code

- Repository: `https://github.com/yccm/SkillGen`
- Local path: `code/official`
- Commit: `3c4537bb12ac287ceb1b5d410b491206089fdcb7`
- Intake status: `intake_complete`

## Benchmark Result

- Benchmark status: `official_code_smoke_completed`
- Baseline accuracy: `50.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `-25.0%`
- Repairs: `0`
- Regressions: `1`
- Net gain: `-1`

## All-Claim Verification

- Claim status counts: `blocked=6, not_testable=4, partially_reproduced=2`
- Matrix: `artifacts/all_claim_verification_matrix.json`
- Catalog: `artifacts/all_claims.json`

## Evidence Files

- `artifacts/verification_contract.json`
- `artifacts/command_plan.json`
- `artifacts/all_claims.json`
- `artifacts/all_claim_verification_matrix.json`
- `outputs/install_stdout.txt`
- `outputs/install_stderr.txt`
- `outputs/benchmark_stdout.txt`
- `outputs/benchmark_stderr.txt`
- `artifacts/benchmark_results.json`
- `artifacts/claim_comparison.json`

## Limitations

- This is a paper-specific automation POC.
- The selected target is a low-cost AIME smoke validation, not the paper's full Table 1 benchmark matrix.
- Live install and benchmark execution require `artifacts/approval.json` plus API keys.
