# AI4Research-B Phase 0 Preliminary Design Notes

> Source: `docs/preliminary design.txt`

### Purpose of this document

This document keeps the original design checklist and adds Phase 0-specific thoughts
under each item. The goal is to make the design easier to learn from, not just to produce
a polished spec.

### Phase 0 means the research validation phase of AI4Research-B

```text
research paper/report + official code
  -> extracted claim
  -> official install and benchmark run
  -> reproduced result
  -> comparison with the paper result
  -> research validation report
```

## 1. 目标：这个程序要解决什么问题，成功标准是什么。

### What problem Phase 0 solves

Phase 0 checks whether an AI research paper's official code can reproduce the paper's
stated benchmark claim. It should not merely summarize the paper, and it should not
create a new implementation of the paper's idea. The point is to turn a paper claim into
visible validation evidence.

### Core question

Does the paper's official code run as instructed, and do the observed benchmark results
match the paper's stated claims?

### Success standard

- A run folder is created under runs/<run_id>/.
- The input paper/report and official code source are recorded.
- At least one benchmarkable claim is extracted.
- The official install and benchmark commands are recorded.
- Human review happens before risky command execution.
- Install logs and benchmark logs are saved.
- The reproduced result is parsed from real output, not guessed by AI.
- The reproduced result is compared with the paper's reported result.
- The final report says one of: reproduced, partially_reproduced, not_reproduced,
  not_testable, failed_to_run, blocked, or out_of_scope.

> **Learning note:**
> The success standard is not "the pipeline ran." The success standard is "a human can
> inspect the artifacts and understand whether the paper claim was reproduced."

## 2. 用户和场景：谁会用，在什么情况下用，最重要的 workflow 是什么。

### Users

- Researcher: wants to know if a paper's official code supports its claim.
- Developer: wants validated evidence before building a downstream POC.
- Reviewer: wants to inspect claims, commands, logs, results, and conclusions.
- Future agent: needs to resume work from files without relying on previous chat.

### Main scenario

The user provides a paper PDF or research report plus official code. Phase 0 creates a
run package, extracts a claim, extracts official commands, waits for human approval,
runs the official code, captures evidence, compares results, and writes a report.

