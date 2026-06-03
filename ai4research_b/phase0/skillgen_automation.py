"""SkillGen-specific Phase 0 automation.

This module is intentionally scoped to the SkillGen paper and the AIME smoke
target. The artifact boundaries are kept generic so the code can later be split
into reusable Phase 0 components.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai4research_b.phase0.skillgen_demo import (
    append_jsonl,
    extract_claims,
    hardcoding_disclosures,
    read_pdf_text,
    run_demo,
    write_json,
    write_text,
)


OFFICIAL_REPO_URL = "https://github.com/yccm/SkillGen"
TARGET_ID = "skillgen_aime_smoke"
STATUS_BLOCKED = "blocked"
STATUS_FAILED_TO_RUN = "failed_to_run"
STATUS_NOT_TESTABLE = "not_testable"
STATUS_NOT_REPRODUCED = "not_reproduced"
STATUS_REPRODUCED = "reproduced"
STATUS_PARTIALLY_REPRODUCED = "partially_reproduced"
STATUS_READY_FOR_EXECUTION = "ready_for_execution"
STATUS_ROUTE_RESOLUTION_REQUIRED = "route_resolution_required"

PAPER_MODEL_NAMES = [
    "Gemma-4-26B",
    "Llama-3.1-8B",
    "Mistral-Nemo",
    "Qwen-2.5-7B",
    "Claude-Haiku-4.5",
    "GPT-5.4-Nano",
    "GPT-5.4-Mini",
    "Grok-4-Fast",
]

PAPER_MODEL_ROUTE_RESOLUTIONS = {
    "Gemma-4-26B": {
        "provider_route_id": "google/gemma-4-26b-a4b-it",
        "status": "route_resolved_equivalent",
        "basis": "OpenRouter current catalog exposes Google Gemma 4 26B A4B; treated as the current executable equivalent of the paper display name.",
    },
    "Llama-3.1-8B": {
        "provider_route_id": "meta-llama/llama-3.1-8b-instruct",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact family/size instruction route.",
    },
    "Mistral-Nemo": {
        "provider_route_id": "mistralai/mistral-nemo",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact named route.",
    },
    "Qwen-2.5-7B": {
        "provider_route_id": "qwen/qwen-2.5-7b-instruct",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact family/size instruction route.",
    },
    "Claude-Haiku-4.5": {
        "provider_route_id": "anthropic/claude-haiku-4.5",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact named route.",
    },
    "GPT-5.4-Nano": {
        "provider_route_id": "openai/gpt-5.4-nano",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact named route; also used by the existing smoke config.",
    },
    "GPT-5.4-Mini": {
        "provider_route_id": "openai/gpt-5.4-mini",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact named route; also used by the existing smoke config.",
    },
    "Grok-4-Fast": {
        "provider_route_id": "x-ai/grok-4.3",
        "status": "route_resolved_equivalent",
        "basis": "OpenRouter current catalog did not expose Grok-4-Fast; x-ai/grok-4.3 is recorded as the closest current Grok 4 series executable route.",
    },
    "GPT-OSS-20B": {
        "provider_route_id": "openai/gpt-oss-20b",
        "status": "route_resolved_exact",
        "basis": "OpenRouter current catalog exact named route.",
    },
}

TABLE1_REQUIRED_ROWS = [
    "alfworld_iod",
    "alfworld_ood",
    "livecodebench",
    "mcp_bench_all",
    "mcp_bench_single",
    "mind2web",
    "pubmedqa",
    "scienceworld",
    "socialmaze_fts",
    "socialmaze_upi",
]

TRANSFER_MODEL_NAMES = [
    "Qwen-2.5-7B",
    "Llama-3.1-8B",
    "GPT-OSS-20B",
    "GPT-5.4-Nano",
    "GPT-5.4-Mini",
    "Grok-4-Fast",
]

TRANSFER_BENCHMARK_ROWS = [
    "alfworld_ood",
    "scienceworld",
    "mind2web",
    "socialmaze_fts",
]

TOKEN_COST_BENCHMARKS = [
    {
        "paper_name": "ScienceWorld",
        "target_id": "scienceworld",
        "paper_train_mtok": 2.2,
        "paper_base_tokens_per_call": 1630,
        "paper_skill_tokens_per_call": 1977,
    },
    {
        "paper_name": "PubMedQA",
        "target_id": "pubmedqa",
        "paper_train_mtok": 2.7,
        "paper_base_tokens_per_call": 1173,
        "paper_skill_tokens_per_call": 2429,
    },
    {
        "paper_name": "Mind2Web",
        "target_id": "mind2web",
        "paper_train_mtok": 5.2,
        "paper_base_tokens_per_call": 4482,
        "paper_skill_tokens_per_call": 5919,
    },
    {
        "paper_name": "MCPBench",
        "target_id": "mcp_bench",
        "paper_train_mtok": 7.5,
        "paper_base_tokens_per_call": 4847,
        "paper_skill_tokens_per_call": 6000,
    },
    {
        "paper_name": "tau-Bench",
        "target_id": "tau_bench_retail",
        "paper_train_mtok": 10.2,
        "paper_base_tokens_per_call": 5813,
        "paper_skill_tokens_per_call": 6358,
    },
]

CANONICAL_BENCHMARK_SOURCES = {
    "alfworld": {
        "paper_benchmark": "ALFWorld",
        "source": "alfworld/alfworld",
        "source_url": "https://github.com/alfworld/alfworld.git",
        "target_path": "code/official/benchmarks/external/alfworld",
        "identity_basis": "Paper Table 1 and Figure 4 name ALFWorld; this is the canonical public ALFWorld benchmark repository.",
        "skillgen_compatibility_status": "missing_skillgen_adapter_and_iod_ood_split_contract",
    },
    "scienceworld": {
        "paper_benchmark": "ScienceWorld",
        "source": "allenai/ScienceWorld",
        "source_url": "https://github.com/allenai/ScienceWorld.git",
        "target_path": "code/official/external/scienceworld",
        "identity_basis": "SkillGen official prepare_scienceworld.py records source allenai/ScienceWorld.",
        "skillgen_compatibility_status": "bundled_data_already_ready_for_skillgen_execution_plan",
    },
}

BUNDLED_DATASET_MAP = {
    "aime": "data/aime",
    "mcp_bench_single": "data/mcp_bench",
    "mind2web": "data/mind2web",
    "pubmedqa": "data/pubmedqa",
    "scienceworld": "data/scienceworld",
    "socialmaze_fts": "data/socialmaze",
    "toolbench": "data/toolbench",
}

EXTERNAL_SOURCE_CANDIDATES = {
    "livecodebench": [
        {
            "source_type": "huggingface_dataset",
            "source": "livecodebench/code_generation_lite",
            "source_url": "https://huggingface.co/datasets/livecodebench/code_generation_lite",
            "target_location": "code/official/data/livecodebench",
            "intake": (
                "Use code/official/scripts/prepare_benchmarks.py with "
                "--benchmark livecodebench and the paper-matching version tag."
            ),
            "identity_basis": (
                "Official prepare_benchmarks.py names hf_id "
                "livecodebench/code_generation_lite and imports the LiveCodeBench adapter."
            ),
            "official_evidence_paths": [
                "scripts/prepare_benchmarks.py",
                "benchmarks/livecodebench_adapter.py",
            ],
        }
    ],
    "mcp_bench_all": [
        {
            "source_type": "git_repo",
            "source": "Accenture/mcp-bench",
            "source_url": "https://github.com/Accenture/mcp-bench.git",
            "target_location": "code/official/benchmarks/external/mcp-bench",
            "intake": (
                "Clone under code/official/benchmarks/external/mcp-bench, then run "
                "code/official/scripts/prepare_mcp_bench.py --split all with "
                "paper-matching train/test sizes."
            ),
            "identity_basis": (
                "Official README names Accenture/mcp-bench and official "
                "prepare_mcp_bench.py supports --split all; the current adapter resolves "
                "the executable path under benchmarks/external."
            ),
            "official_evidence_paths": [
                "README.md",
                "scripts/prepare_mcp_bench.py",
                "benchmarks/mcp_bench_adapter.py",
            ],
        }
    ],
    "socialmaze_upi": [
        {
            "source_type": "git_repo_or_official_generation",
            "source": "xzx34/SocialMaze",
            "source_url": "https://github.com/xzx34/SocialMaze",
            "target_location": "code/official/benchmarks/external/social-maze or code/official/data/socialmaze/upi",
            "intake": (
                "Use code/official/scripts/prepare_socialmaze.py upi. The script can "
                "use shipped SocialMaze material or generate/cache a UPI pool under "
                "the requested output directory."
            ),
            "identity_basis": (
                "Official socialmaze adapter/preparation script records source "
                "xzx34/SocialMaze and includes a UPI subcommand; the adapter resolves "
                "shipped SocialMaze data under benchmarks/external."
            ),
            "official_evidence_paths": [
                "scripts/prepare_socialmaze.py",
                "benchmarks/socialmaze_adapter.py",
            ],
        }
    ],
    "tau_bench": [
        {
            "source_type": "git_repo_or_package",
            "source": "sierra-research/tau-bench",
            "source_url": "https://github.com/sierra-research/tau-bench",
            "target_location": "code/official/benchmarks/external/tau-bench",
            "intake": (
                "Place tau-bench under code/official/benchmarks/external/tau-bench, then run "
                "code/official/scripts/prepare_tau_bench.py for the paper-matching domain and split."
            ),
            "identity_basis": (
                "Official prepare_tau_bench.py records source sierra-research/tau-bench "
                "and the current adapter resolves tau-bench under benchmarks/external."
            ),
            "official_evidence_paths": [
                "scripts/prepare_tau_bench.py",
                "benchmarks/tau_bench_adapter.py",
            ],
        }
    ],
    "chemllmbench": [
        {
            "source_type": "git_repo",
            "source": "ChemFoundationModels/ChemLLMBench",
            "source_url": "https://github.com/ChemFoundationModels/ChemLLMBench.git",
            "target_location": "code/official/external/chemllmbench",
            "intake": (
                "Clone under code/official/external/chemllmbench, then run "
                "code/official/scripts/prepare_chemllmbench.py for the paper-matching tasks."
            ),
            "identity_basis": (
                "Official prepare_chemllmbench.py records source "
                "ChemFoundationModels/ChemLLMBench and prints the matching clone command."
            ),
            "official_evidence_paths": [
                "scripts/prepare_chemllmbench.py",
                "benchmarks/chemllmbench_adapter.py",
            ],
        }
    ],
    "toolbench": [
        {
            "source_type": "git_repo",
            "source": "OpenBMB/ToolBench",
            "source_url": "https://github.com/OpenBMB/ToolBench",
            "target_location": "code/official/benchmarks/external/ToolBench",
            "intake": (
                "Clone under code/official/benchmarks/external/ToolBench, then run "
                "code/official/scripts/prepare_toolbench.py with the paper-matching subset."
            ),
            "identity_basis": (
                "Official README and ToolBench adapter name OpenBMB/ToolBench; the "
                "current adapter resolves the executable path under benchmarks/external."
            ),
            "official_evidence_paths": [
                "README.md",
                "scripts/prepare_toolbench.py",
                "benchmarks/toolbench_adapter.py",
            ],
        }
    ],
}


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    input_dir: Path
    artifacts_dir: Path
    outputs_dir: Path
    code_dir: Path
    official_dir: Path
    integration_dir: Path
    playback_dir: Path
    raw_dir: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def paths_for(run_dir: Path) -> RunPaths:
    return RunPaths(
        run_dir=run_dir,
        input_dir=run_dir / "input",
        artifacts_dir=run_dir / "artifacts",
        outputs_dir=run_dir / "outputs",
        code_dir=run_dir / "code",
        official_dir=run_dir / "code" / "official",
        integration_dir=run_dir / "integration",
        playback_dir=run_dir / "playback",
        raw_dir=run_dir / "artifacts" / "raw_benchmark_outputs" / TARGET_ID,
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_event(run_dir: Path, step: str, status: str, **extra: Any) -> None:
    event = {"step": step, "status": status, "timestamp": utc_now()}
    event.update(extra)
    append_jsonl(paths_for(run_dir).integration_dir / "pipeline_run_log.jsonl", event)


def append_decision(run_dir: Path, decision: str, **extra: Any) -> None:
    event = {"decision": decision, "timestamp": utc_now()}
    event.update(extra)
    append_jsonl(paths_for(run_dir).playback_dir / "decision_trace.jsonl", event)


def rel(path: Path, root: Path) -> str:
    path_abs = path.resolve()
    root_abs = root.resolve()
    try:
        return path_abs.relative_to(root_abs).as_posix()
    except ValueError:
        return os.path.relpath(path_abs, root_abs)


def project_root_from(run_dir: Path) -> Path:
    current = run_dir.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "ai4research_b").exists():
            return candidate
    return Path.cwd()


def load_dotenv(project_root: Path) -> dict[str, str]:
    env_path = project_root / ".env"
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def command_env(run_dir: Path, command_env_values: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env.update(load_dotenv(project_root_from(run_dir)))
    if command_env_values:
        env.update(command_env_values)
    return env


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def official_code_present(official_dir: Path) -> bool:
    return (official_dir / "README.md").exists() and (official_dir / "main.py").exists()


def copy_official_source(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Official source not found: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        return
    ignore = shutil.ignore_patterns(".venv", ".uv-cache", "__pycache__", "*.pyc")
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=ignore)
        else:
            shutil.copy2(item, target)


def clone_official_repo(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and any(destination.iterdir()):
        return
    result = subprocess.run(
        ["git", "clone", OFFICIAL_REPO_URL, str(destination)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git clone failed")


def code_intake(run_dir: Path, official_source: Path | None = None, allow_clone: bool = False) -> dict[str, Any]:
    paths = paths_for(run_dir)
    status = "missing_official_code"
    clone_error = None

    if official_source is not None:
        copy_official_source(official_source, paths.official_dir)

    if not official_code_present(paths.official_dir) and allow_clone:
        try:
            clone_official_repo(paths.official_dir)
        except RuntimeError as exc:
            clone_error = str(exc)

    if official_code_present(paths.official_dir):
        status = "intake_complete"

    commit = git_value(["rev-parse", "HEAD"], paths.official_dir) if status == "intake_complete" else None
    branch = git_value(["rev-parse", "--abbrev-ref", "HEAD"], paths.official_dir) if status == "intake_complete" else None
    tracked_files = git_value(["ls-files"], paths.official_dir) if status == "intake_complete" else None
    files = sorted(tracked_files.splitlines()) if tracked_files else []
    if status == "intake_complete" and not files:
        files = sorted(rel(path, paths.official_dir) for path in paths.official_dir.rglob("*") if path.is_file())

    manifest = {
        "schema_version": "0.3",
        "status": status,
        "official_repo_url": OFFICIAL_REPO_URL,
        "local_path": "code/official",
        "commit": commit,
        "branch": branch,
        "clone_error": clone_error,
        "key_files": [file for file in files if file in {"README.md", "requirements.txt", "config.yaml", "main.py", "eval_skill.py"}],
        "file_count": len(files),
    }
    write_json(paths.artifacts_dir / "code_manifest.json", manifest)

    if status == "intake_complete":
        snapshot_lines = [
            "# Repository Snapshot",
            "",
            "Status: `intake_complete`",
            "",
            f"- Repository: `{OFFICIAL_REPO_URL}`",
            f"- Commit: `{commit or 'unknown'}`",
            f"- Branch: `{branch or 'unknown'}`",
            "- Local path: `code/official`",
            "",
            "## Key Files",
            "",
        ]
        for key_file in manifest["key_files"]:
            snapshot_lines.append(f"- `{key_file}`")
    else:
        snapshot_lines = [
            "# Repository Snapshot",
            "",
            "Status: `missing_official_code`",
            "",
            f"Official code is not present at `{paths.official_dir}`.",
        ]
        if clone_error:
            snapshot_lines.extend(["", f"Clone error: `{clone_error}`"])
    write_text(paths.artifacts_dir / "repo_snapshot.md", "\n".join(snapshot_lines))
    append_event(run_dir, "official_code_intake", status, artifact="artifacts/code_manifest.json")
    return manifest


def extract_cli_flags(script_path: Path) -> list[str]:
    if not script_path.exists():
        return []
    text = script_path.read_text(encoding="utf-8", errors="replace")
    flags = re.findall(r"add_argument\(\s*['\"](--[A-Za-z0-9][A-Za-z0-9_-]*)['\"]", text)
    return sorted(set(flags))


def extract_official_instructions(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    readme = paths.official_dir / "README.md"
    requirements = paths.official_dir / "requirements.txt"
    main_py = paths.official_dir / "main.py"
    eval_py = paths.official_dir / "eval_skill.py"

    eval_flags = extract_cli_flags(eval_py)
    main_flags = extract_cli_flags(main_py)
    readme_text = readme.read_text(encoding="utf-8", errors="replace") if readme.exists() else ""
    readme_eval_mismatch = "--skill-path" in readme_text and "--skill-repo" in eval_flags

    instructions = {
        "schema_version": "0.3",
        "status": "extracted" if official_code_present(paths.official_dir) else "missing_official_code",
        "source_files": {
            "readme": "code/official/README.md" if readme.exists() else None,
            "requirements": "code/official/requirements.txt" if requirements.exists() else None,
            "main": "code/official/main.py" if main_py.exists() else None,
            "eval": "code/official/eval_skill.py" if eval_py.exists() else None,
        },
        "main_cli_flags": main_flags,
        "eval_cli_flags": eval_flags,
        "readme_eval_cli_mismatch": readme_eval_mismatch,
        "install_source": "requirements.txt" if requirements.exists() else None,
        "train_entrypoint": "main.py" if main_py.exists() else None,
        "eval_entrypoint": "eval_skill.py" if eval_py.exists() else None,
    }
    write_json(paths.artifacts_dir / "official_instructions.json", instructions)

    md = [
        "# Official Instructions",
        "",
        f"Status: `{instructions['status']}`",
        "",
        "## Detected Files",
        "",
    ]
    for label, value in instructions["source_files"].items():
        md.append(f"- {label}: `{value or 'missing'}`")
    md.extend(["", "## CLI Flags", "", f"- main.py: `{', '.join(main_flags) or 'none detected'}`"])
    md.append(f"- eval_skill.py: `{', '.join(eval_flags) or 'none detected'}`")
    md.extend(
        [
            "",
            "## Notes",
            "",
            "- Install source is `requirements.txt`.",
            "- Training entrypoint is `main.py <dataset> --config <config>`.",
            "- Evaluation entrypoint uses `eval_skill.py --skill-repo --dataset --n --seed --models --judge-model --output`.",
        ]
    )
    if readme_eval_mismatch:
        md.append("- Deviation required: README eval flags differ from the current `eval_skill.py` parser.")
    write_text(paths.artifacts_dir / "official_instructions.md", "\n".join(md))
    append_event(run_dir, "official_instruction_extraction", instructions["status"], artifact="artifacts/official_instructions.md")
    return instructions


def sample_dataset(source_path: Path, target_path: Path, n: int, seed: int) -> None:
    if target_path.exists():
        return
    data = read_json(source_path)
    instances = list(data.get("instances", []))
    if len(instances) > n:
        instances = random.Random(seed).sample(instances, n)
    data["instances"] = instances
    data["dataset_id"] = f"{data.get('dataset_id', source_path.stem)}_smoke_n{len(instances)}_seed{seed}"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_path, data)


def write_smoke_config(run_dir: Path) -> None:
    config_path = paths_for(run_dir).artifacts_dir / "skillgen_aime_smoke_config.yaml"
    if config_path.exists():
        return
    config = """# SkillGen Phase 0 cheap smoke config.
