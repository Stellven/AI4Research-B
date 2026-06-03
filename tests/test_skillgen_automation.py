from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from ai4research_b.phase0.skillgen_automation import (
    STATUS_BLOCKED,
    approval_status,
    build_verification_contract,
    execute_install,
    parse_compare_report,
    prepare_automation_artifacts,
    write_approval_artifact,
)
from ai4research_b.phase0.skillgen_demo import run_demo


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def make_instances(n: int) -> list[dict[str, object]]:
    return [
        {
            "instance_id": str(index),
            "input": f"problem {index}",
            "ground_truth": f"{index:03d}",
            "metadata": {"benchmark": "aime"},
        }
        for index in range(n)
    ]


def make_fake_official_source(root: Path) -> Path:
    source = root / "official_source"
    source.mkdir()
    (source / "README.md").write_text(
        "Quick start uses main.py. Old eval example mentions --skill-path.\n",
        encoding="utf-8",
    )
    (source / "requirements.txt").write_text("pydantic\n", encoding="utf-8")
    (source / "config.yaml").write_text("models: {}\n", encoding="utf-8")
    (source / "main.py").write_text(
        "import argparse\n"
        "p=argparse.ArgumentParser()\n"
        "p.add_argument('dataset')\n"
        "p.add_argument('--config')\n",
        encoding="utf-8",
    )
    (source / "eval_skill.py").write_text(
        "import argparse\n"
        "p=argparse.ArgumentParser()\n"
        "p.add_argument('--skill-repo', required=True)\n"
        "p.add_argument('--dataset', required=True)\n"
        "p.add_argument('--n', type=int)\n"
        "p.add_argument('--seed', type=int)\n"
        "p.add_argument('--models', nargs='+')\n"
        "p.add_argument('--judge-model')\n"
        "p.add_argument('--output')\n",
        encoding="utf-8",
    )
    for relative_path in [
        "scripts/prepare_benchmarks.py",
        "benchmarks/livecodebench_adapter.py",
        "scripts/prepare_mcp_bench.py",
        "benchmarks/mcp_bench_adapter.py",
        "scripts/prepare_socialmaze.py",
        "benchmarks/socialmaze_adapter.py",
        "scripts/prepare_tau_bench.py",
        "benchmarks/tau_bench_adapter.py",
        "scripts/prepare_chemllmbench.py",
        "benchmarks/chemllmbench_adapter.py",
    ]:
        path = source / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture for source-intake detection\n", encoding="utf-8")
    write_json(
        source / "data" / "aime" / "train.json",
        {
            "dataset_id": "aime_train",
            "task_name": "aime",
            "task_type": "binary",
            "instances": make_instances(10),
        },
    )
    write_json(
        source / "data" / "aime" / "test.json",
        {
            "dataset_id": "aime_test",
            "task_name": "aime",
            "task_type": "binary",
            "instances": make_instances(5),
        },
    )
    return source