### Most important workflow

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
```

> **Learning note:**
> The workflow has human gates because the system runs third-party research code and may
> make claims about scientific reproducibility. It should be inspectable, not fully hidden.

## 3. 输入和输出：输入格式、输出格式、边界条件、错误输入怎么处理。

### Inputs

- paper.pdf
- research_report.md
- official Git repository URL
- local official source folder
- source archive
- optional commit hash, release tag, dataset path, model weight path, API key
  availability, hardware constraints, or runtime budget

### Outputs

- input_manifest.json
- paper_parse.md and paper_parse.json
- claims.md and claims.json
- benchmark_claims.json
- code_manifest.json
- repo_snapshot.md
- official_instructions.md
- command_plan.json
- human review artifacts
- install_stdout.txt and install_stderr.txt
- benchmark_stdout.txt and benchmark_stderr.txt
- raw_benchmark_outputs/
- benchmark_results.json and benchmark_results.md
- claim_comparison.json and claim_comparison.md
- research_validation_report.md
- failure_modes.md
- pipeline_run_log.jsonl
- thought_playback.md and decision_trace.jsonl

### Boundary conditions

- No paper/report: the run cannot start.
- No official code: mark out_of_scope or not_testable.
- Paper cannot be parsed: write failure_modes.md and mark not_testable.
- Claim is too vague to benchmark: stop at claim review or mark not_testable.
- Official commands require network, GPU, API key, Docker, large download, or unclear
  file writes: block for human command review.
- Install command fails: preserve logs and mark failed_to_run.
- Benchmark command fails: preserve logs and mark failed_to_run.
- Benchmark runs but no metric can be parsed: mark not_testable.
- Reproduced result uses a different metric, dataset, split, config, or aggregation:
  record the mismatch and do not overclaim reproduction.
- Full benchmark is too expensive: allow a clearly labeled smoke validation, but do not
  call it full reproduction.

### Bad input handling

- Missing file: block and explain what is missing.
- Unsupported file type: reject or request paper.pdf/research_report.md.
- Invalid JSON artifact: block the next dependent step.
- Ambiguous code source: block until the official source is clarified.
- Non-AI paper or no runnable implementation: mark out_of_scope.

> **Learning note:**
> Boundary conditions are broader than CS "edge cases." They include invalid inputs,
> missing resources, ambiguous claims, unsafe commands, and conditions where the system
> must stop instead of pretending it reproduced the paper.

## 4. 核心流程：从输入到输出，每一步发生什么。

### Step 0: Run intake

Create the run folder, copy or reference input files, and write input_manifest.json.

### Step 1: Research parse

Extract readable text and structure from paper.pdf or research_report.md. Write
paper_parse.md and paper_parse.json.

### Step 2: Claim and benchmark extraction

Extract the validation target: claim text, benchmark, dataset, split, metric, reported
value, unit, aggregation method, and paper location. Write claims.json,
benchmark_claims.json, and claims.md.

### Step 3: Human claim review

The human approves, revises, or rejects the selected claim. Write human_claim_review.md.

### Step 4: Code intake

Clone, copy, or unpack the official code. Record source URL, branch, commit, timestamp,
README files, scripts, and environment files. Write code_manifest.json and
repo_snapshot.md.

### Step 5: Official instruction extraction

Read README, docs, scripts, configs, and paper appendix. Extract official install and
benchmark commands. Write official_instructions.md and command_plan.json.

### Step 6: Human command review

The human reviews commands and resource risks before execution. Write
human_command_review.md.

### Step 7: Install execution

Run official install commands as recorded. Capture stdout, stderr, exit code, runtime,
and environment metadata.

### Step 8: Benchmark execution

Run official benchmark commands as recorded. Capture stdout, stderr, exit code, runtime,
and generated outputs.

### Step 9: Result parsing

Parse observed metrics from result files first, then logs if needed. If parsing is not
reliable, mark not_testable instead of guessing.

### Step 10: Claim comparison

Compare the paper's reported metric with the reproduced metric. Use the same metric,
dataset, split, config, and aggregation when possible.

### Step 11: Human result review

The human reviews parsed results and comparison before final conclusion.

### Step 12: Final report

Write research_validation_report.md with inputs, official code, commands, environment,
logs, observed results, comparison, status, limitations, and review points.

> **Learning note:**
> Each step should read files and write files. This makes the workflow resumable and
> auditable.

## 5. 数据结构和 artifact：中间状态如何保存，哪些结果需要可追踪、可恢复、可审计。

### Design principle

Every important state should become an artifact. The pipeline should not depend on
hidden chat context.

### Required layout

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
    human_claim_review.md
    code_manifest.json
    repo_snapshot.md
    official_instructions.md
    command_plan.json
    human_command_review.md
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
    human_result_review.md
    research_validation_report.md
    failure_modes.md
  code/
    official/
  integration/
    pipeline_run_log.jsonl
  playback/
    thought_playback.md
    decision_trace.jsonl
```

### Important schemas

- InputManifest
- Claim
- BenchmarkClaim
- CodeManifest
- CommandPlan
- EnvironmentReport
- BenchmarkRunPlan
- BenchmarkResult
- ClaimComparison
- GateResult
- RunEvent

### Accuracy result example

```json
{
  "metric": "accuracy",
  "unit": "percent",
  "paper_reported_value": 91.2,
  "reproduced_value": 90.8,
  "difference": -0.4,
  "dataset": "Dataset X",
  "split": "test",
  "aggregation": "simple_mean_across_tasks"
}
```

> **Learning note:**
> For comparison, use the paper's original metric. Standard deviation is supporting data
> only when the paper reports it or when Phase 0 runs multiple trials. It does not replace
> accuracy, F1, pass@k, reward, or whatever metric the paper used.

