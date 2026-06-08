from pathlib import Path
import importlib.util
from types import ModuleType
import math
import os
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


def load_skillgen_llm():
    openai_stub = ModuleType("openai")

    class OpenAIStub:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("OpenAI client should not be constructed for hash embeddings")

    openai_stub.OpenAI = OpenAIStub  # type: ignore[attr-defined]

    original_openai = sys.modules.get("openai")
    sys.modules["openai"] = openai_stub
    try:
        spec = importlib.util.spec_from_file_location(
            "skillgen_official_llm_under_test",
            OFFICIAL_SOURCE / "llm.py",
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load SkillGen llm module")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if original_openai is None:
            sys.modules.pop("openai", None)
        else:
            sys.modules["openai"] = original_openai


class SkillGenHashEmbeddingTest(unittest.TestCase):
    def test_hash_embedding_is_deterministic_and_local_without_api_keys(self) -> None:
        if not (OFFICIAL_SOURCE / "llm.py").exists():
            self.skipTest("local SkillGen official source copy is not present")

        llm = load_skillgen_llm()
        saved_env = {key: os.environ.get(key) for key in [
            "SKILLGEN_LOCAL_EMBEDDING_MODE",
            "OPENAI_API_KEY",
            "OPENROUTER_API_KEY",
        ]}
        try:
            os.environ["SKILLGEN_LOCAL_EMBEDDING_MODE"] = "hash"
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("OPENROUTER_API_KEY", None)

            first = llm.embed("Plan with stable tool calls and evidence.")
            second = llm.embed("Plan with stable tool calls and evidence.")
            different = llm.embed("A distinct planning request with other terms.")
            batch = llm.embed([
                "Plan with stable tool calls and evidence.",
                "A distinct planning request with other terms.",
            ])
        finally:
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertEqual(len(first), 256)
        self.assertEqual(first, second)
        self.assertNotEqual(first, different)
        self.assertEqual(batch[0], first)
        self.assertEqual(batch[1], different)
        self.assertAlmostEqual(math.sqrt(sum(value * value for value in first)), 1.0)


if __name__ == "__main__":
    unittest.main()
