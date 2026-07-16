"""Lightweight grader for reconstructed ALFWorld offline-plan tasks."""

from __future__ import annotations

import os
import re
from typing import Any


PASS_THRESHOLD_DEFAULT = 0.55

_NUMBERED_RE = re.compile(r"^\s*(?:\d+)[\.\)\:]\s*(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
_FENCE_RE = re.compile(r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL)
_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "in",
    "into",
    "of",
    "on",
    "the",
    "to",
    "under",
    "with",
}
_VERB_SYNONYMS = {
    "grab": "pick",
    "pickup": "pick",
    "take": "pick",
    "place": "put",
    "move": "put",
    "set": "put",
    "turn": "toggle",
    "switch": "toggle",
    "activate": "toggle",
    "wash": "clean",
    "rinse": "clean",
    "warm": "heat",
    "cool": "cool",
    "chill": "cool",
    "slice": "slice",
    "cut": "slice",
    "go": "go",
    "navigate": "go",
    "walk": "go",
    "look": "look",
    "inspect": "look",
    "examine": "look",
}


def _extract_plan(raw: str) -> list[str]:
    if not raw:
        return []
    fenced = _FENCE_RE.findall(raw)
    source = fenced[-1] if fenced else raw
    actions: list[str] = []
    for line in source.splitlines():
        line = line.strip()
        if not line:
            continue
        match = _NUMBERED_RE.match(line) or _BULLET_RE.match(line)
        if match:
            actions.append(match.group(1).strip())
    if not actions:
        actions = [line.strip() for line in source.splitlines() if line.strip()]
    return [a.strip(" `\"'") for a in actions if 0 < len(a) <= 200]


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _verb(text: str) -> str:
    tokens = _normalise(text).split()
    if not tokens:
        return ""
    if tokens[:2] == ["pick", "up"]:
        return "pick"
    if tokens[:2] == ["turn", "on"]:
        return "toggle"
    return _VERB_SYNONYMS.get(tokens[0], tokens[0])


def _tokens(text: str) -> set[str]:
    return {tok for tok in _normalise(text).split() if tok not in _STOPWORDS}


def compute_action_coverage(agent_actions: list[str], gold_actions: list[str]) -> dict[str, Any]:
    if not gold_actions:
        return {"matched": [], "coverage_rate": 0.0, "hit": 0, "total": 0}
    agent = [
        {
            "raw": action,
            "verb": _verb(action),
            "tokens": _tokens(action),
        }
        for action in agent_actions
    ]
    matched = []
    for gold in gold_actions:
        gold_verb = _verb(gold)
        gold_tokens = _tokens(gold)
        best = None
        best_overlap = 0.0
        for candidate in agent:
            if gold_verb and candidate["verb"] != gold_verb:
                continue
            overlap = len(gold_tokens & candidate["tokens"]) / max(1, len(gold_tokens))
            if overlap > best_overlap:
                best = candidate["raw"]
                best_overlap = overlap
        matched.append(
            {
                "gold_action": gold,
                "matched_agent_action": best if best_overlap >= 0.5 else None,
                "overlap": best_overlap,
            }
        )
    hit = sum(1 for row in matched if row["matched_agent_action"])
    return {
        "matched": matched,
        "coverage_rate": hit / len(gold_actions),
        "hit": hit,
        "total": len(gold_actions),
    }


def _threshold() -> float:
    raw = os.environ.get("ALFWORLD_PASS_THRESHOLD")
    if not raw:
        return PASS_THRESHOLD_DEFAULT
    try:
        value = float(raw)
    except ValueError:
        return PASS_THRESHOLD_DEFAULT
    return max(0.0, min(1.0, value))


def evaluate_alfworld_output(
    model_output: str,
    instance_metadata: dict[str, Any],
    *,
    judge_model: str | None = None,
) -> dict[str, Any]:
    del judge_model
    meta = instance_metadata or {}
    agent_plan = _extract_plan(str(model_output or ""))
    gold_actions = meta.get("gold_actions") or meta.get("human_high_descs") or []
    coverage = compute_action_coverage(agent_plan, [str(action) for action in gold_actions])
    threshold = _threshold()
    score = float(coverage.get("coverage_rate") or 0.0)
    passed = bool(agent_plan and score >= threshold)
    return {
        "passed": passed,
        "score": score,
        "threshold": threshold,
        "extracted_plan": agent_plan,
        "action_coverage": coverage,
        "adapter_mode": meta.get("adapter_mode", "unknown"),
        "error_message": None if passed else f"coverage={score:.2f} < threshold={threshold:.2f}",
    }


__all__ = ["evaluate_alfworld_output", "compute_action_coverage", "PASS_THRESHOLD_DEFAULT"]