# Deviation from official config.yaml: reduces instances/rounds/workers for cost control.
models:
  default: "openai/gpt-5.4-mini"
  baseline_agent: "openai/gpt-5.4-nano"
  baseline_judge: "openai/gpt-5.4-mini"
  induction: "openai/gpt-5.4-mini"
  induction_contextual: "openai/gpt-5.4-mini"
  induction_summary: "openai/gpt-5.4-mini"
  induction_pattern: "openai/gpt-5.4-mini"
  induction_contrastive: "openai/gpt-5.4-mini"
  generation_plan: "openai/gpt-5.4-mini"
  generation_execute: "openai/gpt-5.4-mini"
  refinement: "openai/gpt-5.4-mini"
  verification_agent: "openai/gpt-5.4-nano"
  verification_judge: "openai/gpt-5.4-mini"
  verification_case_analyst: "openai/gpt-5.4-mini"
  verification_revision_synthesiser: "openai/gpt-5.4-mini"

llm:
  temperature: 0.0
  max_tokens: 1024
  max_tokens_generation: 4096

embedding:
  model: "text-embedding-3-small"

clustering:
  method: "kmeans"
  n_clusters: null
  max_failure_clusters: 2
  max_success_clusters: 2
  min_clusters: 2
  target_cluster_size: 4
  min_cluster_size: 1

induction:
  max_contrastive_pairs: 4

generation:
  use_web_search: false
  max_search_queries: 0
  candidate_output_dir: "../../artifacts/raw_benchmark_outputs/skillgen_aime_smoke/candidates"
  generate_scripts: false
  max_failure_clusters_in_prompt: 2
  max_success_clusters_in_prompt: 2
  max_contrastive_pairs_in_prompt: 4

verification_analysis:
  case_analyst_workers: 1
  case_analyst_max_tokens: 1024
  revision_synthesiser_max_tokens: 2048

verification:
  sample_size: 4
  min_sample: 2
  seed: 42
  min_net_gain_abs: 1
  min_net_gain_rel: 0.0

router:
  enabled: false
  model: "openai/gpt-5.4-mini"
  max_workers: 1

pipeline:
  max_refine_rounds: 1
  baseline_runs_per_instance: 1
  max_workers: 1
  artifact_root: "../../artifacts/raw_benchmark_outputs/skillgen_aime_smoke/artifacts/runs"

skill_output:
  path: "../../artifacts/raw_benchmark_outputs/skillgen_aime_smoke/skill_output"
