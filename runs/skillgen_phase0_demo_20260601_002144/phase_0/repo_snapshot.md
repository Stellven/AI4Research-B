# Official Repository Snapshot

Status: `intake_complete_command_review_required`

- Official URL: `https://github.com/yccm/SkillGen`
- Local path: `runs/skillgen_phase0_demo_20260601_002144/code/official`
- Commit: `3c4537bb12ac287ceb1b5d410b491206089fdcb7`
- Commit date: `2026-05-08 19:36:46 +0200`
- Clone mode: `git clone --depth 1`

## Key Files

- `README.md`: official install, API key, quick-start, and dataset instructions
- `requirements.txt`: Python dependencies
- `config.yaml`: default models and Phase 0-relevant hyperparameters
- `main.py`: skill discovery entry point
- `eval_skill.py`: held-out skill evaluation entry point
- `data/aime/train.json`, `data/aime/test.json`: README quick-start data

## Instruction Mismatch Found

The README evaluation example uses `eval_skill.py --skill-path`, but the actual CLI parser in `eval_skill.py` requires `--skill-repo`. Running the README eval command exactly is expected to fail unless the repository is changed or the command is corrected. Any corrected eval command should be recorded as a human-approved deviation.
