# AI4Research Project Understanding

This file captures the current working understanding of the AI4Research project for future agents and contributors. It is based on the project notes in:

- `5.21 Meeting Notes.txt`
- `AI4Research workflow.txt`
- `5.12 Project Overview.txt`
- `5.19 ai4research flow.txt`

## Core Purpose

AI4Research is a multi-agent research automation system. Its input is a user-provided topic, usually framed as an existing technical problem or research direction. Its output is not only a written research artifact, but a working proof of concept that validates a proposed solution derived from the research.

The intended end-to-end flow is:

1. Accept a topic or problem from the user.
2. Research the current state of the field and identify gaps, drawbacks, or opportunities for improvement.
3. Generate a research report or paper containing candidate proposals.
4. Convert the selected proposal into formal requirements.
5. Use human-in-the-loop review to confirm or revise the requirements.
6. Generate a research design and coding plan.
7. Build a POC demo using AI coding agents.
8. Run benchmarks and tests against the POC.
9. Have review agents assess whether the POC validates the proposed solution.
10. Package the final model, demo, or research output for release, ideally to the open-source community.

In short: AI4Research turns a topic into research, turns research into a design, turns the design into a POC, and then validates whether the POC actually supports the research claim.

## Project Philosophy

The project is built around the idea of using AI to manage, develop, and optimize AI systems. Agents should not only produce outputs; they should help govern the process, critique intermediate artifacts, create reusable skills, validate work, and improve the system over time.

Fast iteration matters, but the project notes repeatedly emphasize that the design must be solid before implementation scales. The system should support open-source components wherever available, while still allowing integration with APIs, MCP tools, commercial software, and external services when they provide useful capabilities.

The system should always allow human intervention. AI agents can generate reports, requirements, designs, code, tests, and evaluations, but humans remain responsible for key decisions such as choosing final requirements and approving demo direction.

## Main Pipeline

The project uses a V-model-inspired pipeline:

- Requirements map to user acceptance tests.
- Design maps to integration tests.
- Code maps to unit tests.

This means validation should be planned early, not treated as an afterthought. When agents generate requirements, they should also help define what successful acceptance looks like. When agents generate designs, they should also define integration-level checks. When agents generate code, they should also create unit tests.

The expected workflow is:

1. **Topic intake**
   - Understand the user's topic, problem, intent, and expected audience.
   - Different users may need different research depth, framing, or deliverables.
   - A planner agent may be needed because the domain is hard to pre-classify.

2. **Research and technology scan**
   - Search online sources, databases, papers, and existing open-source projects.
   - Identify latest progress under the topic.
   - Analyze current drawbacks, unresolved issues, and improvement opportunities.
   - Compare competitors or related systems when relevant.

3. **Requirement generation**
   - Generate roughly five or six candidate research requirements.
   - Requirements should address the discovered gap or issue.
   - Requirements may be represented in SysML v2 or another structured requirement form.
   - Output should include a `requirement.md` or equivalent artifact.
   - Human-in-the-loop confirmation is required here.

4. **Research design**
   - After requirements are confirmed, agents generate a research design.
   - The design should explain the proposed solution, the POC scope, and the verification strategy.
   - Agents should summarize prior analysis into a concise coding plan while preserving key reasoning.
   - Output should include a `design.md` or equivalent artifact.

5. **POC implementation**
   - AI coding agents implement the demo or prototype.
   - The implementation should be constrained by the confirmed requirements and design.
   - The POC should be practical enough to test the research proposal, not merely illustrative.

6. **Benchmarking and validation**
   - Agents run benchmark tests against the POC.
   - The system should be able to spin up isolated test environments, potentially including Docker.
   - A validation or review agent assesses benchmark results and decides whether the demo works.
   - A dedicated POC validation skill is likely needed.

7. **Release**
   - If the POC validates the solution, the final model, code, or demo can be prepared for open-source release.

## Agent Architecture

AI4Research should be treated as a multi-agent environment, with Codex serving as both a development environment and an execution environment for agents.

Likely agent roles include:

- **Intent/query understanding agent**: interprets the user's topic, goals, audience, and constraints.
- **Planner agent**: decomposes the topic into subtasks and decides what research path to follow.
- **Research/search agent**: scans online sources, databases, papers, and open-source projects.
- **Analysis agent**: identifies drawbacks, gaps, and possible improvements in the current state of the field.
- **Requirement agent**: converts findings into structured requirements.
- **Critique agent**: checks whether outputs satisfy the user's demand and project constraints.
- **Design agent**: turns confirmed requirements into a research design and POC plan.
- **Coding agent**: builds the POC demo.
- **Benchmark agent**: runs tests, benchmarks, and possibly Dockerized evaluations.
- **Review agent**: evaluates benchmark results and determines whether the POC validates the proposed solution.
- **Skill governance agent**: creates, audits, tests, and improves reusable skills.