"""
    write_text(config_path, config)


def prepare_smoke_assets(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    train_source = paths.official_dir / "data" / "aime" / "train.json"
    test_source = paths.official_dir / "data" / "aime" / "test.json"
    train_target = paths.artifacts_dir / "smoke_data" / "aime_train_n8_seed42.json"
    test_target = paths.artifacts_dir / "smoke_data" / "aime_test_n4_seed42.json"
    result = {
        "status": "missing_official_aime_data",
        "train_subset": "artifacts/smoke_data/aime_train_n8_seed42.json",
        "test_subset": "artifacts/smoke_data/aime_test_n4_seed42.json",
        "config": "artifacts/skillgen_aime_smoke_config.yaml",
    }
    config_target = paths.artifacts_dir / "skillgen_aime_smoke_config.yaml"
    if train_target.exists() and test_target.exists() and config_target.exists():
        result["status"] = "already_prepared"
        return result
    if train_source.exists() and test_source.exists():
        sample_dataset(train_source, train_target, n=8, seed=42)
        sample_dataset(test_source, test_target, n=4, seed=42)
        write_smoke_config(run_dir)
        result["status"] = "prepared"
    return result


def build_verification_contract(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    benchmark_claims_path = paths.artifacts_dir / "benchmark_claims.json"
    claim = {}
    if benchmark_claims_path.exists():
        claims_data = read_json(benchmark_claims_path)
        claims = claims_data.get("benchmark_claims", [])
        claim = claims[0] if claims else {}
    contract = {
        "schema_version": "0.3",
        "target_id": TARGET_ID,
        "target_name": "SkillGen AIME smoke validation",
        "scope": "official-code smoke only; not full Table 1 reproduction",
        "paper_claim_id": claim.get("claim_id", "claim_skillgen_table1_average_gains"),
        "benchmark_claim_id": claim.get("id", "bench_skillgen_table1_paired_accuracy"),
        "paper_claim_scope_status": "blocked_unless_full_table1_setup_runs",
        "official_code": {
            "repo_url": OFFICIAL_REPO_URL,
            "path": "code/official",
        },
        "dataset": {
            "benchmark": "aime",
            "train_subset": "artifacts/smoke_data/aime_train_n8_seed42.json",
            "test_subset": "artifacts/smoke_data/aime_test_n4_seed42.json",
            "seed": 42,
            "train_n": 8,
            "eval_n": 4,
        },
        "models": {
            "baseline_agent": "openai/gpt-5.4-nano",
            "judge_model": "openai/gpt-5.4-mini",
            "skillgen_auxiliary": "openai/gpt-5.4-mini",
        },
        "metric": {
            "name": "accuracy",
            "baseline_field": "baseline_acc",
            "skill_field": "skill_acc",
            "delta_field": "delta_acc",
            "repair_field": "repair",
            "regression_field": "regression",
            "net_gain_field": "net_gain",
            "expected_direction": "higher_is_better",
        },
        "result_parser": "skillgen_eval_results_v1",
        "comparison_rule": {
            "smoke_reproduced_if": "skill_acc > baseline_acc and net_gain > 0",
            "smoke_not_reproduced_if": "skill_acc <= baseline_acc or net_gain <= 0",
            "full_paper_claim_status": "blocked",
        },
        "required_env_vars": ["OPENROUTER_API_KEY", "OPENAI_API_KEY"],
        "requires_network": True,
        "requires_paid_api_or_token_budget": True,
        "hardcoding_disclosures": [
            "SkillGen-specific target.",
            "AIME smoke subset selected for lowest-cost official-code validation.",
            "Known SkillGen eval_results.json parser.",
        ],
    }
    write_json(paths.artifacts_dir / "verification_contract.json", contract)
    write_text(
        paths.artifacts_dir / "verification_contract.md",
        "# Verification Contract\n\n"
        "Target: `skillgen_aime_smoke`\n\n"
        "This contract validates a SkillGen AIME smoke target. It is not a full Table 1 reproduction.\n",
    )
    append_event(run_dir, "verification_contract_generation", "completed", artifact="artifacts/verification_contract.json")
    return contract


def build_command_plan(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    contract = read_json(paths.artifacts_dir / "verification_contract.json")
    plan = {
        "schema_version": "0.3",
        "status": "ready_for_approval",
        "target_id": contract["target_id"],
        "official_code_url": OFFICIAL_REPO_URL,
        "requires_network": True,
        "requires_api_keys": True,
        "requires_paid_api_or_token_budget": True,
        "required_env_vars": contract["required_env_vars"],
        "commands": {
            "create_venv": {
                "kind": "install",
                "workdir": ".",
                "argv": ["python3", "-m", "venv", "code/official/.venv"],
                "requires_approval": True,
                "requires_network": False,
            },
            "install": {
                "kind": "install",
                "workdir": ".",
                "argv": [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "code/official/.venv/bin/python",
                    "-r",
                    "code/official/requirements.txt",
                ],
                "env": {"UV_CACHE_DIR": "code/official/.uv-cache"},
                "requires_approval": True,
                "requires_network": True,
            },
            "train": {
                "kind": "benchmark_train",
                "workdir": "code/official",
                "argv": [
                    ".venv/bin/python",
                    "main.py",
                    "../../artifacts/smoke_data/aime_train_n8_seed42.json",
                    "--config",
                    "../../artifacts/skillgen_aime_smoke_config.yaml",
                ],
                "requires_approval": True,
                "requires_network": True,
                "requires_api_keys": True,
            },
            "eval_template": {
                "kind": "benchmark_eval",
                "workdir": "code/official",
                "argv": [
                    ".venv/bin/python",
                    "eval_skill.py",
                    "--skill-repo",
                    "{skill_output_dir}",
                    "--dataset",
                    "../../artifacts/smoke_data/aime_test_n4_seed42.json",
                    "--n",
                    "4",
                    "--seed",
                    "42",
                    "--models",
                    "openai/gpt-5.4-nano",
                    "--judge-model",
                    "openai/gpt-5.4-mini",
                    "--max-workers",
                    "1",
                    "--output",
                    "../../artifacts/raw_benchmark_outputs/skillgen_aime_smoke/eval_results.json",
                ],
                "requires_approval": True,
                "requires_network": True,
                "requires_api_keys": True,
            },
        },
        "expected_outputs": [
            "artifacts/raw_benchmark_outputs/skillgen_aime_smoke/eval_results.json",
            "artifacts/raw_benchmark_outputs/skillgen_aime_smoke/eval_results.token_usage.json",
        ],
        "deviations_requiring_approval": [
            "AIME smoke subset instead of the full paper Table 1 setup.",
            "Reduced smoke config instead of official config.yaml.",
            "Corrected eval CLI uses --skill-repo and --dataset based on eval_skill.py.",
            "uv cache and virtual environment are kept inside the run directory.",
        ],
    }
    write_json(paths.artifacts_dir / "command_plan.json", plan)
    write_text(
        paths.artifacts_dir / "human_command_review.md",
        "# Human Command Review\n\n"
        "Status: `approval_required`\n\n"
        "The command runner requires `artifacts/approval.json` before install or benchmark execution.\n",
    )
    write_json(
        paths.artifacts_dir / "approval.template.json",
        {
            "schema_version": "0.1",
            "command_plan_approved": True,
            "approved_targets": [TARGET_ID],
            "allow_install": True,
            "allow_benchmark": True,
            "allow_network": True,
            "allow_paid_api": True,
            "allow_project_local_install": True,
            "skip_install_if_environment_present": True,
            "auto_retry_approved": True,
            "max_retry_attempts": 1,
            "dependency_scope_required": "inside_project_directory",
            "max_cost_usd": 5.0,
            "approved_by": "human",
            "notes": "Approve only after reviewing command_plan.json.",
        },
    )
    append_event(run_dir, "command_plan_generation", "completed", artifact="artifacts/command_plan.json")
    return plan


def write_automation_hardcoding_disclosures(run_dir: Path) -> None:
    paths = paths_for(run_dir)
    json_path = paths.artifacts_dir / "hardcoding_disclosures.json"
    md_path = paths.artifacts_dir / "hardcoding_disclosures.md"
    if json_path.exists():
        payload = read_json(json_path)
        hardcodings = list(payload.get("hardcodings", []))
    else:
        hardcodings = [asdict(item) for item in hardcoding_disclosures()]

    additions = [
        {
            "id": "official_repo_url",
            "description": f"The automation uses `{OFFICIAL_REPO_URL}` as the official SkillGen code source.",
            "reason": "The paper-specific POC targets SkillGen and needs a deterministic official-code intake source.",
            "impact": "A different paper or fork requires a different code-intake contract.",
        },
        {
            "id": "skillgen_aime_smoke_target",
            "description": "The first executable target is AIME with train_n=8, eval_n=4, and seed=42.",
            "reason": "The user requested the cheapest validation target for the preliminary Phase 0 POC.",
            "impact": "The smoke verdict does not reproduce the full SkillGen Table 1 claim.",
        },
        {
            "id": "skillgen_smoke_models",
            "description": "The smoke command plan uses OpenRouter model names openai/gpt-5.4-nano and openai/gpt-5.4-mini.",
            "reason": "The existing smoke run used the cheapest available validation setup that still exercises official code.",
            "impact": "Changing provider routing or model availability may change cost, behavior, or reproducibility.",
        },
        {
            "id": "skillgen_eval_parser",
            "description": "The result parser expects SkillGen eval_results.json, token usage JSON, and verification_summary.json shapes.",
            "reason": "The POC only needs to automate this paper's official-code output format.",
            "impact": "Other papers or future SkillGen output schemas need a different parser contract.",
        },
        {
            "id": "skillgen_eval_cli_deviation",
            "description": "The command plan uses eval_skill.py --skill-repo/--dataset flags when the README example appears mismatched.",
            "reason": "The executable script parser is treated as the source of truth for the current official checkout.",
            "impact": "This is a recorded deviation from README text and must remain visible for human review.",
        },
        {
            "id": "skillgen_all_claim_catalog",
            "description": "The all-claims automation uses a SkillGen-specific catalog of major empirical and executable claims.",
            "reason": "The POC is scoped to SkillGen.pdf and the paper's claims require paper-specific grouping before verification.",
            "impact": "The catalog is not a general claim extractor for arbitrary papers.",
        },
        {
            "id": "skillgen_table1_rows_and_models",
            "description": "The all-claims matrix hardcodes the Table 1 row ids and eight paper model display names.",
            "reason": "These are needed to detect which full-paper claims can be matched to official-code data and model routes.",
            "impact": "Exact provider route IDs still need review before full unattended Table 1 execution.",
        },
        {
            "id": "skillgen_external_source_catalog",
            "description": "The automation hardcodes official external-source candidates for missing SkillGen benchmark components.",
            "reason": "The POC needs to distinguish unresolved missing data from officially referenced sources that can be pulled into the run package.",
            "impact": "Only sources supported by official README/script/adapter evidence are treated as valid reproduction intake candidates.",
        },
        {
            "id": "skillgen_transfer_and_token_claim_tables",
            "description": "The automation hardcodes the paper's transfer-model display names, transfer benchmark rows, and Table 4 token-cost benchmark rows.",
            "reason": "These claim-level runner plans are SkillGen-specific and need deterministic row/model names before execution artifacts can be generated.",
            "impact": "The route IDs, actual token logs, and benchmark outputs still need execution evidence before the corresponding claims can be reproduced.",
        },
        {
            "id": "skillgen_canonical_benchmark_sources",
            "description": "The automation records canonical external benchmark repositories for paper-named benchmarks when the SkillGen checkout lacks complete runnable support.",
            "reason": "The user asked to fetch code for paper-indicated sources even when the paper does not provide a detailed SkillGen-compatible integration.",
            "impact": "Fetched canonical code is source evidence only until a SkillGen-compatible adapter, split contract, and execution plan are available.",
        },
        {
            "id": "skillgen_direct_openai_fallback_deviation",
            "description": "Some additional target executions use a recorded official-code patch that routes openai/* chat calls directly to OpenAI when SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1.",
            "reason": "The OpenRouter account returned insufficient-credit errors during approved execution, while the user's OpenAI key could execute the same OpenAI model routes.",
            "impact": "This is a human-visible execution deviation from the unpatched official checkout and must be considered when comparing results to the paper.",
        },
        {
            "id": "skillgen_table4_reduced_poc_scale_deviation",
            "description": "Table 4 token groups were executed with reduced POC-scale configs rather than the full paper-scale Table 4 setup.",
            "reason": "The Phase 0 POC needed to clear non-structural API/cost blockers while keeping the run tractable inside the current project run directory.",
            "impact": "The run verifies token-log collection mechanics for the ready Table 4 groups, but it does not reproduce the paper's full-scale token totals.",
        },
        {
            "id": "skillgen_table4_concurrency_retry_deviation",
            "description": "Some generated Table 4 configs used max_workers=4 for speed; Mind2Web was retried at max_workers=1 after an OpenAI TPM 429 rate-limit failure.",
            "reason": "Concurrency reduced wall-clock time for long ready targets, while the retry avoided a non-structural provider rate-limit blocker.",
            "impact": "Concurrency and retry behavior are recorded deviations that may affect latency and token timing, but the raw logs preserve the attempted and successful executions.",
        },
    ]
    by_id = {item.get("id"): item for item in hardcodings}
    for item in additions:
        by_id[item["id"]] = item
    merged = list(by_id.values())
    write_json(json_path, {"schema_version": "0.2", "hardcodings": merged})

    lines = ["# Hardcoding Disclosures"]
    for item in merged:
        lines.extend(
            [
                "",
                f"## {item['id']}",
                "",
                f"- Description: {item['description']}",
                f"- Reason: {item['reason']}",
                f"- Impact: {item['impact']}",
            ]
        )
    write_text(md_path, "\n".join(lines) + "\n")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()


def evidence_snippet(text: str, anchor: str, radius: int = 420) -> str:
    compact = normalize_text(text)
    index = compact.lower().find(anchor.lower())
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(compact), index + len(anchor) + radius)
    return compact[start:end]


def build_external_source_catalog(official_dir: Path) -> dict[str, list[dict[str, Any]]]:
    catalog: dict[str, list[dict[str, Any]]] = {}
    for source_key, candidates in EXTERNAL_SOURCE_CANDIDATES.items():
        enriched = []
        for candidate in candidates:
            evidence_paths = candidate["official_evidence_paths"]
            present = [path for path in evidence_paths if (official_dir / path).exists()]
            missing = [path for path in evidence_paths if path not in present]
            row = dict(candidate)
            row["source_key"] = source_key
            row["official_evidence_present"] = present
            row["official_evidence_missing"] = missing
            row["identity_status"] = (
                "identified_by_official_code"
                if not missing
                else "candidate_definition_not_confirmed_in_current_checkout"
            )
            row["requires_source_intake_approval"] = True
            enriched.append(row)
        catalog[source_key] = enriched
    return catalog


def supported_external_candidates(support: dict[str, Any], source_keys: list[str]) -> list[dict[str, Any]]:
    catalog = support.get("external_source_candidates", {})
    candidates: list[dict[str, Any]] = []
    for source_key in source_keys:
        for candidate in catalog.get(source_key, []):
            if candidate.get("identity_status") == "identified_by_official_code":
                candidates.append(candidate)
    return candidates


def external_source_status_map(support: dict[str, Any]) -> dict[str, dict[str, Any]]:
    status = support.get("external_source_intake_status", {})
    return {row["source_key"]: row for row in status.get("tasks", [])}


def external_source_is_prepared(support: dict[str, Any], source_key: str) -> bool:
    row = external_source_status_map(support).get(source_key, {})
    return row.get("status") == "prepared"


def external_source_keys_for_claim(claim_id: str, support: dict[str, Any]) -> list[str]:
    if claim_id in {"claim_table1_average_gains_all_models", "claim_table1_entry_counts"}:
        return [row for row in support.get("table1_missing_rows", []) if row in EXTERNAL_SOURCE_CANDIDATES]
    mapping = {
        "claim_tau_bench_gate_activated": ["tau_bench"],
        "claim_chemllmbench_useful_gains": ["chemllmbench"],
    }
    return mapping.get(claim_id, [])


def format_source_candidate(candidate: dict[str, Any]) -> str:
    return (
        f"{candidate['source_key']} via {candidate['source']} "
        f"({candidate['intake']})"
    )


def status_badge(status: str | None) -> str:
    value = status or "unknown"
    palette = {
        STATUS_REPRODUCED: ("#d1fae5", "#065f46", "#34d399"),
        STATUS_PARTIALLY_REPRODUCED: ("#fef3c7", "#92400e", "#f59e0b"),
        STATUS_NOT_REPRODUCED: ("#fee2e2", "#991b1b", "#f87171"),
        STATUS_BLOCKED: ("#dbeafe", "#1e40af", "#60a5fa"),
        STATUS_NOT_TESTABLE: ("#e5e7eb", "#374151", "#9ca3af"),
        STATUS_FAILED_TO_RUN: ("#fee2e2", "#7f1d1d", "#ef4444"),
        STATUS_READY_FOR_EXECUTION: ("#dcfce7", "#166534", "#86efac"),
        STATUS_ROUTE_RESOLUTION_REQUIRED: ("#ede9fe", "#5b21b6", "#a78bfa"),
    }
    background, text, border = palette.get(value, ("#f3f4f6", "#111827", "#d1d5db"))
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:4px;'
        f'background:{background};color:{text};border:1px solid {border};'
        f'font-weight:600">{value}</span>'
    )


def official_support_snapshot(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    intake_status_path = paths.artifacts_dir / "external_source_intake_status.json"
    benchmark_execution_plan_path = paths.artifacts_dir / "benchmark_execution_plan.json"
    model_route_mapping_path = paths.artifacts_dir / "model_route_mapping.template.json"
    transfer_runner_plan_path = paths.artifacts_dir / "transfer_runner_plan.json"
    token_log_plan_path = paths.artifacts_dir / "token_log_plan.json"
    canonical_source_status_path = paths.artifacts_dir / "canonical_benchmark_source_status.json"
    data_support: dict[str, Any] = {}
    for target_id, relative_dir in BUNDLED_DATASET_MAP.items():
        data_dir = paths.official_dir / relative_dir
        train_path = data_dir / "train.json"
        test_path = data_dir / "test.json"
        train_n = test_n = None
        train_metadata = test_metadata = {}
        if train_path.exists():
            train_data = read_json(train_path)
            train_n = len(train_data.get("instances", []))
            train_metadata = train_data.get("metadata", {})
        if test_path.exists():
            test_data = read_json(test_path)
            test_n = len(test_data.get("instances", []))
            test_metadata = test_data.get("metadata", {})
        data_support[target_id] = {
            "available": train_path.exists() and test_path.exists(),
            "data_dir": relative_dir,
            "train_path": f"{relative_dir}/train.json",
            "test_path": f"{relative_dir}/test.json",
            "train_n": train_n,
            "test_n": test_n,
            "train_metadata": train_metadata,
            "test_metadata": test_metadata,
        }

    table1_present = [row for row in TABLE1_REQUIRED_ROWS if row in data_support and data_support[row]["available"]]
    table1_missing = [row for row in TABLE1_REQUIRED_ROWS if row not in table1_present]
    source_files = {
        "baseline_generators": any((paths.official_dir / name).exists() for name in ["baselines", "baseline_generators"]),
        "ablation_runner": any((paths.official_dir / name).exists() for name in ["ablation.py", "run_ablation.py", "scripts/run_ablation.py"]),
        "transfer_runner": any((paths.official_dir / name).exists() for name in ["transfer.py", "run_transfer.py", "scripts/run_transfer.py"]),
        "eval_skill": (paths.official_dir / "eval_skill.py").exists(),
        "main": (paths.official_dir / "main.py").exists(),
    }
    return {
        "schema_version": "0.1",
        "official_code_present": official_code_present(paths.official_dir),
        "data_support": data_support,
        "table1_required_rows": TABLE1_REQUIRED_ROWS,
        "table1_present_rows": table1_present,
        "table1_missing_rows": table1_missing,
        "paper_model_names": PAPER_MODEL_NAMES,
        "source_files": source_files,
        "external_source_candidates": build_external_source_catalog(paths.official_dir),
        "external_source_intake_status": read_json(intake_status_path) if intake_status_path.exists() else {},
        "benchmark_execution_plan": read_json(benchmark_execution_plan_path) if benchmark_execution_plan_path.exists() else {},
        "model_route_mapping": read_json(model_route_mapping_path) if model_route_mapping_path.exists() else {},
        "transfer_runner_plan": read_json(transfer_runner_plan_path) if transfer_runner_plan_path.exists() else {},
        "token_log_plan": read_json(token_log_plan_path) if token_log_plan_path.exists() else {},
        "canonical_benchmark_source_status": read_json(canonical_source_status_path) if canonical_source_status_path.exists() else {},
    }


def skillgen_all_claims(paper_text: str) -> list[dict[str, Any]]:
    specs = [
        {
            "id": "claim_method_paired_intervention",
            "claim_type": "method_contract",
            "paper_location": "Abstract, Section 2, Section 3",
            "claim_text": "SkillGen models skills as inference-time interventions and evaluates the same instances with and without a generated skill, accounting for repairs and regressions.",
            "anchor": "we compare outcomes on the same instances with and without the skill",
            "verification_mode": "official_code_structure_and_smoke_output",
            "requires": ["main.py", "eval_skill.py", "paired result fields", "smoke or full run output"],
        },
        {
            "id": "claim_table1_average_gains_all_models",
            "claim_type": "main_result",
            "paper_location": "Section 4, Table 1",
            "claim_text": "SkillGen improves average held-out accuracy for all eight evaluated base LLMs, with gains from +3.27 to +10.08 percentage points.",
            "anchor": "improves average accuracy for all eight base agents",
            "verification_mode": "full_table1_matrix",
            "requires": ["Table 1 rows", "8 model routes", "official train/eval execution", "API/token budget"],
        },
        {
            "id": "claim_table1_entry_counts",
            "claim_type": "main_result",
            "paper_location": "Section 4, Table 1",
            "claim_text": "Out of 80 held-out benchmark-split-model entries, 50 improve, 25 remain unchanged, and 5 regress.",
            "anchor": "out of 80 held-out benchmark",
            "verification_mode": "full_table1_matrix",
            "requires": ["80 paired benchmark entries", "delta threshold/count rule"],
        },
        {
            "id": "claim_table1_alfworld_scienceworld_patterns",
            "claim_type": "main_result_breakdown",
            "paper_location": "Section 4, Table 1",
            "claim_text": "ALFWorld improves in 14 of 16 entries and ScienceWorld improves for all eight agents.",
            "anchor": "ALFWorld improves in 14 of 16 entries",
            "verification_mode": "full_table1_subset",
            "requires": ["ALFWorld IOD/OOD official data", "ScienceWorld official data", "8 model routes"],
        },
        {
            "id": "claim_baseline_generator_comparison",
            "claim_type": "baseline_comparison",
            "paper_location": "RQ2, Figure 2, Appendix C.6",
            "claim_text": "SkillGen is consistently positive and achieves the largest average improvement compared with Trace2Skill, SkillX, EvoSkill, and CoEvoSkills.",
            "anchor": "compare SKILLGEN against four recent skill-generation baselines",
            "verification_mode": "baseline_generator_matrix",
            "requires": ["baseline generator implementations", "shared paired evaluation harness", "representative benchmark-model entries"],
        },
        {
            "id": "claim_ablation_full_wins",
            "claim_type": "ablation",
            "paper_location": "RQ3, Figure 3",
            "claim_text": "The full SkillGen system wins on every ablation dataset-model pair, showing that contrastive induction, refinement, verification gate, failure lessons, and script/reference bundles contribute.",
            "anchor": "Full wins on every dataset",
            "verification_mode": "ablation_matrix",
            "requires": ["ablation runner", "ablated configs", "shared no-skill baseline"],
        },
        {
            "id": "claim_cross_model_transfer",
            "claim_type": "transfer",
            "paper_location": "RQ4, Figure 4",
            "claim_text": "Generated skills often transfer across models; across 120 off-diagonal comparisons, 70% are non-negative and 42% exceed +5 percentage points.",
            "anchor": "Across 120 off-diagonal comparisons",
            "verification_mode": "transfer_matrix",
            "requires": ["skills generated by source models", "evaluator model routes", "transfer benchmark datasets"],
        },
        {
            "id": "claim_tau_bench_gate_activated",
            "claim_type": "additional_benchmark",
            "paper_location": "RQ5, Figure 5",
            "claim_text": "On tau-Bench retail, SkillGen improves every model whose verification gate activated.",
            "anchor": "SKILLGEN improves every model whose",
            "verification_mode": "tau_bench_matrix",
            "requires": ["tau-Bench data", "retail user simulator", "gate activation records"],
        },
        {
            "id": "claim_chemllmbench_useful_gains",
            "claim_type": "additional_benchmark",
            "paper_location": "RQ5, Figure 6",
            "claim_text": "On ChemLLMBench property and yield prediction, SkillGen provides useful gains in the reported settings.",
            "anchor": "Insights for ChemLLMBench",
            "verification_mode": "chemllmbench_matrix",
            "requires": ["ChemLLMBench data", "property/yield prediction splits", "model routes"],
        },
        {
            "id": "claim_refinement_best_of_k",
            "claim_type": "refinement_analysis",
            "paper_location": "RQ5, Figure 7",
            "claim_text": "Best-of-K selection over refinement rounds improves aggregate skill accuracy over individual rounds in representative runs.",
            "anchor": "Best-of-K skill accuracy",
            "verification_mode": "refinement_trace_analysis",
            "requires": ["per-round candidate records", "verification traces", "aggregate bootstrap calculation"],
        },
        {
            "id": "claim_token_cost",
            "claim_type": "cost_analysis",
            "paper_location": "Appendix C.5, Table 4",
            "claim_text": "Skill construction token cost ranges from 2.2M to 10.2M tokens across listed benchmarks, with mean 5.6M and about $8.2 per generated skill under the stated pricing.",
            "anchor": "Token cost of SKILLGEN",
            "verification_mode": "token_usage_aggregation",
            "requires": ["full token_usage logs", "benchmark grouping", "pricing formula"],
        },
        {
            "id": "claim_auditable_skill_artifact",
            "claim_type": "artifact_property",
            "paper_location": "Abstract, Contributions",
            "claim_text": "SkillGen produces a single human-readable auditable skill artifact that can be inspected before use.",
            "anchor": "single auditable skill",
            "verification_mode": "official_code_output_inspection",
            "requires": ["generated skill artifact", "human-readable skill body"],
        },
    ]
    claims: list[dict[str, Any]] = []
    for spec in specs:
        claims.append(
            {
                "id": spec["id"],
                "claim_type": spec["claim_type"],
                "claim_text": spec["claim_text"],
                "paper_location": spec["paper_location"],
                "evidence_text": evidence_snippet(paper_text, spec["anchor"]),
                "verification_mode": spec["verification_mode"],
                "requires": spec["requires"],
                "status": "pending_verification_planning",
            }
        )
    return claims


def all_claim_status(claim: dict[str, Any], support: dict[str, Any], benchmark: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    claim_id = claim["id"]
    blockers: list[str] = []
    evidence: list[str] = []
    source_files = support["source_files"]
    data_support = support["data_support"]

    if claim_id == "claim_method_paired_intervention":
        if source_files["eval_skill"] and benchmark.get("status") == "official_code_smoke_completed":
            evidence.append("Existing AIME smoke eval output contains baseline_acc, skill_acc, repair, regression, and net_gain fields.")
            return STATUS_PARTIALLY_REPRODUCED, blockers, evidence
        blockers.append("Needs at least one official eval output with paired result fields.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_auditable_skill_artifact":
        skill_output = (benchmark.get("train") or {}).get("skill_output")
        if skill_output:
            evidence.append(f"Existing smoke run produced a skill output directory: {skill_output}.")
            return STATUS_PARTIALLY_REPRODUCED, blockers, evidence
        blockers.append("Needs an official run that produces a SkillGen skill artifact.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id in {"claim_table1_average_gains_all_models", "claim_table1_entry_counts"}:
        missing_rows = support["table1_missing_rows"]
        external_candidates = supported_external_candidates(
            support,
            [row for row in missing_rows if row in EXTERNAL_SOURCE_CANDIDATES],
        )
        recoverable_rows = sorted({candidate["source_key"] for candidate in external_candidates})
        prepared_rows = [row for row in recoverable_rows if external_source_is_prepared(support, row)]
        unprepared_rows = [row for row in recoverable_rows if row not in prepared_rows]
        unresolved_rows = [row for row in missing_rows if row not in recoverable_rows]
        canonical_sources = {
            row.get("source_key"): row
            for row in (support.get("canonical_benchmark_source_status") or {}).get("sources", [])
        }
        alfworld_canonical_ready = bool((canonical_sources.get("alfworld") or {}).get("target_exists"))
        canonical_only_rows: list[str] = []
        if alfworld_canonical_ready:
            canonical_only_rows = [row for row in unresolved_rows if row in {"alfworld_iod", "alfworld_ood"}]
            unresolved_rows = [row for row in unresolved_rows if row not in canonical_only_rows]
        execution_plan = support.get("benchmark_execution_plan") or {}
        execution_targets = {
            target.get("table1_row"): target
            for target in execution_plan.get("targets", [])
            if target.get("table1_row")
        }
        ready_execution_rows = [
            row for row in TABLE1_REQUIRED_ROWS
            if (execution_targets.get(row) or {}).get("status") == STATUS_READY_FOR_EXECUTION
        ]
        nonready_execution_rows = [
            f"{row} ({(execution_targets.get(row) or {}).get('status', 'missing_execution_plan')})"
            for row in TABLE1_REQUIRED_ROWS
            if (execution_targets.get(row) or {}).get("status") != STATUS_READY_FOR_EXECUTION
        ]
        blockers.extend(
            [
                "Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.",
            ]
        )
        if prepared_rows:
            evidence.append("External-source data has been prepared for rows: " + ", ".join(prepared_rows) + ".")
        if ready_execution_rows:
            evidence.append("Benchmark execution plan has Table 1-ready rows with resolved model routes: " + ", ".join(ready_execution_rows) + ".")
        if nonready_execution_rows:
            blockers.append("Rows not yet Table 1 execution-ready: " + ", ".join(nonready_execution_rows) + ".")
        if unprepared_rows:
            remaining_candidates = [candidate for candidate in external_candidates if candidate["source_key"] in unprepared_rows]
            blockers.append(
                "Official external-source intake or full-size preparation is still required for rows: "
                + "; ".join(format_source_candidate(candidate) for candidate in remaining_candidates)
            )
        if canonical_only_rows:
            evidence.append(
                "Canonical ALFWorld code has been fetched, but these rows still need a SkillGen-compatible adapter and IOD/OOD split contract: "
                + ", ".join(canonical_only_rows)
                + "."
            )
        if unresolved_rows:
            blockers.append(
                "Missing rows with no verified official external twin in the current checkout: "
                + ", ".join(unresolved_rows)
            )
        present = ", ".join(support["table1_present_rows"]) or "none"
        evidence.append(f"Official release currently has bundled data for these Table 1 rows: {present}.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_table1_alfworld_scienceworld_patterns":
        if not data_support.get("scienceworld", {}).get("available"):
            blockers.append("ScienceWorld bundled data is missing.")
        if "alfworld_iod" in support["table1_missing_rows"] or "alfworld_ood" in support["table1_missing_rows"]:
            canonical_sources = {
                row.get("source_key"): row
                for row in (support.get("canonical_benchmark_source_status") or {}).get("sources", [])
            }
            alfworld_source = canonical_sources.get("alfworld", {})
            if alfworld_source.get("target_exists"):
                evidence.append(
                    "Canonical ALFWorld benchmark code is fetched at "
                    f"{alfworld_source.get('target_path')} (commit {alfworld_source.get('commit') or 'unknown'})."
                )
                blockers.append("ALFWorld IOD/OOD data is not bundled and no SkillGen-compatible ALFWorld adapter/split contract exists yet.")
            else:
                blockers.append("ALFWorld IOD/OOD data is not bundled in code/official/data.")
        if data_support.get("scienceworld", {}).get("available"):
            evidence.append("ScienceWorld train/test JSON is bundled and can be planned for execution.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_baseline_generator_comparison":
        blockers.extend(
            [
                "Official checkout does not include Trace2Skill, SkillX, EvoSkill, or CoEvoSkills runner implementations.",
                "README describes baseline adaptation details in the paper, but no executable baseline-comparison command is present.",
                "A public baseline project would still need identity review and a SkillGen-compatible runner before it can count as an identical reproduction source.",
            ]
        )
        return STATUS_NOT_TESTABLE, blockers, evidence

    if claim_id == "claim_ablation_full_wins":
        blockers.extend(
            [
                "Official checkout does not include an ablation runner or named ablated configs.",
                "Cannot reproduce Figure 3 without reconstructing unprovided ablation variants.",
            ]
        )
        return STATUS_NOT_TESTABLE, blockers, evidence

    if claim_id == "claim_cross_model_transfer":
        transfer_plan = support.get("transfer_runner_plan") or {}
        if transfer_plan:
            ready_rows = [
                row["benchmark_row"]
                for row in transfer_plan.get("benchmarks", [])
                if row.get("dataset_status") == STATUS_READY_FOR_EXECUTION
            ]
            if ready_rows:
                evidence.append("Transfer runner plan has ready datasets for: " + ", ".join(ready_rows) + ".")
            evidence.append(
                "Transfer runner plan encodes "
                f"{transfer_plan.get('planned_off_diagonal_comparisons', 'unknown')} off-diagonal comparisons before execution."
            )
        blockers.extend(
            [
                "Full 120-comparison transfer claim still requires the ALFWorld OOD SkillGen adapter/split contract.",
            ]
        )
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_tau_bench_gate_activated":
        tau_target = (benchmark.get("additional_targets") or {}).get("tau_bench_retail")
        if tau_target:
            train_verification = (tau_target.get("train") or {}).get("construction_verification") or {}
            eval_result = tau_target.get("eval") or {}
            evidence.append(
                "tau-Bench official smoke execution completed with "
                f"skill_status={(tau_target.get('train') or {}).get('skill_status')}, "
                f"verification_passed={train_verification.get('passed')}, "
                f"train_net_gain={train_verification.get('net_gain')}."
            )
            if eval_result.get("n_instances") is not None:
                evidence.append(
                    "Held-out tau-Bench eval observed "
                    f"baseline={percent(eval_result.get('baseline_acc'))}, "
                    f"skill={percent(eval_result.get('skill_acc'))}, "
                    f"delta={percent(eval_result.get('delta_acc'))}, "
                    f"net_gain={eval_result.get('net_gain')}."
                )
            status = tau_target.get("claim_status") or STATUS_NOT_REPRODUCED
            if status == STATUS_PARTIALLY_REPRODUCED:
                evidence.append("The limited tau-Bench smoke target showed a positive skill delta.")
                return STATUS_PARTIALLY_REPRODUCED, blockers, evidence
            blockers.append(
                "Executed tau-Bench smoke did not support the paper claim: the generated skill failed the internal verification gate or produced no positive held-out skill delta."
            )
            return STATUS_NOT_REPRODUCED, blockers, evidence
        external_candidates = supported_external_candidates(support, ["tau_bench"])
        if external_source_is_prepared(support, "tau_bench"):
            evidence.append("tau-Bench external source and retail train/test JSONs have been prepared.")
            evidence.append("No structural blocker remains for the prepared tau-Bench retail target.")
            return STATUS_READY_FOR_EXECUTION, blockers, evidence
        if external_candidates:
            blockers.append(
                "tau-Bench train/test data is not bundled, but official code identifies external intake: "
                + "; ".join(format_source_candidate(candidate) for candidate in external_candidates)
            )
            return STATUS_BLOCKED, blockers, evidence
        blockers.extend(
            [
                "tau-Bench train/test data is not bundled in code/official/data.",
                "No verified official external-source path was found in the current checkout.",
            ]
        )
        return STATUS_NOT_TESTABLE, blockers, evidence

    if claim_id == "claim_chemllmbench_useful_gains":
        additional = benchmark.get("additional_targets") or {}
        chem_targets = [
            additional.get("chemllmbench_property_prediction"),
            additional.get("chemllmbench_yield_prediction"),
        ]
        executed_chem_targets = [target for target in chem_targets if target]
        if executed_chem_targets:
            positive = 0
            negative = 0
            for target in executed_chem_targets:
                eval_result = target.get("eval") or {}
                train_verification = (target.get("train") or {}).get("construction_verification") or {}
                evidence.append(
                    f"{target['target_id']} execution status={target.get('status')}, "
                    f"verification_passed={train_verification.get('passed')}, "
                    f"train_net_gain={train_verification.get('net_gain')}, "
                    f"heldout_delta={percent(eval_result.get('delta_acc'))}."
                )
                if target.get("claim_status") == STATUS_PARTIALLY_REPRODUCED:
                    positive += 1
                elif target.get("claim_status") == STATUS_NOT_REPRODUCED:
                    negative += 1
            if len(executed_chem_targets) < 2:
                evidence.append("Only one ChemLLMBench subtask has been executed so far.")
                return STATUS_PARTIALLY_REPRODUCED if positive else STATUS_NOT_REPRODUCED, blockers, evidence
            if positive and not negative:
                return STATUS_PARTIALLY_REPRODUCED, blockers, evidence
            blockers.append("Executed ChemLLMBench smoke targets did not show positive skill gains for all prepared subtasks.")
            return STATUS_NOT_REPRODUCED, blockers, evidence
        external_candidates = supported_external_candidates(support, ["chemllmbench"])
        if external_source_is_prepared(support, "chemllmbench"):
            evidence.append("ChemLLMBench external source and task train/test JSONs have been prepared.")
            evidence.append("No structural blocker remains for ChemLLMBench property/yield execution.")
            return STATUS_READY_FOR_EXECUTION, blockers, evidence
        if external_candidates:
            blockers.append(
                "ChemLLMBench train/test data is not bundled, but official code identifies external intake: "
                + "; ".join(format_source_candidate(candidate) for candidate in external_candidates)
            )
            return STATUS_BLOCKED, blockers, evidence
        blockers.extend(
            [
                "ChemLLMBench train/test data is not bundled in code/official/data.",
                "No verified official external-source path was found in the current checkout.",
            ]
        )
        return STATUS_NOT_TESTABLE, blockers, evidence

    if claim_id == "claim_refinement_best_of_k":
        blockers.extend(
            [
                "Official pipeline records refinement outputs for executed runs, but the paper's aggregate Figure 7 traces are not bundled.",
                "Needs full per-round run logs across representative benchmark-model entries.",
            ]
        )
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_token_cost":
        train_tokens = (benchmark.get("train") or {}).get("token_usage_total")
        eval_tokens = (benchmark.get("eval") or {}).get("token_usage_total")
        if train_tokens or eval_tokens:
            evidence.append(f"Existing smoke token evidence: train={train_tokens}, eval={eval_tokens}.")
        additional = benchmark.get("additional_targets") or {}
        additional_token_targets = []
        for target_id, target in sorted(additional.items()):
            train_total = ((target.get("train") or {}).get("token_usage_total"))
            eval_total = ((target.get("eval") or {}).get("token_usage_total"))
            if train_total or eval_total:
                additional_token_targets.append((target_id, train_total, eval_total))
        for target_id, train_total, eval_total in additional_token_targets:
            evidence.append(f"{target_id} token evidence: train={train_total}, eval={eval_total}.")
        token_plan = support.get("token_log_plan") or {}
        if token_plan:
            groups = [row.get("paper_name") for row in token_plan.get("benchmark_groups", [])]
            evidence.append("Token-log aggregation plan covers Table 4 groups: " + ", ".join(groups) + ".")
        table4_target_ids = {
            "scienceworld_token",
            "pubmedqa_token",
            "mind2web_token",
            "mcp_bench_token",
            "tau_bench_retail",
        }
        executed_table4_targets = {
            target_id
            for target_id, train_total, eval_total in additional_token_targets
            if target_id in table4_target_ids and (train_total or eval_total)
        }
        missing_table4_targets = sorted(table4_target_ids - executed_table4_targets)
        if table4_target_ids and not missing_table4_targets:
            evidence.append(
                "All Table 4 ready token groups were executed at reduced POC scale: "
                + ", ".join(sorted(executed_table4_targets))
                + "."
            )
            blockers.append(
                "The run uses reduced POC-scale configs, so token-log mechanics are reproduced but the paper's full-scale token totals are not."
            )
            return STATUS_PARTIALLY_REPRODUCED, blockers, evidence
        if train_tokens or eval_tokens or additional_token_targets:
            if missing_table4_targets:
                blockers.append("Table 4 token groups without executed token logs: " + ", ".join(missing_table4_targets) + ".")
            else:
                blockers.append("Only reduced POC-scale token logs are available in this run.")
            return STATUS_PARTIALLY_REPRODUCED, blockers, evidence
        evidence.append("No structural blocker remains for Table 4 token-log collection on the ready benchmark groups.")
        return STATUS_READY_FOR_EXECUTION, blockers, evidence

    blockers.append("No verification rule has been implemented for this claim.")
    return STATUS_NOT_TESTABLE, blockers, evidence


def next_step_for_claim(
    status: str,
    verification_mode: str,
    has_external_candidates: bool = False,
    claim_id: str | None = None,
    support: dict[str, Any] | None = None,
) -> str:
    support = support or {}
    if status == STATUS_NOT_REPRODUCED and claim_id in {"claim_tau_bench_gate_activated", "claim_chemllmbench_useful_gains"}:
        return (
            "Inspect the raw execution logs and rerun at full paper scale only if the smoke scope is considered insufficient; "
            "the current executed smoke evidence does not support the claim."
        )
    if claim_id in {"claim_tau_bench_gate_activated", "claim_chemllmbench_useful_gains"}:
        source_key = "tau_bench" if claim_id == "claim_tau_bench_gate_activated" else "chemllmbench"
        if external_source_is_prepared(support, source_key):
            return "Create/approve the benchmark execution contract, run the prepared benchmark, parse results, and compare to the paper claim."
    if claim_id in {"claim_table1_average_gains_all_models", "claim_table1_entry_counts"}:
        source_keys = external_source_keys_for_claim(claim_id, support)
        unprepared = [source_key for source_key in source_keys if not external_source_is_prepared(support, source_key)]
        execution_plan = support.get("benchmark_execution_plan") or {}
        nonready_rows = [
            target.get("table1_row")
            for target in execution_plan.get("targets", [])
            if target.get("table1_row") and target.get("status") != STATUS_READY_FOR_EXECUTION
        ]
        if unprepared:
            return (
                "Finish remaining structurally non-ready Table 1 rows, then run and aggregate the full Table 1 matrix."
            )
        if nonready_rows:
            return (
                "Resolve structurally non-ready Table 1 rows ("
                + ", ".join(nonready_rows)
                + "), then aggregate the full Table 1 matrix."
            )
        return "Run and aggregate the full Table 1 matrix."
    if claim_id == "claim_cross_model_transfer" and support.get("transfer_runner_plan"):
        return "Fill the ALFWorld OOD SkillGen contract gap, then execute transfer_runner_plan.json."
    if claim_id == "claim_token_cost" and status == STATUS_PARTIALLY_REPRODUCED:
        return (
            "Promote the reduced POC token-log executions to full paper-scale Table 4 runs only if exact numeric token-cost reproduction is required."
        )
    if claim_id == "claim_token_cost" and support.get("token_log_plan"):
        return "Run the Table 4 benchmark groups from token_log_plan.json, collect token logs, then compare grouped totals to the paper."
    if has_external_candidates:
        return (
            "Approve official external-source intake, pull/cache the source inside the run directory, "
            "then run the official preparation script before benchmark execution."
        )
    if status == STATUS_PARTIALLY_REPRODUCED:
        return "Promote from smoke evidence to full-paper evidence only if the matching full contract is executed."
    if status == STATUS_READY_FOR_EXECUTION:
        return "Execute the prepared benchmark target and parse/compare the resulting logs."
    if status == STATUS_BLOCKED and verification_mode in {"full_table1_matrix", "full_table1_subset", "transfer_matrix", "refinement_trace_analysis", "token_usage_aggregation"}:
        return "Resolve the remaining structural missing contract or artifact, then execute the relevant benchmark plan."
    if status == STATUS_NOT_TESTABLE:
        return "Obtain missing official code, data, or scripts; otherwise keep this claim not_testable."
    return "No next step defined."


def count_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def build_executable_target_inventory(support: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for target_id, data in support["data_support"].items():
        if not data["available"]:
            continue
        targets.append(
            {
                "target_id": f"skillgen_{target_id}",
                "data_dir": data["data_dir"],
                "train_path": data["train_path"],
                "test_path": data["test_path"],
                "train_n": data["train_n"],
                "test_n": data["test_n"],
                "status": STATUS_READY_FOR_EXECUTION,
                "limitations": [
                    "Use recorded route mapping and approved API execution policy.",
                ],
            }
        )
    return targets


def render_all_claims_md(claims: list[dict[str, Any]]) -> str:
    lines = [
        "# SkillGen All-Claims Catalog",
        "",
        "This catalog covers the major empirical and executable claims detected for the SkillGen Phase 0 POC.",
    ]
    for claim in claims:
        lines.extend(
            [
                "",
                f"## {claim['id']}",
                "",
                f"- Type: `{claim['claim_type']}`",
                f"- Location: {claim['paper_location']}",
                f"- Verification mode: `{claim['verification_mode']}`",
                "",
                claim["claim_text"],
            ]
        )
        if claim.get("evidence_text"):
            lines.extend(["", "Evidence anchor:", "", f"> {claim['evidence_text']}"])
    return "\n".join(lines) + "\n"


def render_all_claim_matrix_md(payload: dict[str, Any]) -> str:
    lines = [
        "# All-Claim Verification Matrix",
        "",
        "This matrix separates executable claims from claims that are blocked or not testable with the current official release.",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Claims", ""])
    for row in payload["claims"]:
        external_candidates = row.get("external_source_candidates") or []
        lines.extend(
            [
                f"### {row['claim_id']}",
                "",
                f"- Status: `{row['status']}`",
                f"- Verification mode: `{row['verification_mode']}`",
                f"- Next step: {row['next_step']}",
            ]
        )
        if row["evidence"]:
            lines.append("- Evidence: " + " ".join(row["evidence"]))
        if external_candidates:
            lines.append("- External source candidates:")
            for candidate in external_candidates:
                lines.append(
                    f"  - `{candidate['source_key']}`: {candidate['source']} -> "
                    f"{candidate['target_location']}"
                )
        if row["blockers"]:
            lines.append("- Blockers:")
            lines.extend(f"  - {blocker}" for blocker in row["blockers"])
        lines.append("")
    lines.extend(["## Executable Official-Code Targets", ""])
    for target in payload["executable_targets"]:
        lines.append(
            f"- `{target['target_id']}`: {target['train_path']} -> {target['test_path']} "
            f"(train_n={target['train_n']}, test_n={target['test_n']})"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_external_source_intake_plan(run_dir: Path, support: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = paths_for(run_dir)
    support = support or official_support_snapshot(run_dir)
    catalog = support.get("external_source_candidates", {})
    wanted_source_keys = ["livecodebench", "mcp_bench_all", "socialmaze_upi", "tau_bench", "chemllmbench"]
    tasks = []
    for source_key in wanted_source_keys:
        candidates = [
            candidate for candidate in catalog.get(source_key, [])
            if candidate.get("identity_status") == "identified_by_official_code"
        ]
        if not candidates:
            tasks.append(
                {
                    "source_key": source_key,
                    "status": STATUS_BLOCKED,
                    "reason": "No official-code-verified external source candidate is available.",
                }
            )
            continue
        candidate = candidates[0]
        target_location = candidate["target_location"]
        target_path = target_location.split(" or ", 1)[0]
        task = {
            "source_key": source_key,
            "status": "pending_source_intake",
            "source": candidate["source"],
            "source_type": candidate["source_type"],
            "source_url": candidate["source_url"],
            "target_location": target_location,
            "target_path": target_path,
            "identity_basis": candidate["identity_basis"],
            "requires_network": True,
            "requires_project_local_storage": True,
            "requires_api": source_key == "socialmaze_upi",
            "notes": [],
        }
        if source_key == "livecodebench":
            task["intake_method"] = "huggingface_dataset"
            task["cache_env"] = {
                "HF_HOME": rel(paths.official_dir / ".hf-cache", paths.official_dir),
                "HF_DATASETS_CACHE": rel(paths.official_dir / ".hf-cache" / "datasets", paths.official_dir),
            }
            task["prepare_commands"] = [
                {
                    "workdir": "code/official",
                    "argv": [
                        ".venv/bin/python",
                        "scripts/prepare_benchmarks.py",
                        "--benchmark",
                        "livecodebench",
                        "--livecodebench-version",
                        "release_v6",
                        "--n",
                        "0",
                        "-o",
                        "data/livecodebench/release_v6_all.json",
                    ],
                    "env": task["cache_env"],
                }
            ]
            task["notes"].append("Official script currently creates one dataset file; train/test splitting still needs a contract.")
        elif source_key == "mcp_bench_all":
            task["intake_method"] = "git_clone"
            task["clone_command"] = {
                "workdir": ".",
                "argv": ["git", "clone", "--depth", "1", candidate["source_url"], target_path],
            }
            task["prepare_commands"] = [
                {
                    "workdir": "code/official",
                    "argv": [
                        ".venv/bin/python",
                        "scripts/prepare_mcp_bench.py",
                        "--split",
                        "all",
                        "--train-n",
                        "40",
                        "--test-n",
                        "16",
                        "--out-dir",
                        "data/mcp_bench_all",
                    ],
                }
            ]
            task["notes"].append("Uses existing single-split train/test sizes as a first all-split preparation contract.")
        elif source_key == "socialmaze_upi":
            task["intake_method"] = "git_clone_or_generation"
            task["clone_command"] = {
                "workdir": ".",
                "argv": ["git", "clone", "--depth", "1", candidate["source_url"], target_path],
            }
            task["prepare_commands"] = [
                {
                    "workdir": "code/official",
                    "argv": [
                        ".venv/bin/python",
                        "scripts/prepare_socialmaze.py",
                        "upi",
                        "--pool-size",
                        "120",
                        "--train-n",
                        "60",
                        "--test-n",
                        "50",
                        "--variant",
                        "persona",
                        "--out-dir",
                        "data/socialmaze_upi",
                    ],
                }
            ]
            task["notes"].append("If shipped UPI data is insufficient, the official script will generate more examples through an LLM.")
        elif source_key == "tau_bench":
            task["intake_method"] = "git_clone"
            task["clone_command"] = {
                "workdir": ".",
                "argv": ["git", "clone", "--depth", "1", candidate["source_url"], target_path],
            }
            task["prepare_commands"] = [
                {
                    "workdir": "code/official",
                    "argv": [
                        ".venv/bin/python",
                        "scripts/prepare_tau_bench.py",
                        "--domain",
                        "retail",
                        "--train-n",
                        "30",
                        "--test-n",
                        "30",
                        "--out-dir",
                        "data/tau_bench",
                    ],
                }
            ]
        elif source_key == "chemllmbench":
            task["intake_method"] = "git_clone"
            task["clone_command"] = {
                "workdir": ".",
                "argv": ["git", "clone", "--depth", "1", candidate["source_url"], target_path],
            }
            task["prepare_commands"] = [
                {
                    "workdir": "code/official",
                    "argv": [
                        ".venv/bin/python",
                        "scripts/prepare_chemllmbench.py",
                        "--task",
                        "all",
                        "--train-n",
                        "30",
                        "--test-n",
                        "10",
                        "--out-dir",
                        "data/chemllmbench",
                    ],
                }
            ]
        tasks.append(task)

    payload = {
        "schema_version": "0.1",
        "scope": "External source intake plan for currently actionable SkillGen blocked targets",
        "run_dir": paths.run_dir.name,
        "storage_rule": "All cloned repositories, generated datasets, and caches must remain inside the project/run directory.",
        "tasks": tasks,
    }
    return payload


def render_external_source_intake_plan_md(payload: dict[str, Any]) -> str:
    lines = [
        "# External Source Intake Plan",
        "",
        payload["scope"],
        "",
        f"Storage rule: {payload['storage_rule']}",
        "",
        "## Tasks",
        "",
    ]
    for task in payload["tasks"]:
        lines.extend(
            [
                f"### {task['source_key']}",
                "",
                f"- Status: `{task['status']}`",
                f"- Source: `{task.get('source', 'unknown')}`",
                f"- Source type: `{task.get('source_type', 'unknown')}`",
                f"- Target: `{task.get('target_location', 'unknown')}`",
                f"- Requires network: `{task.get('requires_network', False)}`",
                f"- Requires API: `{task.get('requires_api', False)}`",
            ]
        )
        if task.get("clone_command"):
            command = " ".join(task["clone_command"]["argv"])
            lines.append(f"- Clone command: `{command}`")
        if task.get("prepare_commands"):
            lines.append("- Prepare command(s):")
            for command in task["prepare_commands"]:
                lines.append(f"  - `{command['workdir']}$ {' '.join(command['argv'])}`")
        if task.get("notes"):
            lines.append("- Notes:")
            lines.extend(f"  - {note}" for note in task["notes"])
        if task.get("reason"):
            lines.append(f"- Reason: {task['reason']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_benchmark_preparation_plan(run_dir: Path, intake_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = paths_for(run_dir)
    intake_plan = intake_plan or build_external_source_intake_plan(run_dir)
    tasks = []
    for task in intake_plan["tasks"]:
        for command in task.get("prepare_commands", []):
            tasks.append(
                {
                    "source_key": task["source_key"],
                    "status": "pending_source_intake",
                    "workdir": command["workdir"],
                    "argv": command["argv"],
                    "env": command.get("env", {}),
                    "expected_outputs": expected_preparation_outputs(task["source_key"]),
                }
            )
    payload = {
        "schema_version": "0.1",
        "scope": "Preparation commands for externally sourced SkillGen benchmark data",
        "run_dir": paths.run_dir.name,
        "tasks": tasks,
    }
    return payload


def expected_preparation_outputs(source_key: str) -> list[str]:
    mapping = {
        "livecodebench": ["code/official/data/livecodebench/release_v6_all.json"],
        "mcp_bench_all": [
            "code/official/data/mcp_bench_all/train_all_n40_seed42.json",
            "code/official/data/mcp_bench_all/test_all_n16_seed42.json",
        ],
        "socialmaze_upi": [
            "code/official/data/socialmaze_upi/train_n60_seed42.json",
            "code/official/data/socialmaze_upi/test_n50_seed42.json",
        ],
        "tau_bench": [
            "code/official/data/tau_bench/train_retail_n30_seed42.json",
            "code/official/data/tau_bench/test_retail_n30_seed42.json",
        ],
        "chemllmbench": ["code/official/data/chemllmbench"],
    }
    return mapping.get(source_key, [])


def write_external_source_intake_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    support = official_support_snapshot(run_dir)
    intake_plan = build_external_source_intake_plan(run_dir, support)
    preparation_plan = build_benchmark_preparation_plan(run_dir, intake_plan)
    write_json(paths.artifacts_dir / "external_source_intake_plan.json", intake_plan)
    write_text(paths.artifacts_dir / "external_source_intake_plan.md", render_external_source_intake_plan_md(intake_plan))
    write_json(paths.artifacts_dir / "benchmark_preparation_plan.json", preparation_plan)
    status = build_external_source_intake_status(run_dir, intake_plan, preparation_plan)
    write_json(paths.artifacts_dir / "external_source_intake_status.json", status)
    write_text(paths.artifacts_dir / "external_source_intake_status.md", render_external_source_intake_status_md(status))
    append_event(run_dir, "external_source_intake_planning", "completed", artifact="artifacts/external_source_intake_plan.json")
    return intake_plan


def build_external_source_intake_status(
    run_dir: Path,
    intake_plan: dict[str, Any] | None = None,
    preparation_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    intake_plan = intake_plan or build_external_source_intake_plan(run_dir)
    preparation_plan = preparation_plan or build_benchmark_preparation_plan(run_dir, intake_plan)
    prep_by_key: dict[str, list[dict[str, Any]]] = {}
    for task in preparation_plan.get("tasks", []):
        prep_by_key.setdefault(task["source_key"], []).append(task)

    rows = []
    for task in intake_plan["tasks"]:
        source_key = task["source_key"]
        target_path = task.get("target_path")
        local_target = paths.run_dir / target_path if target_path else None
        cloned = bool(local_target and local_target.exists())
        commit = git_value(["rev-parse", "HEAD"], local_target) if cloned and (local_target / ".git").exists() else None
        expected_outputs = [
            output
            for prep in prep_by_key.get(source_key, [])
            for output in prep.get("expected_outputs", [])
        ]
        output_status = [
            {
                "path": output,
                "exists": (paths.run_dir / output).exists(),
                "kind": "directory" if (paths.run_dir / output).is_dir() else "file",
            }
            for output in expected_outputs
        ]
        prepared = bool(output_status) and all(item["exists"] for item in output_status)
        partial_outputs = detect_partial_external_outputs(paths, source_key)
        if prepared:
            status = "prepared"
        elif cloned or partial_outputs:
            status = "source_intake_complete_preparation_partial"
        elif task.get("intake_method") == "huggingface_dataset" and output_status:
            status = "pending_download"
        else:
            status = "pending_source_intake"
        rows.append(
            {
                "source_key": source_key,
                "status": status,
                "source": task.get("source"),
                "target_path": target_path,
                "target_exists": cloned,
                "commit": commit,
                "expected_outputs": output_status,
                "partial_outputs": partial_outputs,
                "requires_api": task.get("requires_api", False),
                "remaining_blockers": external_source_remaining_blockers(source_key, status, partial_outputs),
            }
        )

    return {
        "schema_version": "0.1",
        "scope": "Observed external source intake and preparation status for SkillGen blocked targets",
        "run_dir": paths.run_dir.name,
        "status_counts": count_statuses(rows),
        "tasks": rows,
    }


def detect_partial_external_outputs(paths: RunPaths, source_key: str) -> list[str]:
    candidates = {
        "livecodebench": ["code/official/data/livecodebench/release_v6_all.json"],
        "socialmaze_upi": [
            "code/official/data/socialmaze_upi_smoke/train_n1_seed42.json",
            "code/official/data/socialmaze_upi_smoke/test_n1_seed42.json",
        ],
    }.get(source_key, [])
    return [path for path in candidates if (paths.run_dir / path).exists()]


def external_source_remaining_blockers(source_key: str, status: str, partial_outputs: list[str]) -> list[str]:
    if status == "prepared":
        return []
    if source_key == "socialmaze_upi" and partial_outputs:
        return [
            "Only smoke-size shipped UPI data has been prepared.",
            "Full 60/50 train/test UPI preparation still needs LLM generation or a larger official shipped pool.",
        ]
    if source_key == "livecodebench" and partial_outputs:
        return [
            "LiveCodeBench source data has been converted into one all-instances file.",
            "A train/test split contract is still needed before Table 1 execution.",
        ]
    return ["Source intake or benchmark preparation is not complete."]


def render_external_source_intake_status_md(payload: dict[str, Any]) -> str:
    lines = [
        "# External Source Intake Status",
        "",
        payload["scope"],
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Tasks", ""])
    for task in payload["tasks"]:
        lines.extend(
            [
                f"### {task['source_key']}",
                "",
                f"- Status: `{task['status']}`",
                f"- Source: `{task.get('source', 'unknown')}`",
                f"- Target exists: `{task['target_exists']}`",
            ]
        )
        if task.get("commit"):
            lines.append(f"- Commit: `{task['commit']}`")
        if task.get("expected_outputs"):
            lines.append("- Expected outputs:")
            lines.extend(f"  - `{item['path']}`: `{item['exists']}`" for item in task["expected_outputs"])
        if task.get("partial_outputs"):
            lines.append("- Partial outputs:")
            lines.extend(f"  - `{item}`" for item in task["partial_outputs"])
        if task.get("remaining_blockers"):
            lines.append("- Remaining blockers:")
            lines.extend(f"  - {item}" for item in task["remaining_blockers"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_canonical_benchmark_source_status(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    rows = []
    for source_key, spec in CANONICAL_BENCHMARK_SOURCES.items():
        target_path = paths.run_dir / spec["target_path"]
        target_exists = target_path.exists()
        commit = git_value(["rev-parse", "HEAD"], target_path) if target_exists and (target_path / ".git").exists() else None
        if target_exists:
            if spec["skillgen_compatibility_status"].startswith("bundled_data_already_ready"):
                status = "canonical_source_fetched_skillgen_data_ready"
            else:
                status = "canonical_source_fetched_not_skillgen_ready"
        else:
            status = "pending_canonical_source_fetch"
        rows.append(
            {
                "source_key": source_key,
                "status": status,
                "paper_benchmark": spec["paper_benchmark"],
                "source": spec["source"],
                "source_url": spec["source_url"],
                "target_path": spec["target_path"],
                "target_exists": target_exists,
                "commit": commit,
                "identity_basis": spec["identity_basis"],
                "skillgen_compatibility_status": spec["skillgen_compatibility_status"],
                "remaining_blockers": canonical_source_remaining_blockers(source_key, status),
            }
        )
    return {
        "schema_version": "0.1",
        "scope": "Canonical benchmark source fetch status for paper-named sources not fully covered by SkillGen official checkout",
        "run_dir": paths.run_dir.name,
        "status_counts": count_statuses(rows),
        "sources": rows,
    }


def canonical_source_remaining_blockers(source_key: str, status: str) -> list[str]:
    if source_key == "alfworld" and status == "canonical_source_fetched_not_skillgen_ready":
        return [
            "Canonical ALFWorld code is fetched, but SkillGen has no ALFWorld adapter in the current checkout.",
            "No paper-matching IOD/OOD train/test JSON split has been produced in SkillGen TaskInstance format.",
            "ALFWorld environment/data installation may require additional resources and a separate human-approved environment plan.",
        ]
    if status == "pending_canonical_source_fetch":
        return ["Canonical source code has not been fetched into the run directory yet."]
    return []


def render_canonical_benchmark_source_status_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Canonical Benchmark Source Status",
        "",
        payload["scope"],
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Sources", "", "| Source | Status | Target | Commit | Blockers |", "| --- | --- | --- | --- | --- |"])
    for row in payload["sources"]:
        blockers = "; ".join(row.get("remaining_blockers") or [])
        lines.append(
            f"| `{row['source_key']}` | `{row['status']}` | `{row['target_path']}` | `{row.get('commit') or ''}` | {table_cell(blockers or 'none')} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def canonical_source_fetched(run_dir: Path, source_key: str) -> bool:
    spec = CANONICAL_BENCHMARK_SOURCES.get(source_key)
    if not spec:
        return False
    return (paths_for(run_dir).run_dir / spec["target_path"]).exists()


def dataset_instance_count(path: Path) -> int | None:
    if not path.exists() or path.is_dir():
        return None
    try:
        data = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    instances = data.get("instances")
    if isinstance(instances, list):
        return len(instances)
    return None


def benchmark_train_command_template(train_dataset: str) -> dict[str, Any]:
    return {
        "workdir": "code/official",
        "argv": [
            ".venv/bin/python",
            "main.py",
            train_dataset,
            "--config",
            "{config_path}",
        ],
    }


def benchmark_eval_command_template(target_id: str, test_dataset: str, eval_n: int | str | None) -> dict[str, Any]:
    n_value = str(eval_n if eval_n is not None else "{eval_n}")
    return {
        "workdir": "code/official",
        "argv": [
            ".venv/bin/python",
            "eval_skill.py",
            "--skill-repo",
            "{skill_output_dir}",
            "--dataset",
            test_dataset,
            "--n",
            n_value,
            "--seed",
            "42",
            "--models",
            "{model_route}",
            "--judge-model",
            "{judge_model_route}",
            "--max-workers",
            "{max_workers}",
            "--output",
            f"../../artifacts/raw_benchmark_outputs/full_matrix/{target_id}/{{model_slug}}/eval_results.json",
        ],
    }


def benchmark_target(
    run_dir: Path,
    target_id: str,
    train_rel: str | None,
    test_rel: str | None,
    *,
    claim_ids: list[str],
    table1_row: str | None = None,
    status_if_missing: str = "blocked_missing_dataset",
    reason_if_missing: str = "Required train/test dataset files are missing.",
    notes: list[str] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    train_path = paths.official_dir / train_rel if train_rel else None
    test_path = paths.official_dir / test_rel if test_rel else None
    train_exists = bool(train_path and train_path.exists())
    test_exists = bool(test_path and test_path.exists())
    train_n = dataset_instance_count(train_path) if train_path else None
    test_n = dataset_instance_count(test_path) if test_path else None
    status = STATUS_READY_FOR_EXECUTION if train_exists and test_exists else status_if_missing
    blockers = []
    if status != STATUS_READY_FOR_EXECUTION:
        blockers.append(reason_if_missing)
    target = {
        "target_id": target_id,
        "claim_ids": claim_ids,
        "table1_row": table1_row,
        "status": status,
        "dataset": {
            "train": train_rel,
            "test": test_rel,
            "train_exists": train_exists,
            "test_exists": test_exists,
            "train_n": train_n,
            "test_n": test_n,
        },
        "runner_contract": {
            "requires_config_generation": True,
            "config_path_template": f"artifacts/generated_configs/{target_id}/{{model_slug}}.yaml",
            "skill_output_template": f"artifacts/raw_benchmark_outputs/full_matrix/{target_id}/{{model_slug}}/skill_output",
            "train_command_template": benchmark_train_command_template(train_rel or "{train_dataset}"),
            "eval_command_template": benchmark_eval_command_template(target_id, test_rel or "{test_dataset}", test_n),
            "expected_outputs": [
                f"artifacts/raw_benchmark_outputs/full_matrix/{target_id}/{{model_slug}}/eval_results.json",
                f"artifacts/raw_benchmark_outputs/full_matrix/{target_id}/{{model_slug}}/eval_results.token_usage.json",
                f"artifacts/raw_benchmark_outputs/full_matrix/{target_id}/{{model_slug}}/skill_output",
            ],
        },
        "requires": {
            "model_route_mapping": True,
            "api_keys": True,
            "network": True,
            "paid_api_or_token_budget": True,
            "human_gate_before_execution": True,
        },
        "execution_prerequisites": [
            "Use artifacts/model_route_mapping.template.json for paper-model display-name routes.",
            "Use human-approved API/network/token execution policy.",
            "Generate a per-target config file so artifacts do not overwrite another target.",
        ],
        "blockers": blockers,
        "notes": notes or [],
    }
    if table1_row is not None:
        target["paper_table1_entry_count"] = len(PAPER_MODEL_NAMES) if status == STATUS_READY_FOR_EXECUTION else 0
    return target


def build_model_route_mapping_template(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    paper_models = []
    for name in PAPER_MODEL_NAMES:
        resolution = PAPER_MODEL_ROUTE_RESOLUTIONS.get(name, {})
        paper_models.append(
            {
                "paper_display_name": name,
                "provider_route_id": resolution.get("provider_route_id"),
                "status": resolution.get("status", "unresolved"),
                "resolution_rule": resolution.get("basis", "Resolve against the chosen provider's current model IDs before execution; do not guess."),
            }
        )
    transfer_models = []
    for name in TRANSFER_MODEL_NAMES:
        resolution = PAPER_MODEL_ROUTE_RESOLUTIONS.get(name, {})
        transfer_models.append(
            {
                "paper_display_name": name,
                "provider_route_id": resolution.get("provider_route_id"),
                "status": resolution.get("status", "unresolved"),
                "resolution_rule": resolution.get("basis", "Resolve against the chosen provider's current model IDs before execution; do not guess."),
            }
        )
    all_rows = paper_models + transfer_models
    unresolved = [row["paper_display_name"] for row in all_rows if not row.get("provider_route_id")]
    equivalent = [
        row["paper_display_name"]
        for row in all_rows
        if row.get("status") == "route_resolved_equivalent"
    ]
    return {
        "schema_version": "0.1",
        "scope": "Resolved SkillGen paper model display names to executable provider route IDs",
        "run_dir": paths.run_dir.name,
        "status": "route_resolution_required" if unresolved else ("route_resolved_with_equivalent_deviations" if equivalent else "route_resolved_exact"),
        "provider_policy": (
            "OpenRouter can be used for chat routes, but it is not required by the paper. "
            "OpenAI is currently required by the official code for embeddings unless that dependency is patched and approved."
        ),
        "paper_table1_models": paper_models,
        "paper_transfer_models": transfer_models,
        "unresolved_models": sorted(set(unresolved)),
        "equivalent_deviation_models": sorted(set(equivalent)),
        "route_resolution_gate": {
            "required_before": ["full_table1_matrix", "transfer_matrix", "tau_bench_matrix", "chemllmbench_matrix"],
            "acceptance_criteria": [
                "Every paper display name maps to a current executable provider route.",
                "Any unavailable paper model is marked with an explicit replacement/deviation before execution.",
                "The chosen judge model route is recorded.",
            ],
        },
    }


def render_model_route_mapping_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Model Route Mapping Template",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Provider policy: {payload['provider_policy']}",
        "",
        f"Unresolved models: `{', '.join(payload.get('unresolved_models') or []) or 'none'}`",
        f"Equivalent route deviations: `{', '.join(payload.get('equivalent_deviation_models') or []) or 'none'}`",
        "",
        "## Table 1 Models",
        "",
        "| Paper display name | Provider route ID | Status |",
        "| --- | --- | --- |",
    ]
    for row in payload["paper_table1_models"]:
        lines.append(
            f"| `{row['paper_display_name']}` | `{row.get('provider_route_id') or ''}` | `{row['status']}` |"
        )
    lines.extend(["", "## Transfer Models", "", "| Paper display name | Provider route ID | Status |", "| --- | --- | --- |"])
    for row in payload["paper_transfer_models"]:
        lines.append(
            f"| `{row['paper_display_name']}` | `{row.get('provider_route_id') or ''}` | `{row['status']}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_benchmark_execution_plan(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    targets: list[dict[str, Any]] = []
    alfworld_status = (
        "blocked_canonical_code_fetched_missing_skillgen_contract"
        if canonical_source_fetched(run_dir, "alfworld")
        else "blocked_missing_official_artifact"
    )
    alfworld_reason = (
        "Canonical ALFWorld code is fetched, but no SkillGen-compatible ALFWorld adapter and paper-matching IOD/OOD train/test split contract exists."
        if canonical_source_fetched(run_dir, "alfworld")
        else "No official ALFWorld IOD/OOD train/test dataset has been identified in the current checkout."
    )
    table1_specs = [
        ("alfworld_iod", None, None, alfworld_status, alfworld_reason),
        ("alfworld_ood", None, None, alfworld_status, alfworld_reason),
        ("livecodebench", "data/livecodebench/release_v6_all.json", None, "blocked_pending_train_test_split_contract", "LiveCodeBench is prepared as one all-instances file; Table 1 needs an approved train/test split contract."),
        ("mcp_bench_all", "data/mcp_bench_all/train_all_n40_seed42.json", "data/mcp_bench_all/test_all_n16_seed42.json", "blocked_pending_source_preparation", "MCP-Bench all split train/test preparation is incomplete."),
        ("mcp_bench_single", "data/mcp_bench/train.json", "data/mcp_bench/test.json", "blocked_missing_dataset", "Bundled MCP-Bench single train/test data is missing."),
        ("mind2web", "data/mind2web/train.json", "data/mind2web/test.json", "blocked_missing_dataset", "Bundled Mind2Web train/test data is missing."),
        ("pubmedqa", "data/pubmedqa/train.json", "data/pubmedqa/test.json", "blocked_missing_dataset", "Bundled PubMedQA train/test data is missing."),
        ("scienceworld", "data/scienceworld/train.json", "data/scienceworld/test.json", "blocked_missing_dataset", "Bundled ScienceWorld train/test data is missing."),
        ("socialmaze_fts", "data/socialmaze/train.json", "data/socialmaze/test.json", "blocked_missing_dataset", "Bundled SocialMaze FTS train/test data is missing."),
        ("socialmaze_upi", "data/socialmaze_upi/train_n60_seed42.json", "data/socialmaze_upi/test_n50_seed42.json", "blocked_pending_full_size_generation", "Only SocialMaze UPI smoke data is prepared; full 60/50 train/test data is missing."),
    ]
    for row_id, train_rel, test_rel, missing_status, missing_reason in table1_specs:
        target = benchmark_target(
            run_dir,
            row_id,
            train_rel,
            test_rel,
            claim_ids=["claim_table1_average_gains_all_models", "claim_table1_entry_counts"],
            table1_row=row_id,
            status_if_missing=missing_status,
            reason_if_missing=missing_reason,
        )
        if row_id == "socialmaze_upi":
            smoke_train = "data/socialmaze_upi_smoke/train_n1_seed42.json"
            smoke_test = "data/socialmaze_upi_smoke/test_n1_seed42.json"
            target["alternate_smoke_target"] = benchmark_target(
                run_dir,
                "socialmaze_upi_smoke",
                smoke_train,
                smoke_test,
                claim_ids=["claim_table1_average_gains_all_models"],
                status_if_missing="blocked_missing_smoke_dataset",
                reason_if_missing="SocialMaze UPI smoke train/test data is missing.",
                notes=["Smoke data can exercise the adapter but cannot reproduce the full Table 1 UPI row."],
            )
        targets.append(target)

    targets.extend(
        [
            benchmark_target(
                run_dir,
                "tau_bench_retail",
                "data/tau_bench/train_retail_n30_seed42.json",
                "data/tau_bench/test_retail_n30_seed42.json",
                claim_ids=["claim_tau_bench_gate_activated"],
                status_if_missing="blocked_pending_source_preparation",
                reason_if_missing="tau-Bench retail train/test data is missing.",
            ),
            benchmark_target(
                run_dir,
                "chemllmbench_property_prediction",
                "data/chemllmbench/property_prediction_train.json",
                "data/chemllmbench/property_prediction_test.json",
                claim_ids=["claim_chemllmbench_useful_gains"],
                status_if_missing="blocked_pending_source_preparation",
                reason_if_missing="ChemLLMBench property prediction train/test data is missing.",
            ),
            benchmark_target(
                run_dir,
                "chemllmbench_yield_prediction",
                "data/chemllmbench/yield_prediction_train.json",
                "data/chemllmbench/yield_prediction_test.json",
                claim_ids=["claim_chemllmbench_useful_gains"],
                status_if_missing="blocked_pending_source_preparation",
                reason_if_missing="ChemLLMBench yield prediction train/test data is missing.",
            ),
        ]
    )

    ready_table1_rows = [
        target["table1_row"]
        for target in targets
        if target.get("table1_row") and target["status"] == STATUS_READY_FOR_EXECUTION
    ]
    payload = {
        "schema_version": "0.1",
        "scope": "Execution contract for actionable SkillGen blocked benchmark tests",
        "run_dir": paths.run_dir.name,
        "status": "ready_for_execution_where_structural_contract_exists",
        "storage_rule": "All generated configs, outputs, cloned sources, caches, and logs must remain inside this run directory.",
        "model_route_mapping_artifact": "artifacts/model_route_mapping.template.json",
        "approval_required_before_execution": True,
        "targets": targets,
        "status_counts": count_statuses(targets),
        "table1_matrix": {
            "required_rows": TABLE1_REQUIRED_ROWS,
            "ready_rows": ready_table1_rows,
            "paper_model_count": len(PAPER_MODEL_NAMES),
            "ready_entry_count": len(ready_table1_rows) * len(PAPER_MODEL_NAMES),
            "paper_entry_count": len(TABLE1_REQUIRED_ROWS) * len(PAPER_MODEL_NAMES),
        },
    }
    return payload


def render_benchmark_execution_plan_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Benchmark Execution Plan",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Storage rule: {payload['storage_rule']}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")
    matrix = payload["table1_matrix"]
    lines.extend(
        [
            "",
            "## Table 1 Coverage",
            "",
            f"- Structurally ready rows: `{', '.join(matrix['ready_rows']) or 'none'}`",
            f"- Structurally ready entries: `{matrix['ready_entry_count']}` of `{matrix['paper_entry_count']}`",
            "",
            "## Targets",
            "",
            "| Target | Status | Train/Test | Main blockers |",
            "| --- | --- | --- | --- |",
        ]
    )
    for target in payload["targets"]:
        dataset = target["dataset"]
        train_test = f"{dataset.get('train') or 'missing'} / {dataset.get('test') or 'missing'}"
        blockers = "; ".join(target.get("blockers") or ["none"])
        lines.append(f"| `{target['target_id']}` | `{target['status']}` | `{train_test}` | {table_cell(blockers)} |")
    return "\n".join(lines).rstrip() + "\n"


def build_transfer_runner_plan(run_dir: Path, benchmark_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = paths_for(run_dir)
    benchmark_plan = benchmark_plan or build_benchmark_execution_plan(run_dir)
    target_by_id = {target["target_id"]: target for target in benchmark_plan.get("targets", [])}
    rows = []
    for row_id in TRANSFER_BENCHMARK_ROWS:
        target = target_by_id.get(row_id)
        rows.append(
            {
                "benchmark_row": row_id,
                "dataset_status": target.get("status") if target else "blocked_missing_target_plan",
                "train": (target.get("dataset") or {}).get("train") if target else None,
                "test": (target.get("dataset") or {}).get("test") if target else None,
                "blockers": target.get("blockers", []) if target else ["No target plan exists for this transfer row."],
            }
        )
    source_target_pairs = [
        {
            "source_model": source_model,
            "evaluator_model": evaluator_model,
            "status": STATUS_READY_FOR_EXECUTION if source_model != evaluator_model else "diagonal_not_counted",
        }
        for source_model in TRANSFER_MODEL_NAMES
        for evaluator_model in TRANSFER_MODEL_NAMES
        if source_model != evaluator_model
    ]
    return {
        "schema_version": "0.1",
        "scope": "Cross-model transfer runner plan for SkillGen Figure 4",
        "run_dir": paths.run_dir.name,
        "paper_claim": "120 off-diagonal comparisons; 70% non-negative and 42% exceed +5 percentage points.",
        "benchmarks": rows,
        "paper_transfer_models": TRANSFER_MODEL_NAMES,
        "off_diagonal_pairs_per_benchmark": len(source_target_pairs),
        "planned_off_diagonal_comparisons": len(source_target_pairs) * len(TRANSFER_BENCHMARK_ROWS),
        "source_target_pair_template": source_target_pairs,
        "execution_contract": [
            "Generate or reuse a source-model skill for each transfer benchmark and source model.",
            "Evaluate that skill on the same benchmark test split with each non-identical evaluator model.",
            "Compare each transferred skill against the evaluator model's own no-skill baseline.",
            "Treat source skills deprecated by the verification gate as no-op skills, matching the paper description.",
        ],
        "remaining_blockers": [
            "ALFWorld OOD data is not available in the current official checkout.",
            "ALFWorld OOD canonical code is fetched but still lacks a SkillGen-compatible adapter/split contract.",
        ],
    }


def render_transfer_runner_plan_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Cross-Model Transfer Runner Plan",
        "",
        payload["scope"],
        "",
        f"Paper claim: {payload['paper_claim']}",
        "",
        f"Planned off-diagonal comparisons: `{payload['planned_off_diagonal_comparisons']}`",
        "",
        "## Benchmarks",
        "",
        "| Benchmark | Dataset status | Train/Test | Blockers |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["benchmarks"]:
        train_test = f"{row.get('train') or 'missing'} / {row.get('test') or 'missing'}"
        lines.append(
            f"| `{row['benchmark_row']}` | `{row['dataset_status']}` | `{train_test}` | {table_cell('; '.join(row.get('blockers') or []))} |"
        )
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(f"- {item}" for item in payload["remaining_blockers"])
    return "\n".join(lines).rstrip() + "\n"


def current_token_log_inventory(paths: RunPaths) -> list[dict[str, Any]]:
    logs = []
    if paths.raw_dir.exists():
        for path in sorted(paths.raw_dir.rglob("*token_usage*.json")):
            logs.append(
                {
                    "path": rel(path, paths.run_dir),
                    "total_tokens": sum_token_usage(path),
                    "scope": "smoke_or_existing_run",
                }
            )
    return logs


def build_token_log_plan(run_dir: Path, benchmark_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = paths_for(run_dir)
    benchmark_plan = benchmark_plan or build_benchmark_execution_plan(run_dir)
    target_by_id = {target["target_id"]: target for target in benchmark_plan.get("targets", [])}
    groups = []
    for benchmark in TOKEN_COST_BENCHMARKS:
        target_id = benchmark["target_id"]
        target = target_by_id.get(target_id)
        if target is None and target_id == "mcp_bench":
            target = target_by_id.get("mcp_bench_single") or target_by_id.get("mcp_bench_all")
        groups.append(
            {
                **benchmark,
                "dataset_status": target.get("status") if target else "blocked_missing_target_plan",
                "planned_train_log_glob": f"artifacts/raw_benchmark_outputs/full_matrix/{target_id}/*/artifacts/runs/**/token_usage.json",
                "planned_eval_log_glob": f"artifacts/raw_benchmark_outputs/full_matrix/{target_id}/*/eval_results.token_usage.json",
            }
        )
    return {
        "schema_version": "0.1",
        "scope": "Token-log collection and aggregation plan for SkillGen Table 4",
        "run_dir": paths.run_dir.name,
        "paper_claim": "Train token cost ranges from 2.2M to 10.2M tokens; mean is 5.6M tokens and mean cost is about $8.2 per generated skill.",
        "benchmark_groups": groups,
        "current_observed_logs": current_token_log_inventory(paths),
        "aggregation_contract": [
            "Collect one-time construction token logs from each generated skill run.",
            "Collect no-skill and with-skill eval token logs from eval_results.token_usage.json.",
            "Group logs by paper benchmark name before comparing to Table 4.",
            "Do not mix AIME smoke token logs into the Table 4 claim comparison.",
        ],
        "remaining_blockers": [
            "Full benchmark runs have not produced Table 4 grouped token logs yet.",
        ],
    }


def render_token_log_plan_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Token Log Plan",
        "",
        payload["scope"],
        "",
        f"Paper claim: {payload['paper_claim']}",
        "",
        "## Benchmark Groups",
        "",
        "| Benchmark | Dataset status | Paper train M tok | BASE tok/call | SKILL tok/call |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["benchmark_groups"]:
        lines.append(
            f"| `{row['paper_name']}` | `{row['dataset_status']}` | `{row['paper_train_mtok']}` | `{row['paper_base_tokens_per_call']}` | `{row['paper_skill_tokens_per_call']}` |"
        )
    lines.extend(["", "## Current Observed Logs", ""])
    if payload["current_observed_logs"]:
        for log in payload["current_observed_logs"]:
            lines.append(f"- `{log['path']}`: `{log.get('total_tokens')}` tokens")
    else:
        lines.append("- No token logs found yet.")
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(f"- {item}" for item in payload["remaining_blockers"])
    return "\n".join(lines).rstrip() + "\n"


def write_execution_planning_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    canonical_source_status = build_canonical_benchmark_source_status(run_dir)
    model_routes = build_model_route_mapping_template(run_dir)
    benchmark_plan = build_benchmark_execution_plan(run_dir)
    transfer_plan = build_transfer_runner_plan(run_dir, benchmark_plan)
    token_plan = build_token_log_plan(run_dir, benchmark_plan)
    write_json(paths.artifacts_dir / "canonical_benchmark_source_status.json", canonical_source_status)
    write_text(
        paths.artifacts_dir / "canonical_benchmark_source_status.md",
        render_canonical_benchmark_source_status_md(canonical_source_status),
    )
    write_json(paths.artifacts_dir / "model_route_mapping.template.json", model_routes)
    write_text(paths.artifacts_dir / "model_route_mapping.template.md", render_model_route_mapping_md(model_routes))
    write_json(paths.artifacts_dir / "benchmark_execution_plan.json", benchmark_plan)
    write_text(paths.artifacts_dir / "benchmark_execution_plan.md", render_benchmark_execution_plan_md(benchmark_plan))
    write_json(paths.artifacts_dir / "transfer_runner_plan.json", transfer_plan)
    write_text(paths.artifacts_dir / "transfer_runner_plan.md", render_transfer_runner_plan_md(transfer_plan))
    write_json(paths.artifacts_dir / "token_log_plan.json", token_plan)
    write_text(paths.artifacts_dir / "token_log_plan.md", render_token_log_plan_md(token_plan))
    append_event(run_dir, "benchmark_execution_planning", "completed", artifact="artifacts/benchmark_execution_plan.json")
    return {
        "model_route_mapping": model_routes,
        "benchmark_execution_plan": benchmark_plan,
        "transfer_runner_plan": transfer_plan,
        "token_log_plan": token_plan,
        "canonical_benchmark_source_status": canonical_source_status,
    }


def build_all_claim_verification_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    paper_text = ""
    paper_parse_path = paths.artifacts_dir / "paper_parse.md"
    if paper_parse_path.exists():
        paper_text = paper_parse_path.read_text(encoding="utf-8", errors="replace")
    claims = skillgen_all_claims(paper_text)
    support = official_support_snapshot(run_dir)
    benchmark = read_json(paths.artifacts_dir / "benchmark_results.json") if (paths.artifacts_dir / "benchmark_results.json").exists() else {}

    matrix = []
    for claim in claims:
        status, blockers, evidence = all_claim_status(claim, support, benchmark)
        external_candidates = supported_external_candidates(
            support,
            external_source_keys_for_claim(claim["id"], support),
        )
        matrix.append(
            {
                "claim_id": claim["id"],
                "claim_type": claim["claim_type"],
                "verification_mode": claim["verification_mode"],
                "status": status,
                "blockers": blockers,
                "evidence": evidence,
                "external_source_candidates": external_candidates,
                "next_step": next_step_for_claim(
                    status,
                    claim["verification_mode"],
                    bool(external_candidates),
                    claim_id=claim["id"],
                    support=support,
                ),
            }
        )

    payload = {
        "schema_version": "0.2",
        "scope": "SkillGen paper major empirical claims",
        "claim_count": len(claims),
        "claims": claims,
    }
    matrix_payload = {
        "schema_version": "0.2",
        "scope": "Claim-by-claim verification status for SkillGen",
        "status_counts": count_statuses(matrix),
        "official_support": support,
        "executable_targets": build_executable_target_inventory(support),
        "claims": matrix,
    }
    write_json(paths.artifacts_dir / "all_claims.json", payload)
    write_text(paths.artifacts_dir / "all_claims.md", render_all_claims_md(claims))
    write_json(paths.artifacts_dir / "all_claim_verification_matrix.json", matrix_payload)
    write_text(paths.artifacts_dir / "all_claim_verification_matrix.md", render_all_claim_matrix_md(matrix_payload))
    append_event(run_dir, "all_claim_verification_planning", "completed", artifact="artifacts/all_claim_verification_matrix.json")
    return matrix_payload


def prepare_automation_artifacts(run_dir: Path, official_source: Path | None = None, allow_clone: bool = False) -> Path:
    paths = paths_for(run_dir)
    paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    paths.raw_dir.mkdir(parents=True, exist_ok=True)
    code_manifest = code_intake(run_dir, official_source=official_source, allow_clone=allow_clone)
    extract_official_instructions(run_dir)
    smoke_assets = prepare_smoke_assets(run_dir)
    contract = build_verification_contract(run_dir)
    plan = build_command_plan(run_dir)
    write_automation_hardcoding_disclosures(run_dir)
    intake_plan = write_external_source_intake_artifacts(run_dir)
    execution_plans = write_execution_planning_artifacts(run_dir)
    all_claims = build_all_claim_verification_artifacts(run_dir)
    write_json(
        paths.artifacts_dir / "automation_state.json",
        {
            "schema_version": "0.1",
            "status": "ready_for_approval" if code_manifest["status"] == "intake_complete" else "blocked_missing_official_code",
            "code_intake": code_manifest["status"],
            "smoke_assets": smoke_assets["status"],
            "contract": contract["target_id"],
            "command_plan": plan["status"],
            "all_claim_status_counts": all_claims["status_counts"],
            "external_source_intake_task_count": len(intake_plan["tasks"]),
            "benchmark_execution_target_counts": execution_plans["benchmark_execution_plan"]["status_counts"],
        },
    )
    render_report(run_dir)
    return run_dir


def create_automated_run(
    paper: Path,
    output_root: Path,
    run_id: str | None = None,
    official_source: Path | None = None,
    allow_clone: bool = False,
) -> Path:
    run_dir = run_demo(paper, output_root, run_id)
    prepare_automation_artifacts(run_dir, official_source=official_source, allow_clone=allow_clone)
    return run_dir


def approval_status(run_dir: Path, phase: str) -> tuple[bool, list[str]]:
    paths = paths_for(run_dir)
    approval_path = paths.artifacts_dir / "approval.json"
    if not approval_path.exists():
        return False, ["missing artifacts/approval.json"]
    approval = read_json(approval_path)
    reasons: list[str] = []
    if not approval.get("command_plan_approved"):
        reasons.append("command_plan_approved is not true")
    if TARGET_ID not in approval.get("approved_targets", []):
        reasons.append(f"{TARGET_ID} is not approved")
    if phase == "install" and not approval.get("allow_install"):
        if not approval.get("allow_project_local_install"):
            reasons.append("neither allow_install nor allow_project_local_install is true")
        if approval.get("dependency_scope_required") not in {None, "inside_project_directory"}:
            reasons.append("dependency_scope_required must be inside_project_directory")
    if phase == "benchmark" and not approval.get("allow_benchmark"):
        reasons.append("allow_benchmark is not true")
    if not approval.get("allow_network"):
        reasons.append("allow_network is not true")
    if phase == "benchmark" and not approval.get("allow_paid_api"):
        reasons.append("allow_paid_api is not true")
    max_cost = approval.get("max_cost_usd")
    if phase == "benchmark" and (not isinstance(max_cost, (int, float)) or max_cost <= 0):
        reasons.append("max_cost_usd must be a positive number")

    env = command_env(run_dir)
    missing_keys = [name for name in ["OPENROUTER_API_KEY", "OPENAI_API_KEY"] if not env.get(name)]
    if phase == "benchmark" and missing_keys:
        reasons.append("missing required env vars: " + ", ".join(missing_keys))
    return not reasons, reasons


def approval_policy(run_dir: Path) -> dict[str, Any]:
    approval_path = paths_for(run_dir).artifacts_dir / "approval.json"
    if not approval_path.exists():
        return {}
    return read_json(approval_path)


def approved_retry_attempts(run_dir: Path) -> int:
    approval = approval_policy(run_dir)
    if not approval.get("auto_retry_approved"):
        return 0
    attempts = approval.get("max_retry_attempts", 0)
    return max(0, int(attempts)) if isinstance(attempts, int) else 0


def install_already_succeeded(run_dir: Path) -> bool:
    paths = paths_for(run_dir)
    environment_path = paths.artifacts_dir / "environment.json"
    if not environment_path.exists():
        return False
    environment = read_json(environment_path)
    if environment.get("status") != "install_succeeded":
        return False
    venv_python = paths.official_dir / ".venv" / "bin" / "python"
    uv_cache = paths.official_dir / ".uv-cache"
    return venv_python.exists() and uv_cache.exists()


def write_approval_artifact(
    run_dir: Path,
    approved_by: str,
    max_cost_usd: float,
    notes: str,
    approval_source: str = "manual_artifact",
    allow_install: bool = True,
    allow_benchmark: bool = True,
    allow_network: bool = True,
    allow_paid_api: bool = True,
    allow_project_local_install: bool = True,
    skip_install_if_environment_present: bool = True,
    auto_retry_approved: bool = True,
    max_retry_attempts: int = 1,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    approval = {
        "schema_version": "0.2",
        "command_plan_approved": True,
        "approved_targets": [TARGET_ID],
        "allow_install": allow_install,
        "allow_benchmark": allow_benchmark,
        "allow_network": allow_network,
        "allow_paid_api": allow_paid_api,
        "allow_project_local_install": allow_project_local_install,
        "skip_install_if_environment_present": skip_install_if_environment_present,
        "auto_retry_approved": auto_retry_approved,
        "max_retry_attempts": max_retry_attempts,
        "dependency_scope_required": "inside_project_directory",
        "max_cost_usd": max_cost_usd,
        "approved_by": approved_by,
        "approval_source": approval_source,
        "approved_at": utc_now(),
        "notes": notes,
    }
    write_json(paths.artifacts_dir / "approval.json", approval)
    write_text(
        paths.artifacts_dir / "human_command_review.md",
        "# Human Command Review\n\n"
        "Status: `approved`\n\n"
        f"- Approved target: `{TARGET_ID}`\n"
        f"- Approval source: `{approval_source}`\n"
        f"- Approved by: `{approved_by}`\n"
        f"- Max cost USD: `{max_cost_usd}`\n"
        f"- Project-local install allowed: `{allow_project_local_install}`\n"
        f"- Auto retry approved steps: `{auto_retry_approved}`\n"
        f"- Max retry attempts: `{max_retry_attempts}`\n"
        f"- Notes: {notes}\n",
    )
    append_event(run_dir, "human_command_approval", "approved", artifact="artifacts/approval.json", approval_source=approval_source)
    append_decision(run_dir, "approve_command_plan", approval_source=approval_source, target_id=TARGET_ID)
    return approval


def write_blocked_execution(run_dir: Path, phase: str, reasons: list[str]) -> None:
    paths = paths_for(run_dir)
    append_event(run_dir, f"{phase}_execution", STATUS_BLOCKED, reasons=reasons)
    append_decision(run_dir, f"block_{phase}_execution", reasons=reasons)
    failure_path = paths.artifacts_dir / "failure_modes.md"
    current = failure_path.read_text(encoding="utf-8") if failure_path.exists() else "# Failure Modes And Blockers\n"
    current = current.rstrip() + "\n\n"
    current += f"## {phase.title()} Execution Blocked\n\n"
    current += "\n".join(f"- {reason}" for reason in reasons) + "\n"
    write_text(failure_path, current)


def write_command_output(path: Path, argv: list[str], content: str, append: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "$ " + " ".join(argv) + "\n"
    body = header + content
    if append and path.exists():
        path.write_text(path.read_text(encoding="utf-8") + "\n" + body, encoding="utf-8")
    else:
        path.write_text(body, encoding="utf-8")


def run_command(
    run_dir: Path,
    command: dict[str, Any],
    stdout_path: Path,
    stderr_path: Path,
    append_logs: bool = False,
) -> dict[str, Any]:
    cwd = run_dir / command.get("workdir", ".")
    env_values = command.get("env", {})
    env = command_env(run_dir, env_values)
    started = utc_now()
    result = subprocess.run(
        command["argv"],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    write_command_output(stdout_path, command["argv"], result.stdout, append_logs)
    write_command_output(stderr_path, command["argv"], result.stderr, append_logs)
    return {
        "argv": command["argv"],
        "workdir": rel(cwd, run_dir),
        "stdout": rel(stdout_path, run_dir),
        "stderr": rel(stderr_path, run_dir),
        "started_at": started,
        "ended_at": utc_now(),
        "exit_code": result.returncode,
    }


def run_command_with_retries(
    run_dir: Path,
    command: dict[str, Any],
    stdout_path: Path,
    stderr_path: Path,
    append_logs: bool = False,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    result = run_command(run_dir, command, stdout_path, stderr_path, append_logs=append_logs)
    attempts.append(result)
    retry_count = approved_retry_attempts(run_dir)
    for retry_index in range(1, retry_count + 1):
        if result["exit_code"] == 0:
            break
        append_event(
            run_dir,
            "approved_command_retry",
            "retrying",
            retry_index=retry_index,
            max_retry_attempts=retry_count,
            argv=command["argv"],
        )
        result = run_command(run_dir, command, stdout_path, stderr_path, append_logs=True)
        attempts.append(result)
    if len(attempts) == 1:
        return result
    final = dict(result)
    final["attempts"] = attempts
    return final


def execute_install(run_dir: Path) -> str:
    allowed, reasons = approval_status(run_dir, "install")
    if not allowed:
        write_blocked_execution(run_dir, "install", reasons)
        return STATUS_BLOCKED
    paths = paths_for(run_dir)
    plan = read_json(paths.artifacts_dir / "command_plan.json")
    commands = plan["commands"]
    runs = [
        run_command_with_retries(
            run_dir,
            commands["create_venv"],
            paths.outputs_dir / "install_stdout.txt",
            paths.outputs_dir / "install_stderr.txt",
        ),
        run_command_with_retries(
            run_dir,
            commands["install"],
            paths.outputs_dir / "install_stdout.txt",
            paths.outputs_dir / "install_stderr.txt",
            append_logs=True,
        ),
    ]
    status = "install_succeeded" if all(item["exit_code"] == 0 for item in runs) else STATUS_FAILED_TO_RUN
    write_json(
        paths.artifacts_dir / "environment.json",
        {
            "schema_version": "0.3",
            "status": status,
            "python_venv": "code/official/.venv",
            "uv_cache": "code/official/.uv-cache",
            "dependency_scope": "inside_project_directory",
            "api_key_values_printed": False,
            "commands": runs,
        },
    )
    append_event(run_dir, "install_execution", status, artifact="artifacts/environment.json")
    return status


def latest_subdir(path: Path) -> Path | None:
    if not path.exists():
        return None
    candidates = [child for child in path.iterdir() if child.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda child: child.stat().st_mtime)


def find_skill_output_dir(run_dir: Path) -> Path | None:
    skill_root = paths_for(run_dir).raw_dir / "skill_output"
    latest = latest_subdir(skill_root)
    if latest is not None:
        return latest
    return None


def execute_benchmark(run_dir: Path) -> str:
    allowed, reasons = approval_status(run_dir, "benchmark")
    if not allowed:
        write_blocked_execution(run_dir, "benchmark", reasons)
        return STATUS_BLOCKED
    paths = paths_for(run_dir)
    plan = read_json(paths.artifacts_dir / "command_plan.json")
    commands = plan["commands"]

    skill_output_dir = find_skill_output_dir(run_dir)
    train: dict[str, Any] | None = None
    if skill_output_dir is None:
        train = run_command_with_retries(run_dir, commands["train"], paths.outputs_dir / "benchmark_stdout.txt", paths.outputs_dir / "benchmark_stderr.txt")
        if train["exit_code"] != 0:
            append_event(run_dir, "benchmark_train_execution", STATUS_FAILED_TO_RUN, command=train)
            return STATUS_FAILED_TO_RUN
        skill_output_dir = find_skill_output_dir(run_dir)
    else:
        append_event(
            run_dir,
            "benchmark_train_execution",
            "reused_existing_skill_output",
            skill_output=rel(skill_output_dir, paths.run_dir),
        )

    if skill_output_dir is None:
        append_event(run_dir, "benchmark_eval_execution", STATUS_NOT_TESTABLE, reason="missing skill_output directory")
        return STATUS_NOT_TESTABLE

    relative_skill_path = rel(skill_output_dir, paths.official_dir)
    eval_command = dict(commands["eval_template"])
    eval_command["argv"] = [part.format(skill_output_dir=relative_skill_path) for part in eval_command["argv"]]
    eval_result = run_command_with_retries(run_dir, eval_command, paths.raw_dir / "eval_stdout.txt", paths.raw_dir / "eval_stderr.txt")
    status = "benchmark_succeeded" if eval_result["exit_code"] == 0 else STATUS_FAILED_TO_RUN
    append_event(run_dir, "benchmark_execution", status, train_command=train, eval_command=eval_result)
    return status


def sum_token_usage(path: Path) -> int | None:
    if not path.exists():
        return None
    data = read_json(path)
    if isinstance(data, list):
        return sum(int(item.get("total_tokens", 0) or 0) for item in data)
    if isinstance(data, dict):
        return int(data.get("total_tokens", 0) or 0)
    return None


def latest_file(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = sorted(root.rglob(pattern), key=lambda path: path.stat().st_mtime)
    return files[-1] if files else None


def latest_dir(root: Path) -> Path | None:
    if not root.exists():
        return None
    dirs = sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.stat().st_mtime)
    return dirs[-1] if dirs else None


def parse_skill_id(skill_output_dir: Path | None) -> str | None:
    if skill_output_dir is None or not skill_output_dir.exists():
        return None
    json_files = [path for path in skill_output_dir.glob("*.json") if path.name not in {"skill_analysis.json", "skill_analysis_summary.json"}]
    if not json_files:
        return None
    return json_files[0].stem


def parse_skill_record(skill_output_dir: Path | None) -> dict[str, Any]:
    if skill_output_dir is None or not skill_output_dir.exists():
        return {}
    json_files = [
        path
        for path in skill_output_dir.glob("*.json")
        if path.name not in {"skill_analysis.json", "skill_analysis_summary.json"}
    ]
    if not json_files:
        return {}
    return read_json(json_files[0])


def additional_target_claim_status(target: dict[str, Any]) -> str:
    train = target.get("train") or {}
    train_verification = train.get("construction_verification") or {}
    eval_result = target.get("eval") or {}
    skill_rejected = bool(target.get("skill_rejected")) or str(train.get("skill_status", "")).lower() == "deprecated"

    if target.get("status") == STATUS_FAILED_TO_RUN:
        return STATUS_FAILED_TO_RUN
    if train_verification and train_verification.get("passed") is False:
        return STATUS_NOT_REPRODUCED
    if skill_rejected:
        return STATUS_NOT_REPRODUCED
    baseline_acc = eval_result.get("baseline_acc")
    skill_acc = eval_result.get("skill_acc")
    net_gain = eval_result.get("net_gain")
    if isinstance(baseline_acc, (int, float)) and isinstance(skill_acc, (int, float)):
        if skill_acc > baseline_acc and isinstance(net_gain, int) and net_gain > 0:
            return STATUS_PARTIALLY_REPRODUCED
        return STATUS_NOT_REPRODUCED
    return STATUS_READY_FOR_EXECUTION


def parse_additional_skillgen_target(paths: RunPaths, target_id: str, dataset_label: str) -> dict[str, Any] | None:
    root = paths.artifacts_dir / "raw_benchmark_outputs" / target_id
    if not root.exists():
        return None

    artifact_run = latest_dir(root / "artifacts" / "runs")
    verification_summary_path = latest_file(artifact_run / "verification" if artifact_run else Path("__missing__"), "verification_summary.json")
    verification_summary = read_json(verification_summary_path) if verification_summary_path else {}
    verification_result = verification_summary.get("result") or {}
    skill_output_dir = latest_dir(root / "skill_output")
    skill_record = parse_skill_record(skill_output_dir)
    skill_id = skill_record.get("skill_id") or parse_skill_id(skill_output_dir)
    eval_path = root / "eval_results.json"
    eval_data = read_json(eval_path) if eval_path.exists() else {}
    first_eval = (eval_data.get("results") or [{}])[0]
    train_token_usage = sum_token_usage(latest_file(root / "artifacts" / "runs", "token_usage.json") or Path("__missing__"))
    eval_token_usage = sum_token_usage(root / "eval_results.token_usage.json")
    status = "official_code_eval_completed" if eval_path.exists() else "official_code_train_completed"

    target = {
        "target_id": target_id,
        "dataset_label": dataset_label,
        "status": status,
        "skill_id": skill_id,
        "skill_rejected": bool(eval_data.get("skill_rejected")) or str(skill_record.get("status", "")).lower() == "deprecated",
        "train": {
            "artifact_run": rel(artifact_run, paths.run_dir) if artifact_run else None,
            "skill_output": rel(skill_output_dir, paths.run_dir) if skill_output_dir else None,
            "skill_status": skill_record.get("status") or eval_data.get("skill_status"),
            "construction_verification": {
                "paired_n": verification_result.get("paired_n"),
                "baseline_acc": verification_result.get("baseline_acc"),
                "skill_acc": verification_result.get("skill_acc"),
                "repair": verification_result.get("repair_count"),
                "regression": verification_result.get("regression_count"),
                "net_gain": verification_result.get("net_gain"),
                "passed": verification_result.get("passed"),
                "diagnostic_summary": verification_result.get("diagnostic_summary"),
            },
            "token_usage_total": train_token_usage,
        },
        "eval": {
            "dataset": eval_data.get("dataset"),
            "model": first_eval.get("model"),
            "n_instances": first_eval.get("n_instances"),
            "baseline_acc": first_eval.get("baseline_acc"),
            "skill_acc": first_eval.get("skill_acc"),
            "delta_acc": first_eval.get("delta_acc"),
            "repair": first_eval.get("repair"),
            "regression": first_eval.get("regression"),
            "net_gain": first_eval.get("net_gain"),
            "blank_filter": first_eval.get("blank_filter"),
            "token_usage_total": eval_token_usage,
        },
        "raw_outputs": {
            "eval_results": rel(eval_path, paths.run_dir) if eval_path.exists() else None,
            "eval_token_usage": rel(root / "eval_results.token_usage.json", paths.run_dir)
            if (root / "eval_results.token_usage.json").exists()
            else None,
            "verification_summary": rel(verification_summary_path, paths.run_dir) if verification_summary_path else None,
        },
    }
    target["claim_status"] = additional_target_claim_status(target)
    return target


def parse_additional_skillgen_targets(paths: RunPaths) -> dict[str, Any]:
    targets = {}
    specs = {
        "tau_bench_retail": "tau-Bench retail smoke execution",
        "chemllmbench_property_prediction": "ChemLLMBench property prediction smoke execution",
        "chemllmbench_yield_prediction": "ChemLLMBench yield prediction smoke execution",
        "scienceworld_token": "ScienceWorld Table 4 token smoke execution",
        "pubmedqa_token": "PubMedQA Table 4 token smoke execution",
        "mind2web_token": "Mind2Web Table 4 token smoke execution",
        "mcp_bench_token": "MCPBench Table 4 token smoke execution",
    }
    for target_id, label in specs.items():
        parsed = parse_additional_skillgen_target(paths, target_id, label)
        if parsed:
            targets[target_id] = parsed
    return targets


def parse_results(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    eval_path = paths.raw_dir / "eval_results.json"
    if not eval_path.exists():
        result = {"schema_version": "0.3", "status": STATUS_NOT_TESTABLE, "reason": "missing eval_results.json"}
        write_json(paths.artifacts_dir / "benchmark_results.json", result)
        write_text(paths.artifacts_dir / "benchmark_results.md", "# Benchmark Results\n\nStatus: `not_testable`\n\nMissing `eval_results.json`.\n")
        append_event(run_dir, "result_parsing", STATUS_NOT_TESTABLE, reason="missing eval_results.json")
        return result

    eval_data = read_json(eval_path)
    first = (eval_data.get("results") or [{}])[0]
    token_usage_total = sum_token_usage(paths.raw_dir / "eval_results.token_usage.json")
    train_token_usage = sum_token_usage(latest_file(paths.raw_dir / "artifacts" / "runs", "token_usage.json") or Path("__missing__"))
    verification_summary_path = latest_file(paths.raw_dir / "artifacts" / "runs", "verification_summary.json")
    verification_summary = read_json(verification_summary_path) if verification_summary_path else {}
    verification_result = verification_summary.get("result", {})
    skill_output_dir = find_skill_output_dir(run_dir)
    skill_id = eval_data.get("skill_id") or parse_skill_id(skill_output_dir)

    result = {
        "schema_version": "0.3",
        "status": "official_code_smoke_completed",
        "scope": "AIME smoke validation only; not SkillGen Table 1 reproduction",
        "target_id": TARGET_ID,
        "skill_id": skill_id,
        "train": {
            "skill_output": rel(skill_output_dir, paths.run_dir) if skill_output_dir else None,
            "construction_verification": {
                "paired_n": verification_result.get("paired_n"),
                "baseline_acc": verification_result.get("baseline_acc"),
                "skill_acc": verification_result.get("skill_acc"),
                "repair": verification_result.get("repair_count"),
                "regression": verification_result.get("regression_count"),
                "net_gain": verification_result.get("net_gain"),
                "passed": verification_result.get("passed"),
            },
            "token_usage_total": train_token_usage,
        },
        "eval": {
            "dataset": eval_data.get("dataset"),
            "model": first.get("model"),
            "n_instances": first.get("n_instances"),
            "baseline_acc": first.get("baseline_acc"),
            "skill_acc": first.get("skill_acc"),
            "delta_acc": first.get("delta_acc"),
            "repair": first.get("repair"),
            "regression": first.get("regression"),
            "net_gain": first.get("net_gain"),
            "blank_filter": first.get("blank_filter"),
            "token_usage_total": token_usage_total,
        },
        "raw_outputs": {
            "eval_results": "artifacts/raw_benchmark_outputs/skillgen_aime_smoke/eval_results.json",
            "eval_token_usage": "artifacts/raw_benchmark_outputs/skillgen_aime_smoke/eval_results.token_usage.json",
            "verification_summary": rel(verification_summary_path, paths.run_dir) if verification_summary_path else None,
        },
        "additional_targets": parse_additional_skillgen_targets(paths),
    }
    write_json(paths.artifacts_dir / "benchmark_results.json", result)
    write_text(paths.artifacts_dir / "benchmark_results.md", render_benchmark_results_md(result))
    append_event(run_dir, "result_parsing", "completed", artifact="artifacts/benchmark_results.json")
    return result


def percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%"
    return "unavailable"


def render_benchmark_results_md(result: dict[str, Any]) -> str:
    train = result.get("train", {})
    train_verification = train.get("construction_verification", {})
    eval_result = result.get("eval", {})
    lines = [f"""# Benchmark Results

