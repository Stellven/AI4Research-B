"""ALFWorld adapter for SkillGen's static TaskDataset format.

This is a reconstructed offline-plan adapter. It converts canonical ALFWorld
TextWorld task metadata into one-shot planning prompts that SkillGen's current
`main.py` and `eval_skill.py` can load. It does not claim to reproduce an
author-original live ALFWorld runner.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


CANONICAL_SOURCE = "alfworld/alfworld"
CANONICAL_SOURCE_URL = "https://github.com/alfworld/alfworld.git"
CANONICAL_COMMIT = "aaba6870f86c5be6a08a491f32a50b906227bc3e"
CANONICAL_VERSION = "0.5.0"

DATA_RELEASE_URLS = {
    "json": "https://github.com/alfworld/alfworld/releases/download/0.2.2/json_2.1.1_json.zip",
    "pddl": "https://github.com/alfworld/alfworld/releases/download/0.2.2/json_2.1.1_pddl.zip",
    "tw_pddl": "https://github.com/alfworld/alfworld/releases/download/0.4.2/json_2.1.3_tw-pddl.zip",
    "mrcnn": "https://github.com/alfworld/alfworld/releases/download/0.2.2/mrcnn_alfred_objects_sep13_004.pth",
}

PAPER_SPLIT_PROTOCOL = {
    "alfworld_iod": {
        "paper_split": "iod",
        "construction_source_split": "train",
        "test_source_split": "valid_seen",
        "construction_n": 500,
        "test_n": 150,
        "paper_note": "In-distribution; task types overlap with train.",
    },
    "alfworld_ood": {
        "paper_split": "ood",
        "construction_source_split": "train",
        "test_source_split": "valid_unseen",
        "construction_n": 500,
        "test_n": 255,
        "paper_note": "Out-of-distribution; paper table labels this as novel task types.",
    },
}

ACTION_GRAMMAR_HINT = """\
ALFWorld TextWorld actions are short imperative commands. Common high-level
steps include:
  navigation   : go to <location>
  pickup       : pick up <object>
  placement    : put <object> in/on <receptacle>
  cleaning     : clean <object>
  heating      : heat <object>
  cooling      : cool <object>
  lighting     : turn on <object>, look at <object> under <light>
  two-object   : repeat pickup/place steps for both target objects

