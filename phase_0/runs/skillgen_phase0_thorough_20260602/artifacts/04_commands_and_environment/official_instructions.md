# Official Instructions

Status: `extracted`

## Detected Files

- readme: `code/official/README.md`
- requirements: `code/official/requirements.txt`
- main: `code/official/main.py`
- eval: `code/official/eval_skill.py`

## CLI Flags

- main.py: `--config, --generate-scripts, --resume, --verbose-http`
- eval_skill.py: `--baseline-trajectories, --dataset, --drop-blank, --enable-execute-scripts, --enable-web-search, --judge-model, --keep-blank, --max-workers, --models, --n, --no-execute-scripts, --no-save-trajectories, --no-web-search, --output, --save-trajectories, --seed, --skill-id, --skill-repo`

## Notes

- Install source is `requirements.txt`.
- Training entrypoint is `main.py <dataset> --config <config>`.
- Evaluation entrypoint uses `eval_skill.py --skill-repo --dataset --n --seed --models --judge-model --output`.
- Deviation required: README eval flags differ from the current `eval_skill.py` parser.