Status: `{result.get("status")}`

## Scope

This is an official-code AIME smoke validation. It is not a reproduction of the full SkillGen Table 1 claim.

## Construction-Time Verification

- Skill ID: `{result.get("skill_id")}`
- Paired N: `{train_verification.get("paired_n")}`
- Baseline accuracy: `{percent(train_verification.get("baseline_acc"))}`
- Skill accuracy: `{percent(train_verification.get("skill_acc"))}`
- Repairs: `{train_verification.get("repair")}`
- Regressions: `{train_verification.get("regression")}`
- Net gain: `{train_verification.get("net_gain")}`
- Verification passed: `{train_verification.get("passed")}`
- Training token usage: `{train.get("token_usage_total")}`

## Held-Out Smoke Evaluation

- Model: `{eval_result.get("model")}`
- Paired N: `{eval_result.get("n_instances")}`
- Baseline accuracy: `{percent(eval_result.get("baseline_acc"))}`
- Skill accuracy: `{percent(eval_result.get("skill_acc"))}`
- Accuracy delta: `{percent(eval_result.get("delta_acc"))}`
- Repairs: `{eval_result.get("repair")}`
- Regressions: `{eval_result.get("regression")}`
- Net gain: `{eval_result.get("net_gain")}`
- Eval token usage: `{eval_result.get("token_usage_total")}`
"""]
    additional_targets = result.get("additional_targets") or {}
    if additional_targets:
        lines.extend(["## Additional Target Executions", ""])
        for target_id, target in sorted(additional_targets.items()):
            target_train = target.get("train") or {}
            target_verification = target_train.get("construction_verification") or {}
            target_eval = target.get("eval") or {}
            lines.extend(
                [
                    f"### {target_id}",
                    "",
                    f"- Claim status: `{target.get('claim_status')}`",
                    f"- Execution status: `{target.get('status')}`",
                    f"- Skill ID: `{target.get('skill_id')}`",
                    f"- Skill status: `{target_train.get('skill_status')}`",
                    f"- Skill rejected: `{target.get('skill_rejected')}`",
                    f"- Construction baseline accuracy: `{percent(target_verification.get('baseline_acc'))}`",
                    f"- Construction skill accuracy: `{percent(target_verification.get('skill_acc'))}`",
                    f"- Construction net gain: `{target_verification.get('net_gain')}`",
                    f"- Verification passed: `{target_verification.get('passed')}`",
                    f"- Held-out model: `{target_eval.get('model')}`",
                    f"- Held-out paired N: `{target_eval.get('n_instances')}`",
                    f"- Held-out baseline accuracy: `{percent(target_eval.get('baseline_acc'))}`",
                    f"- Held-out skill accuracy: `{percent(target_eval.get('skill_acc'))}`",
                    f"- Held-out delta: `{percent(target_eval.get('delta_acc'))}`",
                    f"- Held-out net gain: `{target_eval.get('net_gain')}`",
                    f"- Train token usage: `{target_train.get('token_usage_total')}`",
                    f"- Eval token usage: `{target_eval.get('token_usage_total')}`",
                    "",
                ]
            )
    return "\n".join(lines)


def compare_results(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    contract = read_json(paths.artifacts_dir / "verification_contract.json")
    benchmark = read_json(paths.artifacts_dir / "benchmark_results.json")
    if benchmark.get("status") != "official_code_smoke_completed":
        comparison = {
            "schema_version": "0.3",
            "target_id": TARGET_ID,
            "status": benchmark.get("status", STATUS_NOT_TESTABLE),
            "reason": benchmark.get("reason", "benchmark result unavailable"),
            "full_paper_claim_status": "blocked",
        }
    else:
        eval_result = benchmark["eval"]
        baseline_acc = eval_result.get("baseline_acc")
        skill_acc = eval_result.get("skill_acc")
        net_gain = eval_result.get("net_gain")
        positive = (
            isinstance(baseline_acc, (int, float))
            and isinstance(skill_acc, (int, float))
            and isinstance(net_gain, int)
            and skill_acc > baseline_acc
            and net_gain > 0
        )
        smoke_status = STATUS_REPRODUCED if positive else STATUS_NOT_REPRODUCED
        comparison = {
            "schema_version": "0.3",
            "target_id": TARGET_ID,
            "benchmark_claim_id": contract["benchmark_claim_id"],
            "paper_claim_id": contract["paper_claim_id"],
            "smoke_status": smoke_status,
            "full_paper_claim_status": "blocked",
            "full_paper_claim_reason": "The AIME smoke target is not the full SkillGen Table 1 benchmark setup.",
            "observed": {
                "baseline_acc": baseline_acc,
                "skill_acc": skill_acc,
                "delta_acc": eval_result.get("delta_acc"),
                "repair": eval_result.get("repair"),
                "regression": eval_result.get("regression"),
                "net_gain": net_gain,
            },
            "comparison_rule": contract["comparison_rule"],
        }
    write_json(paths.artifacts_dir / "claim_comparison.json", comparison)
    write_text(paths.artifacts_dir / "claim_comparison.md", render_comparison_md(comparison))
    append_event(run_dir, "claim_comparison", comparison.get("smoke_status", comparison.get("status", STATUS_NOT_TESTABLE)))
    return comparison


def render_comparison_md(comparison: dict[str, Any]) -> str:
    smoke_status = comparison.get("smoke_status", comparison.get("status"))
    observed = comparison.get("observed", {})
    return f"""# Claim Comparison

