# SkillGen All-Claims Catalog

This catalog covers the major empirical and executable claims detected for the SkillGen Phase 0 POC.

## claim_method_paired_intervention

- Type: `method_contract`
- Location: Abstract, Section 2, Section 3
- Verification mode: `official_code_structure_and_smoke_output`

SkillGen models skills as inference-time interventions and evaluates the same instances with and without a generated skill, accounting for repairs and regressions.

Evidence anchor:

> er both successful and failed trajectories to identify reusable success patterns, recurring failure modes, and behaviors that appear in nearby successes but are missing from failures. SKILLGENthen generates candidate skills and iteratively refines the skill. A key novelty in SKILLGENis that we model agent skills as interventions to empirically verify the net effect of skills on the overall performance. Specifically, we compare outcomes on the same instances with and without the skill, so that we account for both repairs (cases where the skill fixes a baseline failure) and regressions (cases where the skill breaks a baseline success). Across a broad range of agents and datasets, SKILLGENconsistently improves held-out performance, outperforms existing skill-generation baselines, and produces skills that transfer across models. 1 Introduction Large language models (LLMs) are increasingly used to so

## claim_table1_average_gains_all_models

- Type: `main_result`
- Location: Section 4, Table 1
- Verification mode: `full_table1_matrix`

SkillGen improves average held-out accuracy for all eight evaluated base LLMs, with gains from +3.27 to +10.08 percentage points.

Evidence anchor:

> skill and its active/deprecated status is fixed using only the skill- training dataset: the induction subset for trajectory analysis and the construction-time verification subset for refinement and selection. Table 1 reports the no-skill baseline accuracy, the skill-augmented accuracy, and the absolute accuracy change over 80 held-out benchmark–split–model combinations. Table 1 shows three main patterns: (i) SKILLGENimproves average accuracy for all eight base agents, with gains from +3.27 to +10.08 percentage points; (ii) the effect holds across both open-weight 3Here, gabs ∈Z ≥0 is an absolute minimum number of net repairs, and grel ∈[0,1] is a relative minimum as a fraction of the construction-time verification subset. The gate is a simple construction-time safeguard: the absolute term prevents deploying candidates whose gain is negligible in count, the relative term requires

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

Evidence anchor:

