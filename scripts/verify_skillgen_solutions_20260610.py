#!/usr/bin/env python3
"""Verify SkillGen Phase 0 solution-validation readiness.

This script does not claim paper reproduction. It audits the solution paths
that were created after the project shifted toward local/reconstructed
solution validation, then prepares tiny local-Ollama smoke inputs for the
benchmark paths that can be exercised with an LLM.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase_0/runs/20260602"
OFFICIAL = RUN_DIR / "code/official"
ARTIFACTS = RUN_DIR / "artifacts"
RESULT_DIR = ARTIFACTS / "08_results/solution_validation/all_solutions_verification_20260610"
SMOKE_DATA_DIR = RESULT_DIR / "smoke_data"
CONFIG_DIR = ARTIFACTS / "07_configs_and_inputs/generated_configs/local_ollama/all_solutions_20260610"


@dataclass
class Check:
    solution_id: str
    verification_type: str
    status: str
    summary: str
    evidence: list[str]
    missing: list[str]
    next_action: str | None = None


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def exists_check(solution_id: str, verification_type: str, required: list[Path], summary: str) -> Check:
    evidence = [rel(path) for path in required if path.exists()]
    missing = [rel(path) for path in required if not path.exists()]
    status = "verified" if not missing else "blocked_missing_artifacts"
    return Check(
        solution_id=solution_id,
        verification_type=verification_type,
        status=status,
        summary=summary if status == "verified" else summary + " Some required artifacts are missing.",
        evidence=evidence,
        missing=missing,
        next_action=None if status == "verified" else "Create or restore missing artifacts, then rerun this verifier.",
    )


def dataset_check(solution_id: str, train_path: Path, test_path: Path, min_train: int, min_test: int) -> Check:
    required = [train_path, test_path]
    missing = [rel(path) for path in required if not path.exists()]
    evidence: list[str] = []
    problems: list[str] = []
    if not missing:
        for path, min_n in [(train_path, min_train), (test_path, min_test)]:
            data = read_json(path)
            instances = data.get("instances") or []
            evidence.append(f"{rel(path)} ({len(instances)} instances)")
            if len(instances) < min_n:
                problems.append(f"{rel(path)} has {len(instances)} instances, expected at least {min_n}")
            for key in ["dataset_id", "task_name", "task_type", "instances"]:
                if key not in data:
                    problems.append(f"{rel(path)} missing key {key}")
            for idx, inst in enumerate(instances[:3]):
                for key in ["instance_id", "input"]:
                    if key not in inst:
                        problems.append(f"{rel(path)} instance {idx} missing key {key}")
    status = "verified" if not missing and not problems else "blocked_or_invalid_dataset"
    return Check(
        solution_id=solution_id,
        verification_type="dataset_contract",
        status=status,
        summary=(
            "Dataset files exist, are JSON-loadable, and have enough SkillGen-format instances."
            if status == "verified"
            else "Dataset contract check failed."
        ),
        evidence=evidence,
        missing=missing + problems,
        next_action=None if status == "verified" else "Fix dataset files or regenerate split/adapter outputs.",
    )


def make_subset(source: Path, target: Path, n: int, dataset_id_suffix: str) -> None:
    data = read_json(source)
    subset = dict(data)
    subset["dataset_id"] = f"{data.get('dataset_id', source.stem)}_{dataset_id_suffix}"
    subset["instances"] = list(data.get("instances", []))[:n]
    metadata = dict(subset.get("metadata") or {})
    metadata["solution_validation_smoke"] = True
    metadata["source_dataset"] = rel(source)
    metadata["source_instance_count"] = len(data.get("instances", []))
    subset["metadata"] = metadata
    write_json(target, subset)


def write_local_smoke_config(
    *,
    target_id: str,
    model: str,
    candidate_dir: str,
    artifact_root: str,
    skill_output: str,
    config_path: Path,
    max_tokens: int = 192,
    max_tokens_generation: int = 512,
) -> None:
    text = f"""# Local Ollama solution-verification smoke config.