## Smoke Target Status

`{smoke_status}`

## Full Paper Claim Status

`{comparison.get("full_paper_claim_status")}`

{comparison.get("full_paper_claim_reason", comparison.get("reason", ""))}

## Observed Smoke Metrics

- Baseline accuracy: `{percent(observed.get("baseline_acc"))}`
- Skill accuracy: `{percent(observed.get("skill_acc"))}`
- Accuracy delta: `{percent(observed.get("delta_acc"))}`
- Repairs: `{observed.get("repair")}`
- Regressions: `{observed.get("regression")}`
- Net gain: `{observed.get("net_gain")}`
    """


def table_cell(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().replace("|", "/")


def claim_summary_comparison(row: dict[str, Any]) -> str:
    claim_id = row.get("claim_id")
    comparisons = {
        "claim_method_paired_intervention": (
            "Official AIME smoke output fields for paired no-skill vs with-skill evaluation: "
            "baseline_acc, skill_acc, repair, regression, and net_gain."
        ),
        "claim_table1_average_gains_all_models": (
            "Paper Table 1 average gains across 80 benchmark-split-model entries vs the current "
            "AIME smoke scope and official support inventory."
        ),
        "claim_table1_entry_counts": (
            "Paper Table 1 count claim, 50 improved / 25 unchanged / 5 regressed, vs current "
            "run scope and missing-row inventory."
        ),
        "claim_table1_alfworld_scienceworld_patterns": (
            "Paper ALFWorld and ScienceWorld per-model improvement pattern vs official bundled "
            "data and executable target availability."
        ),
        "claim_baseline_generator_comparison": (
            "Paper SkillGen-vs-baseline-generator comparison vs baseline runner implementations "
            "available in the official checkout."
        ),
        "claim_ablation_full_wins": (
            "Paper Figure 3 ablation claim vs ablation scripts and named ablated configs in the "
            "official checkout."
        ),
        "claim_cross_model_transfer": (
            "Paper 120 off-diagonal transfer comparisons vs available transfer-run matrix support "
            "and model route mapping."
        ),
        "claim_tau_bench_gate_activated": (
            "Paper tau-Bench retail claim vs official tau-Bench smoke execution, internal "
            "verification gate, and held-out no-skill/skill comparison."
        ),
        "claim_chemllmbench_useful_gains": (
            "Paper ChemLLMBench property/yield claim vs prepared ChemLLMBench smoke executions "
            "and held-out no-skill/skill comparison."
        ),
        "claim_refinement_best_of_k": (
            "Paper Figure 7 Best-of-K aggregate vs available per-round verification traces from "
            "executed runs."
        ),
        "claim_token_cost": (
            "Paper Table 4 token-cost summary vs available token logs from AIME/tau/Chem/ScienceWorld/PubMedQA/Mind2Web/MCPBench smoke runs and the Table 4 token plan."
        ),
        "claim_auditable_skill_artifact": (
            "Generated SkillGen skill output directory and skill JSON artifact vs paper's "
            "auditable-skill property."
        ),
    }
    return comparisons.get(claim_id, "Implemented claim rule vs available official-code evidence.")


def claim_summary_reason(row: dict[str, Any], benchmark: dict[str, Any]) -> str:
    claim_id = row.get("claim_id")
    eval_result = benchmark.get("eval") or {}
    train_result = benchmark.get("train") or {}
    additional = benchmark.get("additional_targets") or {}
    tau_result = additional.get("tau_bench_retail") or {}
    tau_eval = tau_result.get("eval") or {}
    tau_train = tau_result.get("train") or {}
    tau_verification = tau_train.get("construction_verification") or {}
    chem_targets = [
        target
        for target in [
            additional.get("chemllmbench_property_prediction"),
            additional.get("chemllmbench_yield_prediction"),
        ]
        if target
    ]
    if chem_targets:
        chem_reason = "; ".join(
            f"{target.get('target_id')}: status={target.get('claim_status')}, "
            f"delta={percent((target.get('eval') or {}).get('delta_acc'))}, "
            f"gate_passed={((target.get('train') or {}).get('construction_verification') or {}).get('passed')}"
            for target in chem_targets
        )
    else:
        chem_reason = "no executed ChemLLMBench target yet"
    reasons = {
        "claim_method_paired_intervention": (
            "Partially reproduced: the smoke run exercised the paired comparison mechanism, "
            "but it is only one low-cost target rather than the full paper setup."
        ),
        "claim_table1_average_gains_all_models": (
            "Blocked: Table 1 requires the full 80-entry matrix; the current run only evaluated "
            f"the AIME smoke target, whose held-out delta was {percent(eval_result.get('delta_acc'))}; "
            "some external rows are now prepared, but structural row contracts still remain."
        ),
        "claim_table1_entry_counts": (
            "Blocked: the 50/25/5 entry counts cannot be computed until all Table 1 rows and "
            "structural row contracts are executable and then run."
        ),
        "claim_table1_alfworld_scienceworld_patterns": (
            "Blocked: ScienceWorld is present, but ALFWorld still lacks a SkillGen-compatible "
            "adapter and IOD/OOD split contract, even though canonical ALFWorld source code has been fetched."
        ),
        "claim_baseline_generator_comparison": (
            "Not testable: the official checkout does not include executable Trace2Skill, "
            "SkillX, EvoSkill, or CoEvoSkills comparison runners."
        ),
        "claim_ablation_full_wins": (
            "Not testable: the official checkout does not include an ablation runner or "
            "named ablated configurations for Figure 3."
        ),
        "claim_cross_model_transfer": (
            "Blocked: the transfer matrix plan is available, but the ALFWorld OOD structural contract is still missing."
        ),
        "claim_tau_bench_gate_activated": (
            "Not reproduced in this limited run: tau-Bench generated a skill, but "
            f"gate_passed={tau_verification.get('passed')}, "
            f"train_net_gain={tau_verification.get('net_gain')}, "
            f"heldout_delta={percent(tau_eval.get('delta_acc'))}; "
            "the official evaluator treats rejected/deprecated skills as skill==baseline."
            if tau_result
            else "Ready for execution: tau-Bench source/data preparation is done and no structural blocker remains."
        ),
        "claim_chemllmbench_useful_gains": (
            f"ChemLLMBench execution summary: {chem_reason}."
            if chem_targets
            else "Ready for execution: ChemLLMBench source/data preparation is done and no structural blocker remains."
        ),
        "claim_refinement_best_of_k": (
            "Blocked: the smoke run has construction verification traces, but not the full "
            "aggregate per-round traces needed for the paper's Figure 7 result."
        ),
        "claim_token_cost": (
            "Partially reproduced: token logs exist "
            f"(train={train_result.get('token_usage_total')}, eval={eval_result.get('token_usage_total')}), "
            "and all ready Table 4 token groups were executed at reduced POC scale; this verifies token logging but not the paper's full-scale token totals."
        ),
        "claim_auditable_skill_artifact": (
            "Partially reproduced: the smoke run produced a skill artifact directory, but this "
            "only verifies the property for the smoke run."
        ),
    }
    if claim_id in reasons:
        return reasons[claim_id]
    blockers = row.get("blockers") or []
    if blockers:
        return " ".join(blockers)
    evidence = row.get("evidence") or []
    if evidence:
        return " ".join(evidence)
    return "No concise reason is available for this claim status."


def render_status_explanations_md(
    overall: str,
    full_claim: str,
    benchmark: dict[str, Any],
    comparison: dict[str, Any],
    all_claim_matrix: dict[str, Any],
) -> str:
    lines = ["## Status Explanations", ""]
    observed = comparison.get("observed", {})
    if overall != STATUS_REPRODUCED:
        if overall == STATUS_NOT_REPRODUCED:
            lines.append(
                "- Overall status is `not_reproduced` because the held-out smoke result did not satisfy "
                "`skill_acc > baseline_acc and net_gain > 0`: "
                f"baseline={percent(observed.get('baseline_acc'))}, "
                f"skill={percent(observed.get('skill_acc'))}, "
                f"net_gain={observed.get('net_gain')}."
            )
        elif benchmark.get("status"):
            lines.append(f"- Overall status is `{overall}` because benchmark status is `{benchmark.get('status')}`.")
        else:
            lines.append(f"- Overall status is `{overall}` because no successful benchmark comparison is available yet.")

    if full_claim != STATUS_REPRODUCED:
        reason = comparison.get("full_paper_claim_reason")
        if reason:
            lines.append(f"- Full paper claim status is `{full_claim}`: {reason}")
        else:
            lines.append(f"- Full paper claim status is `{full_claim}` because the executed target does not yet match the full paper contract.")

    claims = all_claim_matrix.get("claims", [])
    if claims:
        lines.extend(["", "### Claim-Level Status Summary", ""])
        lines.extend(
            [
                "| Claim | Status | Compared / required evidence | Reason for status | Next step |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in claims:
            lines.append(
                f"| `{row.get('claim_id')}` | {status_badge(row.get('status'))} | "
                f"{table_cell(claim_summary_comparison(row))} | "
                f"{table_cell(claim_summary_reason(row, benchmark))} | "
                f"{table_cell(row.get('next_step', 'No next step defined.'))} |"
            )

    non_success = [row for row in claims if row.get("status") != STATUS_REPRODUCED]
    if non_success:
        lines.extend(["", "### Claim-Level Non-Success Details", ""])
        for row in non_success:
            lines.extend(
                [
                    f"#### {row.get('claim_id')}",
                    "",
                    f"- Status: {status_badge(row.get('status'))}",
                    f"- Verification mode: `{row.get('verification_mode', 'unknown')}`",
                    f"- Next step: {row.get('next_step', 'No next step defined.')}",
                ]
            )
            blockers = row.get("blockers") or []
            if blockers:
                lines.append("- Reason:")
                lines.extend(f"  - {blocker}" for blocker in blockers)
            elif row.get("evidence"):
                lines.append("- Reason:")
                lines.append("  - Only partial/smoke evidence is available.")
                lines.append("- Evidence:")
                lines.extend(f"  - {item}" for item in row.get("evidence"))
            else:
                lines.append("- Reason:")
                lines.append("  - No successful verification evidence is available for this claim.")
            external_candidates = row.get("external_source_candidates") or []
            if external_candidates:
                lines.append("- External intake candidates:")
                lines.extend(f"  - {format_source_candidate(candidate)}" for candidate in external_candidates)
            lines.append("")
    return "\n".join(lines) + "\n"


def render_report(run_dir: Path) -> None:
    paths = paths_for(run_dir)
    manifest = read_json(paths.input_dir / "input_manifest.json") if (paths.input_dir / "input_manifest.json").exists() else {}
    contract = read_json(paths.artifacts_dir / "verification_contract.json") if (paths.artifacts_dir / "verification_contract.json").exists() else {}
    code_manifest = read_json(paths.artifacts_dir / "code_manifest.json") if (paths.artifacts_dir / "code_manifest.json").exists() else {}
    benchmark = read_json(paths.artifacts_dir / "benchmark_results.json") if (paths.artifacts_dir / "benchmark_results.json").exists() else {}
    comparison = read_json(paths.artifacts_dir / "claim_comparison.json") if (paths.artifacts_dir / "claim_comparison.json").exists() else {}
    automation_state = read_json(paths.artifacts_dir / "automation_state.json") if (paths.artifacts_dir / "automation_state.json").exists() else {}
    all_claim_matrix = read_json(paths.artifacts_dir / "all_claim_verification_matrix.json") if (paths.artifacts_dir / "all_claim_verification_matrix.json").exists() else {}

    overall = comparison.get("smoke_status") or comparison.get("status") or automation_state.get("status") or STATUS_BLOCKED
    full_claim = comparison.get("full_paper_claim_status", "blocked")
    all_claim_counts = all_claim_matrix.get("status_counts", {})
    all_claim_summary = ", ".join(f"{status}={count}" for status, count in sorted(all_claim_counts.items())) or "unavailable"
    status_explanations = render_status_explanations_md(overall, full_claim, benchmark, comparison, all_claim_matrix)
    report = f"""# SkillGen Phase 0 Automated Validation Report

