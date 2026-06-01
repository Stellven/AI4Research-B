# AI4Research-B Agent Guide

This file captures the current working understanding of AI4Research-B, the research-validation and report-to-POC part of the larger AI4Research project. It is intended for future agents and contributors working inside this repository.

AI4Research-B is the user's part of the project. It can start from either a research paper with official code or a source-grounded research report from AI4Research-A. Phase 0 validates whether the original research claims can be reproduced from the official code. Later phases consume the validated research evidence or report, extract possible POC-worthy solutions, help a human select a candidate, build a POC, validate the POC, and validate whether the full pipeline is reliable, visible, and safe.

## Core Purpose

AI4Research-B converts research claims into validated implementation evidence.

Phase 0 performs research validation:

```text
research paper/report + official code
  -> extracted claims
  -> official install and benchmark run
  -> benchmark comparison
  -> research validation report
```

Later phases perform report-to-POC conversion:

```text
research report -> POC candidates -> selected solution -> POC design -> POC build -> POC validation -> pipeline validation
```

The project should not behave like a single prompt that reads a paper and writes code. It should operate as an inspectable, file-first, multi-agent workflow where every major AI output becomes an artifact, every key transition is testable, and humans can intervene at any point.

## Relationship To AI4Research-A

AI4Research-A owns the earlier topic-to-report workflow:

```text
topic -> scoped brief -> research plan -> sources -> evidence -> claims -> reviewed report
```

When AI4Research-B starts from AI4Research-A, it begins with the report bundle produced by Part A. The handoff should be a structured `research_report.md` or equivalent report bundle.

At minimum, the report bundle should include:

- problem statement
- proposed solution or solution candidates
- research claims
- assumptions
- cited evidence
- expected validation direction
- limitations or uncertainty

Part B must not depend on hidden chat context from Part A. If Part B needs a fact, assumption, claim, or citation, it should be present in the report bundle or requested through a human-visible revision gate.

When Phase 0 starts directly from a research paper, the paper PDF and official code source become the visible handoff artifacts. Any extracted claim, benchmark target, command, or assumption must be written to files before downstream validation or POC work depends on it.

## Design Principles

- Follow SDD: define contracts, interfaces, and acceptance criteria before implementation.
- Keep all major AI outputs visible as files.
- Treat paper analysis, candidate solutions, POC scope, requirements, design, implementation, tests, validation, and review as separate artifacts.
- For Phase 0, treat official code execution, raw logs, observed benchmark results, and claim comparison as first-class artifacts.
- Gate downstream work on validated artifacts instead of hidden model context.
- Preserve human intervention points at every major transition.
- Run testing agents continuously as the main workflow progresses.
- Preserve agent thought playback as human-readable decision traces, summaries, and rationale notes.
- Do not rely on raw hidden chain-of-thought as a required artifact.
- Run official research code exactly as instructed before modifying, fixing, or reimplementing anything. Any deviation from official instructions must be recorded as a human-visible artifact.
- Apply the V-model locally to individual POC builds.
- Apply the V-model globally to the whole report-to-POC pipeline.
- Treat skill safety as a first-class concern, with explicit review of skills, tools, permissions, side effects, and failure modes.

## Project Phases

### Phase 0

### Phase 1

### Phase 2

### Phase 3

### Phase 4

### Phase 5

## Phase 0: Research Validator Production Guidelines

Phase 0 is a research reproduction and validation workflow. It should be built and operated as a contract-first pipeline, not as a loose collection of autonomous agents.

Phase 0 answers:

```text
Does the paper's official code run as instructed, and do the observed benchmark results match the paper's stated claims?
```

### Phase 0 Inputs

Phase 0 may accept either:

- a research paper PDF, or
- a structured research report.

Phase 0 requires official code:

- an official Git repository,
- a local official source folder,
- a source archive, or
- a code link extracted from the paper or report.

For the current project scope, Phase 0 should only target AI-related papers or AI-related features that include official code. If official code is missing, mark the paper `out_of_scope` or `not_testable` instead of inventing an implementation.

