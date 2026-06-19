# Date Split Reorganization

Date: 2026-06-10

The Phase 0 SkillGen evidence package was reorganized so generated evidence lives under the directory matching its local generation date.

Date directories now present:

- `phase_0/runs/20260602/`
- `phase_0/runs/20260603/`
- `phase_0/runs/20260604/`
- `phase_0/runs/20260605/`
- `phase_0/runs/20260606/`
- `phase_0/runs/20260607/`
- `phase_0/runs/20260610/`

Scope of the split:

- Regular files under `artifacts/`, `outputs/`, `integration/`, and `playback/` were moved by local filesystem modification date.
- `integration/pipeline_run_log.jsonl` was split by each JSONL record timestamp because the original file contained events from multiple dates.
- Original inputs remain under the intake date. `phase_0/runs/20260602/input/paper.pdf` keeps its original source timestamp.
- `phase_0/runs/20260602/code/official/` remains intact as the runnable official-code checkout. It was not split by file timestamp.

Verification after reorganization:

- Generated evidence outside `code/` and the original paper input has zero date-folder mismatches.
- Compatibility symlinks were kept only when they resolve inside the same date directory.
