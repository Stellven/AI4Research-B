# SkillGen All-Claims Catalog

This catalog covers the major empirical and executable claims detected for the SkillGen Phase 0 POC.

## claim_method_paired_intervention

- Type: `method_contract`
- Location: Abstract, Section 2, Section 3
- Verification mode: `official_code_structure_and_smoke_output`

SkillGen models skills as inference-time interventions and evaluates the same instances with and without a generated skill, accounting for repairs and regressions.

## claim_table1_average_gains_all_models

- Type: `main_result`
- Location: Section 4, Table 1
- Verification mode: `full_table1_matrix`

SkillGen improves average held-out accuracy for all eight evaluated base LLMs, with gains from +3.27 to +10.08 percentage points.

## claim_table1_entry_counts

- Type: `main_result`
- Location: Section 4, Table 1
- Verification mode: `full_table1_matrix`

Out of 80 held-out benchmark-split-model entries, 50 improve, 25 remain unchanged, and 5 regress.

## claim_table1_alfworld_scienceworld_patterns

- Type: `main_result_breakdown`
- Location: Section 4, Table 1
- Verification mode: `full_table1_subset`

ALFWorld improves in 14 of 16 entries and ScienceWorld improves for all eight agents.

## claim_baseline_generator_comparison

- Type: `baseline_comparison`
- Location: RQ2, Figure 2, Appendix C.6
- Verification mode: `baseline_generator_matrix`

SkillGen is consistently positive and achieves the largest average improvement compared with Trace2Skill, SkillX, EvoSkill, and CoEvoSkills.

## claim_ablation_full_wins

- Type: `ablation`
- Location: RQ3, Figure 3
- Verification mode: `ablation_matrix`

The full SkillGen system wins on every ablation dataset-model pair, showing that contrastive induction, refinement, verification gate, failure lessons, and script/reference bundles contribute.

## claim_cross_model_transfer

- Type: `transfer`
- Location: RQ4, Figure 4
- Verification mode: `transfer_matrix`

Generated skills often transfer across models; across 120 off-diagonal comparisons, 70% are non-negative and 42% exceed +5 percentage points.

## claim_tau_bench_gate_activated

- Type: `additional_benchmark`
- Location: RQ5, Figure 5
- Verification mode: `tau_bench_matrix`

On tau-Bench retail, SkillGen improves every model whose verification gate activated.

## claim_chemllmbench_useful_gains

- Type: `additional_benchmark`
- Location: RQ5, Figure 6
- Verification mode: `chemllmbench_matrix`

On ChemLLMBench property and yield prediction, SkillGen provides useful gains in the reported settings.

## claim_refinement_best_of_k

- Type: `refinement_analysis`
- Location: RQ5, Figure 7
- Verification mode: `refinement_trace_analysis`

Best-of-K selection over refinement rounds improves aggregate skill accuracy over individual rounds in representative runs.

## claim_token_cost

- Type: `cost_analysis`
- Location: Appendix C.5, Table 4
- Verification mode: `token_usage_aggregation`

Skill construction token cost ranges from 2.2M to 10.2M tokens across listed benchmarks, with mean 5.6M and about $8.2 per generated skill under the stated pricing.

## claim_auditable_skill_artifact

- Type: `artifact_property`
- Location: Abstract, Contributions
- Verification mode: `official_code_output_inspection`

SkillGen produces a single human-readable auditable skill artifact that can be inspected before use.