Run ID: `{manifest.get("run_id", paths.run_dir.name)}`

## Overall Status

`{overall}`

## Full Paper Claim Status

`{full_claim}`

The current automation targets the SkillGen AIME smoke validation. It does not claim to reproduce the full Table 1 result unless a matching Table 1 contract is executed.

## Input

- Paper source: `{manifest.get("paper_source_path", "unknown")}`
- Paper copy: `{manifest.get("paper_copied_to", "input/paper.pdf")}`

## Verification Contract

- Target: `{contract.get("target_id", "missing")}`
- Scope: `{contract.get("scope", "unknown")}`
- Dataset: `{(contract.get("dataset") or {}).get("benchmark", "unknown")}`
- Train subset: `{(contract.get("dataset") or {}).get("train_subset", "unknown")}`
- Test subset: `{(contract.get("dataset") or {}).get("test_subset", "unknown")}`

## Official Code

- Repository: `{code_manifest.get("official_repo_url", OFFICIAL_REPO_URL)}`
- Local path: `{code_manifest.get("local_path", "code/official")}`
- Commit: `{code_manifest.get("commit", "unknown")}`
- Intake status: `{code_manifest.get("status", "unknown")}`

## Benchmark Result

- Benchmark status: `{benchmark.get("status", "missing")}`
- Baseline accuracy: `{percent((benchmark.get("eval") or {}).get("baseline_acc"))}`
- Skill accuracy: `{percent((benchmark.get("eval") or {}).get("skill_acc"))}`
- Accuracy delta: `{percent((benchmark.get("eval") or {}).get("delta_acc"))}`
- Repairs: `{(benchmark.get("eval") or {}).get("repair")}`
- Regressions: `{(benchmark.get("eval") or {}).get("regression")}`
- Net gain: `{(benchmark.get("eval") or {}).get("net_gain")}`