models:
  default: "{model}"
  baseline_agent: "{model}"
  baseline_judge: "{model}"
  induction: "{model}"
  induction_contextual: "{model}"
  induction_summary: "{model}"
  induction_pattern: "{model}"
  induction_contrastive: "{model}"
  generation_plan: "{model}"
  generation_execute: "{model}"
  refinement: "{model}"
  verification_agent: "{model}"
  verification_judge: "{model}"
  verification_case_analyst: "{model}"
  verification_revision_synthesiser: "{model}"

llm:
  temperature: 0.0
  max_tokens: {max_tokens}
  max_tokens_generation: {max_tokens_generation}

embedding:
  model: "local-hash-embedding"

clustering:
  method: "kmeans"
  n_clusters: null
  max_failure_clusters: 1
  max_success_clusters: 1
  min_clusters: 1
  target_cluster_size: 1
  min_cluster_size: 1

induction:
  max_contrastive_pairs: 1

generation:
  use_web_search: false
  max_search_queries: 0
  candidate_output_dir: "{candidate_dir}"
  generate_scripts: false
  max_failure_clusters_in_prompt: 1
  max_success_clusters_in_prompt: 1
  max_contrastive_pairs_in_prompt: 1

verification_analysis:
  case_analyst_workers: 1
  case_analyst_max_tokens: 256
  revision_synthesiser_max_tokens: 512

verification:
  sample_size: 2
  min_sample: 1
  seed: 42
  min_net_gain_abs: 1
  min_net_gain_rel: 0.0

router:
  enabled: false
  model: "{model}"
  max_workers: 1

pipeline:
  max_refine_rounds: 1
  baseline_runs_per_instance: 1
  max_workers: 1
  artifact_root: "{artifact_root}"

skill_output:
  path: "{skill_output}"
