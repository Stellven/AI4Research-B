# Phase 0 Automation Temporary Design

This note captures the current approach for turning the SkillGen-specific Phase 0 demo into an automated claim verification pipeline. It is temporary and should be merged into the main Phase 0 design once the implementation stabilizes.

## Current Position

The current SkillGen run has valid evidence artifacts, but not every step was produced by an automated pipeline.

Automated today:

- run intake
- PDF parsing
- primary claim extraction
- preliminary benchmark claim artifact generation
- blocked-state report generation

Manually or partially automated today:

- official code intake
- official instruction extraction
- executable contract formation
- command approval enforcement
- install execution
- benchmark execution
- result parsing
- claim comparison
- report update after benchmark results

The next goal is to automate the already-proven SkillGen AIME smoke path end to end, while keeping the artifact boundaries general enough for later Table 1 rows.

## Implementation Update

The first SkillGen-specific POC automation now exists in `ai4research_b/phase0/skillgen_automation.py`.

Implemented:

- official code intake or local official-source verification
- official instruction extraction from README and CLI scripts
- AIME smoke asset preparation with idempotent preservation of existing reviewed assets
- verification contract generation
- command-plan generation
- machine-readable approval gate checks
- install runner scaffold with project-local virtual environment and cache paths
- benchmark train/eval runner scaffold
- structured result parsing
- deterministic claim comparison
- artifact-driven report rendering
- no-network unit tests using a fake official-code fixture
- SkillGen all-claims catalog generation
- claim-by-claim verification matrix generation
- official-code support detection for bundled benchmark data and missing benchmark/baseline assets

Still gated or intentionally limited:

- live install execution requires `artifacts/approval.json`
- live benchmark execution requires `artifacts/approval.json`, API keys, network permission, and token-spend approval
- full SkillGen Table 1 reproduction is still blocked until a matching Table 1 verification contract is created and approved
- generalized environment planning remains out of scope for this temporary POC
- claims requiring unreleased baseline-generator code, ablation runners, or missing benchmark data are marked `not_testable` instead of being reconstructed silently
- all-claims automation currently covers major empirical/executable paper claims, not every prose sentence in the paper

Approval UX note:

- The repository code cannot create arbitrary native Codex UI boxes.
- The durable Phase 0 approval state remains `artifacts/approval.json`, because future agents must be able to resume from files.
- When running inside Codex, use Codex's native command-approval prompt for risky execution and launch `execute --record-codex-approval`; after the human clicks approve, the runner records that approval into `artifacts/approval.json` before proceeding.
- Outside Codex, use the `approve` subcommand to write the same artifact after human review.

## Automation Principle

For this phase, the pipeline may be SkillGen-specific, but the automation should still preserve generic Phase 0 boundaries:

```text
paper parse
-> claim extraction
-> verification contract
-> command plan
-> approval gate
-> install runner with minimal environment record
-> benchmark execution
-> result parsing
-> comparison
-> report
```

LLM usage is acceptable for semantic understanding, but executable validation must come from deterministic artifacts, official code, command logs, and result files.

## Temporary Environment Scope

For the small SkillGen-only Phase 0 POC, robust environment planning is intentionally out of scope. Environment handling should be reduced to a minimal, factual environment record instead of a standalone planning phase.

Keep:

- dependency-location rule enforcement
- official-code virtual environment under the run directory
- package/tool cache directories under the project or run directory
- API-key presence checks without printing values
- network/API/cost flags in `command_plan.json`
- raw install logs in `outputs/`
- final `artifacts/environment.json`

Omit for now:

- generalized hardware planning
- Docker detection
- large dataset/model-weight planning
- cross-platform environment inference
- broad dependency risk analysis

This changes the temporary POC loop to:

```text
verification contract
-> command plan
-> approval gate
-> install runner with minimal environment record
-> benchmark runner
-> result parser
-> comparator
-> report renderer
```

## Missing Automation Steps

