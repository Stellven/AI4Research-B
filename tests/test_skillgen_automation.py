from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import unittest

from ai4research_b.phase0.skillgen_automation import (
    STATUS_BLOCKED,
    STATUS_READY_FOR_EXECUTION,
    approval_status,
    build_benchmark_execution_plan,
    build_transfer_runner_plan,
    build_verification_contract,
    execute_install,
    parse_compare_report,
    prepare_automation_artifacts,
    prepare_livecodebench_split,
    run_full_matrix_entries,
    write_execution_planning_artifacts,
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


def make_livecodebench_instances(n: int) -> list[dict[str, object]]:
    return [
        {
            "instance_id": f"lcb_{index}",
            "input": f"solve problem {index}",
            "ground_truth": None,
            "metadata": {
                "benchmark": "livecodebench",
                "question_id": f"question_{index}",
                "contest_id": index // 5,
                "contest_date": f"2025-04-{(index % 28) + 1:02d}",
            },
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
    write_json(
        source / "data" / "livecodebench" / "release_v6_all.json",
        {
            "dataset_id": "livecodebench_release_v6",
            "task_name": "livecodebench_release_v6_competitive_programming",
            "task_type": "binary",
            "instances": make_livecodebench_instances(230),
        },
    )
    return source


def add_fake_alfworld_source(source: Path) -> None:
    alfworld = source / "benchmarks" / "external" / "alfworld"
    alfworld.mkdir(parents=True, exist_ok=True)
    (alfworld / "README.md").write_text("ALFWorld fixture\n", encoding="utf-8")


def add_fake_alfworld_data(source: Path) -> None:
    for split, n_train, n_test in [("alfworld_iod", 6, 4), ("alfworld_ood", 6, 4)]:
        write_json(
            source / "data" / split / "train.json",
            {
                "dataset_id": f"{split}_train",
                "task_name": split,
                "task_type": "binary",
                "metadata": {"reconstruction": "offline_plan_adapter_fixture"},
                "instances": make_instances(n_train),
            },
        )
        write_json(
            source / "data" / split / "test.json",
            {
                "dataset_id": f"{split}_test",
                "task_name": split,
                "task_type": "binary",
                "metadata": {"reconstruction": "offline_plan_adapter_fixture"},
                "instances": make_instances(n_test),
            },
        )


def write_fake_alfworld_group_a_docs(run_dir: Path) -> None:
    docs = {
        "artifacts/03_code_and_sources/alfworld_source_review.md": "# ALFWorld Source Review\n",
        "artifacts/06_plans_and_contracts/alfworld_adapter_contract.md": "# ALFWorld Adapter Contract\n",
        "artifacts/06_plans_and_contracts/alfworld_split_contract.md": "# ALFWorld Split Contract\n",
        "artifacts/09_safety_and_deviations/alfworld_deviation_note.md": "# ALFWorld Deviation Note\n",
    }
    for relative_path, body in docs.items():
        path = run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")


class SkillGenAutomationTest(unittest.TestCase):
    def test_prepare_defaults_to_minimal_artifact_set(self) -> None:
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
            automation_state = json.loads((run_dir / "artifacts" / "automation_state.json").read_text(encoding="utf-8"))
            approval_template = json.loads((run_dir / "artifacts" / "approval.template.json").read_text(encoding="utf-8"))

            self.assertEqual(contract["target_id"], "skillgen_aime_smoke")
            self.assertEqual(command_plan["commands"]["eval_template"]["argv"][3], "{skill_output_dir}")
            self.assertTrue(instructions["readme_eval_cli_mismatch"])
            self.assertEqual(len(train_subset["instances"]), 8)
            self.assertEqual(automation_state["artifact_mode"], "minimal")
            self.assertFalse(automation_state["long_inference_approved"])
            self.assertFalse(approval_template["long_inference_approved"])
            self.assertFalse((run_dir / "artifacts" / "all_claims.json").exists())
            self.assertFalse((run_dir / "artifacts" / "all_claim_verification_matrix.json").exists())
            self.assertFalse((run_dir / "artifacts" / "external_source_intake_plan.json").exists())
            self.assertFalse((run_dir / "artifacts" / "benchmark_execution_plan.json").exists())
            self.assertFalse((run_dir / "artifacts" / "model_route_mapping.template.json").exists())
            self.assertFalse((run_dir / "artifacts" / "transfer_runner_plan.json").exists())
            self.assertFalse((run_dir / "artifacts" / "full_matrix_execution_contract.json").exists())
            self.assertFalse((run_dir / "artifacts" / "transfer_execution_contract.json").exists())
            self.assertFalse((run_dir / "artifacts" / "figure7_trace_extraction_contract.json").exists())
            self.assertFalse((run_dir / "artifacts" / "per_round_trace_retention_checklist.json").exists())
            self.assertFalse((run_dir / "artifacts" / "token_log_plan.json").exists())
            self.assertFalse((run_dir / "artifacts" / "baseline_source_identity_review.json").exists())
            self.assertFalse((run_dir / "artifacts" / "baseline_single_skill_adapter_contract.json").exists())
            self.assertFalse((run_dir / "artifacts" / "baseline_deviation_note.md").exists())
            self.assertFalse((run_dir / "artifacts" / "reconstructed_ablation_contract.json").exists())
            self.assertFalse((run_dir / "artifacts" / "ablation_config_matrix.json").exists())
            self.assertFalse((run_dir / "artifacts" / "ablation_smoke_plan.json").exists())
            self.assertFalse((run_dir / "artifacts" / "ablation_deviation_note.md").exists())
            self.assertTrue((run_dir / "artifacts" / "approval.template.json").exists())

    def test_prepare_with_long_inference_approved_writes_expanded_artifacts(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_long_artifacts_test")
            write_approval_artifact(
                run_dir,
                approved_by="tester",
                max_cost_usd=1.25,
                notes="Unit-test long artifact approval only.",
                approval_source="unit_test",
                long_inference_approved=True,
            )

            prepare_automation_artifacts(run_dir, official_source=source)

            hardcodings = json.loads((run_dir / "artifacts" / "hardcoding_disclosures.json").read_text(encoding="utf-8"))
            all_claims = json.loads((run_dir / "artifacts" / "all_claims.json").read_text(encoding="utf-8"))
            all_claim_matrix = json.loads((run_dir / "artifacts" / "all_claim_verification_matrix.json").read_text(encoding="utf-8"))
            intake_plan = json.loads((run_dir / "artifacts" / "external_source_intake_plan.json").read_text(encoding="utf-8"))
            intake_status = json.loads((run_dir / "artifacts" / "external_source_intake_status.json").read_text(encoding="utf-8"))
            preparation_plan = json.loads((run_dir / "artifacts" / "benchmark_preparation_plan.json").read_text(encoding="utf-8"))
            benchmark_execution_plan = json.loads((run_dir / "artifacts" / "benchmark_execution_plan.json").read_text(encoding="utf-8"))
            model_route_mapping = json.loads((run_dir / "artifacts" / "model_route_mapping.template.json").read_text(encoding="utf-8"))
            transfer_runner_plan = json.loads((run_dir / "artifacts" / "transfer_runner_plan.json").read_text(encoding="utf-8"))
            full_matrix_contract = json.loads((run_dir / "artifacts" / "full_matrix_execution_contract.json").read_text(encoding="utf-8"))
            transfer_contract = json.loads((run_dir / "artifacts" / "transfer_execution_contract.json").read_text(encoding="utf-8"))
            figure7_contract = json.loads((run_dir / "artifacts" / "figure7_trace_extraction_contract.json").read_text(encoding="utf-8"))
            trace_checklist = json.loads((run_dir / "artifacts" / "per_round_trace_retention_checklist.json").read_text(encoding="utf-8"))
            token_log_plan = json.loads((run_dir / "artifacts" / "token_log_plan.json").read_text(encoding="utf-8"))
            baseline_review = json.loads((run_dir / "artifacts" / "baseline_source_identity_review.json").read_text(encoding="utf-8"))
            baseline_adapter = json.loads((run_dir / "artifacts" / "baseline_single_skill_adapter_contract.json").read_text(encoding="utf-8"))
            baseline_deviation = (run_dir / "artifacts" / "baseline_deviation_note.md").read_text(encoding="utf-8")
            ablation_contract = json.loads((run_dir / "artifacts" / "reconstructed_ablation_contract.json").read_text(encoding="utf-8"))
            ablation_config_matrix = json.loads((run_dir / "artifacts" / "ablation_config_matrix.json").read_text(encoding="utf-8"))
            ablation_smoke_plan = json.loads((run_dir / "artifacts" / "ablation_smoke_plan.json").read_text(encoding="utf-8"))
            ablation_deviation = (run_dir / "artifacts" / "ablation_deviation_note.md").read_text(encoding="utf-8")
            automation_state = json.loads((run_dir / "artifacts" / "automation_state.json").read_text(encoding="utf-8"))
            claim_rows = {row["claim_id"]: row for row in all_claim_matrix["claims"]}
            intake_rows = {row["source_key"]: row for row in intake_plan["tasks"]}
            status_rows = {row["source_key"]: row for row in intake_status["tasks"]}
            execution_targets = {row["target_id"]: row for row in benchmark_execution_plan["targets"]}

            self.assertEqual(automation_state["artifact_mode"], "full")
            self.assertTrue(automation_state["long_inference_approved"])
            self.assertEqual(
                automation_state["baseline_comparison_status"],
                "blocked_pending_baseline_source_identity_review",
            )
            self.assertIn("skillgen_aime_smoke_target", {item["id"] for item in hardcodings["hardcodings"]})
            self.assertGreaterEqual(all_claims["claim_count"], 10)
            self.assertEqual(
                all_claim_matrix["status_model"]["status"],
                "Backward-compatible alias for claim_verdict_status.",
            )
            self.assertEqual(
                claim_rows["claim_baseline_generator_comparison"]["claim_verdict_status"],
                "blocked",
            )
            self.assertEqual(
                claim_rows["claim_baseline_generator_comparison"]["status"],
                "blocked",
            )
            self.assertEqual(
                claim_rows["claim_baseline_generator_comparison"]["execution_readiness_status"],
                "ready_for_source_identity_review",
            )
            self.assertEqual(
                claim_rows["claim_ablation_full_wins"]["status"],
                "blocked",
            )
            self.assertEqual(
                claim_rows["claim_ablation_full_wins"]["execution_readiness_status"],
                "ready_for_reconstructed_ablation_human_review",
            )
            self.assertEqual(claim_rows["claim_tau_bench_gate_activated"]["status"], "blocked")
            self.assertEqual(
                claim_rows["claim_tau_bench_gate_activated"]["execution_readiness_status"],
                "blocked_pending_tau_bench_source_intake",
            )
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
            self.assertIn(
                execution_targets["alfworld_ood"]["status"],
                {"blocked_missing_official_artifact", "ready_for_reconstructed_execution"},
            )
            if execution_targets["alfworld_ood"]["status"] == "ready_for_reconstructed_execution":
                self.assertEqual(execution_targets["alfworld_ood"]["group_a_contract"]["missing_documents"], [])
            self.assertEqual(transfer_runner_plan["planned_off_diagonal_comparisons"], 120)
            self.assertEqual(full_matrix_contract["entry_count"]["paper_required"], 80)
            self.assertEqual(full_matrix_contract["aggregation_rules"][1]["claim_id"], "claim_table1_entry_counts")
            self.assertEqual(transfer_contract["matrix_dimensions"]["paper_required_comparisons"], 120)
            self.assertIn("non_negative_rate", transfer_contract["aggregation_rules"][0])
            self.assertEqual(figure7_contract["round_record_schema"]["round_index"], "integer")
            self.assertIn("verification_case_analyses", figure7_contract["trace_globs"])
            self.assertIn("candidate_skill_artifact", {check["id"] for check in trace_checklist["checks"]})
            self.assertEqual(model_route_mapping["status"], "route_resolved_with_equivalent_deviations")
            self.assertIn("ScienceWorld", {row["paper_name"] for row in token_log_plan["benchmark_groups"]})
            self.assertEqual(baseline_review["status"], "blocked_pending_baseline_source_identity_review")
            self.assertEqual(baseline_review["source_count"], 4)
            self.assertEqual(
                {row["method_name"] for row in baseline_review["baselines"]},
                {"Trace2Skill", "SkillX", "EvoSkill", "CoEvoSkills"},
            )
            self.assertEqual(baseline_adapter["status"], "blocked_pending_baseline_source_identity_review")
            self.assertIn("public-code reconstructed verification path", baseline_deviation)
            self.assertEqual(ablation_contract["reproduction_class"], "deviation_backed_reconstructed_verification")
            self.assertEqual({row["arm_id"] for row in ablation_config_matrix["rows"]}, {"Full", "A1", "A2", "A3", "A4", "A5"})
            self.assertEqual(ablation_smoke_plan["status"], "ready_for_reconstructed_ablation_execution")
            self.assertIn("A3", ablation_smoke_plan["expected_outputs"])
            self.assertIn("deviation-backed reconstructed verification plan", ablation_deviation)

    def test_livecodebench_group_b_split_generates_ready_execution_target(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_livecodebench_split_test")
            prepare_automation_artifacts(run_dir, official_source=source)

            manifest = prepare_livecodebench_split(run_dir)
            train = json.loads(
                (run_dir / "code" / "official" / "data" / "livecodebench" / "train_release_v6_n50_seed42.json").read_text(
                    encoding="utf-8"
                )
            )
            test = json.loads(
                (run_dir / "code" / "official" / "data" / "livecodebench" / "test_release_v6_n150_seed42.json").read_text(
                    encoding="utf-8"
                )
            )
            contract = json.loads((run_dir / "artifacts" / "livecodebench_split_contract.json").read_text(encoding="utf-8"))
            execution_plan = build_benchmark_execution_plan(run_dir)
            execution_targets = {row["target_id"]: row for row in execution_plan["targets"]}

            self.assertEqual(manifest["status"], STATUS_READY_FOR_EXECUTION)
            self.assertEqual(manifest["source_total_instances"], 230)
            self.assertEqual(len(train["instances"]), 50)
            self.assertEqual(len(test["instances"]), 150)
            self.assertFalse(set(manifest["train"]["instance_ids"]) & set(manifest["test"]["instance_ids"]))
            self.assertEqual(contract["status"], STATUS_READY_FOR_EXECUTION)
            self.assertEqual(contract["deviation_classification"], "paper_matching_inferred_split")
            self.assertEqual(execution_targets["livecodebench"]["status"], STATUS_READY_FOR_EXECUTION)
            self.assertEqual(execution_targets["livecodebench"]["dataset"]["train_n"], 50)
            self.assertEqual(execution_targets["livecodebench"]["dataset"]["test_n"], 150)

    def test_full_matrix_runner_dry_run_plans_openai_first_and_generates_configs(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            run_dir = run_demo(paper, temp / "runs", "skillgen_full_matrix_runner_test")
            write_approval_artifact(
                run_dir,
                approved_by="tester",
                max_cost_usd=1.25,
                notes="Unit-test full matrix dry-run only.",
                approval_source="unit_test",
                long_inference_approved=True,
            )
            prepare_automation_artifacts(run_dir, official_source=source)
            prepare_livecodebench_split(run_dir)
            (run_dir / "artifacts" / "09_safety_and_deviations").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts" / "09_safety_and_deviations" / "reconstructed_validation_path_index.md").write_text(
                "# Reconstructed Validation Path Index\n",
                encoding="utf-8",
            )
            write_execution_planning_artifacts(run_dir)

            state = run_full_matrix_entries(run_dir, max_entries=2, dry_run=True)

            self.assertEqual(state["status"], "dry_run_completed")
            self.assertEqual(
                state["selected_entry_ids"],
                [
                    "livecodebench::GPT-5.4-Nano",
                    "livecodebench::GPT-5.4-Mini",
                ],
            )
            self.assertTrue(state["source_artifacts"]["reconstructed_validation_path_index"])
            self.assertTrue(state["source_artifacts"]["provider_resolution_status"])
            self.assertIn("provider_resolution_status", state)
            self.assertGreater(
                state["counts"].get("waiting_provider_route_resolution", 0)
                + state["counts"].get("provider_unavailable", 0),
                0,
            )
            nano_config = run_dir / "artifacts" / "generated_configs" / "livecodebench" / "openai_gpt-5.4-nano.yaml"
            nano_config_mirror = (
                run_dir
                / "artifacts"
                / "07_configs_and_inputs"
                / "generated_configs"
                / "livecodebench"
                / "openai_gpt-5.4-nano.yaml"
            )
            self.assertTrue(nano_config.exists())
            self.assertTrue(nano_config_mirror.exists())
            selected_rows = {row["entry_id"]: row for row in state["entries"] if row["entry_id"] in state["selected_entry_ids"]}
            self.assertEqual(selected_rows["livecodebench::GPT-5.4-Nano"]["evidence_class"], "reconstructed_evidence")
            self.assertIn("direct_openai_provider_fallback", selected_rows["livecodebench::GPT-5.4-Nano"]["reconstruction_disclosures"])
            self.assertEqual(selected_rows["livecodebench::GPT-5.4-Nano"]["runner_status"], "not_started")
            self.assertTrue(selected_rows["livecodebench::GPT-5.4-Nano"]["dry_run_planned"])

    def test_full_matrix_runner_can_override_historical_openrouter_402_after_repair(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        previous_key = os.environ.get("OPENROUTER_API_KEY")
        os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
        with TemporaryDirectory() as temp_dir:
            try:
                temp = Path(temp_dir)
                source = make_fake_official_source(temp)
                run_dir = run_demo(paper, temp / "runs", "skillgen_openrouter_402_override_test")
                write_approval_artifact(
                    run_dir,
                    approved_by="tester",
                    max_cost_usd=1.25,
                    notes="Unit-test OpenRouter 402 override only.",
                    approval_source="unit_test",
                    long_inference_approved=True,
                )
                prepare_automation_artifacts(run_dir, official_source=source)
                prepare_livecodebench_split(run_dir)
                write_execution_planning_artifacts(run_dir)
                stderr_path = run_dir / "artifacts" / "08_results" / "raw_benchmark_outputs" / "historical" / "train_stderr.txt"
                stderr_path.parent.mkdir(parents=True, exist_ok=True)
                stderr_path.write_text("OpenRouter HTTP 402 insufficient credits\n", encoding="utf-8")

                blocked_state = run_full_matrix_entries(
                    run_dir,
                    max_entries=1,
                    dry_run=True,
                    target_subset={"livecodebench"},
                    model_subset={"Gemma-4-26B"},
                    include_non_openai=True,
                )
                override_state = run_full_matrix_entries(
                    run_dir,
                    max_entries=1,
                    dry_run=True,
                    target_subset={"livecodebench"},
                    model_subset={"Gemma-4-26B"},
                    include_non_openai=True,
                    allow_openrouter_after_402=True,
                )

                self.assertEqual(blocked_state["counts"].get("provider_unavailable"), 1)
                self.assertEqual(override_state["selected_entry_ids"], ["livecodebench::Gemma-4-26B"])
                selected = next(row for row in override_state["entries"] if row["entry_id"] == "livecodebench::Gemma-4-26B")
                self.assertEqual(selected["provider_runner_status"], "candidate_ready")
                self.assertIn("historical", selected["runner_reason"])
            finally:
                if previous_key is None:
                    os.environ.pop("OPENROUTER_API_KEY", None)
                else:
                    os.environ["OPENROUTER_API_KEY"] = previous_key

    def test_full_matrix_runner_marks_alfworld_reconstructed_evidence(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            add_fake_alfworld_source(source)
            add_fake_alfworld_data(source)
            run_dir = run_demo(paper, temp / "runs", "skillgen_full_matrix_alfworld_runner_test")
            write_approval_artifact(
                run_dir,
                approved_by="tester",
                max_cost_usd=1.25,
                notes="Unit-test reconstructed ALFWorld dry-run only.",
                approval_source="unit_test",
                long_inference_approved=True,
            )
            prepare_automation_artifacts(run_dir, official_source=source)
            write_fake_alfworld_group_a_docs(run_dir)
            write_execution_planning_artifacts(run_dir)

            state = run_full_matrix_entries(run_dir, max_entries=1, dry_run=True)

            self.assertEqual(state["selected_entry_ids"], ["alfworld_iod::GPT-5.4-Nano"])
            self.assertGreater(state["counts"]["budget_stopped"], 0)
            selected = next(row for row in state["entries"] if row["entry_id"] == "alfworld_iod::GPT-5.4-Nano")
            self.assertEqual(selected["evidence_class"], "reconstructed_evidence")
            self.assertIn(
                "canonical ALFWorld data + reconstructed SkillGen offline-plan adapter",
                selected["reconstruction_disclosures"],
            )
            self.assertIn("direct_openai_provider_fallback", selected["reconstruction_disclosures"])

    def test_alfworld_group_a_contract_updates_execution_plan_status(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = make_fake_official_source(temp)
            add_fake_alfworld_source(source)
            run_dir = run_demo(paper, temp / "runs", "skillgen_alfworld_group_a_test")
            prepare_automation_artifacts(run_dir, official_source=source)
            write_fake_alfworld_group_a_docs(run_dir)

            plan = build_benchmark_execution_plan(run_dir)
            targets = {target["target_id"]: target for target in plan["targets"]}
            transfer = build_transfer_runner_plan(run_dir, plan)
            transfer_rows = {row["benchmark_row"]: row for row in transfer["benchmarks"]}

            self.assertEqual(targets["alfworld_iod"]["status"], "ready_for_reconstructed_execution")
            self.assertEqual(targets["alfworld_ood"]["status"], "ready_for_reconstructed_execution")
            self.assertEqual(targets["alfworld_iod"]["paper_table1_entry_count"], 0)
            self.assertEqual(targets["alfworld_iod"]["group_a_contract"]["missing_documents"], [])
            self.assertIn("adapter implementation", "; ".join(targets["alfworld_ood"]["blockers"]))
            self.assertEqual(transfer_rows["alfworld_ood"]["dataset_status"], "ready_for_reconstructed_execution")
            self.assertIn("Group A reconstructed-execution contract", "; ".join(transfer["remaining_blockers"]))

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
            self.assertFalse(approval["long_inference_approved"])
            self.assertIn("Status: `approved`", review)
            self.assertIn("Auto retry approved steps: `True`", review)
            self.assertIn("Long inference approved: `False`", review)

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
            self.assertIn("## Artifact Mode", report)
            self.assertIn("`minimal`", report)
            self.assertIn("## Status Explanations", report)
            self.assertIn("held-out smoke result did not satisfy", report)
            self.assertFalse((artifacts / "all_claim_verification_matrix.json").exists())


if __name__ == "__main__":
    unittest.main()
