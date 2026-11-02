import tempfile
import unittest
from pathlib import Path

from agi_evidence import (
    EffectLedger, EvidenceError, RecoveryController, RecoveryError, gap_check,
    make_packet, reconcile, validate_packet,
)


def packet():
    return make_packet(run_id="run-1", claim="bounded claim", evidence_refs=["sha256:a", "sha256:b"],
                       environment={"host": "test", "model": "mock"}, e_level="E1",
                       artifact_hashes={"out.txt": "c" * 64})


class EvidenceTests(unittest.TestCase):
    def test_packet_roundtrip_and_gap(self):
        p = packet(); validate_packet(p)
        self.assertTrue(gap_check(p, ["sha256:a"])["ok"])
        self.assertFalse(gap_check(p, ["sha256:z"])["ok"])

    def test_missing_refs_fails(self):
        with self.assertRaisesRegex(EvidenceError, "refs"):
            make_packet(run_id="r", claim="c", evidence_refs=[], environment={"h": "x"},
                        e_level="E1", artifact_hashes={"a": "b"})

    def test_tamper_detected(self):
        p = packet(); p["claim"] = "changed"
        with self.assertRaisesRegex(EvidenceError, "digest mismatch"):
            validate_packet(p)

    def test_invalid_e_level(self):
        with self.assertRaisesRegex(EvidenceError, "E-level"):
            make_packet(run_id="r", claim="c", evidence_refs=["x"], environment={"h": "x"},
                        e_level="E9", artifact_hashes={"a": "b"})


class LedgerTests(unittest.TestCase):
    def test_append_idempotent_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            l = EffectLedger(Path(td) / "effects.jsonl")
            l.append("e1", "write", "emitted", "r1")
            l.append("e1", "write", "emitted", "r1")
            with self.assertRaisesRegex(EvidenceError, "different content"):
                l.append("e1", "write", "emitted", "r2")

    def test_reconcile_emitted_not_discarded(self):
        with tempfile.TemporaryDirectory() as td:
            l = EffectLedger(Path(td) / "effects.jsonl")
            l.append("e1", "write", "emitted", "r1")
            l.append("e2", "network", "emitted", "r2")
            r = reconcile([{"effect_id": "e1"}], l.effects())
            self.assertFalse(r["ok"])
            self.assertEqual([e["effect_id"] for e in r["emitted_not_in_checkpoint"]], ["e2"])

    def test_corrupt_ledger_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "effects.jsonl"; p.write_text("not json\n", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceError, "corrupt"):
                EffectLedger(p)


class RecoveryTests(unittest.TestCase):
    def test_requires_verified_then_resume(self):
        r = RecoveryController(); r.isolate(); r.replay()
        self.assertEqual(r.verify(state_digest_ok=False, effects_reconciled=True, lease_valid=True), "incident")
        r2 = RecoveryController(); r2.isolate(); r2.replay()
        self.assertEqual(r2.verify(state_digest_ok=True, effects_reconciled=True, lease_valid=True), "verified")
        self.assertEqual(r2.resume(), "resumed")

    def test_resume_before_verified_fails(self):
        r = RecoveryController()
        with self.assertRaisesRegex(EvidenceError, "verified"):
            r.resume()

    def test_lease_invalid_blocks_verified(self):
        r = RecoveryController(); r.isolate(); r.replay()
        self.assertEqual(r.verify(state_digest_ok=True, effects_reconciled=True, lease_valid=False), "incident")


if __name__ == "__main__":
    unittest.main()
