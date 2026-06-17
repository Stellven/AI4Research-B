# AI4Research-B Phase 0 Current Design

Status: current consolidated design
Last updated: 2026-06-10

This document is the canonical Phase 0 design for AI4Research-B. It consolidates the older Phase 0 notes that now live in `logs/`, keeps the useful design intent from the general AI4Research notes, and updates the artifact layout to match the current Phase 0 run structure.

Phase 0 means research validation:

```text
research paper/report + official code
  -> extracted benchmark claim
  -> official install and benchmark execution
  -> observed result
  -> comparison against the paper result
  -> research validation package
```

Phase 0 is not a paper summarizer and not a reimplementation engine. Its job is to produce visible evidence about whether the paper's official code supports the paper's own benchmark claim.

### Workspace Document Rules

- `meeting docs/` contains only the current overall design document and active paper inputs.
- Historical meeting notes, obsolete drafts, and supporting planning documents live in `logs/`.
- Files moved from `meeting docs/` into `logs/` use `mm.dd - summary` naming, keep their original extension when one exists, and keep `summary` to no more than three words.
- Phase 0 run evidence does not live in `meeting docs/` or `logs/`; generated evidence lives under the matching generation-date directory in `phase_0/runs/`.

## 2. Goal And Success Standard

### Problem

Phase 0 answers this question:

```text
Does the paper's official code run as instructed, and do the observed benchmark results match the paper's stated claims?
```

### Success Standard

A Phase 0 run is successful when a human can inspect the run package and answer:

- what paper or report was validated
- what official code was used
- what claim and benchmark were selected
- what install and benchmark commands were run
- what environment and resources were used
- what raw logs and generated result files were produced
- what observed metrics were parsed from real outputs
- whether those metrics match the paper claim
- what failed, changed, or remains uncertain
- where humans approved claims, commands, results, and final conclusions

The final status must be one of:

- `reproduced`
- `partially_reproduced`
- `not_reproduced`
- `not_testable`
- `failed_to_run`
- `blocked`
- `out_of_scope`

The success criterion is not "the code ran." The success criterion is "the evidence package supports the conclusion."

### Main Workflow

The user provides a paper PDF or structured research report plus official code. Phase 0 creates a run package, extracts a benchmarkable claim, extracts official commands, waits for human approval before risky execution, runs official code, captures evidence, compares results with the paper, and writes a validation report.

## 4. Scope And Non-Goals

### In Scope

- AI-related papers or reports with official code.
- Official install and official benchmark reproduction.
- Paper-claim extraction and benchmark-contract creation.
- Human gates before trusting claims, running risky commands, interpreting results, and accepting final conclusions.
- Smoke validation when full reproduction is too expensive, as long as it is clearly labeled.
- Optional extended benchmarks after official reproduction has been attempted.

### Out Of Scope For Phase 0

- Papers without official code, unless marked `out_of_scope` or `not_testable`.
- New implementation of the paper's method as a substitute for official code.
- Treating an AI-written summary as validation evidence.
- Calling a smoke test full reproduction.
- Mixing optional extended benchmark results with original-paper reproduction status.
- Building the downstream POC. That begins after Phase 0.

## 5. Inputs, Outputs, Boundary Conditions, And Error Handling

### Inputs

At least one research source:

- `paper.pdf`
- `research_report.md`

At least one official code source:

- official Git repository URL
- local official source folder
- source archive
- code URL extracted from the paper/report

Optional inputs:

- commit hash or release tag
- dataset path
- model weight path
- API key availability
- hardware constraints
- runtime budget
- maximum cost budget
- approved command/resource policy

### Outputs

The primary output is a date-split Phase 0 evidence package under:

```text
phase_0/runs/<yyyymmdd>/
```

The directory name is the local generation date using `yyyymmdd`, for example `20260610`. Generated artifacts from different dates must write to different date directories under `phase_0/runs/`; evidence from separate dates must not be mixed in one folder.

The final human-readable output is:

```text
phase_0/runs/<yyyymmdd>/artifacts/00_run_summary/research_validation_report.md
```

Use the date on which the report version was generated or updated. If the same paper is worked on across multiple days, the evidence package is spread across multiple date directories.

### Boundary Conditions

