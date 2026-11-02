import json
import tempfile
import unittest
from pathlib import Path

from agi_findings_validate import main, validate

TASK_HASH = "sha256:" + "a" * 64
BUNDLE = "sha256:" + "b" * 64
BYTES = 12345
MANIFEST = 20


def good():
    return {
        "schema": "agi-citadel/report/0.1",
        "task_id": "v41e-v-14",
        "station": "kilo",
        "decision": "PASS",
        "checks": [{"id": "PV-01", "decision": "PASS", "evidence": "ok"}],
        "findings": [],
        "evidence": {
            "task_hash": TASK_HASH + " (MATCH)",
            "bundle_sha256": BUNDLE + " (MATCH)",
            "bundle_bytes": BYTES,
            "manifest_count": MANIFEST,
            "signature": {"alg": "ML-DSA-65", "key_id": "a73eaa5d3c31e009", "crypto_verified": False},
        },
    }


def run(doc):
    return validate(doc, task_hash=TASK_HASH, bundle_sha256=BUNDLE,
                    bundle_bytes=BYTES, manifest_count=MANIFEST)


class ValidationTests(unittest.TestCase):
    def test_good_findings_pass(self):
        r = run(good())
        self.assertTrue(r["ok"], r)

    def test_v13_task_id_defect_fails(self):
        doc = good(); doc["task_id"] = "v41e-v-11"
        self.assertFalse(run(doc)["ok"])

    def test_v12_stale_bundle_fails(self):
        doc = good(); doc["evidence"]["bundle_sha256"] = "sha256:" + "c" * 64
        self.assertFalse(run(doc)["ok"])

    def test_v12_stale_v10_hash_fails(self):
        doc = good()
        doc["evidence"]["bundle_sha256"] = "sha256:205d22f39d128dd8666822a7d570bbd46f499b207d2ba48c2f36ad7f7d8651c1"
        self.assertFalse(run(doc)["ok"])

    def test_wrong_byte_count_fails(self):
        doc = good(); doc["evidence"]["bundle_bytes"] = 26916
        self.assertFalse(run(doc)["ok"])

    def test_wrong_manifest_count_fails(self):
        doc = good(); doc["evidence"]["manifest_count"] = 8
        self.assertFalse(run(doc)["ok"])

    def test_false_crypto_verified_warns(self):
        doc = good(); doc["evidence"]["signature"]["crypto_verified"] = True
        r = run(doc)
        self.assertTrue(r["ok"])
        self.assertTrue(r["warnings"])

    def test_missing_key_fails(self):
        doc = good(); doc.pop("checks")
        self.assertFalse(run(doc)["ok"])

    def test_invalid_decision_fails(self):
        doc = good(); doc["decision"] = "MAYBE"
        self.assertFalse(run(doc)["ok"])

    def test_cli_ok_and_bad(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.json"
            p.write_text(json.dumps(good()), encoding="utf-8")
            args = [str(p), "--task-hash", TASK_HASH, "--bundle-sha256", BUNDLE,
                    "--bundle-bytes", str(BYTES), "--manifest-count", str(MANIFEST)]
            self.assertEqual(main(args), 0)
            bad = good(); bad["task_id"] = "v41e-v-12"
            p.write_text(json.dumps(bad), encoding="utf-8")
            self.assertEqual(main(args), 1)


if __name__ == "__main__":
    unittest.main()
