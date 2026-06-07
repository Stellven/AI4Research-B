# Ollama Local Solution Validation Execution Manual

Date: 2026-06-04
Owner role: orchestrator / supervising agent
Execution role: delegated benchmark agent

## 1. Goal

This run does not try to reproduce the paper's original numerical claims.

The goal is to validate our Phase 0 solution direction:

> Can we turn previously `blocked` or `not_testable` SkillGen claim verifications into executable, evidence-producing validation runs by using local infrastructure, reconstructed adapters, explicit deviations, and preserved traces?

In this manual, Codex is the orchestrator. Ollama is the local LLM backend under test. The output should be a local evidence package showing whether the SkillGen-style pipeline can run, generate skills, evaluate those skills, and preserve enough evidence to support at least `partially_solution_validated`.

## 2. Feasibility Verdict

This is feasible, with two important conditions.

First, the current official SkillGen code is not already Ollama-native. In `phase_0/runs/skillgen_phase0_thorough_20260602/code/official/llm.py`, chat calls normally go through OpenRouter, and the direct OpenAI fallback only applies to `openai/...` model names. A local Ollama run therefore needs a small, recorded deviation patch that routes chat calls to an OpenAI-compatible local endpoint.

Second, SkillGen also uses embeddings. The current code path uses OpenAI embeddings. If the run must avoid all external APIs, the delegated agent must either route embeddings to a local embedding backend or add an env-gated deterministic embedding fallback. For first validation, use a deterministic hash embedding fallback. It is less semantically accurate than the paper's original setup, so it must be documented as a reconstructed solution-validation deviation.

## 3. What This Run Can And Cannot Prove

This run can prove:

- The benchmark pipeline is executable without external LLM APIs.
- A local model can be used as the benchmark model through Ollama.
- Skill generation, verification, held-out evaluation, result parsing, and trace preservation can be made observable.
- Previously blocked or not-testable verification paths can become testable under an explicitly documented local execution strategy.

This run cannot prove:

- The original paper's exact reported percentages are reproduced.
- The original model suite is reproduced.
- The original embedding behavior is reproduced, if hash embeddings are used.
- The original claim is fully reproduced under paper-equivalent conditions.

Use solution-validation statuses, not paper-reproduction statuses.

## 4. Status Labels For This Work

Use these labels in the output report:

- `solution_validated`: the local run completes, the generated skill improves held-out evaluation over the no-skill baseline, net gain is positive, skill artifacts exist, and per-round traces are preserved.
- `partially_solution_validated`: the local run completes and produces useful evidence, but improvement is partial, only appears in construction verification, is benchmark-limited, or depends on a documented reconstructed component.
- `not_solution_validated`: the local run completes, but the generated skill does not improve evaluation or is rejected/deprecated by the verification process.
- `failed_to_run`: install, train, or eval commands fail before producing usable evidence.
- `inconclusive`: the local model runs but its output format breaks parsing/evaluation so often that the benchmark result cannot be interpreted.

Do not mark these runs as `reproduced` unless a separate paper-equivalent reproduction is actually performed.

## 5. Recommended First Benchmark

Start with `mcp_bench_single`.

Reasons:

- It already has a known train-and-eval path in our previous work.
- The data size can be kept small.
- It avoids ALFWorld adapter complexity for the first Ollama integration test.
- It is sufficient to validate whether the local execution strategy can produce complete evidence.

Suggested first run:

- Benchmark: `mcp_bench_single`
- Train set size: 40
- Held-out test size: 16
- Max refine rounds: 1
- Max workers: 1
- Verification sample size: 4
- Web search: disabled
- Router: disabled

Only after this first run completes should the agent expand to ALFWorld, ScienceWorld, LiveBenchCode, AIME, or cross-model transfer.

## 6. Required Output Directory

Write all new evidence under:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/<model_slug>/
```

Also copy the exact config used into:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/<model_slug>.yaml
```

Use a filesystem-safe model slug. For example:

```text
qwen2.5:7b-instruct -> qwen2.5_7b-instruct
llama3.1:8b -> llama3.1_8b
```

## 7. Required Evidence Files

The delegated agent must produce at least these files:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/<model_slug>/
  environment_manifest.md
  deviation_note.md
  ollama_probe_stdout.txt
  chat_probe_stdout.txt
  embedding_probe_stdout.txt
  train_stdout.txt
  train_stderr.txt
  eval_stdout.txt
  eval_stderr.txt
  eval_results.json
  parsed_metrics.json
  solution_validation_result.md
  solution_validation_result.json
  trace_inventory.md
