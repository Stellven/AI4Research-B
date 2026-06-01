# SkillGen Claim Analysis For Phase 0

Source PDF: `/Users/jamesyuan/Desktop/SkillGen.pdf`

Paper: "SkillGen: Verified Inference-Time Agent Skill Synthesis"

arXiv: `2605.10999v1`

Official code link stated in the paper: `https://github.com/yccm/SkillGen`

## Core Claim

The paper's main claim is that inference-time agent skills should be treated as interventions, not just as reusable prompts or summaries.

SkillGen claims to synthesize one auditable skill from baseline agent trajectories, then verify whether that skill has a positive net effect before deployment. The method compares the same task instances with and without the generated skill, counting both:

- repairs: baseline failed, skill succeeds
- regressions: baseline succeeded, skill fails

The selected skill is accepted only if its net gain is positive enough under a construction-time verification gate.

In the paper's notation:

```text
net gain = repairs - regressions
G_m(s) = n_01(s) - n_10(s)
```

This is the most important idea for Phase 0: the paper does not treat "generated skill looks good" as evidence. Evidence comes from paired evaluation against a no-skill baseline.

## What SkillGen Contributes

SkillGen has three stages:

1. Baseline elicitation: run a base agent to collect successful and failed trajectories.
2. Contrastive behavioral induction: compare successes and failures to identify reusable procedures, failure modes, and missing behaviors.
3. Generation-verification-refinement: generate candidate skills, evaluate each candidate on paired verification instances, refine from repairs/regressions/unresolved failures, and select the best verified candidate.

The generated skill has a structured bundle form:

```text
skill = instructions + task metadata + optional scripts + optional references
```

The instruction body is split into:

- task context
- success procedures
- failure-avoidance lessons

This structure maps well to AI4Research-B's skill-safety goal because the output is human-readable, inspectable, and can be marked active or deprecated.

## Main Empirical Claims To Validate

The PDF makes several testable empirical claims:

1. SkillGen improves average held-out accuracy for all eight main evaluated base LLMs.
2. Reported average gains range from `+3.27` to `+10.08` percentage points across those models.
3. Across 80 held-out benchmark-split-model entries, 50 improve, 25 are unchanged, and 5 regress.
4. SkillGen outperforms recent skill-generation baselines in the controlled single-skill setting.
5. Ablations show that contrastive induction, refinement, the verification gate, failure lessons, and script/reference bundles each contribute.
6. Generated skills can transfer across models, but transfer quality depends on the skill-generating model.
7. The verification gate reduces harm by rejecting candidate skills whose construction-time net gain is insufficient.

The strongest Phase 0 target is claim 1 or claim 3 because those are directly tied to tables/logs and can be checked by running paired evaluations.

## Important Limitations In The Paper Claim

The claim is empirical, not a theoretical guarantee. It should be validated as reported benchmark behavior under the paper's implementation.

Phase 0 should preserve these limitations:

- Reproduction may require hosted LLM APIs, OpenRouter routing, API keys, and model versions that may drift over time.
- Some reported models are proprietary API models, so exact provider-side compute is not reproducible locally.
- Benchmarks such as ALFWorld, ScienceWorld, Mind2Web, tau-Bench, and ChemLLMBench may require nontrivial environment setup.
- The paper reports that accepted skills can still regress on held-out instances, so the verification gate is a risk reducer, not a complete safety guarantee.
- The main baseline comparison adapts library-style skill methods into a single-skill interface, so Phase 0 should not overclaim that it validates those systems' full native deployment modes.
- If official scripts, datasets, seeds, prompts, or logs are missing, Phase 0 should mark the claim `not_testable` or `blocked`, not infer missing evidence.

## How This Should Shape Phase 0

Use SkillGen as a design pattern for Phase 0, not as something Phase 0 must reimplement.

Phase 0's job is:

```text
paper claim -> benchmark contract -> official execution -> observed evidence -> verdict
```