### Phase 0 Workflow

The production Phase 0 workflow is:

```text
Paper/report + official code
  -> Run intake
  -> Research parse
  -> Claim and benchmark extraction
  -> Human claim review
  -> Code intake
  -> Official instruction extraction
  -> Human command review
  -> Environment planning
  -> Install execution
  -> Benchmark planning
  -> Benchmark execution
  -> Result parsing
  -> Claim comparison
  -> Human result review
  -> Research validation report
  -> Optional extended benchmarks
```

Each step must have an input artifact, output artifact, status, and failure path. A future agent should be able to resume from a step by reading files from the run directory, not by depending on chat history.

### Phase 0 Required Artifacts

Use this layout for Phase 0 run evidence:

```text
phase_0/
  runs/<run_id>/
    input/
      paper.pdf
      research_report.md
      input_manifest.json
    artifacts/
      paper_parse.md
      paper_parse.json
      claims.md
      claims.json
      benchmark_claims.json
      human_claim_review.md
      code_manifest.json
      repo_snapshot.md
      official_instructions.md
      command_plan.json
      human_command_review.md
      environment_plan.md
      environment.json
      benchmark_run_plan.md
      raw_benchmark_outputs/
      benchmark_results.json
      benchmark_results.md
      claim_comparison.json
      claim_comparison.md
      human_result_review.md
      research_validation_report.md
      failure_modes.md
    outputs/
      install_stdout.txt
      install_stderr.txt
      benchmark_stdout.txt
      benchmark_stderr.txt
    code/
      official/
    integration/
      pipeline_run_log.jsonl
    playback/
      thought_playback.md
      decision_trace.jsonl
```

Artifacts may be empty or marked unavailable only when the reason is recorded. For example, if benchmark output cannot be parsed, write `benchmark_results.md` explaining why and mark the result `not_testable`; do not silently omit the artifact.

### Phase 0 Status Labels

Use consistent status labels:

- `reproduced`: the observed result matches the paper claim within an accepted tolerance or clearly supports the same conclusion.
- `partially_reproduced`: official code runs and supports part of the claim, but not the full reported result.
- `not_reproduced`: official code runs, but observed results contradict or fall short of the paper claim.
- `not_testable`: required data, model weights, scripts, metrics, or instructions are missing or ambiguous.
- `failed_to_run`: official install or benchmark command failed.
- `blocked`: validation cannot proceed without human input, credentials, hardware, network access, or external resources.
- `out_of_scope`: the paper is not in the target scope or does not include official code.

### Phase 0 Human Gates

Human review is required before trusting or executing critical Phase 0 artifacts:

- Claim review: confirm the extracted claim and benchmark target.
- Command review: inspect official install and benchmark commands before execution.
- Result review: inspect parsed benchmark output and claim comparison.
- Final review: accept, revise, or reject the research validation report.
- Optional benchmark approval: approve any benchmark not used by the original paper.

Human gates must write artifacts such as `human_claim_review.md`, not rely on chat-only approval.

### Phase 0 Execution Rules

- Run official code as instructed first.
- Capture raw stdout, stderr, exit codes, generated files, runtime, and environment metadata.
- Do not patch official code unless a human approves a recorded deviation.
- Do not replace the official benchmark with a new benchmark when the task is original-paper validation.
- Keep original reproduction results separate from optional extended benchmark results.
- Treat failed runs as valid evidence if logs and failure reasons are preserved.
- Mark commands that require network, GPU, large datasets, model weights, API keys, Docker, or external services.
- If a command is risky, expensive, or unclear, stop at a human-visible gate.

### Phase 0 AI Usage

AI may assist with:

- extracting claims from paper text,
- summarizing official README instructions,
- mapping benchmark outputs to paper claims,
- drafting human-readable reports from artifacts.

AI must not be treated as validation evidence. Validation evidence must come from official code, official commands, captured logs, result files, and explicit comparison to the paper claim.