```

If any file cannot be produced, create it anyway and explain why it is unavailable.

## 8. Preflight Checks

Run from repository root:

```bash
pwd
```

Expected:

```text
/Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B
```

Check Ollama:

```bash
ollama --version
ollama list
```

Check the Ollama HTTP API:

```bash
curl http://127.0.0.1:11434/api/tags
```

Choose one installed model from `ollama list`. Do not download a new model unless the user explicitly approves the disk and time cost.

If no useful model is installed, stop and report:

```text
blocked: no local Ollama model available
```

Recommended model types:

- instruction-tuned model
- at least 7B class if available
- stable enough to produce JSON-like outputs

Examples, only if already installed:

```text
qwen2.5:7b-instruct
llama3.1:8b
mistral:7b-instruct
```

## 9. Safety And Deviation Note

Before changing any official-code file, create:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/solution_validation/ollama_mcp_bench_single/<model_slug>/deviation_note.md
```

It must say:

- This is not an original-paper reproduction.
- The official LLM API path is being redirected to local Ollama.
- External OpenAI/OpenRouter chat is disabled for this run.
- OpenAI embeddings are replaced by a local deterministic fallback, unless a real local embedding endpoint is used.
- The purpose is to validate whether the blocked/not-testable path can be made executable and evidence-producing.

## 10. Code Patch Required

Patch only the local official-code copy:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/llm.py
```

Do not patch upstream repositories or unrelated folders.

The patch should be env-gated. The existing behavior must remain available when the local flags are not set.

Required environment variables:

```bash
export SKILLGEN_LOCAL_OPENAI_COMPAT=1
export SKILLGEN_LOCAL_BASE_URL=http://127.0.0.1:11434/v1
export SKILLGEN_LOCAL_API_KEY=ollama
export SKILLGEN_LOCAL_MODEL=<exact_ollama_model_name>
export SKILLGEN_LOCAL_EMBEDDING_MODE=hash
export SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0
```

### 10.1 Chat Routing Patch

In `llm.py`, make the OpenRouter client factory check `SKILLGEN_LOCAL_OPENAI_COMPAT` first.

Expected behavior:

- If `SKILLGEN_LOCAL_OPENAI_COMPAT=1`, create `OpenAI(base_url=SKILLGEN_LOCAL_BASE_URL, api_key=SKILLGEN_LOCAL_API_KEY)`.
- Otherwise, preserve the existing OpenRouter behavior.
- When local mode is enabled, use `SKILLGEN_LOCAL_MODEL` as the actual model name sent to Ollama, regardless of the paper config's provider prefix.

The local model name should match `ollama list` exactly, for example:

```text
qwen2.5:7b-instruct
```

Do not send `openai/...` or `ollama/...` unless that exact name exists in Ollama.

### 10.2 Direct OpenAI Fallback

The code already has a direct OpenAI fallback for `openai/...` model names.

For local validation, this fallback must not be used.

Set:

```bash
export SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=0
```

If the code has branches that still call `_get_openai_client()` for chat, patch them so local mode takes precedence.

### 10.3 Embedding Fallback Patch

Find the embedding function in `llm.py`. It currently uses OpenAI embeddings.

Add an env-gated fallback:

```text
if SKILLGEN_LOCAL_EMBEDDING_MODE == "hash":
    return deterministic_hash_embeddings(texts)
```

Implementation requirements:

- No network calls.
- No new dependencies.
- Fixed vector length, for example 256.
- Deterministic across runs.
- Normalize vectors so magnitude does not grow only because text is longer.
- Accept both a single string and a list of strings if the existing function supports both.
- Preserve the existing OpenAI embedding behavior when the env var is not set.

Suggested algorithm:

```text
1. Lowercase text.
2. Split on whitespace and punctuation.
3. For each token, hash token with sha256.
4. Map hash to an index in [0, 255].
5. Add +1 or -1 based on another hash bit.
6. L2-normalize the vector.
```

Record clearly that this is a reconstructed local fallback, not the paper's original embedding method.

## 11. Config Creation

Use the existing generated config as the base:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/mcp_bench_single/openai_gpt-5.4-nano.yaml
```

Copy it to:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/<model_slug>.yaml
```

Edit the copied config only.

Required changes:

- Set all chat model fields to the exact Ollama model name.
- Set embedding model to `local-hash-embedding` if using hash fallback.
- Keep `generation.use_web_search: false`.
- Keep `router.enabled: false`.
- Keep `pipeline.max_refine_rounds: 1`.
- Keep `max_workers: 1`.
- Keep `verification.sample_size: 4`.
- Set output paths to the solution-validation directory.

The config must not require OpenRouter, OpenAI, web search, remote embeddings, Docker, or GPU unless separately approved.

## 12. Local Probe Commands

Run all probes before the benchmark.

### 12.1 Ollama API Probe

```bash
curl http://127.0.0.1:11434/api/tags
```

Save output to:

```text
ollama_probe_stdout.txt
```

### 12.2 OpenAI-Compatible Chat Probe

From the official code folder:

```bash
cd "phase_0/runs/skillgen_phase0_thorough_20260602/code/official"
.venv/bin/python - <<'PY'
import os
from openai import OpenAI