The notes suggest that Codex should not just be used to write code. It should be part of the multi-agent operating environment where agents create files, manage versions, run tests, generate artifacts, and build skills.

## Filesystem-Centered Operation

The project should lean into a filesystem-based workflow. Important intermediate outputs should become durable files that agents and humans can inspect, version, modify, and reuse.

Important artifacts may include:

- `soul.md`: a possible user profile or intent model used to understand user needs.
- `requirement.md`: confirmed requirements, ideally structured and testable.
- `design.md`: research design, solution plan, POC scope, and verification strategy.
- Skill packages: reusable operational knowledge created from successful workflows.
- Evidence records: citations, source links, benchmark outputs, and reasoning traces.
- Test artifacts: acceptance tests, integration tests, unit tests, and benchmark reports.

Git version control is considered necessary because the pipeline produces many intermediate artifacts and should support iteration, human review, and rollback.

## Skills and Skill Governance

Skills are central to the project. They are the mechanism for transferring human knowledge into agents and making useful workflows reusable.

AI4Research should be able to:

- Create a skill for repeated tasks.
- Convert documents or methods into skill packages.
- Test whether a skill works.
- Audit skill quality.
- Govern skill lifecycle over time.
- Reuse skills across research, design, implementation, validation, and reporting tasks.

The project notes point toward model-driven skill engineering and harness engineering. Skills should not be trusted only because they sound good. They need practical test cases, evaluation hooks, and quality checks.

Skill governance can involve formalization, but the notes favor testing as the practical method: write test cases and prove skills through behavior.

Meta-skills are also important. These are skills that help audit, improve, or evolve other skills. The project should support self-improvement, but with safeguards and evaluation.

## Harnesses, World Models, and SysML v2

A recurring idea in the notes is that LLM output is unstable, so the system needs semantic harnesses and world models to constrain and verify agent behavior.

SysML v2 is considered useful because it can define requirements, constraints, rules, logic, and world models in a structured way. It may serve as:

- A semantic harness for the multi-agent system.
- A way to define ground-truth constraints.
- A representation for requirements.
- A verification artifact for checking whether outputs satisfy the model.

However, SysML v2 is also considered heavy. The project may need a pragmatic layer that captures the benefits of formal modeling without making the workflow too cumbersome.

The larger principle is that agents need explicit constraints. They should not operate only from freeform prompts. The system should define terms, metadata, evidence, requirements, and validation rules in a way agents can reference and tools can check.

## Evaluation Layer

Evaluation is not a single final step. It should be layered throughout the project.

Evaluation should cover:

- Whether the user intent was understood correctly.
- Whether the research scan is current and well-supported.
- Whether generated requirements address the real issue.
- Whether the design follows from the requirements.
- Whether the POC implements the design.
- Whether unit, integration, and acceptance tests pass.
- Whether benchmark results actually support the research claim.
- Whether skills used in the process are reliable and reusable.

The critique/review function is important. Agents should assess whether outputs satisfy user demand, project constraints, and benchmark criteria. Evidence such as citations, benchmark logs, test results, and rationale should be preserved.

## Human-in-the-Loop Points

The system should allow humans to jump in at any time, but some points explicitly require human decision:

- Confirming generated requirements.
- Choosing among proposed research directions.
- Approving the POC design.
- Reviewing whether the final demo validates the research claim.
- Deciding what is ready for release.

Human intervention should not break the pipeline. The framework should make intermediate artifacts editable and resumable.

## Key Design Concerns

The notes identify several risks and concerns:

- Existing multi-agent frameworks such as OpenClaw and Hermes may be complex.
- Multi-agent systems may burn many tokens.
- The project needs visibility into agent reasoning, planning, and process.
- It is hard to pre-determine the topic domain, so planning and routing matter.
- The system needs a whole-picture architecture, including Codex's role.
- Each layer should be specified clearly: data layer, evaluation layer, skills layer, agent layer, and artifact layer.
- Persistent memory may be needed to preserve context without overloading prompts.
- The framework should adapt to MCP and external tools.

## Target Users

The system may serve:

- Individual researchers or builders.
- Internal teams.
- Enterprises.

The expected near-term user seems to be a team workflow where human review and reusable skills matter.

## Current Working Definition

AI4Research is a Codex-centered, filesystem-first, multi-agent research engineering framework. It takes a topic, researches the state of the field, generates and validates requirements, designs a candidate solution, builds a POC, benchmarks it, and uses structured evaluation to determine whether the POC supports the research proposal.

The defining challenge is not simply generating a paper or demo. The project must govern the full lifecycle from ambiguous topic to validated artifact, with reusable skills, human checkpoints, evidence tracking, formal or semi-formal constraints, and tests mapped to each phase of the V-model.
