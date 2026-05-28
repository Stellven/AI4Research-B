# AI4Research-B Agent Guide

This file captures the current working understanding of AI4Research-B, the report-to-POC part of the larger AI4Research project. It is intended for future agents and contributors working inside this repository.

AI4Research-B is the user's part of the project. It starts after AI4Research-A has produced a source-grounded research report from a topic. Part B consumes that research report, extracts possible POC-worthy solutions, helps a human select a candidate, builds a POC, validates the POC, and validates whether the report-to-POC pipeline itself is reliable, visible, and safe.

## Core Purpose

AI4Research-B converts a reviewed research report into validated implementation evidence.

The central transformation is:

```text
research report -> POC candidates -> selected solution -> POC design -> POC build -> POC validation -> pipeline validation
```

The project should not behave like a single prompt that reads a paper and writes code. It should operate as an inspectable, file-first, multi-agent workflow where every major AI output becomes an artifact, every key transition is testable, and humans can intervene at any point.

## Relationship To AI4Research-A

AI4Research-A owns the earlier topic-to-report workflow:

```text
topic -> scoped brief -> research plan -> sources -> evidence -> claims -> reviewed report
```

AI4Research-B begins with the report bundle produced by Part A. The handoff should be a structured `research_report.md` or equivalent report bundle.

At minimum, the report bundle should include:

- problem statement
- proposed solution or solution candidates
- research claims
- assumptions
- cited evidence
- expected validation direction
- limitations or uncertainty

Part B must not depend on hidden chat context from Part A. If Part B needs a fact, assumption, claim, or citation, it should be present in the report bundle or requested through a human-visible revision gate.

## Design Principles

- Follow SDD: define contracts, interfaces, and acceptance criteria before implementation.
- Keep all major AI outputs visible as files.
- Treat paper analysis, candidate solutions, POC scope, requirements, design, implementation, tests, validation, and review as separate artifacts.
- Gate downstream work on validated artifacts instead of hidden model context.
- Preserve human intervention points at every major transition.
- Run testing agents continuously as the main workflow progresses.
- Preserve agent thought playback as human-readable decision traces, summaries, and rationale notes.
- Do not rely on raw hidden chain-of-thought as a required artifact.
- Apply the V-model locally to individual POC builds.
- Apply the V-model globally to the whole report-to-POC pipeline.
- Treat skill safety as a first-class concern, with explicit review of skills, tools, permissions, side effects, and failure modes.

## Target Pipeline

The target report-to-POC pipeline is:

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

Each run should use a file-first layout:

```text
runs/<run_id>/
  input/
    research_report.md
    report_bundle_manifest.json
  ingest/
    report_parse.json
    report_completeness_check.json
  extraction/
    paper_analysis.md
    solution_candidates.json
    solution_candidates.md
    claim_map.json
    assumption_map.json
    poc_feasibility_review.md
  selection/
    selected_solution.md
    human_selection.md
  poc/
    poc_scope.md
    requirements.md
    design.md
    test_plan.md
    implementation_report.md
    validation_report.md
  code/
    src/
    tests/
    benchmarks/
  integration/
    handoff_contract.md
    pipeline_run_log.jsonl
    failure_modes.md
    integration_review.md
    recovery_plan.md
  pipeline_validation/
    pipeline_requirements.md
    pipeline_design.md
    pipeline_v_model.md
    system_test_results.md
  safety/
    skill_manifest.schema.json
    skill_safety_policy.md
    skill_audit_report.md
    approved_skills.json
    blocked_skills.json
  playback/
    thought_playback.md
    decision_trace.jsonl
  review/
    final_review.md
    human_approval.md
```

## Testing Model

AI4Research-B uses testing at two levels.

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

A successful Part B run should produce more than code. It should produce a validated run package showing:

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
    ingestion/
    extraction/
    selection/
    poc/
    integration/
    pipeline_validation/
    safety/
    playback/
    review/
  docs/
  prompts/
  schemas/
  tests/
  runs/
```

## Current Working Definition

AI4Research-B is a Codex-centered, file-first, multi-agent workflow for converting a reviewed research report into a validated POC and a validated report-to-POC pipeline.

Its defining challenge is not merely generating demo code. It must preserve traceability from paper claims to POC behavior, expose AI outputs and decision summaries, allow human intervention at every major point, run tests continuously, and enforce skill safety before implementation-critical actions.
