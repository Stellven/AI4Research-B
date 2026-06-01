# Official Instructions Extracted From SkillGen Repo

Status: `command_review_required`

Source files inspected:

- `README.md`
- `requirements.txt`
- `config.yaml`
- `main.py`
- `eval_skill.py`

## Official Install Instruction

From README:

```bash
pip install -r requirements.txt
```

For this project, the dependency-local equivalent should install into a repo-local virtual environment:

```bash
python3 -m venv runs/skillgen_phase0_demo_20260601_002144/code/official/.venv
env UV_CACHE_DIR=runs/skillgen_phase0_demo_20260601_002144/code/official/.uv-cache uv pip install --python runs/skillgen_phase0_demo_20260601_002144/code/official/.venv/bin/python -r runs/skillgen_phase0_demo_20260601_002144/code/official/requirements.txt
```

## Required Environment Variables

From README:

```bash
export OPENROUTER_API_KEY="sk-or-..."
export OPENAI_API_KEY="sk-..."
```

Current shell visibility check: both names are currently `missing` in this Codex shell. Values were not printed.

## Official Quick Start

From README:

```bash
python main.py data/aime/train.json --config config.yaml
```

README evaluation example:

```bash
python eval_skill.py     --skill-path ./skill_output/<run>/skill.json     --test-data  data/aime/test.json     --config     config.yaml
```

## CLI Mismatch

The current `eval_skill.py` parser does not define `--skill-path`, `--test-data`, or `--config`. It defines `--skill-repo`, `--dataset`, `--n`, `--seed`, `--models`, and `--judge-model`. A working eval command likely needs the corrected CLI shape, but this should be approved as a deviation before execution.
