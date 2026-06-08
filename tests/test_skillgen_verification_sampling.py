from pathlib import Path
import importlib.util
from types import ModuleType, SimpleNamespace
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


def _install_pipeline_import_stubs() -> dict[str, ModuleType | None]:
    stubs: dict[str, ModuleType] = {}

    yaml_stub = ModuleType("yaml")
    yaml_stub.safe_load = lambda *_args, **_kwargs: {}  # type: ignore[attr-defined]
    stubs["yaml"] = yaml_stub

    artifacts_stub = ModuleType("artifacts")
    for name in [
        "ensure_dir",
        "make_run_dir",
        "write_json",
        "write_trajectories",
        "save_trajectories",
        "load_trajectories",
        "checkpoint_exists",
        "load_progress",
        "save_progress",
    ]:
        setattr(artifacts_stub, name, lambda *_args, **_kwargs: None)
    stubs["artifacts"] = artifacts_stub

    models_stub = ModuleType("models")
    models_stub.SkillAnalysis = object  # type: ignore[attr-defined]
    models_stub.SkillStatus = SimpleNamespace(ACTIVE="active", DEPRECATED="deprecated")  # type: ignore[attr-defined]
    models_stub.TaskInstance = SimpleNamespace  # type: ignore[attr-defined]
    models_stub.TaskType = object  # type: ignore[attr-defined]
    models_stub.Trajectory = SimpleNamespace  # type: ignore[attr-defined]
    models_stub.VerificationFeedback = object  # type: ignore[attr-defined]
    stubs["models"] = models_stub

    trajectory_stub = ModuleType("trajectory")
    trajectory_stub.collect_trajectories = lambda *_args, **_kwargs: []  # type: ignore[attr-defined]
    trajectory_stub.AgentConfig = object  # type: ignore[attr-defined]
    stubs["trajectory"] = trajectory_stub

    agents_stub = ModuleType("agents")
    agents_stub.__path__ = []  # type: ignore[attr-defined]
    stubs["agents"] = agents_stub

    induction_stub = ModuleType("agents.induction")
    induction_stub.run_induction = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    induction_stub.save_analysis = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    induction_stub.load_analysis = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    stubs["agents.induction"] = induction_stub

    generation_stub = ModuleType("agents.generation")
    generation_stub.generate_skill = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    generation_stub.generate_skill_with_resources = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    generation_stub.refine_skill = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    stubs["agents.generation"] = generation_stub

    verification_stub = ModuleType("agents.verification")
    verification_stub.run_verification = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    stubs["agents.verification"] = verification_stub

    skill_store_stub = ModuleType("skill_store")
    skill_store_stub.finalize_skill = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    skill_store_stub.save_skill = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    stubs["skill_store"] = skill_store_stub

    stubs["llm"] = ModuleType("llm")

    originals = {name: sys.modules.get(name) for name in stubs}
    sys.modules.update(stubs)
    return originals


def _restore_modules(originals: dict[str, ModuleType | None]) -> None:
    for name, module in originals.items():
        if module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module


def load_skillgen_pipeline():
    sys.path.insert(0, str(OFFICIAL_SOURCE))
    originals = _install_pipeline_import_stubs()
    try:
        spec = importlib.util.spec_from_file_location(
            "skillgen_official_pipeline_under_test",
            OFFICIAL_SOURCE / "pipeline.py",
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load SkillGen pipeline module")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(OFFICIAL_SOURCE))
        _restore_modules(originals)
    return module


class SkillGenVerificationSamplingTest(unittest.TestCase):
    def test_verification_sample_includes_failures_when_failures_exist(self) -> None:
        if not (OFFICIAL_SOURCE / "pipeline.py").exists():
            self.skipTest("local SkillGen official source copy is not present")

        pipeline = load_skillgen_pipeline()
        fail_ids = [f"f{index}" for index in range(5)]
        success_ids = [f"s{index}" for index in range(35)]
        inst_map = {
            instance_id: SimpleNamespace(
                instance_id=instance_id,
                input=f"task {instance_id}",
                ground_truth=True,
            )
            for instance_id in fail_ids + success_ids
        }
        failures = [
            SimpleNamespace(
                trajectory_id=f"traj-{instance_id}",
                instance_id=instance_id,
                agent_config={},
                messages=[],
                final_output="",
                success=False,
            )
            for instance_id in fail_ids
        ]
        successes = [
            SimpleNamespace(
                trajectory_id=f"traj-{instance_id}",
                instance_id=instance_id,
                agent_config={},
                messages=[],
                final_output="",
                success=True,
            )
            for instance_id in success_ids
        ]

        target_failures, success_guard = pipeline._build_verification_sample(
            failures,
            successes,
            inst_map,
            sample_size=4,
            min_sample=2,
            seed=42,
        )

        target_ids = {instance.instance_id for instance in target_failures}
        guard_ids = {instance.instance_id for instance in success_guard}

        self.assertEqual(len(target_ids), 2)
        self.assertEqual(len(guard_ids), 2)
        self.assertTrue(target_ids <= set(fail_ids))
        self.assertTrue(guard_ids <= set(success_ids))

    def test_verification_sample_handles_fewer_failures_than_reserved_slots(self) -> None:
        if not (OFFICIAL_SOURCE / "pipeline.py").exists():
            self.skipTest("local SkillGen official source copy is not present")

        pipeline = load_skillgen_pipeline()
        fail_ids = ["f0"]
        success_ids = [f"s{index}" for index in range(10)]
        inst_map = {
            instance_id: SimpleNamespace(
                instance_id=instance_id,
                input=f"task {instance_id}",
                ground_truth=True,
            )
            for instance_id in fail_ids + success_ids
        }
        failures = [
            SimpleNamespace(
                trajectory_id=f"traj-{instance_id}",
                instance_id=instance_id,
                agent_config={},
                messages=[],
                final_output="",
                success=False,
            )
            for instance_id in fail_ids
        ]
        successes = [
            SimpleNamespace(
                trajectory_id=f"traj-{instance_id}",
                instance_id=instance_id,
                agent_config={},
                messages=[],
                final_output="",
                success=True,
            )
            for instance_id in success_ids
        ]

        target_failures, success_guard = pipeline._build_verification_sample(
            failures,
            successes,
            inst_map,
            sample_size=4,
            min_sample=2,
            seed=42,
        )

        target_ids = {instance.instance_id for instance in target_failures}
        guard_ids = {instance.instance_id for instance in success_guard}

        self.assertEqual(target_ids, {"f0"})
        self.assertEqual(len(guard_ids), 3)
        self.assertTrue(guard_ids <= set(success_ids))


if __name__ == "__main__":
    unittest.main()
