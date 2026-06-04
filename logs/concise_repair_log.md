## Group A - ALFWorld Adapter

- Issue addressed: `alfworld_iod` and `alfworld_ood` were blocked for full matrix execution because SkillGen lacked ALFWorld-compatible train/test JSON, adapter code, provenance, deviation labeling, and smoke evidence.
- Approach: downloaded canonical ALFWorld data into the run directory, generated seed-42 SkillGen-compatible IOD/OOD train/test JSON, added reconstructed offline-plan adapter/grader scripts, wrote split manifest/deviation/run-command artifacts, and created a C-group handoff checklist with trace retention requirements.
- Result: structural adapter package is complete for reconstructed execution handoff. Further action is required before claim reproduction: C group must create per-model configs, get human execution approval, run full train/eval commands, preserve traces, and report results with the reconstructed deviation label.

## Group F - Report Integration / Cost Governance

- Issue addressed: full-matrix execution has high and uneven cost/time risk; one reconstructed low-cost entry used 557,877 tokens, so blind 80-entry execution needs governance without changing paper-defined validation standards.
- Approach: wrote budget gate, stop-condition, metadata-retention, deviation-disclosure, per-entry cost-report, and final-report wording artifacts; mirrored policy/template files into the run package.
- Result: governance/reporting issue is solved at the policy layer. Further action is required from C group to implement runner-side enforcement, fill per-entry cost reports, and keep every partial run labeled incomplete.

## Group D - Baseline Source Identity

- Issue addressed: `claim_baseline_generator_comparison` was stuck as `not_testable` because the SkillGen checkout lacks executable Trace2Skill, SkillX, EvoSkill, and CoEvoSkills comparison runners.
- Approach: added public-code baseline source identity review artifacts, a single-Markdown-skill adapter contract, deviation disclosure, automation support, and tests so the claim now has a visible reconstructed-comparison path.
- Result: partially solved. The claim now advances to `blocked_pending_baseline_source_identity_review`; further action is required to clone/pin repos, review licenses and identities, approve the adapter contract, then execute the reconstructed comparison.

## Group B - LiveCodeBench Split

- Issue addressed: LiveCodeBench had only `release_v6_all.json`, so Table 1 claims stayed blocked by a missing train/test split contract.
- Approach: Added a deterministic paper-matching inferred split using release v6, `test_release_v6`, construction `n=50`, test `n=150`, seed `42`; wrote split data, manifest, source review, split contract, and deviation note.
- Result: Group B issue is solved for execution readiness. LiveCodeBench is now `ready_for_execution`; further action is still required to execute the benchmark and to resolve remaining non-Group-B blockers, especially ALFWorld IOD/OOD.

## Group E - Reconstructed Ablation

- Issue addressed: `claim_ablation_full_wins` was stuck as `not_testable` because the SkillGen checkout lacks author-provided Figure 3 A1-A5 ablation runner/configs.
- Approach: defined a deviation-backed reconstructed ablation path for Full, A1 ICL k=3, A2 no refinement, A3 no verification gate, A4 no Failure Lessons, and A5 plain-text skill; wrote contract, config matrix, smoke plan, deviation note, automation support, and tests.
- Result: partially solved. The claim now advances to `ready_for_reconstructed_ablation_execution`; further action is required for human review/approval, smoke execution, and later paper-target Figure 3 matrix execution. It is not exact reproduction unless original author configs are found.

## Group C - Full Matrix Execution Runner

- Issue addressed: full matrix execution was still blocked by pre-execution human-gate language and the runner needed a resumable per-entry execution contract with evidence validation.
- Approach: added full-matrix authorization artifacts, updated execution plans/contracts to remove pre-execution human approval blockers, implemented OpenAI-first runner controls/statuses, per-entry config generation, direct OpenAI fallback, deviation labels, and post-run evidence checks.
- Result: preparation issue is solved. ALFWorld IOD/OOD OpenAI routes are runner-attemptable as reconstructed evidence; full 80-entry reproduction still requires actual execution, post-run evidence validation, and technically working non-OpenAI provider routes.

## Manager - Cross-Group Consolidation

| Issue addressed | Approach | Result |
| --- | --- | --- |
| Claim verdict status and execution readiness status were being conflated across the original seven problem claims. | Split reporting semantics into `claim_verdict_status` and `execution_readiness_status`, keeping legacy `status` only as the verdict alias. | Solved as a reporting contract; further action is required whenever agents update claim matrices, because readiness must not be promoted into reproduction evidence. |
| The original Table 1 claims require an 80-entry aggregate, but the overnight run produced only one full-matrix entry. | Added observed-entry artifacts and report addenda that separate single-entry evidence from aggregate Table 1 claims. | Solved for evidence accounting; further action is required to execute and aggregate the full 80-entry matrix. |
| The completed `mcp_bench_single::openai/gpt-5.4-nano` entry was negative evidence, not partial reproduction. | Recorded construction failure, deprecated skill status, held-out `delta_acc=0.0`, and entry verdict `not_reproduced`. | Solved for that entry; aggregate claims remain blocked, and future negative entries should be accepted as valid evidence without forced promotion. |
| OpenRouter 402 and non-OpenAI model execution were not cleanly separated from benchmark failure. | Added provider resolution artifacts and runner status handling: OpenAI routes use direct OpenAI fallback, while non-OpenAI routes become `provider_unavailable` when OpenRouter 402 evidence is present. | Partially solved. OpenAI entries are executable; non-OpenAI entries require repaired OpenRouter billing/key or reviewed direct-provider integrations. |
| Model substitution risk: replacing non-OpenAI paper models with OpenAI models would change the Table 1 reproduction target. | Recorded policy that substitute-model runs are extension/deviation experiments only, not paper-model reproduction. | Solved as a policy guard; further action is required only if a future agent proposes substitute models. |
| Official `main.py --resume` could not reuse a failed run that had trajectories but no `checkpoint.json`. | Preserved failed and resume logs, then reran the entry fresh through direct OpenAI fallback. | Not solved in official behavior. Further action would require a deviation-backed checkpoint converter or induction-resume wrapper. |
| Figure 7 / refinement claim needs complete per-round traces, not only final eval summaries. | Added trace-retention requirements and runner evidence checks for verification baseline/with-skill JSONL, summaries, case analyses, candidate skill artifacts, token logs, and held-out trajectories. | Partially solved. The contract exists; actual Figure 7 verification still requires full representative runs with those traces present. |
| Cross-model transfer is separate from Table 1 and needs all 120 off-diagonal comparisons, including ALFWorld OOD. | Kept transfer as its own contract and noted its dependency on ALFWorld OOD execution, evaluator baselines, source-model skills, and provider routes. | Not yet solved by full-matrix preparation alone. Further action is required after ALFWorld OOD and required model routes are executable. |
| Top-level artifacts and categorized mirrors can drift, causing future agents to read stale conclusions. | Updated both report mirrors and used/wrote mirror-aware artifacts for provider resolution. | Partially solved. Future artifact edits must keep top-level and categorized copies synchronized. |
| Existing positive evidence is mostly smoke or reduced POC-scale evidence, not exact paper-scale reproduction. | Preserved partial labels for AIME mechanism, token logging, and auditable skill artifacts while requiring full-scale execution for `reproduced`. | Solved as a labeling rule; further action is required only if exact numeric reproduction is demanded. |
