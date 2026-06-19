# Ablation Config Matrix

Config and wrapper matrix for reconstructed SkillGen Figure 3 ablations

Status: `ready_for_reconstructed_ablation_execution`

| Arm | Implementation type | Patch/config path | Key overrides | Rollback |
| --- | --- | --- | --- | --- |
| `Full` | `full_config` | `none` | pipeline.max_refine_rounds=8, verification.gate_enabled=True, generation.include_failure_lessons=True, generation.generate_scripts=paper_target_dependent, generation.generate_references=paper_target_dependent | No rollback needed; this is the reference arm. |
| `A1` | `wrapper_generated_skill` | `artifacts/ablation_configs/A1_icl_k3_demonstration_skill.md` | ablation.mode=icl_k3_demonstration_skill, ablation.demo_k=3, ablation.demo_source=construction_baseline_successes, ablation.demo_seed=42 | Delete the generated demonstration skill and rerun the normal Full generation path. |
| `A2` | `config_only` | `artifacts/ablation_configs/A2_no_refinement.yaml` | pipeline.max_refine_rounds=1 | Restore pipeline.max_refine_rounds to the Full arm value. |
| `A3` | `behavioral_config_or_runner_patch` | `artifacts/ablation_patches/A3_disable_gate.patch` | verification.disable_gate_for_ablation=True, verification.record_results=True, ablation.force_eval_failed_gate_skill=True | Remove the A3 runner override and restore normal deprecated-skill/no-op handling. |
| `A4` | `prompt_patch_preferred` | `artifacts/ablation_patches/A4_no_failure_lessons_prompt.patch` | generation.include_failure_lessons=False, refinement.include_failure_lessons=False | Restore the original generation/refinement prompts and skill post-processing. |
| `A5` | `config_only` | `artifacts/ablation_configs/A5_plain_text_skill.yaml` | generation.generate_scripts=False, generation.generate_references=False | Restore script/reference generation to the Full arm setting. |