## 6. 模块职责：每个组件负责什么，不负责什么。

### CLI

Responsible for user-facing commands. Not responsible for deciding scientific validity.

### Orchestrator

Responsible for step order, artifact checks, event logging, human gates, and resume
behavior. Not responsible for parsing PDFs or running benchmarks directly.

### Artifact Store

Responsible for paths, JSON/Markdown/log writes, artifact reads, and overwrite rules.
Not responsible for interpreting claims.

### Research Parser

Responsible for extracting paper/report text and source locations. Not responsible for
judging whether claims are true.

### Claim Extractor

Responsible for extracting benchmarkable claims. Not responsible for executing code.

### Code Intake

Responsible for obtaining official code and recording provenance. Not responsible for
patching or fixing the code.

### Instruction Extractor

Responsible for extracting official commands and resource requirements. Not responsible
for approving execution.

### Environment Runner

Responsible for running install commands and capturing logs. Not responsible for hiding
or silently fixing failed installs.

### Benchmark Runner

Responsible for running benchmark commands and capturing logs/output files. Not
responsible for deciding whether the paper was reproduced.

### Result Parser

Responsible for extracting observed metrics. Not responsible for guessing missing
numbers.

### Claim Comparator

Responsible for comparing paper-reported values with reproduced values and assigning a
status. Not responsible for inventing evidence.

### Report Writer

Responsible for writing the final human-readable report from artifacts. Not responsible
for changing the underlying evidence.

> **Learning note:**
> A good module boundary says both what the module does and what it must not do.

## 7. 接口契约：模块之间传什么数据，用什么 schema，谁可以拒绝谁的输出。

### Contract style

Modules communicate through artifacts and schemas, not hidden memory.

### Examples

- ResearchParser writes paper_parse.json.
- ClaimExtractor consumes paper_parse.json and writes claims.json and
  benchmark_claims.json.
- CodeIntake writes code_manifest.json.
- InstructionExtractor consumes code_manifest.json and writes command_plan.json.
- BenchmarkRunner consumes command_plan.json and writes benchmark_stdout.txt,
  benchmark_stderr.txt, and raw_benchmark_outputs/.
- ResultParser consumes benchmark logs/output files and writes benchmark_results.json.
- ClaimComparator consumes benchmark_claims.json and benchmark_results.json and writes
  claim_comparison.json.

### When a module can reject upstream output

- required artifact is missing
- JSON does not match schema
- required field is missing
- selected claim is not benchmarkable
- command source is not official or not recorded
- resource risks are unknown before execution
- benchmark result cannot map to the claim
- result uses the wrong metric/dataset/split/config without explanation

> **Learning note:**
> "Who can reject whose output" is important because it prevents bad artifacts from quietly
> becoming final conclusions.

## 8. 技术栈：用什么库、工具、模型、renderer、数据库、文件格式。

### Language

- Python 3.12

### CLI

- Typer

### Schemas

- Pydantic

### Testing

- pytest

### PDF parsing

- PyMuPDF first
- pdfplumber fallback

### Code intake

- Git CLI
- local copy/unpack for local folders and archives

### Command execution

- Python subprocess
- explicit working directory
- stdout/stderr capture
- exit code capture
- timeouts

### Artifacts

- JSON for structured data
- Markdown for human-readable artifacts
- JSONL for event logs and decision traces
- TXT for raw stdout/stderr logs

### Environment

- Python venv for MVP
- Docker later if stronger isolation is needed

### AI/model usage

- AI can help extract claims, summarize official instructions, and draft reports.
- AI is not validation evidence.

### Database

- Not needed for MVP. The filesystem is enough because file-first traceability is a core
  requirement.

### Renderer/UI

- Not needed for MVP. Markdown artifacts are enough for human inspection.

## 9. 失败模式：每一步可能怎么失败，失败后是重试、降级、阻塞还是人工介入。

### Intake failures

- missing paper/report
- missing code source
- unsupported input type
- code URL inaccessible