### 1. Contract Formation

Current issue: `benchmark_claims.json` describes the paper claim, but it does not fully bind the claim to an executable run target.

Approach:

- Use the LLM or paper-specific parser to identify the claim semantics.
- Use deterministic code to normalize the contract.
- Add a SkillGen-specific `verification_contract.json` or extend `benchmark_claims.json`.

The contract should include:

- selected target: AIME smoke or a specific Table 1 row
- dataset and split
- training subset and evaluation subset
- model and judge model
- seed
- baseline condition
- treatment condition
- metric
- expected output files
- parser name
- comparison rule
- status rule
- required environment variables
- estimated cost or token budget
- hardcoding disclosures

### 2. Official Code Intake

Current issue: the official repository exists in the run package, but cloning and snapshot recording were not handled by reusable code.

Why it is not automated yet:

- The current demo extracts the SkillGen GitHub URL from the paper, but it does not run a reusable clone-or-verify step.
- The current code does not record repository metadata automatically, such as commit hash, branch, README files, scripts, config files, and nested Git state.
- The richer `code_manifest.json` and `repo_snapshot.md` in the existing run were created through manual inspection and artifact updates, not a reusable intake component.

Approach:

- Add a SkillGen code-intake step.
- Clone or verify the official repository at `code/official/`.
- Record repository URL, commit hash, branch, README path, key scripts, config files, and local path.
- Write `code_manifest.json` and `repo_snapshot.md`.

For now, hardcoding the SkillGen GitHub URL is acceptable if recorded in `hardcoding_disclosures.md`.

### 3. Official Instruction Extraction

Current issue: README and script inspection were performed manually.

Why it is not automated yet:

- The current demo writes a blocked placeholder for `official_instructions.md`.
- The current code does not parse `README.md`, `requirements.txt`, `config.yaml`, `main.py`, or `eval_skill.py`.
- The README/eval CLI mismatch was discovered manually; no extractor currently compares README examples with actual parser flags.
- The command plan was manually enriched after inspecting the official repository, rather than generated from an instruction-extraction component.

Approach:

- Read official `README.md`, `config.yaml`, `main.py`, and `eval_skill.py`.
- Extract install instructions, quickstart training command, evaluation command shape, supported CLI flags, data paths, and config requirements.
- Detect mismatches between README examples and actual CLI parser.
- Write `official_instructions.md`.

For SkillGen, one known issue is that the README eval example uses flags that differ from `eval_skill.py`. The automated extractor should record this as a deviation instead of silently fixing it.

### 4. Command Plan

Current issue: command plans exist, but they are not generated from an executable contract.

Why it is not automated yet:

- `benchmark_claims.json` currently describes the claim, but it is not yet a complete executable verification contract.
- The command plan needs both official instruction extraction and the selected verification target.
- The current command plan was assembled from manual repository inspection and the manually selected AIME smoke target.
- There is not yet a deterministic command-plan generator that turns `verification_contract.json` into install, train, and eval command objects.

Approach:

- Generate `command_plan.json` from `verification_contract.json` plus official instruction extraction.
- Separate install commands, training commands, and evaluation commands.
- Record workdir, environment variables, output paths, timeout, expected generated files, and cost risk.
- Mark network/API/token-spend requirements explicitly.

The runner should only consume commands from `command_plan.json`, not from hidden chat context.

### 5. Gate Enforcement

Current issue: approval happened through chat and artifact notes, not through a machine-readable approval state.

Why it is not automated yet:

- Human approval exists as conversation context and Markdown notes, not as a machine-readable artifact consumed by the runner.
- The runner does not yet check whether an approved target, cost limit, network permission, and API-key permission exist before executing.
- Human-in-the-loop approval should remain, but the gate logic itself should be automated: the machine should pause, inspect approval state, and either proceed or write `blocked`.

Approach:

- Add `human_command_review.md` for human readability.
- Add a small machine-readable approval field or file, such as `approval.json`.
- Runner checks approval before network, API, paid, Docker, or large-download steps.

Example:

```json
{
  "command_plan_approved": true,
  "approved_targets": ["skillgen_aime_smoke"],
  "max_cost_usd": 5.0,
  "approved_by": "human",
  "notes": "Approved only for AIME smoke, not full Table 1."
}
```

### 6. Install Execution

Current issue: install was run manually.

Why it is not automated yet:

- Install execution needs approval because it can use network, execute third-party package setup code, and write dependencies/caches.
- The current project does not yet have a runner that reads install command objects from `command_plan.json`.
- The current project does not yet enforce the dependency-location rule programmatically.
- The previous install was run by a human-approved shell command and then recorded as evidence.

Automation behavior:

- Check `approval.json` before running any install command that requires network or third-party package execution.
- Create or reuse the official-code virtual environment inside the run directory.
- Set cache directories inside the project, such as `UV_CACHE_DIR` under `code/official/.uv-cache`.
- Execute only commands listed in `command_plan.json`.
- Capture stdout, stderr, exit code, start time, end time, duration, workdir, and command string.
- Mark `failed_to_run` if install fails, and stop before benchmark execution.

Approach:

- Add a command runner that executes install commands from `command_plan.json`.
- Capture stdout, stderr, exit code, start time, end time, runtime, and command workdir.
- Write raw logs to `outputs/install_stdout.txt` and `outputs/install_stderr.txt`.
- Write environment metadata to `artifacts/environment.json`.

The runner must keep all dependencies inside the project directory, using repo-local virtual environments and cache directories.

### 7. Benchmark Execution

Current issue: training and evaluation were manually run.

Why it is not automated yet:

- The benchmark runner does not yet exist.
- The SkillGen eval command depends on the timestamped skill output directory produced by the training command.
- The current code does not yet detect generated SkillGen output paths or fill the eval command template.
- API-key usage and token spend still require a machine-readable approval gate before execution.

Automation behavior:

- Check that install completed successfully.
- Check `approval.json` for the selected target and cost/network/API permissions.
- Run the SkillGen training command from `command_plan.json`.
- Detect the generated `skill_output/<timestamp>/` directory and skill id.
- Fill the eval command template with the detected skill path.
- Run the eval command.
- Capture train/eval stdout and stderr under `outputs/`.
- Preserve SkillGen-generated artifacts under `artifacts/raw_benchmark_outputs/`.
- Mark `failed_to_run` if command execution fails, `not_testable` if expected output files are missing, and continue to parsing only when required outputs exist.

Approach:

- Add SkillGen benchmark runner that executes the train command first.
- Detect the generated skill output directory after training.
- Fill the eval command template with the generated skill path.
- Execute eval command.
- Capture benchmark stdout/stderr in `outputs/`.
- Preserve generated files under `artifacts/raw_benchmark_outputs/`.

For now, support the AIME smoke target first. Table 1 row automation can be added after the smoke runner is stable.

### 8. Result Parsing

Current issue: benchmark results were manually summarized.

Why it is not automated yet:

- The parser for SkillGen output files has not been implemented.
- The current `benchmark_results.json` was manually assembled from `eval_results.json`, token usage files, and verification summaries.
- There is not yet a deterministic rule for choosing structured files over logs and marking missing fields as `not_testable`.

Automation behavior:

- Read structured output files first.
- Parse logs only as fallback evidence.
- Validate that all required fields for the selected contract are present.
- Write `benchmark_results.json` as the normalized machine-readable result.
- Write `benchmark_results.md` as the human-readable result summary.
- Preserve raw files unchanged.

Approach:

- Parse structured files first, especially `eval_results.json`, token usage JSON, verification summary JSON, and generated skill analysis files.
- Fall back to logs only when structured files are missing.
- Produce `benchmark_results.json` and `benchmark_results.md`.

For SkillGen AIME smoke, parse:

