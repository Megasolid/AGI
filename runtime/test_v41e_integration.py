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

    @unittest.skipUnless((REPO / "DNA.md").exists() and (REPO / "citadel/inputs/v41e/baseline-hashes.json").exists(),
                         "release baseline files not present in this checkout")
    def test_protected_baseline_unchanged(self):
        """Compare COMMITTED BLOB bytes, never the worktree.

        The worktree applies .gitattributes (eol=lf) and line endings vary per OS,
        so hashing the checkout is not portable. The blob-anchored manifest v2 is
        the authoritative anchor.
        """
        manifest = json.loads(
            (REPO / "citadel/inputs/v41e/baseline-hashes-2.json").read_text(encoding="utf-8"))
        entries = manifest.get("protected_files") or manifest.get("protected_repo_files")
        for rel, val in entries.items():
            expected = val.get("sha256") if isinstance(val, dict) else val
            sha = subprocess.run(["git", "-C", str(REPO), "rev-parse", f"HEAD:{rel}"],
                                 capture_output=True, text=True)
            self.assertEqual(sha.returncode, 0, f"{rel} not in HEAD")
            blob = subprocess.run(["git", "-C", str(REPO), "cat-file", "-p", sha.stdout.strip()],
                                  capture_output=True)
            self.assertEqual(hashlib.sha256(blob.stdout).hexdigest(), expected, rel)

    @unittest.skipUnless((REPO / ".git").exists() and shutil.which("git") is not None,
                         "git checkout not available in this environment")
    def test_v401_is_ancestor(self):
        proc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "v4.0.1", "HEAD"])
        self.assertEqual(proc.returncode, 0)

    def test_additive_runtime_imports(self):
        import agi_capability, agi_context, agi_evidence, agi_handoff, agi_operator, agi_sem
        self.assertTrue(all((agi_capability, agi_context, agi_evidence, agi_handoff,
                             agi_operator, agi_sem)))


if __name__ == "__main__":
    unittest.main()