### Response

- block, or mark out_of_scope/not_testable

### Parsing failures

- PDF unreadable
- extraction incomplete
- report missing required sections

### Response

- write failure_modes.md
- mark not_testable or request human-supplied report

### Claim failures

- no benchmarkable claim
- reported value missing
- metric/dataset/split ambiguous

### Response

- block at claim review
- mark not_testable if ambiguity cannot be resolved

### Command planning failures

- README missing install command
- README missing benchmark command
- command source unclear
- command requires unapproved network/GPU/API key/Docker/large download

### Response

- block for human command review

### Execution failures

- install exits nonzero
- benchmark exits nonzero
- timeout
- memory exhaustion
- disk fills up
- dependency conflict

### Response

- save stdout/stderr/exit code/runtime
- mark failed_to_run or blocked

### Result failures

- benchmark succeeds but produces no metric
- output format unknown
- observed metric does not match paper metric
- result uses different dataset or split

### Response

- mark not_testable, partially_reproduced, or not_reproduced depending on evidence

### Report failures

- report conclusion is unsupported by artifacts
- optional benchmark is mixed with original reproduction

### Response

- block final report gate until corrected

> **Learning note:**
> Failure does not always mean "the code crashed." It can also mean the result is
> ambiguous, unsafe to obtain, too expensive, or not comparable to the paper claim.

## 10. 质量门：怎么判断每一步真的合格，而不是只是“跑完了”。

### Design principle

Keep quality gates lightweight. Do not put a heavy formal review after every step.

### Use two levels

- Light checks: automatic checks after artifact-writing steps.
- Formal gates: only before trusting, executing, or concluding something important.

### Light checks

- artifact exists
- JSON parses
- schema is valid
- required fields are present
- status label is valid

### Formal gates

## 1. Claim Selection Gate

Before using an extracted claim as the validation target.

### Checks

- claim is benchmarkable
- benchmark/dataset is known
- metric is known
- reported value exists or missing value is explicitly justified
- human_claim_review.md exists

## 2. Command Execution Gate

Before running third-party code.

### Checks

- commands are copied from or derived from official sources
- command_plan.json records install and benchmark commands
- resource risks are explicit
- human_command_review.md exists
- high-risk commands are not run silently

## 3. Result Interpretation Gate

Before declaring reproduced, partially_reproduced, or not_reproduced.

### Checks

- observed metric exists
- metric matches the paper metric
- dataset/split/config/aggregation match or mismatches are recorded
- raw logs or result files support the parsed result

## 4. Final Report Gate

Before accepting the final validation package.

### Checks

- final status is supported by artifacts
- report points to raw logs and parsed results
- limitations are stated
- official reproduction is separated from optional extended benchmarks

### Gate outcomes

- pass: continue
- warn: continue but record limitation
- block: stop until fixed or reviewed

> **Learning note:**
> A light check asks: can the next program step safely read this artifact?

A formal gate asks: are we about to trust, execute, or conclude something important?

## 11. 测试策略：unit test、integration test、end-to-end test、人工 review 分别覆盖什么。

### Unit tests

- artifact path generation
- schema validation
- status label validation
- command plan validation
- result parser behavior
- claim comparison logic
- gate result logic

### Integration tests

- create a fake run folder
- parse a fake research_report.md
- extract one fake benchmark claim
- copy a fake official code repo
- run a tiny benchmark script
- capture logs
- parse result
- compare result
- write report

### End-to-end test

### Use a tiny local fixture

```text
tests/fixtures/phase0_fake_paper/
  research_report.md
  official_code/
    README.md
    requirements.txt
    benchmark.py
    expected_results.json
```

The fake benchmark should run quickly and deterministically. It proves the pipeline
works before trying real research code.

### Human review covers

- claim selection
- command execution
- result interpretation
- final report acceptance

> **Learning note:**
> The first real test should not be a large research paper. Build confidence with a tiny
> fake official repo first.