- baseline accuracy
- skill accuracy
- delta accuracy
- repairs
- regressions
- net gain
- paired sample count
- token usage
- generated skill id

### 9. Claim Comparison

Current issue: comparison was manually written.

Why it is not automated yet:

- The comparator does not yet read a verification contract and normalized benchmark result.
- The status rules are currently implicit in the manually written report.
- The smoke target and full Table 1 paper claim need separate verdict scopes, and that distinction is not yet encoded.

Automation behavior:

- Read `verification_contract.json` and `benchmark_results.json`.
- Apply deterministic status rules.
- Assign a scoped verdict for the executed target.
- Keep the full paper claim `blocked` unless the executed target actually matches the full paper setup.
- Write `claim_comparison.json` and `claim_comparison.md`.

Approach:

- Compare `benchmark_results.json` against the selected `verification_contract.json`.
- Assign a Phase 0 status using deterministic rules.
- Write `claim_comparison.json` and `claim_comparison.md`.

For the AIME smoke target, the status should be scoped carefully:

- smoke target can be `reproduced` or `not_reproduced`
- full Table 1 claim should remain `blocked` unless the Table 1 setup is actually run

### 10. Report Generation

Current issue: report generation works for blocked preliminary state, but not yet as a final renderer from all artifacts.

Why it is not automated yet:

- The current report writer handles the initial blocked state, but the post-benchmark report was manually updated.
- The renderer does not yet read the complete set of artifacts and rebuild the report from source evidence.
- The report currently mixes generated automation output with manually curated summary text.

Automation behavior:

- Render the report from artifacts only.
- Support repeated execution after any step.
- Include missing or failed steps explicitly instead of omitting them.
- Include deviations, hardcoding disclosures, resource requirements, raw log locations, parsed results, comparison status, and limitations.
- Never infer a reproduction result from chat history or model judgment.

Approach:

- Make report generation read only artifacts.
- Include selected claim, official code, commands, environment, raw outputs, parsed results, comparison, limitations, deviations, and status.
- Never let the report infer results from chat.

The report writer should be rerunnable after any step.

### 11. Run Logging And Playback

Current issue: logs exist, but not every future automated step has a consistent event format.

Approach:

- Every step appends to `integration/pipeline_run_log.jsonl`.
- Every major decision appends to `playback/decision_trace.jsonl`.
- Human-readable summaries go to `playback/thought_playback.md`.
- Failure cases write or update `artifacts/failure_modes.md`.

## Recommended Implementation Order

1. Add `verification_contract.json` for the SkillGen AIME smoke target.
2. Add a command-plan generator that reads the contract.
3. Add machine-readable approval checking.
4. Add install runner.
5. Add train/eval runner.
6. Add result parser for SkillGen eval outputs.
7. Add comparator.
8. Replace manual report update with artifact-driven report generation.
9. Add tests using a fake no-network fixture.
10. Add an integration test that is skipped unless API keys and approval are present.

## Hardcoding Policy For This Temporary Version

Allowed hardcoding:

- SkillGen paper-specific claim selector.
- Official repository URL: `https://github.com/yccm/SkillGen`.
- AIME smoke target as the first validation target.
- Known SkillGen result parser for `eval_results.json`.
- Known README/CLI mismatch handling.

Required disclosure:

- Every hardcoded item must appear in `hardcoding_disclosures.json` and `hardcoding_disclosures.md`.
- Hardcoded paths should be relative to the run directory when possible.
- Hardcoded paper-specific logic should be isolated in a SkillGen module, not spread across the runner.

## Success Criteria

This temporary automation succeeds when a fresh SkillGen run can:

- create the run package,
- parse the paper,
- generate an executable verification contract,
- generate the command plan,
- stop if approval is missing,
- run install and AIME smoke when approval exists,
- parse official output files,
- compare results deterministically,
- write the final report,
- and allow a future agent to resume from artifacts without chat history.