> entative benchmark–model entries. Mini, Grok, and Gemma denote GPT-5.4-Mini, Grok-4-Fast, and Gemma-4-26B, respectively. All methods use the same evalua- tion harness. models (+3.27to+4.77pp) and proprietary models (+4.79to+10.08pp); and (iii) out of 80 held- out benchmark–split–model entries, 50 improve, 25 remain unchanged, and only 5 show regressions. The largest gains appear on procedural, multi-step benchmarks: ALFWorld improves in 14 of 16 entries, and ScienceWorld improves for all eight agents. Further, SKILLGENis especially useful when the base model has enough task capability to execute a learned procedure but still has room to improve. RQ2 How does SKILLGENcompare with state-of-the-art automatic skill-generation baselines? We compare SKILLGENagainst four recent skill-generation baselines:Trace2Skill(Ni et al., 2026), SkillX(Wang et al., 2026a),EvoSkill(Al

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

Evidence anchor:

> training it, then executing it with a different evaluator model on ALFWorld OOD, ScienceWorld, Mind2Web, and SocialMaze FTS. Each transferred skill is compared against the evaluator’s own no-skill baseline; skills marked ‘deprecated’ by the source pipeline are retained as no-op skills. Figure 4 shows that SKILLGENproduces skills that often transfer across models, but relevant is the choice of skill-generating model. Across 120 off-diagonal comparisons, 70% are non-negative, and 42% exceed +5 pp. We see a clear pattern: transferable skills are not simply written by the strongest baseline agents; on ALFWorld, Qwen-2.5-7B is the best skill-generating model on average, while, onScienceWorld,GPT-5.4-Nanois best. 8 <!-- page 9 --> Qwen-2.5-7BLlama-3.1-8BGPT-OSS-20BGPT-5.4-nanoGPT-5.4-miniGrok-4-fast 0% 20% 40% 60% 80%Accuracy Property prediction +13.3 37 50 43 +13.6 55

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

Evidence anchor:

> ienceWorld,GPT-5.4-Nanois best. 8 <!-- page 9 --> Qwen-2.5-7BLlama-3.1-8BGPT-OSS-20BGPT-5.4-nanoGPT-5.4-miniGrok-4-fast 0% 20% 40% 60% 80%Accuracy Property prediction +13.3 37 50 43 +13.6 55 68 ±0.0 57 ±0.0 63 ±0.0 67 Llama-3.1-8BQwen-2.5-7BGPT-OSS-20BGPT-5.4-miniGrok-4-fastGPT-5.4-nano Yield prediction +6.7 27 33 +40.0 30 70 ±0.0 41 +26.7 43 70 +16.7 47 63 +6.7 63 70 Baseline (no skill) With SkillGen skill Figure 6:Insights for ChemLLMBench.Held-out accuracy on ChemLLMBench property prediction (left) and yield prediction (right). Gray bars are no-skill baselines and teal bars apply the SKILLGEN skill; bars labeled “±0.0” or “gate off” indicate no measurable change or rejection by the verification gate. 1 2 3 4 5 6 7 8 Refinement round r 20% 40% 60% 80% 100% Paired accuracy (with skill) = accuracy of the candidate produced at round r alone (no gate / no

## claim_refinement_best_of_k

- Type: `refinement_analysis`
- Location: RQ5, Figure 7
- Verification mode: `refinement_trace_analysis`

Best-of-K selection over refinement rounds improves aggregate skill accuracy over individual rounds in representative runs.

Evidence anchor:

> SKILLGEN skill; bars labeled “±0.0” or “gate off” indicate no measurable change or rejection by the verification gate. 1 2 3 4 5 6 7 8 Refinement round r 20% 40% 60% 80% 100% Paired accuracy (with skill) = accuracy of the candidate produced at round r alone (no gate / no selection) dashed = paired baseline for that (model, dataset) (a) Per-round skill accuracy 1 2 3 4 5 6 7 8 Refinement budget K 20% 40% 60% 80% 100% Best-of-K skill accuracy = max accuracy in rounds 1 : K (what SkillGen's gate keeps) (b) Best-so-far across rounds 1 2 3 4 5 6 7 8 Refinement round r (or budget K) -4.0% -2.0% +0.0% +2.0% +4.0% +6.0% +8.0% +10.0% accuracy (skill baseline) red = expected per-round acc; blue = expected best-of-K acc (c) Aggregate over all runs per-round acc (mean ± 95% CI) best-of-K acc (mean ± 95% CI) ALFWorld · gemma-4-26b ALFWorld · qwen-2.5-7b ALFWorld · 

## claim_token_cost

- Type: `cost_analysis`
- Location: Appendix C.5, Table 4
- Verification mode: `token_usage_aggregation`

Skill construction token cost ranges from 2.2M to 10.2M tokens across listed benchmarks, with mean 5.6M and about $8.2 per generated skill under the stated pricing.

Evidence anchor:

> cess guard checks to expose regressions on already-solved instances. Skills that fail the gate are persisted with statusdeprecated; downstream evaluation treats them as empty interventions, so cells labeled “gate off” report zero change rather than an unverified skill. The pipeline uses four workers for independent runs, and the verification agent’s feedback stage uses eight workers. C.5 Token Cost Analysis Table 4: Token cost of SKILLGEN.Trainis the one-time construction budget; BASEand SKILLare average tokens per call. Benchmark Train BASE SKILL (M tok) (tok/call) (tok/call) ScienceWorld 2.2 1,630 1,977 PubMedQA2.7 1,173 2,429 Mind2Web 5.2 4,482 5,919 MCPBench7.5 4,847 6,000 τ-Bench 10.2 5,813 6,358 Mean 5.6 3,589 4,537 Median 5.2 4,482 5,919 Table 4 separates one-time construction cost from per-call inference overhead. All values are computed per 

## claim_auditable_skill_artifact

- Type: `artifact_property`
- Location: Abstract, Contributions
- Verification mode: `official_code_output_inspection`

SkillGen produces a single human-readable auditable skill artifact that can be inspected before use.

Evidence anchor:

> ley3 Xiangliang Zhang2 Stefan Feuerriegel1 1Munich Center for Machine Learning, LMU Munich 2University of Notre Dame 3Microsoft Research Abstract Skills are a promising way to improve LLM agent capabilities without retraining, while keeping the added procedure reusable and controllable. However, high- quality skills are still largely written by hand. We introduce SKILLGEN, a multi- agent framework that synthesizes a single auditable skill from trajectories generated by a base agent. The output is a human-readable artifact that can be inspected before use. Rather than merely summarizing trajectories, SKILLGENleverages contrastive induction over both successful and failed trajectories to identify reusable success patterns, recurring failure modes, and behaviors that appear in nearby successes but are missing from failures. SKILLGENthen generates candid
