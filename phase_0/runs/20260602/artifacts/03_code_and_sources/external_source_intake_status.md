# External Source Intake Status

Observed external source intake and preparation status for SkillGen blocked targets

## Status Counts

- `prepared`: 5

## Tasks

### livecodebench

- Status: `prepared`
- Source: `livecodebench/code_generation_lite`
- Target exists: `True`
- Expected outputs:
  - `code/official/data/livecodebench/release_v6_all.json`: `True`
- Partial outputs:
  - `code/official/data/livecodebench/release_v6_all.json`

### mcp_bench_all

- Status: `prepared`
- Source: `Accenture/mcp-bench`
- Target exists: `True`
- Commit: `7a8eaeae83a842a2949080acc5473f65e1569daf`
- Expected outputs:
  - `code/official/data/mcp_bench_all/train_all_n40_seed42.json`: `True`
  - `code/official/data/mcp_bench_all/test_all_n16_seed42.json`: `True`

### socialmaze_upi

- Status: `prepared`
- Source: `xzx34/SocialMaze`
- Target exists: `True`
- Commit: `825ac19999e035a68dfe3ae6be32ac4554d2f841`
- Expected outputs:
  - `code/official/data/socialmaze_upi/train_n60_seed42.json`: `True`
  - `code/official/data/socialmaze_upi/test_n50_seed42.json`: `True`
- Partial outputs:
  - `code/official/data/socialmaze_upi_smoke/train_n1_seed42.json`
  - `code/official/data/socialmaze_upi_smoke/test_n1_seed42.json`

### tau_bench

- Status: `prepared`
- Source: `sierra-research/tau-bench`
- Target exists: `True`
- Commit: `59a200c6d575d595120f1cb70fea53cef0632f6b`
- Expected outputs:
  - `code/official/data/tau_bench/train_retail_n30_seed42.json`: `True`
  - `code/official/data/tau_bench/test_retail_n30_seed42.json`: `True`

### chemllmbench

- Status: `prepared`
- Source: `ChemFoundationModels/ChemLLMBench`
- Target exists: `True`
- Commit: `b8cfb59fe1bc8500c6916cdf00c12e457f6c0720`
- Expected outputs:
  - `code/official/data/chemllmbench`: `True`
