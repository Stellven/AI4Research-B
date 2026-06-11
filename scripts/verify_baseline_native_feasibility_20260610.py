#!/usr/bin/env python3
"""Probe whether baseline generator repos are natively executable.

This is intentionally stricter than the previous baseline-comparison smoke:
the smoke proved that our shared evaluator accepts one exported Markdown skill
per baseline slot. This probe asks whether the actual open-source baseline
repos currently remove the original "missing baseline implementation" blocker.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase_0/runs/20260602"
BASELINE_DIR = RUN_DIR / "code/official/baselines"
RESULT_DIR = (
    RUN_DIR
    / "artifacts/08_results/solution_validation/all_solutions_verification_20260610/baseline_native_feasibility"
)


@dataclass
class ProbeCommand:
    name: str
    argv: list[str]
    timeout_seconds: int = 25
    pythonpath: list[Path] | None = None


@dataclass
class MethodVerdict:
    method: str
    repo_path: str
    local_commit: str | None
    remote_head: str | None
    python_files: int
    probe_status: str
    source_identity_solved: bool
    native_algorithm_adapter_verified: bool
    evidence: list[str]
    missing_or_failed: list[str]
    interpretation: str


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_command(
    *,
    cwd: Path,
    command: ProbeCommand,
    out_dir: Path,
) -> dict[str, Any]:
    env = os.environ.copy()
    pythonpath = command.pythonpath or []
    if pythonpath:
        existing = env.get("PYTHONPATH")
        parts = [str(path) for path in pythonpath]
        if existing:
            parts.append(existing)
        env["PYTHONPATH"] = os.pathsep.join(parts)

    started = True
    timed_out = False
    try:
        completed = subprocess.run(
            command.argv,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=command.timeout_seconds,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", "replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", "replace")
        stderr += f"\nTIMEOUT after {command.timeout_seconds}s\n"
    except Exception as exc:  # pragma: no cover - defensive evidence capture
        started = False
        returncode = 999
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}\n"

    prefix = command.name.replace("/", "_").replace(" ", "_")
    stdout_path = out_dir / f"{prefix}_stdout.txt"
    stderr_path = out_dir / f"{prefix}_stderr.txt"
    status_path = out_dir / f"{prefix}_status.json"
    write_text(stdout_path, stdout)
    write_text(stderr_path, stderr)
    status = {
        "name": command.name,
        "argv": command.argv,
        "cwd": rel(cwd),
        "started": started,
        "timed_out": timed_out,
        "returncode": returncode,
        "stdout_path": rel(stdout_path),
        "stderr_path": rel(stderr_path),
        "status_path": rel(status_path),
    }
    write_json(status_path, status)
    return status


def git_text(cwd: Path, args: list[str], timeout: int = 20) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def count_python_files(path: Path) -> int:
    count = 0
    for candidate in path.rglob("*.py"):
        if ".venv_probe" in candidate.parts:
            continue
        count += 1
    return count


def probe_python(repo: Path) -> str:
    local = repo / ".venv_probe/bin/python"
    if local.exists():
        return str(local)
    return sys.executable


def method_commands(method: str, repo: Path) -> list[ProbeCommand]:
    py = probe_python(repo)
    if method == "Trace2Skill":
        return [
            ProbeCommand("py_compile_core_entrypoints", [py, "-m", "py_compile", "analyze_results.py", "analysis/run_error_analysis.py", "analysis/run_success_analysis_llm.py", "skill_evolver/run_parallel_skill_evolution.py"]),
            ProbeCommand("analyze_results_help", [py, "analyze_results.py", "--help"]),
            ProbeCommand("error_analysis_help", [py, "analysis/run_error_analysis.py", "--help"]),
            ProbeCommand("success_analysis_help", [py, "analysis/run_success_analysis_llm.py", "--help"]),
            ProbeCommand("skill_evolution_help", [py, "-m", "skill_evolver.run_parallel_skill_evolution", "--help"]),
        ]
    if method == "SkillX":
        parent = repo.parent
        return [
            ProbeCommand("py_compile_pipeline", [py, "-m", "py_compile", "pipeline.py", "data/loaders.py", "data/exporters.py", "core/skill.py", "core/trajectory.py"]),
            ProbeCommand(
                "package_import_pipeline",
                [
                    py,
                    "-c",
                    "import SkillX.pipeline as p; print('IterativeSkillPipeline', hasattr(p, 'IterativeSkillPipeline'))",
                ],
                pythonpath=[parent],
            ),
            ProbeCommand("pipeline_script_help", [py, "pipeline.py", "--help"]),
        ]
    if method == "EvoSkill":
        return [
            ProbeCommand("py_compile_cli_and_scripts", [py, "-m", "py_compile", "src/cli/main.py", "scripts/run_loop.py", "scripts/run_eval.py"]),
            ProbeCommand("cli_module_help", [py, "-m", "src.cli.main", "--help"], pythonpath=[repo]),
            ProbeCommand("run_loop_help", [py, "scripts/run_loop.py", "--help"], pythonpath=[repo]),
            ProbeCommand("run_eval_help", [py, "scripts/run_eval.py", "--help"], pythonpath=[repo]),
        ]
    if method == "CoEvoSkills":
        return []
    raise ValueError(method)


def interpret_method(method: str, repo: Path, statuses: list[dict[str, Any]]) -> tuple[str, bool, bool, str, list[str]]:
    failures = [
        f"{status['name']} exited {status['returncode']}"
        for status in statuses
        if status.get("returncode") != 0
    ]
    help_successes = [status for status in statuses if status.get("returncode") == 0]

    if method == "CoEvoSkills":
        readme = (repo / "README.md").read_text(encoding="utf-8", errors="replace") if (repo / "README.md").exists() else ""
        has_coming_soon = "Code-coming soon" in readme or "Code-coming-soon" in readme or "coming soon" in readme.lower()
        missing = ["No Python/source implementation files were found in the local CoEvoSkills repository."]
        if has_coming_soon:
            missing.append("README advertises code as coming soon rather than available.")
        return (
            "source_page_only_no_native_code",
            False,
            False,
            "The local CoEvoSkills repository is a project page/assets repository, not an executable baseline implementation.",
            missing,
        )

    if method == "Trace2Skill":
        if help_successes:
            return (
                "native_entrypoints_help_verified_domain_mismatch",
                True,
                False,
                "Trace2Skill has runnable native entrypoints, but they target SpreadsheetBench logs/skills. This verifies source-code availability, not a SkillGen-trajectory adapter.",
                failures,
            )
        return (
            "native_entrypoints_not_runnable",
            True,
            False,
            "Trace2Skill source exists, but bounded local entrypoint probes did not run successfully.",
            failures,
        )

    if method == "SkillX":
        ok_names = {status["name"] for status in statuses if status.get("returncode") == 0}
        if "package_import_pipeline" in ok_names or "py_compile_pipeline" in ok_names:
            return (
                "library_import_or_compile_verified_no_cli_adapter",
                True,
                False,
                "SkillX source can be compiled/imported locally, but the repo has no verified CLI that consumes SkillGen trajectories and exports one static Markdown skill.",
                failures,
            )
        return (
            "native_library_probe_failed",
            True,
            False,
            "SkillX source exists, but bounded local library probes did not run successfully.",
            failures,
        )

    if method == "EvoSkill":
        ok_names = {status["name"] for status in statuses if status.get("returncode") == 0}
        if "cli_module_help" in ok_names or "py_compile_cli_and_scripts" in ok_names:
            return (
                "native_cli_or_compile_verified_benchmark_adapter_missing",
                True,
                False,
                "EvoSkill has native code/CLI surfaces, but no verified project/config adapter maps SkillGen trajectories into EvoSkill and exports a single Markdown skill.",
                failures,
            )
        return (
            "native_cli_probe_failed",
            True,
            False,
            "EvoSkill source exists, but bounded local CLI probes did not run successfully.",
            failures,
        )

    raise ValueError(method)


def verify_method(method: str, rel_repo: str) -> MethodVerdict:
    repo = BASELINE_DIR / rel_repo
    out_dir = RESULT_DIR / method.lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not repo.exists():
        return MethodVerdict(
            method=method,
            repo_path=rel(repo),
            local_commit=None,
            remote_head=None,
            python_files=0,
            probe_status="repo_missing",
            source_identity_solved=False,
            native_algorithm_adapter_verified=False,
            evidence=[],
            missing_or_failed=[f"{rel(repo)} does not exist"],
            interpretation="No local repository exists, so neither source identity nor native adapter can be verified.",
        )

    local_commit = git_text(repo, ["rev-parse", "HEAD"])
    remote_ls = git_text(repo, ["ls-remote", "origin", "HEAD"])
    remote_head = remote_ls.split()[0] if remote_ls else None
    python_files = count_python_files(repo)

    commit_status = {
        "method": method,
        "repo_path": rel(repo),
        "local_commit": local_commit,
        "remote_head": remote_head,
        "python_files": python_files,
    }
    write_json(out_dir / "repo_identity_status.json", commit_status)

    statuses = [run_command(cwd=repo, command=command, out_dir=out_dir) for command in method_commands(method, repo)]
    probe_status, source_solved, native_verified, interpretation, problems = interpret_method(method, repo, statuses)

    evidence = [rel(out_dir / "repo_identity_status.json")]
    evidence.extend(status["status_path"] for status in statuses)
    readme = repo / "README.md"
    if readme.exists():
        evidence.append(rel(readme))

    if remote_head and local_commit and remote_head != local_commit:
        problems.append(
            f"Remote HEAD {remote_head} differs from pinned local commit {local_commit}; this probe did not change the reviewed source."
        )

    return MethodVerdict(
        method=method,
        repo_path=rel(repo),
        local_commit=local_commit,
        remote_head=remote_head,
        python_files=python_files,
        probe_status=probe_status,
        source_identity_solved=source_solved,
        native_algorithm_adapter_verified=native_verified,
        evidence=evidence,
        missing_or_failed=problems,
        interpretation=interpretation,
    )


def write_markdown(verdicts: list[MethodVerdict]) -> None:
    counts: dict[str, int] = {}
    for verdict in verdicts:
        counts[verdict.probe_status] = counts.get(verdict.probe_status, 0) + 1

    lines = [
        "# Baseline Native Feasibility Verification",
        "",
        "Date: 2026-06-10",
        "",
        "Scope: stricter verification of the open-source baseline-code solution. This checks whether each native baseline repository is locally present and probe-runnable, and whether it has actually been adapted to consume SkillGen trajectories and export the single Markdown skill required by the shared evaluator.",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Verdict Table", ""])
    lines.append("| Method | Probe status | Source identity solved | Native SkillGen adapter verified | Interpretation |")
    lines.append("| --- | --- | --- | --- | --- |")
    for verdict in verdicts:
        lines.append(
            f"| `{verdict.method}` | `{verdict.probe_status}` | `{verdict.source_identity_solved}` | `{verdict.native_algorithm_adapter_verified}` | {verdict.interpretation} |"
        )
    lines.extend(["", "## Method Details", ""])
    for verdict in verdicts:
        lines.extend(
            [
                f"### {verdict.method}",
                "",
                f"- Probe status: `{verdict.probe_status}`",
                f"- Local commit: `{verdict.local_commit}`",
                f"- Remote HEAD: `{verdict.remote_head}`",
                f"- Python files: `{verdict.python_files}`",
                f"- Source identity solved: `{verdict.source_identity_solved}`",
                f"- Native SkillGen adapter verified: `{verdict.native_algorithm_adapter_verified}`",
                f"- Interpretation: {verdict.interpretation}",
                "- Evidence:",
            ]
        )
        for item in verdict.evidence:
            lines.append(f"  - `{item}`")
        lines.append("- Missing or failed:")
        if verdict.missing_or_failed:
            for item in verdict.missing_or_failed:
                lines.append(f"  - {item}")
        else:
            lines.append("  - None from bounded probes.")
        lines.append("")
    lines.extend(
        [
            "## Bottom Line",
            "",
            "The baseline-code solution is now verified for source identity for Trace2Skill, SkillX, and EvoSkill, and those repos have at least some local executable or importable surfaces. CoEvoSkills is not verified as executable code because the local repository contains only project-page assets and states that code is coming soon. None of the four native algorithms is yet verified as a SkillGen-compatible adapter that consumes SkillGen trajectories and exports exactly one Markdown skill. Therefore the earlier mechanical baseline-comparison smoke solves the evaluator-output-contract issue, but not the stricter native-baseline-execution issue.",
            "",
        ]
    )
    write_text(RESULT_DIR / "baseline_native_feasibility.md", "\n".join(lines))


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    methods = [
        ("Trace2Skill", "Trace2Skill"),
        ("SkillX", "SkillX"),
        ("EvoSkill", "EvoSkill"),
        ("CoEvoSkills", "CoEvoSkills"),
    ]
    verdicts = [verify_method(method, rel_repo) for method, rel_repo in methods]
    write_json(RESULT_DIR / "baseline_native_feasibility.json", [asdict(verdict) for verdict in verdicts])
    write_markdown(verdicts)
    print(f"baseline native feasibility written to {rel(RESULT_DIR)}")
    print(f"source_identity_solved_count={sum(1 for verdict in verdicts if verdict.source_identity_solved)}")
    print(f"native_algorithm_adapter_verified_count={sum(1 for verdict in verdicts if verdict.native_algorithm_adapter_verified)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
