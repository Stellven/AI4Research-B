# AI4Research-B Architecture

## Goal

AI4Research-B converts a source-grounded research report into one or more POC candidates, builds a selected POC, validates the result, and then validates the full report-to-POC pipeline as a system.

Part A of the larger AI4Research project produces the research report:

```text
topic -> scoped brief -> research plan -> sources -> evidence -> claims -> reviewed report
```

Part B consumes that report and turns it into validated implementation evidence:

```text
research report -> POC candidates -> selected solution -> POC design -> POC build -> POC validation -> pipeline validation
```

The system should not behave like a single prompt that reads a paper and writes code. It should preserve intermediate artifacts, expose AI outputs, support human intervention at any point, run tests after key steps, and keep skill/tool safety visible.

## Relationship To AI4Research-A

AI4Research-A is responsible for generating a reviewed research report from a user topic. AI4Research-B starts after that report exists.

The handoff artifact from Part A to Part B should be a structured `research_report.md` or equivalent report bundle. At minimum, it should include:

- problem statement
- proposed solution or solution candidates
- claims
- assumptions
- cited evidence
- expected validation direction
- limitations or uncertainty

Part B should not depend on hidden chat context from Part A. If Part B needs something, it should be present in the report bundle or requested through a human-visible revision gate.

## Design Principles

- Follow SDD: define contracts, interfaces, and acceptance criteria before implementation.
- Keep all major AI outputs visible as files.
- Treat paper analysis, candidate solutions, POC scope, requirements, design, implementation, tests, validation, and review as separate artifacts.
- Gate downstream work on validated artifacts instead of hidden model context.
- Preserve human intervention points at every major transition.
- Run testing agents continuously as the main workflow progresses.
- Preserve agent thought playback as human-readable decision traces, summaries, and rationale notes. Do not rely on raw hidden chain-of-thought as a required artifact.
- Apply the V-model locally to the POC in Phase 2.
- Apply the V-model globally to the whole report-to-POC pipeline in Phase 4.
- Treat skill safety as a first-class project concern, with lightweight checks early and a formal checker in Phase 4.

## Target Pipeline

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

## Core Components

### Orchestrator

Owns run creation, step ordering, artifact paths, validation, trace events, human gates, retries, and revision loops.

### Agent Runtime

Provides a common interface for model-backed, manual, and stubbed agents. The orchestrator should call agents through this abstraction rather than depending directly on one model provider.

### Report Ingestor

Loads the research report bundle from Part A, validates that required sections exist, and normalizes it into structured artifacts for downstream agents.

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

Ranks candidate solutions by feasibility, relevance to the paper's central claim, validation value, implementation cost, and risk.

### POC Builder

Turns a selected candidate into a scoped POC with requirements, design, tests, implementation, and validation output.

### Test Agents

Run after key steps. They validate extraction quality, handoff contracts, POC correctness, integration behavior, and pipeline-level requirements.

### Thought Playback Summarizer

Writes human-readable summaries of agent decisions, assumptions, revisions, and uncertainty. This exists so a human can inspect what happened without depending on hidden model state.

### Skill Safety Checker

Audits skills and tools before implementation-critical use. It checks manifests, permissions, side effects, declared input/output contracts, test coverage, and failure modes.

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

## Phase 1: Accurate Solution Extraction

### Objective

Achieve accurate extraction of possible solutions that could be turned into a POC from the research report.

### Deliverables

- Report ingestion and completeness validation.
- `paper_analysis.md`.
- `solution_candidates.md` and structured `solution_candidates.json`.
- `claim_map.json`.
- `assumption_map.json`.
- `poc_feasibility_review.md`.
- Human review artifact for candidate approval.
- Thought playback summary for extraction decisions.

### Tests

- Extraction completeness test.
- Claim-to-solution traceability test.
- Citation/evidence coverage check.
- Hallucination check for unsupported candidate solutions.
- Human review gate for the candidate shortlist.

### Acceptance Criteria

- Major research claims are represented in the analysis.
- Each POC candidate links back to claims, assumptions, and evidence.
- Unsupported or speculative candidates are explicitly marked.
- A human can inspect and approve the POC candidate shortlist.

## Phase 2: Successful POC Build

### Objective

Build a successful POC from one selected solution candidate.

### Local V-Model Scope

Phase 2 applies the V-model to the POC itself:

```text
POC requirements -> POC acceptance tests
POC design       -> POC integration tests
POC code         -> POC unit tests
```

This phase answers:

```text
Did this generated POC correctly implement the selected paper solution?
```

### Deliverables

- `selected_solution.md`.
- `poc_scope.md`.
- `requirements.md`.
- `design.md`.
- `test_plan.md`.
- POC source code.
- Unit, integration, and acceptance tests.
- `implementation_report.md`.
- `validation_report.md`.
- Thought playback summary for build decisions.

### Tests

- Requirement-to-acceptance-test mapping.
- Design-to-integration-test mapping.
- Code-to-unit-test mapping.
- Unit tests.
- Integration tests.
- Acceptance tests.
- Validation comparison against the selected paper claim.

### Acceptance Criteria

- The selected solution is converted into testable requirements.
- The design follows the requirements.
- The implementation follows the design.
- POC-level tests pass or failures are documented with evidence.
- The validation report states whether the POC supports, partially supports, or fails to support the selected claim.

