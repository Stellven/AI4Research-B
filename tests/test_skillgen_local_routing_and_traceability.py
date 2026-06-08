from pathlib import Path
import importlib.util
from types import ModuleType, SimpleNamespace
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


class _FakeOpenAI:
    instances = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        self.requests = []
        _FakeOpenAI.instances.append(self)

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        message = SimpleNamespace(content="local response", tool_calls=None)
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(prompt_tokens=2, completion_tokens=3, total_tokens=5)
        return SimpleNamespace(choices=[choice], usage=usage)


def load_skillgen_llm_with_fake_openai():
    _FakeOpenAI.instances.clear()
    openai_stub = ModuleType("openai")
    openai_stub.OpenAI = _FakeOpenAI  # type: ignore[attr-defined]

    original_openai = sys.modules.get("openai")
    sys.modules["openai"] = openai_stub
    try:
        spec = importlib.util.spec_from_file_location(
            "skillgen_official_llm_local_routing_under_test",
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


def load_skill_store_modules():
    original_path = list(sys.path)
    original_models = sys.modules.get("models")
    original_skill_store = sys.modules.get("skill_store")
    sys.path.insert(0, str(OFFICIAL_SOURCE))
    try:
        models_spec = importlib.util.spec_from_file_location(
            "models",
            OFFICIAL_SOURCE / "models.py",
        )
        if models_spec is None or models_spec.loader is None:
            raise RuntimeError("could not load SkillGen models module")
        models = importlib.util.module_from_spec(models_spec)
        sys.modules["models"] = models
        models_spec.loader.exec_module(models)

        store_spec = importlib.util.spec_from_file_location(
            "skill_store",
            OFFICIAL_SOURCE / "skill_store.py",
        )
        if store_spec is None or store_spec.loader is None:
            raise RuntimeError("could not load SkillGen skill_store module")
        skill_store = importlib.util.module_from_spec(store_spec)
        sys.modules["skill_store"] = skill_store
        store_spec.loader.exec_module(skill_store)
        return models, skill_store
    finally:
        sys.path = original_path
        if original_models is None:
            sys.modules.pop("models", None)
        else:
            sys.modules["models"] = original_models
        if original_skill_store is None:
            sys.modules.pop("skill_store", None)
        else:
            sys.modules["skill_store"] = original_skill_store


class SkillGenLocalRoutingAndTraceabilityTest(unittest.TestCase):
    def test_local_openai_compat_routes_chat_without_external_api_keys(self) -> None:
        if not (OFFICIAL_SOURCE / "llm.py").exists():
            self.skipTest("local SkillGen official source copy is not present")

        llm = load_skillgen_llm_with_fake_openai()
        saved_env = {key: os.environ.get(key) for key in [
            "SKILLGEN_LOCAL_OPENAI_COMPAT",
            "SKILLGEN_LOCAL_BASE_URL",
            "SKILLGEN_LOCAL_API_KEY",
            "SKILLGEN_LOCAL_MODEL",
            "SKILLGEN_LOCAL_NUM_CTX",
            "SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS",
            "OPENAI_API_KEY",
            "OPENROUTER_API_KEY",
        ]}
        try:
            os.environ["SKILLGEN_LOCAL_OPENAI_COMPAT"] = "1"
            os.environ["SKILLGEN_LOCAL_BASE_URL"] = "http://local.test/v1"
            os.environ["SKILLGEN_LOCAL_API_KEY"] = "local-key"
            os.environ["SKILLGEN_LOCAL_MODEL"] = "local-model"
            os.environ["SKILLGEN_LOCAL_NUM_CTX"] = "4096"
            os.environ["SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS"] = "1"
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("OPENROUTER_API_KEY", None)

            result = llm.chat("hello", model="openai/gpt-would-be-direct")
        finally:
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertEqual(result, "local response")
        self.assertEqual(len(_FakeOpenAI.instances), 1)
        client = _FakeOpenAI.instances[0]
        self.assertEqual(client.kwargs["base_url"], "http://local.test/v1")
        self.assertEqual(client.kwargs["api_key"], "local-key")
        self.assertEqual(client.requests[0]["model"], "local-model")
        self.assertEqual(client.requests[0]["extra_body"], {"options": {"num_ctx": 4096}})

    def test_candidate_finalization_preserves_source_candidate_id(self) -> None:
        if not (OFFICIAL_SOURCE / "skill_store.py").exists():
            self.skipTest("local SkillGen official source copy is not present")

        models, skill_store = load_skill_store_modules()
        candidate = models.CandidateSkill(
            candidate_id="candidate-123",
            analysis_id="analysis-456",
            body="Use precise tool names and preserve evidence.",
            contextual_abstract="Planning task",
        )

        skill = skill_store.candidate_to_skill(
            candidate,
            dataset_id="dataset-789",
            task_name="mcp_bench_single",
        )

        self.assertNotEqual(skill.skill_id, candidate.candidate_id)
        self.assertEqual(skill.source_candidate_id, "candidate-123")
        self.assertEqual(skill.analysis_id, "analysis-456")
        self.assertEqual(skill.dataset_id, "dataset-789")
        self.assertEqual(skill.task_name, "mcp_bench_single")


if __name__ == "__main__":
    unittest.main()