## All-Claim Verification

- Claim status counts: `{all_claim_summary}`
- Matrix: `artifacts/all_claim_verification_matrix.json`
- Catalog: `artifacts/all_claims.json`

{status_explanations}
## Evidence Files

- `artifacts/verification_contract.json`
- `artifacts/command_plan.json`
- `artifacts/all_claims.json`
- `artifacts/all_claim_verification_matrix.json`
- `artifacts/external_source_intake_status.json`
- `artifacts/canonical_benchmark_source_status.json`
- `artifacts/model_route_mapping.template.json`
- `artifacts/benchmark_execution_plan.json`
- `artifacts/transfer_runner_plan.json`
- `artifacts/token_log_plan.json`
- `outputs/install_stdout.txt`
- `outputs/install_stderr.txt`
- `outputs/benchmark_stdout.txt`
- `outputs/benchmark_stderr.txt`
- `artifacts/benchmark_results.json`
- `artifacts/claim_comparison.json`

## Limitations

- This is a paper-specific automation POC.
- The selected target is a low-cost AIME smoke validation, not the paper's full Table 1 benchmark matrix.
- Live install and benchmark execution require `artifacts/approval.json` plus API keys.
- Additional target executions may include recorded deviations, especially the direct OpenAI fallback used when OpenRouter credits were unavailable.
"""
    write_text(paths.artifacts_dir / "research_validation_report.md", report)
    append_event(run_dir, "report_generation", "completed", artifact="artifacts/research_validation_report.md")


def parse_compare_report(run_dir: Path) -> None:
    paths = paths_for(run_dir)
    if not (paths.artifacts_dir / "verification_contract.json").exists():
        build_verification_contract(run_dir)
    write_external_source_intake_artifacts(run_dir)
    write_execution_planning_artifacts(run_dir)
    parse_results(run_dir)
    compare_results(run_dir)
    build_all_claim_verification_artifacts(run_dir)
    render_report(run_dir)


def execute_approved_pipeline(run_dir: Path, skip_install: bool = False) -> str:
    approval = approval_policy(run_dir)
    should_skip_existing_install = (
        bool(approval.get("skip_install_if_environment_present"))
        and install_already_succeeded(run_dir)
    )
    if skip_install or should_skip_existing_install:
        append_event(
            run_dir,
            "install_execution",
            "skipped_existing_project_local_environment",
            reason="skip_install flag" if skip_install else "approval permits reuse of existing project-local install",
        )
    else:
        install_status = execute_install(run_dir)
        if install_status != "install_succeeded":
            render_report(run_dir)
            return install_status
    benchmark_status = execute_benchmark(run_dir)
    if benchmark_status == "benchmark_succeeded":
        parse_compare_report(run_dir)
    else:
        render_report(run_dir)
    return benchmark_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automate the SkillGen Phase 0 AIME smoke POC.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Create a SkillGen run and automation artifacts.")
    prepare.add_argument("--paper", type=Path, default=Path("meeting docs/SkillGen.pdf"))
    prepare.add_argument("--output-root", type=Path, default=Path("phase_0/runs"))
    prepare.add_argument("--run-id", default=None)
    prepare.add_argument("--official-source", type=Path, default=None)
    prepare.add_argument("--allow-clone", action="store_true")

    enrich = subparsers.add_parser("enrich", help="Add automation artifacts to an existing run.")
    enrich.add_argument("--run-dir", type=Path, required=True)
    enrich.add_argument("--official-source", type=Path, default=None)
    enrich.add_argument("--allow-clone", action="store_true")

    approve = subparsers.add_parser("approve", help="Write artifacts/approval.json after human command review.")
    approve.add_argument("--run-dir", type=Path, required=True)
    approve.add_argument("--approved-by", default="human")
    approve.add_argument("--max-cost-usd", type=float, default=5.0)
    approve.add_argument("--notes", default="Approved after reviewing command_plan.json.")
    approve.add_argument("--approval-source", default="manual_artifact")
    approve.add_argument("--no-install", action="store_true")
    approve.add_argument("--no-benchmark", action="store_true")
    approve.add_argument("--no-network", action="store_true")
    approve.add_argument("--no-paid-api", action="store_true")
    approve.add_argument("--no-project-local-install", action="store_true")
    approve.add_argument("--no-skip-install-if-present", action="store_true")
    approve.add_argument("--no-auto-retry", action="store_true")
    approve.add_argument("--max-retry-attempts", type=int, default=1)

    execute = subparsers.add_parser("execute", help="Execute approved install and benchmark commands.")
    execute.add_argument("--run-dir", type=Path, required=True)
    execute.add_argument("--skip-install", action="store_true")
    execute.add_argument(
        "--record-codex-approval",
        action="store_true",
        help="Write approval.json first. Use only when launched through Codex's native command approval prompt.",
    )
    execute.add_argument("--approved-by", default="codex_tool_approval")
    execute.add_argument("--max-cost-usd", type=float, default=5.0)
    execute.add_argument("--approval-notes", default="Approved through Codex native command approval prompt.")
    execute.add_argument("--max-retry-attempts", type=int, default=1)

    parse = subparsers.add_parser("parse", help="Parse existing raw outputs, compare, and render report.")
    parse.add_argument("--run-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare":
        run_dir = create_automated_run(args.paper, args.output_root, args.run_id, args.official_source, args.allow_clone)
        print(run_dir)
        return 0
    if args.command == "enrich":
        prepare_automation_artifacts(args.run_dir, args.official_source, args.allow_clone)
        print(args.run_dir)
        return 0
    if args.command == "approve":
        write_approval_artifact(
            args.run_dir,
            approved_by=args.approved_by,
            max_cost_usd=args.max_cost_usd,
            notes=args.notes,
            approval_source=args.approval_source,
            allow_install=not args.no_install,
            allow_benchmark=not args.no_benchmark,
            allow_network=not args.no_network,
            allow_paid_api=not args.no_paid_api,
            allow_project_local_install=not args.no_project_local_install,
            skip_install_if_environment_present=not args.no_skip_install_if_present,
            auto_retry_approved=not args.no_auto_retry,
            max_retry_attempts=args.max_retry_attempts,
        )
        print(args.run_dir / "artifacts" / "approval.json")
        return 0
    if args.command == "execute":
        if args.record_codex_approval:
            write_approval_artifact(
                args.run_dir,
                approved_by=args.approved_by,
                max_cost_usd=args.max_cost_usd,
                notes=args.approval_notes,
                approval_source="codex_native_command_approval",
                max_retry_attempts=args.max_retry_attempts,
            )
        status = execute_approved_pipeline(args.run_dir, skip_install=args.skip_install)
        print(status)
        return 0 if status not in {STATUS_FAILED_TO_RUN, STATUS_NOT_TESTABLE} else 1
    if args.command == "parse":
        parse_compare_report(args.run_dir)
        print(args.run_dir)
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
