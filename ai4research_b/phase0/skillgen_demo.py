"""Preliminary Phase 0 demo for the SkillGen paper.

This module intentionally stops before official-code execution when the paper
environment requires hosted APIs or other unapproved external resources.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_BLOCKED = "blocked"
STATUS_PENDING = "pending_human_review"


@dataclass(frozen=True)
class HardcodingDisclosure:
    id: str
    description: str
    reason: str
    impact: str


@dataclass(frozen=True)
class ExtractedClaim:
    id: str
    claim_type: str
    claim_text: str
    paper_location: str
    evidence_text: str
    requires_benchmark: bool
    status: str


@dataclass(frozen=True)
class BenchmarkClaim:
    id: str
    claim_id: str
    claim_type: str
    baseline_condition: str
    treatment_condition: str
    instance_matching: str
    metric: str
    expected_direction: str
    repair_regression_required: bool
    reported_delta_min_pp: float | None
    reported_delta_max_pp: float | None
    reported_improved_entries: int | None
    reported_unchanged_entries: int | None
    reported_regressed_entries: int | None
    reported_total_entries: int | None
    paper_location: str


@dataclass(frozen=True)
class EnvironmentBlocker:
    id: str
    source: str
    description: str
    evidence: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_pdf_text(pdf_path: Path) -> tuple[str, dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: pypdf. Install it into the repo-local venv with "
            "`env UV_CACHE_DIR=.uv-cache uv pip install --python .venv/bin/python pypdf`."
        ) from exc

    reader = PdfReader(str(pdf_path))
    page_texts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_texts.append(f"\n\n<!-- page {index} -->\n\n{text.strip()}")

    metadata = {str(k).lstrip("/"): str(v) for k, v in (reader.metadata or {}).items()}
    metadata["pages"] = len(reader.pages)
    return "\n".join(page_texts).strip(), metadata


def first_match(pattern: str, text: str, flags: int = re.IGNORECASE | re.DOTALL) -> re.Match[str] | None:
    return re.search(pattern, text, flags)


def snippet_around(text: str, needle: str, radius: int = 700) -> str:
    index = text.lower().find(needle.lower())
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(text), index + len(needle) + radius)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def extract_code_urls(text: str) -> list[str]:
    raw_urls = re.findall(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text)
    urls = sorted({url.rstrip(".,);:]") for url in raw_urls})
    return urls


def extract_claims(text: str) -> tuple[list[ExtractedClaim], list[BenchmarkClaim]]:
    gain_match = first_match(
        r"gains\s+from\s+\+?([0-9]+(?:\.[0-9]+)?)\s+to\s+\+?([0-9]+(?:\.[0-9]+)?)\s+percentage\s+points",
        text,
    )
    entry_match = first_match(
        r"out\s+of\s+([0-9]+)\s+held[-\s]*out\s+benchmark[\u2013\u2014\-]split[\u2013\u2014\-]model\s+entries,\s+"
        r"([0-9]+)\s+improve,\s+([0-9]+)\s+remain\s+unchanged,\s+and\s+only\s+([0-9]+)\s+show\s+regressions",
        text,
    )
    if not entry_match:
        entry_match = first_match(
            r"out\s+of\s+([0-9]+).*?entries,\s+([0-9]+)\s+improve,\s+([0-9]+)\s+remain\s+unchanged,.*?([0-9]+)\s+show\s+regressions",
            text,
        )

    gain_min = float(gain_match.group(1)) if gain_match else None
    gain_max = float(gain_match.group(2)) if gain_match else None
    total = int(entry_match.group(1)) if entry_match else None
    improved = int(entry_match.group(2)) if entry_match else None
    unchanged = int(entry_match.group(3)) if entry_match else None
    regressed = int(entry_match.group(4)) if entry_match else None

    evidence = snippet_around(text, "Table 1 shows three main patterns") or snippet_around(
        text, "improves average accuracy for all eight"
    )
    claim_text = (
        "SkillGen improves average held-out accuracy for all eight evaluated base LLMs, "
        "with reported gains ranging from "
        f"+{gain_min:g} to +{gain_max:g} percentage points."
        if gain_min is not None and gain_max is not None
        else "SkillGen improves average held-out accuracy for all eight evaluated base LLMs."
    )

    claims = [
        ExtractedClaim(
            id="claim_skillgen_table1_average_gains",
            claim_type="paired_intervention_performance",
            claim_text=claim_text,
            paper_location="Section 4, Table 1, Appendix C.2",
            evidence_text=evidence,
            requires_benchmark=True,
            status=STATUS_PENDING,
        )
    ]
    benchmark_claims = [
        BenchmarkClaim(
            id="bench_skillgen_table1_paired_accuracy",
            claim_id="claim_skillgen_table1_average_gains",
            claim_type="paired_intervention",
            baseline_condition="base agent rollout without generated SkillGen skill",
            treatment_condition="same base agent and same task instance with the generated SkillGen skill loaded",
            instance_matching="same held-out task instance identifier and random seed, as described in Appendix C.2",
            metric="accuracy",
            expected_direction="higher_is_better",
            repair_regression_required=True,
            reported_delta_min_pp=gain_min,
            reported_delta_max_pp=gain_max,
            reported_improved_entries=improved,
            reported_unchanged_entries=unchanged,
            reported_regressed_entries=regressed,
            reported_total_entries=total,
            paper_location="Table 1 and Appendix C.2",
        )
    ]
    return claims, benchmark_claims


def detect_environment_blockers(text: str) -> list[EnvironmentBlocker]:
    probes = [
        (
            "hosted_llm_apis",
            "Appendix C.5",
            "Experiments use hosted LLM APIs routed through OpenRouter; provider-side accelerator details are not exposed.",
            "OpenRouter",
        ),
        (
            "paid_token_budget",
            "Appendix C.5 / Table 4",
            "The reported runs consume millions of tokens per generated skill and cite API pricing.",
            "$8.2 per generated skill",
        ),
        (
            "external_benchmark_assets",
            "Appendix C.2 / Table 3",
            "Reproduction requires benchmark-specific datasets/environments and held-out split protocols.",
            "Controlled split protocol for benchmark-specific studies",
        ),
        (
            "proprietary_models",
            "Appendix C.1 / Table 2",
            "Some evaluated base models are proprietary hosted models, so exact provider-side inference is not locally reproducible.",
            "proprietary models are accessed through hosted APIs",
        ),
    ]
    blockers: list[EnvironmentBlocker] = []
    for blocker_id, source, description, needle in probes:
        evidence = snippet_around(text, needle, radius=450)
        if evidence:
            blockers.append(
                EnvironmentBlocker(
                    id=blocker_id,
                    source=source,
                    description=description,
                    evidence=evidence,
                )
            )
    return blockers


def hardcoding_disclosures() -> list[HardcodingDisclosure]:
    return [
        HardcodingDisclosure(
            id="target_paper_scope",
            description="The demo is intentionally scoped to SkillGen.pdf.",
            reason="The user explicitly asked for a preliminary demo that only needs to work for this paper.",
            impact="The claim selector prioritizes SkillGen's paired-intervention/Table 1 claim shape.",
        ),
        HardcodingDisclosure(
            id="claim_selector_priority",
            description="The demo selects the Table 1 average-gains claim as the primary benchmark claim.",
            reason="The existing Phase 0 SkillGen note and the paper text identify it as the strongest Phase 0 target.",
            impact="Other SkillGen claims are not selected for the preliminary run, though they remain in the parsed paper text.",
        ),
        HardcodingDisclosure(
            id="execution_stop_policy",
            description="The demo blocks before official-code execution when hosted APIs, paid token use, external benchmark assets, or missing human approval are detected.",
            reason="Phase 0 rules require a human-visible command gate before risky or costly third-party execution.",
            impact="The demo produces a blocked validation package instead of running official benchmarks.",
        ),
    ]


def render_claims_md(claims: list[ExtractedClaim], benchmark_claims: list[BenchmarkClaim]) -> str:
    lines = ["# Extracted SkillGen Claims", "", "## Selected Claim", ""]
    for claim in claims:
        lines.extend(
            [
                f"- ID: `{claim.id}`",
                f"- Type: `{claim.claim_type}`",
                f"- Status: `{claim.status}`",
                f"- Paper location: {claim.paper_location}",
                "",
                claim.claim_text,
                "",
                "### Evidence Snippet",
                "",
                f"> {claim.evidence_text}" if claim.evidence_text else "> No snippet extracted.",
                "",
            ]
        )
    lines.extend(["## Benchmark Contract Summary", ""])
    for bench in benchmark_claims:
        lines.extend(
            [
                f"- ID: `{bench.id}`",
                f"- Baseline: {bench.baseline_condition}",
                f"- Treatment: {bench.treatment_condition}",
                f"- Matching: {bench.instance_matching}",
                f"- Metric: `{bench.metric}`",
                f"- Reported gain range: `{bench.reported_delta_min_pp}` to `{bench.reported_delta_max_pp}` percentage points",
                f"- Reported entry counts: improved `{bench.reported_improved_entries}`, unchanged `{bench.reported_unchanged_entries}`, regressed `{bench.reported_regressed_entries}`, total `{bench.reported_total_entries}`",
                "",
            ]
        )
    return "\n".join(lines)


def render_command_plan(code_urls: list[str], blockers: list[EnvironmentBlocker]) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "status": STATUS_BLOCKED,
        "official_code_urls": code_urls,
        "install_commands": [],
        "benchmark_commands": [],
        "source": "SkillGen.pdf paper text only; official repository README was not executed or interpreted in this demo run.",
        "requires_network": True,
        "requires_gpu": None,
        "requires_dataset_download": True,
        "requires_api_keys": True,
        "requires_paid_api_or_token_budget": True,
        "requires_docker": None,
        "reason_for_block": (
            "The paper reports hosted LLM API execution through OpenRouter, proprietary models, "
            "external benchmark split protocols, and token costs. Official benchmark execution "
            "requires human command review and credentials/resources."
        ),
        "environment_blockers": [asdict(blocker) for blocker in blockers],
    }


def render_report(run_id: str, claims: list[ExtractedClaim], benchmark_claims: list[BenchmarkClaim], blockers: list[EnvironmentBlocker]) -> str:
    claim = claims[0]
    bench = benchmark_claims[0]
    blocker_lines = "\n".join(
        f"- `{blocker.id}` ({blocker.source}): {blocker.description}" for blocker in blockers
    )
    return f"""# SkillGen Phase 0 Preliminary Validation Report