## 12. 可观测性：日志、运行记录、调试 artifact、决策 trace。

### Pipeline log

```text
runs/<run_id>/integration/pipeline_run_log.jsonl
```

### Each event should include

- run_id
- step
- status
- started_at
- ended_at
- artifacts_written
- message

### Debug artifacts

- install_stdout.txt
- install_stderr.txt
- benchmark_stdout.txt
- benchmark_stderr.txt
- raw_benchmark_outputs/
- environment.json
- failure_modes.md
- gate result files

### Decision trace

```text
runs/<run_id>/playback/decision_trace.jsonl
```

### Thought playback

```text
runs/<run_id>/playback/thought_playback.md
```

### Thought playback should summarize

- what was decided
- what artifact supported the decision
- what assumptions were made
- what uncertainty remains
- what a human should review

> **Learning note:**
> Observability means a future person can inspect what happened without rerunning the
> whole pipeline or reading hidden model reasoning.

## 13. 成本和性能：运行时间、API 调用、并发、缓存、timeout、fallback。

### Expected runtime

- Artifact validation and parsing should be fast.
- Fake fixture tests should run in seconds.
- Real paper reproduction may take minutes or hours.
- API-based agent papers may cost money and may not be exactly reproducible over time.

### Performance controls

- command timeouts
- benchmark timeout setting
- avoid rerunning completed steps unless rerun is explicit
- cache cloned repos only when commit/provenance remains clear
- separate planning from execution

### Cost controls

- detect API key requirements
- record expected model/API calls when possible
- block paid API use until human approval
- record when a benchmark is reduced to a smoke validation

### Fallbacks

- If PDF parsing fails, accept research_report.md.
- If result files are missing, parse stdout/stderr.
- If full benchmark is too expensive, run a clearly labeled smoke validation.
- If official benchmark is impossible locally, mark blocked or not_testable instead of
  inventing a substitute.

> **Learning note:**
> A smoke validation can show that the code path works, but it should not be reported as
> full reproduction of the paper's benchmark.

## 14. 安全和权限：文件写入、网络、外部代码、API key、Docker、模型调用等风险。

### Main risk

Phase 0 runs third-party research code. That code can install packages, download large
files, call APIs, use CPU/GPU heavily, write files, modify environments, or fail in
misleading ways.

### Practical risks

- disk fills up from model/dataset downloads
- memory exhaustion makes the machine freeze
- long-running benchmark consumes CPU/GPU
- API calls cost money
- global package install pollutes the environment
- script writes files outside the run folder
- install script runs arbitrary shell commands
- command succeeds but benchmark used dummy data or skipped evaluation

### MVP safety rules

- Do not run third-party commands automatically.
- Write command_plan.json before execution.
- Require human command review before install or benchmark execution.
- Mark network, GPU, API key, Docker, large download, and unclear file-write risks.
- Prefer isolated virtual environments.
- Avoid global pip installs.
- Use explicit working directories.
- Capture stdout, stderr, exit code, and runtime.
- Do not patch official code unless a human approves a recorded deviation.
- Treat failed runs as evidence.

### Risk levels

- low: local parsing and artifact validation, no external code execution
- medium: bounded local commands inside the run/code folder
- high: network, API calls, Docker, large downloads, GPU-heavy jobs, global installs, or
  unclear side effects

> **Learning note:**
> Most failures are harmless, but command execution deserves caution because external code
> can consume disk, memory, time, money, or modify files.

## 15. Overall MVP Shape

### The first version should be simple

- file-first
- local filesystem artifacts
- Python CLI
- Pydantic schemas
- lightweight checks
- four formal gates
- fake fixture end-to-end test
- no full UI
- no database
- no automatic risky command execution

### The main design idea

Phase 0 should be strict about evidence but lightweight in process.

Do not validate every tiny step with a heavy gate. Instead, use cheap automatic checks

### after artifact-writing steps and reserve formal gates for

- choosing the claim
- running third-party code
- interpreting results
- accepting the final report
