import hashlib
import unittest
from datetime import timedelta

from agi_sem import (
    SemError, SemSession, canonical_json, check_constraints, constraint_digest,
    make_message, message_digest, validate_constraints, verify_semantics,
)

TS = "2026-11-02T00:00:00+00:00"
EXP = "2026-11-03T00:00:00+00:00"
NOW = TS


def constraint():
    c = {"id": "C1", "kind": "MUST_NOT", "text": "no write outside branch",
         "machine_check": "no_write", "source": "task", "enforcement": "runtime"}
    c["digest"] = constraint_digest(c)
    return c


def msg(mtype, seq, *, sender="mind-a", receiver="mind-b", body=None,
        constraints=None, mid=None, expires=EXP):
    return make_message(
        message_type=mtype, session_id="s1", message_id=mid or f"m-{mtype}-{seq}-{sender}",
        sequence=seq, from_ref=sender, to_ref=receiver, body=body or {},
        constraints=constraints or [], ts=TS, expires_at=expires,
    )


def handshake(s):
    s.receive(msg("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}), now=NOW)
    s.receive(msg("HELLO_ACK", 1, sender="mind-b", body={"version": "0.2"}), now=NOW)
    s.receive(msg("CAPABILITIES", 2, body={"classes": ["reasoning"]}), now=NOW)


def to_receipt(s, receipt=None):
    handshake(s)
    s.receive(msg("INTENT", 3, body={"goal": "read the file and summarize"},
                  constraints=[constraint()]), now=NOW)
    body = receipt or {
        "own_words": "I will read only and summarize the file",
        "constraint_check": [{"id": "C1", "preserved": True}],
        "assumptions": [], "questions": [], "context_used": [],
        "probe_answer": "read-only", "confidence": 0.9,
    }
    return s.receive(msg("SEMANTIC_RECEIPT", 2, sender="mind-b", body=body), now=NOW)


class ConstraintTests(unittest.TestCase):
    def test_constraint_digest_and_check(self):
        c = constraint()
        validate_constraints([c])
        self.assertTrue(check_constraints([c], lambda name, params: True)["ok"])

    def test_tampered_constraint_digest(self):
        c = constraint(); c["text"] = "changed"
        with self.assertRaisesRegex(SemError, "digest mismatch"):
            validate_constraints([c])

    def test_failed_hard_constraint(self):
        r = check_constraints([constraint()], lambda name, params: False)
        self.assertFalse(r["ok"])


class SemTests(unittest.TestCase):
    def test_canonical_digest_stable(self):
        m = msg("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"})
        self.assertEqual(message_digest(m), message_digest(m))
        self.assertEqual(canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_handshake_intent_receipt(self):
        s = SemSession("s1"); to_receipt(s)
        self.assertEqual(s.state, "INTERPRETED")

    def test_copied_receipt_rejected(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "copy"):
            to_receipt(s, {
                "own_words": "read the file and summarize",
                "constraint_check": [{"id": "C1", "preserved": True}],
                "assumptions": [], "questions": [], "context_used": [],
                "probe_answer": "x", "confidence": 0.5,
            })

    def test_missing_hard_constraint_check_rejected(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "not checked"):
            to_receipt(s, {
                "own_words": "I will only read the file",
                "constraint_check": [], "assumptions": [], "questions": [],
                "context_used": [], "probe_answer": "x", "confidence": 0.5,
            })

    def test_missing_probe_answer_rejected(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "probe_answer"):
            to_receipt(s, {
                "own_words": "I will only read the file",
                "constraint_check": [{"id": "C1", "preserved": True}],
                "assumptions": [], "questions": [], "context_used": [],
                "confidence": 0.5,
            })

    def test_commit_is_semantic_only(self):
        s = SemSession("s1"); to_receipt(s)
        r = s.receive(msg("COMMIT", 4, body={}), now=NOW)
        self.assertEqual(r["state"], "COMMITTED")
        self.assertEqual(s.commits, 1)
        self.assertFalse(hasattr(s, "authorize"))
        self.assertFalse(hasattr(s, "execute"))

    def test_sequence_gap_rejected(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "sequence gap"):
            s.receive(msg("HELLO", 2, body={"min_version": "0.2", "max_version": "0.2"}), now=NOW)

    def test_duplicate_identical_is_idempotent(self):
        s = SemSession("s1")
        m = msg("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"})
        s.receive(m, now=NOW)
        self.assertEqual(s.receive(m, now=NOW)["status"], "idempotent")

    def test_duplicate_different_is_replay(self):
        s = SemSession("s1")
        m = msg("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"})
        s.receive(m, now=NOW)
        m2 = dict(m); m2["body"] = {"min_version": "0.1", "max_version": "0.1"}
        with self.assertRaisesRegex(SemError, "replay"):
            s.receive(m2, now=NOW)

    def test_expired_message_rejected(self):
        s = SemSession("s1")
        m = msg("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"},
                expires="2026-11-01T00:00:00+00:00")
        with self.assertRaisesRegex(SemError, "expired"):
            s.receive(m, now=NOW)

    def test_version_downgrade_rejected(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "version"):
            s.receive(msg("HELLO", 1, body={"min_version": "0.1", "max_version": "0.1"}), now=NOW)

    def test_state_violation(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "state_violation"):
            s.receive(msg("SEMANTIC_RECEIPT", 1, sender="mind-b", body={}), now=NOW)

    def test_unknown_type(self):
        s = SemSession("s1")
        with self.assertRaisesRegex(SemError, "unknown message type"):
            s.receive(msg("AUTHORIZATION", 1), now=NOW)

    def test_correction_budget_one(self):
        s = SemSession("s1"); to_receipt(s)
        s.receive(msg("CHALLENGE", 4, body={"issue": "ambiguous"}), now=NOW)
        self.assertEqual(s.state, "CHALLENGE_PENDING")
        s.receive(msg("CLARIFY", 3, sender="mind-b", body={"answer": "clarified"}), now=NOW)
        self.assertEqual(s.state, "INTERPRETED")
        with self.assertRaisesRegex(SemError, "budget"):
            s.receive(msg("CHALLENGE", 5, body={"issue": "again"}), now=NOW)

    def test_timeout_aborts(self):
        s = SemSession("s1", idle_timeout_s=10)
        # The session starts at real wall-clock time; advance relative to it so the
        # test is deterministic whenever it runs (not only on 2026-11-02).
        later = (s.last_activity + timedelta(seconds=60)).isoformat()
        self.assertEqual(s.tick(now=later), "ABORTED")

    def test_terminal_session_rejects_more(self):
        s = SemSession("s1")
        s.receive(msg("ABORT", 1, body={}), now=NOW)
        with self.assertRaisesRegex(SemError, "terminal"):
            s.receive(msg("HELLO", 2, body={"min_version": "0.2", "max_version": "0.2"}), now=NOW)

    def test_verify_semantics_pass_and_fail(self):
        c = [constraint()]
        receipt = {
            "own_words": "I will only read and summarize",
            "constraint_check": [{"id": "C1", "preserved": True}],
            "assumptions": [], "questions": [], "context_used": [],
            "probe_answer": "read-only", "confidence": 0.9,
        }
        good = verify_semantics(receipt, intent_goal="read", constraints=c,
                                checker=lambda n, p: True, verifier_ref="mind-v",
                                sender_ref="mind-a", receiver_ref="mind-b",
                                semantic_verifier=lambda r, g: "PASS")
        self.assertEqual(good["result"], "PASS")
        bad = verify_semantics(receipt, intent_goal="read", constraints=c,
                               checker=lambda n, p: False, verifier_ref="mind-v",
                               sender_ref="mind-a", receiver_ref="mind-b",
                               semantic_verifier=lambda r, g: "PASS")
        self.assertEqual(bad["result"], "FAIL")

    def test_verifier_independence(self):
        receipt = {
            "own_words": "I will only read and summarize",
            "constraint_check": [{"id": "C1", "preserved": True}],
            "assumptions": [], "questions": [], "context_used": [],
            "probe_answer": "read-only", "confidence": 0.9,
        }
        with self.assertRaisesRegex(SemError, "independent"):
            verify_semantics(receipt, intent_goal="read", constraints=[constraint()],
                             checker=lambda n, p: True, verifier_ref="mind-a",
                             sender_ref="mind-a", receiver_ref="mind-b",
                             semantic_verifier=lambda r, g: "PASS")

    def test_verifier_unavailable_is_uncertain(self):
        receipt = {
            "own_words": "I will only read and summarize",
            "constraint_check": [{"id": "C1", "preserved": True}],
            "assumptions": [], "questions": [], "context_used": [],
            "probe_answer": "read-only", "confidence": 0.9,
        }
        r = verify_semantics(receipt, intent_goal="read", constraints=[constraint()],
                             checker=lambda n, p: True, verifier_ref="mind-v",
                             sender_ref="mind-a", receiver_ref="mind-b",
                             semantic_verifier=None)
        self.assertEqual(r["result"], "UNCERTAIN")


if __name__ == "__main__":
    unittest.main()
