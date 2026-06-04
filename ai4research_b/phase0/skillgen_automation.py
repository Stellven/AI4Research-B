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
STATUS_READY_FOR_RECONSTRUCTED_EXECUTION = "ready_for_reconstructed_execution"
STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION = "ready_for_reconstructed_ablation_execution"
STATUS_BLOCKED_PENDING_RECONSTRUCTED_ABLATION_CONTRACT = "blocked_pending_reconstructed_ablation_contract"
STATUS_BLOCKED_PENDING_BASELINE_SOURCE_IDENTITY_REVIEW = "blocked_pending_baseline_source_identity_review"
STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON = "ready_for_reconstructed_baseline_comparison"
STATUS_PARTIALLY_READY_FULL_MATRIX = "partially_ready_full_matrix"
STATUS_READY_FOR_FULL_MATRIX_EXECUTION_AFTER_DEPENDENCIES = "ready_for_full_matrix_execution_after_dependencies"
STATUS_READY_FOR_RECONSTRUCTED_ALFWORLD_IMPLEMENTATION = "ready_for_reconstructed_alfworld_implementation"
STATUS_READY_FOR_SOURCE_IDENTITY_REVIEW = "ready_for_source_identity_review"
STATUS_READY_FOR_RECONSTRUCTED_ABLATION_HUMAN_REVIEW = "ready_for_reconstructed_ablation_human_review"
STATUS_BLOCKED_BY_ALFWORLD_OOD_EXECUTION = "blocked_by_alfworld_ood_execution"
STATUS_READY_FOR_TRACE_GENERATION_AFTER_FULL_RUNS = "ready_for_trace_generation_after_full_runs"
STATUS_READY_FOR_FULL_TOKEN_COST_EXECUTION = "ready_for_full_token_cost_execution"
STATUS_READY_FOR_FULL_SCOPE_ARTIFACT_CHECK = "ready_for_full_scope_artifact_check"
STATUS_PROVIDER_UNAVAILABLE = "provider_unavailable"
STATUS_WAITING_PROVIDER_ROUTE_RESOLUTION = "waiting_provider_route_resolution"
LONG_INFERENCE_APPROVED_FIELD = "long_inference_approved"

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

PROVIDER_ENV_KEYS = [
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "MISTRAL_API_KEY",
    "XAI_API_KEY",
    "GROQ_API_KEY",
    "TOGETHER_API_KEY",
    "FIREWORKS_API_KEY",
    "DEEPINFRA_API_KEY",
]

