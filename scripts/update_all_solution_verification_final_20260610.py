#!/usr/bin/env python3
"""Update the final all-solution verification report with stricter evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase_0/runs/20260602"
RESULT_DIR = RUN_DIR / "artifacts/08_results/solution_validation/all_solutions_verification_20260610"
FINAL_JSON = RESULT_DIR / "all_solution_verification_final.json"
FINAL_MD = RESULT_DIR / "all_solution_verification_final.md"
OP_LOG = RESULT_DIR / "operation_log.md"


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def metric(path: Path) -> dict[str, Any]:
    data = read_json(path)
    result = data["results"][0]
    return {
        "n_instances": result["n_instances"],
        "baseline_acc": result["baseline_acc"],
        "skill_acc": result["skill_acc"],
        "delta_acc": result["delta_acc"],
        "repair": result["repair"],
        "regression": result["regression"],
        "net_gain": result["net_gain"],
        "skill_status": data.get("skill_status"),
    }


def status(path: Path) -> int | None:
    if not path.exists():
        return None
    return read_json(path).get("exit_code")


def replace_solution(payload: dict[str, Any], solution_id: str, updated: dict[str, Any]) -> None:
    for idx, solution in enumerate(payload["solutions"]):
        if solution["solution_id"] == solution_id:
            payload["solutions"][idx] = updated
            return
    payload["solutions"].append(updated)


def recalc_counts(payload: dict[str, Any]) -> None:
    counts: dict[str, int] = {}
    for solution in payload["solutions"]:
        counts[solution["status"]] = counts.get(solution["status"], 0) + 1
    payload["status_counts"] = counts


def render(payload: dict[str, Any]) -> str:
    lines = [
        "# All-Solution Verification Final Report",
        "",
        "Date: 2026-06-10",
        "",
        "This report verifies whether each repair solution removes the reproduction blocker it was meant to address after the project shifted from exact paper reproduction to local/reconstructed solution validation. It does not claim that the paper results are reproduced.",
        "",
        "## Strict Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for key, value in payload["status_counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(
        [
            "",
            "## Solution Results",
            "",
            "| Solution | Status | Blocker resolution | What was verified | Main limitation |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for solution in payload["solutions"]:
        lines.append(
            f"| `{solution['solution_id']}` | `{solution['status']}` | {solution.get('blocker_resolution', '')} | {solution['meaning']} | {solution['limitation']} |"
        )

    lines.extend(["", "## Details", ""])
    for solution in payload["solutions"]:
        lines.extend(
            [
                f"### {solution['solution_id']}",
                "",
                f"- Status: `{solution['status']}`",
                f"- Blocker resolution: {solution.get('blocker_resolution', '')}",
                f"- Meaning: {solution['meaning']}",
            ]
        )
        for key in [
            "train_exit_code",
            "eval_exit_code",
            "iod_train_exit_code",
            "iod_eval_exit_code",
            "ood_train_exit_code",
            "ood_eval_exit_code",
            "n3_train_exit_code",
            "ultra_train_exit_code",
            "ultra_eval_exit_code",
            "qwen_attempt_exit_code",
            "fast_attempt_exit_code",
            "full_matrix_dry_run_exit_code",
        ]:
            if key in solution:
                lines.append(f"- {key}: `{solution[key]}`")
        if "metrics" in solution:
            lines.append(f"- Metrics: `{json.dumps(solution['metrics'], ensure_ascii=False)}`")
        if "iod_metrics" in solution:
            lines.append(f"- IOD metrics: `{json.dumps(solution['iod_metrics'], ensure_ascii=False)}`")
        if "ood_metrics" in solution:
            lines.append(f"- OOD metrics: `{json.dumps(solution['ood_metrics'], ensure_ascii=False)}`")
        if "baseline_native_feasibility" in solution:
            lines.append("- Baseline native feasibility:")
            for row in solution["baseline_native_feasibility"]:
                lines.append(
                    f"  - `{row['method']}`: `{row['probe_status']}`, source_identity_solved={row['source_identity_solved']}, native_adapter_verified={row['native_algorithm_adapter_verified']}"
                )
        if "coevoskills_unofficial_fallback" in solution:
            lines.append(f"- CoEvoSkills unofficial fallback: `{json.dumps(solution['coevoskills_unofficial_fallback'], ensure_ascii=False)}`")
        if "ablation_arm_metrics" in solution:
            lines.append("- Ablation arm exit codes:")
            for arm, item in solution["ablation_arm_metrics"].items():
                lines.append(f"  - `{arm}`: exit `{item['exit_code']}`, metrics `{json.dumps(item['metrics'], ensure_ascii=False)}`")
        if "baseline_slot_metrics" in solution:
            lines.append("- Baseline slot exit codes:")
            for method, item in solution["baseline_slot_metrics"].items():
                lines.append(f"  - `{method}`: exit `{item['exit_code']}`, metrics `{json.dumps(item['metrics'], ensure_ascii=False)}`")
        lines.append("- Evidence:")
        for item in solution["evidence"]:
            lines.append(f"  - `{item}`")
        lines.append(f"- Limitation: {solution['limitation']}")
        lines.append("")

    lines.extend(
        [
            "## Bottom Line",
            "",
            "Most solution paths are now verified at structural, smoke, or mechanical-execution scale. ALFWorld is verified on both IOD and OOD reconstructed local-smoke paths. LiveCodeBench is verified only at n=1 ultra-smoke, with n=3 still a runtime risk. The baseline comparison solution is verified for shared evaluator output contract and for open-source source identity/probe surfaces, but not for native algorithm adapters. In particular, the official CoEvoSkills repository remains project-page-only; an unofficial implementation has a runnable CLI surface but is not official and is not adapted to SkillGen trajectories.",
            "",
            "Sources checked for CoEvoSkills code availability:",
            "",
            "- Official repo: https://github.com/Zhang-Henry/CoEvoSkills",
            "- Unofficial fallback candidate: https://github.com/AndyLongest/CoEvoSkills",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    payload = read_json(FINAL_JSON)
    payload["scope"] = "All currently identified SkillGen Phase 0 repair solutions under strict blocker-resolution verification"
    payload["paper_reproduction"] = False
    payload["strict_blocker_resolution_verification"] = True

    alfworld = {
        "solution_id": "alfworld_reconstructed_adapter_pipeline",
        "status": "verified_executable_iod_ood_smoke_no_heldout_gain",
        "blocker_resolution": "solved for executable local/reconstructed ALFWorld IOD and OOD smoke validation; not solved for paper-scale performance reproduction.",
        "meaning": "Reconstructed ALFWorld IOD and OOD data/adapters can be loaded by SkillGen, trained with local Ollama, evaluated, and traced.",
        "iod_train_exit_code": status(RESULT_DIR / "alfworld_iod/train_command_status.json"),
        "iod_eval_exit_code": status(RESULT_DIR / "alfworld_iod/eval_command_status.json"),
        "ood_train_exit_code": status(RESULT_DIR / "alfworld_ood/train_command_status.json"),
        "ood_eval_exit_code": status(RESULT_DIR / "alfworld_ood/eval_command_status.json"),
        "iod_metrics": metric(RESULT_DIR / "alfworld_iod/eval_results.json"),
        "ood_metrics": metric(RESULT_DIR / "alfworld_ood/eval_results.json"),
        "evidence": [
            "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/alfworld_iod/train_stdout.txt",
            "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/alfworld_iod/eval_results.json",
            "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/alfworld_ood/train_stdout.txt",
            "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/alfworld_ood/eval_results.json",
            "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/alfworld_ood/eval_results_trajectories",
        ],
        "limitation": "Smoke scale only. IOD produced a deprecated/no-gain skill; OOD produced an active skill with no held-out gain because baseline already passed both sampled test instances.",
    }
    replace_solution(payload, "alfworld_reconstructed_adapter_pipeline", alfworld)

    baseline_rows = read_json(RESULT_DIR / "baseline_native_feasibility/baseline_native_feasibility.json")
    coevo_unofficial = read_json(RESULT_DIR / "baseline_native_feasibility/coevoskills_unofficial/probe_status.json")
    baseline = None
    for solution in payload["solutions"]:
        if solution["solution_id"] == "baseline_generator_comparison_path":
            baseline = solution
            break
    assert baseline is not None
    baseline.update(
        {
            "status": "partially_verified_contract_and_source_identity_native_adapters_unverified",
            "blocker_resolution": "solved for evaluator-output contract and source/probe discovery; not solved for native baseline algorithm execution or SkillGen-compatible adapters.",
            "meaning": "Four baseline slots still evaluate through the shared single-Markdown-skill harness. Trace2Skill, SkillX, and EvoSkill official/open-source repos have local source/probe evidence; official CoEvoSkills does not contain executable code. An unofficial CoEvoSkills fallback has compile/help evidence but is not official.",
            "baseline_native_feasibility": [
                {
                    "method": row["method"],
                    "probe_status": row["probe_status"],
                    "source_identity_solved": row["source_identity_solved"],
                    "native_algorithm_adapter_verified": row["native_algorithm_adapter_verified"],
                }
                for row in baseline_rows
            ],
            "coevoskills_unofficial_fallback": coevo_unofficial,
            "evidence": baseline["evidence"]
            + [
                "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/baseline_native_feasibility.md",
                "phase_0/runs/20260602/artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility/coevoskills_unofficial/probe_status.json",
                "phase_0/runs/20260602/code/official/baselines/CoEvoSkills_unofficial_AndyLongest/README.md",
            ],
            "limitation": "Native baseline algorithms are still not verified as SkillGen-compatible adapters. Official CoEvoSkills remains non-executable; the executable fallback is unofficial and still requires SkillsBench/Docker/opencode/API resources for full evolution.",
        }
    )

    for solution in payload["solutions"]:
        solution.setdefault("blocker_resolution", "verified for its scoped blocker under current local/reconstructed validation criteria.")

    recalc_counts(payload)
    write_json(FINAL_JSON, payload)
    FINAL_MD.write_text(render(payload), encoding="utf-8")

    append = "\n".join(
        [
            "",
            "- Re-audited baseline native feasibility after the user clarified that verification must prove blocker resolution, not only output-shape compatibility.",
            "- Installed probe-only dependencies inside Trace2Skill, SkillX, EvoSkill, and the unofficial CoEvoSkills fallback repo-local `.venv_probe` directories.",
            "- Verified Trace2Skill, SkillX, and EvoSkill source/probe surfaces; native SkillGen-compatible adapters remain unverified.",
            "- Confirmed official CoEvoSkills repo remains project-page-only at HEAD `3171de28cc8d3c3bbbec0ef5445e59faca46815b`.",
            "- Cloned and probe-verified unofficial CoEvoSkills fallback `AndyLongest/CoEvoSkills` at commit `96388fc20af036a86e8ad1f5352b912027481f52`; marked it unofficial and not a SkillGen adapter.",
            "- Added and executed ALFWorld OOD local smoke. Attempt1 failed because local OpenAI-compatible routing was not enabled; attempt2 failed because hash embeddings were not enabled; attempt3 completed train with local chat + hash embeddings and eval completed with exit code 0.",
            "- Updated final all-solution verification report and JSON with strict blocker-resolution statuses.",
            "",
        ]
    )
    with OP_LOG.open("a", encoding="utf-8") as handle:
        handle.write(append)
    print(FINAL_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
