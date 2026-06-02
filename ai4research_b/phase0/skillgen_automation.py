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

BUNDLED_DATASET_MAP = {
    "aime": "data/aime",
    "mcp_bench_single": "data/mcp_bench",
    "mind2web": "data/mind2web",
    "pubmedqa": "data/pubmedqa",
    "scienceworld": "data/scienceworld",
    "socialmaze_fts": "data/socialmaze",
    "toolbench": "data/toolbench",
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
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


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


def official_support_snapshot(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
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
        blockers.extend(
            [
                "Full Table 1 requires 80 benchmark-split-model entries, not only the AIME smoke target.",
                "Missing bundled official data for rows: " + ", ".join(support["table1_missing_rows"]),
                "Paper model display names still need exact provider route IDs before unattended execution.",
                "Requires API/network/token-spend approval.",
            ]
        )
        present = ", ".join(support["table1_present_rows"]) or "none"
        evidence.append(f"Official release currently has bundled data for these Table 1 rows: {present}.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_table1_alfworld_scienceworld_patterns":
        if not data_support.get("scienceworld", {}).get("available"):
            blockers.append("ScienceWorld bundled data is missing.")
        if "alfworld_iod" in support["table1_missing_rows"] or "alfworld_ood" in support["table1_missing_rows"]:
            blockers.append("ALFWorld IOD/OOD data is not bundled in code/official/data.")
        blockers.append("Requires all eight model routes and API/token-spend approval.")
        if data_support.get("scienceworld", {}).get("available"):
            evidence.append("ScienceWorld train/test JSON is bundled and can be planned for execution.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_baseline_generator_comparison":
        blockers.extend(
            [
                "Official checkout does not include Trace2Skill, SkillX, EvoSkill, or CoEvoSkills runner implementations.",
                "README describes baseline adaptation details in the paper, but no executable baseline-comparison command is present.",
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
        blockers.extend(
            [
                "Official eval_skill.py can evaluate a skill across multiple models, but no transfer-run matrix script is provided.",
                "Requires generated source-model skills plus exact provider route IDs for source and evaluator models.",
                "Requires API/network/token-spend approval.",
            ]
        )
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_tau_bench_gate_activated":
        blockers.extend(
            [
                "tau-Bench train/test data is not bundled in code/official/data.",
                "README says additional preparation is required.",
                "Requires user-simulator setup and API/token-spend approval.",
            ]
        )
        return STATUS_NOT_TESTABLE, blockers, evidence

    if claim_id == "claim_chemllmbench_useful_gains":
        blockers.extend(
            [
                "ChemLLMBench train/test data is not bundled in code/official/data.",
                "README says additional preparation is required.",
                "Requires property/yield split generation and API/token-spend approval.",
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
        blockers.extend(
            [
                "Table 4 requires full token usage logs grouped by benchmark, not the current AIME smoke run.",
                "Requires reproducing or obtaining complete training/evaluation token logs.",
            ]
        )
        return STATUS_BLOCKED, blockers, evidence

    blockers.append("No verification rule has been implemented for this claim.")
    return STATUS_NOT_TESTABLE, blockers, evidence


def next_step_for_claim(status: str, verification_mode: str) -> str:
    if status == STATUS_PARTIALLY_REPRODUCED:
        return "Promote from smoke evidence to full-paper evidence only if the matching full contract is executed."
    if status == STATUS_BLOCKED and verification_mode in {"full_table1_matrix", "full_table1_subset", "transfer_matrix", "refinement_trace_analysis", "token_usage_aggregation"}:
        return "Create or approve the required full-run contract, model-route mapping, and API/token budget."
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
                "status": "command_plan_possible",
                "limitations": [
                    "Needs exact model-route mapping for paper model names.",
                    "Needs approval for network/API/token spend before execution.",
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
        matrix.append(
            {
                "claim_id": claim["id"],
                "claim_type": claim["claim_type"],
                "verification_mode": claim["verification_mode"],
                "status": status,
                "blockers": blockers,
                "evidence": evidence,
                "next_step": next_step_for_claim(status, claim["verification_mode"]),
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
        reasons.append("allow_install is not true")
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


def execute_install(run_dir: Path) -> str:
    allowed, reasons = approval_status(run_dir, "install")
    if not allowed:
        write_blocked_execution(run_dir, "install", reasons)
        return STATUS_BLOCKED
    paths = paths_for(run_dir)
    plan = read_json(paths.artifacts_dir / "command_plan.json")
    commands = plan["commands"]
    runs = [
        run_command(
            run_dir,
            commands["create_venv"],
            paths.outputs_dir / "install_stdout.txt",
            paths.outputs_dir / "install_stderr.txt",
        ),
        run_command(
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

    train = run_command(run_dir, commands["train"], paths.outputs_dir / "benchmark_stdout.txt", paths.outputs_dir / "benchmark_stderr.txt")
    if train["exit_code"] != 0:
        append_event(run_dir, "benchmark_train_execution", STATUS_FAILED_TO_RUN, command=train)
        return STATUS_FAILED_TO_RUN

    skill_output_dir = find_skill_output_dir(run_dir)
    if skill_output_dir is None:
        append_event(run_dir, "benchmark_eval_execution", STATUS_NOT_TESTABLE, reason="missing skill_output directory")
        return STATUS_NOT_TESTABLE

    relative_skill_path = rel(skill_output_dir, paths.official_dir)
    eval_command = dict(commands["eval_template"])
    eval_command["argv"] = [part.format(skill_output_dir=relative_skill_path) for part in eval_command["argv"]]
    eval_result = run_command(run_dir, eval_command, paths.raw_dir / "eval_stdout.txt", paths.raw_dir / "eval_stderr.txt")
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


def parse_skill_id(skill_output_dir: Path | None) -> str | None:
    if skill_output_dir is None or not skill_output_dir.exists():
        return None
    json_files = [path for path in skill_output_dir.glob("*.json") if path.name not in {"skill_analysis.json", "skill_analysis_summary.json"}]
    if not json_files:
        return None
    return json_files[0].stem


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
    return f"""# Benchmark Results

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
"""


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

## Evidence Files

- `artifacts/verification_contract.json`
- `artifacts/command_plan.json`
- `artifacts/all_claims.json`
- `artifacts/all_claim_verification_matrix.json`
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
"""
    write_text(paths.artifacts_dir / "research_validation_report.md", report)
    append_event(run_dir, "report_generation", "completed", artifact="artifacts/research_validation_report.md")


def parse_compare_report(run_dir: Path) -> None:
    paths = paths_for(run_dir)
    if not (paths.artifacts_dir / "verification_contract.json").exists():
        build_verification_contract(run_dir)
    parse_results(run_dir)
    compare_results(run_dir)
    build_all_claim_verification_artifacts(run_dir)
    render_report(run_dir)


def execute_approved_pipeline(run_dir: Path, skip_install: bool = False) -> str:
    if not skip_install:
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