## Phase 3: Integration And Hidden Issue Resolution

### Objective

Connect solution extraction and POC build into one reliable pipeline, then discover and fix hidden issues.

### Deliverables

- Connected extraction-to-build workflow.
- `handoff_contract.md`.
- `pipeline_run_log.jsonl`.
- `failure_modes.md`.
- `integration_review.md`.
- `recovery_plan.md`.
- Human edit/resume artifacts.
- Thought playback summary for integration issues and recovery decisions.

### Hidden Issues To Target

- Candidate solution is too vague for requirements generation.
- Claims do not map cleanly to validation criteria.
- Human edits break downstream assumptions.
- Agent output passes schema validation but fails semantic review.
- POC build requires tools or skills that were not anticipated.
- Context needed by the build step exists only in prior chat instead of artifacts.
- Failed builds do not produce actionable recovery instructions.

### Tests

- Full paper-to-POC run.
- Ambiguous solution handoff test.
- Weak or incomplete report test.
- Failed build recovery test.
- Human edit and resume test.
- Thought playback completeness check.

### Acceptance Criteria

- Extraction output reliably feeds POC build without hidden context.
- Handoff failures are detected and produce actionable revision requests.
- A human can revise an intermediate artifact and resume the pipeline.
- The integration review identifies unresolved risks before Phase 4.

## Phase 4: Pipeline-Level V-Model And Skill Safety Checker

### Objective

Apply the V-model to the entire AI4Research-B pipeline and implement the formal skill safety checker.

### System-Level V-Model Scope

Phase 4 applies the V-model to the whole report-to-validated-POC system:

```text
Pipeline requirements -> pipeline acceptance tests
Pipeline design       -> pipeline integration tests
Pipeline modules      -> module/unit tests
```

This phase answers:

```text
Does the entire research-report-to-validated-POC pipeline work reliably, visibly, safely, and with human intervention?
```

### Deliverables

- `pipeline_requirements.md`.
- `pipeline_design.md`.
- `pipeline_v_model.md`.
- System acceptance test suite.
- Pipeline integration test suite.
- Module/unit tests for pipeline components.
- `skill_manifest.schema.json`.
- `skill_safety_policy.md`.
- Skill safety checker implementation.
- `skill_audit_report.md`.
- Approved and blocked skill registries.
- Agent thought playback verifier.

### Pipeline Acceptance Tests

- Given a research report, the system produces candidate POC solutions.
- A human can select or revise a solution.
- The system builds a POC from the selected solution.
- The system produces a validation report.
- All major AI outputs are visible as artifacts.
- Human intervention is available at every gate.
- Thought playback summaries are available for every phase.
- Unsafe skill usage is blocked before critical actions.

### Pipeline Integration Tests

- Report ingestion feeds solution extraction.
- Candidate extraction feeds human selection.
- Selected solution maps to POC requirements.
- Requirements map to design.
- Design maps to implementation.
- Implementation maps to validation report.
- Test agent outputs feed review gates.
- Skill safety checker runs before implementation-critical tools.
- Human edits can resume the pipeline without corrupting state.

### Pipeline Module Tests

- Report parser.
- Solution extractor.
- Claim mapper.
- Candidate ranker.
- Handoff contract validator.
- Requirement generator.
- Design generator.
- Test generator.
- Build runner.
- Validation report generator.
- Skill manifest checker.
- Permission checker.
- Thought playback summarizer.

### Skill Safety Tests

- Missing skill manifest is blocked.
- Invalid manifest is blocked.
- Excessive permissions are blocked.
- Undeclared file, shell, network, or Docker side effects are blocked.
- Untested implementation-critical skills are blocked or require human approval.
- Skill audit result is visible to humans before use.

### Acceptance Criteria

- Pipeline-level acceptance tests pass.
- Pipeline-level integration tests pass.
- Critical pipeline modules have unit tests.
- Unsafe skills are blocked.
- Human approvals and thought playback are recorded.
- Final review can accept, revise, or reject the pipeline with evidence.

## Continuous Side Rails Across All Phases

Testing agents and thought playback are not final-stage features. They run continuously while the main stream job progresses.

```text
main stream:      extract -> build -> integrate -> system validate
testing side rail: check -> critique -> test -> report after each key output
playback side rail: summarize decisions -> record assumptions -> expose uncertainty
safety side rail: lightweight safety checks early -> formal skill checker in Phase 4
```

Every phase should produce:

- visible artifacts
- test results
- human review points
- thought playback summaries
- safety notes for tools and skills used

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

## Near-Term Build Order

1. Define the `research_report.md` handoff contract from Part A.
2. Create the run artifact layout.
3. Define schemas for report parsing, solution candidates, claim maps, selected solution, POC scope, requirements, design, validation reports, and skill manifests.
4. Implement report ingestion and completeness validation.
5. Implement Phase 1 solution extraction with stubbed or manual agents.
6. Add extraction tests and human review artifacts.
7. Implement Phase 2 POC scope, requirements, design, and test-plan generation.
8. Add local POC-level V-model tests.
9. Implement a minimal POC builder for one controlled example.
10. Connect Phase 1 and Phase 2 through a handoff contract.
11. Add hidden-issue and recovery tests.
12. Define pipeline-level requirements and system tests.
13. Implement the skill safety checker.
14. Add thought playback verification across all phases.