NON_OPENAI_DIRECT_PROVIDER_KEY_HINTS = {
    "anthropic/": ["ANTHROPIC_API_KEY"],
    "google/": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "mistralai/": ["MISTRAL_API_KEY"],
    "x-ai/": ["XAI_API_KEY"],
    "qwen/": ["TOGETHER_API_KEY", "FIREWORKS_API_KEY", "DEEPINFRA_API_KEY"],
    "meta-llama/": ["TOGETHER_API_KEY", "FIREWORKS_API_KEY", "DEEPINFRA_API_KEY", "GROQ_API_KEY"],
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

ABLATION_ARMS = [
    {
        "arm_id": "Full",
        "name": "Complete SkillGen",
        "paper_behavior": "Run contrastive induction, refinement, verification gate, Failure Lessons, and script/reference bundles where enabled by the paper setup.",
        "implementation_type": "full_config",
        "implementation_method": "Use the normal SkillGen configuration as the paired reference arm.",
        "config_overrides": {
            "pipeline.max_refine_rounds": 8,
            "verification.gate_enabled": True,
            "generation.include_failure_lessons": True,
            "generation.generate_scripts": "paper_target_dependent",
            "generation.generate_references": "paper_target_dependent",
        },
        "patch_or_wrapper_path": None,
        "deviation_label": "reference_full_system",
        "safety_note": "Full must use the same split, model route, judge route, and seed as every ablation arm.",
        "rollback_note": "No rollback needed; this is the reference arm.",
    },
    {
        "arm_id": "A1",
        "name": "ICL k=3 instead of induced skill",
        "paper_behavior": "Replace induced skill generation with three in-context demonstrations.",
        "implementation_type": "wrapper_generated_skill",
        "implementation_method": (
            "Select three baseline-success construction trajectories with seed 42, render them as a Markdown demonstration skill, "
            "skip induction/refinement for this arm, and evaluate the demonstration skill through eval_skill.py."
        ),
        "config_overrides": {
            "ablation.mode": "icl_k3_demonstration_skill",
            "ablation.demo_k": 3,
            "ablation.demo_source": "construction_baseline_successes",
            "ablation.demo_seed": 42,
        },
        "patch_or_wrapper_path": "artifacts/ablation_configs/A1_icl_k3_demonstration_skill.md",
        "deviation_label": "reconstructed_icl_k3_demo_selection",
        "safety_note": "Demonstrations must come only from construction trajectories; held-out test instances must not leak into the skill text.",
        "rollback_note": "Delete the generated demonstration skill and rerun the normal Full generation path.",
    },
    {
        "arm_id": "A2",
        "name": "No refinement",
        "paper_behavior": "Use the initial generated candidate skill without later refinement rounds.",
        "implementation_type": "config_only",
        "implementation_method": "Set pipeline.max_refine_rounds to 1 so only the initial generation round is evaluated.",
        "config_overrides": {
            "pipeline.max_refine_rounds": 1,
        },
        "patch_or_wrapper_path": "artifacts/ablation_configs/A2_no_refinement.yaml",
        "deviation_label": "reconstructed_no_refinement_config",
        "safety_note": "Keep verification output for round 1 so failures and regressions remain auditable.",
        "rollback_note": "Restore pipeline.max_refine_rounds to the Full arm value.",
    },
    {
        "arm_id": "A3",
        "name": "No verification gate",
        "paper_behavior": "Disable the construction-time gate that rejects skills without positive verification gain.",
        "implementation_type": "behavioral_config_or_runner_patch",
        "implementation_method": (
            "Record verification results normally, but force the selected candidate into held-out evaluation even when the gate fails. "
            "If the official code marks failed skills as DEPRECATED, the ablation runner must override that status only for this arm."
        ),
        "config_overrides": {
            "verification.disable_gate_for_ablation": True,
            "verification.record_results": True,
            "ablation.force_eval_failed_gate_skill": True,
        },
        "patch_or_wrapper_path": "artifacts/ablation_patches/A3_disable_gate.patch",
        "deviation_label": "safety_gate_disabled_reconstructed_ablation",
        "safety_note": "This arm intentionally disables a safety/quality gate; raw failed-gate evidence must be preserved before held-out evaluation.",
        "rollback_note": "Remove the A3 runner override and restore normal deprecated-skill/no-op handling.",
    },
    {
        "arm_id": "A4",
        "name": "No Failure Lessons",
        "paper_behavior": "Remove Failure Lessons from the skill generation/refinement process.",
        "implementation_type": "prompt_patch_preferred",
        "implementation_method": (
            "Preferred path: patch generation/refinement prompts so they neither request nor emit a Failure Lessons section. "
            "Fallback path: remove the final '## Failure lessons' section before held-out evaluation and label it as a weaker post-process ablation."
        ),
        "config_overrides": {
            "generation.include_failure_lessons": False,
            "refinement.include_failure_lessons": False,
        },
        "patch_or_wrapper_path": "artifacts/ablation_patches/A4_no_failure_lessons_prompt.patch",
        "deviation_label": "reconstructed_no_failure_lessons_prompt",
        "safety_note": "If the fallback post-process path is used, record that the generator still saw failure evidence during construction.",
        "rollback_note": "Restore the original generation/refinement prompts and skill post-processing.",
    },
    {
        "arm_id": "A5",
        "name": "Plain-text skill, no script/reference bundle",
        "paper_behavior": "Disable executable helper scripts and reference bundles so the skill is plain text only.",
        "implementation_type": "config_only",
        "implementation_method": "Set generation.generate_scripts and generation.generate_references to false for this arm.",
        "config_overrides": {
            "generation.generate_scripts": False,
            "generation.generate_references": False,
        },
        "patch_or_wrapper_path": "artifacts/ablation_configs/A5_plain_text_skill.yaml",
        "deviation_label": "reconstructed_plain_text_skill_config",
        "safety_note": "Only compare A5 against Full on dataset-model pairs where Full actually enables script/reference bundles.",
        "rollback_note": "Restore script/reference generation to the Full arm setting.",
    },
]

LIVECODEBENCH_SOURCE_REL = "data/livecodebench/release_v6_all.json"
LIVECODEBENCH_TRAIN_REL = "data/livecodebench/train_release_v6_n50_seed42.json"
LIVECODEBENCH_TEST_REL = "data/livecodebench/test_release_v6_n150_seed42.json"
LIVECODEBENCH_SPLIT_MANIFEST_REL = "data/livecodebench/split_release_v6_n50_n150_seed42_manifest.json"
LIVECODEBENCH_RELEASE = "release_v6"
LIVECODEBENCH_HELD_OUT_SPLIT = "test_release_v6"
LIVECODEBENCH_CONSTRUCTION_N = 50
LIVECODEBENCH_TEST_N = 150
LIVECODEBENCH_SPLIT_SEED = 42

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

ALFWORLD_GROUP_A_CONTRACT_DOCS = {
    "source_review": [
        Path("logs/phase_0_parallel_20260604/A_alfworld/alfworld_source_review.md"),
        Path("artifacts/03_code_and_sources/alfworld_source_review.md"),
        Path("artifacts/alfworld_source_review.md"),
    ],
    "adapter_contract": [
        Path("logs/phase_0_parallel_20260604/A_alfworld/alfworld_adapter_contract.md"),
        Path("artifacts/06_plans_and_contracts/alfworld_adapter_contract.md"),
        Path("artifacts/alfworld_adapter_contract.md"),
    ],
    "split_contract": [
        Path("logs/phase_0_parallel_20260604/A_alfworld/alfworld_split_contract.md"),
        Path("artifacts/06_plans_and_contracts/alfworld_split_contract.md"),
        Path("artifacts/alfworld_split_contract.md"),
    ],
    "deviation_note": [
        Path("logs/phase_0_parallel_20260604/A_alfworld/alfworld_deviation_note.md"),
        Path("artifacts/09_safety_and_deviations/alfworld_deviation_note.md"),
        Path("artifacts/alfworld_deviation_note.md"),
    ],
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


BASELINE_GENERATOR_SOURCES = [
    {
        "source_key": "trace2skill",
        "method_name": "Trace2Skill",
        "repository": "Qwen-Applications/Trace2Skill",
        "source_url": "https://github.com/Qwen-Applications/Trace2Skill.git",
        "target_path": "code/official/baselines/Trace2Skill",
        "expected_license_spdx": "Apache-2.0",
        "paper_identity_basis": "SkillGen Appendix C.6 names Trace2Skill as a baseline generator; Group D identifies this public repository as the candidate implementation.",
        "native_output": "A skill directory evolved from trajectory analyses, with spreadsheet-agent skills and released skill artifacts.",
        "single_skill_adapter_strategy": (
            "Run Trace2Skill on the SkillGen training trajectories, then flatten the selected evolved skill "
            "directory and its changelog into one Markdown skill body for the shared SkillGen eval harness."
        ),
    },
    {
        "source_key": "skillx",
        "method_name": "SkillX",
        "repository": "zjunlp/SkillX",
        "source_url": "https://github.com/zjunlp/SkillX.git",
        "target_path": "code/official/baselines/SkillX",
        "expected_license_spdx": "MIT",
        "paper_identity_basis": "SkillGen Appendix C.6 names SkillX as a baseline generator; Group D identifies this public repository as the candidate implementation.",
        "native_output": "A reusable skill knowledge base with planning, functional, and atomic skill hierarchy.",
        "single_skill_adapter_strategy": (
            "Build the SkillX skill knowledge base from the SkillGen training trajectories, then render the "
            "chosen hierarchy into one static Markdown skill without retrieval or test-time skill selection."
        ),
    },
    {
        "source_key": "evoskill",
        "method_name": "EvoSkill",
        "repository": "sentient-agi/EvoSkill",
        "source_url": "https://github.com/sentient-agi/EvoSkill.git",
        "target_path": "code/official/baselines/EvoSkill",
        "expected_license_spdx": "Apache-2.0",
        "paper_identity_basis": "SkillGen Appendix C.6 names EvoSkill as a baseline generator; Group D identifies this public repository as the candidate implementation.",
        "native_output": "An evolved agent program containing prompt and skill mutations selected by validation performance.",
        "single_skill_adapter_strategy": (
            "Run the EvoSkill loop against the SkillGen construction split, select the best validation program, "
            "and export only the skill/prompt delta that can be represented as one Markdown skill."
        ),
    },
    {
        "source_key": "coevoskills",
        "method_name": "CoEvoSkills",
        "repository": "Zhang-Henry/CoEvoSkills",
        "source_url": "https://github.com/Zhang-Henry/CoEvoSkills.git",
        "target_path": "code/official/baselines/CoEvoSkills",
        "expected_license_spdx": "MIT",
        "paper_identity_basis": "SkillGen Appendix C.6 names CoEvoSkills as a baseline generator; Group D identifies this public repository as the candidate implementation.",
        "native_output": "A structured multi-file skill package generated with co-evolutionary verification.",
        "single_skill_adapter_strategy": (
            "Use the generator/verifier loop on the SkillGen construction split, then render the selected "
            "skill package into one Markdown instruction artifact and drop scripts, assets, and references."
        ),
    },
]


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


def read_artifact_json(paths: RunPaths, filename: str, categories: list[str] | None = None) -> Any:
    for candidate in [paths.artifacts_dir / filename, *[paths.artifacts_dir / category / filename for category in (categories or [])]]:
        if candidate.exists():
            return read_json(candidate)
    return {}


def write_json_with_category_mirrors(paths: RunPaths, filename: str, payload: Any, categories: list[str]) -> None:
    write_json(paths.artifacts_dir / filename, payload)
    for category in categories:
        category_dir = paths.artifacts_dir / category
        if category_dir.exists():
            write_json(category_dir / filename, payload)


def write_text_with_category_mirrors(paths: RunPaths, filename: str, text: str, categories: list[str]) -> None:
    write_text(paths.artifacts_dir / filename, text)
    for category in categories:
        category_dir = paths.artifacts_dir / category
        if category_dir.exists():
            write_text(category_dir / filename, text)


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


def json_string_field_from_prefix(prefix: str, field: str) -> str | None:
    match = re.search(rf'"{re.escape(field)}"\s*:\s*("(?:\\.|[^"\\])*")', prefix)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def dataset_envelope_from_prefix(source_path: Path) -> dict[str, Any]:
    with source_path.open(encoding="utf-8") as handle:
        prefix = handle.read(2_000_000)
    dataset_id = json_string_field_from_prefix(prefix, "dataset_id") or source_path.stem
    task_name = json_string_field_from_prefix(prefix, "task_name") or dataset_id
    task_type = json_string_field_from_prefix(prefix, "task_type") or "binary"
    return {
        "dataset_id": dataset_id,
        "task_name": task_name,
        "task_type": task_type,
    }


def iter_dataset_instances(source_path: Path, array_key: str = "instances") -> Any:
    decoder = json.JSONDecoder()
    chunk_size = 1_048_576
    key = f'"{array_key}"'
    with source_path.open(encoding="utf-8") as handle:
        buffer = ""
        pos = 0
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                raise ValueError(f"Could not find top-level `{array_key}` array in {source_path}.")
            buffer += chunk
            key_index = buffer.find(key)
            if key_index < 0:
                if len(buffer) > len(key) + 256:
                    buffer = buffer[-(len(key) + 256) :]
                continue
            colon_index = buffer.find(":", key_index + len(key))
            bracket_index = buffer.find("[", colon_index + 1) if colon_index >= 0 else -1
            if bracket_index >= 0:
                pos = bracket_index + 1
                break

        while True:
            while True:
                if pos >= len(buffer):
                    chunk = handle.read(chunk_size)
                    if not chunk:
                        raise ValueError(f"Unterminated `{array_key}` array in {source_path}.")
                    buffer += chunk
                    continue
                if buffer[pos] in " \t\r\n,":
                    pos += 1
                    continue
                break
            if buffer[pos] == "]":
                return

            while True:
                try:
                    item, end = decoder.raw_decode(buffer, pos)
                    yield item
                    pos = end
                    if pos > chunk_size:
                        buffer = buffer[pos:]
                        pos = 0
                    break
                except json.JSONDecodeError:
                    chunk = handle.read(chunk_size)
                    if not chunk:
                        raise
                    buffer += chunk


def count_dataset_instances_streaming(source_path: Path) -> int:
    return sum(1 for _ in iter_dataset_instances(source_path))


def livecodebench_split_paths(run_dir: Path) -> dict[str, Path]:
    paths = paths_for(run_dir)
    return {
        "source": paths.official_dir / LIVECODEBENCH_SOURCE_REL,
        "train": paths.official_dir / LIVECODEBENCH_TRAIN_REL,
        "test": paths.official_dir / LIVECODEBENCH_TEST_REL,
        "manifest": paths.official_dir / LIVECODEBENCH_SPLIT_MANIFEST_REL,
    }


def livecodebench_split_exists(run_dir: Path) -> bool:
    split_paths = livecodebench_split_paths(run_dir)
    return split_paths["train"].exists() and split_paths["test"].exists() and split_paths["manifest"].exists()


def livecodebench_split_manifest(run_dir: Path) -> dict[str, Any] | None:
    manifest_path = livecodebench_split_paths(run_dir)["manifest"]
    if manifest_path.exists():
        try:
            manifest = read_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            return None
        if isinstance(manifest, dict):
            return manifest
    return None


def build_livecodebench_source_review(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    split_paths = livecodebench_split_paths(run_dir)
    source_path = split_paths["source"]
    adapter_path = paths.official_dir / "benchmarks" / "livecodebench_adapter.py"
    source_exists = source_path.exists()
    envelope = dataset_envelope_from_prefix(source_path) if source_exists else {}
    instance_count = None
    manifest = livecodebench_split_manifest(run_dir)
    if manifest:
        instance_count = manifest.get("source_total_instances")
    return {
        "schema_version": "0.1",
        "source_key": "livecodebench",
        "status": "source_ready_needs_or_has_split" if source_exists and adapter_path.exists() else STATUS_BLOCKED,
        "official_source": "livecodebench/code_generation_lite",
        "official_release": LIVECODEBENCH_RELEASE,
        "paper_held_out_split": LIVECODEBENCH_HELD_OUT_SPLIT,
        "source_dataset": rel(source_path, paths.run_dir),
        "source_exists": source_exists,
        "adapter": rel(adapter_path, paths.run_dir),
        "adapter_exists": adapter_path.exists(),
        "dataset_id": envelope.get("dataset_id"),
        "task_name": envelope.get("task_name"),
        "task_type": envelope.get("task_type"),
        "source_total_instances": instance_count,
        "paper_table3": {
            "construction_n": LIVECODEBENCH_CONSTRUCTION_N,
            "held_out_test_n": LIVECODEBENCH_TEST_N,
            "seed": LIVECODEBENCH_SPLIT_SEED,
            "note": "Sampled from release v6; seed 42.",
        },
        "identity_basis": [
            "Official SkillGen code includes benchmarks/livecodebench_adapter.py.",
            "Official preparation plan uses livecodebench/code_generation_lite with release_v6.",
            "The local release_v6_all.json is already a SkillGen TaskInstance wrapper.",
        ],
    }


def build_livecodebench_split_contract(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    split_paths = livecodebench_split_paths(run_dir)
    manifest = livecodebench_split_manifest(run_dir)
    status = STATUS_READY_FOR_EXECUTION if livecodebench_split_exists(run_dir) else "blocked_pending_split_generation"
    return {
        "schema_version": "0.1",
        "target_id": "livecodebench",
        "status": status,
        "paper_claims_unblocked": [
            "claim_table1_average_gains_all_models",
            "claim_table1_entry_counts",
        ],
        "paper_table3_contract": {
            "benchmark": "LiveCodeBench",
            "held_out_test_split": LIVECODEBENCH_HELD_OUT_SPLIT,
            "construction_n": LIVECODEBENCH_CONSTRUCTION_N,
            "held_out_test_n": LIVECODEBENCH_TEST_N,
            "source_release": LIVECODEBENCH_RELEASE,
            "seed": LIVECODEBENCH_SPLIT_SEED,
        },
        "source_dataset": rel(split_paths["source"], paths.run_dir),
        "derived_datasets": {
            "construction_train": rel(split_paths["train"], paths.run_dir),
            "held_out_test": rel(split_paths["test"], paths.run_dir),
            "manifest": rel(split_paths["manifest"], paths.run_dir),
        },
        "split_rule": [
            "Use the source order in release_v6_all.json as the canonical pool order.",
            "Use random.Random(42).sample(range(total_instances), 200).",
            "Assign the first 50 sampled indices to construction and the next 150 sampled indices to held-out test.",
            "Write output instances in source-file order within each split to keep files auditable.",
            "Do not overwrite release_v6_all.json.",
        ],
        "deviation_classification": "paper_matching_inferred_split",
        "deviation_reason": (
            "The paper gives release_v6/test_release_v6, construction/test sizes, and seed 42, "
            "but does not publish exact LiveCodeBench instance IDs in the local artifacts."
        ),
        "manifest_summary": {
            "source_total_instances": manifest.get("source_total_instances") if manifest else None,
            "train_n": (manifest.get("train") or {}).get("n") if manifest else None,
            "test_n": (manifest.get("test") or {}).get("n") if manifest else None,
        },
        "human_gate": {
            "required_before_execution": True,
            "review_items": [
                "Confirm the inferred split rule is acceptable for reconstructed Table 1 execution.",
                "Confirm generated train/test instance IDs in the manifest.",
                "Confirm model-route and paid-API approval before executing the benchmark.",
            ],
        },
    }


def render_livecodebench_source_review_md(payload: dict[str, Any]) -> str:
    table = payload["paper_table3"]
    return f"""# LiveCodeBench Source Review

Status: `{payload['status']}`

## Source Identity

- Official source: `{payload['official_source']}`
- Official release: `{payload['official_release']}`
- Paper held-out split: `{payload['paper_held_out_split']}`
- Local dataset: `{payload['source_dataset']}`
- Dataset exists: `{payload['source_exists']}`
- Adapter: `{payload['adapter']}`
- Adapter exists: `{payload['adapter_exists']}`

## Local Dataset Shape

- Dataset ID: `{payload.get('dataset_id')}`
- Task name: `{payload.get('task_name')}`
- Task type: `{payload.get('task_type')}`
- Source total instances: `{payload.get('source_total_instances')}`

## Paper Table 3 Values

- Construction N: `{table['construction_n']}`
- Held-out test N: `{table['held_out_test_n']}`
- Seed: `{table['seed']}`
- Note: {table['note']}

## Identity Basis

{chr(10).join(f"- {item}" for item in payload['identity_basis'])}
"""


def render_livecodebench_split_contract_md(payload: dict[str, Any]) -> str:
    table = payload["paper_table3_contract"]
    outputs = payload["derived_datasets"]
    split_rule = "\n".join(f"- {item}" for item in payload["split_rule"])
    reviews = "\n".join(f"- {item}" for item in payload["human_gate"]["review_items"])
    return f"""# LiveCodeBench Split Contract

Status: `{payload['status']}`

## Paper Contract

- Benchmark: `{table['benchmark']}`
- Held-out split: `{table['held_out_test_split']}`
- Source release: `{table['source_release']}`
- Construction N: `{table['construction_n']}`
- Held-out test N: `{table['held_out_test_n']}`
- Seed: `{table['seed']}`

## Source And Outputs

- Source dataset: `{payload['source_dataset']}`
- Construction train: `{outputs['construction_train']}`
- Held-out test: `{outputs['held_out_test']}`
- Manifest: `{outputs['manifest']}`

## Split Rule

{split_rule}

## Deviation Classification

`{payload['deviation_classification']}`

{payload['deviation_reason']}

## Human Gate

{reviews}
"""


def render_livecodebench_deviation_note_md(payload: dict[str, Any]) -> str:
    return f"""# LiveCodeBench Deviation Note

Status: `{payload['status']}`

The LiveCodeBench adapter and release v6 source are available locally, but the exact paper instance IDs for the 50 construction and 150 held-out test examples are not published in the current run artifacts. The generated split is therefore a paper-matching inferred split: it follows the paper's release, sizes, and seed, while recording the reconstructed sampling rule and every selected instance ID.

This result may support a canonical-source reconstructed Table 1 verification. It should not be described as an exact original-paper split unless the authors' exact instance list is later recovered.
"""


def write_livecodebench_contract_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    source_review = build_livecodebench_source_review(run_dir)
    split_contract = build_livecodebench_split_contract(run_dir)
    deviation_note = {"status": split_contract["status"]}

    root_outputs = [
        (paths.artifacts_dir / "livecodebench_source_review.json", source_review),
        (paths.artifacts_dir / "livecodebench_split_contract.json", split_contract),
    ]
    for path, payload in root_outputs:
        write_json(path, payload)
    write_text(paths.artifacts_dir / "livecodebench_source_review.md", render_livecodebench_source_review_md(source_review))
    write_text(paths.artifacts_dir / "livecodebench_split_contract.md", render_livecodebench_split_contract_md(split_contract))
    write_text(paths.artifacts_dir / "livecodebench_deviation_note.md", render_livecodebench_deviation_note_md(deviation_note))

    categorized_outputs = [
        (paths.artifacts_dir / "03_code_and_sources" / "livecodebench_source_review.md", render_livecodebench_source_review_md(source_review)),
        (paths.artifacts_dir / "06_plans_and_contracts" / "livecodebench_split_contract.md", render_livecodebench_split_contract_md(split_contract)),
        (paths.artifacts_dir / "09_safety_and_deviations" / "livecodebench_deviation_note.md", render_livecodebench_deviation_note_md(deviation_note)),
    ]
    for path, text in categorized_outputs:
        if path.parent.exists():
            write_text(path, text)

    project_runs_dir = (Path.cwd() / "phase_0" / "runs").resolve()
    try:
        run_dir.resolve().relative_to(project_runs_dir)
        write_parallel_handoff = True
    except ValueError:
        write_parallel_handoff = False
    if write_parallel_handoff:
        parallel_dir = Path("logs") / "phase_0_parallel_20260604" / "B_livecodebench"
        write_text(parallel_dir / "livecodebench_source_review.md", render_livecodebench_source_review_md(source_review))
        write_text(parallel_dir / "livecodebench_split_contract.md", render_livecodebench_split_contract_md(split_contract))
        write_text(parallel_dir / "livecodebench_deviation_note.md", render_livecodebench_deviation_note_md(deviation_note))
    return split_contract


def livecodebench_split_dataset(
    source_path: Path,
    selected: list[tuple[int, dict[str, Any]]],
    *,
    envelope: dict[str, Any],
    split_name: str,
    split_n: int,
    total_instances: int,
) -> dict[str, Any]:
    instance_ids = [str(instance.get("instance_id")) for _, instance in selected]
    return {
        "dataset_id": f"{envelope['dataset_id']}_{split_name}_n{split_n}_seed{LIVECODEBENCH_SPLIT_SEED}",
        "task_name": envelope["task_name"],
        "task_type": envelope["task_type"],
        "instances": [instance for _, instance in selected],
        "metadata": {
            "benchmark": "livecodebench",
            "source_dataset_id": envelope["dataset_id"],
            "source_file": str(source_path),
            "source_release": LIVECODEBENCH_RELEASE,
            "paper_held_out_split": LIVECODEBENCH_HELD_OUT_SPLIT,
            "split_name": split_name,
            "split_n": split_n,
            "seed": LIVECODEBENCH_SPLIT_SEED,
            "source_total_instances": total_instances,
            "source_indices": [index for index, _ in selected],
            "instance_ids": instance_ids,
            "split_rule": "random.Random(42).sample(range(total), 200); first 50 construction, next 150 held-out test; output sorted by source order.",
            "deviation_classification": "paper_matching_inferred_split",
        },
    }


def prepare_livecodebench_split(run_dir: Path, force: bool = False) -> dict[str, Any]:
    paths = paths_for(run_dir)
    split_paths = livecodebench_split_paths(run_dir)
    source_path = split_paths["source"]
    train_path = split_paths["train"]
    test_path = split_paths["test"]
    manifest_path = split_paths["manifest"]
    outputs = [train_path, test_path, manifest_path]

    if not source_path.exists():
        manifest = {
            "schema_version": "0.1",
            "status": STATUS_BLOCKED,
            "reason": "missing_livecodebench_release_v6_all_json",
            "source": rel(source_path, paths.run_dir),
        }
        write_livecodebench_contract_artifacts(run_dir)
        return manifest

    existing = [path for path in outputs if path.exists()]
    if existing and len(existing) < len(outputs) and not force:
        manifest = {
            "schema_version": "0.1",
            "status": "blocked_existing_partial_split_outputs",
            "reason": "Refusing to overwrite partial LiveCodeBench split outputs without force.",
            "existing_outputs": [rel(path, paths.run_dir) for path in existing],
        }
        write_livecodebench_contract_artifacts(run_dir)
        return manifest
    if len(existing) == len(outputs) and not force:
        manifest = read_json(manifest_path)
        write_livecodebench_contract_artifacts(run_dir)
        return manifest

    envelope = dataset_envelope_from_prefix(source_path)
    total = count_dataset_instances_streaming(source_path)
    required = LIVECODEBENCH_CONSTRUCTION_N + LIVECODEBENCH_TEST_N
    if total < required:
        raise ValueError(f"LiveCodeBench source has {total} instances, but {required} are required.")

    sampled_indices = random.Random(LIVECODEBENCH_SPLIT_SEED).sample(range(total), required)
    train_indices = set(sampled_indices[:LIVECODEBENCH_CONSTRUCTION_N])
    test_indices = set(sampled_indices[LIVECODEBENCH_CONSTRUCTION_N:])
    train_selected: list[tuple[int, dict[str, Any]]] = []
    test_selected: list[tuple[int, dict[str, Any]]] = []
    for index, instance in enumerate(iter_dataset_instances(source_path)):
        if index in train_indices:
            train_selected.append((index, instance))
        elif index in test_indices:
            test_selected.append((index, instance))
        if len(train_selected) == LIVECODEBENCH_CONSTRUCTION_N and len(test_selected) == LIVECODEBENCH_TEST_N:
            break

    train_selected.sort(key=lambda item: item[0])
    test_selected.sort(key=lambda item: item[0])
    train_dataset = livecodebench_split_dataset(
        source_path,
        train_selected,
        envelope=envelope,
        split_name="construction",
        split_n=LIVECODEBENCH_CONSTRUCTION_N,
        total_instances=total,
    )
    test_dataset = livecodebench_split_dataset(
        source_path,
        test_selected,
        envelope=envelope,
        split_name="held_out_test",
        split_n=LIVECODEBENCH_TEST_N,
        total_instances=total,
    )

    write_json(train_path, train_dataset)
    write_json(test_path, test_dataset)
    manifest = {
        "schema_version": "0.1",
        "status": STATUS_READY_FOR_EXECUTION,
        "source": rel(source_path, paths.run_dir),
        "source_total_instances": total,
        "paper_table3": {
            "benchmark": "LiveCodeBench",
            "held_out_test_split": LIVECODEBENCH_HELD_OUT_SPLIT,
            "construction_n": LIVECODEBENCH_CONSTRUCTION_N,
            "held_out_test_n": LIVECODEBENCH_TEST_N,
            "source_release": LIVECODEBENCH_RELEASE,
            "seed": LIVECODEBENCH_SPLIT_SEED,
        },
        "split_rule": "random.Random(42).sample(range(total), 200); first 50 construction, next 150 held-out test; output sorted by source order.",
        "rng_sample_order_source_indices": sampled_indices,
        "train": {
            "path": rel(train_path, paths.run_dir),
            "n": len(train_selected),
            "source_indices": [index for index, _ in train_selected],
            "instance_ids": train_dataset["metadata"]["instance_ids"],
        },
        "test": {
            "path": rel(test_path, paths.run_dir),
            "n": len(test_selected),
            "source_indices": [index for index, _ in test_selected],
            "instance_ids": test_dataset["metadata"]["instance_ids"],
        },
        "deviation_classification": "paper_matching_inferred_split",
        "deviation_reason": (
            "The paper publishes release, sizes, and seed but not exact LiveCodeBench instance IDs. "
            "This manifest records the inferred deterministic split for audit."
        ),
    }
    write_json(manifest_path, manifest)
    write_livecodebench_contract_artifacts(run_dir)
    append_event(run_dir, "livecodebench_split_preparation", STATUS_READY_FOR_EXECUTION, artifact=rel(manifest_path, paths.run_dir))
    return manifest


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
            "schema_version": "0.2",
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
            LONG_INFERENCE_APPROVED_FIELD: False,
            "dependency_scope_required": "inside_project_directory",
            "max_cost_usd": 5.0,
            "approved_by": "human",
            "notes": (
                "Approve only after reviewing command_plan.json. Keep "
                "long_inference_approved false for the minimal necessary artifact set; "
                "set it true to generate the full long-planning artifact set."
            ),
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
            "id": "skillgen_baseline_generator_source_catalog",
            "description": "The automation records public baseline generator source candidates for Trace2Skill, SkillX, EvoSkill, and CoEvoSkills.",
            "reason": "Group D needs a source identity review path before the Figure 2 baseline comparison can move beyond not_testable.",
            "impact": "These candidates are not treated as exact SkillGen author runners until commit, license, identity, and single-skill adaptation are human-reviewed.",
        },
        {
            "id": "skillgen_reconstructed_ablation_arms",
            "description": "The automation records reconstructed Figure 3 A1-A5 ablation arms from the paper description rather than from author-provided named configs.",
            "reason": "The official checkout does not include a Figure 3 ablation runner or A1-A5 config package, but the validation workflow needs a human-reviewable execution path.",
            "impact": "The resulting ablation matrix is deviation-backed reconstructed verification unless original author configs are later found and substituted.",
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
        STATUS_READY_FOR_RECONSTRUCTED_EXECUTION: ("#dcfce7", "#166534", "#86efac"),
        STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION: ("#ecfdf5", "#065f46", "#6ee7b7"),
        STATUS_BLOCKED_PENDING_RECONSTRUCTED_ABLATION_CONTRACT: ("#dbeafe", "#1e40af", "#60a5fa"),
        STATUS_BLOCKED_PENDING_BASELINE_SOURCE_IDENTITY_REVIEW: ("#dbeafe", "#1e40af", "#60a5fa"),
        STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON: ("#dcfce7", "#166534", "#86efac"),
        STATUS_PARTIALLY_READY_FULL_MATRIX: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_READY_FOR_FULL_MATRIX_EXECUTION_AFTER_DEPENDENCIES: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_READY_FOR_RECONSTRUCTED_ALFWORLD_IMPLEMENTATION: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_READY_FOR_SOURCE_IDENTITY_REVIEW: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_READY_FOR_RECONSTRUCTED_ABLATION_HUMAN_REVIEW: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_BLOCKED_BY_ALFWORLD_OOD_EXECUTION: ("#dbeafe", "#1e40af", "#60a5fa"),
        STATUS_READY_FOR_TRACE_GENERATION_AFTER_FULL_RUNS: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_READY_FOR_FULL_TOKEN_COST_EXECUTION: ("#fef9c3", "#854d0e", "#fde047"),
        STATUS_READY_FOR_FULL_SCOPE_ARTIFACT_CHECK: ("#fef9c3", "#854d0e", "#fde047"),
    }
    background, text, border = palette.get(value, ("#f3f4f6", "#111827", "#d1d5db"))
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:4px;'
        f'background:{background};color:{text};border:1px solid {border};'
        f'font-weight:600">{value}</span>'
    )


def read_json_from_candidates(paths: list[Path]) -> dict[str, Any]:
    for path in paths:
        if path.exists():
            return read_json(path)
    return {}


def official_support_snapshot(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    intake_status_paths = [
        paths.artifacts_dir / "external_source_intake_status.json",
        paths.artifacts_dir / "03_code_and_sources" / "external_source_intake_status.json",
    ]
    benchmark_execution_plan_paths = [
        paths.artifacts_dir / "benchmark_execution_plan.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "benchmark_execution_plan.json",
    ]
    model_route_mapping_paths = [
        paths.artifacts_dir / "model_route_mapping.template.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "model_route_mapping.template.json",
    ]
    transfer_runner_plan_paths = [
        paths.artifacts_dir / "transfer_runner_plan.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "transfer_runner_plan.json",
    ]
    token_log_plan_paths = [
        paths.artifacts_dir / "token_log_plan.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "token_log_plan.json",
    ]
    canonical_source_status_paths = [
        paths.artifacts_dir / "canonical_benchmark_source_status.json",
        paths.artifacts_dir / "03_code_and_sources" / "canonical_benchmark_source_status.json",
    ]
    baseline_source_identity_review_paths = [
        paths.artifacts_dir / "baseline_source_identity_review.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "baseline_source_identity_review.json",
    ]
    baseline_adapter_contract_paths = [
        paths.artifacts_dir / "baseline_single_skill_adapter_contract.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "baseline_single_skill_adapter_contract.json",
    ]
    reconstructed_ablation_contract_paths = [
        paths.artifacts_dir / "reconstructed_ablation_contract.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "reconstructed_ablation_contract.json",
    ]
    ablation_config_matrix_paths = [
        paths.artifacts_dir / "ablation_config_matrix.json",
        paths.artifacts_dir / "06_plans_and_contracts" / "ablation_config_matrix.json",
    ]
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
        "external_source_intake_status": read_json_from_candidates(intake_status_paths),
        "benchmark_execution_plan": read_json_from_candidates(benchmark_execution_plan_paths),
        "model_route_mapping": read_json_from_candidates(model_route_mapping_paths),
        "transfer_runner_plan": read_json_from_candidates(transfer_runner_plan_paths),
        "token_log_plan": read_json_from_candidates(token_log_plan_paths),
        "canonical_benchmark_source_status": read_json_from_candidates(canonical_source_status_paths),
        "baseline_source_identity_review": read_json_from_candidates(baseline_source_identity_review_paths),
        "baseline_single_skill_adapter_contract": read_json_from_candidates(baseline_adapter_contract_paths),
        "reconstructed_ablation_contract": read_json_from_candidates(reconstructed_ablation_contract_paths),
        "ablation_config_matrix": read_json_from_candidates(ablation_config_matrix_paths),
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
            reconstructed_rows = [
                row for row in canonical_only_rows
                if (execution_targets.get(row) or {}).get("status") == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
            ]
            missing_contract_rows = [row for row in canonical_only_rows if row not in reconstructed_rows]
            if reconstructed_rows:
                evidence.append(
                    "Group A ALFWorld source/adapter/split/deviation contracts exist for reconstructed execution rows: "
                    + ", ".join(reconstructed_rows)
                    + "."
                )
                blockers.append(
                    "ALFWorld reconstructed rows still require canonical data download, adapter implementation, generated train/test JSON, smoke logs, and human approval before Table 1 execution."
                )
            if missing_contract_rows:
                evidence.append(
                    "Canonical ALFWorld code has been fetched, but these rows still need a SkillGen-compatible adapter and IOD/OOD split contract: "
                    + ", ".join(missing_contract_rows)
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
                execution_plan = support.get("benchmark_execution_plan") or {}
                target_statuses = {
                    target.get("target_id"): target.get("status")
                    for target in execution_plan.get("targets", [])
                }
                if (
                    target_statuses.get("alfworld_iod") == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
                    and target_statuses.get("alfworld_ood") == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
                ):
                    evidence.append("Group A ALFWorld reconstructed-execution contracts are present for IOD and OOD.")
                    blockers.append("ALFWorld IOD/OOD still need canonical data download, adapter implementation, generated split files, smoke logs, and human approval before result comparison.")
                else:
                    blockers.append("ALFWorld IOD/OOD data is not bundled and no SkillGen-compatible ALFWorld adapter/split contract exists yet.")
            else:
                blockers.append("ALFWorld IOD/OOD data is not bundled in code/official/data.")
        if data_support.get("scienceworld", {}).get("available"):
            evidence.append("ScienceWorld train/test JSON is bundled and can be planned for execution.")
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_baseline_generator_comparison":
        identity_review = support.get("baseline_source_identity_review") or {}
        adapter_contract = support.get("baseline_single_skill_adapter_contract") or {}
        if identity_review:
            method_names = [row.get("method_name") for row in identity_review.get("baselines", [])]
            evidence.append(
                "Group D baseline source identity review exists for: "
                + ", ".join(name for name in method_names if name)
                + "."
            )
            evidence.append(
                "Single-Markdown-skill adapter contract status is "
                f"{adapter_contract.get('status', 'missing')}."
            )
            if (
                identity_review.get("status") == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
                and adapter_contract.get("status") == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
            ):
                evidence.append("All public baseline sources are pinned and human-approved for reconstructed comparison.")
                blockers.append("Reconstructed Figure 2 baseline comparison has not been executed yet.")
                return STATUS_BLOCKED, blockers, evidence
            pending = [
                row.get("method_name", row.get("source_key", "unknown"))
                for row in identity_review.get("baselines", [])
                if row.get("status") != "source_intake_complete_pending_human_identity_review"
            ]
            blockers.append("Official SkillGen checkout still does not include executable Figure 2 baseline runners.")
            blockers.append("Baseline source identity review is not complete or not human-approved.")
            if pending:
                blockers.append("Baseline repositories still needing source intake or commit/license review: " + ", ".join(pending) + ".")
            blockers.append("Reconstructed comparison must use the single-Markdown-skill adapter contract before execution.")
            return STATUS_BLOCKED, blockers, evidence
        blockers.extend(
            [
                "Official checkout does not include Trace2Skill, SkillX, EvoSkill, or CoEvoSkills runner implementations.",
                "README describes baseline adaptation details in the paper, but no executable baseline-comparison command is present.",
                "Generate the Group D baseline source identity review before deciding whether public-code reconstruction is possible.",
            ]
        )
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_ablation_full_wins":
        ablation_contract = support.get("reconstructed_ablation_contract") or {}
        config_matrix = support.get("ablation_config_matrix") or {}
        if ablation_contract:
            arm_ids = [arm.get("arm_id") for arm in ablation_contract.get("arms", []) if arm.get("arm_id")]
            evidence.append(
                "Group E reconstructed ablation contract exists with arms: "
                + ", ".join(arm_ids)
                + "."
            )
            evidence.append(
                "Config matrix status is "
                f"{config_matrix.get('status', 'missing')}; reproduction class is "
                f"{ablation_contract.get('reproduction_class', 'unknown')}."
            )
            evidence.append(
                "Original author Figure 3 runner/configs are still absent, so this can only support reconstructed ablation evidence unless those artifacts are later found."
            )
            if ablation_contract.get("status") == STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION:
                blockers.append("Reconstructed ablation smoke execution has not been run or parsed yet.")
                return STATUS_BLOCKED, blockers, evidence
            blockers.append("Group E reconstructed ablation contract exists but is not marked ready for execution.")
            return STATUS_BLOCKED, blockers, evidence
        blockers.extend(
            [
                "Official checkout does not include an ablation runner or named ablated configs.",
                "Generate the Group E reconstructed ablation contract before executing deviation-backed Figure 3 verification.",
            ]
        )
        return STATUS_BLOCKED, blockers, evidence

    if claim_id == "claim_cross_model_transfer":
        transfer_plan = support.get("transfer_runner_plan") or {}
        if transfer_plan:
            ready_rows = [
                row["benchmark_row"]
                for row in transfer_plan.get("benchmarks", [])
                if row.get("dataset_status") == STATUS_READY_FOR_EXECUTION
            ]
            reconstructed_rows = [
                row["benchmark_row"]
                for row in transfer_plan.get("benchmarks", [])
                if row.get("dataset_status") == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
            ]
            if ready_rows:
                evidence.append("Transfer runner plan has ready datasets for: " + ", ".join(ready_rows) + ".")
            if reconstructed_rows:
                evidence.append("Transfer runner plan has reconstructed-execution contracts for: " + ", ".join(reconstructed_rows) + ".")
            evidence.append(
                "Transfer runner plan encodes "
                f"{transfer_plan.get('planned_off_diagonal_comparisons', 'unknown')} off-diagonal comparisons before execution."
            )
        alfworld_ood_status = None
        for row in transfer_plan.get("benchmarks", []):
            if row.get("benchmark_row") == "alfworld_ood":
                alfworld_ood_status = row.get("dataset_status")
        blockers.extend(
            [
                (
                    "Full 120-comparison transfer claim still requires executing the ALFWorld OOD reconstructed contract, including data download, adapter implementation, generated split files, and retained per-round traces."
                    if alfworld_ood_status == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
                    else "Full 120-comparison transfer claim still requires the ALFWorld OOD SkillGen adapter/split contract."
                ),
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
            blockers.append("Prepared tau-Bench target has not been executed and compared for this claim.")
            return STATUS_BLOCKED, blockers, evidence
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
            blockers.append("Prepared ChemLLMBench targets have not been executed and compared for this claim.")
            return STATUS_BLOCKED, blockers, evidence
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
        blockers.append("Table 4 token-log collection has not been executed for the paper-scale grouped totals.")
        return STATUS_BLOCKED, blockers, evidence

    blockers.append("No verification rule has been implemented for this claim.")
    return STATUS_NOT_TESTABLE, blockers, evidence


def claim_execution_readiness_status(
    claim_id: str,
    support: dict[str, Any],
    benchmark: dict[str, Any],
) -> str:
    execution_plan = support.get("benchmark_execution_plan") or {}
    execution_targets = {
        target.get("target_id"): target
        for target in execution_plan.get("targets", [])
        if target.get("target_id")
    }
    table1_target_rows = {
        target.get("table1_row"): target
        for target in execution_plan.get("targets", [])
        if target.get("table1_row")
    }

    if claim_id == "claim_method_paired_intervention":
        if benchmark.get("status") == "official_code_smoke_completed":
            return STATUS_READY_FOR_FULL_MATRIX_EXECUTION_AFTER_DEPENDENCIES
        return "blocked_missing_paired_smoke_output"

    if claim_id in {"claim_table1_average_gains_all_models", "claim_table1_entry_counts"}:
        row_statuses = [
            (table1_target_rows.get(row) or {}).get("status", "missing_execution_plan")
            for row in TABLE1_REQUIRED_ROWS
        ]
        if all(status == STATUS_READY_FOR_EXECUTION for status in row_statuses):
            return STATUS_READY_FOR_EXECUTION
        if any(status in {STATUS_READY_FOR_EXECUTION, STATUS_READY_FOR_RECONSTRUCTED_EXECUTION} for status in row_statuses):
            return STATUS_PARTIALLY_READY_FULL_MATRIX
        return "blocked_missing_table1_execution_contract"

    if claim_id == "claim_table1_alfworld_scienceworld_patterns":
        alfworld_iod = (execution_targets.get("alfworld_iod") or {}).get("status")
        alfworld_ood = (execution_targets.get("alfworld_ood") or {}).get("status")
        if alfworld_iod == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION and alfworld_ood == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION:
            return STATUS_READY_FOR_RECONSTRUCTED_ALFWORLD_IMPLEMENTATION
        return "blocked_missing_alfworld_adapter_or_split_contract"

    if claim_id == "claim_baseline_generator_comparison":
        identity_review = support.get("baseline_source_identity_review") or {}
        adapter_contract = support.get("baseline_single_skill_adapter_contract") or {}
        if (
            identity_review.get("status") == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
            and adapter_contract.get("status") == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
        ):
            return STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
        if identity_review or adapter_contract:
            return STATUS_READY_FOR_SOURCE_IDENTITY_REVIEW
        return STATUS_BLOCKED_PENDING_BASELINE_SOURCE_IDENTITY_REVIEW

    if claim_id == "claim_ablation_full_wins":
        ablation_contract = support.get("reconstructed_ablation_contract") or {}
        if ablation_contract.get("status") == STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION:
            return STATUS_READY_FOR_RECONSTRUCTED_ABLATION_HUMAN_REVIEW
        if ablation_contract:
            return STATUS_BLOCKED_PENDING_RECONSTRUCTED_ABLATION_CONTRACT
        return STATUS_BLOCKED_PENDING_RECONSTRUCTED_ABLATION_CONTRACT

    if claim_id == "claim_cross_model_transfer":
        transfer_plan = support.get("transfer_runner_plan") or {}
        for row in transfer_plan.get("benchmarks", []):
            if row.get("benchmark_row") == "alfworld_ood" and row.get("dataset_status") == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION:
                return STATUS_BLOCKED_BY_ALFWORLD_OOD_EXECUTION
        if transfer_plan:
            return "blocked_missing_alfworld_ood_reconstructed_contract"
        return "blocked_missing_transfer_runner_plan"

    if claim_id == "claim_tau_bench_gate_activated":
        if (benchmark.get("additional_targets") or {}).get("tau_bench_retail") or external_source_is_prepared(support, "tau_bench"):
            return STATUS_READY_FOR_EXECUTION
        if supported_external_candidates(support, ["tau_bench"]):
            return "blocked_pending_tau_bench_source_intake"
        return "blocked_missing_tau_bench_source"

    if claim_id == "claim_chemllmbench_useful_gains":
        additional = benchmark.get("additional_targets") or {}
        if (
            additional.get("chemllmbench_property_prediction")
            or additional.get("chemllmbench_yield_prediction")
            or external_source_is_prepared(support, "chemllmbench")
        ):
            return STATUS_READY_FOR_EXECUTION
        if supported_external_candidates(support, ["chemllmbench"]):
            return "blocked_pending_chemllmbench_source_intake"
        return "blocked_missing_chemllmbench_source"

    if claim_id == "claim_refinement_best_of_k":
        return STATUS_READY_FOR_TRACE_GENERATION_AFTER_FULL_RUNS

    if claim_id == "claim_token_cost":
        if support.get("token_log_plan") or (benchmark.get("train") or {}).get("token_usage_total") or (benchmark.get("eval") or {}).get("token_usage_total"):
            return STATUS_READY_FOR_FULL_TOKEN_COST_EXECUTION
        return "blocked_missing_token_log_plan"

    if claim_id == "claim_auditable_skill_artifact":
        if (benchmark.get("train") or {}).get("skill_output"):
            return STATUS_READY_FOR_FULL_SCOPE_ARTIFACT_CHECK
        return "blocked_missing_skill_artifact_run"

    return "readiness_unknown"


def split_claim_evidence(
    claim_id: str,
    claim_verdict_status: str,
    evidence: list[str],
) -> tuple[list[str], list[str]]:
    if claim_verdict_status not in {STATUS_REPRODUCED, STATUS_PARTIALLY_REPRODUCED, STATUS_NOT_REPRODUCED}:
        return [], evidence

    if claim_id in {
        "claim_method_paired_intervention",
        "claim_tau_bench_gate_activated",
        "claim_chemllmbench_useful_gains",
        "claim_auditable_skill_artifact",
    }:
        return evidence, []

    if claim_id == "claim_token_cost":
        validation_markers = (
            "token evidence",
            "Existing smoke token evidence",
            "All Table 4 ready token groups were executed",
        )
        validation = [item for item in evidence if any(marker in item for marker in validation_markers)]
        planning = [item for item in evidence if item not in validation]
        return validation, planning

    return evidence, []


def next_step_for_claim(
    status: str,
    verification_mode: str,
    has_external_candidates: bool = False,
    claim_id: str | None = None,
    support: dict[str, Any] | None = None,
    readiness_status: str | None = None,
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
    if claim_id == "claim_baseline_generator_comparison":
        if readiness_status == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON:
            return "Execute baseline_single_skill_adapter_contract.json with the shared paired rollout harness, then aggregate Figure 2 deltas."
        if readiness_status == STATUS_READY_FOR_SOURCE_IDENTITY_REVIEW:
            identity_review = support.get("baseline_source_identity_review") or {}
            rows = identity_review.get("baselines", [])
            if rows and all(row.get("target_exists") and row.get("commit") for row in rows):
                missing_license = [row.get("method_name") for row in rows if not row.get("local_license_files")]
                prefix = (
                    "Confirm missing local license evidence for " + ", ".join(name for name in missing_license if name) + ", "
                    if missing_license
                    else ""
                )
                return (
                    prefix
                    + "write/approve baseline_source_identity_human_review.json, then approve reconstructed baseline adapter execution."
                )
            return (
                "Clone/pin the four public baseline repositories inside code/official/baselines, "
                "record commits and licenses, write the human identity review artifact, then approve reconstructed comparison execution."
            )
    if claim_id == "claim_ablation_full_wins":
        if readiness_status == STATUS_READY_FOR_RECONSTRUCTED_ABLATION_HUMAN_REVIEW:
            return (
                "Human-review reconstructed_ablation_contract.json, ablation_config_matrix.json, "
                "and ablation_deviation_note.md, then execute ablation_smoke_plan.json before any paper-target Figure 3 matrix."
            )
        if readiness_status == STATUS_BLOCKED_PENDING_RECONSTRUCTED_ABLATION_CONTRACT:
            return "Finish the Group E reconstructed ablation contract and config matrix, then request human approval for smoke execution."
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
        transfer_plan = support.get("transfer_runner_plan") or {}
        alfworld_ood_status = None
        for row in transfer_plan.get("benchmarks", []):
            if row.get("benchmark_row") == "alfworld_ood":
                alfworld_ood_status = row.get("dataset_status")
                break
        if alfworld_ood_status == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION:
            return (
                "Execute the approved ALFWorld OOD reconstructed contract first "
                "(data download, adapter implementation, split JSONs, trace retention), "
                "then run transfer_runner_plan.json."
            )
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


def count_statuses(rows: list[dict[str, Any]], field: str = "status") -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get(field, "unknown")
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
        "This matrix separates paper-claim verdict status from next-step execution readiness.",
        "",
        "## Claim Verdict Status Counts",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Execution Readiness Status Counts", ""])
    for status, count in sorted(payload.get("readiness_status_counts", {}).items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Claims", ""])
    for row in payload["claims"]:
        external_candidates = row.get("external_source_candidates") or []
        verdict_status = row.get("claim_verdict_status", row.get("status"))
        readiness_status = row.get("execution_readiness_status", "unknown")
        validation_evidence = row.get("validation_evidence", row.get("evidence", []))
        planning_evidence = row.get("planning_evidence", [])
        lines.extend(
            [
                f"### {row['claim_id']}",
                "",
                f"- Claim verdict status: `{verdict_status}`",
                f"- Execution readiness status: `{readiness_status}`",
                f"- Verification mode: `{row['verification_mode']}`",
                f"- Next step: {row['next_step']}",
            ]
        )
        if validation_evidence:
            lines.append("- Validation evidence: " + " ".join(validation_evidence))
        if planning_evidence:
            lines.append("- Planning/readiness evidence: " + " ".join(planning_evidence))
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
        "livecodebench": [
            f"code/official/{LIVECODEBENCH_TRAIN_REL}",
            f"code/official/{LIVECODEBENCH_TEST_REL}",
            f"code/official/{LIVECODEBENCH_SPLIT_MANIFEST_REL}",
        ],
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
        "livecodebench": [
            f"code/official/{LIVECODEBENCH_SOURCE_REL}",
            f"code/official/{LIVECODEBENCH_TRAIN_REL}",
            f"code/official/{LIVECODEBENCH_TEST_REL}",
            f"code/official/{LIVECODEBENCH_SPLIT_MANIFEST_REL}",
        ],
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
        if all(
            output in partial_outputs
            for output in [
                f"code/official/{LIVECODEBENCH_TRAIN_REL}",
                f"code/official/{LIVECODEBENCH_TEST_REL}",
                f"code/official/{LIVECODEBENCH_SPLIT_MANIFEST_REL}",
            ]
        ):
            return []
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


def local_license_files(target_path: Path, run_dir: Path) -> list[str]:
    names = {"LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md"}
    if not target_path.exists():
        return []
    top_level = [
        rel(path, run_dir)
        for path in sorted(target_path.iterdir())
        if path.is_file() and path.name in names
    ]
    if top_level:
        return top_level
    return [
        rel(path, run_dir)
        for path in sorted(target_path.rglob("*"))
        if path.is_file() and path.name in names
    ]


def license_evidence_scope(target_path: Path, license_files: list[str], run_dir: Path) -> str:
    if not license_files:
        return "missing"
    top_level_names = {"LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md"}
    top_level_files = {
        rel(path, run_dir)
        for path in sorted(target_path.iterdir())
        if path.is_file() and path.name in top_level_names
    }
    if any(path in top_level_files for path in license_files):
        return "top_level"
    return "nested_only"


def baseline_human_review_decisions(human_review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row.get("method_name"): row
        for row in human_review.get("baselines", [])
        if row.get("method_name")
    }


def build_baseline_source_identity_review(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    human_review_path = paths.artifacts_dir / "baseline_source_identity_human_review.json"
    human_review = read_json(human_review_path) if human_review_path.exists() else {}
    human_approved = bool(human_review.get("baseline_source_identity_review_approved"))
    human_decisions = baseline_human_review_decisions(human_review)
    license_exception_approved = bool(human_review.get("license_exception_approved", False))
    adapter_deviation_approved = bool(human_review.get("adapter_deviation_approved", False))
    rows = []
    for spec in BASELINE_GENERATOR_SOURCES:
        target_path = paths.run_dir / spec["target_path"]
        target_exists = target_path.exists()
        commit = git_value(["rev-parse", "HEAD"], target_path) if target_exists and (target_path / ".git").exists() else None
        license_files = local_license_files(target_path, paths.run_dir)
        license_scope = license_evidence_scope(target_path, license_files, paths.run_dir) if target_exists else "missing"
        human_decision = human_decisions.get(spec["method_name"], {})
        identity_approved = human_approved and human_decision.get("review_decision") == "approved"
        license_approved = bool(human_decision.get("license_evidence_approved", False))
        if not target_exists:
            status = "pending_source_intake"
        elif not commit:
            status = "source_present_commit_unknown"
        elif identity_approved and license_files and (license_scope == "top_level" or license_approved or license_exception_approved):
            status = "source_identity_human_approved"
        else:
            status = "source_intake_complete_pending_human_identity_review"
        blockers = []
        if not target_exists:
            blockers.append(f"Clone `{spec['source_url']}` into `{spec['target_path']}` inside the run directory.")
        if target_exists and not commit:
            blockers.append("Record an immutable commit hash from the local Git checkout.")
        if not license_files:
            blockers.append(f"Confirm the local license file and expected SPDX id `{spec['expected_license_spdx']}`.")
        elif license_scope != "top_level" and not (license_approved or license_exception_approved):
            blockers.append("Human must confirm nested-only local license evidence is acceptable for this baseline.")
        if not identity_approved:
            blockers.append("Human must confirm this repository is the correct implementation identity for the SkillGen Appendix C.6 baseline.")
        rows.append(
            {
                "source_key": spec["source_key"],
                "method_name": spec["method_name"],
                "repository": spec["repository"],
                "source_url": spec["source_url"],
                "target_path": spec["target_path"],
                "target_exists": target_exists,
                "commit": commit,
                "expected_license_spdx": spec["expected_license_spdx"],
                "local_license_files": license_files,
                "license_evidence_scope": license_scope,
                "human_review_decision": human_decision.get("review_decision", "pending"),
                "license_evidence_approved": license_approved or (license_scope == "top_level" and identity_approved),
                "paper_identity_basis": spec["paper_identity_basis"],
                "native_output": spec["native_output"],
                "status": status,
                "remaining_blockers": blockers,
            }
        )

    all_sources_pinned = all(
        row["target_exists"]
        and row.get("commit")
        and row.get("local_license_files")
        and row.get("human_review_decision") == "approved"
        and (row.get("license_evidence_scope") == "top_level" or row.get("license_evidence_approved") or license_exception_approved)
        for row in rows
    )
    overall_status = (
        STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
        if human_approved and all_sources_pinned and adapter_deviation_approved
        else STATUS_BLOCKED_PENDING_BASELINE_SOURCE_IDENTITY_REVIEW
    )
    return {
        "schema_version": "0.1",
        "scope": "Group D baseline source identity review for SkillGen Figure 2 reconstruction",
        "run_dir": paths.run_dir.name,
        "status": overall_status,
        "storage_rule": "All baseline repositories must be cloned under code/official/baselines inside this run directory before execution.",
        "human_review_artifact": "artifacts/baseline_source_identity_human_review.json",
        "human_review_approved": human_approved,
        "license_exception_approved": license_exception_approved,
        "adapter_deviation_approved": adapter_deviation_approved,
        "source_count": len(rows),
        "status_counts": count_statuses(rows),
        "baselines": rows,
        "ready_conditions": [
            "All four repositories exist under code/official/baselines.",
            "Each repository has an immutable commit recorded in this artifact.",
            "Each repository license is present locally and reviewed.",
            "A human review artifact approves the repository identity for reconstructed comparison use.",
        ],
    }


def render_baseline_source_identity_review_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Baseline Source Identity Review",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Storage rule: {payload['storage_rule']}",
        f"Human review approved: `{payload['human_review_approved']}`",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(
        [
            "",
            "## Baseline Repositories",
            "",
            "| Baseline | Repository | Status | Target | Commit | License | License evidence | Human decision | Main blockers |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["baselines"]:
        blockers = "; ".join(row.get("remaining_blockers") or [])
        lines.append(
            f"| `{row['method_name']}` | `{row['repository']}` | `{row['status']}` | "
            f"`{row['target_path']}` | `{row.get('commit') or ''}` | "
            f"`{row['expected_license_spdx']}` | `{row.get('license_evidence_scope', 'unknown')}` | "
            f"`{row.get('human_review_decision', 'pending')}` | {table_cell(blockers)} |"
        )
    lines.extend(["", "## Ready Conditions", ""])
    lines.extend(f"- {item}" for item in payload["ready_conditions"])
    return "\n".join(lines).rstrip() + "\n"


def build_baseline_single_skill_adapter_contract(
    run_dir: Path,
    identity_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    identity_review = identity_review or build_baseline_source_identity_review(run_dir)
    adapters = []
    for spec in BASELINE_GENERATOR_SOURCES:
        adapters.append(
            {
                "source_key": spec["source_key"],
                "method_name": spec["method_name"],
                "native_output": spec["native_output"],
                "single_skill_adapter_strategy": spec["single_skill_adapter_strategy"],
                "adapter_status": (
                    "adapter_contract_defined"
                    if identity_review["status"] == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
                    else "adapter_contract_defined_pending_source_identity_review"
                ),
                "expected_outputs": [
                    f"artifacts/baseline_comparison/{spec['source_key']}/skill.md",
                    f"artifacts/baseline_comparison/{spec['source_key']}/adapter_metadata.json",
                    f"artifacts/baseline_comparison/{spec['source_key']}/construction_stdout.txt",
                    f"artifacts/baseline_comparison/{spec['source_key']}/construction_stderr.txt",
                ],
            }
        )
    status = (
        STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
        if identity_review["status"] == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
        else STATUS_BLOCKED_PENDING_BASELINE_SOURCE_IDENTITY_REVIEW
    )
    return {
        "schema_version": "0.1",
        "scope": "Single-Markdown-skill adapter contract for reconstructed baseline generator comparison",
        "run_dir": paths.run_dir.name,
        "status": status,
        "input_contract": [
            "Use the same SkillGen construction split, base model, seed, and saved baseline trajectories as the SkillGen run being compared.",
            "Provide each baseline with only construction-split information available to SkillGen before held-out evaluation.",
            "Record all baseline construction stdout, stderr, prompts/configs, and generated intermediate artifacts inside the run directory.",
        ],
        "output_contract": [
            "Each baseline adapter must output exactly one Markdown skill used as the with-skill intervention.",
            "The Markdown skill must have a stable artifact path and adapter_metadata.json describing source commit, input split, model, seed, and dropped capabilities.",
            "Held-out evaluation must use the same SkillGen paired rollout harness and compare BASE vs with-baseline-skill on the same instances.",
        ],
        "forbidden_capabilities": [
            "No executable helper scripts in the final skill.",
            "No reference bundles or retrieval documents.",
            "No multi-skill library routing.",
            "No test-time skill selection.",
            "No benchmark-specific held-out labels during construction.",
        ],
        "paired_rollout_harness": [
            "Use the same test split, evaluator model route, judge route, max workers, and random seed as the corresponding SkillGen evaluation.",
            "Parse outputs into baseline_acc, baseline_skill_acc, delta_acc, repair, regression, and net_gain fields.",
            "Aggregate deltas with the same rule as Figure 2: average improvement per compared benchmark-model setting.",
        ],
        "adapters": adapters,
        "remaining_blockers": [
            "Baseline repository identities and commits are not fully human-reviewed.",
            "No reconstructed baseline construction/evaluation commands have been approved or executed.",
        ]
        if status != STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON
        else [],
    }


def render_baseline_single_skill_adapter_contract_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Baseline Single-Skill Adapter Contract",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Input Contract",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["input_contract"])
    lines.extend(["", "## Output Contract", ""])
    lines.extend(f"- {item}" for item in payload["output_contract"])
    lines.extend(["", "## Forbidden Capabilities", ""])
    lines.extend(f"- {item}" for item in payload["forbidden_capabilities"])
    lines.extend(["", "## Adapters", ""])
    for adapter in payload["adapters"]:
        lines.extend(
            [
                f"### {adapter['method_name']}",
                "",
                f"- Status: `{adapter['adapter_status']}`",
                f"- Native output: {adapter['native_output']}",
                f"- Adapter strategy: {adapter['single_skill_adapter_strategy']}",
                "- Expected outputs:",
            ]
        )
        lines.extend(f"  - `{path}`" for path in adapter["expected_outputs"])
        lines.append("")
    if payload.get("remaining_blockers"):
        lines.extend(["## Remaining Blockers", ""])
        lines.extend(f"- {item}" for item in payload["remaining_blockers"])
    return "\n".join(lines).rstrip() + "\n"


def render_baseline_deviation_note_md(
    identity_review: dict[str, Any],
    adapter_contract: dict[str, Any],
) -> str:
    license_notes: list[str] = []
    if identity_review.get("license_exception_approved"):
        nested_only = [
            row["method_name"]
            for row in identity_review.get("baselines", [])
            if row.get("license_evidence_scope") == "nested_only"
        ]
        if nested_only:
            license_notes.append(
                "Human review approved a license-evidence exception for nested-only local license files: "
                + ", ".join(nested_only)
                + "."
            )
    license_note_lines = ["- " + item for item in license_notes] or ["- No license-evidence exception is recorded."]
    return "\n".join(
        [
            "# Baseline Deviation Note",
            "",
            "Status: `" + adapter_contract["status"] + "`",
            "",
            "This comparison is a public-code reconstructed verification path, not an exact SkillGen Figure 2 reproduction yet.",
            "",
            "## Required Disclosure",
            "",
            "- Source: public baseline repositories named in the Group D source identity review.",
            "- Adaptation: each baseline is constrained to emit one Markdown skill and then uses the SkillGen paired rollout harness.",
            "- Deviation: the SkillGen official checkout does not include the authors' executable Figure 2 baseline runners.",
            "- Limitation: even after repository identity, commit, license evidence, and adapter deviation are human-reviewed, the claim remains blocked rather than reproduced until reconstructed baseline execution produces parsed comparison results.",
            "",
            "## License Evidence Notes",
            "",
            *license_note_lines,
            "",
            "## Status Transition",
            "",
            f"- Current source identity status: `{identity_review['status']}`",
            f"- Current adapter contract status: `{adapter_contract['status']}`",
            "- If the reconstructed comparison supports SkillGen's largest average improvement, mark the claim `partially_reproduced` unless the exact author runner is later identified.",
            "- If it contradicts the paper result, mark the claim `not_reproduced` with raw logs preserved.",
            "- If any baseline cannot run after approved setup, mark the affected comparison `failed_to_run` and keep the aggregate clearly incomplete.",
            "",
        ]
    )


def write_baseline_comparison_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    identity_review = build_baseline_source_identity_review(run_dir)
    adapter_contract = build_baseline_single_skill_adapter_contract(run_dir, identity_review)
    write_json_with_category_mirrors(paths, "baseline_source_identity_review.json", identity_review, ["06_plans_and_contracts"])
    write_text_with_category_mirrors(
        paths,
        "baseline_source_identity_review.md",
        render_baseline_source_identity_review_md(identity_review),
        ["06_plans_and_contracts"],
    )
    write_json_with_category_mirrors(paths, "baseline_single_skill_adapter_contract.json", adapter_contract, ["06_plans_and_contracts"])
    write_text_with_category_mirrors(
        paths,
        "baseline_single_skill_adapter_contract.md",
        render_baseline_single_skill_adapter_contract_md(adapter_contract),
        ["06_plans_and_contracts"],
    )
    write_text_with_category_mirrors(
        paths,
        "baseline_deviation_note.md",
        render_baseline_deviation_note_md(identity_review, adapter_contract),
        ["09_safety_and_deviations"],
    )
    append_event(run_dir, "baseline_comparison_planning", identity_review["status"], artifact="artifacts/baseline_source_identity_review.json")
    return {
        "source_identity_review": identity_review,
        "adapter_contract": adapter_contract,
    }


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
                "remaining_blockers": canonical_source_remaining_blockers(run_dir, source_key, status),
            }
        )
    return {
        "schema_version": "0.1",
        "scope": "Canonical benchmark source fetch status for paper-named sources not fully covered by SkillGen official checkout",
        "run_dir": paths.run_dir.name,
        "status_counts": count_statuses(rows),
        "sources": rows,
    }


def canonical_source_remaining_blockers(run_dir: Path, source_key: str, status: str) -> list[str]:
    if source_key == "alfworld" and status == "canonical_source_fetched_not_skillgen_ready":
        contract = alfworld_group_a_contract_status(run_dir)
        if contract["status"] == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION:
            return [
                "Group A ALFWorld source/adapter/split/deviation contracts are present.",
                "Canonical data still needs to be downloaded into the run directory after human approval.",
                "The reconstructed SkillGen TextWorld adapter still needs implementation and smoke execution evidence.",
            ]
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


def contract_doc_candidate_paths(run_dir: Path, relative_path: Path) -> list[Path]:
    if relative_path.parts and relative_path.parts[0] == "artifacts":
        return [paths_for(run_dir).run_dir / relative_path]
    roots = [Path.cwd(), run_dir, *run_dir.parents]
    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        candidate = root / relative_path
        if candidate not in seen:
            unique_paths.append(candidate)
            seen.add(candidate)
    return unique_paths


def find_contract_doc(run_dir: Path, doc_key: str) -> Path | None:
    for relative_path in ALFWORLD_GROUP_A_CONTRACT_DOCS[doc_key]:
        for candidate in contract_doc_candidate_paths(run_dir, relative_path):
            if candidate.exists():
                return candidate
    return None


def alfworld_group_a_contract_status(run_dir: Path) -> dict[str, Any]:
    docs = {
        doc_key: find_contract_doc(run_dir, doc_key)
        for doc_key in ALFWORLD_GROUP_A_CONTRACT_DOCS
    }
    missing = [doc_key for doc_key, path in docs.items() if path is None]
    source_present = canonical_source_fetched(run_dir, "alfworld")
    if not source_present:
        status = "blocked_missing_official_artifact"
        remaining_blockers = [
            "Canonical ALFWorld source has not been fetched into the run directory.",
        ]
        if missing:
            remaining_blockers.append(
                "Required Group A contract documents missing: " + ", ".join(missing) + "."
            )
    elif missing:
        status = (
            "blocked_canonical_code_fetched_missing_skillgen_contract"
        )
        remaining_blockers = [
            "Group A ALFWorld contract package is incomplete.",
            "Required contract documents missing: " + ", ".join(missing) + ".",
        ]
    else:
        status = STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
        remaining_blockers = [
            "Download canonical ALFWorld data into the run directory with human approval.",
            "Implement the SkillGen-compatible ALFWorld TextWorld runner/adapter described by the contract.",
            "Generate audited IOD/OOD construction and held-out test TaskInstance files before Table 1 or transfer execution.",
        ]
    return {
        "status": status,
        "documents": {
            doc_key: str(path) if path else None
            for doc_key, path in docs.items()
        },
        "missing_documents": missing,
        "remaining_blockers": remaining_blockers,
    }


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


def env_key_inventory(run_dir: Path) -> dict[str, Any]:
    project_root = project_root_from(run_dir)
    dotenv_values = load_dotenv(project_root)
    keys: dict[str, dict[str, Any]] = {}
    for name in PROVIDER_ENV_KEYS:
        sources = []
        if os.environ.get(name):
            sources.append("process_env")
        if dotenv_values.get(name):
            sources.append("project_root_dotenv")
        keys[name] = {
            "present": bool(sources),
            "sources": sources,
        }
    return {
        "project_root": rel(project_root, project_root) if project_root.exists() else str(project_root),
        "dotenv_path": ".env" if (project_root / ".env").exists() else None,
        "keys": keys,
        "security_note": "Only key presence and source type are recorded; secret values are never written.",
    }


def detect_openrouter_billing_failure(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    search_roots = [
        paths.outputs_dir,
        paths.artifacts_dir / "08_results" / "raw_benchmark_outputs",
        paths.artifacts_dir / "raw_benchmark_outputs",
    ]
    evidence_files: list[str] = []
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*stderr*.txt"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")[:1_000_000].lower()
            except OSError:
                continue
            if "openrouter" in text and ("402" in text or "insufficient credits" in text):
                evidence_files.append(rel(path, paths.run_dir))
    return {
        "detected": bool(evidence_files),
        "evidence_files": sorted(set(evidence_files)),
    }


def direct_provider_key_hints_for_route(route: str) -> list[str]:
    for prefix, keys in NON_OPENAI_DIRECT_PROVIDER_KEY_HINTS.items():
        if route.startswith(prefix):
            return keys
    return []


def build_provider_resolution_status(
    run_dir: Path,
    *,
    include_non_openai: bool = False,
    direct_openai_fallback: bool = True,
    allow_openrouter_after_402: bool = False,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    route_mapping = build_model_route_mapping_template(run_dir)
    inventory = env_key_inventory(run_dir)
    keys = inventory["keys"]
    openrouter_failure = detect_openrouter_billing_failure(run_dir)
    openrouter_key_present = bool(keys.get("OPENROUTER_API_KEY", {}).get("present"))
    openai_key_present = bool(keys.get("OPENAI_API_KEY", {}).get("present"))
    openrouter_usable = openrouter_key_present and (allow_openrouter_after_402 or not openrouter_failure["detected"])
    openai_direct_planned = direct_openai_fallback

    route_rows = []
    for model in route_mapping.get("paper_table1_models", []):
        route = model.get("provider_route_id") or ""
        route_is_openai = route.startswith("openai/")
        direct_key_hints = direct_provider_key_hints_for_route(route)
        direct_keys_present = [key for key in direct_key_hints if keys.get(key, {}).get("present")]
        if route_is_openai and openai_direct_planned:
            execution_status = "executable_via_direct_openai"
            runner_status = "candidate_ready"
            reason = "OpenAI paper route can bypass OpenRouter through SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1."
            if not openai_key_present:
                reason += " OPENAI_API_KEY was not detected in this process/root .env inventory, so execution would still need that key at runtime."
        elif route_is_openai and openrouter_usable:
            execution_status = "executable_via_openrouter_unverified"
            runner_status = "candidate_ready"
            reason = "OpenRouter key is present and no 402 evidence was detected in this run directory."
        elif not route_is_openai and not openrouter_key_present:
            execution_status = "provider_unavailable_missing_openrouter_key"
            runner_status = STATUS_PROVIDER_UNAVAILABLE
            reason = "The current runner has no direct non-OpenAI provider integration and no OpenRouter key was detected."
        elif not route_is_openai and openrouter_failure["detected"] and not allow_openrouter_after_402:
            execution_status = "provider_unavailable_openrouter_402"
            runner_status = STATUS_PROVIDER_UNAVAILABLE
            reason = "The current non-OpenAI route path depends on OpenRouter, and this run has captured OpenRouter 402 insufficient-credit evidence. If credits/key are repaired, rerun with --allow-openrouter-after-402 to treat this as historical evidence."
        elif not route_is_openai and not include_non_openai:
            execution_status = STATUS_WAITING_PROVIDER_ROUTE_RESOLUTION
            runner_status = STATUS_WAITING_PROVIDER_ROUTE_RESOLUTION
            reason = "Non-OpenAI routes are intentionally skipped by default; pass --include-non-openai only after provider execution is intentionally enabled."
        else:
            execution_status = "executable_via_openrouter_unverified"
            runner_status = "candidate_ready"
            reason = "OpenRouter key is present and no 402 evidence was detected; execution may still fail if billing/catalog/provider access changes."
            if openrouter_failure["detected"] and allow_openrouter_after_402:
                reason = "OpenRouter key is present; prior captured 402 evidence is being treated as historical because --allow-openrouter-after-402 was set. Execution may still fail if credits/key are not actually repaired."
        route_rows.append(
            {
                "paper_display_name": model.get("paper_display_name"),
                "provider_route_id": route,
                "route_status": model.get("status"),
                "route_is_openai": route_is_openai,
                "execution_status": execution_status,
                "runner_status": runner_status,
                "reason": reason,
                "direct_provider_key_hints": direct_key_hints,
                "direct_provider_keys_present": direct_keys_present,
                "direct_provider_runner_status": (
                    "available_for_openai_only"
                    if route_is_openai and openai_direct_planned
                    else "not_integrated_by_current_runner"
                ),
            }
        )

    non_openai_unavailable = [row for row in route_rows if not row["route_is_openai"] and row["runner_status"] == STATUS_PROVIDER_UNAVAILABLE]
    non_openai_waiting = [row for row in route_rows if not row["route_is_openai"] and row["runner_status"] == STATUS_WAITING_PROVIDER_ROUTE_RESOLUTION]
    openai_ready = [row for row in route_rows if row["route_is_openai"] and row["runner_status"] == "candidate_ready"]
    status = "provider_policy_ready"
    if non_openai_unavailable:
        status = "openai_ready_non_openai_provider_unavailable"
    elif non_openai_waiting:
        status = "openai_ready_non_openai_waiting_route_resolution"
    if not openai_ready:
        status = "provider_resolution_blocked"

    return {
        "schema_version": "0.1",
        "scope": "Provider availability policy for SkillGen full-matrix execution.",
        "run_dir": paths.run_dir.name,
        "status": status,
        "policy": {
            "direct_openai_fallback": direct_openai_fallback,
            "include_non_openai": include_non_openai,
            "allow_openrouter_after_402": allow_openrouter_after_402,
            "model_substitution_allowed": False,
            "non_openai_direct_provider_runner_status": "not_integrated_by_current_runner",
            "matrix_behavior": "Run executable entries; record provider-unavailable entries without treating provider failure as benchmark evidence.",
        },
        "env_key_inventory": inventory,
        "openrouter_billing_failure": openrouter_failure,
        "provider_summary": {
            "openai_candidate_ready_models": len(openai_ready),
            "non_openai_provider_unavailable_models": len(non_openai_unavailable),
            "non_openai_waiting_route_resolution_models": len(non_openai_waiting),
        },
        "routes": route_rows,
        "operational_decision": [
            "Continue full-matrix execution for openai/* routes with direct OpenAI fallback enabled.",
            "Do not attempt non-OpenAI routes while OpenRouter 402 evidence is present unless OpenRouter credits/key are repaired or a reviewed direct-provider integration is added.",
            "Do not substitute non-OpenAI paper models with OpenAI models for Table 1 reproduction; any substitute-model run must be marked as an extended/deviation-backed experiment.",
        ],
    }


def render_provider_resolution_status_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Provider Resolution Status",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Policy",
        "",
    ]
    for key, value in payload.get("policy", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    summary = payload.get("provider_summary") or {}
    lines.extend(["", "## Provider Summary", ""])
    for key, value in summary.items():
        lines.append(f"- `{key}`: `{value}`")
    billing = payload.get("openrouter_billing_failure") or {}
    lines.extend(
        [
            "",
            "## OpenRouter Billing Evidence",
            "",
            f"- `detected`: `{billing.get('detected')}`",
        ]
    )
    evidence_files = billing.get("evidence_files") or []
    if evidence_files:
        lines.extend(f"- `evidence_file`: `{path}`" for path in evidence_files)
    inventory = payload.get("env_key_inventory") or {}
    keys = inventory.get("keys") or {}
    lines.extend(["", "## Key Inventory", "", "| Key | Present | Sources |", "| --- | --- | --- |"])
    for key in PROVIDER_ENV_KEYS:
        row = keys.get(key, {})
        lines.append(f"| `{key}` | `{bool(row.get('present'))}` | `{', '.join(row.get('sources') or []) or 'none'}` |")
    lines.extend(
        [
            "",
            "## Routes",
            "",
            "| Paper model | Provider route | Execution status | Runner status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in payload.get("routes", []):
        lines.append(
            f"| `{row.get('paper_display_name')}` | `{row.get('provider_route_id')}` | `{row.get('execution_status')}` | `{row.get('runner_status')}` |"
        )
    lines.extend(["", "## Operational Decision", ""])
    lines.extend(f"- {item}" for item in payload.get("operational_decision", []))
    return "\n".join(lines).rstrip() + "\n"


def write_provider_resolution_status(
    run_dir: Path,
    *,
    include_non_openai: bool = False,
    direct_openai_fallback: bool = True,
    allow_openrouter_after_402: bool = False,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    payload = build_provider_resolution_status(
        run_dir,
        include_non_openai=include_non_openai,
        direct_openai_fallback=direct_openai_fallback,
        allow_openrouter_after_402=allow_openrouter_after_402,
    )
    write_json_with_category_mirrors(paths, "provider_resolution_status.json", payload, ["06_plans_and_contracts"])
    write_text_with_category_mirrors(
        paths,
        "provider_resolution_status.md",
        render_provider_resolution_status_md(payload),
        ["06_plans_and_contracts"],
    )
    return payload


def build_benchmark_execution_plan(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    targets: list[dict[str, Any]] = []
    alfworld_group_a = alfworld_group_a_contract_status(run_dir)
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
    if alfworld_group_a["status"] == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION:
        alfworld_status = STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
        alfworld_reason = (
            "Group A reconstructed-execution contract is present; execution still requires canonical ALFWorld "
            "data download, adapter implementation, and generated IOD/OOD TaskInstance train/test files."
        )
    table1_specs = [
        ("alfworld_iod", "data/alfworld_iod/train.json", "data/alfworld_iod/test.json", alfworld_status, alfworld_reason),
        ("alfworld_ood", "data/alfworld_ood/train.json", "data/alfworld_ood/test.json", alfworld_status, alfworld_reason),
        ("livecodebench", LIVECODEBENCH_TRAIN_REL, LIVECODEBENCH_TEST_REL, "blocked_pending_train_test_split_contract", "LiveCodeBench release v6 source exists, but the paper-matching 50/150 seed-42 train/test split has not been generated and approved."),
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
        if row_id in {"alfworld_iod", "alfworld_ood"}:
            target["group_a_contract"] = alfworld_group_a
            if (
                alfworld_group_a["status"] == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
                and target["dataset"]["train_exists"]
                and target["dataset"]["test_exists"]
            ):
                target["status"] = STATUS_READY_FOR_RECONSTRUCTED_EXECUTION
                target["paper_table1_entry_count"] = 0
                target["blockers"] = [
                    "Reconstructed ALFWorld offline-plan adapter data is present and load-smoked; full execution still requires human approval of the deviation label, model route, cost, and trace-retention policy."
                ]
                target["notes"].extend(
                    [
                        "Uses canonical ALFWorld data source with reconstructed SkillGen offline-plan adapter.",
                        "Generated split/provenance manifest: code/official/data/alfworld_split_manifest_seed42.json.",
                        "Adapter deviation note: artifacts/09_safety_and_deviations/alfworld_adapter_deviation_note.md.",
                        "Per-round traces and eval_skill trajectory JSONL outputs must be retained for every future run.",
                    ]
                )
        if row_id == "livecodebench":
            target["group_b_contract"] = build_livecodebench_split_contract(run_dir)
            target["notes"].extend(
                [
                    "Uses the reconstructed paper Table 3 split contract: release_v6/test_release_v6, construction n=50, held-out test n=150, seed=42.",
                    f"Split manifest: code/official/{LIVECODEBENCH_SPLIT_MANIFEST_REL}",
                ]
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
    alfworld_ood_target = target_by_id.get("alfworld_ood")
    if (alfworld_ood_target or {}).get("status") == STATUS_READY_FOR_RECONSTRUCTED_EXECUTION:
        remaining_blockers = [
            "ALFWorld OOD has a Group A reconstructed-execution contract package.",
            "Transfer execution still needs approved canonical data download, adapter implementation, generated OOD train/test TaskInstance files, and per-round trace retention.",
        ]
    else:
        remaining_blockers = [
            "ALFWorld OOD data is not available in the current official checkout.",
            "ALFWorld OOD canonical code is fetched but still lacks a SkillGen-compatible adapter/split contract.",
        ]
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
        "remaining_blockers": remaining_blockers,
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


def build_full_matrix_execution_contract(
    run_dir: Path,
    benchmark_plan: dict[str, Any] | None = None,
    model_routes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    benchmark_plan = benchmark_plan or build_benchmark_execution_plan(run_dir)
    model_routes = model_routes or build_model_route_mapping_template(run_dir)
    target_by_row = {
        target.get("table1_row"): target
        for target in benchmark_plan.get("targets", [])
        if target.get("table1_row")
    }
    route_by_name = {
        row["paper_display_name"]: row
        for row in model_routes.get("paper_table1_models", [])
    }
    row_contracts = []
    execution_entries = []
    for row_id in TABLE1_REQUIRED_ROWS:
        target = target_by_row.get(row_id, {})
        row_status = target.get("status", "blocked_missing_target_plan")
        row_contracts.append(
            {
                "table1_row": row_id,
                "dataset_status": row_status,
                "train": (target.get("dataset") or {}).get("train"),
                "test": (target.get("dataset") or {}).get("test"),
                "blockers": target.get("blockers") or ["No benchmark target plan exists for this Table 1 row."],
            }
        )
        for model_name in PAPER_MODEL_NAMES:
            route = route_by_name.get(model_name, {})
            route_status = route.get("status", "unresolved")
            entry_ready = row_status == STATUS_READY_FOR_EXECUTION and route.get("provider_route_id") is not None
            execution_entries.append(
                {
                    "entry_id": f"{row_id}::{model_name}",
                    "table1_row": row_id,
                    "paper_model": model_name,
                    "provider_route_id": route.get("provider_route_id"),
                    "dataset_status": row_status,
                    "route_status": route_status,
                    "status": STATUS_READY_FOR_EXECUTION if entry_ready else STATUS_BLOCKED,
                    "output_dir_template": f"artifacts/raw_benchmark_outputs/full_matrix/{row_id}/{{model_slug}}",
                }
            )
    ready_entries = [entry for entry in execution_entries if entry["status"] == STATUS_READY_FOR_EXECUTION]
    blocked_rows = [row for row in row_contracts if row["dataset_status"] != STATUS_READY_FOR_EXECUTION]
    return {
        "schema_version": "0.1",
        "group": "C_execution_trace",
        "scope": "Full Table 1 execution and aggregation contract for SkillGen Phase 0",
        "run_dir": paths.run_dir.name,
        "status": STATUS_READY_FOR_EXECUTION if len(ready_entries) == len(execution_entries) else STATUS_BLOCKED,
        "dependencies": [
            {
                "group": "A",
                "artifact": "logs/phase_0_parallel_20260604/A_alfworld/alfworld_adapter_contract.md",
                "reason": "ALFWorld IOD/OOD rows need a SkillGen adapter and paper-matching split before the 80-entry matrix is complete.",
            },
            {
                "group": "B",
                "artifact": "logs/phase_0_parallel_20260604/B_livecodebench/livecodebench_split_contract.md",
                "reason": "LiveCodeBench needs an approved train/test split contract before its eight model entries can be counted.",
            },
        ],
        "source_artifacts": [
            "artifacts/benchmark_execution_plan.json",
            "artifacts/model_route_mapping.template.json",
        ],
        "table1_rows": row_contracts,
        "paper_models": PAPER_MODEL_NAMES,
        "entry_count": {
            "paper_required": len(TABLE1_REQUIRED_ROWS) * len(PAPER_MODEL_NAMES),
            "ready": len(ready_entries),
            "blocked": len(execution_entries) - len(ready_entries),
        },
        "execution_manifest_template": {
            "entry_key": "{table1_row}::{paper_model}",
            "config_path": "artifacts/generated_configs/{table1_row}/{model_slug}.yaml",
            "skill_output_dir": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/skill_output",
            "eval_results": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/eval_results.json",
            "eval_trajectories_dir": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/eval_results_trajectories",
            "token_usage": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/eval_results.token_usage.json",
            "run_metadata": "artifacts/raw_benchmark_outputs/full_matrix/{table1_row}/{model_slug}/artifacts/runs/{run_id}/run_metadata.json",
        },
        "required_result_fields": [
            "n_instances",
            "baseline_acc",
            "skill_acc",
            "delta_acc",
            "repair",
            "regression",
            "net_gain",
        ],
        "aggregation_rules": [
            {
                "claim_id": "claim_table1_average_gains_all_models",
                "rule": "For each paper model, average delta_acc across the 10 Table 1 rows after all 80 entries are present.",
                "ready_condition": "All 80 entries have parsed baseline_acc, skill_acc, and delta_acc from official eval outputs.",
            },
            {
                "claim_id": "claim_table1_entry_counts",
                "rule": "Classify each of the 80 delta_acc values as improved if > 0, unchanged if == 0, and regressed if < 0; compare counts to 50/25/5.",
                "ready_condition": "All 80 entries are present and no row is filled by a smoke-scale or reconstructed-only substitute.",
            },
            {
                "claim_id": "claim_table1_alfworld_scienceworld_patterns",
                "rule": "Count positive delta_acc for ALFWorld IOD/OOD across 16 entries and ScienceWorld across 8 entries; compare to 14/16 and 8/8.",
                "ready_condition": "ALFWorld IOD/OOD and ScienceWorld entries are executed against paper-matching splits.",
            },
        ],
        "blocked_rows": blocked_rows,
        "execution_entries": execution_entries,
    }


def render_full_matrix_execution_contract_md(payload: dict[str, Any]) -> str:
    counts = payload["entry_count"]
    lines = [
        "# Full Matrix Execution Contract",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Ready entries: `{counts['ready']}` of `{counts['paper_required']}`",
        "",
        "## Dependencies",
        "",
    ]
    for dependency in payload["dependencies"]:
        lines.append(f"- Group `{dependency['group']}`: `{dependency['artifact']}` - {dependency['reason']}")
    lines.extend(
        [
            "",
            "## Table 1 Rows",
            "",
            "| Row | Dataset status | Train/Test | Blockers |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in payload["table1_rows"]:
        train_test = f"{row.get('train') or 'missing'} / {row.get('test') or 'missing'}"
        blockers = "; ".join(row.get("blockers") or [])
        lines.append(f"| `{row['table1_row']}` | `{row['dataset_status']}` | `{train_test}` | {table_cell(blockers)} |")
    lines.extend(["", "## Aggregation Rules", ""])
    for rule in payload["aggregation_rules"]:
        lines.append(f"- `{rule['claim_id']}`: {rule['rule']}")
    lines.extend(["", "## Required Result Fields", ""])
    lines.extend(f"- `{field}`" for field in payload["required_result_fields"])
    return "\n".join(lines).rstrip() + "\n"


def build_transfer_execution_contract(
    run_dir: Path,
    transfer_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    transfer_plan = transfer_plan or build_transfer_runner_plan(run_dir)
    benchmark_rows = transfer_plan.get("benchmarks", [])
    ready_benchmarks = [
        row["benchmark_row"]
        for row in benchmark_rows
        if row.get("dataset_status") == STATUS_READY_FOR_EXECUTION
    ]
    blocked_benchmarks = [
        row
        for row in benchmark_rows
        if row.get("dataset_status") != STATUS_READY_FOR_EXECUTION
    ]
    return {
        "schema_version": "0.1",
        "group": "C_execution_trace",
        "scope": "Cross-model transfer execution and aggregation contract for SkillGen Figure 4",
        "run_dir": paths.run_dir.name,
        "status": STATUS_READY_FOR_EXECUTION if not blocked_benchmarks else STATUS_BLOCKED,
        "source_artifacts": ["artifacts/transfer_runner_plan.json", "artifacts/model_route_mapping.template.json"],
        "matrix_dimensions": {
            "benchmarks": TRANSFER_BENCHMARK_ROWS,
            "source_models": TRANSFER_MODEL_NAMES,
            "evaluator_models": TRANSFER_MODEL_NAMES,
            "off_diagonal_pairs_per_benchmark": transfer_plan.get("off_diagonal_pairs_per_benchmark"),
            "paper_required_comparisons": 120,
            "planned_comparisons": transfer_plan.get("planned_off_diagonal_comparisons"),
        },
        "ready_benchmarks": ready_benchmarks,
        "blocked_benchmarks": blocked_benchmarks,
        "execution_manifest_template": {
            "source_skill_dir": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/{source_model_slug}/skill_output",
            "evaluator_baseline": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/baselines/{evaluator_model_slug}/eval_results.json",
            "transferred_eval": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/{source_model_slug}/{evaluator_model_slug}/eval_results.json",
            "transferred_trajectories": "artifacts/raw_benchmark_outputs/transfer/{benchmark_row}/{source_model_slug}/{evaluator_model_slug}/eval_results_trajectories",
        },
        "comparison_contract": [
            "Only source_model != evaluator_model pairs count toward the 120 off-diagonal comparisons.",
            "Compare transferred_eval skill_acc against the same evaluator model's no-skill baseline_acc on the same held-out instances.",
            "Use the same benchmark split for source skill construction, evaluator baseline, and transferred-skill evaluation.",
            "Record gate-deprecated source skills explicitly; do not silently drop those source/evaluator pairs.",
        ],
        "aggregation_rules": [
            "non_negative_rate = count(delta_acc >= 0) / 120 after all off-diagonal comparisons are parsed.",
            "exceed_5pp_rate = count(delta_acc > 0.05) / 120 after all off-diagonal comparisons are parsed.",
            "A partial transfer matrix can be reported only as incomplete evidence and must not be compared as the paper Figure 4 result.",
        ],
        "remaining_blockers": transfer_plan.get("remaining_blockers", []),
    }


def render_transfer_execution_contract_md(payload: dict[str, Any]) -> str:
    dimensions = payload["matrix_dimensions"]
    lines = [
        "# Transfer Execution Contract",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Planned comparisons: `{dimensions.get('planned_comparisons')}` of `{dimensions['paper_required_comparisons']}`",
        "",
        "## Benchmark Readiness",
        "",
        f"- Ready: `{', '.join(payload['ready_benchmarks']) or 'none'}`",
        f"- Blocked: `{', '.join(row['benchmark_row'] for row in payload['blocked_benchmarks']) or 'none'}`",
        "",
        "## Comparison Contract",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["comparison_contract"])
    lines.extend(["", "## Aggregation Rules", ""])
    lines.extend(f"- {item}" for item in payload["aggregation_rules"])
    return "\n".join(lines).rstrip() + "\n"


def per_round_trace_inventory(paths: RunPaths) -> list[dict[str, Any]]:
    if not paths.raw_dir.exists():
        return []
    inventory = []
    for summary_path in sorted(paths.raw_dir.rglob("verification_summary.json")):
        round_dir = summary_path.parent
        inventory.append(
            {
                "round_dir": rel(round_dir, paths.run_dir),
                "verification_summary": rel(summary_path, paths.run_dir),
                "verification_baseline_exists": (round_dir / "verification_baseline.jsonl").exists(),
                "verification_with_skill_exists": (round_dir / "verification_with_skill.jsonl").exists(),
                "verification_case_analyses_exists": (round_dir / "verification_case_analyses.json").exists(),
            }
        )
    return inventory


def build_figure7_trace_extraction_contract(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    inventory = per_round_trace_inventory(paths)
    complete_rounds = [
        row
        for row in inventory
        if row["verification_baseline_exists"]
        and row["verification_with_skill_exists"]
        and row["verification_case_analyses_exists"]
    ]
    return {
        "schema_version": "0.1",
        "group": "C_execution_trace",
        "scope": "Figure 7 per-round refinement trace extraction and aggregation contract",
        "run_dir": paths.run_dir.name,
        "status": STATUS_BLOCKED,
        "paper_claim_id": "claim_refinement_best_of_k",
        "trace_globs": {
            "verification_baseline": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_baseline.jsonl",
            "verification_with_skill": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_with_skill.jsonl",
            "verification_summary": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_summary.json",
            "verification_case_analyses": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_case_analyses.json",
            "candidate_skill": "artifacts/raw_benchmark_outputs/**/candidates/*_gen.json",
        },
        "round_record_schema": {
            "run_id": "string",
            "benchmark_row": "string",
            "paper_model": "string",
            "round_index": "integer",
            "candidate_skill_id": "string",
            "candidate_skill_artifact": "path",
            "baseline_trace_path": "path",
            "with_skill_trace_path": "path",
            "case_analyses_path": "path",
            "paired_n": "integer",
            "baseline_acc": "number",
            "skill_acc": "number",
            "delta_acc": "number",
            "repair_count": "integer",
            "regression_count": "integer",
            "net_gain": "integer",
            "gate_passed": "boolean",
        },
        "extraction_steps": [
            "Inventory every verification/round_* directory for each benchmark-model run.",
            "Reject a round record unless baseline traces, with-skill traces, summary, and case analyses are all present.",
            "Parse verification_summary.json as the source of accuracy, repair, regression, net_gain, and gate fields.",
            "Link each round to its candidate skill artifact before calculating best-of-K.",
            "Compute best_of_k_skill_acc as the cumulative max skill_acc over ordered rounds within a run.",
            "Aggregate per-round and best-of-K curves across representative runs only after the full paper-scale trace set is available.",
        ],
        "aggregation_rules": [
            "per_round_skill_accuracy[K] = mean(skill_acc for round K across included runs).",
            "best_of_k_skill_accuracy[K] = mean(max(skill_acc for rounds <= K) across included runs).",
            "Confidence intervals must be computed over run-level curves, not over individual cases pooled across runs.",
        ],
        "current_inventory": {
            "rounds_with_summary": len(inventory),
            "complete_rounds": len(complete_rounds),
            "rounds": inventory,
        },
        "remaining_blockers": [
            "The current run does not contain the paper-scale representative per-round trace set for Figure 7.",
            "Future full runs must preserve round-level files instead of only final skill/eval summaries.",
        ],
    }


def render_figure7_trace_extraction_contract_md(payload: dict[str, Any]) -> str:
    inventory = payload["current_inventory"]
    lines = [
        "# Figure 7 Trace Extraction Contract",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Current complete rounds: `{inventory['complete_rounds']}` of `{inventory['rounds_with_summary']}` with summaries",
        "",
        "## Required Trace Globs",
        "",
    ]
    for name, pattern in payload["trace_globs"].items():
        lines.append(f"- `{name}`: `{pattern}`")
    lines.extend(["", "## Extraction Steps", ""])
    lines.extend(f"- {step}" for step in payload["extraction_steps"])
    lines.extend(["", "## Aggregation Rules", ""])
    lines.extend(f"- {rule}" for rule in payload["aggregation_rules"])
    return "\n".join(lines).rstrip() + "\n"


def build_per_round_trace_retention_checklist(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    checks = [
        {
            "id": "verification_baseline",
            "required": True,
            "glob": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_baseline.jsonl",
            "purpose": "Recompute baseline outcomes and identify cases repaired by candidate skills.",
        },
        {
            "id": "verification_with_skill",
            "required": True,
            "glob": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_with_skill.jsonl",
            "purpose": "Recompute with-skill outcomes and identify regressions.",
        },
        {
            "id": "verification_summary",
            "required": True,
            "glob": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_summary.json",
            "purpose": "Read paired_n, accuracy, repair, regression, net_gain, and gate pass/fail per round.",
        },
        {
            "id": "verification_case_analyses",
            "required": True,
            "glob": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/verification/round_*/verification_case_analyses.json",
            "purpose": "Preserve per-case repair/regression explanations for audit and Figure 7 debugging.",
        },
        {
            "id": "candidate_skill_artifact",
            "required": True,
            "glob": "artifacts/raw_benchmark_outputs/**/candidates/*_gen.json",
            "purpose": "Link each round's result to the candidate skill that was evaluated.",
        },
        {
            "id": "run_metadata",
            "required": True,
            "glob": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/run_metadata.json",
            "purpose": "Preserve benchmark, model, dataset, config, route, and execution metadata for grouping.",
        },
        {
            "id": "token_usage",
            "required": False,
            "glob": "artifacts/raw_benchmark_outputs/**/artifacts/runs/*/token_usage.json",
            "purpose": "Support token-cost and runtime diagnostics without mixing them into Figure 7 accuracy.",
        },
    ]
    for check in checks:
        check["current_count"] = len(list(paths.run_dir.glob(check["glob"])))
        check["status"] = "present" if check["current_count"] else "missing_in_current_run"
    return {
        "schema_version": "0.1",
        "group": "C_execution_trace",
        "scope": "Minimum per-round trace retention checklist for future SkillGen full/refinement runs",
        "run_dir": paths.run_dir.name,
        "status": STATUS_READY_FOR_EXECUTION,
        "retention_policy": [
            "Do not delete or overwrite verification/round_* directories after selecting the final skill.",
            "Store round artifacts under target/model/run-specific directories so retries cannot replace earlier evidence.",
            "Every future full-matrix or Figure 7 run must fail validation if a required trace file is missing.",
            "A parsed aggregate may be regenerated from raw traces, but raw traces must remain the primary evidence.",
        ],
        "checks": checks,
    }


def render_per_round_trace_retention_checklist_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Per-Round Trace Retention Checklist",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Retention Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["retention_policy"])
    lines.extend(["", "## Required Files", "", "| Check | Required | Current count | Purpose |", "| --- | --- | --- | --- |"])
    for check in payload["checks"]:
        lines.append(
            f"| `{check['id']}` | `{check['required']}` | `{check['current_count']}` | {table_cell(check['purpose'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def ablation_expected_outputs(arm_id: str) -> list[str]:
    return [
        f"artifacts/raw_benchmark_outputs/ablation/{{layer}}/{{dataset_id}}/{{model_slug}}/{arm_id}/train_stdout.txt",
        f"artifacts/raw_benchmark_outputs/ablation/{{layer}}/{{dataset_id}}/{{model_slug}}/{arm_id}/train_stderr.txt",
        f"artifacts/raw_benchmark_outputs/ablation/{{layer}}/{{dataset_id}}/{{model_slug}}/{arm_id}/skill_output",
        f"artifacts/raw_benchmark_outputs/ablation/{{layer}}/{{dataset_id}}/{{model_slug}}/{arm_id}/eval_results.json",
        f"artifacts/raw_benchmark_outputs/ablation/{{layer}}/{{dataset_id}}/{{model_slug}}/{arm_id}/eval_results_trajectories",
        f"artifacts/raw_benchmark_outputs/ablation/{{layer}}/{{dataset_id}}/{{model_slug}}/{arm_id}/deviation_note.md",
    ]


def reconstructed_ablation_arm_rows() -> list[dict[str, Any]]:
    rows = []
    for arm in ABLATION_ARMS:
        row = dict(arm)
        row["status"] = STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION
        row["expected_artifact_outputs"] = ablation_expected_outputs(row["arm_id"])
        row["approval_required_before_execution"] = row["arm_id"] != "Full"
        rows.append(row)
    return rows


def build_reconstructed_ablation_contract(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    arms = reconstructed_ablation_arm_rows()
    return {
        "schema_version": "0.1",
        "group": "E_ablation",
        "scope": "Deviation-backed reconstructed execution contract for SkillGen Figure 3 ablations",
        "run_dir": paths.run_dir.name,
        "claim_id": "claim_ablation_full_wins",
        "status": STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION,
        "reproduction_class": "deviation_backed_reconstructed_verification",
        "exact_reproduction_blockers": [
            "The current official checkout does not include an author-provided Figure 3 ablation runner.",
            "The current official checkout does not include named A1-A5 ablated config files.",
            "Any execution from this contract must be reported as reconstructed unless original author configs are later found.",
        ],
        "paper_arms": [arm["arm_id"] for arm in arms],
        "shared_execution_contract": {
            "paired_harness": "Use the same no-skill baseline, held-out instances, model route, judge route, seed, and evaluator for Full and every ablation arm.",
            "primary_metric": "delta_acc = skill_acc - baseline_acc on held-out paired evaluation.",
            "claim_rule": "Full wins only if Full has higher held-out skill_acc or delta_acc than each A1-A5 arm for every executed dataset-model pair.",
            "human_gate": "Human approval is required before executing reconstructed ablations, especially A3 because it disables the verification gate.",
            "storage_rule": "All configs, patches, generated skills, raw logs, trajectories, and caches must remain inside the run directory.",
            "trace_retention": [
                "Retain construction baseline and checkpoint trajectories.",
                "Retain verification/round_* baseline, with-skill, summary, and case-analysis files.",
                "Retain held-out eval_results.json and eval_results_trajectories for every arm.",
            ],
        },
        "arms": arms,
        "execution_layers": [
            {
                "layer": "smoke_reconstructed_ablation",
                "status": STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION,
                "purpose": "Exercise Full and A1-A5 mechanics on one cheap approved dataset-model pair before paper-target matrix execution.",
                "default_target": TARGET_ID,
                "acceptance_criteria": [
                    "Every arm writes config or patch artifacts before execution.",
                    "Every arm writes raw stdout/stderr and eval_results.json.",
                    "The A3 run preserves failed-gate verification evidence before gate override.",
                    "The output claim comparison labels the run as reconstructed smoke evidence.",
                ],
            },
            {
                "layer": "paper_target_reconstructed_ablation",
                "status": STATUS_BLOCKED,
                "purpose": "Run the reconstructed ablation matrix on the Figure 3 dataset-model pairs after those pairs are explicitly reviewed.",
                "remaining_blockers": [
                    "Figure 3 dataset-model pair list must be confirmed from paper/report artifacts.",
                    "Human must approve any prompt/code patch before execution.",
                    "Full Table 1 structural blockers may still limit paper-target pair availability.",
                ],
            },
        ],
    }


def render_reconstructed_ablation_contract_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Reconstructed Ablation Contract",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Reproduction class: `{payload['reproduction_class']}`",
        "",
        "## Exact Reproduction Blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["exact_reproduction_blockers"])
    lines.extend(
        [
            "",
            "## Shared Execution Contract",
            "",
        ]
    )
    for key, value in payload["shared_execution_contract"].items():
        if isinstance(value, list):
            lines.append(f"- `{key}`:")
            lines.extend(f"  - {item}" for item in value)
        else:
            lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Arms",
            "",
            "| Arm | Name | Implementation | Deviation label | Safety note |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for arm in payload["arms"]:
        lines.append(
            f"| `{arm['arm_id']}` | {table_cell(arm['name'])} | `{arm['implementation_type']}` | "
            f"`{arm['deviation_label']}` | {table_cell(arm['safety_note'])} |"
        )
    lines.extend(["", "## Execution Layers", ""])
    for layer in payload["execution_layers"]:
        lines.append(f"- `{layer['layer']}`: `{layer['status']}` - {layer['purpose']}")
    return "\n".join(lines).rstrip() + "\n"


def build_ablation_config_matrix(contract: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for arm in contract["arms"]:
        rows.append(
            {
                "arm_id": arm["arm_id"],
                "name": arm["name"],
                "status": arm["status"],
                "implementation_type": arm["implementation_type"],
                "config_overrides": arm["config_overrides"],
                "patch_or_wrapper_path": arm["patch_or_wrapper_path"],
                "expected_artifact_outputs": arm["expected_artifact_outputs"],
                "deviation_label": arm["deviation_label"],
                "rollback_note": arm["rollback_note"],
            }
        )
    return {
        "schema_version": "0.1",
        "group": "E_ablation",
        "scope": "Config and wrapper matrix for reconstructed SkillGen Figure 3 ablations",
        "status": contract["status"],
        "claim_id": contract["claim_id"],
        "rows": rows,
    }


def render_ablation_config_matrix_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Ablation Config Matrix",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        "",
        "| Arm | Implementation type | Patch/config path | Key overrides | Rollback |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        overrides = ", ".join(f"{key}={value}" for key, value in row["config_overrides"].items()) or "none"
        lines.append(
            f"| `{row['arm_id']}` | `{row['implementation_type']}` | `{row.get('patch_or_wrapper_path') or 'none'}` | "
            f"{table_cell(overrides)} | {table_cell(row['rollback_note'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_ablation_smoke_plan(run_dir: Path, contract: dict[str, Any]) -> dict[str, Any]:
    paths = paths_for(run_dir)
    return {
        "schema_version": "0.1",
        "group": "E_ablation",
        "scope": "Smoke execution plan for reconstructed SkillGen Figure 3 ablation arms",
        "run_dir": paths.run_dir.name,
        "status": STATUS_READY_FOR_RECONSTRUCTED_ABLATION_EXECUTION,
        "approval_required_before_execution": True,
        "recommended_target": {
            "target_id": TARGET_ID,
            "reason": "Use the existing low-cost smoke target to verify ablation mechanics before any paper-target matrix.",
            "train_dataset": "artifacts/smoke_data/aime_train_n8_seed42.json",
            "test_dataset": "artifacts/smoke_data/aime_test_n4_seed42.json",
            "model_route": "openai/gpt-5.4-nano",
            "judge_model_route": "openai/gpt-5.4-mini",
        },
        "arm_sequence": [arm["arm_id"] for arm in contract["arms"]],
        "command_templates": {
            "train": {
                "workdir": "code/official",
                "argv": [".venv/bin/python", "main.py", "{train_dataset}", "--config", "{ablation_config_path}"],
            },
            "eval": {
                "workdir": "code/official",
                "argv": [
                    ".venv/bin/python",
                    "eval_skill.py",
                    "--skill-repo",
                    "{skill_output_dir}",
                    "--dataset",
                    "{test_dataset}",
                    "--n",
                    "{eval_n}",
                    "--seed",
                    "42",
                    "--models",
                    "{model_route}",
                    "--judge-model",
                    "{judge_model_route}",
                    "--max-workers",
                    "{max_workers}",
                    "--output",
                    "artifacts/raw_benchmark_outputs/ablation/smoke/{target_id}/{model_slug}/{arm_id}/eval_results.json",
                ],
            },
        },
        "required_preflight_checks": [
            "Write one config/patch/deviation artifact per arm before execution.",
            "Verify A1 demonstration ids come only from construction successes.",
            "Verify A3 gate override is scoped only to A3 and records original gate result.",
            "Verify A4 records whether prompt-level or fallback post-process ablation was used.",
            "Verify A5 Full comparison is meaningful only when Full has scripts/references enabled.",
        ],
        "expected_outputs": {
            arm["arm_id"]: arm["expected_artifact_outputs"]
            for arm in contract["arms"]
        },
    }


def render_ablation_smoke_plan_md(payload: dict[str, Any]) -> str:
    target = payload["recommended_target"]
    lines = [
        "# Ablation Smoke Plan",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        f"Approval required before execution: `{payload['approval_required_before_execution']}`",
        "",
        "## Recommended Target",
        "",
        f"- Target: `{target['target_id']}`",
        f"- Train: `{target['train_dataset']}`",
        f"- Test: `{target['test_dataset']}`",
        f"- Model: `{target['model_route']}`",
        f"- Judge: `{target['judge_model_route']}`",
        "",
        "## Arm Sequence",
        "",
    ]
    lines.extend(f"- `{arm_id}`" for arm_id in payload["arm_sequence"])
    lines.extend(["", "## Preflight Checks", ""])
    lines.extend(f"- {item}" for item in payload["required_preflight_checks"])
    return "\n".join(lines).rstrip() + "\n"


def render_ablation_deviation_note_md(contract: dict[str, Any]) -> str:
    lines = [
        "# Ablation Deviation Note",
        "",
        "The Figure 3 ablation package is a deviation-backed reconstructed verification plan.",
        "",
        "It is not an exact original-paper reproduction because the current official checkout does not provide an author-supplied Figure 3 runner or named A1-A5 configs.",
        "",
        "## Arm-Level Deviations",
        "",
        "| Arm | Deviation label | Safety / review note |",
        "| --- | --- | --- |",
    ]
    for arm in contract["arms"]:
        lines.append(f"| `{arm['arm_id']}` | `{arm['deviation_label']}` | {table_cell(arm['safety_note'])} |")
    lines.extend(
        [
            "",
            "## Reporting Rule",
            "",
            "Any result produced from this package must be reported as reconstructed ablation evidence. Use `partially_reproduced`, `not_reproduced`, or `failed_to_run` after execution; reserve `reproduced` for a future run that uses verified author-original Figure 3 configs.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_reconstructed_ablation_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    contract = build_reconstructed_ablation_contract(run_dir)
    config_matrix = build_ablation_config_matrix(contract)
    smoke_plan = build_ablation_smoke_plan(run_dir, contract)
    write_json(paths.artifacts_dir / "reconstructed_ablation_contract.json", contract)
    write_text(paths.artifacts_dir / "reconstructed_ablation_contract.md", render_reconstructed_ablation_contract_md(contract))
    write_json(paths.artifacts_dir / "ablation_config_matrix.json", config_matrix)
    write_text(paths.artifacts_dir / "ablation_config_matrix.md", render_ablation_config_matrix_md(config_matrix))
    write_json(paths.artifacts_dir / "ablation_smoke_plan.json", smoke_plan)
    write_text(paths.artifacts_dir / "ablation_smoke_plan.md", render_ablation_smoke_plan_md(smoke_plan))
    write_text(paths.artifacts_dir / "ablation_deviation_note.md", render_ablation_deviation_note_md(contract))
    append_event(run_dir, "reconstructed_ablation_planning", "completed", artifact="artifacts/reconstructed_ablation_contract.json")
    return {
        "reconstructed_ablation_contract": contract,
        "ablation_config_matrix": config_matrix,
        "ablation_smoke_plan": smoke_plan,
    }


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
    livecodebench_contract = write_livecodebench_contract_artifacts(run_dir)
    model_routes = build_model_route_mapping_template(run_dir)
    benchmark_plan = build_benchmark_execution_plan(run_dir)
    transfer_plan = build_transfer_runner_plan(run_dir, benchmark_plan)
    full_matrix_contract = build_full_matrix_execution_contract(run_dir, benchmark_plan, model_routes)
    transfer_contract = build_transfer_execution_contract(run_dir, transfer_plan)
    figure7_contract = build_figure7_trace_extraction_contract(run_dir)
    trace_checklist = build_per_round_trace_retention_checklist(run_dir)
    token_plan = build_token_log_plan(run_dir, benchmark_plan)
    ablation_artifacts = write_reconstructed_ablation_artifacts(run_dir)
    plans_dir = paths.artifacts_dir / "06_plans_and_contracts"
    sources_dir = paths.artifacts_dir / "03_code_and_sources"

    def write_categorized_json(directory: Path, name: str, payload: dict[str, Any]) -> None:
        if directory.exists():
            write_json(directory / name, payload)

    def write_categorized_text(directory: Path, name: str, text: str) -> None:
        if directory.exists():
            write_text(directory / name, text)

    write_json(paths.artifacts_dir / "canonical_benchmark_source_status.json", canonical_source_status)
    write_text(
        paths.artifacts_dir / "canonical_benchmark_source_status.md",
        render_canonical_benchmark_source_status_md(canonical_source_status),
    )
    write_categorized_json(sources_dir, "canonical_benchmark_source_status.json", canonical_source_status)
    write_categorized_text(sources_dir, "canonical_benchmark_source_status.md", render_canonical_benchmark_source_status_md(canonical_source_status))
    write_json(paths.artifacts_dir / "model_route_mapping.template.json", model_routes)
    write_text(paths.artifacts_dir / "model_route_mapping.template.md", render_model_route_mapping_md(model_routes))
    write_categorized_json(plans_dir, "model_route_mapping.template.json", model_routes)
    write_categorized_text(plans_dir, "model_route_mapping.template.md", render_model_route_mapping_md(model_routes))
    provider_resolution = write_provider_resolution_status(run_dir)
    write_json(paths.artifacts_dir / "benchmark_execution_plan.json", benchmark_plan)
    write_text(paths.artifacts_dir / "benchmark_execution_plan.md", render_benchmark_execution_plan_md(benchmark_plan))
    write_categorized_json(plans_dir, "benchmark_execution_plan.json", benchmark_plan)
    write_categorized_text(plans_dir, "benchmark_execution_plan.md", render_benchmark_execution_plan_md(benchmark_plan))
    write_json(paths.artifacts_dir / "transfer_runner_plan.json", transfer_plan)
    write_text(paths.artifacts_dir / "transfer_runner_plan.md", render_transfer_runner_plan_md(transfer_plan))
    write_categorized_json(plans_dir, "transfer_runner_plan.json", transfer_plan)
    write_categorized_text(plans_dir, "transfer_runner_plan.md", render_transfer_runner_plan_md(transfer_plan))
    write_json(paths.artifacts_dir / "full_matrix_execution_contract.json", full_matrix_contract)
    write_text(paths.artifacts_dir / "full_matrix_execution_contract.md", render_full_matrix_execution_contract_md(full_matrix_contract))
    write_categorized_json(plans_dir, "full_matrix_execution_contract.json", full_matrix_contract)
    write_categorized_text(plans_dir, "full_matrix_execution_contract.md", render_full_matrix_execution_contract_md(full_matrix_contract))
    write_json(paths.artifacts_dir / "transfer_execution_contract.json", transfer_contract)
    write_text(paths.artifacts_dir / "transfer_execution_contract.md", render_transfer_execution_contract_md(transfer_contract))
    write_categorized_json(plans_dir, "transfer_execution_contract.json", transfer_contract)
    write_categorized_text(plans_dir, "transfer_execution_contract.md", render_transfer_execution_contract_md(transfer_contract))
    write_json(paths.artifacts_dir / "figure7_trace_extraction_contract.json", figure7_contract)
    write_text(paths.artifacts_dir / "figure7_trace_extraction_contract.md", render_figure7_trace_extraction_contract_md(figure7_contract))
    write_categorized_json(plans_dir, "figure7_trace_extraction_contract.json", figure7_contract)
    write_categorized_text(plans_dir, "figure7_trace_extraction_contract.md", render_figure7_trace_extraction_contract_md(figure7_contract))
    write_json(paths.artifacts_dir / "per_round_trace_retention_checklist.json", trace_checklist)
    write_text(paths.artifacts_dir / "per_round_trace_retention_checklist.md", render_per_round_trace_retention_checklist_md(trace_checklist))
    write_categorized_json(plans_dir, "per_round_trace_retention_checklist.json", trace_checklist)
    write_categorized_text(plans_dir, "per_round_trace_retention_checklist.md", render_per_round_trace_retention_checklist_md(trace_checklist))
    write_json(paths.artifacts_dir / "token_log_plan.json", token_plan)
    write_text(paths.artifacts_dir / "token_log_plan.md", render_token_log_plan_md(token_plan))
    write_categorized_json(plans_dir, "token_log_plan.json", token_plan)
    write_categorized_text(plans_dir, "token_log_plan.md", render_token_log_plan_md(token_plan))
    append_event(run_dir, "benchmark_execution_planning", "completed", artifact="artifacts/benchmark_execution_plan.json")
    return {
        "model_route_mapping": model_routes,
        "provider_resolution_status": provider_resolution,
        "benchmark_execution_plan": benchmark_plan,
        "transfer_runner_plan": transfer_plan,
        "full_matrix_execution_contract": full_matrix_contract,
        "transfer_execution_contract": transfer_contract,
        "figure7_trace_extraction_contract": figure7_contract,
        "per_round_trace_retention_checklist": trace_checklist,
        "token_log_plan": token_plan,
        "canonical_benchmark_source_status": canonical_source_status,
        "livecodebench_group_b_contract": livecodebench_contract,
        **ablation_artifacts,
    }


def build_all_claim_verification_artifacts(run_dir: Path) -> dict[str, Any]:
    paths = paths_for(run_dir)
    paper_text = ""
    paper_parse_path = paths.artifacts_dir / "paper_parse.md"
    if paper_parse_path.exists():
        paper_text = paper_parse_path.read_text(encoding="utf-8", errors="replace")
    claims = skillgen_all_claims(paper_text)
    if not (paths.artifacts_dir / "baseline_source_identity_review.json").exists():
        write_baseline_comparison_artifacts(run_dir)
    support = official_support_snapshot(run_dir)
    benchmark = read_artifact_json(paths, "benchmark_results.json", ["08_results"])

    matrix = []
    for claim in claims:
        claim_verdict_status, blockers, evidence = all_claim_status(claim, support, benchmark)
        execution_readiness_status = claim_execution_readiness_status(claim["id"], support, benchmark)
        validation_evidence, planning_evidence = split_claim_evidence(claim["id"], claim_verdict_status, evidence)
        external_candidates = supported_external_candidates(
            support,
            external_source_keys_for_claim(claim["id"], support),
        )
        matrix.append(
            {
                "claim_id": claim["id"],
                "claim_type": claim["claim_type"],
                "verification_mode": claim["verification_mode"],
                "status": claim_verdict_status,
                "claim_verdict_status": claim_verdict_status,
                "execution_readiness_status": execution_readiness_status,
                "blockers": blockers,
                "evidence": validation_evidence,
                "validation_evidence": validation_evidence,
                "planning_evidence": planning_evidence,
                "external_source_candidates": external_candidates,
                "next_step": next_step_for_claim(
                    claim_verdict_status,
                    claim["verification_mode"],
                    bool(external_candidates),
                    claim_id=claim["id"],
                    support=support,
                    readiness_status=execution_readiness_status,
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
        "schema_version": "0.3",
        "scope": "Claim-by-claim verification status and execution readiness for SkillGen",
        "status_model": {
            "status": "Backward-compatible alias for claim_verdict_status.",
            "claim_verdict_status": "Evidence verdict for the paper claim. Counts in status_counts are computed from this field only.",
            "execution_readiness_status": "Operational readiness for the next run or repair step. This is not a validation verdict.",
            "validation_evidence": "Executed benchmark, parsed result, or artifact-inspection evidence that can support reproduced/partially_reproduced/not_reproduced.",
            "planning_evidence": "Contracts, source reviews, split plans, or readiness artifacts. These can unblock execution but do not validate the claim by themselves.",
        },
        "status_counts": count_statuses(matrix, "claim_verdict_status"),
        "claim_verdict_status_counts": count_statuses(matrix, "claim_verdict_status"),
        "readiness_status_counts": count_statuses(matrix, "execution_readiness_status"),
        "official_support": support,
        "executable_targets": build_executable_target_inventory(support),
        "claims": matrix,
    }
    write_json(paths.artifacts_dir / "all_claims.json", payload)
    write_text(paths.artifacts_dir / "all_claims.md", render_all_claims_md(claims))
    write_json(paths.artifacts_dir / "all_claim_verification_matrix.json", matrix_payload)
    write_text(paths.artifacts_dir / "all_claim_verification_matrix.md", render_all_claim_matrix_md(matrix_payload))
    claims_dir = paths.artifacts_dir / "02_claims"
    if claims_dir.exists():
        write_json(claims_dir / "all_claims.json", payload)
        write_text(claims_dir / "all_claims.md", render_all_claims_md(claims))
        write_json(claims_dir / "all_claim_verification_matrix.json", matrix_payload)
        write_text(claims_dir / "all_claim_verification_matrix.md", render_all_claim_matrix_md(matrix_payload))
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
    long_inference = long_inference_approved(run_dir)
    intake_task_count: int | None = None
    execution_target_counts: dict[str, int] | None = None
    all_claim_status_counts: dict[str, int] | None = None
    all_claim_readiness_status_counts: dict[str, int] | None = None
    baseline_comparison_status: str | None = None
    existing_all_claims: dict[str, Any] = {}
    if long_inference:
        write_automation_hardcoding_disclosures(run_dir)
        intake_plan = write_external_source_intake_artifacts(run_dir)
        execution_plans = write_execution_planning_artifacts(run_dir)
        baseline_artifacts = write_baseline_comparison_artifacts(run_dir)
        all_claims = build_all_claim_verification_artifacts(run_dir)
        intake_task_count = len(intake_plan["tasks"])
        execution_target_counts = execution_plans["benchmark_execution_plan"]["status_counts"]
        all_claim_status_counts = all_claims["status_counts"]
        all_claim_readiness_status_counts = all_claims["readiness_status_counts"]
        baseline_comparison_status = baseline_artifacts["source_identity_review"]["status"]
    else:
        existing_all_claims = read_artifact_json(paths, "all_claim_verification_matrix.json", ["02_claims"])
        if existing_all_claims:
            all_claim_status_counts = existing_all_claims.get("claim_verdict_status_counts") or existing_all_claims.get("status_counts")
            all_claim_readiness_status_counts = existing_all_claims.get("readiness_status_counts")
    artifact_mode = "full" if long_inference else ("minimal_with_existing_all_claim_artifacts" if existing_all_claims else "minimal")
    automation_state = {
        "schema_version": "0.3",
        "status": "ready_for_approval" if code_manifest["status"] == "intake_complete" else "blocked_missing_official_code",
        "code_intake": code_manifest["status"],
        "smoke_assets": smoke_assets["status"],
        "contract": contract["target_id"],
        "command_plan": plan["status"],
        "artifact_mode": artifact_mode,
        LONG_INFERENCE_APPROVED_FIELD: long_inference,
        "status_model": {
            "all_claim_status_counts": "Backward-compatible alias for all_claim_verdict_status_counts.",
            "all_claim_verdict_status_counts": "Counts paper-claim validation verdicts only.",
            "all_claim_readiness_status_counts": "Counts next-step execution readiness only; not claim validation evidence.",
        },
        "minimal_artifact_policy": (
            "When long_inference_approved is false, the run writes only the "
            "core Phase 0 evidence artifacts needed for selected-claim validation."
        ),
        "all_claim_status_counts": all_claim_status_counts,
        "all_claim_verdict_status_counts": all_claim_status_counts,
        "all_claim_readiness_status_counts": all_claim_readiness_status_counts,
        "external_source_intake_task_count": intake_task_count,
        "benchmark_execution_target_counts": execution_target_counts,
        "baseline_comparison_status": baseline_comparison_status,
    }
    write_json_with_category_mirrors(paths, "automation_state.json", automation_state, ["00_run_summary"])
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
    approval_summary_path = paths.artifacts_dir / "00_run_summary" / "approval.json"
    if approval_path.exists():
        approval = read_json(approval_path)
    elif approval_summary_path.exists():
        approval = read_json(approval_summary_path)
    else:
        return False, ["missing artifacts/approval.json"]
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
    return read_artifact_json(paths_for(run_dir), "approval.json", ["00_run_summary"])


def long_inference_approved(run_dir: Path) -> bool:
    return bool(approval_policy(run_dir).get(LONG_INFERENCE_APPROVED_FIELD, False))


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
    long_inference_approved: bool = False,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    approval = {
        "schema_version": "0.3",
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
        LONG_INFERENCE_APPROVED_FIELD: long_inference_approved,
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
        f"- Long inference approved: `{long_inference_approved}`\n"
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


def model_slug(model_route: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", model_route).strip("_")


def full_matrix_dir(paths: RunPaths) -> Path:
    return paths.artifacts_dir / "08_results" / "full_matrix"


def full_matrix_raw_entry_dir(paths: RunPaths, target_id: str, slug: str) -> Path:
    return paths.artifacts_dir / "08_results" / "raw_benchmark_outputs" / "full_matrix" / target_id / slug


def find_artifact_path(paths: RunPaths, filename: str, categories: list[str] | None = None) -> Path | None:
    for candidate in [paths.artifacts_dir / filename, *[paths.artifacts_dir / category / filename for category in (categories or [])]]:
        if candidate.exists():
            return candidate
    return None


def format_command_template(value: Any, values: dict[str, str]) -> Any:
    if isinstance(value, str):
        return value.format(**values)
    if isinstance(value, list):
        return [format_command_template(item, values) for item in value]
    if isinstance(value, dict):
        return {key: format_command_template(item, values) for key, item in value.items()}
    return value


def write_full_matrix_entry_config(
    run_dir: Path,
    target_id: str,
    model_route: str,
    judge_model_route: str,
    *,
    max_refine_rounds: int,
    max_workers: int,
    verification_sample_size: int,
    force: bool = False,
) -> dict[str, str]:
    paths = paths_for(run_dir)
    slug = model_slug(model_route)
    root_rel = f"../../artifacts/08_results/raw_benchmark_outputs/full_matrix/{target_id}/{slug}"
    body = f"""# SkillGen Phase 0 full-matrix runner config.
# Reconstructed/deviation-controlled config generated per entry.
models:
  default: "{judge_model_route}"
  baseline_agent: "{model_route}"
  baseline_judge: "{judge_model_route}"
  induction: "{judge_model_route}"
  induction_contextual: "{judge_model_route}"
  induction_summary: "{judge_model_route}"
  induction_pattern: "{judge_model_route}"
  induction_contrastive: "{judge_model_route}"
  generation_plan: "{judge_model_route}"
  generation_execute: "{judge_model_route}"
  refinement: "{judge_model_route}"
  verification_agent: "{model_route}"
  verification_judge: "{judge_model_route}"
  verification_case_analyst: "{judge_model_route}"
  verification_revision_synthesiser: "{judge_model_route}"

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
  candidate_output_dir: "{root_rel}/candidates"
  generate_scripts: false
  max_failure_clusters_in_prompt: 2
  max_success_clusters_in_prompt: 2
  max_contrastive_pairs_in_prompt: 4

verification_analysis:
  case_analyst_workers: 1
  case_analyst_max_tokens: 1024
  revision_synthesiser_max_tokens: 2048

verification:
  sample_size: {verification_sample_size}
  min_sample: 2
  seed: 42
  min_net_gain_abs: 1
  min_net_gain_rel: 0.0

router:
  enabled: false
  model: "{judge_model_route}"
  max_workers: {max_workers}

pipeline:
  max_refine_rounds: {max_refine_rounds}
  baseline_runs_per_instance: 1
  max_workers: {max_workers}
  artifact_root: "{root_rel}/artifacts/runs"

skill_output:
  path: "{root_rel}/skill_output"
"""
    primary = paths.artifacts_dir / "generated_configs" / target_id / f"{slug}.yaml"
    mirror = paths.artifacts_dir / "07_configs_and_inputs" / "generated_configs" / target_id / f"{slug}.yaml"
    for config_path in [primary, mirror]:
        if force or not config_path.exists():
            write_text(config_path, body)
    return {
        "config": rel(primary, paths.run_dir),
        "config_mirror": rel(mirror, paths.run_dir),
        "config_for_official_workdir": rel(primary, paths.official_dir),
    }


def full_matrix_reconstructed_labels(table1_row: str, provider_route_id: str, direct_openai_fallback: bool) -> list[str]:
    labels: list[str] = []
    if table1_row in {"alfworld_iod", "alfworld_ood"}:
        labels.append("canonical ALFWorld data + reconstructed SkillGen offline-plan adapter")
    if table1_row == "livecodebench":
        labels.append("reconstructed_livecodebench_split")
    if direct_openai_fallback and provider_route_id.startswith("openai/"):
        labels.append("direct_openai_provider_fallback")
    return labels


def full_matrix_evidence_class(labels: list[str]) -> str:
    return "reconstructed_evidence" if labels else "official_code_execution_evidence"


def full_matrix_deviation_label(labels: list[str]) -> str:
    return "; ".join(labels) if labels else "none"


def full_matrix_entry_verdict(entry: dict[str, Any]) -> tuple[str, str]:
    train = entry.get("construction_verification") or {}
    held_out = entry.get("held_out_eval") or {}
    if entry.get("execution_status") == STATUS_FAILED_TO_RUN:
        return STATUS_FAILED_TO_RUN, "The full-matrix entry command failed before complete held-out evidence was parsed."
    if train and train.get("passed") is False:
        return STATUS_NOT_REPRODUCED, "Construction-time verification failed, so the generated skill did not pass SkillGen's gate."
    if entry.get("skill_rejected"):
        return STATUS_NOT_REPRODUCED, "Official code marked the generated skill as rejected or deprecated."
    baseline_acc = held_out.get("baseline_acc")
    skill_acc = held_out.get("skill_acc")
    net_gain = held_out.get("net_gain")
    if isinstance(baseline_acc, (int, float)) and isinstance(skill_acc, (int, float)):
        if skill_acc > baseline_acc and isinstance(net_gain, int) and net_gain > 0:
            return STATUS_PARTIALLY_REPRODUCED, "The reconstructed/entry-level run showed a positive held-out skill delta."
        return STATUS_NOT_REPRODUCED, "Held-out evaluation did not show skill_acc > baseline_acc with positive net gain."
    return STATUS_NOT_TESTABLE, "Held-out eval_results.json is missing or does not contain comparable accuracy fields."


def observed_full_matrix_entry_index(paths: RunPaths) -> dict[str, dict[str, Any]]:
    path = full_matrix_dir(paths) / "observed_entries.json"
    if not path.exists():
        return {}
    payload = read_json(path)
    return {entry["entry_id"]: entry for entry in payload.get("entries", []) if entry.get("entry_id")}


def full_matrix_entry_evidence_validation(
    run_dir: Path,
    entry: dict[str, Any],
    target: dict[str, Any],
    config_rel: str | None,
    labels: list[str],
    observed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    route = entry.get("provider_route_id") or ""
    slug = entry.get("model_slug") or model_slug(route)
    target_id = entry.get("table1_row") or entry.get("target_id")
    root = full_matrix_raw_entry_dir(paths, target_id, slug)
    observed = observed or observed_full_matrix_entry_index(paths).get(entry.get("entry_id"), {})

    def exists_glob(pattern: str) -> bool:
        return bool(list(root.rglob(pattern))) if root.exists() else False

    eval_path = root / "eval_results.json"
    eval_parseable = False
    if eval_path.exists():
        try:
            eval_data = read_json(eval_path)
            eval_parseable = isinstance(eval_data, dict) and isinstance(eval_data.get("results"), list)
        except (OSError, json.JSONDecodeError):
            eval_parseable = False
    config_path = paths.run_dir / config_rel if config_rel else None
    verification_round_dirs = list((root / "artifacts" / "runs").glob("*/verification/round_*")) if (root / "artifacts" / "runs").exists() else []
    complete_round_trace = any(
        (round_dir / "verification_baseline.jsonl").exists()
        and (round_dir / "verification_with_skill.jsonl").exists()
        and (round_dir / "verification_summary.json").exists()
        and (round_dir / "verification_case_analyses.json").exists()
        for round_dir in verification_round_dirs
    )
    observed_labels = set(observed.get("reconstruction_disclosures") or [])
    required_labels = set(labels)
    checks = {
        "train_stdout_saved": exists_glob("*train*stdout*.txt"),
        "train_stderr_saved": exists_glob("*train*stderr*.txt"),
        "eval_stdout_saved": exists_glob("*eval*stdout*.txt"),
        "eval_stderr_saved": exists_glob("*eval*stderr*.txt"),
        "eval_results_exists": eval_path.exists(),
        "eval_results_parseable": eval_parseable,
        "eval_token_usage_exists": (root / "eval_results.token_usage.json").exists(),
        "eval_trajectories_exists": (root / "eval_results_trajectories").exists(),
        "training_run_artifacts_exist": (root / "artifacts" / "runs").exists() and any((root / "artifacts" / "runs").iterdir()),
        "verification_round_traces_exist": complete_round_trace,
        "config_path_recorded": bool(config_rel),
        "config_path_exists": bool(config_path and config_path.exists()),
        "provider_route_recorded": bool(route),
        "deviation_labels_recorded": required_labels.issubset(observed_labels) if required_labels else True,
        "entry_verdict_recorded": bool(observed.get("entry_verdict")),
        "entry_verdict_uses_executed_evidence": bool(observed.get("entry_verdict")) and eval_parseable,
    }
    missing = [key for key, value in checks.items() if not value]
    return {
        "status": "completed_valid_evidence" if not missing else "completed_invalid_evidence",
        "checks": checks,
        "missing": missing,
        "entry_root": rel(root, paths.run_dir),
    }


def parse_full_matrix_observed_entry(
    run_dir: Path,
    entry_plan: dict[str, Any],
    target: dict[str, Any],
    config_rel: str,
    labels: list[str],
    execution_status: str,
    command_records: list[dict[str, Any]],
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    route = entry_plan["provider_route_id"]
    slug = model_slug(route)
    target_id = entry_plan["table1_row"]
    root = full_matrix_raw_entry_dir(paths, target_id, slug)
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
    train_dataset = (target.get("dataset") or {}).get("train")
    test_dataset = (target.get("dataset") or {}).get("test")
    observed = {
        "entry_id": entry_plan["entry_id"],
        "table1_row": target_id,
        "paper_model_display_name": entry_plan["paper_model"],
        "provider_route_id": route,
        "route_execution_mode": "direct_openai_for_openai_models" if "direct_openai_provider_fallback" in labels else "provider_route",
        "evidence_class": full_matrix_evidence_class(labels),
        "reconstruction_disclosures": labels,
        "deviation_label": full_matrix_deviation_label(labels),
        "deviation_labels": labels,
        "train_dataset": f"code/official/{train_dataset}" if train_dataset else None,
        "test_dataset": f"code/official/{test_dataset}" if test_dataset else None,
        "train_n": (target.get("dataset") or {}).get("train_n"),
        "test_n": (target.get("dataset") or {}).get("test_n"),
        "config": config_rel,
        "config_deviation": "Per-entry generated config with explicit max_refine_rounds, max_workers, and verification sample limit.",
        "skill_id": skill_id,
        "skill_status": skill_record.get("status") or eval_data.get("skill_status"),
        "skill_rejected": bool(eval_data.get("skill_rejected")) or str(skill_record.get("status", "")).lower() == "deprecated",
        "execution_status": execution_status,
        "commands": command_records,
        "construction_verification": {
            "paired_n": verification_result.get("paired_n"),
            "baseline_acc": verification_result.get("baseline_acc"),
            "skill_acc": verification_result.get("skill_acc"),
            "delta_acc": (
                verification_result.get("skill_acc") - verification_result.get("baseline_acc")
                if isinstance(verification_result.get("skill_acc"), (int, float))
                and isinstance(verification_result.get("baseline_acc"), (int, float))
                else None
            ),
            "repair": verification_result.get("repair_count"),
            "regression": verification_result.get("regression_count"),
            "net_gain": verification_result.get("net_gain"),
            "passed": verification_result.get("passed"),
        },
        "held_out_eval": {
            "n_instances": first_eval.get("n_instances"),
            "baseline_acc": first_eval.get("baseline_acc"),
            "skill_acc": first_eval.get("skill_acc"),
            "delta_acc": first_eval.get("delta_acc"),
            "repair": first_eval.get("repair"),
            "regression": first_eval.get("regression"),
            "net_gain": first_eval.get("net_gain"),
            "blank_filter": first_eval.get("blank_filter"),
        },
        "paper_claim_impact": {
            "claim_table1_average_gains_all_models": "still_blocked_incomplete_matrix",
            "claim_table1_entry_counts": "still_blocked_incomplete_matrix",
        },
        "raw_outputs": {
            "entry_root": rel(root, paths.run_dir),
            "skill_output": rel(skill_output_dir, paths.run_dir) if skill_output_dir else None,
            "run_artifacts": rel(artifact_run, paths.run_dir) if artifact_run else None,
            "eval_results": rel(eval_path, paths.run_dir) if eval_path.exists() else None,
            "eval_token_usage": rel(root / "eval_results.token_usage.json", paths.run_dir) if (root / "eval_results.token_usage.json").exists() else None,
            "eval_trajectories": rel(root / "eval_results_trajectories", paths.run_dir) if (root / "eval_results_trajectories").exists() else None,
            "verification_summary": rel(verification_summary_path, paths.run_dir) if verification_summary_path else None,
        },
        "token_usage_total": {
            "training": train_token_usage,
            "held_out_eval": eval_token_usage,
            "combined": (train_token_usage or 0) + (eval_token_usage or 0) if train_token_usage or eval_token_usage else None,
        },
    }
    verdict, reason = full_matrix_entry_verdict(observed)
    observed["entry_verdict"] = verdict
    observed["entry_verdict_reason"] = reason
    if labels:
        observed["strongest_allowed_positive_status"] = STATUS_PARTIALLY_REPRODUCED
    observed["post_run_evidence_validation"] = full_matrix_entry_evidence_validation(
        run_dir,
        entry_plan,
        target,
        config_rel,
        labels,
        observed,
    )
    return observed


def render_observed_full_matrix_entries_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Observed Full-Matrix Entries",
        "",
        payload["scope"],
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Entry Counts",
        "",
    ]
    for key, value in payload.get("entry_counts", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Entries", ""])
    if not payload.get("entries"):
        lines.append("- No full-matrix entries have completed yet.")
    for entry in payload.get("entries", []):
        lines.extend(
            [
                f"### {entry['entry_id']}",
                "",
                f"- Verdict: `{entry.get('entry_verdict')}`",
                f"- Evidence class: `{entry.get('evidence_class')}`",
                f"- Route: `{entry.get('provider_route_id')}`",
                f"- Reconstruction disclosures: `{', '.join(entry.get('reconstruction_disclosures') or []) or 'none'}`",
                f"- Held-out delta: `{percent((entry.get('held_out_eval') or {}).get('delta_acc'))}`",
                f"- Raw entry root: `{(entry.get('raw_outputs') or {}).get('entry_root')}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_observed_full_matrix_entry(run_dir: Path, observed: dict[str, Any], paper_required: int) -> dict[str, Any]:
    paths = paths_for(run_dir)
    output_dir = full_matrix_dir(paths)
    output_path = output_dir / "observed_entries.json"
    existing = read_json(output_path) if output_path.exists() else {}
    entries = existing.get("entries", [])
    by_id = {entry["entry_id"]: entry for entry in entries if entry.get("entry_id")}
    by_id[observed["entry_id"]] = observed
    merged_entries = list(by_id.values())
    counts = {
        "paper_required": paper_required,
        "observed": len(merged_entries),
        "observed_not_reproduced": sum(1 for entry in merged_entries if entry.get("entry_verdict") == STATUS_NOT_REPRODUCED),
        "observed_partially_reproduced": sum(1 for entry in merged_entries if entry.get("entry_verdict") == STATUS_PARTIALLY_REPRODUCED),
        "observed_failed_to_run": sum(1 for entry in merged_entries if entry.get("entry_verdict") == STATUS_FAILED_TO_RUN),
        "remaining": max(paper_required - len(merged_entries), 0),
    }
    payload = {
        "schema_version": "0.2",
        "scope": "Observed SkillGen Table 1 full-matrix entries executed by the resumable full-matrix runner.",
        "status": "incomplete_full_matrix_observed" if len(merged_entries) < paper_required else "full_matrix_observed",
        "important_limitations": [
            "This artifact records executed entries only; it is not a complete Table 1 reproduction until all 80 entries are present.",
            "Entries with reconstructed disclosures can support positive evidence only up to partially_reproduced.",
            "Negative reconstructed evidence can still support an entry-level not_reproduced verdict.",
        ],
        "entries": sorted(merged_entries, key=lambda entry: entry["entry_id"]),
        "entry_counts": counts,
    }
    write_json(output_path, payload)
    write_text(output_dir / "observed_entries.md", render_observed_full_matrix_entries_md(payload))
    return payload


def full_matrix_artifact_inputs(paths: RunPaths) -> dict[str, Any]:
    benchmark_plan_path = find_artifact_path(paths, "benchmark_execution_plan.json", ["06_plans_and_contracts"])
    contract_path = find_artifact_path(paths, "full_matrix_execution_contract.json", ["06_plans_and_contracts"])
    reconstructed_index_path = find_artifact_path(paths, "reconstructed_validation_path_index.md", ["09_safety_and_deviations"])
    provider_resolution_path = find_artifact_path(paths, "provider_resolution_status.json", ["06_plans_and_contracts"])
    if benchmark_plan_path is None:
        raise FileNotFoundError("Missing benchmark_execution_plan.json")
    if contract_path is None:
        raise FileNotFoundError("Missing full_matrix_execution_contract.json")
    return {
        "benchmark_execution_plan_path": benchmark_plan_path,
        "benchmark_execution_plan": read_json(benchmark_plan_path),
        "full_matrix_execution_contract_path": contract_path,
        "full_matrix_execution_contract": read_json(contract_path),
        "reconstructed_validation_path_index_path": reconstructed_index_path,
        "reconstructed_validation_path_index_present": reconstructed_index_path is not None,
        "provider_resolution_status_path": provider_resolution_path,
        "provider_resolution_status": read_json(provider_resolution_path) if provider_resolution_path else {},
    }


def full_matrix_target_map(benchmark_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {target["target_id"]: target for target in benchmark_plan.get("targets", [])}


def full_matrix_entry_dataset_ready(target: dict[str, Any]) -> bool:
    dataset = target.get("dataset") or {}
    return bool(dataset.get("train_exists") and dataset.get("test_exists"))


def full_matrix_entry_candidates(
    run_dir: Path,
    *,
    include_non_openai: bool,
    direct_openai_fallback: bool,
    allow_openrouter_after_402: bool,
    target_subset: set[str] | None = None,
    model_subset: set[str] | None = None,
) -> list[dict[str, Any]]:
    paths = paths_for(run_dir)
    provider_resolution = write_provider_resolution_status(
        run_dir,
        include_non_openai=include_non_openai,
        direct_openai_fallback=direct_openai_fallback,
        allow_openrouter_after_402=allow_openrouter_after_402,
    )
    provider_by_route = {
        row.get("provider_route_id"): row
        for row in provider_resolution.get("routes", [])
        if row.get("provider_route_id")
    }
    inputs = full_matrix_artifact_inputs(paths)
    benchmark_plan = inputs["benchmark_execution_plan"]
    contract = inputs["full_matrix_execution_contract"]
    targets = full_matrix_target_map(benchmark_plan)
    observed_index = observed_full_matrix_entry_index(paths)
    rows = []
    for entry in contract.get("execution_entries", []):
        route = entry.get("provider_route_id") or ""
        target_id = entry.get("table1_row", "")
        target = targets.get(entry.get("table1_row"), {})
        slug = model_slug(route)
        labels = full_matrix_reconstructed_labels(target_id, route, direct_openai_fallback)
        eval_path = full_matrix_raw_entry_dir(paths, target_id, slug) / "eval_results.json"
        provider_row = provider_by_route.get(route, {})
        status = "not_started"
        reason = (
            provider_row.get("reason")
            if not route.startswith("openai/") and provider_row.get("runner_status") == "candidate_ready"
            else "Entry is ready for execution."
        )
        selectable = True
        subset_excluded = False
        evidence_validation = None
        if target_subset and target_id not in target_subset:
            selectable = False
            subset_excluded = True
            reason = "Entry is outside the requested target subset."
        elif model_subset and entry.get("paper_model") not in model_subset and route not in model_subset:
            selectable = False
            subset_excluded = True
            reason = "Entry is outside the requested model subset."
        elif not route.startswith("openai/") and provider_row.get("runner_status") == STATUS_PROVIDER_UNAVAILABLE:
            status = STATUS_PROVIDER_UNAVAILABLE
            selectable = False
            reason = provider_row.get("reason") or "Provider route is unavailable in the current execution environment."
        elif not route.startswith("openai/") and not include_non_openai:
            status = STATUS_WAITING_PROVIDER_ROUTE_RESOLUTION
            selectable = False
            reason = provider_row.get("reason") or "Non-OpenAI provider routes still require a technically working route; this is not a human-approval blocker."
        elif target.get("status") not in {STATUS_READY_FOR_EXECUTION, STATUS_READY_FOR_RECONSTRUCTED_EXECUTION}:
            selectable = False
            reason = f"Target status is {target.get('status')}."
        elif not full_matrix_entry_dataset_ready(target):
            selectable = False
            reason = "Train/test dataset files are not present under code/official."
        elif eval_path.exists():
            observed = observed_index.get(entry.get("entry_id"), {})
            config_rel = observed.get("config")
            if not config_rel:
                default_config = paths.artifacts_dir / "generated_configs" / target_id / f"{slug}.yaml"
                config_rel = rel(default_config, paths.run_dir) if default_config.exists() else None
            evidence_validation = full_matrix_entry_evidence_validation(
                run_dir,
                {**entry, "model_slug": slug, "reconstruction_disclosures": labels},
                target,
                config_rel,
                labels,
                observed,
            )
            status = evidence_validation["status"]
            selectable = False
            reason = "Existing eval_results.json found; resume will not overwrite it."
        rows.append(
            {
                **entry,
                "target_status": target.get("status"),
                "dataset": target.get("dataset", {}),
                "model_slug": slug,
                "route_is_openai": route.startswith("openai/"),
                "provider_execution_status": provider_row.get("execution_status"),
                "provider_runner_status": provider_row.get("runner_status"),
                "evidence_class": full_matrix_evidence_class(labels),
                "reconstruction_disclosures": labels,
                "deviation_label": full_matrix_deviation_label(labels),
                "deviation_labels": labels,
                "runner_status": status,
                "runner_reason": reason,
                "runner_selectable": selectable,
                "subset_excluded": subset_excluded,
                "post_run_evidence_validation": evidence_validation,
                "entry_root": rel(full_matrix_raw_entry_dir(paths, target_id, slug), paths.run_dir),
            }
        )
    openai_priority = {
        "openai/gpt-5.4-nano": 0,
        "openai/gpt-5.4-mini": 1,
        "openai/gpt-oss-20b": 2,
    }
    return sorted(
        rows,
        key=lambda row: (
            not row["route_is_openai"],
            TABLE1_REQUIRED_ROWS.index(row["table1_row"]) if row.get("table1_row") in TABLE1_REQUIRED_ROWS else 999,
            openai_priority.get(row.get("provider_route_id"), 100),
            row.get("paper_model", ""),
        ),
    )


def execute_full_matrix_entry(
    run_dir: Path,
    entry: dict[str, Any],
    target: dict[str, Any],
    *,
    judge_model_route: str,
    max_workers: int,
    max_refine_rounds: int,
    verification_sample_size: int,
    max_eval_instances: int | None,
    direct_openai_fallback: bool,
    dry_run: bool,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    route = entry["provider_route_id"]
    slug = entry["model_slug"]
    target_id = entry["table1_row"]
    root = full_matrix_raw_entry_dir(paths, target_id, slug)
    root.mkdir(parents=True, exist_ok=True)
    config = write_full_matrix_entry_config(
        run_dir,
        target_id,
        route,
        judge_model_route,
        max_refine_rounds=max_refine_rounds,
        max_workers=max_workers,
        verification_sample_size=verification_sample_size,
    )
    if dry_run:
        return {
            "entry_id": entry["entry_id"],
            "status": "not_started",
            "dry_run_planned": True,
            "config": config,
            "commands": [],
        }

    attempt_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    attempt_dir = root / "runner_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        root / "entry_status.json",
        {
            "entry_id": entry["entry_id"],
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "config": config,
            "provider_route_id": route,
            "deviation_label": full_matrix_deviation_label(entry["reconstruction_disclosures"]),
            "deviation_labels": entry["reconstruction_disclosures"],
        },
    )
    command_values = {
        "config_path": config["config_for_official_workdir"],
        "model_slug": slug,
        "model_route": route,
        "judge_model_route": judge_model_route,
        "max_workers": str(max_workers),
    }
    command_env_values = {"PYTHONUNBUFFERED": "1"}
    if direct_openai_fallback and route.startswith("openai/"):
        command_env_values["SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS"] = "1"

    commands_run: list[dict[str, Any]] = []
    skill_output_dir = latest_dir(root / "skill_output")
    if skill_output_dir is None:
        train_template = (target.get("runner_contract") or {}).get("train_command_template")
        if not train_template:
            result = {"entry_id": entry["entry_id"], "status": "failed_to_run", "reason": "missing train command template", "config": config, "commands": []}
            write_json(root / "entry_status.json", result)
            return result
        train_command = format_command_template(train_template, command_values)
        train_command["env"] = {**train_command.get("env", {}), **command_env_values}
        train_record = run_command_with_retries(
            run_dir,
            train_command,
            attempt_dir / "train_stdout.txt",
            attempt_dir / "train_stderr.txt",
        )
        commands_run.append({"phase": "train", **train_record})
        if train_record["exit_code"] != 0:
            observed = parse_full_matrix_observed_entry(
                run_dir,
                entry,
                target,
                config["config"],
                entry["reconstruction_disclosures"],
                "failed_to_run",
                commands_run,
            )
            result = {"entry_id": entry["entry_id"], "status": "failed_to_run", "observed_entry": observed, "commands": commands_run}
            write_json(root / "entry_status.json", result)
            return result
        skill_output_dir = latest_dir(root / "skill_output")

    if skill_output_dir is None:
        result = {"entry_id": entry["entry_id"], "status": "failed_to_run", "reason": "missing skill output after train", "config": config, "commands": commands_run}
        write_json(root / "entry_status.json", result)
        return result

    eval_template = (target.get("runner_contract") or {}).get("eval_command_template")
    if not eval_template:
        result = {"entry_id": entry["entry_id"], "status": "failed_to_run", "reason": "missing eval command template", "config": config, "commands": commands_run}
        write_json(root / "entry_status.json", result)
        return result
    command_values["skill_output_dir"] = rel(skill_output_dir, paths.official_dir)
    eval_command = format_command_template(eval_template, command_values)
    argv = list(eval_command["argv"])
    if max_eval_instances is not None and "--n" in argv:
        argv[argv.index("--n") + 1] = str(max_eval_instances)
    if "--output" in argv:
        argv[argv.index("--output") + 1] = rel(root / "eval_results.json", paths.official_dir)
    eval_command["argv"] = argv
    eval_command["env"] = {**eval_command.get("env", {}), **command_env_values}
    eval_record = run_command_with_retries(
        run_dir,
        eval_command,
        attempt_dir / "eval_stdout.txt",
        attempt_dir / "eval_stderr.txt",
    )
    commands_run.append({"phase": "eval", **eval_record})
    execution_status = "entry_execution_completed" if eval_record["exit_code"] == 0 else "failed_to_run"
    observed = parse_full_matrix_observed_entry(
        run_dir,
        entry,
        target,
        config["config"],
        entry["reconstruction_disclosures"],
        execution_status,
        commands_run,
    )
    status = "failed_to_run" if eval_record["exit_code"] != 0 else observed["post_run_evidence_validation"]["status"]
    result = {"entry_id": entry["entry_id"], "status": status, "observed_entry": observed, "commands": commands_run}
    write_json(root / "entry_status.json", result)
    return result


def run_full_matrix_entries(
    run_dir: Path,
    *,
    max_entries: int | None = None,
    include_non_openai: bool = False,
    direct_openai_fallback: bool = True,
    allow_openrouter_after_402: bool = False,
    dry_run: bool = False,
    judge_model_route: str = "openai/gpt-5.4-mini",
    max_workers: int = 1,
    max_refine_rounds: int = 1,
    verification_sample_size: int = 4,
    max_eval_instances: int | None = None,
    target_subset: set[str] | None = None,
    model_subset: set[str] | None = None,
) -> dict[str, Any]:
    paths = paths_for(run_dir)
    provider_resolution = write_provider_resolution_status(
        run_dir,
        include_non_openai=include_non_openai,
        direct_openai_fallback=direct_openai_fallback,
        allow_openrouter_after_402=allow_openrouter_after_402,
    )
    inputs = full_matrix_artifact_inputs(paths)
    targets = full_matrix_target_map(inputs["benchmark_execution_plan"])
    entries = full_matrix_entry_candidates(
        run_dir,
        include_non_openai=include_non_openai,
        direct_openai_fallback=direct_openai_fallback,
        allow_openrouter_after_402=allow_openrouter_after_402,
        target_subset=target_subset,
        model_subset=model_subset,
    )
    executable = [entry for entry in entries if entry["runner_status"] == "not_started" and entry.get("runner_selectable")]
    selected = executable[:max_entries] if max_entries is not None else executable
    results = []
    paper_required = (inputs["full_matrix_execution_contract"].get("entry_count") or {}).get("paper_required", 80)
    for entry in selected:
        result = execute_full_matrix_entry(
            run_dir,
            entry,
            targets[entry["table1_row"]],
            judge_model_route=judge_model_route,
            max_workers=max_workers,
            max_refine_rounds=max_refine_rounds,
            verification_sample_size=verification_sample_size,
            max_eval_instances=max_eval_instances,
            direct_openai_fallback=direct_openai_fallback,
            dry_run=dry_run,
        )
        results.append(result)
        if result.get("observed_entry"):
            write_observed_full_matrix_entry(run_dir, result["observed_entry"], paper_required)
        append_event(run_dir, "full_matrix_entry_execution", result["status"], entry_id=entry["entry_id"])

    state_entries = []
    selected_ids = {entry["entry_id"] for entry in selected}
    result_by_id = {result["entry_id"]: result for result in results}
    for entry in entries:
        state = dict(entry)
        if entry["entry_id"] in result_by_id:
            state["runner_status"] = result_by_id[entry["entry_id"]]["status"]
            if result_by_id[entry["entry_id"]].get("dry_run_planned"):
                state["dry_run_planned"] = True
        elif (
            max_entries is not None
            and entry.get("runner_selectable")
            and entry["runner_status"] == "not_started"
            and entry["entry_id"] not in selected_ids
        ):
            state["runner_status"] = "budget_stopped"
            state["runner_reason"] = "Entry is technically executable but outside this invocation's max-entry limit."
        state_entries.append(state)
    counts = count_statuses([{"status": row["runner_status"]} for row in state_entries])
    state = {
        "schema_version": "0.1",
        "status": "dry_run_completed" if dry_run else "runner_completed",
        "run_dir": paths.run_dir.name,
        "source_artifacts": {
            "benchmark_execution_plan": rel(inputs["benchmark_execution_plan_path"], paths.run_dir),
            "full_matrix_execution_contract": rel(inputs["full_matrix_execution_contract_path"], paths.run_dir),
            "reconstructed_validation_path_index": rel(inputs["reconstructed_validation_path_index_path"], paths.run_dir)
            if inputs["reconstructed_validation_path_index_path"]
            else None,
            "provider_resolution_status": rel(inputs["provider_resolution_status_path"], paths.run_dir)
            if inputs["provider_resolution_status_path"]
            else None,
        },
        "policy": {
            "openai_routes_first": True,
            "include_non_openai": include_non_openai,
            "direct_openai_fallback": direct_openai_fallback,
            "allow_openrouter_after_402": allow_openrouter_after_402,
            "max_entries": max_entries,
            "dry_run": dry_run,
            "judge_model_route": judge_model_route,
            "max_workers": max_workers,
            "max_refine_rounds": max_refine_rounds,
            "verification_sample_size": verification_sample_size,
            "max_eval_instances": max_eval_instances,
            "target_subset": sorted(target_subset) if target_subset else None,
            "model_subset": sorted(model_subset) if model_subset else None,
        },
        "provider_resolution_status": provider_resolution.get("status"),
        "provider_summary": provider_resolution.get("provider_summary"),
        "counts": counts,
        "selected_entry_ids": [entry["entry_id"] for entry in selected],
        "results": results,
        "entries": state_entries,
    }
    output_dir = full_matrix_dir(paths)
    write_json(output_dir / "full_matrix_runner_state.json", state)
    write_text(output_dir / "full_matrix_runner_state.md", render_full_matrix_runner_state_md(state))
    append_event(run_dir, "full_matrix_runner", state["status"], artifact="artifacts/08_results/full_matrix/full_matrix_runner_state.json")
    return state


def render_full_matrix_runner_state_md(state: dict[str, Any]) -> str:
    lines = [
        "# Full Matrix Runner State",
        "",
        f"Status: `{state['status']}`",
        "",
        "## Policy",
        "",
    ]
    for key, value in state.get("policy", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    if state.get("provider_resolution_status"):
        lines.extend(["", "## Provider Resolution", "", f"- `status`: `{state.get('provider_resolution_status')}`"])
        for key, value in (state.get("provider_summary") or {}).items():
            lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Counts", ""])
    for status, count in sorted((state.get("counts") or {}).items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "## Selected Entries", ""])
    if state.get("selected_entry_ids"):
        lines.extend(f"- `{entry_id}`" for entry_id in state["selected_entry_ids"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Provider Unavailable", ""])
    unavailable = [entry for entry in state.get("entries", []) if entry.get("runner_status") == "provider_unavailable"]
    if unavailable:
        lines.extend(f"- `{entry['entry_id']}` via `{entry.get('provider_route_id')}`" for entry in unavailable)
    else:
        lines.append("- None.")
    return "\n".join(lines).rstrip() + "\n"


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
        write_json_with_category_mirrors(paths, "benchmark_results.json", result, ["08_results"])
        write_text_with_category_mirrors(
            paths,
            "benchmark_results.md",
            "# Benchmark Results\n\nStatus: `not_testable`\n\nMissing `eval_results.json`.\n",
            ["08_results"],
        )
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
    write_json_with_category_mirrors(paths, "benchmark_results.json", result, ["08_results"])
    write_text_with_category_mirrors(paths, "benchmark_results.md", render_benchmark_results_md(result), ["08_results"])
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
    write_json_with_category_mirrors(paths, "claim_comparison.json", comparison, ["08_results"])
    write_text_with_category_mirrors(paths, "claim_comparison.md", render_comparison_md(comparison), ["08_results"])
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
            "Paper Figure 3 ablation claim vs official ablation scripts plus the Group E reconstructed "
            "A1-A5 contract/config/deviation package."
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
    claim_verdict_status = row.get("claim_verdict_status", row.get("status"))
    readiness_status = row.get("execution_readiness_status")
    baseline_status = readiness_status
    if baseline_status == STATUS_READY_FOR_RECONSTRUCTED_BASELINE_COMPARISON:
        baseline_reason = (
            "Blocked pending execution: public baseline sources are pinned and human-approved, "
            "and the single-Markdown-skill adapter contract is ready, but Figure 2 comparison has not been run."
        )
    elif baseline_status == STATUS_READY_FOR_SOURCE_IDENTITY_REVIEW:
        blockers = row.get("blockers") or []
        all_sources_pinned = not any("still needing source intake or commit/license review" in blocker for blocker in blockers)
        if all_sources_pinned:
            trace2skill_license_clause = (
                " Trace2Skill still lacks top-level local license evidence."
                if any("Trace2Skill" in blocker and "license" in blocker.lower() for blocker in blockers)
                else ""
            )
            baseline_reason = (
                "Blocked pending human source identity review: all four public baseline repositories are cloned and pinned, "
                "but the human identity review artifact is not approved."
                + trace2skill_license_clause
            )
        else:
            baseline_reason = (
                "Blocked pending baseline source identity review: Group D artifacts identify public baseline candidates "
                "and the single-skill adapter contract, but commits, local licenses, and human identity approval are not complete."
            )
    else:
        baseline_reason = (
            "Blocked: the official checkout does not include executable Trace2Skill, SkillX, EvoSkill, "
            "or CoEvoSkills comparison runners, and the reconstructed source-identity path is not complete."
        )
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
            baseline_reason
        ),
        "claim_ablation_full_wins": (
            "Blocked pending reconstructed smoke execution: Group E defines A1-A5 behavior, config/patch paths, expected outputs, "
            "and deviation notes, but no ablation smoke result has been run or parsed. This is not exact Figure 3 reproduction until author-original configs are found."
            if readiness_status == STATUS_READY_FOR_RECONSTRUCTED_ABLATION_HUMAN_REVIEW
            else "Blocked: the official checkout does not include an ablation runner or named ablated configurations for Figure 3, and the reconstructed contract is not ready."
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
            else "Blocked pending execution: tau-Bench source/data preparation is done and no structural blocker remains, but the claim has not been executed and compared yet."
        ),
        "claim_chemllmbench_useful_gains": (
            f"ChemLLMBench execution summary: {chem_reason}."
            if chem_targets
            else "Blocked pending execution: ChemLLMBench source/data preparation is done and no structural blocker remains, but the claim has not been executed and compared yet."
        ),
        "claim_refinement_best_of_k": (
            "Blocked: the smoke run has construction verification traces, but not the full "
            "aggregate per-round traces needed for the paper's Figure 7 result."
        ),
        "claim_token_cost": (
            (
                "Partially reproduced: token logs exist "
                f"(train={train_result.get('token_usage_total')}, eval={eval_result.get('token_usage_total')}), "
                "and all ready Table 4 token groups were executed at reduced POC scale; this verifies token logging but not the paper's full-scale token totals."
            )
            if claim_verdict_status == STATUS_PARTIALLY_REPRODUCED
            else "Blocked pending execution: the token-log plan exists, but paper-scale Table 4 grouped totals have not been run and compared."
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
                "| Claim | Claim verdict | Execution readiness | Compared / required evidence | Reason for verdict | Next step |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in claims:
            verdict_status = row.get("claim_verdict_status", row.get("status"))
            readiness_status = row.get("execution_readiness_status", "unknown")
            lines.append(
                f"| `{row.get('claim_id')}` | {status_badge(verdict_status)} | "
                f"{status_badge(readiness_status)} | "
                f"{table_cell(claim_summary_comparison(row))} | "
                f"{table_cell(claim_summary_reason(row, benchmark))} | "
                f"{table_cell(row.get('next_step', 'No next step defined.'))} |"
            )

    non_success = [row for row in claims if row.get("claim_verdict_status", row.get("status")) != STATUS_REPRODUCED]
    if non_success:
        lines.extend(["", "### Claim-Level Non-Success Details", ""])
        for row in non_success:
            verdict_status = row.get("claim_verdict_status", row.get("status"))
            readiness_status = row.get("execution_readiness_status", "unknown")
            validation_evidence = row.get("validation_evidence", row.get("evidence", []))
            planning_evidence = row.get("planning_evidence", [])
            lines.extend(
                [
                    f"#### {row.get('claim_id')}",
                    "",
                    f"- Claim verdict status: {status_badge(verdict_status)}",
                    f"- Execution readiness status: {status_badge(readiness_status)}",
                    f"- Verification mode: `{row.get('verification_mode', 'unknown')}`",
                    f"- Next step: {row.get('next_step', 'No next step defined.')}",
                ]
            )
            blockers = row.get("blockers") or []
            if blockers:
                lines.append("- Reason:")
                lines.extend(f"  - {blocker}" for blocker in blockers)
            elif validation_evidence:
                lines.append("- Reason:")
                lines.append("  - Only partial/smoke evidence is available.")
            else:
                lines.append("- Reason:")
                lines.append("  - No successful verification evidence is available for this claim.")
            if validation_evidence:
                lines.append("- Validation evidence:")
                lines.extend(f"  - {item}" for item in validation_evidence)
            if planning_evidence:
                lines.append("- Planning/readiness evidence:")
                lines.extend(f"  - {item}" for item in planning_evidence)
            external_candidates = row.get("external_source_candidates") or []
            if external_candidates:
                lines.append("- External intake candidates:")
                lines.extend(f"  - {format_source_candidate(candidate)}" for candidate in external_candidates)
            lines.append("")
    return "\n".join(lines) + "\n"


def render_report(run_dir: Path) -> None:
    paths = paths_for(run_dir)
    manifest = read_json(paths.input_dir / "input_manifest.json") if (paths.input_dir / "input_manifest.json").exists() else {}
    contract = read_artifact_json(paths, "verification_contract.json", ["06_plans_and_contracts"])
    code_manifest = read_artifact_json(paths, "code_manifest.json", ["03_code_and_sources"])
    benchmark = read_artifact_json(paths, "benchmark_results.json", ["08_results"])
    comparison = read_artifact_json(paths, "claim_comparison.json", ["08_results"])
    automation_state = read_artifact_json(paths, "automation_state.json", ["00_run_summary"])
    all_claim_matrix = read_artifact_json(paths, "all_claim_verification_matrix.json", ["02_claims"])
    long_inference = long_inference_approved(run_dir)

    overall = comparison.get("smoke_status") or comparison.get("status") or automation_state.get("status") or STATUS_BLOCKED
    full_claim = comparison.get("full_paper_claim_status", "blocked")
    all_claim_counts = all_claim_matrix.get("claim_verdict_status_counts") or all_claim_matrix.get("status_counts", {})
    readiness_counts = all_claim_matrix.get("readiness_status_counts", {})
    all_claim_summary = ", ".join(f"{status}={count}" for status, count in sorted(all_claim_counts.items())) or "unavailable"
    readiness_summary = ", ".join(f"{status}={count}" for status, count in sorted(readiness_counts.items())) or "unavailable"
    status_explanations = render_status_explanations_md(overall, full_claim, benchmark, comparison, all_claim_matrix)
    if long_inference or all_claim_matrix.get("claims"):
        all_claim_section = (
            "## All-Claim Verification\n\n"
            f"- Claim verdict status counts: `{all_claim_summary}`\n"
            f"- Execution readiness status counts: `{readiness_summary}`\n"
            "- Matrix: `artifacts/all_claim_verification_matrix.json`\n"
            "- Catalog: `artifacts/all_claims.json`\n\n"
        )
        validation_evidence_files = [
            "artifacts/benchmark_results.json",
            "artifacts/claim_comparison.json",
        ]
        planning_artifact_files = [
            "artifacts/verification_contract.json",
            "artifacts/command_plan.json",
            "artifacts/all_claims.json",
            "artifacts/all_claim_verification_matrix.json",
            "artifacts/external_source_intake_status.json",
            "artifacts/canonical_benchmark_source_status.json",
            "artifacts/model_route_mapping.template.json",
            "artifacts/benchmark_execution_plan.json",
            "artifacts/transfer_runner_plan.json",
            "artifacts/full_matrix_execution_contract.json",
            "artifacts/transfer_execution_contract.json",
            "artifacts/figure7_trace_extraction_contract.json",
            "artifacts/per_round_trace_retention_checklist.json",
            "artifacts/token_log_plan.json",
            "artifacts/baseline_source_identity_review.json",
            "artifacts/baseline_single_skill_adapter_contract.json",
            "artifacts/baseline_deviation_note.md",
            "artifacts/reconstructed_ablation_contract.json",
            "artifacts/ablation_config_matrix.json",
            "artifacts/ablation_smoke_plan.json",
            "artifacts/ablation_deviation_note.md",
        ]
        raw_output_files = [
            "outputs/install_stdout.txt",
            "outputs/install_stderr.txt",
            "outputs/benchmark_stdout.txt",
            "outputs/benchmark_stderr.txt",
        ]
    else:
        all_claim_section = (
            "## Artifact Mode\n\n"
            "`minimal`\n\n"
            "`long_inference_approved` is false or absent in `artifacts/approval.json`, so this run keeps only the core Phase 0 evidence artifacts for the selected validation target.\n\n"
        )
        validation_evidence_files = [
            "artifacts/benchmark_results.json",
            "artifacts/claim_comparison.json",
        ]
        planning_artifact_files = [
            "artifacts/paper_parse.json",
            "artifacts/claims.json",
            "artifacts/benchmark_claims.json",
            "artifacts/code_manifest.json",
            "artifacts/official_instructions.json",
            "artifacts/verification_contract.json",
            "artifacts/command_plan.json",
        ]
        raw_output_files = [
            "outputs/install_stdout.txt",
            "outputs/install_stderr.txt",
            "outputs/benchmark_stdout.txt",
            "outputs/benchmark_stderr.txt",
        ]
    validation_evidence_file_lines = "\n".join(f"- `{path}`" for path in validation_evidence_files)
    planning_artifact_file_lines = "\n".join(f"- `{path}`" for path in planning_artifact_files)
    raw_output_file_lines = "\n".join(f"- `{path}`" for path in raw_output_files)
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

{all_claim_section}
{status_explanations}
## Validation Evidence Files

{validation_evidence_file_lines}

## Planning And Readiness Artifacts

{planning_artifact_file_lines}

## Raw Output Files

{raw_output_file_lines}

## Limitations

- This is a paper-specific automation POC.
- The selected target is a low-cost AIME smoke validation, not the paper's full Table 1 benchmark matrix.
- Live install and benchmark execution require `artifacts/approval.json` plus API keys.
- Additional target executions may include recorded deviations, especially the direct OpenAI fallback used when OpenRouter credits were unavailable.
"""
    write_text_with_category_mirrors(paths, "research_validation_report.md", report, ["00_run_summary"])
    append_event(run_dir, "report_generation", "completed", artifact="artifacts/research_validation_report.md")


def parse_compare_report(run_dir: Path) -> None:
    paths = paths_for(run_dir)
    if not (paths.artifacts_dir / "verification_contract.json").exists():
        build_verification_contract(run_dir)
    if long_inference_approved(run_dir):
        write_external_source_intake_artifacts(run_dir)
        write_execution_planning_artifacts(run_dir)
        write_baseline_comparison_artifacts(run_dir)
    parse_results(run_dir)
    compare_results(run_dir)
    if long_inference_approved(run_dir):
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
    approve.add_argument(
        "--long-inference-approved",
        action="store_true",
        help="Allow the full verbose artifact set. Defaults to false/minimal artifacts.",
    )

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
    execute.add_argument(
        "--long-inference-approved",
        action="store_true",
        help="When recording Codex approval, allow the full verbose artifact set.",
    )

    parse = subparsers.add_parser("parse", help="Parse existing raw outputs, compare, and render report.")
    parse.add_argument("--run-dir", type=Path, required=True)

    lcb_split = subparsers.add_parser(
        "prepare-livecodebench-split",
        help="Generate the reconstructed release_v6 50/150 seed-42 LiveCodeBench split.",
    )
    lcb_split.add_argument("--run-dir", type=Path, required=True)
    lcb_split.add_argument("--force", action="store_true", help="Overwrite existing generated LiveCodeBench split files.")

    provider_resolution = subparsers.add_parser(
        "write-provider-resolution",
        help="Write provider availability policy without executing API calls.",
    )
    provider_resolution.add_argument("--run-dir", type=Path, required=True)
    provider_resolution.add_argument(
        "--include-non-openai",
        action="store_true",
        help="Record policy as if non-openai provider routes are enabled.",
    )
    provider_resolution.add_argument(
        "--no-direct-openai-fallback",
        action="store_true",
        help="Record policy without direct OpenAI fallback for openai/* routes.",
    )
    provider_resolution.add_argument(
        "--allow-openrouter-after-402",
        action="store_true",
        help="Treat previously captured OpenRouter 402 logs as historical after credits/key have been repaired.",
    )

    full_matrix = subparsers.add_parser(
        "run-full-matrix",
        help="Run or dry-run resumable per-entry SkillGen Table 1 full-matrix entries.",
    )
    full_matrix.add_argument("--run-dir", type=Path, required=True)
    full_matrix.add_argument("--max-entries", type=int, default=None, help="Maximum executable entries to run this invocation.")
    full_matrix.add_argument("--dry-run", action="store_true", help="Plan entries and generate configs without executing official code.")
    full_matrix.add_argument(
        "--include-non-openai",
        action="store_true",
        help="Allow non-openai provider routes. Defaults to waiting until provider routes are resolved.",
    )
    full_matrix.add_argument(
        "--no-direct-openai-fallback",
        action="store_true",
        help="Do not set SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1 for openai routes.",
    )
    full_matrix.add_argument(
        "--allow-openrouter-after-402",
        action="store_true",
        help="Allow non-openai OpenRouter attempts even though older logs contain OpenRouter 402 evidence.",
    )
    full_matrix.add_argument("--judge-model-route", default="openai/gpt-5.4-mini")
    full_matrix.add_argument("--max-workers", type=int, default=1)
    full_matrix.add_argument("--max-refine-rounds", type=int, default=1)
    full_matrix.add_argument("--verification-sample-size", type=int, default=4)
    full_matrix.add_argument("--max-eval-instances", type=int, default=None)
    full_matrix.add_argument(
        "--target",
        action="append",
        default=None,
        help="Limit this invocation to a Table 1 target id. May be repeated.",
    )
    full_matrix.add_argument(
        "--model",
        action="append",
        default=None,
        help="Limit this invocation to a paper model display name or provider route id. May be repeated.",
    )
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
            long_inference_approved=args.long_inference_approved,
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
                long_inference_approved=args.long_inference_approved,
            )
        status = execute_approved_pipeline(args.run_dir, skip_install=args.skip_install)
        print(status)
        return 0 if status not in {STATUS_FAILED_TO_RUN, STATUS_NOT_TESTABLE} else 1
    if args.command == "parse":
        parse_compare_report(args.run_dir)
        print(args.run_dir)
        return 0
    if args.command == "prepare-livecodebench-split":
        manifest = prepare_livecodebench_split(args.run_dir, force=args.force)
        print(manifest.get("status"))
        return 0 if manifest.get("status") == STATUS_READY_FOR_EXECUTION else 1
    if args.command == "write-provider-resolution":
        payload = write_provider_resolution_status(
            args.run_dir,
            include_non_openai=args.include_non_openai,
            direct_openai_fallback=not args.no_direct_openai_fallback,
            allow_openrouter_after_402=args.allow_openrouter_after_402,
        )
        print(payload["status"])
        return 0
    if args.command == "run-full-matrix":
        state = run_full_matrix_entries(
            args.run_dir,
            max_entries=args.max_entries,
            include_non_openai=args.include_non_openai,
            direct_openai_fallback=not args.no_direct_openai_fallback,
            allow_openrouter_after_402=args.allow_openrouter_after_402,
            dry_run=args.dry_run,
            judge_model_route=args.judge_model_route,
            max_workers=args.max_workers,
            max_refine_rounds=args.max_refine_rounds,
            verification_sample_size=args.verification_sample_size,
            max_eval_instances=args.max_eval_instances,
            target_subset=set(args.target) if args.target else None,
            model_subset=set(args.model) if args.model else None,
        )
        print(state["status"])
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