### Phase 0 Optional Extension

Creating new benchmarks is optional and must happen after official reproduction has been attempted. Extended benchmarks answer:

```text
Does the paper's solution remain effective under additional evaluation conditions?
```

Extended benchmark results must not be mixed with the status of original-paper reproduction.

## Target Pipeline

The target Phase 0 research validation pipeline is:

```text
Research Paper Or Research Report
  -> Research Parser
  -> Claim And Benchmark Extractor
  -> Human Claim Review
  -> Official Code Intake
  -> Official Instruction Extractor
  -> Human Command Review
  -> Environment Runner
  -> Benchmark Runner
  -> Result Parser
  -> Claim Comparator
  -> Human Result Review
  -> Research Validation Reporter
  -> Optional Extended Benchmark Generator
```

The target report-to-POC pipeline after Phase 0 is:

```text
Reviewed Research Report
  -> Report Ingestor
  -> Solution Extractor
  -> Claim And Assumption Mapper
  -> POC Candidate Ranker
  -> Human Selection Gate
  -> POC Scope Generator
  -> Requirement Generator
  -> POC Designer
  -> Test Planner
  -> POC Builder
  -> POC Validator
  -> Integration And Hidden-Issue Reviewer
  -> Pipeline-Level V-Model Validator
  -> Skill Safety Checker
  -> Final Review Gate
```

Each step should have a clear input contract, output contract, validation check, and human-inspectable artifact.

## Core Components

### Orchestrator

Owns run creation, step ordering, artifact paths, validation, trace events, human gates, retries, and revision loops. It should keep the workflow resumable and should avoid storing important state only in model context.

### Agent Runtime

Provides a common interface for model-backed, manual, and stubbed agents. The orchestrator should call agents through this abstraction rather than depending directly on one model provider.

### Phase 0 Research Validator

Owns paper/report parsing, claim extraction, official code intake, official instruction extraction, install execution, benchmark execution, result parsing, and claim comparison. It should produce reproducibility evidence before downstream POC design begins.

The validator should be split into clear components:

- Research Parser
- Claim And Benchmark Extractor
- Code Intake
- Instruction Extractor
- Environment Runner
- Benchmark Runner
- Result Parser
- Claim Comparator
- Research Validation Reporter

Each component should communicate through artifacts and schemas rather than hidden model context.

### Report Ingestor

Loads the research report bundle from Part A, checks required sections, and normalizes the report into structured artifacts for downstream agents.

### Solution Extractor

Extracts possible POC-worthy solutions from the paper. It should separate:

- what the paper explicitly proposes
- what the paper only implies
- what assumptions the POC would need
- what evidence supports each candidate
- what is too vague or unsupported to build safely

### Claim And Assumption Mapper

Builds traceability between research claims, assumptions, citations, candidate solutions, and possible validation methods.

### POC Candidate Ranker

Ranks candidate solutions by feasibility, relevance to the paper's central claim, validation value, implementation cost, implementation risk, and required tools or data.

### Human Selection Gate

Lets the human approve, reject, edit, or combine POC candidates before the system proceeds into POC design and implementation.

### POC Scope Generator

Defines the smallest meaningful POC that can validate the selected solution candidate. It should also explicitly define what is out of scope so the build does not expand into an untestable demo.

### Requirement Generator

Converts the selected solution and POC scope into concrete, testable requirements. Requirements should map to acceptance tests.

### POC Designer

Turns requirements into a technical design, including architecture, components, data flow, interfaces, dependencies, risk points, and integration-test expectations.

### Test Planner

Creates test plans before or alongside implementation. It should map requirements to acceptance tests, design to integration tests, and code modules to unit tests.

### POC Builder

Implements the selected candidate as a POC. The POC should be practical enough to test the paper's proposed solution, not merely illustrative.

### POC Validator

Runs tests and benchmarks, compares results against the selected paper claim, and produces a validation report stating whether the POC supports, partially supports, or fails to support the claim.