SkillGen teaches that many agent papers make interventional claims:

```text
agent without method vs. agent with method on the same instances
```

So Phase 0 should support paired benchmark contracts, not only single scalar metric checks.

## Phase 0 Contract Additions Inspired By SkillGen

Add or support these artifact concepts:

```text
paired_benchmark_claim.json
baseline_results.json
treatment_results.json
contingency_table.json
intervention_verdict.json
```

Suggested `paired_benchmark_claim.json` shape:

```json
{
  "schema_version": "0.1",
  "claim_id": "claim_skillgen_main_001",
  "claim_type": "paired_intervention",
  "baseline_condition": "base agent without generated skill",
  "treatment_condition": "same base agent with SkillGen-generated skill",
  "instance_matching": "same benchmark instances and random seed",
  "metric": "accuracy",
  "reported_baseline_value": null,
  "reported_treatment_value": null,
  "reported_delta": 0.0327,
  "expected_direction": "higher_is_better",
  "repair_regression_required": true,
  "paper_location": "Table 1 and Section 4"
}
```

Suggested `contingency_table.json` shape:

```json
{
  "schema_version": "0.1",
  "claim_id": "claim_skillgen_main_001",
  "n_00": 0,
  "n_01_repairs": 0,
  "n_10_regressions": 0,
  "n_11": 0,
  "net_gain": 0,
  "sample_size": 0,
  "observed_delta": null
}
```

This lets Phase 0 validate the paper's actual causal comparison structure:

```text
same input, same base agent, no skill vs. skill
```

## Recommended Phase 0 MVP Based On This Paper

Do not start by reproducing every SkillGen result. Use the paper to build a small but correct validation slice.

### MVP Goal

Validate one official SkillGen claim on one benchmark, one base model, and one split, using the official repository and official instructions.

A good first target is whichever official script can run cheapest and fastest. If the official code offers a smoke-test or toy split, use that first. If not, use a small public benchmark subset such as PubMedQA or ScienceWorld only after confirming the official commands and required API access.

### MVP Steps

1. Intake the PDF and official code URL.
2. Extract SkillGen's main interventional claim and one concrete table claim.
3. Create a paired benchmark contract.
4. Clone or copy the official SkillGen code into `runs/<run_id>/code/official/`.
5. Extract official setup and evaluation commands from the repo.
6. Stop for human command review, especially because API/network costs are likely.
7. Run the official baseline condition and save raw logs.
8. Run the official skill condition and save raw logs.
9. Parse per-instance outcomes if available.
10. Compute repairs, regressions, net gain, accuracy delta, and status.
11. Write a validation verdict that separates:
    - exact reproduction of a paper table
    - small-sample smoke validation
    - blocked/not-testable conditions

## What To Build First In The Repo

Build these Phase 0 components in order:

1. `ResearchParser`: extracts title, arXiv id, code URL, sections, tables, and claim text from a PDF.
2. `ClaimExtractor`: supports `paired_intervention` claims in addition to normal scalar benchmark claims.
3. `BenchmarkContractWriter`: converts a selected claim into an editable benchmark contract.
4. `CommandPlan`: records official install and run commands plus resource flags.
5. `PairedRunRecorder`: stores baseline and treatment outputs separately.
6. `InterventionComparator`: computes accuracy delta, repairs, regressions, net gain, and verdict.
7. `ReportWriter`: writes a human-readable validation report with links to raw logs and parsed artifacts.

This is the shortest path from the SkillGen paper to a useful Phase 0 system.

## Key Design Rule

Phase 0 should not say "the paper is valid" because an AI summarized it well.

For SkillGen-style papers, Phase 0 should only say:

```text
The official code was run under recorded conditions.
The observed paired comparison was X.
The paper reported Y.
The claim is reproduced, partially reproduced, not reproduced, not testable, failed to run, or blocked.
```

That matches both the SkillGen paper's own verification philosophy and AI4Research-B's artifact-first validation goals.

