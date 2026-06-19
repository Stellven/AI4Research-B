# External Source Intake Plan

External source intake plan for currently actionable SkillGen blocked targets

Storage rule: All cloned repositories, generated datasets, and caches must remain inside the project/run directory.

## Tasks

### livecodebench

- Status: `pending_source_intake`
- Source: `livecodebench/code_generation_lite`
- Source type: `huggingface_dataset`
- Target: `code/official/data/livecodebench`
- Requires network: `True`
- Requires API: `False`
- Prepare command(s):
  - `code/official$ .venv/bin/python scripts/prepare_benchmarks.py --benchmark livecodebench --livecodebench-version release_v6 --n 0 -o data/livecodebench/release_v6_all.json`
- Notes:
  - Official script currently creates one dataset file; train/test splitting still needs a contract.

### mcp_bench_all

- Status: `pending_source_intake`
- Source: `Accenture/mcp-bench`
- Source type: `git_repo`
- Target: `code/official/benchmarks/external/mcp-bench`
- Requires network: `True`
- Requires API: `False`
- Clone command: `git clone --depth 1 https://github.com/Accenture/mcp-bench.git code/official/benchmarks/external/mcp-bench`
- Prepare command(s):
  - `code/official$ .venv/bin/python scripts/prepare_mcp_bench.py --split all --train-n 40 --test-n 16 --out-dir data/mcp_bench_all`
- Notes:
  - Uses existing single-split train/test sizes as a first all-split preparation contract.

### socialmaze_upi

- Status: `pending_source_intake`
- Source: `xzx34/SocialMaze`
- Source type: `git_repo_or_official_generation`
- Target: `code/official/benchmarks/external/social-maze or code/official/data/socialmaze/upi`
- Requires network: `True`
- Requires API: `True`
- Clone command: `git clone --depth 1 https://github.com/xzx34/SocialMaze code/official/benchmarks/external/social-maze`
- Prepare command(s):
  - `code/official$ .venv/bin/python scripts/prepare_socialmaze.py upi --pool-size 120 --train-n 60 --test-n 50 --variant persona --out-dir data/socialmaze_upi`
- Notes:
  - If shipped UPI data is insufficient, the official script will generate more examples through an LLM.

### tau_bench

- Status: `pending_source_intake`
- Source: `sierra-research/tau-bench`
- Source type: `git_repo_or_package`
- Target: `code/official/benchmarks/external/tau-bench`
- Requires network: `True`
- Requires API: `False`
- Clone command: `git clone --depth 1 https://github.com/sierra-research/tau-bench code/official/benchmarks/external/tau-bench`
- Prepare command(s):
  - `code/official$ .venv/bin/python scripts/prepare_tau_bench.py --domain retail --train-n 30 --test-n 30 --out-dir data/tau_bench`

### chemllmbench

- Status: `pending_source_intake`
- Source: `ChemFoundationModels/ChemLLMBench`
- Source type: `git_repo`
- Target: `code/official/external/chemllmbench`
- Requires network: `True`
- Requires API: `False`
- Clone command: `git clone --depth 1 https://github.com/ChemFoundationModels/ChemLLMBench.git code/official/external/chemllmbench`
- Prepare command(s):
  - `code/official$ .venv/bin/python scripts/prepare_chemllmbench.py --task all --train-n 30 --test-n 10 --out-dir data/chemllmbench`
