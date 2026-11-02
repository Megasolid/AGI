import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from agi_v41e import run_smoke

REPO = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    def test_smoke_all_steps(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_smoke(td)
        self.assertTrue(result["ok"], result)
        for step in ("E1_context", "E4_handoff", "E2_sem", "E3_operator",
                     "E5_capability", "E6_evidence"):
            self.assertTrue(result["steps"][step], step)

    def test_protected_baseline_unchanged(self):
        baseline = json.loads((REPO / "citadel/inputs/v41e/baseline-hashes.json").read_text(encoding="utf-8"))
        for rel, expected in baseline["protected_repo_files"].items():
            actual = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel)

    def test_v401_is_ancestor(self):
        if shutil.which("git") is None:
            self.skipTest("git unavailable")
        proc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "v4.0.1", "HEAD"])
        self.assertEqual(proc.returncode, 0)

    def test_additive_runtime_imports(self):
        import agi_capability, agi_context, agi_evidence, agi_handoff, agi_operator, agi_sem
        self.assertTrue(all((agi_capability, agi_context, agi_evidence, agi_handoff,
                             agi_operator, agi_sem)))


if __name__ == "__main__":
    unittest.main()