- No paper/report: block; the run cannot start.
- No official code: mark `out_of_scope` or `not_testable`.
- Paper cannot be parsed: write failure evidence and mark `not_testable`.
- Claim is too vague to benchmark: block at claim review or mark `not_testable`.
- Official commands require network, GPU, API key, Docker, large downloads, paid APIs, or unclear file writes: block for human command review.
- Install fails: preserve stdout/stderr/exit code/runtime and mark `failed_to_run` or `blocked`.
- Benchmark fails: preserve logs and mark `failed_to_run` or `blocked`.
- Benchmark runs but no metric can be parsed: mark `not_testable`.
- Result uses a different metric, dataset, split, config, or aggregation: record mismatch and avoid overclaiming reproduction.
- Full benchmark is too expensive: allow a clearly labeled smoke validation, but do not call it full reproduction.
- Optional benchmark requested before official reproduction: block or move it to an extension stage.

### Bad Input Handling

- Missing file: block and state what is missing.
- Unsupported file type: request `paper.pdf` or `research_report.md`.
- Invalid JSON artifact: block the next dependent step.
- Ambiguous code source: block until official source is clarified.
- Non-AI paper or no runnable implementation: mark `out_of_scope`.

Boundary conditions are broader than CS edge cases. They include missing resources, ambiguous claims, unsafe commands, cost limits, and any situation where the system must stop instead of pretending it reproduced the paper.

## 6. Core Flow

```text
paper/report + official code
  -> run intake
  -> research parse
  -> claim and benchmark extraction
  -> human claim review
  -> official code intake
  -> official instruction extraction
  -> human command review
  -> environment planning
  -> install execution
  -> benchmark planning
  -> benchmark execution
  -> result parsing
  -> claim comparison
  -> human result review
  -> research validation report
  -> optional extended benchmarks
```

### Step Responsibilities

1. Run intake creates the run folder, copies or references inputs, and writes `input_manifest.json`.
2. Research parse extracts paper/report text, tables, source locations, code links, and claim candidates.
3. Claim and benchmark extraction identifies benchmarkable claims: claim text, dataset, split, metric, paper value, unit, aggregation, and paper location.
4. Human claim review approves, edits, or rejects the selected validation target.
5. Code intake obtains official code and records source URL, branch, commit, timestamp, README files, scripts, configs, and environment files.
6. Official instruction extraction reads README/docs/scripts/appendix and writes official install/evaluation commands.
7. Human command review inspects resource risks before third-party code runs.
8. Environment planning records package manager, venv/Docker needs, dependencies, hardware, network, API, and file-write expectations.
9. Install execution runs approved install commands and captures logs.
10. Benchmark planning turns selected claims and official instructions into executable benchmark commands.
11. Benchmark execution runs approved commands and captures stdout, stderr, exit code, runtime, and generated files.
12. Result parsing extracts observed metrics from result files first and logs second.
13. Claim comparison compares observed metrics with paper metrics using the same metric, dataset, split, config, and aggregation where possible.
14. Human result review checks parsed metrics and conclusion before final reporting.
15. Research validation report writes the final evidence-backed conclusion.
16. Optional extended benchmarks run only after official reproduction has been attempted and must be labeled separately.


## 8. Core Schemas And Contracts

All module boundaries should be file-backed. The downstream component consumes artifacts, not hidden chat memory.

### Required Schema Families

- `InputManifest`
- `PaperParse`
- `Claim`
- `BenchmarkClaim`
- `PairedBenchmarkClaim`
- `CodeManifest`
- `OfficialInstructions`
- `CommandPlan`
- `ApprovalPolicy`
- `EnvironmentReport`
- `BenchmarkRunPlan`
- `BenchmarkResult`
- `ClaimComparison`
- `GateResult`
- `RunEvent`
- `DecisionTraceEvent`

### Standard Metric Comparison

Use the paper's original metric for comparison. If the paper reports accuracy, compare accuracy. If the paper reports F1, compare F1. If it reports pass@k, reward, exact match, success rate, or another metric, use that metric.

Standard deviation is supporting evidence only when the paper reports it or Phase 0 runs multiple trials. It does not replace the paper's primary metric.

Example:

```json
{
  "metric": "accuracy",
  "unit": "percent",
  "paper_reported_value": 91.2,
  "observed_value": 90.8,
  "difference": -0.4,
  "dataset": "Dataset X",
  "split": "test",
  "aggregation": "simple_mean_across_tasks",
  "status": "partially_reproduced"
}
```

### Same Split, Same Metric, Same Aggregation Checks

These checks are separate because a run can pass one and fail another.