"""
    write_text(config_path, text)


def prepare_local_llm_smokes() -> list[Check]:
    checks: list[Check] = []
    model = "gemma3:1b"

    smoke_specs = [
        {
            "target_id": "alfworld_iod",
            "train_source": OFFICIAL / "data/alfworld_iod/train.json",
            "test_source": OFFICIAL / "data/alfworld_iod/test.json",
            "train_n": 4,
            "test_n": 2,
            "max_tokens": 192,
            "max_tokens_generation": 512,
        },
        {
            "target_id": "alfworld_ood",
            "train_source": OFFICIAL / "data/alfworld_ood/train.json",
            "test_source": OFFICIAL / "data/alfworld_ood/test.json",
            "train_n": 4,
            "test_n": 2,
            "max_tokens": 192,
            "max_tokens_generation": 512,
        },
        {
            "target_id": "livecodebench",
            "train_source": OFFICIAL / "data/livecodebench/train_release_v6_n50_seed42.json",
            "test_source": OFFICIAL / "data/livecodebench/test_release_v6_n150_seed42.json",
            "train_n": 3,
            "test_n": 1,
            "max_tokens": 192,
            "max_tokens_generation": 512,
        },
    ]

    for spec in smoke_specs:
        target_id = str(spec["target_id"])
        out_dir = RESULT_DIR / target_id
        train_subset = SMOKE_DATA_DIR / f"{target_id}_train_n{spec['train_n']}.json"
        test_subset = SMOKE_DATA_DIR / f"{target_id}_test_n{spec['test_n']}.json"
        config_path = CONFIG_DIR / f"{target_id}_gemma3_1b.yaml"

        if Path(spec["train_source"]).exists() and Path(spec["test_source"]).exists():
            make_subset(Path(spec["train_source"]), train_subset, int(spec["train_n"]), "local_smoke_train_20260610")
            make_subset(Path(spec["test_source"]), test_subset, int(spec["test_n"]), "local_smoke_test_20260610")
            write_local_smoke_config(
                target_id=target_id,
                model=model,
                candidate_dir=f"../../artifacts/08_results/solution_validation/all_solutions_verification_20260610/{target_id}/candidates",
                artifact_root=f"../../artifacts/08_results/solution_validation/all_solutions_verification_20260610/{target_id}/artifacts/runs",
                skill_output=f"../../artifacts/08_results/solution_validation/all_solutions_verification_20260610/{target_id}/skill_output",
                config_path=config_path,
                max_tokens=int(spec["max_tokens"]),
                max_tokens_generation=int(spec["max_tokens_generation"]),
            )
            evidence = [rel(train_subset), rel(test_subset), rel(config_path)]
            status = "prepared_for_local_llm_smoke"
            summary = f"Prepared local Ollama smoke assets for {target_id} with model {model}."
            missing: list[str] = []
        else:
            evidence = []
            missing = [rel(Path(spec["train_source"])), rel(Path(spec["test_source"]))]
            status = "blocked_missing_source_dataset"
            summary = f"Could not prepare local Ollama smoke assets for {target_id}; source dataset missing."
        checks.append(
            Check(
                solution_id=f"{target_id}_local_llm_smoke",
                verification_type="local_llm_smoke_preparation",
                status=status,
                summary=summary,
                evidence=evidence,
                missing=missing,
                next_action=(
                    f"Run main.py with {rel(train_subset)} and {rel(config_path)}, then eval_skill.py on {rel(test_subset)}."
                    if not missing
                    else "Restore source dataset files."
                ),
            )
        )

    return checks


def structural_checks() -> list[Check]:
    checks: list[Check] = []
    checks.append(
        dataset_check(
            "alfworld_reconstructed_adapter",
            OFFICIAL / "data/alfworld_iod/train.json",
            OFFICIAL / "data/alfworld_iod/test.json",
            1,
            1,
        )
    )
    checks.append(
        dataset_check(
            "alfworld_ood_reconstructed_adapter",
            OFFICIAL / "data/alfworld_ood/train.json",
            OFFICIAL / "data/alfworld_ood/test.json",
            1,
            1,
        )
    )
    checks.append(
        exists_check(
            "alfworld_reconstructed_adapter",
            "adapter_contract_and_code",
            [
                OFFICIAL / "benchmarks/alfworld_adapter.py",
                OFFICIAL / "benchmarks/alfworld_grader.py",
                OFFICIAL / "scripts/prepare_alfworld.py",
                ARTIFACTS / "06_plans_and_contracts/alfworld_split_manifest_seed42.md",
                ARTIFACTS / "06_plans_and_contracts/alfworld_run_commands.md",
                ARTIFACTS / "09_safety_and_deviations/alfworld_adapter_deviation_note.md",
            ],
            "ALFWorld reconstructed adapter has code, split manifest, run commands, and deviation note.",
        )
    )
    checks.append(
        dataset_check(
            "livecodebench_reconstructed_split",
            OFFICIAL / "data/livecodebench/train_release_v6_n50_seed42.json",
            OFFICIAL / "data/livecodebench/test_release_v6_n150_seed42.json",
            1,
            1,
        )
    )
    checks.append(
        exists_check(
            "livecodebench_reconstructed_split",
            "split_contract_and_adapter",
            [
                OFFICIAL / "benchmarks/livecodebench_adapter.py",
                OFFICIAL / "data/livecodebench/split_release_v6_n50_n150_seed42_manifest.json",
                ARTIFACTS / "03_code_and_sources/livecodebench_source_review.md",
                ARTIFACTS / "06_plans_and_contracts/livecodebench_split_contract.md",
                ARTIFACTS / "09_safety_and_deviations/livecodebench_deviation_note.md",
            ],
            "LiveCodeBench reconstructed split has adapter, manifest, source review, contract, and deviation note.",
        )
    )
    baseline_paths = [
        OFFICIAL / "baselines/Trace2Skill/README.md",
        OFFICIAL / "baselines/SkillX/README.md",
        OFFICIAL / "baselines/EvoSkill/README.md",
        OFFICIAL / "baselines/CoEvoSkills/README.md",
        ARTIFACTS / "06_plans_and_contracts/baseline_source_identity_review.json",
        ARTIFACTS / "06_plans_and_contracts/baseline_single_skill_adapter_contract.json",
        ARTIFACTS / "09_safety_and_deviations/baseline_deviation_note.md",
        ARTIFACTS / "baseline_source_identity_human_review.json",
    ]
    checks.append(
        exists_check(
            "baseline_generator_comparison",
            "source_identity_and_adapter_contract",
            baseline_paths,
            "Baseline comparison has public repos, identity review, adapter contract, deviation note, and human approval artifact.",
        )
    )
    checks.append(
        exists_check(
            "reconstructed_ablation",
            "ablation_contract",
            [
                ARTIFACTS / "06_plans_and_contracts/reconstructed_ablation_contract.json",
                ARTIFACTS / "06_plans_and_contracts/ablation_config_matrix.json",
                ARTIFACTS / "06_plans_and_contracts/ablation_smoke_plan.json",
                ARTIFACTS / "09_safety_and_deviations/ablation_deviation_note.md",
            ],
            "Reconstructed ablation has contract, config matrix, smoke plan, and deviation note.",
        )
    )
    checks.append(
        exists_check(
            "cross_model_transfer",
            "transfer_contract",
            [
                ARTIFACTS / "06_plans_and_contracts/transfer_runner_plan.json",
                ARTIFACTS / "06_plans_and_contracts/transfer_execution_contract.json",
            ],
            "Transfer has runner plan and execution contract.",
        )
    )
    checks.append(
        exists_check(
            "full_matrix_runner",
            "full_matrix_contract_and_state",
            [
                ARTIFACTS / "06_plans_and_contracts/full_matrix_execution_contract.json",
                ARTIFACTS / "08_results/full_matrix/full_matrix_runner_state.json",
                ARTIFACTS / "08_results/full_matrix/observed_entries.json",
            ],
            "Full-matrix solution has execution contract, runner state, and observed-entry accounting.",
        )
    )
    checks.append(
        exists_check(
            "trace_retention",
            "trace_contract_and_existing_evidence",
            [
                ARTIFACTS / "06_plans_and_contracts/per_round_trace_retention_checklist.json",
                ARTIFACTS / "06_plans_and_contracts/figure7_trace_extraction_contract.json",
                ARTIFACTS / "08_results/solution_validation/overnight_verification_20260607/skill_traceability_audit.md",
            ],
            "Trace-retention solution has checklist, Figure 7 contract, and existing traceability audit.",
        )
    )
    checks.append(
        exists_check(
            "provider_and_cost_governance",
            "provider_cost_policy",
            [
                ARTIFACTS / "06_plans_and_contracts/provider_resolution_status.json",
                ARTIFACTS / "06_plans_and_contracts/full_matrix_execution_budget_policy.json",
                ARTIFACTS / "09_safety_and_deviations/full_matrix_cost_governance.md",
            ],
            "Provider/cost solution has provider resolution status, budget policy, and cost governance note.",
        )
    )
    return checks


def render_md(checks: list[Check]) -> str:
    lines = [
        "# All-Solutions Structural Verification",
        "",
        "Date: 2026-06-10",
        "",
        "This is solution validation, not paper reproduction.",
        "",
        "| Solution | Verification type | Status | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for check in checks:
        lines.append(
            f"| `{check.solution_id}` | `{check.verification_type}` | `{check.status}` | {check.summary} |"
        )
    lines.extend(["", "## Evidence Details", ""])
    for check in checks:
        lines.append(f"### {check.solution_id} / {check.verification_type}")
        lines.append("")
        lines.append(f"- Status: `{check.status}`")
        lines.append(f"- Summary: {check.summary}")
        if check.evidence:
            lines.append("- Evidence:")
            for item in check.evidence:
                lines.append(f"  - `{item}`")
        if check.missing:
            lines.append("- Missing/problems:")
            for item in check.missing:
                lines.append(f"  - `{item}`")
        if check.next_action:
            lines.append(f"- Next action: {check.next_action}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    checks = structural_checks()
    checks.extend(prepare_local_llm_smokes())
    payload = {
        "date": "2026-06-10",
        "scope": "SkillGen Phase 0 local/reconstructed solution verification",
        "paper_reproduction": False,
        "checks": [asdict(check) for check in checks],
        "status_counts": {},
    }
    for check in checks:
        payload["status_counts"][check.status] = payload["status_counts"].get(check.status, 0) + 1
    write_json(RESULT_DIR / "structural_verification.json", payload)
    write_text(RESULT_DIR / "structural_verification.md", render_md(checks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