model = os.environ["SKILLGEN_LOCAL_MODEL"]
client = OpenAI(
    base_url=os.environ.get("SKILLGEN_LOCAL_BASE_URL", "http://127.0.0.1:11434/v1"),
    api_key=os.environ.get("SKILLGEN_LOCAL_API_KEY", "ollama"),
)
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Return OK only."}],
    temperature=0,
)
print(resp.choices[0].message.content)
PY
```

Save output to:

```text
chat_probe_stdout.txt
```

Expected content should contain `OK` or a very short equivalent.

### 12.3 SkillGen LLM Wrapper Probe

From the official code folder:

```bash
.venv/bin/python - <<'PY'
import os
import llm

model = os.environ["SKILLGEN_LOCAL_MODEL"]
print(llm.chat("Return OK only.", model=model, temperature=0))
PY
```

If this calls OpenRouter or OpenAI, the patch is incomplete.

### 12.4 Embedding Probe

From the official code folder, call the local embedding function directly after inspecting its real function name.

The probe must prove:

- It returns vectors.
- It does not call OpenAI.
- Repeated calls on the same text return the same vector.

Save output to:

```text
embedding_probe_stdout.txt
```

## 13. Environment Manifest

Create:

```text
environment_manifest.md
```

Include:

- date and timezone
- git branch and commit, if available
- Python version
- virtualenv path
- Ollama version
- selected Ollama model name
- selected Ollama model digest, if visible from `ollama list` or `ollama show`
- all `SKILLGEN_LOCAL_*` environment variables except secrets
- whether OpenAI/OpenRouter keys were unset, ignored, or present but bypassed
- machine notes relevant to runtime

Do not paste real API keys.

## 14. Benchmark Execution

Run from:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official
```

Use the project-local virtualenv. Do not install dependencies outside the project directory.

If `.venv` is missing, stop and report the missing dependency environment. Do not create a global environment.

### 14.1 Train / Skill Generation

Use the copied local config.

Command shape:

```bash
.venv/bin/python main.py data/mcp_bench/train.json --config "../../artifacts/07_configs_and_inputs/generated_configs/local_ollama/mcp_bench_single/<model_slug>.yaml"
```

Capture stdout and stderr into:

```text
train_stdout.txt
train_stderr.txt
```

If the config path differs because of the working directory, fix the path and record the final command in `solution_validation_result.md`.

### 14.2 Locate Skill Output

After train finishes, locate the generated skill repository or run artifact.

Search likely locations:

```text
phase_0/runs/skillgen_phase0_thorough_20260602/code/official/artifacts/
phase_0/runs/skillgen_phase0_thorough_20260602/artifacts/08_results/raw_benchmark_outputs/
```

Record:

- skill repo path
- verification summary path
- per-round trace paths
- candidate skill file paths
- whether the skill was accepted, rejected, or deprecated

Write this to:

```text
trace_inventory.md
```

### 14.3 Held-Out Eval

Use the generated skill repo from training.

Command shape:

```bash
.venv/bin/python eval_skill.py \
  --skill-repo "<skill_output_dir>" \
  --dataset data/mcp_bench/test.json \
  --n 16 \
  --seed 42 \
  --models "<exact_ollama_model_name>" \
  --judge-model "<exact_ollama_model_name>" \
  --output "../../artifacts/08_results/solution_validation/ollama_mcp_bench_single/<model_slug>/eval_results.json"
```

Capture stdout and stderr into:

```text
eval_stdout.txt
eval_stderr.txt
```

If the eval script uses different flags, inspect `eval_skill.py --help` and adapt. Record the exact final command.

## 15. Parsing And Metrics

Create:

```text
parsed_metrics.json
```

Extract at least:

```json
{
  "benchmark": "mcp_bench_single",
  "model": "<exact_ollama_model_name>",
  "train_n": 40,
  "test_n": 16,
  "construction": {
    "baseline_correct": null,
    "skill_correct": null,
    "baseline_acc": null,
    "skill_acc": null,
    "delta_acc": null,
    "repair_count": null,
    "regression_count": null,
    "net_gain": null,
    "skill_status": null
  },
  "held_out": {
    "baseline_correct": null,
    "skill_correct": null,
    "baseline_acc": null,
    "skill_acc": null,
    "delta_acc": null,
    "repair_count": null,
    "regression_count": null,
    "net_gain": null
  },
  "runtime": {
    "train_seconds": null,
    "eval_seconds": null
  },
  "evidence": {
    "config_path": "",
    "skill_repo_path": "",
    "verification_summary_path": "",
    "eval_results_path": "",
    "trace_inventory_path": ""
  }
}
```