- Same split check: the observed result used the same dataset split as the paper, such as test vs validation vs held-out.
- Same metric check: the observed result used the same metric definition as the paper, such as accuracy vs macro-F1.
- Same aggregation check: the observed result combined per-example, per-task, per-benchmark, or per-model results the same way as the paper.

If any check fails, Phase 0 records the mismatch and avoids claiming exact reproduction.

### Long Inference Approval

`approval.json` includes:

```json
{
  "long_inference_approved": false
}
```

The default is `false`. When it is false or missing, a run should write only the core Phase 0 evidence artifacts needed for selected-claim validation:

- input manifest
- paper parse
- selected claims and benchmark claims
- code manifest and repository snapshot
- official instructions
- command plan and human review/approval files
- environment plan/report
- verification contract and benchmark run plan
- raw stdout/stderr logs
- benchmark results
- claim comparison
- failure modes and final validation report
- pipeline log and thought playback

When `long_inference_approved` is true, the runner may generate the full expanded artifact set used before, including all-claim catalogs, all-claim verification matrices, external-source intake plans/statuses, canonical benchmark source status, model-route mapping, benchmark execution plans, transfer-runner plans, token-log plans, generated configs, and other long-planning artifacts.

This flag exists to keep ordinary runs fast and readable while preserving a deliberate opt-in path for exhaustive analysis.

### Paired Intervention Contract

Some AI-agent papers, including SkillGen, make intervention claims:

```text
same task instances, same base agent, no method vs with method
```

Phase 0 must support paired contracts in addition to scalar metric checks.

Suggested `paired_benchmark_claim.json`:

```json
{
  "schema_version": "0.1",
  "claim_id": "claim_skillgen_main_001",
  "claim_type": "paired_intervention",
  "baseline_condition": "base agent without generated skill",
  "treatment_condition": "same base agent with generated skill",
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

Suggested `contingency_table.json`:

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

## 9. Module Responsibilities

### CLI

Owns user-facing commands and entry points. It does not decide scientific validity.

### Orchestrator

Owns step ordering, artifact checks, event logging, human gates, retries, resume behavior, and revision loops. It does not parse PDFs or run benchmarks directly.

### Artifact Store

Owns run paths, JSON/Markdown/TXT/JSONL writes, artifact reads, symlinks, and overwrite rules. It does not interpret claims.

### Research Parser

Extracts paper/report text, title, source sections, tables, code links, and candidate claim locations. It does not judge whether claims are true.

### Claim Extractor

Extracts benchmarkable claims and supports scalar and paired-intervention claims. It does not execute code.

### Benchmark Contract Writer

Converts a selected claim into an editable benchmark contract. It records metric, dataset, split, config, aggregation, tolerance, paper location, and expected comparison logic.

### Code Intake

Obtains official code and records provenance. It does not patch or fix the code unless a recorded human-approved deviation exists.

### Instruction Extractor

Extracts official install and benchmark commands from official sources. It does not approve execution.

### Environment Runner

Runs approved install commands and captures logs. It does not hide or silently fix failed installs.

### Benchmark Runner

Runs approved benchmark commands and captures logs and output files. It does not decide reproduction status.

### Result Parser

Extracts observed metrics from result files and logs. It does not guess missing numbers.

### Claim Comparator

Compares paper values and observed values, records mismatches, and assigns status. It does not invent evidence.

### Research Validation Reporter

Writes the final human-readable report from artifacts. It does not change underlying evidence.

### Skill Safety Checker

Audits skills/tools used in implementation-critical paths. It checks manifest validity, permissions, side effects, file/network/API/Docker access, and whether unsafe usage needs human approval.

### Thought Playback Summarizer

Writes concise human-readable decision summaries and machine-readable decision trace events. It does not expose hidden chain-of-thought.

## 10. Interface Contracts And Rejection Rights

Any module may reject upstream output when:

- required artifact is missing
- JSON does not match schema
- required field is missing
- selected claim is not benchmarkable
- official command source is not recorded
- resource risks are unknown before execution
- benchmark result cannot map to the claim
- observed metric/dataset/split/config/aggregation does not match the paper and no limitation is recorded
- final report conclusion is unsupported by artifacts

Examples:

- `ResearchParser` writes `01_research_parse/paper_parse.json`.
- `ClaimExtractor` consumes `paper_parse.json` and writes `02_claims/claims.json` and `02_claims/benchmark_claims.json`.
- `CodeIntake` writes `03_code_and_sources/code_manifest.json`.
- `InstructionExtractor` consumes code artifacts and writes `04_commands_and_environment/command_plan.json`.
- `BenchmarkRunner` consumes `command_plan.json` and writes logs plus `08_results/raw_benchmark_outputs/`.
- `ResultParser` consumes raw outputs and writes `08_results/benchmark_results.json`.
- `ClaimComparator` consumes benchmark claims and benchmark results, then writes `08_results/claim_comparison.json`.

## 11. Technology Stack

### MVP Stack

- Language: Python 3.12
- CLI: Typer
- Schemas: Pydantic
- Tests: unittest already exists; pytest is acceptable as the test suite grows
- PDF parsing: PyMuPDF first, pdfplumber fallback
- Code intake: Git CLI, local copy, or archive unpack
- Command execution: Python subprocess with explicit cwd, stdout/stderr capture, exit code, runtime, and timeout
- Artifacts: JSON for structured data, Markdown for human review, JSONL for run/decision events, TXT for raw logs
- Environment isolation: project-local venv for MVP; Docker later when stronger isolation is needed
- Database: not needed for MVP; filesystem is the durable artifact store
- Renderer/UI: not needed for MVP; Markdown artifacts are enough for inspection

### AI Usage

AI may assist with:

- claim extraction
- paper/report summarization
- official instruction summarization
- mapping raw outputs to claim contracts
- report drafting

AI must not be treated as validation evidence. Evidence comes from official code, official commands, captured logs, generated result files, environment metadata, and explicit comparison to the paper claim.

## 12. Human Gates And Quality Gates

Quality should be light but effective.

### Light Checks

Run after ordinary artifact-writing steps:

- artifact exists
- JSON parses
- schema is valid
- required fields are present
- status labels are valid
- referenced files exist where expected

### Formal Gates

Use formal gates only before trusting, executing, or concluding something important.

#### Claim Selection Gate

Before using an extracted claim as the validation target:

- claim is benchmarkable
- benchmark/dataset is known
- metric is known
- reported value exists or absence is justified
- paper location is recorded
- `human_claim_review.md` exists

#### Command Execution Gate

Before running third-party code:

- install and benchmark commands are copied from or derived from official sources
- `command_plan.json` records commands and cwd
- network/GPU/API key/Docker/large download/paid API/file-write risks are explicit
- approval policy exists in `00_run_summary/approval.json`
- `long_inference_approved` is explicitly reviewed if the run will generate the full expanded artifact set
- `human_command_review.md` exists
- high-risk commands are not run silently

#### Result Interpretation Gate

Before declaring `reproduced`, `partially_reproduced`, or `not_reproduced`:

- observed metric exists
- same metric/split/aggregation checks are recorded
- mismatches are recorded
- raw logs or result files support the parsed result
- smoke validation is labeled if the run is reduced

#### Final Report Gate

Before accepting the validation package:

- final status is supported by artifacts
- report points to raw logs and parsed results
- limitations are stated
- official reproduction is separated from optional extended benchmarks
- human result review exists

### Gate Outcomes

- `pass`: continue
- `warn`: continue but record limitation
- `block`: stop until fixed or reviewed

## 13. Failure Modes And Responses

| Failure area | Examples | Response |
| --- | --- | --- |
| Intake | missing paper/report, missing code, unsupported input type, inaccessible URL | block, or mark `out_of_scope` / `not_testable` |
| Parsing | unreadable PDF, incomplete extraction, missing report sections | write failure artifact; request human-supplied report or mark `not_testable` |
| Claim extraction | no benchmarkable claim, missing reported value, ambiguous metric/dataset/split | block at claim review or mark `not_testable` |
| Command planning | README lacks install/eval command, command source unclear, resource risks unknown | block for command review |
| Install execution | nonzero exit, dependency conflict, timeout, disk/memory exhaustion | preserve logs; mark `failed_to_run` or `blocked` |
| Benchmark execution | nonzero exit, timeout, API/provider failure, benchmark skipped evaluation | preserve logs; mark `failed_to_run`, `blocked`, or `not_testable` |
| Result parsing | no metric, unknown output format, metric mismatch | mark `not_testable`, `partially_reproduced`, or `not_reproduced` with evidence |
| Reporting | conclusion unsupported, optional benchmark mixed with official reproduction | block final report gate |
| Safety | command writes outside run, global install, paid API without approval, unbounded downloads | block or require human approval |

Failed runs are valid evidence when logs and failure reasons are preserved.

## 14. Testing Strategy

### Unit Tests

Cover:

- artifact path generation
- schema validation
- status label validation
- command plan validation
- approval policy parsing
- result parser behavior
- claim comparison logic
- gate result logic
- paired-intervention repairs/regressions/net-gain calculation

### Integration Tests

Use a fake run folder:

- parse a fake `research_report.md`
- extract one fake benchmark claim
- copy a fake official code repo
- run a tiny deterministic benchmark script
- capture logs
- parse result
- compare result
- write report

### End-To-End Fixture

Recommended fixture:

```text
tests/fixtures/phase0_fake_paper/
  research_report.md
  official_code/
    README.md
    requirements.txt
    benchmark.py
    expected_results.json
