# Environment Plan

Status: `blocked_until_human_approval_and_key_visibility`

## Dependency Isolation

All official-code dependencies should be installed under the current repository, specifically:

- virtual environment: `phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official/.venv/`
- uv cache: `phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official/.uv-cache/`

This satisfies the user's dependency-locality rule while allowing the Python interpreter itself to come from `mise`.

## Required External Resources

- Network access to PyPI or package indexes for dependency installation.
- Network access to OpenRouter/OpenAI endpoints for model and embedding calls.
- `OPENROUTER_API_KEY` and `OPENAI_API_KEY` visible to the command environment.
- Paid/tokenized LLM usage budget.

## Current Blocker

`OPENROUTER_API_KEY` and `OPENAI_API_KEY` are not visible in the current Codex shell environment. Values were not printed or inspected.