Use `null` only when the raw files do not contain that value. Explain every `null` in `solution_validation_result.md`.

## 16. Decision Rules

Use these rules to assign the final solution-validation status.

### 16.1 `solution_validated`

All must be true:

- Train completed.
- Held-out eval completed.
- Skill artifact exists.
- Per-round traces exist.
- Held-out `skill_acc > baseline_acc`.
- Held-out `net_gain > 0`.
- No external LLM API was used.

### 16.2 `partially_solution_validated`

Use this if at least one of the following is true:

- Construction verification improves, but held-out eval does not.
- Held-out eval improves, but a non-critical trace or auxiliary artifact is missing.
- Pipeline runs end-to-end, but the result depends on hash embeddings or another reconstructed component.
- Pipeline runs end-to-end and produces parseable evidence, but improvement is too small or unstable for a stronger label.

### 16.3 `not_solution_validated`

Use this if:

- Train and eval complete, but skill performance is equal or worse than baseline.
- The generated skill is rejected/deprecated and held-out eval gives no positive evidence.

### 16.4 `failed_to_run`

Use this if:

- Ollama cannot serve the selected model.
- Train crashes.
- Eval crashes.
- Required files are not produced.

### 16.5 `inconclusive`

Use this if:

- The local model runs, but output formatting prevents meaningful scoring.
- Parser failures dominate the run.
- The raw evidence cannot distinguish model failure from skill failure.

## 17. Required Summary Report

Create:

```text
solution_validation_result.md
```

Use this exact structure:

```markdown
# Ollama MCP Bench Single Solution Validation

## Verdict

Status: <solution_validated | partially_solution_validated | not_solution_validated | failed_to_run | inconclusive>

One-sentence reason:

## What Was Tested

- Benchmark:
- Model:
- Dataset:
- Train size:
- Test size:
- SkillGen rounds:
- Embedding mode:
- External API usage:

## Deviations From Paper Reproduction

- ...

## Commands Run

### Probe

...

### Train

...

### Eval

...

## Results

| Split | Baseline acc | Skill acc | Delta | Net gain |
| --- | ---: | ---: | ---: | ---: |
| Construction |  |  |  |  |
| Held-out |  |  |  |  |

## Trace Preservation

- Config:
- Raw logs:
- Skill repo:
- Verification summary:
- Eval result:
- Per-round traces:

## Interpretation

Explain whether this result supports our solution strategy.

## Remaining Issues

List anything that still prevents broader full-matrix or cross-benchmark validation.
```

## 18. Full-Matrix Expansion After First Success

Only expand after one `mcp_bench_single` local run completes and produces a valid summary.

Recommended expansion order:

1. Repeat `mcp_bench_single` with the same Ollama model and a second seed.
2. Run one more installed Ollama model on `mcp_bench_single`.
3. Run a small benchmark with less adapter complexity, if available.
4. Run ALFWorld only after its adapter is ready and separately documented.
5. Run transfer tests only after base skill-generation evidence exists.

For each expansion, keep the same evidence structure and status labels.

## 19. What To Report Back To The Supervisor

The delegated agent should report:

- whether Ollama local endpoint worked
- exact selected model
- whether code patch was required and where
- whether embeddings were local
- whether train completed
- whether eval completed
- final status label
- construction metrics
- held-out metrics
- where raw logs and traces are stored
- whether this moves any previously blocked/not-testable verification path to testable

Do not only report a narrative. The report must point to files.

## 20. Minimal Handoff Prompt For Another Agent

Use this prompt if assigning the task to a fresh agent:

```text
You are working in /Users/jamesyuan/Developer/Github Repos (On Git)/AI4Research-B.

Your task is to execute the Ollama local solution-validation plan in logs/ollama_solution_validation_execution_manual_20260604.md.

Goal: use Codex as orchestrator and local Ollama as the benchmark LLM to test whether our reconstructed Phase 0 solution can turn previously blocked/not-testable SkillGen verification paths into executable, evidence-producing runs.

Important constraints:
- This is not paper claim reproduction. Use solution-validation statuses.
- Do not use external OpenAI/OpenRouter APIs.
- Do not install dependencies outside the project directory.
- Patch only phase_0/runs/skillgen_phase0_thorough_20260602/code/official/llm.py if needed.
- Record every deviation before or while making it.
- Preserve raw stdout/stderr, configs, eval outputs, generated skills, verification summaries, and per-round traces.
- Start with mcp_bench_single and one installed Ollama model.
- Stop before downloading new Ollama models unless user approval is explicit.

Deliver:
- solution_validation_result.md
- solution_validation_result.json
- parsed_metrics.json
- environment_manifest.md
- deviation_note.md
- trace_inventory.md
- raw train/eval/probe logs

Report back with file paths and the final status.
```

