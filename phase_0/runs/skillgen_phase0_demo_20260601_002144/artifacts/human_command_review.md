# Human Command Review

Status: `required`

## Commands Awaiting Approval

```bash
python3 -m venv phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official/.venv
```

```bash
env UV_CACHE_DIR=phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official/.uv-cache uv pip install --python phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official/.venv/bin/python -r phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official/requirements.txt
```

```bash
cd phase_0/runs/skillgen_phase0_demo_20260601_002144/code/official && .venv/bin/python main.py ../../artifacts/smoke_data/aime_train_n8_seed42.json --config ../../artifacts/skillgen_aime_smoke_config.yaml
```

Eval command will be filled in after training creates a timestamped skill output directory. It will use the current CLI's `--skill-repo` flag because the README eval flags do not match the code.

## Risks

- Network access and paid API usage.
- API keys must be visible to the process environment.
- The smoke config and subset are a cost-control deviation, not a full paper reproduction.
- Official dependency installation may fail on Python/package compatibility.
