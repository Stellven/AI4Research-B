from pathlib import Path
import importlib
from types import ModuleType
import sys
import unittest


OFFICIAL_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "phase_0"
    / "runs"
    / "skillgen_phase0_thorough_20260602"
    / "code"
    / "official"
)


def load_generation_module():
    original_path = list(sys.path)
    original_llm = sys.modules.get("llm")
    sys.modules["llm"] = ModuleType("llm")
    sys.path.insert(0, str(OFFICIAL_SOURCE))
    for name in ["agents.generation", "agents", "models", "prompts"]:
        sys.modules.pop(name, None)
    try:
        return importlib.import_module("agents.generation")
    finally:
        sys.path = original_path
        if original_llm is None:
            sys.modules.pop("llm", None)
        else:
            sys.modules["llm"] = original_llm


class SkillGenGenerationRobustnessTest(unittest.TestCase):
    def test_plan_outline_and_notes_accept_non_string_json_fields(self) -> None:
        if not (OFFICIAL_SOURCE / "agents" / "generation.py").exists():
            self.skipTest("local SkillGen official source copy is not present")

        generation = load_generation_module()
        outline = generation._format_plan_outline({
            "contextual_abstract": ["one", "two"],
            "successful_experiences": {"key": "value"},
            "failure_lessons": 17,
        })

        self.assertIn("one\ntwo", outline)
        self.assertIn('{"key": "value"}', outline)
        self.assertIn("17", outline)
        self.assertEqual(generation._coerce_text(["a", {"b": 1}]), 'a\n{"b": 1}')


if __name__ == "__main__":
    unittest.main()
