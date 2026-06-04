# Group F Deviation Disclosure Template

Date: 2026-06-04

Scope: Required disclosure format for any reconstructed adapter, inferred split,
route substitution, prompt/config patch, retry behavior, or other difference
from the SkillGen paper's exact executable setup.

## When A Disclosure Is Required

Create a deviation disclosure when any of the following is true:

- A benchmark adapter is written outside the official SkillGen checkout.
- A train/test split is inferred, sampled, regenerated, or reconstructed.
- A public benchmark source is used because SkillGen lacks bundled data.
- A baseline or ablation is reconstructed from paper text rather than an
  official runner/config.
- A model route differs from the paper display name or provider path.
- A command, script, prompt, config, retry policy, worker count, or environment
  variable differs from the paper or README instructions.
- A smoke-scale run is used where the paper claim is full-scale.

## JSON Shape

Deviation disclosures should be machine-readable. Store claim-specific
disclosures in the relevant group directory and, when they affect the current
run, merge them into `artifacts/hardcoding_disclosures.json` or a dedicated
`artifacts/deviation_disclosures.json`.

```json
{
  "schema_version": "0.1",
  "deviation_id": "alfworld_skillgen_adapter_reconstruction",
  "title": "ALFWorld SkillGen adapter reconstructed from canonical ALFWorld data",
  "status": "proposed",
  "deviation_type": "adapter_reconstruction",
  "evidence_class": "canonical_source_reconstruction",
  "claim_ids": [
    "claim_table1_average_gains_all_models",
    "claim_table1_entry_counts",
    "claim_table1_alfworld_scienceworld_patterns",
    "claim_cross_model_transfer"
  ],
  "source_basis": {
    "official_paper_or_code_basis": "SkillGen paper reports ALFWorld IOD/OOD rows; canonical ALFWorld repository provides valid_seen and valid_unseen environments.",
    "source_url": "https://github.com/alfworld/alfworld",
    "source_commit_or_release": "unknown_until_fetched",
    "license": "unknown_until_reviewed",
    "local_source_path": "phase_0/runs/skillgen_phase0_thorough_20260602/code/official/benchmarks/external/alfworld"
  },
  "changed_behavior": [
    "Convert ALFWorld tasks to SkillGen TaskInstance JSON.",
    "Add an environment action loop that maps agent actions to ALFWorld observations.",
    "Map ALFWorld success/failure to SkillGen binary accuracy."
  ],
  "unchanged_behavior": [
    "Use canonical ALFWorld task source.",
    "Preserve valid_seen as IOD and valid_unseen as OOD when approved."
  ],
  "known_risks": [
    "The reconstructed adapter may not match the authors' private execution bridge.",
    "Train/test sampling may differ from the paper if exact task ids are unavailable."
  ],
  "approval_required_before_execution": true,
  "approval_artifact": "artifacts/05_reviews_and_approval/human_command_review.md",
  "raw_log_policy": "Do not overwrite previous logs; write new attempts under a new target/run id.",
  "report_language": "canonical-source reconstruction, not exact reproduction"
}
```

## Markdown Template

Use this human-readable form beside the JSON or inside group deliverables.

```text
# Deviation: <deviation_id>

Status: proposed | approved | executed | rejected
Evidence class: exact_reproduction | official_code_reproduction |
canonical_source_reconstruction | deviation_backed_reconstruction |
smoke_scale_execution

Affected claims:
- <claim_id>

What differs from the paper or official checkout:
- <specific difference>

Official or canonical basis:
- <paper section, README, script, repository, release, or commit>

Why this deviation is needed:
- <missing official artifact or practical execution reason>

Expected impact on validity:
- <how this affects exactness, metrics, comparability, scale, or cost>

Required approval before execution:
- <approval artifact path>

Artifacts to create:
- <contract, command plan, output, parsed result, comparison path>

Report wording:
- <exact phrase that must appear in the final report>
```

## Deviation Type Vocabulary

| Type | Examples |
| --- | --- |
| `adapter_reconstruction` | ALFWorld environment bridge to SkillGen TaskInstance runner. |
| `split_reconstruction` | LiveCodeBench release v6 train/test split inferred from all-instances data. |
| `baseline_adapter_reconstruction` | Trace2Skill/SkillX/EvoSkill/CoEvoSkills converted to single Markdown skill. |
| `ablation_reconstruction` | Figure 3 A1-A5 configs rebuilt from paper text. |
| `model_route_substitution` | Paper display model replaced by current provider route. |
| `execution_patch` | Official code patched for provider fallback or CLI mismatch. |
| `scale_reduction` | Smoke subset or reduced POC run used instead of full paper matrix. |
| `retry_or_concurrency_change` | Worker count, retry count, rate-limit workaround. |

## Severity Labels

Use one severity label per deviation:

| Severity | Meaning |
| --- | --- |
| `low` | Does not affect task set, metric, or claim interpretation. |
| `medium` | May affect exact numeric reproduction but preserves the same validation question. |
| `high` | Reconstructs a missing core benchmark, baseline, split, or ablation behavior. |
| `blocking` | Must be resolved or approved before the claim can leave `not_testable` or `blocked`. |

## Merge Rule

- Every deviation used by execution must appear in the final report's
  limitations or evidence section.
- Group-local deviation notes are valid planning artifacts, but the run package
  must also contain the active deviation list used for status decisions.
- Deviation disclosures do not prove a claim. They only define how to interpret
  the evidence produced by a run.
