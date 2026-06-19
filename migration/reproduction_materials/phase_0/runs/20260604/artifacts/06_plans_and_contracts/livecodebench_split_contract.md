# LiveCodeBench Split Contract

Status: `ready_for_execution`

## Paper Contract

- Benchmark: `LiveCodeBench`
- Held-out split: `test_release_v6`
- Source release: `release_v6`
- Construction N: `50`
- Held-out test N: `150`
- Seed: `42`

## Source And Outputs

- Source dataset: `code/official/data/livecodebench/release_v6_all.json`
- Construction train: `code/official/data/livecodebench/train_release_v6_n50_seed42.json`
- Held-out test: `code/official/data/livecodebench/test_release_v6_n150_seed42.json`
- Manifest: `code/official/data/livecodebench/split_release_v6_n50_n150_seed42_manifest.json`

## Split Rule

- Use the source order in release_v6_all.json as the canonical pool order.
- Use random.Random(42).sample(range(total_instances), 200).
- Assign the first 50 sampled indices to construction and the next 150 sampled indices to held-out test.
- Write output instances in source-file order within each split to keep files auditable.
- Do not overwrite release_v6_all.json.

## Deviation Classification

`paper_matching_inferred_split`

The paper gives release_v6/test_release_v6, construction/test sizes, and seed 42, but does not publish exact LiveCodeBench instance IDs in the local artifacts.

## Human Gate

- Confirm the inferred split rule is acceptable for reconstructed Table 1 execution.
- Confirm generated train/test instance IDs in the manifest.
- Confirm model-route and paid-API approval before executing the benchmark.