### Integration And Hidden-Issue Reviewer

Checks whether extraction, selection, design, build, test, and validation actually connect into one usable workflow. It should surface hidden context, ambiguous handoffs, state problems, recovery failures, and human-resume issues.

### Pipeline-Level V-Model Validator

Validates the whole AI4Research-B pipeline as a system. This is separate from validating one generated POC.

System-level V-model mapping:

```text
Pipeline requirements -> pipeline acceptance tests
Pipeline design       -> pipeline integration tests
Pipeline modules      -> module/unit tests
```

This validator answers:

```text
Does the entire research-report-to-validated-POC pipeline work reliably, visibly, safely, and with human intervention?
```

### Skill Safety Checker

Audits skills and tools before implementation-critical use. It checks:

- skill manifest presence and validity
- declared purpose
- input/output contracts
- allowed and forbidden tools
- file, shell, network, Docker, and API permissions
- side effects
- failure modes
- tests or required human approval
- whether an unsafe skill should be blocked

### Thought Playback Summarizer

Writes human-readable summaries of agent decisions, assumptions, revisions, uncertainty, and important reasoning checkpoints. This exists so a human can inspect what happened without depending on hidden model state.

### Review Gate

Returns `accept`, `revise`, or `reject` for major artifacts and final outputs.

## Run Artifacts

Phase 0 runs should use a file-first layout:

```text
phase_0/
  runs/<run_id>/
    input/
      paper.pdf
      research_report.md
      input_manifest.json
    artifacts/
      paper_parse.md
      paper_parse.json
      claims.md
      claims.json
      benchmark_claims.json
      human_claim_review.md
      code_manifest.json
      repo_snapshot.md
      official_instructions.md
      command_plan.json
      human_command_review.md
      environment_plan.md
      environment.json
      benchmark_run_plan.md
      raw_benchmark_outputs/
      benchmark_results.json
      benchmark_results.md
      claim_comparison.json
      claim_comparison.md
      human_result_review.md
      research_validation_report.md
      failure_modes.md
    outputs/
      install_stdout.txt
      install_stderr.txt
      benchmark_stdout.txt
      benchmark_stderr.txt
    code/
      official/
    integration/
      pipeline_run_log.jsonl
    playback/
      thought_playback.md
      decision_trace.jsonl
```

Later report-to-POC runs should preserve the same file-first approach and add phase-specific artifacts, such as `ingest/`, `extraction/`, `selection/`, `poc/`, `pipeline_validation/`, `safety/`, and `review/`, when those phases are implemented.

## Testing Model

AI4Research-B uses testing at three levels.

Phase 0 research reproduction testing:

```text
paper benchmark claim -> official benchmark execution -> observed result comparison
```

This answers whether the original paper's executable evidence supports the paper's reported claim.

Local POC-level V-model testing:

```text
POC requirements -> POC acceptance tests
POC design       -> POC integration tests
POC code         -> POC unit tests
```

This answers whether one generated POC correctly implements the selected paper solution.

Pipeline-level V-model testing:

```text
Pipeline requirements -> pipeline acceptance tests
Pipeline design       -> pipeline integration tests
Pipeline modules      -> module/unit tests
```

This answers whether the full report-to-validated-POC system works reliably and safely.

Testing agents should run continuously as the main workflow progresses. They should validate extraction quality, handoff contracts, POC correctness, integration behavior, pipeline requirements, and safety assumptions.

## Human Intervention

Human intervention should be available at any time. The system should make it natural for a human to:

- inspect Phase 0 extracted claims and benchmark targets
- approve or revise official install and benchmark commands before execution
- inspect Phase 0 raw logs, parsed results, and claim comparison
- inspect extracted solution candidates
- revise a candidate
- approve or reject a selected solution
- edit POC scope
- revise requirements
- approve or redirect design
- inspect generated code and test results
- review validation evidence
- pause or resume after a failed build
- approve skill/tool usage
- accept, revise, or reject final output

