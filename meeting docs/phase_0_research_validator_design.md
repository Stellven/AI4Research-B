# Phase 0 Research Validator Design

## Goal

Phase 0 validates whether an AI research paper's claimed results can be reproduced from the official code and official instructions provided by the paper or project repository.

Phase 0 is not a POC generator. It is a research reproduction and validation step that answers:

```text
Does the paper's official code run as instructed, and do the observed benchmark results match the paper's stated claims?
```

The output of Phase 0 is a visible validation package: extracted claims, official run instructions, install logs, benchmark logs, observed results, comparison against the paper, and a final research validation report.

## Scope

### In Scope

- Accept a research paper PDF or a research report.
- Accept only papers that include official code or an official code repository.
- Extract the paper's main claims, solved challenge, benchmark, dataset, metric, and reported result.
- Identify the official install and benchmark instructions.
- Run the official code as instructed before making any modifications.
- Capture installation logs, benchmark logs, raw results, and environment metadata.
- Compare observed benchmark results against the paper's reported claims.
- Produce a final status: reproduced, partially reproduced, not reproduced, not testable, failed to run, or blocked.
- Optionally design and run additional benchmarks after official reproduction is attempted.

### Out of Scope For MVP

- Validating papers without public or included code.
- Rewriting the official implementation to make it work.
- Creating a new POC for the paper's idea.
- Judging whether the paper is theoretically correct beyond its executable evidence.
- Building a full UI.
- Automatically downloading large datasets, model weights, or paid resources without a visible approval gate.
- Treating model-generated opinions as validation evidence without executable results.

## Inputs

Phase 0 accepts one of these research inputs:

- `paper.pdf`: the original research paper.
- `research_report.md`: a structured research report about the paper.

Phase 0 also requires official code:

- Git repository URL.
- Local source folder.
- Source archive.
- Code link extracted from the paper or report.

Optional inputs:

- Known commit hash or release tag.
- Dataset location.
- Model weight location.
- Benchmark command supplied by the user.
- Hardware constraints or expected runtime budget.

## Outputs

Phase 0 produces a run package under:

```text
runs/<run_id>/phase_0/
```

The final output is:

```text
runs/<run_id>/phase_0/research_validation_report.md
```

That report must state:

- What paper or report was validated.
- What official code was used.
- What claim was tested.
- What benchmark was run.
- What result the paper reported.
- What result Phase 0 observed.
- Whether the claim was reproduced.
- What failed, if anything.
- What assumptions, limitations, or missing resources remain.

## Workflow

Phase 0 should be designed as an artifact-first pipeline. Each step reads files, writes files, and records status. AI can help extract or summarize, but the workflow must not depend on hidden chat context.

```text
Paper/report + official code
  -> Intake
  -> Research parse
  -> Claim and benchmark extraction
  -> Human claim review
  -> Code intake
  -> Official instruction extraction
  -> Install plan
  -> Install execution
  -> Benchmark plan
  -> Benchmark execution
  -> Result parsing
  -> Claim comparison
  -> Research validation report
  -> Optional extended benchmarks
```

## Step Table