```

The first real test should not be a large research paper. The fake fixture should prove the pipeline before expensive official-code runs.

### Human Review Coverage

Humans cover:

- claim selection
- command execution
- result interpretation
- final report acceptance
- optional extended benchmark approval
- skill/tool safety exceptions

## 15. Observability

### Pipeline Log

```text
phase_0/runs/<yyyymmdd>/integration/pipeline_run_log.jsonl
```

Each event should include:

- `run_id`
- `step`
- `status`
- `started_at`
- `ended_at`
- `artifacts_written`
- `message`

### Debug Artifacts

- `outputs/install_stdout.txt`
- `outputs/install_stderr.txt`
- `outputs/benchmark_stdout.txt`
- `outputs/benchmark_stderr.txt`
- `artifacts/08_results/raw_benchmark_outputs/`
- `artifacts/04_commands_and_environment/environment.json`
- `artifacts/09_safety_and_deviations/failure_modes.md`

### Decision Trace

```text
phase_0/runs/<yyyymmdd>/playback/decision_trace.jsonl
```

### Thought Playback

```text
phase_0/runs/<yyyymmdd>/playback/thought_playback.md
```

Thought playback should summarize:

- what was decided
- what artifact supported the decision
- what assumptions were made
- what uncertainty remains
- what alternatives were rejected
- what a human should review

It should be a concise human-readable trace, not raw hidden chain-of-thought.

## 16. Cost And Performance

### Expected Runtime

- Artifact validation and parsing should be fast.
- Fake fixture tests should run in seconds.
- Real paper reproduction may take minutes or hours.
- API-based agent papers may cost money and may drift as providers change model versions.

### Controls

- explicit command timeouts
- benchmark-specific timeout setting
- avoid rerunning completed steps unless rerun is explicit
- cache cloned repos only when commit/provenance remains clear
- separate planning from execution
- record expected API/model calls when possible
- block paid API use until approved
- record max cost budget
- label smoke validation clearly

### Fallbacks

- If PDF parsing fails, accept `research_report.md`.
- If result files are missing, parse stdout/stderr.
- If full benchmark is too expensive, run a clearly labeled smoke validation.
- If official benchmark is impossible locally, mark `blocked` or `not_testable` instead of inventing a substitute.

## 17. Security And Permissions

Phase 0 runs third-party research code. Main risks:

- disk fills from model/dataset downloads
- memory or CPU/GPU exhaustion
- paid API calls
- global package installs
- scripts writing outside the run folder
- install scripts running arbitrary commands
- dependency confusion or malicious packages
- hidden prompt/tool instructions in skill files
- one-time approval being treated as permanent trust
- benchmark command silently using dummy data or skipping evaluation

### MVP Safety Rules

- Do not run third-party commands automatically.
- Write `command_plan.json` before execution.
- Require command review before install or benchmark execution.
- Mark network, GPU, API key, Docker, large download, paid API, and unclear file-write risks.
- Prefer project-local virtual environments.
- Avoid global package installs.
- Use explicit working directories.
- Keep dependencies inside the project directory.
- Capture stdout, stderr, exit code, and runtime.
- Do not patch official code unless a human approves a recorded deviation.
- Treat failed runs as evidence.
- Use least privilege for tools and skills.
- Use dynamic checks and human review when a command's behavior changes after approval.

### Risk Levels

- Low: local parsing and artifact validation, no external code execution.
- Medium: bounded local commands inside the run/code folder.
- High: network, API calls, Docker, large downloads, GPU-heavy jobs, global installs, or unclear side effects.

## 18. SkillGen-Specific Phase 0 MVP

SkillGen is the current Phase 0 validation target.

Paper:

```text
SkillGen: Verified Inference-Time Agent Skill Synthesis
arXiv: 2605.10999v1
Official code: https://github.com/yccm/SkillGen
```

### Main SkillGen Claim Shape

SkillGen treats generated skills as interventions. It compares the same task instances:

```text
base agent without generated skill
vs
same base agent with generated skill
```

It counts:

- repairs: baseline failed, skill succeeds
- regressions: baseline succeeded, skill fails
- net gain: repairs minus regressions

The paper reports:

- average held-out accuracy improves for all eight main evaluated base LLMs
- average gains range from `+3.27` to `+10.08` percentage points
- across 80 held-out benchmark-split-model entries, 50 improve, 25 are unchanged, and 5 regress
- accepted skills can still regress on some held-out instances, so the verification gate reduces harm but does not eliminate it

### MVP Target

Do not attempt all SkillGen results first. Validate one official SkillGen claim on one benchmark, one base model, and one split using official code and official instructions.

If a full benchmark is too expensive, run a small official or clearly labeled smoke validation. A smoke validation can prove the code path and paired comparison logic, but it cannot be reported as full paper reproduction.

### SkillGen MVP Flow

1. Intake SkillGen PDF and official code URL.
2. Extract main interventional claim and one concrete table claim.
3. Create a paired benchmark contract.
4. Copy official code into `phase_0/runs/<intake_yyyymmdd>/code/official/`.
5. Extract official setup/evaluation commands.
6. Stop for command review because API/network costs are likely.
7. Run baseline condition and save raw logs.
8. Run treatment condition and save raw logs.
9. Parse per-instance outcomes if available.
10. Compute repairs, regressions, net gain, accuracy delta, and status.
11. Write a verdict separating exact table reproduction, smoke validation, blocked/not-testable conditions, and optional extended benchmarks.

## 19. Current Implementation Baseline

Current SkillGen Phase 0 evidence is split by generation date:

```text
phase_0/runs/20260602/
phase_0/runs/20260603/
phase_0/runs/20260604/
phase_0/runs/20260605/
phase_0/runs/20260606/
phase_0/runs/20260607/
phase_0/runs/20260610/
```

Important current state:

- generated evidence has been split into generation-date directories
- `phase_0/runs/20260602/input/` keeps the original SkillGen paper input and intake manifest
- `phase_0/runs/20260602/code/official/` keeps the runnable official-code checkout
- generated artifacts have been reorganized into the numbered directory layout above
- `approval.json` is now a run-summary artifact under `00_run_summary/`
- `approval.json` contains `long_inference_approved`, defaulting to `false`; false means minimal necessary artifacts, true means the previous full expanded artifact set
- compatibility symlinks are retained only when they resolve inside the same date directory
- raw benchmark outputs are under `08_results/raw_benchmark_outputs/`
- generated configs and smoke data are under `07_configs_and_inputs/`
- source code checkout/cache under `code/` is local and not committed because it is large and contains official checkout/env/cache state
- current unit tests cover the SkillGen demo and automation paths

## 20. MVP Implementation Shape

The first production-quality version should remain simple:

- file-first
- local filesystem artifacts
- Python CLI
- Pydantic schemas
- lightweight artifact checks
- four formal gates
- fake fixture end-to-end test
- no database
- no full UI
- no automatic risky command execution

The design principle is:

```text
strict about evidence, lightweight in process
```

Do not put a heavy formal review after every step. Use cheap automatic checks after artifact-writing steps, and reserve formal gates for:

- choosing the claim
- running third-party code
- interpreting results
- accepting the final report

## 21. Historical Document Archive

`meeting docs/` now keeps only:

- `phase_0_current_design.md`
- `SkillGen.pdf`

Historical notes and superseded planning files have been moved to `logs/` with normalized names:

- `logs/05.12 - project overview.md`
- `logs/05.13 - skills.md`
- `logs/05.14 - analysis.docx`
- `logs/05.14 - brief analysis.docx`
- `logs/05.19 - ai4research flow.md`
- `logs/05.21 - meeting notes.md`
- `logs/05.28 - phase build plan.pptx`
- `logs/05.29 - ai4research workflow.md`
- `logs/05.29 - skillgen claims.md`
- `logs/05.29 - stuff learnt.md`
- `logs/06.01 - lisihao presentation.txt`
- `logs/06.02 - meeting docs`

Some already-consolidated obsolete drafts were removed before this archive cleanup: `preliminary design.md`, `Design.docx`, and `temp.md`.

`meeting docs/SkillGen.pdf` remains because it is the research paper input, not an obsolete design note.
