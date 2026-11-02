import tempfile
import unittest
from pathlib import Path

from agi_operator import (
    ApprovalBridge, CancellationController, LeaseStore, OperatorError, PolicyGate,
    ServiceRegistry,
)
from agi_operator_journal import JournalError, OperatorJournal

NOW = "2026-11-02T00:00:00+00:00"


class ServiceTests(unittest.TestCase):
    def test_lifecycle(self):
        r = ServiceRegistry(); r.register("p", start=lambda: None, stop=lambda: None)
        self.assertEqual(r.start("p")["state"], "active")
        self.assertEqual(r.drain("p")["state"], "draining")
        self.assertEqual(r.stop("p")["state"], "removed")

    def test_start_failure(self):
        r = ServiceRegistry()
        def bad(): raise RuntimeError("boom")
        r.register("p", start=bad, stop=lambda: None)
        with self.assertRaises(RuntimeError):
            r.start("p")
        self.assertEqual(r.state("p"), "failed")

    def test_stop_failure(self):
        r = ServiceRegistry(); r.register("p", start=lambda: None, stop=lambda: (_ for _ in ()).throw(RuntimeError()))
        r.start("p")
        with self.assertRaises(RuntimeError):
            r.stop("p")
        self.assertEqual(r.state("p"), "failed")

    def test_duplicate_provider(self):
        r = ServiceRegistry(); r.register("p", start=lambda: None, stop=lambda: None)
        with self.assertRaisesRegex(OperatorError, "duplicate"):
            r.register("p", start=lambda: None, stop=lambda: None)


class PolicyTests(unittest.TestCase):
    def test_deny_is_monotonic(self):
        gate = PolicyGate(); seen = []
        def deny(req): seen.append("deny"); return "blocked"
        def later(req): seen.append("later"); return True
        gate.add_guard(deny); gate.add_guard(later)
        self.assertEqual(gate.decide({})["result"], "deny")
        self.assertEqual(seen, ["deny"])

    def test_guard_exception_denies(self):
        gate = PolicyGate(); gate.add_guard(lambda req: (_ for _ in ()).throw(RuntimeError()))
        self.assertEqual(gate.decide({})["result"], "deny")

    def test_allow(self):
        gate = PolicyGate(); gate.add_guard(lambda req: True)
        self.assertEqual(gate.decide({})["result"], "allow")


class CancellationTests(unittest.TestCase):
    def test_quiescence_required(self):
        c = CancellationController(); c.request(); c.accept(); c.stopping()
        c.add_effect("e1")
        with self.assertRaisesRegex(OperatorError, "not quiesced"):
            c.quiesce()
        c.mark_stopped("e1")
        self.assertEqual(c.quiesce(), "quiesced")
        self.assertEqual(c.record(), "recorded")

    def test_duplicate_effect(self):
        c = CancellationController(); c.request(); c.accept(); c.stopping()
        c.add_effect("e1")
        with self.assertRaisesRegex(OperatorError, "duplicate"):
            c.add_effect("e1")

    def test_failure(self):
        c = CancellationController(); c.request(); c.accept(); c.stopping()
        self.assertEqual(c.fail("stuck"), "failed")


class LeaseTests(unittest.TestCase):
    def test_split_brain_refused(self):
        s = LeaseStore(); s.acquire("br", "a", epoch=1, now=NOW)
        with self.assertRaisesRegex(OperatorError, "split-brain"):
            s.acquire("br", "b", epoch=2, now=NOW)

    def test_stale_epoch_denied(self):
        s = LeaseStore(); s.acquire("br", "a", epoch=1, now=NOW)
        s.check_write("br", 1, now=NOW)
        with self.assertRaisesRegex(OperatorError, "stale"):
            s.check_write("br", 0, now=NOW)

    def test_expiry_and_takeover(self):
        s = LeaseStore(); s.acquire("br", "a", epoch=1, ttl_s=1, now=NOW)
        s.acquire("br", "b", epoch=2, ttl_s=60, now="2026-11-02T00:00:02+00:00")
        with self.assertRaisesRegex(OperatorError, "stale"):
            s.check_write("br", 1, now="2026-11-02T00:00:02+00:00")
        s.check_write("br", 2, now="2026-11-02T00:00:02+00:00")

    def test_release(self):
        s = LeaseStore(); s.acquire("br", "a", epoch=1, now=NOW)
        s.release("br", operator="a", epoch=1)
        with self.assertRaisesRegex(OperatorError, "released"):
            s.check_write("br", 1, now=NOW)


class JournalTests(unittest.TestCase):
    def test_append_read_verify(self):
        with tempfile.TemporaryDirectory() as td:
            j = OperatorJournal(Path(td) / "j.jsonl")
            j.append("e1", "task", {"x": 1})
            j.append("e2", "task", {"x": 2})
            self.assertEqual(j.last_seq, 2)
            self.assertEqual(len(j.read_from(1)), 2)
            self.assertTrue(j.verify()["ok"])

    def test_idempotent_and_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            j = OperatorJournal(Path(td) / "j.jsonl")
            j.append("e1", "task", {"x": 1})
            j.append("e1", "task", {"x": 1})
            with self.assertRaisesRegex(JournalError, "different content"):
                j.append("e1", "task", {"x": 2})

    def test_event_loss(self):
        with tempfile.TemporaryDirectory() as td:
            j = OperatorJournal(Path(td) / "j.jsonl")
            j.append("e1", "task", {"x": 1})
            with self.assertRaisesRegex(JournalError, "event loss"):
                j.read_from(3)

    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "j.jsonl"
            j = OperatorJournal(p); j.append("e1", "task", {"x": 1})
            text = p.read_text(encoding="utf-8").replace('"x":1', '"x":9')
            p.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(JournalError, "digest mismatch"):
                OperatorJournal(p)


class ApprovalTests(unittest.TestCase):
    def test_client_decision_is_not_authority(self):
        b = ApprovalBridge(); req = b.request("read", "needed")
        rec = b.record_client_decision(req["approval_id"], "accept")
        self.assertEqual(rec["decision"], "accept")
        self.assertIn("not consent", rec["note"])
        self.assertFalse(hasattr(b, "authorize"))
        self.assertFalse(hasattr(b, "grant"))

    def test_invalid_decision(self):
        b = ApprovalBridge(); req = b.request("read")
        with self.assertRaisesRegex(OperatorError, "invalid decision"):
            b.record_client_decision(req["approval_id"], "allow")


if __name__ == "__main__":
    unittest.main()
