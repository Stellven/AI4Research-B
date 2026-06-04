# ALFWorld Group A Implementation Notes

Group: A - ALFWorld Contract / Adapter.

Status: `contract_artifacts_written_and_automation_detection_added`

## Code Change

`ai4research_b/phase0/skillgen_automation.py` now detects the four Group A ALFWorld contract documents:

- `alfworld_source_review.md`
- `alfworld_adapter_contract.md`
- `alfworld_split_contract.md`
- `alfworld_deviation_note.md`

Detection supports both project-level group logs and run-local artifact paths.

When canonical ALFWorld source exists and all four documents are present, the benchmark execution plan reports ALFWorld IOD/OOD as:

```text
ready_for_reconstructed_execution
```

This status is intentionally not counted as `ready_for_execution` for Table 1 entries. ALFWorld still requires data download, adapter implementation, generated split files, smoke evidence, and human approval before benchmark execution.

## Test Coverage

`tests/test_skillgen_automation.py` includes a focused test that:

1. Creates a fake ALFWorld canonical source under a temporary run.
2. Writes run-local Group A contract docs.
3. Builds the benchmark execution plan.
4. Verifies ALFWorld IOD/OOD status changes to `ready_for_reconstructed_execution`.
5. Verifies Table 1 ready entry count remains zero.
6. Verifies transfer planning sees the updated ALFWorld OOD status.

## Remaining Work

Next implementation work belongs to a follow-up execution/adapter task:

- download ALFWorld data inside the run directory,
- implement `metadata.benchmark == "alfworld"` runner behavior,
- generate audited SkillGen train/test JSON files,
- run a smoke ALFWorld target and preserve logs.
