# Canonical Benchmark Source Status

Canonical benchmark source fetch status for paper-named sources not fully covered by SkillGen official checkout

## Status Counts

- `canonical_source_fetched_not_skillgen_ready`: 1
- `canonical_source_fetched_skillgen_data_ready`: 1

## Sources

| Source | Status | Target | Commit | Blockers |
| --- | --- | --- | --- | --- |
| `alfworld` | `canonical_source_fetched_not_skillgen_ready` | `code/official/benchmarks/external/alfworld` | `aaba6870f86c5be6a08a491f32a50b906227bc3e` | Canonical ALFWorld code is fetched, but SkillGen has no ALFWorld adapter in the current checkout.; No paper-matching IOD/OOD train/test JSON split has been produced in SkillGen TaskInstance format.; ALFWorld environment/data installation may require additional resources and a separate human-approved environment plan. |
| `scienceworld` | `canonical_source_fetched_skillgen_data_ready` | `code/official/external/scienceworld` | `f6d8f5ec41eadfdcad23cc3ab097f0903dc1378b` | none |