Prefer concise commands. Preserve prerequisite order: navigate before pickup,
pickup before placement, clean/heat/cool before final placement, and turn on
the light before examining an object in light tasks.
"""


def _json_load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _best_annotation(traj: dict[str, Any]) -> dict[str, Any]:
    anns = ((traj.get("turk_annotations") or {}).get("anns") or [])
    if not anns:
        return {"task_desc": "", "high_descs": [], "votes": []}

    def score(ann: dict[str, Any]) -> tuple[int, int]:
        votes = ann.get("votes") or []
        return (sum(int(bool(v)) for v in votes), len(ann.get("high_descs") or []))

    return max(anns, key=score)


def _clean_token(value: Any) -> str:
    text = str(value or "").strip()
    return text.replace("_", " ").lower()


def _discrete_action_to_text(action: dict[str, Any]) -> str:
    discrete = action.get("discrete_action") or {}
    name = str(discrete.get("action") or "").strip()
    args = [_clean_token(v) for v in (discrete.get("args") or []) if str(v or "").strip()]

    if name == "GotoLocation" and args:
        return f"go to {args[0]}"
    if name == "PickupObject" and args:
        return f"pick up {args[0]}"
    if name == "PutObject":
        if len(args) >= 2:
            return f"put {args[0]} in/on {args[1]}"
        if args:
            return f"put {args[0]}"
    if name == "CleanObject" and args:
        return f"clean {args[0]}"
    if name == "HeatObject" and args:
        return f"heat {args[0]}"
    if name == "CoolObject" and args:
        return f"cool {args[0]}"
    if name == "ToggleObject" and args:
        return f"turn on {args[0]}"
    if name == "SliceObject" and args:
        return f"slice {args[0]}"

    fallback = " ".join([name] + args).strip()
    return fallback or "unknown action"


def _gold_actions(traj: dict[str, Any]) -> list[str]:
    high_pddl = (traj.get("plan") or {}).get("high_pddl") or []
    actions = [_discrete_action_to_text(step) for step in high_pddl]
    return [a for a in actions if a and a != "unknown action"]


def _goal_from_record(traj: dict[str, Any], annotation: dict[str, Any]) -> str:
    goal = str(annotation.get("task_desc") or "").strip()
    if goal:
        return goal
    params = traj.get("pddl_params") or {}
    task_type = traj.get("task_type") or "unknown_task"
    return (
        f"Solve ALFWorld task type {task_type} with object_target="
        f"{params.get('object_target')}, parent_target={params.get('parent_target')}, "
        f"mrecep_target={params.get('mrecep_target')}, toggle_target={params.get('toggle_target')}."
    )


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def load_task_pool(alfworld_data_dir: str | Path, source_split: str) -> list[dict[str, Any]]:
    """Load and normalize all ALFWorld tasks for one canonical split."""
    data_root = Path(alfworld_data_dir)
    split_root = data_root / "json_2.1.1" / source_split
    if not split_root.exists():
        raise FileNotFoundError(f"ALFWorld split directory not found: {split_root}")

    rows: list[dict[str, Any]] = []
    seen_task_ids: set[str] = set()
    for traj_path in sorted(split_root.rglob("traj_data.json")):
        traj = _json_load(traj_path)
        task_id = str(traj.get("task_id") or traj_path.parent.name)
        if task_id in seen_task_ids:
            continue
        seen_task_ids.add(task_id)

        annotation = _best_annotation(traj)
        task_dir = traj_path.parent
        game_file = task_dir / "game.tw-pddl"
        initial_state = task_dir / "initial_state.pddl"
        scene = traj.get("scene") or {}
        rows.append(
            {
                "source_split": source_split,
                "task_id": task_id,
                "task_type": str(traj.get("task_type") or "unknown"),
                "pddl_params": traj.get("pddl_params") or {},
                "scene": {
                    "floor_plan": scene.get("floor_plan"),
                    "scene_num": scene.get("scene_num"),
                    "random_seed": scene.get("random_seed"),
                },
                "goal": _goal_from_record(traj, annotation),
                "human_high_descs": [str(v).strip() for v in (annotation.get("high_descs") or []) if str(v).strip()],
                "gold_actions": _gold_actions(traj),
                "task_dir": _rel(task_dir, data_root),
                "traj_data": _rel(traj_path, data_root),
                "game_file": _rel(game_file, data_root) if game_file.exists() else None,
                "initial_state": _rel(initial_state, data_root) if initial_state.exists() else None,
            }
        )
    return rows


def _task_type_counts(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["task_type"]] += 1
    return dict(sorted(counts.items()))


def stratified_sample(pool: list[dict[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    """Deterministic approximate stratified sample by ALFWorld task_type."""
    if n > len(pool):
        raise ValueError(f"Requested n={n} but pool has only {len(pool)} tasks")
    if n == len(pool):
        return list(pool)

    rng = random.Random(seed)
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pool:
        by_type[row["task_type"]].append(row)
    for rows in by_type.values():
        rows.sort(key=lambda r: (r["task_type"], r["task_id"], r["task_dir"]))
        rng.shuffle(rows)

    task_types = sorted(by_type)
    cursors = {task_type: 0 for task_type in task_types}
    picked: list[dict[str, Any]] = []
    while len(picked) < n:
        made_progress = False
        for task_type in task_types:
            cursor = cursors[task_type]
            rows = by_type[task_type]
            if cursor < len(rows):
                picked.append(rows[cursor])
                cursors[task_type] = cursor + 1
                made_progress = True
                if len(picked) == n:
                    break
        if not made_progress:
            break

    rng.shuffle(picked)
    return picked[:n]


def render_prompt(record: dict[str, Any], paper_split: str) -> str:
    params = record.get("pddl_params") or {}
    high_descs = record.get("human_high_descs") or []
    desc_hint = "\n".join(f"- {step}" for step in high_descs[:8]) or "(not provided)"
    param_lines = "\n".join(
        f"- {key}: {value}"
        for key, value in sorted(params.items())
        if value not in (None, "", [], {})
    ) or "(not provided)"
    return (
        "You are solving an ALFWorld task in a reconstructed offline planning "
        "variant for SkillGen. The live TextWorld environment is not available "
        "inside this prompt. Produce a concise high-level plan of ALFWorld text "
        "actions that should solve the task.\n\n"
        f"## Split\n{paper_split.upper()} / source={record['source_split']}\n\n"
        f"## Goal\n{record['goal']}\n\n"
        f"## Task type\n{record['task_type']}\n\n"
        f"## PDDL target parameters\n{param_lines}\n\n"
        f"## Human demonstration step hints\n{desc_hint}\n\n"
        f"## Action grammar\n{ACTION_GRAMMAR_HINT.rstrip()}\n\n"
        "## Output format\n"
        "Respond with exactly a numbered plan, one action per line, and no prose:\n"
        "```\n"
        "1. <action>\n"
        "2. <action>\n"
        "...\n"
        "```"
    )


def convert_record(record: dict[str, Any], *, target_id: str, split_label: str, paper_split: str) -> dict[str, Any]:
    gold_actions = record.get("gold_actions") or record.get("human_high_descs") or []
    ground_truth = (
        f"Goal: {record['goal']}\n"
        "Reference high-level actions:\n"
        + "\n".join(f"{idx + 1}. {action}" for idx, action in enumerate(gold_actions))
    )
    return {
        "instance_id": f"alfworld::{target_id}::{split_label}::{record['task_type']}::{record['task_id']}",
        "input": render_prompt(record, paper_split),
        "ground_truth": ground_truth,
        "metadata": {
            "benchmark": "alfworld",
            "adapter_mode": "reconstructed_offline_plan",
            "environment": "AlfredTWEnv",
            "target_id": target_id,
            "paper_split": paper_split,
            "dataset_split": split_label,
            "source_split": record["source_split"],
            "task_type": record["task_type"],
            "task_id": record["task_id"],
            "task_dir": record["task_dir"],
            "traj_data": record["traj_data"],
            "game_file": record.get("game_file"),
            "initial_state": record.get("initial_state"),
            "goal": record["goal"],
            "pddl_params": record.get("pddl_params") or {},
            "scene": record.get("scene") or {},
            "human_high_descs": record.get("human_high_descs") or [],
            "gold_actions": gold_actions,
            "max_steps": 50,
        },
    }


def _dataset(target_id: str, split_label: str, paper_split: str, source_split: str, records: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    instances = [
        convert_record(record, target_id=target_id, split_label=split_label, paper_split=paper_split)
        for record in records
    ]
    return {
        "dataset_id": f"{target_id}_{split_label}_n{len(instances)}_seed{seed}",
        "task_name": target_id,
        "task_type": "open_ended",
        "instances": instances,
        "metadata": {
            "benchmark": "alfworld",
            "adapter_mode": "reconstructed_offline_plan",
            "environment": "AlfredTWEnv",
            "target_id": target_id,
            "paper_split": paper_split,
            "dataset_split": split_label,
            "source_split": source_split,
            "n": len(instances),
            "seed": seed,
            "source": CANONICAL_SOURCE,
            "source_url": CANONICAL_SOURCE_URL,
            "source_commit": CANONICAL_COMMIT,
            "source_version": CANONICAL_VERSION,
            "sampling": "stratified_by_task_type_seed42",
            "paper_reproduction_scope": "reconstructed_adapter_not_author_original_runner",
            "trace_retention_required": True,
        },
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_and_write_splits(
    *,
    alfworld_data_dir: str | Path,
    out_root: str | Path,
    seed: int = 42,
    train_n: int = 500,
    iod_test_n: int = 150,
    ood_test_n: int = 255,
    manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    data_dir = Path(alfworld_data_dir)
    out_root = Path(out_root)
    train_pool = load_task_pool(data_dir, "train")
    valid_seen_pool = load_task_pool(data_dir, "valid_seen")
    valid_unseen_pool = load_task_pool(data_dir, "valid_unseen")

    train_records = stratified_sample(train_pool, train_n, seed)
    iod_test_records = stratified_sample(valid_seen_pool, iod_test_n, seed ^ 0x105EED)
    ood_test_records = stratified_sample(valid_unseen_pool, ood_test_n, seed ^ 0x00D0D)

    generated = {
        "alfworld_iod": {
            "train": _dataset("alfworld_iod", "train", "iod", "train", train_records, seed),
            "test": _dataset("alfworld_iod", "test", "iod", "valid_seen", iod_test_records, seed),
        },
        "alfworld_ood": {
            "train": _dataset("alfworld_ood", "train", "ood", "train", train_records, seed),
            "test": _dataset("alfworld_ood", "test", "ood", "valid_unseen", ood_test_records, seed),
        },
    }

    output_paths = {
        "alfworld_iod": {
            "train": out_root / "alfworld_iod" / "train.json",
            "test": out_root / "alfworld_iod" / "test.json",
        },
        "alfworld_ood": {
            "train": out_root / "alfworld_ood" / "train.json",
            "test": out_root / "alfworld_ood" / "test.json",
        },
    }
    for target_id, splits in generated.items():
        for split_label, payload in splits.items():
            _write_json(output_paths[target_id][split_label], payload)

    manifest = {
        "schema_version": "0.1",
        "status": "ready_for_reconstructed_alfworld_json_loading_smoke",
        "adapter_mode": "reconstructed_offline_plan",
        "source": {
            "repository": CANONICAL_SOURCE,
            "source_url": CANONICAL_SOURCE_URL,
            "local_commit": CANONICAL_COMMIT,
            "package_version": CANONICAL_VERSION,
            "data_dir": str(data_dir),
            "data_release_urls": DATA_RELEASE_URLS,
        },
        "paper_split_protocol": PAPER_SPLIT_PROTOCOL,
        "observed_source_counts": {
            "train": len(train_pool),
            "valid_seen": len(valid_seen_pool),
            "valid_unseen": len(valid_unseen_pool),
        },
        "observed_task_type_counts": {
            "train": _task_type_counts(train_pool),
            "valid_seen": _task_type_counts(valid_seen_pool),
            "valid_unseen": _task_type_counts(valid_unseen_pool),
        },
        "sampling_rule": {
            "seed": seed,
            "construction_source_split": "train",
            "construction_n": train_n,
            "iod_test_source_split": "valid_seen",
            "iod_test_n": iod_test_n,
            "ood_test_source_split": "valid_unseen",
            "ood_test_n": ood_test_n,
            "method": "stable enumerate traj_data.json, deduplicate by task_id, stratify by task_type, round-robin sample, shuffle final order with seed",
        },
        "outputs": {
            target_id: {
                split_label: {
                    "path": path.as_posix(),
                    "n": len(generated[target_id][split_label]["instances"]),
                    "instance_ids": [
                        inst["instance_id"]
                        for inst in generated[target_id][split_label]["instances"]
                    ],
                }
                for split_label, path in paths.items()
            }
            for target_id, paths in output_paths.items()
        },
        "deviation_summary": [
            "The canonical ALFWorld source and data are used, but the SkillGen official checkout does not include an author-original ALFWorld runner.",
            "This adapter converts ALFWorld into an offline high-level planning task so SkillGen's current one-shot main.py/eval_skill.py can load and run it.",
            "Downstream results must be labeled as reconstructed offline-plan evidence unless exact author ALFWorld adapter/split code is found.",
        ],
        "trace_retention_required": {
            "eval_skill_save_trajectories": True,
            "required_patterns": [
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_iod/{model_slug}/eval_results_trajectories/{model_slug}_baseline.jsonl",
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_iod/{model_slug}/eval_results_trajectories/{model_slug}_with_skill.jsonl",
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_ood/{model_slug}/eval_results_trajectories/{model_slug}_baseline.jsonl",
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_ood/{model_slug}/eval_results_trajectories/{model_slug}_with_skill.jsonl",
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_*.jsonl",
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_summary.json",
                "artifacts/raw_benchmark_outputs/full_matrix/alfworld_*/{model_slug}/artifacts/runs/*/verification/round_*/verification_case_analyses.json",
            ],
        },
    }
    manifest_out = Path(manifest_path) if manifest_path else out_root / "alfworld_split_manifest_seed42.json"
    _write_json(manifest_out, manifest)
    manifest["manifest_path"] = manifest_out.as_posix()
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare ALFWorld IOD/OOD SkillGen JSON splits")
    parser.add_argument("--alfworld-data-dir", default="data/alfworld")
    parser.add_argument("--out-root", default="data")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-n", type=int, default=500)
    parser.add_argument("--iod-test-n", type=int, default=150)
    parser.add_argument("--ood-test-n", type=int, default=255)
    parser.add_argument("--manifest", default=None)
    args = parser.parse_args()

    manifest = build_and_write_splits(
        alfworld_data_dir=args.alfworld_data_dir,
        out_root=args.out_root,
        seed=args.seed,
        train_n=args.train_n,
        iod_test_n=args.iod_test_n,
        ood_test_n=args.ood_test_n,
        manifest_path=args.manifest,
    )
    print("Wrote ALFWorld SkillGen datasets:")
    for target_id, splits in manifest["outputs"].items():
        for split_label, info in splits.items():
            print(f"  {target_id}/{split_label}: {info['n']} -> {info['path']}")
    print(f"Manifest: {manifest['manifest_path']}")


if __name__ == "__main__":
    main()