class SkillGenAutomationTest(unittest.TestCase):
    def test_prepare_writes_contract_command_plan_and_smoke_assets(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_auto_test")

            prepare_automation_artifacts(run_dir, official_source=source)

            contract = json.loads((run_dir / "artifacts" / "verification_contract.json").read_text(encoding="utf-8"))
            command_plan = json.loads((run_dir / "artifacts" / "command_plan.json").read_text(encoding="utf-8"))
            instructions = json.loads((run_dir / "artifacts" / "official_instructions.json").read_text(encoding="utf-8"))
            train_subset = json.loads((run_dir / "artifacts" / "smoke_data" / "aime_train_n8_seed42.json").read_text(encoding="utf-8"))
            hardcodings = json.loads((run_dir / "artifacts" / "hardcoding_disclosures.json").read_text(encoding="utf-8"))
            all_claims = json.loads((run_dir / "artifacts" / "all_claims.json").read_text(encoding="utf-8"))
            all_claim_matrix = json.loads((run_dir / "artifacts" / "all_claim_verification_matrix.json").read_text(encoding="utf-8"))
            intake_plan = json.loads((run_dir / "artifacts" / "external_source_intake_plan.json").read_text(encoding="utf-8"))
            intake_status = json.loads((run_dir / "artifacts" / "external_source_intake_status.json").read_text(encoding="utf-8"))
            preparation_plan = json.loads((run_dir / "artifacts" / "benchmark_preparation_plan.json").read_text(encoding="utf-8"))
            benchmark_execution_plan = json.loads((run_dir / "artifacts" / "benchmark_execution_plan.json").read_text(encoding="utf-8"))
            model_route_mapping = json.loads((run_dir / "artifacts" / "model_route_mapping.template.json").read_text(encoding="utf-8"))
            transfer_runner_plan = json.loads((run_dir / "artifacts" / "transfer_runner_plan.json").read_text(encoding="utf-8"))
            token_log_plan = json.loads((run_dir / "artifacts" / "token_log_plan.json").read_text(encoding="utf-8"))
            claim_rows = {row["claim_id"]: row for row in all_claim_matrix["claims"]}
            intake_rows = {row["source_key"]: row for row in intake_plan["tasks"]}
            status_rows = {row["source_key"]: row for row in intake_status["tasks"]}
            execution_targets = {row["target_id"]: row for row in benchmark_execution_plan["targets"]}

            self.assertEqual(contract["target_id"], "skillgen_aime_smoke")
            self.assertEqual(command_plan["commands"]["eval_template"]["argv"][3], "{skill_output_dir}")
            self.assertTrue(instructions["readme_eval_cli_mismatch"])
            self.assertEqual(len(train_subset["instances"]), 8)
            self.assertIn("skillgen_aime_smoke_target", {item["id"] for item in hardcodings["hardcodings"]})
            self.assertGreaterEqual(all_claims["claim_count"], 10)
            self.assertEqual(claim_rows["claim_baseline_generator_comparison"]["status"], "not_testable")
            self.assertEqual(claim_rows["claim_tau_bench_gate_activated"]["status"], "blocked")
            self.assertIn("external_source_candidates", claim_rows["claim_chemllmbench_useful_gains"])
            self.assertIn("livecodebench", all_claim_matrix["official_support"]["external_source_candidates"])
            self.assertTrue(
                all_claim_matrix["official_support"]["external_source_candidates"]["livecodebench"][0][
                    "official_evidence_present"
                ]
            )
            self.assertIn("mcp_bench_all", intake_rows)
            self.assertEqual(intake_rows["mcp_bench_all"]["target_path"], "code/official/benchmarks/external/mcp-bench")
            self.assertIn("mcp_bench_all", status_rows)
            self.assertIn("livecodebench", {row["source_key"] for row in preparation_plan["tasks"]})
            self.assertIn("skillgen_aime", {target["target_id"] for target in all_claim_matrix["executable_targets"]})
            self.assertIn("scienceworld", execution_targets)
            self.assertEqual(execution_targets["alfworld_ood"]["status"], "blocked_missing_official_artifact")
            self.assertEqual(transfer_runner_plan["planned_off_diagonal_comparisons"], 120)
            self.assertEqual(model_route_mapping["status"], "route_resolved_with_equivalent_deviations")
            self.assertIn("ScienceWorld", {row["paper_name"] for row in token_log_plan["benchmark_groups"]})
            self.assertTrue((run_dir / "artifacts" / "approval.template.json").exists())

    def test_prepare_does_not_overwrite_existing_smoke_assets(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_idempotent_test")
            prepare_automation_artifacts(run_dir, official_source=source)

            train_subset_path = run_dir / "artifacts" / "smoke_data" / "aime_train_n8_seed42.json"
            config_path = run_dir / "artifacts" / "skillgen_aime_smoke_config.yaml"
            write_json(train_subset_path, {"dataset_id": "human_reviewed", "instances": []})
            config_path.write_text("human reviewed config\n", encoding="utf-8")

            prepare_automation_artifacts(run_dir, official_source=source)

            train_subset = json.loads(train_subset_path.read_text(encoding="utf-8"))
            self.assertEqual(train_subset["dataset_id"], "human_reviewed")
            self.assertEqual(config_path.read_text(encoding="utf-8"), "human reviewed config\n")

    def test_install_execution_blocks_without_machine_readable_approval(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_block_test")
            prepare_automation_artifacts(run_dir, official_source=source)

            status = execute_install(run_dir)

            self.assertEqual(status, STATUS_BLOCKED)
            failure_modes = (run_dir / "artifacts" / "failure_modes.md").read_text(encoding="utf-8")
            self.assertIn("missing artifacts/approval.json", failure_modes)

    def test_approval_artifact_allows_install_gate_without_api_keys(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_approval_test")
            prepare_automation_artifacts(run_dir, official_source=source)

            write_approval_artifact(
                run_dir,
                approved_by="tester",
                max_cost_usd=1.25,
                notes="Unit-test approval only.",
                approval_source="unit_test",
            )

            approval = json.loads((run_dir / "artifacts" / "approval.json").read_text(encoding="utf-8"))
            allowed, reasons = approval_status(run_dir, "install")
            review = (run_dir / "artifacts" / "human_command_review.md").read_text(encoding="utf-8")

            self.assertTrue(allowed, reasons)
            self.assertEqual(approval["approval_source"], "unit_test")
            self.assertTrue(approval["allow_project_local_install"])
            self.assertTrue(approval["skip_install_if_environment_present"])
            self.assertTrue(approval["auto_retry_approved"])
            self.assertEqual(approval["max_retry_attempts"], 1)
            self.assertIn("Status: `approved`", review)
            self.assertIn("Auto retry approved steps: `True`", review)

    def test_parse_compare_report_from_structured_skillgen_outputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            artifacts = run_dir / "artifacts"
            raw = artifacts / "raw_benchmark_outputs" / "skillgen_aime_smoke"
            write_json(run_dir / "input" / "input_manifest.json", {"run_id": "run", "paper_source_path": "paper.pdf"})
            build_verification_contract(run_dir)

            write_json(
                raw / "eval_results.json",
                {
                    "skill_id": "skill-1",
                    "dataset": "aime_test.json",
                    "results": [
                        {
                            "model": "openai/gpt-5.4-nano",
                            "n_instances": 4,
                            "baseline_acc": 0.5,
                            "skill_acc": 0.25,
                            "delta_acc": -0.25,
                            "repair": 0,
                            "regression": 1,
                            "net_gain": -1,
                            "blank_filter": {"drop_blank": True},
                        }
                    ],
                },
            )
            write_json(
                raw / "eval_results.token_usage.json",
                [
                    {"total_tokens": 10},
                    {"total_tokens": 20},
                ],
            )
            write_json(
                raw / "artifacts" / "runs" / "run1" / "verification" / "round_1" / "verification_summary.json",
                {
                    "result": {
                        "paired_n": 4,
                        "baseline_acc": 0.5,
                        "skill_acc": 0.75,
                        "repair_count": 2,
                        "regression_count": 1,
                        "net_gain": 1,
                        "passed": True,
                    }
                },
            )
            write_json(raw / "skill_output" / "2026-06-01_00-00-00" / "skill-1.json", {"id": "skill-1"})

            parse_compare_report(run_dir)

            benchmark = json.loads((artifacts / "benchmark_results.json").read_text(encoding="utf-8"))
            comparison = json.loads((artifacts / "claim_comparison.json").read_text(encoding="utf-8"))
            report = (artifacts / "research_validation_report.md").read_text(encoding="utf-8")

            self.assertEqual(benchmark["eval"]["token_usage_total"], 30)
            self.assertEqual(comparison["smoke_status"], "not_reproduced")
            self.assertIn("SkillGen Phase 0 Automated Validation Report", report)
            self.assertIn("## Status Explanations", report)
            self.assertIn("Compared / required evidence", report)
            self.assertIn("Reason for status", report)
            self.assertIn("held-out smoke result did not satisfy", report)


if __name__ == "__main__":
    unittest.main()