Run ID: `{run_id}`

## Status

`blocked`

This preliminary demo completed paper intake, PDF parsing, claim extraction, and benchmark-contract writing. It intentionally stopped before official code installation or benchmark execution because the paper's reported environment requires hosted LLM APIs, OpenRouter/model-provider routing, benchmark-specific datasets/environments, token costs, and human approval before execution.

## Selected Claim

{claim.claim_text}

- Claim ID: `{claim.id}`
- Claim type: `{claim.claim_type}`
- Paper location: {claim.paper_location}
- Benchmark claim ID: `{bench.id}`

## Benchmark Contract

- Baseline condition: {bench.baseline_condition}
- Treatment condition: {bench.treatment_condition}
- Instance matching: {bench.instance_matching}
- Metric: `{bench.metric}`
- Reported gain range: `{bench.reported_delta_min_pp}` to `{bench.reported_delta_max_pp}` percentage points
- Reported entry counts: improved `{bench.reported_improved_entries}`, unchanged `{bench.reported_unchanged_entries}`, regressed `{bench.reported_regressed_entries}`, total `{bench.reported_total_entries}`

## Why Execution Stopped

{blocker_lines}

## What Was Not Done

- The official SkillGen repository was not installed.
- No official benchmark command was run.
- No hosted model/API call was made.
- No benchmark dataset or model weight was downloaded.
- No claim was marked reproduced, partially reproduced, or not reproduced.

