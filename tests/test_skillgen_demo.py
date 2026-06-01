from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import json

from ai4research_b.phase0.skillgen_demo import run_demo


class SkillGenDemoTest(unittest.TestCase):
    def test_demo_writes_blocked_phase0_artifacts(self) -> None:
        paper = Path("meeting docs/SkillGen.pdf")
        if not paper.exists():
            self.skipTest("SkillGen.pdf fixture is not present")

        with TemporaryDirectory() as temp_dir:
            run_dir = run_demo(paper, Path(temp_dir), "skillgen_test")

            self.assertTrue((run_dir / "input" / "input_manifest.json").exists())
            self.assertTrue((run_dir / "artifacts" / "paper_parse.json").exists())
            self.assertTrue((run_dir / "artifacts" / "claims.json").exists())
            self.assertTrue((run_dir / "artifacts" / "benchmark_claims.json").exists())
            self.assertTrue((run_dir / "artifacts" / "command_plan.json").exists())
            self.assertTrue((run_dir / "outputs" / "install_stdout.txt").exists())
            self.assertTrue((run_dir / "outputs" / "benchmark_stderr.txt").exists())
            command_plan = json.loads((run_dir / "artifacts" / "command_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(command_plan["official_code_urls"], ["https://github.com/yccm/SkillGen"])
            report = (run_dir / "artifacts" / "research_validation_report.md").read_text(encoding="utf-8")
            self.assertIn("`blocked`", report)
            self.assertIn("SkillGen improves average held-out accuracy", report)


if __name__ == "__main__":
    unittest.main()