| Step | Input | Action | Output | Gate |
|---|---|---|---|---|
| 0. Run intake | PDF/report, code source | Create run folder and input manifest | `input_manifest.json` | Fail if no paper/report or no official code |
| 1. Research parse | PDF/report | Extract readable text and structure | `paper_parse.md`, `paper_parse.json` | Fail if unreadable |
| 2. Claim extraction | Parsed text | Extract main claim, solved challenge, benchmark, dataset, metric, reported result | `claims.json`, `benchmark_claims.json`, `claims.md` | Human review required |
| 3. Code intake | Official repo/source | Clone/copy code and record source metadata | `code_manifest.json`, `repo_snapshot.md` | Fail if code cannot be obtained |
| 4. Instruction extraction | Code README, paper appendix, scripts | Identify official install and benchmark commands | `official_instructions.md`, `command_plan.json` | Human review before execution |
| 5. Environment planning | Command plan, repo metadata | Define execution environment and expected dependencies | `environment_plan.md` | Fail if requirements are impossible locally |
| 6. Install execution | Official install commands | Run setup exactly as instructed | `install_stdout.txt`, `install_stderr.txt`, `environment.json` | Continue only if install succeeds |
| 7. Benchmark planning | Official benchmark commands | Define benchmark command, expected outputs, timeout, result parser | `benchmark_run_plan.md` | Human review if command is expensive or risky |
| 8. Benchmark execution | Installed repo, benchmark plan | Run benchmark exactly as instructed | `benchmark_stdout.txt`, `benchmark_stderr.txt`, `raw_benchmark_outputs/` | Continue only if benchmark produces usable output |
| 9. Result parsing | Logs and result files | Extract observed metrics | `benchmark_results.json`, `benchmark_results.md` | Mark not testable if results cannot be parsed |
| 10. Claim comparison | `benchmark_claims.json`, `benchmark_results.json` | Compare observed result to paper claim | `claim_comparison.md`, `claim_comparison.json` | Human review required |
| 11. Final report | All artifacts | Write validation conclusion and evidence summary | `research_validation_report.md` | Final accept/revise/reject |
| 12. Optional extension | Reproduced or partially reproduced result | Design and run additional benchmarks | `extended_benchmark_plan.md`, `extended_benchmark_results.json` | Optional human approval |

## Artifact Layout

```text
runs/<run_id>/
  input/
    paper.pdf
    research_report.md
    input_manifest.json
  phase_0/
    paper_parse.md
    paper_parse.json
    claims.md
    claims.json
    benchmark_claims.json
    code_manifest.json
    repo_snapshot.md
    official_instructions.md
    command_plan.json
    environment_plan.md
    install_stdout.txt
    install_stderr.txt
    environment.json
    benchmark_run_plan.md
    benchmark_stdout.txt
    benchmark_stderr.txt
    raw_benchmark_outputs/
    benchmark_results.json
    benchmark_results.md
    claim_comparison.json
    claim_comparison.md
    research_validation_report.md
    failure_modes.md
  code/
    official/
  playback/
    thought_playback.md
    decision_trace.jsonl
  integration/
    pipeline_run_log.jsonl
```

## Core Data Contracts

### Claim

```json
{
  "id": "claim_001",
  "claim_text": "The method improves accuracy over the baseline on Benchmark X.",
  "claim_type": "performance",
  "paper_location": "Section 4.2",
  "evidence_text": "Reported result table or quoted summary.",
  "requires_benchmark": true,
  "status": "pending_validation"
}
```

### Benchmark Claim

```json
{
  "id": "bench_claim_001",
  "claim_id": "claim_001",
  "benchmark_name": "Benchmark X",
  "dataset": "Dataset Y",
  "metric": "accuracy",
  "reported_value": 0.91,
  "reported_unit": "ratio",
  "comparison_target": "baseline_method",
  "expected_direction": "higher_is_better",
  "tolerance": null,
  "paper_location": "Table 2"
}
```

### Command Plan

```json
{
  "install_commands": [
    "pip install -r requirements.txt"
  ],
  "benchmark_commands": [
    "python run_benchmark.py --dataset DatasetY"
  ],
  "source": "README.md",
  "requires_network": true,
  "requires_gpu": false,
  "requires_dataset_download": true,
  "notes": "Commands are copied from official repository instructions."
}
```

### Validation Status

```json
{
  "claim_id": "claim_001",
  "benchmark_claim_id": "bench_claim_001",
  "observed_value": 0.905,
  "reported_value": 0.91,
  "status": "reproduced",
  "comparison_summary": "Observed result is close to the reported result.",
  "limitations": [
    "Hardware differs from the paper."
  ]
}
```

## Status Labels

Use a small set of status labels so reports are consistent:

- `reproduced`: observed result matches the paper's claim within an accepted tolerance or clearly supports the same conclusion.
- `partially_reproduced`: code runs and supports part of the claim, but not the full reported result.
- `not_reproduced`: code runs, but observed results contradict or fall short of the paper's reported claim.
- `not_testable`: required data, model weights, scripts, or metrics are missing or ambiguous.
- `failed_to_run`: official install or benchmark command failed.
- `blocked`: validation cannot proceed without human input, credentials, hardware, or external resources.
- `out_of_scope`: the paper has no official code or is not an AI-related implementation paper.

## Human Gates

Human review is required at these points:

1. Claim review: confirm the extracted claim and benchmark target are the correct ones to validate.
2. Command review: inspect official install and benchmark commands before execution.
3. Result review: inspect parsed benchmark output and comparison.
4. Final review: accept, revise, or reject the validation report.
5. Optional benchmark approval: approve any new benchmarks beyond the official reproduction attempt.

Human gates should write visible artifacts, not hidden approvals:

```text
phase_0/human_claim_review.md
phase_0/human_command_review.md
phase_0/human_result_review.md
phase_0/human_final_review.md
```

## AI Usage Boundaries

AI should be used for narrow interpretation tasks:

- Extracting claims from paper text.
- Summarizing official README instructions.
- Mapping benchmark results to paper claims.
- Drafting human-readable reports from existing artifacts.

AI should not be the source of truth for validation. The validation evidence must come from:

- Official code.
- Official benchmark commands.
- Captured logs.
- Result files.
- Deterministic comparison against extracted paper claims.

## Failure Handling

Phase 0 should not hide failure. A failed run is still useful if it produces a clear reason and recovery path.

Examples:

- If the paper cannot be parsed, write `failure_modes.md` with the parsing error and request a research report or cleaner PDF.
- If official code is missing, mark the paper `out_of_scope`.
- If the README has no benchmark instructions, mark the claim `not_testable`.
- If install fails, preserve stdout/stderr and mark `failed_to_run`.
- If benchmark runs but produces different numbers, mark `not_reproduced` or `partially_reproduced`.
- If a large dataset, GPU, or API key is required, mark `blocked` until approved or provided.

## Success Criteria

Phase 0 MVP succeeds when:

- It can take one AI paper with official code.
- It extracts at least one concrete benchmark claim.
- It records the official code source and run instructions.
- It runs the official install and benchmark commands.
- It captures logs and observed results.
- It compares observed results to the paper claim.
- It writes a final validation report that a human can inspect without relying on chat context.

## MVP Implementation Plan

Build Phase 0 in this order:

1. Manual artifact template: create the folder layout and required Markdown/JSON files.
2. CLI run creator: create `runs/<run_id>/` and input manifests.
3. Paper/report parser: extract text from PDF or read Markdown report.
4. Claim extractor: produce `claims.json` and `benchmark_claims.json`.
5. Code intake: clone/copy official code and write `code_manifest.json`.
6. Command planner: extract or manually record official commands.
7. Command runner: execute install and benchmark commands while saving logs.
8. Result parser: extract metrics from known output files or logs.
9. Comparator: compare observed metrics to paper claims.
10. Report writer: generate `research_validation_report.md`.

## Optional Extension: New Benchmarks

New benchmarks should be added only after official reproduction has been attempted. The extension should answer a different question:

```text
Does the paper's solution remain effective under additional evaluation conditions?
```

The extension must clearly separate original-paper validation from new evaluation:

```text
phase_0/extended_benchmark_plan.md
phase_0/extended_benchmark_results.json
phase_0/extended_benchmark_report.md
```

The final report should not treat new benchmark results as proof that the original paper's reported benchmark was reproduced.

## Relationship To Later Phases

Phase 0 feeds Phase 1 with validated research evidence:

```text
Phase 0 Research Validation
  -> validated claims
  -> reproduced or failed benchmark evidence
  -> known implementation constraints
  -> known missing resources
  -> confidence level for building a downstream POC
```

If Phase 0 reproduces the paper, Phase 1 can extract POC candidates with stronger confidence. If Phase 0 fails or is not testable, Phase 1 should carry that limitation forward instead of assuming the paper's claims are true.
