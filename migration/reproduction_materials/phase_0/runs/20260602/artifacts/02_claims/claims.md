# Extracted SkillGen Claims

## Selected Claim

- ID: `claim_skillgen_table1_average_gains`
- Type: `paired_intervention_performance`
- Status: `pending_human_review`
- Paper location: Section 4, Table 1, Appendix C.2

SkillGen improves average held-out accuracy for all eight evaluated base LLMs, with reported gains ranging from +3.27 to +10.08 percentage points.

### Evidence Snippet

> enchmarks; full implementation details are in Appendix C. All claims use paired held-out evaluations: after construction is complete, the same task instances are rolled out with and without the generated skill. RQ1 Does SKILLGENimprove base agents across model families and benchmark domains? Before any held-out rollout, each skill and its active/deprecated status is fixed using only the skill- training dataset: the induction subset for trajectory analysis and the construction-time verification subset for refinement and selection. Table 1 reports the no-skill baseline accuracy, the skill-augmented accuracy, and the absolute accuracy change over 80 held-out benchmark–split–model combinations. Table 1 shows three main patterns: (i) SKILLGENimproves average accuracy for all eight base agents, with gains from +3.27 to +10.08 percentage points; (ii) the effect holds across both open-weight 3Here, gabs ∈Z ≥0 is an absolute minimum number of net repairs, and grel ∈[0,1] is a relative minimum as a fraction of the construction-time verification subset. The gate is a simple construction-time safeguard: the absolute term prevents deploying candidates whose gain is negligible in count, the relative term requires the gain to scale with the size of the verification subset, and the final lower bound of1requires a strictly positive construction-time net gain. 6 <!-- page 7 --> Table 1:Main results across open-weight and pro

## Benchmark Contract Summary

- ID: `bench_skillgen_table1_paired_accuracy`
- Baseline: base agent rollout without generated SkillGen skill
- Treatment: same base agent and same task instance with the generated SkillGen skill loaded
- Matching: same held-out task instance identifier and random seed, as described in Appendix C.2
- Metric: `accuracy`
- Reported gain range: `3.27` to `10.08` percentage points
- Reported entry counts: improved `50`, unchanged `25`, regressed `5`, total `80`
