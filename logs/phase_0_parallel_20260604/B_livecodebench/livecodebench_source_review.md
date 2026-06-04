# LiveCodeBench Source Review

Status: `source_ready_needs_or_has_split`

## Source Identity

- Official source: `livecodebench/code_generation_lite`
- Official release: `release_v6`
- Paper held-out split: `test_release_v6`
- Local dataset: `code/official/data/livecodebench/release_v6_all.json`
- Dataset exists: `True`
- Adapter: `code/official/benchmarks/livecodebench_adapter.py`
- Adapter exists: `True`

## Local Dataset Shape

- Dataset ID: `livecodebench_release_v6`
- Task name: `livecodebench_release_v6_competitive_programming`
- Task type: `binary`
- Source total instances: `1055`

## Paper Table 3 Values

- Construction N: `50`
- Held-out test N: `150`
- Seed: `42`
- Note: Sampled from release v6; seed 42.

## Identity Basis

- Official SkillGen code includes benchmarks/livecodebench_adapter.py.
- Official preparation plan uses livecodebench/code_generation_lite with release_v6.
- The local release_v6_all.json is already a SkillGen TaskInstance wrapper.