## Next Human Gate

Review `command_plan.json` and decide whether to provide credentials, benchmark data, runtime budget, and approval for official code intake and execution.
"""


def run_demo(paper: Path, output_root: Path, run_id: str | None) -> Path:
    if not paper.exists():
        raise SystemExit(f"Paper not found: {paper}")
    run_id = run_id or f"skillgen_phase0_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = output_root / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    input_dir = run_dir / "input"
    phase_dir = run_dir / "phase_0"
    code_dir = run_dir / "code"
    integration_dir = run_dir / "integration"
    playback_dir = run_dir / "playback"
    raw_outputs_dir = phase_dir / "raw_benchmark_outputs"
    input_dir.mkdir(parents=True, exist_ok=True)
    raw_outputs_dir.mkdir(parents=True, exist_ok=True)
    (code_dir / "official").mkdir(parents=True, exist_ok=True)

    started = utc_now()
    append_jsonl(
        integration_dir / "pipeline_run_log.jsonl",
        {"run_id": run_id, "step": "run_intake", "status": "started", "started_at": started},
    )
    shutil.copy2(paper, input_dir / "paper.pdf")

    text, metadata = read_pdf_text(paper)
    code_urls = extract_code_urls(text)
    claims, benchmark_claims = extract_claims(text)
    blockers = detect_environment_blockers(text)
    hardcodings = hardcoding_disclosures()

    input_manifest = {
        "schema_version": "0.1",
        "run_id": run_id,
        "created_at": started,
        "paper_source_path": str(paper),
        "paper_copied_to": "input/paper.pdf",
        "official_code_urls_extracted": code_urls,
        "demo_scope": "SkillGen.pdf preliminary Phase 0 demo",
    }
    write_json(input_dir / "input_manifest.json", input_manifest)

    write_text(phase_dir / "paper_parse.md", f"# SkillGen Paper Parse\n\n{ text }\n")
    write_json(
        phase_dir / "paper_parse.json",
        {
            "schema_version": "0.1",
            "metadata": metadata,
            "pages": metadata.get("pages"),
            "title": metadata.get("Title"),
            "arxiv_id": metadata.get("arXivID"),
            "code_urls": code_urls,
            "text_characters": len(text),
            "parser": "pypdf.PdfReader.extract_text",
        },
    )
    write_json(phase_dir / "claims.json", {"schema_version": "0.1", "claims": [asdict(c) for c in claims]})
    write_json(
        phase_dir / "benchmark_claims.json",
        {"schema_version": "0.1", "benchmark_claims": [asdict(b) for b in benchmark_claims]},
    )
    write_text(phase_dir / "claims.md", render_claims_md(claims, benchmark_claims))
    write_text(
        phase_dir / "human_claim_review.md",
        "# Human Claim Review\n\nStatus: `pending`\n\nThe preliminary demo selected the Table 1 paired-intervention accuracy claim. A human must approve, revise, or reject this claim before official benchmark execution.\n",
    )
    write_json(
        phase_dir / "code_manifest.json",
        {
            "schema_version": "0.1",
            "status": STATUS_BLOCKED,
            "official_code_urls": code_urls,
            "code_path": "code/official",
            "note": "Official code was not cloned or executed by this preliminary demo.",
        },
    )
    write_text(
        phase_dir / "repo_snapshot.md",
        "# Repository Snapshot\n\nStatus: `blocked`\n\nOfficial repository snapshot is unavailable in this preliminary run because code intake was not performed. Extracted code URL(s):\n\n"
        + "\n".join(f"- {url}" for url in code_urls)
        + "\n",
    )
    write_text(
        phase_dir / "official_instructions.md",
        "# Official Instructions\n\nStatus: `blocked`\n\nThis demo extracted the official code URL from the paper but did not interpret README commands or execute third-party code. Command extraction must happen after official code intake and human review.\n",
    )
    command_plan = render_command_plan(code_urls, blockers)
    write_json(phase_dir / "command_plan.json", command_plan)
    write_text(
        phase_dir / "human_command_review.md",
        "# Human Command Review\n\nStatus: `required`\n\nOfficial install and benchmark commands are blocked pending official code intake. The paper already indicates likely network/API/cost/resource risks, so execution must not proceed silently.\n",
    )
    write_text(
        phase_dir / "environment_plan.md",
        "# Environment Plan\n\nStatus: `blocked`\n\nThe paper reports hosted LLM APIs routed through OpenRouter, external benchmark environments, token costs, and proprietary model providers. This preliminary demo does not attempt to replicate that environment.\n",
    )
    write_text(phase_dir / "install_stdout.txt", "")
    write_text(phase_dir / "install_stderr.txt", "Install not run: blocked before official code execution.\n")
    write_json(
        phase_dir / "environment.json",
        {
            "schema_version": "0.1",
            "status": STATUS_BLOCKED,
            "local_parser_environment": "repo-local .venv using pypdf",
            "official_reproduction_environment": "not created",
            "blockers": [asdict(b) for b in blockers],
        },
    )
    write_text(
        phase_dir / "benchmark_run_plan.md",
        "# Benchmark Run Plan\n\nStatus: `blocked`\n\nTarget benchmark contract: paired no-skill vs SkillGen-skill held-out accuracy under the paper's split protocol. Execution requires official repo instructions, API credentials, benchmark data/environments, and human approval.\n",
    )
    write_text(phase_dir / "benchmark_stdout.txt", "")
    write_text(phase_dir / "benchmark_stderr.txt", "Benchmark not run: blocked before official code execution.\n")
    write_json(
        phase_dir / "benchmark_results.json",
        {"schema_version": "0.1", "status": STATUS_BLOCKED, "results": [], "reason": "benchmark_not_run"},
    )
    write_text(
        phase_dir / "benchmark_results.md",
        "# Benchmark Results\n\nStatus: `blocked`\n\nNo official benchmark results were produced because execution stopped before official code installation and benchmark execution.\n",
    )
    write_json(
        phase_dir / "claim_comparison.json",
        {
            "schema_version": "0.1",
            "status": STATUS_BLOCKED,
            "claim_id": claims[0].id,
            "benchmark_claim_id": benchmark_claims[0].id,
            "paper_reported": asdict(benchmark_claims[0]),
            "observed": None,
            "reason": "official_benchmark_not_run",
        },
    )
    write_text(
        phase_dir / "claim_comparison.md",
        "# Claim Comparison\n\nStatus: `blocked`\n\nThe paper-reported paired accuracy claim was extracted, but no observed benchmark result exists yet. No reproduction verdict is assigned.\n",
    )
    write_text(
        phase_dir / "human_result_review.md",
        "# Human Result Review\n\nStatus: `not_ready`\n\nThere are no official benchmark results to review yet.\n",
    )
    write_text(phase_dir / "research_validation_report.md", render_report(run_id, claims, benchmark_claims, blockers))
    write_text(
        phase_dir / "failure_modes.md",
        "# Failure Modes And Blockers\n\n"
        + "\n".join(f"- `{b.id}`: {b.description}" for b in blockers)
        + "\n",
    )
    write_json(
        phase_dir / "hardcoding_disclosures.json",
        {"schema_version": "0.1", "hardcodings": [asdict(item) for item in hardcodings]},
    )
    write_text(
        phase_dir / "hardcoding_disclosures.md",
        "# Hardcoding Disclosures\n\n"
        + "\n\n".join(
            f"## {item.id}\n\n- Description: {item.description}\n- Reason: {item.reason}\n- Impact: {item.impact}"
            for item in hardcodings
        )
        + "\n",
    )
    write_text(
        playback_dir / "thought_playback.md",
        "# Thought Playback Summary\n\nThe demo treated SkillGen as a paired-intervention paper, selected the Table 1 average held-out accuracy claim, and blocked execution because official reproduction requires hosted APIs, external benchmark assets, and human command approval.\n",
    )
    append_jsonl(
        playback_dir / "decision_trace.jsonl",
        {
            "run_id": run_id,
            "timestamp": utc_now(),
            "decision": "block_before_execution",
            "evidence": [asdict(b) for b in blockers],
            "artifact": "phase_0/command_plan.json",
        },
    )
    append_jsonl(
        integration_dir / "pipeline_run_log.jsonl",
        {
            "run_id": run_id,
            "step": "preliminary_demo",
            "status": STATUS_BLOCKED,
            "ended_at": utc_now(),
            "artifacts_written": [
                "input/input_manifest.json",
                "phase_0/paper_parse.md",
                "phase_0/claims.json",
                "phase_0/benchmark_claims.json",
                "phase_0/command_plan.json",
                "phase_0/research_validation_report.md",
            ],
        },
    )
    return run_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the preliminary SkillGen Phase 0 demo.")
    parser.add_argument("--paper", type=Path, default=Path("docs/SkillGen.pdf"), help="Path to SkillGen.pdf")
    parser.add_argument("--output-root", type=Path, default=Path("runs"), help="Directory for run artifacts")
    parser.add_argument("--run-id", default=None, help="Optional deterministic run id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_dir = run_demo(args.paper, args.output_root, args.run_id)
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
