# Group F Final Report Patch Plan

Date: 2026-06-04

Scope: Standard language and structure for integrating future group A-E outputs
into `research_validation_report.md` without overstating reproduction status.

## Report Goals

The final Phase 0 report must answer four questions:

1. What exact paper claim was validated?
2. What evidence was used: official, canonical-source reconstructed,
   deviation-backed reconstructed, smoke-scale, failed, or negative?
3. What did the observed logs and parsed results show?
4. What remains blocked, not testable, or outside exact reproduction?

## Required Sections

The report should contain these sections in this order when full integration
artifacts exist:

1. `Overall Status`
2. `Full Paper Claim Status`
3. `Evidence Classification`
4. `Input`
5. `Official Code`
6. `Human Review Gates`
7. `Benchmark / Execution Coverage`
8. `Claim-Level Status Summary`
9. `Claim-Level Non-Success Details`
10. `Deviation Disclosures`
11. `Evidence Files`
12. `Limitations`
13. `Next Actions`

Minimal/smoke reports may keep the shorter current structure, but they must
explicitly state `artifact_mode=minimal` and must not imply full-paper
reproduction.

## Evidence Classification Language

Use exact phrases from this table.

| Evidence class | Report phrase |
| --- | --- |
| `exact_reproduction` | "exact reproduction evidence" |
| `official_code_reproduction` | "official-code execution evidence" |
| `canonical_source_reconstruction` | "canonical-source reconstruction evidence" |
| `deviation_backed_reconstruction` | "deviation-backed reconstructed verification evidence" |
| `smoke_scale_execution` | "smoke-scale execution evidence" |
| `executed_negative_evidence` | "executed negative evidence" |
| `failed_execution_evidence` | "failed execution evidence with preserved logs" |
| `planning_only` | "planning evidence only, not validation evidence" |

## Status Wording

Use these wording rules in the report:

- `reproduced`: "Observed results match the paper claim under the approved
  comparison rule."
- `partially_reproduced`: "Observed results support part of the claim, but the
  evidence is limited by scope, scale, reconstruction, or missing rows."
- `not_reproduced`: "Observed execution completed and did not support the paper
  claim."
- `failed_to_run`: "Approved execution was attempted and failed; preserved logs
  are the current evidence."
- `blocked`: "The validation target is clear, but a recoverable contract,
  artifact, approval, or execution path is missing."
- `not_testable`: "Current official materials are insufficient to define a
  faithful validation task."
- `ready_for_execution`: "A reviewable execution path exists, but no validation
  result should be inferred until it runs."

## Deviation Section

Every active deviation must be summarized with:

- deviation id.
- affected claims.
- evidence class.
- what changed.
- why the change was needed.
- expected impact on validity.
- approval artifact.
- raw logs or result artifacts produced under the deviation.

Suggested Markdown:

```text
### <deviation_id>

- Evidence class: `<evidence_class>`
- Affected claims: `<claim_id list>`
- What changed: <one sentence>
- Why needed: <one sentence>
- Impact: <one sentence>
- Approval: `<artifact path or pending>`
- Report interpretation: <exact/canonical/reconstructed/smoke wording>
```

## Claim Summary Table

The final report should keep a compact claim table with these columns:

| Column | Source |
| --- | --- |
| Claim | `all_claim_verification_matrix.json.claims[].claim_id` |
| Status | matrix row status |
| Evidence class | matrix row evidence_class or inferred class |
| Compared / required evidence | matrix row evidence and blockers |
| Reason | status-specific reason from matrix row |
| Next step | matrix row next_step |

Do not manually edit the Markdown table in a way that disagrees with the JSON
matrix. Regenerate or patch both together.

## Evidence Files Section

List only files that exist or are expected from a reviewed command plan. Split
them into groups:

```text
## Evidence Files

### Contracts and Plans
- `artifacts/verification_contract.json`
- `artifacts/benchmark_execution_plan.json`

### Deviation and Review
- `artifacts/hardcoding_disclosures.json`
- `artifacts/deviation_disclosures.json`
- `artifacts/05_reviews_and_approval/human_command_review.md`

### Raw Outputs
- `outputs/install_stdout.txt`
- `outputs/install_stderr.txt`
- `artifacts/raw_benchmark_outputs/...`

### Parsed Results and Comparisons
- `artifacts/benchmark_results.json`
- `artifacts/claim_comparison.json`
- `artifacts/all_claim_verification_matrix.json`
```

If a file is missing, say why instead of listing it as evidence.

## Integration Patch Order

Patch the report only after these artifacts are internally consistent:

1. status transition records.
2. deviation disclosures.
3. benchmark execution or trace aggregation plan.
4. parsed results and claim comparison, if execution happened.
5. all-claim matrix JSON and Markdown.
6. final report.

## Current SkillGen Claim Language

Use these report interpretations for the current unresolved claims until new
artifacts change them:

| Claim | Current report language |
| --- | --- |
| `claim_table1_average_gains_all_models` | Blocked: full Table 1 requires ALFWorld IOD/OOD, LiveCodeBench split, and complete 80-entry execution. |
| `claim_table1_entry_counts` | Blocked: 50/25/5 counts require parsed deltas for all 80 entries. |
| `claim_table1_alfworld_scienceworld_patterns` | Blocked: ScienceWorld evidence does not replace missing ALFWorld IOD/OOD adapter and split evidence. |
| `claim_cross_model_transfer` | Blocked: transfer plan must include ALFWorld OOD to cover all 120 off-diagonal comparisons. |
| `claim_refinement_best_of_k` | Blocked: Figure 7 needs per-round trace retention and aggregation. |
| `claim_baseline_generator_comparison` | Not testable until baseline source identity and single-skill adapters are reviewed. |
| `claim_ablation_full_wins` | Not testable until A1-A5 configs are defined or reconstructed with disclosure. |

## Final Acceptance Checks

Before considering the report integrated:

- No reconstructed run is labeled exact reproduction.
- No planning-only artifact is presented as validation evidence.
- Every claim status has a reason and next step.
- Every execution status links to raw logs and parsed results.
- Every deviation affecting a claim appears in the deviation section.
- Existing failed or negative evidence remains visible.
- Human review gates are referenced for claim, command, result, and final review.
