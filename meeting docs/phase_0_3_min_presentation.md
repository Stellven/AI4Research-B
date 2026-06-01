# Phase 0 Design, SkillGen Paper, And Current Progress

## 3-Minute Presentation Script

### 0:00-0:30 — What Phase 0 Is

Phase 0 is the research validation stage of AI4Research-B.

The goal is simple: given a research paper or research report plus official code, Phase 0 checks whether the official code can reproduce the paper's stated benchmark claim.

It is not a POC generator and it is not a paper summarizer. Its job is to create evidence:

```text
paper claim -> official code execution -> observed benchmark result -> comparison -> validation report
```

The final status should be explicit: `reproduced`, `partially_reproduced`, `not_reproduced`, `not_testable`, `failed_to_run`, `blocked`, or `out_of_scope`.

### 0:30-1:15 — Phase 0 Design

The design is file-first and contract-first.

Every major step writes visible artifacts into a run folder, so a human or future agent can inspect and resume the workflow without relying on chat history.

The core workflow is:

```text
intake
-> parse paper/report
-> extract claim and benchmark target
-> human claim review
-> intake official code
-> extract official commands
-> human command review
-> run install
-> run benchmark
-> parse result
-> compare claim
-> human result review
-> final validation report
```

The important design decision is that we keep quality gates lightweight. We do not put a heavy review after every step. Instead, we use cheap artifact checks most of the time, and only four formal gates:

- claim selection
- command execution
- result interpretation
- final report

This keeps the system practical while still protecting the risky transitions: choosing what to validate, running third-party code, interpreting benchmark evidence, and making the final conclusion.

### 1:15-2:05 — What The SkillGen Paper Is About

The current target paper is **"SkillGen: Verified Inference-Time Agent Skill Synthesis"**, arXiv `2605.10999v1`.

The paper argues that agent skills should not just be reusable prompts or summaries. They should be treated as interventions that must be verified before deployment.

SkillGen works by generating a skill from baseline agent trajectories, then testing whether that skill actually helps on paired examples.

The key comparison is:

```text
same task instance without skill
vs.
same task instance with SkillGen skill
```

The paper counts:

- repairs: baseline failed, skill succeeds
- regressions: baseline succeeded, skill fails

The main empirical claim we selected is that SkillGen improves average held-out accuracy for all eight evaluated base LLMs, with reported gains from `+3.27` to `+10.08` percentage points. The paper also reports that across 80 benchmark-split-model entries, 50 improve, 25 are unchanged, and 5 regress.

This paper is useful for Phase 0 because it forces us to support paired intervention claims, not just simple scalar metric comparisons.

### 2:05-2:50 — Current Progress

Current progress is at the preliminary design plus demo-validation stage.

Completed so far:

- Phase 0 design documents exist.
- The preliminary design now follows the original design checklist: goal, users, inputs/outputs, boundary conditions, workflow, artifacts, modules, contracts, tech stack, failure modes, quality gates, tests, observability, cost/performance, and safety.
- The SkillGen claim analysis document identifies the main claim, limitations, and recommended MVP validation target.
- A preliminary Python demo exists at `ai4research_b/phase0/skillgen_demo.py`.
- The demo parses `docs/SkillGen.pdf`, extracts the official code URL, extracts the main paired accuracy claim, writes Phase 0 artifacts, and produces a validation report.
- A generated run package exists under `runs/skillgen_phase0_demo_20260601_002144/`.
- The generated report currently marks the status as `blocked`, not reproduced, because official execution would require hosted LLM APIs, OpenRouter/provider routing, benchmark-specific assets, token costs, and human approval.
- One unit test exists for the demo, and it passes.

### 2:50-3:00 — Next Step

The next step is to move from the SkillGen-specific demo toward a reusable Phase 0 MVP:

```text
general schemas
-> reusable artifact store
-> generic run creator
-> claim/command/result contracts
-> fake fixture end-to-end test
```

After that, we can decide whether to attempt official SkillGen code execution, but only after reviewing the command plan, API requirements, dataset requirements, and expected cost.