Human edits should not break the pipeline. The orchestrator should record edits as artifacts and resume from the appropriate step.

## Thought Playback

Agent thought playback is a core requirement, but it should be implemented as concise, human-readable summaries rather than raw hidden reasoning.

Thought playback should capture:

- what the agent decided
- why the decision was made at a high level
- what evidence or artifact the decision used
- what assumptions were made
- what uncertainty remains
- what alternatives were rejected
- what a human may need to review

Every major step should write or append to `playback/thought_playback.md` and `playback/decision_trace.jsonl`.

## Skill Safety

Skill safety is highly prioritized in Part B because this part may involve code generation, shell commands, file writes, Docker, network calls, external APIs, local benchmarks, and model/tool orchestration.

Phase 0 is especially safety-sensitive because it executes third-party research code. Before running official code, the system should make install commands, benchmark commands, network needs, dataset needs, GPU needs, API-key needs, Docker needs, and expected file writes visible to the human.

Implementation-critical skills should not be used silently. A skill should be considered unsafe or blocked when:

- it has no manifest
- its input/output contract is unclear
- it requests excessive permissions
- it can modify files without clear boundaries
- it can execute shell commands without review
- it can access network/API resources without explicit need
- it has undeclared side effects
- it has no tests and is used in a critical path
- it can hide or suppress failure evidence

Skill safety outputs should be visible to humans before risky steps run.

## Hidden Issues To Watch

Part B is especially vulnerable to handoff and validation failures. Agents should actively look for:

- papers without official code being treated as reproducible
- vague claims being treated as benchmarkable claims
- README commands that differ from paper benchmark claims
- benchmark scripts that run but do not measure the claimed metric
- generated result summaries that do not match raw logs
- failed installs being hidden by later manual fixes
- optional extended benchmarks being confused with original-paper reproduction
- candidate solutions that are too vague for requirements generation
- claims that do not map cleanly to validation criteria
- assumptions that are required for the POC but not stated in the paper
- missing data, tools, baselines, or metrics
- human edits that break downstream assumptions
- schema-valid outputs that fail semantic review
- build steps that require unanticipated tools or skills
- context needed by the build step that exists only in prior chat
- failed builds that do not produce actionable recovery instructions
- validation reports that describe the demo but do not answer the paper claim

## Final Output Standard

A successful Phase 0 run should produce a research validation package showing:

- what paper or report was validated
- what official code was used
- what claim and benchmark were selected
- what official install and benchmark commands were run
- what environment was used
- what raw logs and result files were produced
- whether observed results reproduced, partially reproduced, failed to reproduce, failed to run, or were not testable
- what limitations, missing resources, or deviations remain
- where humans reviewed claims, commands, results, and final conclusions

A successful full Part B run should produce more than code. It should produce a validated run package showing:

- what solution was extracted from the paper
- why that solution was selected
- how the POC was scoped
- what requirements and design governed the build
- what tests were planned and run
- what the POC actually demonstrated
- whether the POC supports the selected paper claim
- what limitations remain
- what skills/tools were used
- whether safety checks passed
- what agent decisions were made along the way
- where humans intervened

## Suggested Repository Structure

```text
AI4Research-B/
  ai4research_b/
    cli.py
    orchestrator.py
    artifacts.py
    validation.py
    runtime.py
    phase0/
    ingestion/
    extraction/
    selection/
    poc/
    integration/
    pipeline_validation/
    safety/
    playback/
    review/
  meeting docs/
  prompts/
  schemas/
  tests/
  phase_0/
    runs/
```

## Current Working Definition

AI4Research-B is a Codex-centered, file-first, contract-first workflow for validating AI research claims and converting validated research evidence into a validated POC and a validated report-to-POC pipeline.

Its defining challenge is not merely generating demo code. It must preserve traceability from paper claims to official code execution, benchmark evidence, POC behavior, AI outputs, decision summaries, human intervention points, tests, and skill safety checks.
