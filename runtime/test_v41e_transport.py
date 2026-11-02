import base64
import hashlib
import hmac
import unittest

from agi_sem import SemError, make_message, verify_semantics
from agi_sem_transport import (
    SemChannel, TransportError, sign_message, validate_message_schema,
    validate_json_schema, verify_binding, verify_message_auth,
)

TS = "2026-11-02T00:00:00+00:00"
EXP = "2026-11-03T00:00:00+00:00"
NOW = TS
SECRET_A = b"a-secret-mock"
SECRET_B = b"b-secret-mock"


def signer(secret):
    def _sign(payload):
        sig = hmac.new(secret, payload, hashlib.sha256).digest()
        return {"schema": "agi.sem.auth/0.1", "alg": "test-hmac", "key_id": "test-key",
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
                "signature_b64": base64.b64encode(sig).decode("ascii")}
    return _sign


def verifier(secret):
    def _verify(payload, env):
        want = hmac.new(secret, payload, hashlib.sha256).digest()
        return hmac.compare_digest(base64.b64encode(want).decode("ascii"), env.get("signature_b64", ""))
    return _verify


def message(mtype, seq, *, sender="a", receiver="b", body=None, constraints=None, session="s1"):
    return make_message(message_type=mtype, session_id=session,
                        message_id=f"m-{mtype}-{seq}-{sender}", sequence=seq,
                        from_ref=sender, to_ref=receiver, body=body or {},
                        constraints=constraints or [], ts=TS, expires_at=EXP)


def channel(session="s1"):
    return SemChannel(session, a_signer=signer(SECRET_A), a_verifier=verifier(SECRET_A),
                      b_signer=signer(SECRET_B), b_verifier=verifier(SECRET_B))


class SchemaTests(unittest.TestCase):
    def test_valid_message_passes(self):
        validate_message_schema(message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))

    def test_missing_field_fails(self):
        m = message("HELLO", 1, body={})
        m.pop("session_id")
        with self.assertRaisesRegex(TransportError, "missing"):
            validate_message_schema(m)

    def test_unknown_type_fails(self):
        m = message("HELLO", 1)
        m["type"] = "AUTHORIZATION"
        with self.assertRaisesRegex(TransportError, "enum"):
            validate_message_schema(m)

    def test_additional_property_fails(self):
        m = message("HELLO", 1)
        m["extra"] = True
        with self.assertRaisesRegex(TransportError, "additional property"):
            validate_json_schema(m, __import__("agi_sem_transport").MESSAGE_SCHEMA)


class AuthTests(unittest.TestCase):
    def test_sign_verify_and_tamper(self):
        m = message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"})
        signed = sign_message(m, signer(SECRET_A))
        verify_message_auth(signed, verifier(SECRET_A), expected_key_id="test-key")
        signed["body"]["min_version"] = "0.1"
        with self.assertRaisesRegex(TransportError, "payload changed"):
            verify_message_auth(signed, verifier(SECRET_A), expected_key_id="test-key")

    def test_wrong_key_id_fails(self):
        signed = sign_message(message("HELLO", 1), signer(SECRET_A))
        with self.assertRaisesRegex(TransportError, "key_id"):
            verify_message_auth(signed, verifier(SECRET_A), expected_key_id="other")

    def test_wrong_verifier_fails(self):
        signed = sign_message(message("HELLO", 1), signer(SECRET_A))
        with self.assertRaisesRegex(TransportError, "verification failed"):
            verify_message_auth(signed, verifier(SECRET_B), expected_key_id="test-key")


class ChannelTests(unittest.TestCase):
    def test_two_endpoint_handshake(self):
        c = channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
        self.assertEqual(c.deliver("b", hello, now=NOW)["state"], "GREETING")
        ack = c.send("b", message("HELLO_ACK", 1, sender="b", receiver="a", body={"version": "0.2"}))
        self.assertEqual(c.deliver("a", ack, now=NOW)["state"], "NEGOTIATED")
        caps = c.send("a", message("CAPABILITIES", 2, body={"classes": ["reasoning"]}))
        self.assertEqual(c.deliver("b", caps, now=NOW)["state"], "IDLE")

    def test_binding_mismatch(self):
        c = channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
        with self.assertRaisesRegex(TransportError, "session binding"):
            verify_binding(hello, session_id="s2", from_ref="a", to_ref="b")

    def test_cross_session_replay_rejected(self):
        c1 = channel("s1"); c2 = channel("s2")
        hello = c1.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}, session="s1"))
        with self.assertRaisesRegex(TransportError, "session binding"):
            c2.deliver("b", hello, now=NOW)

    def test_reordering_gap_rejected(self):
        c = channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
        c.deliver("b", hello, now=NOW)
        late = c.send("a", message("CAPABILITIES", 3, body={"classes": ["reasoning"]}))
        with self.assertRaisesRegex(SemError, "sequence gap"):
            c.deliver("b", late, now=NOW)

    def test_partial_delivery_schema_fail(self):
        c = channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
        del hello["body"]
        with self.assertRaisesRegex(TransportError, "missing body"):
            c.deliver("b", hello, now=NOW)

    def test_downgrade_rejected(self):
        c = channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.1", "max_version": "0.1"}))
        with self.assertRaisesRegex(SemError, "version"):
            c.deliver("b", hello, now=NOW)

    def test_timeout(self):
        c = channel()
        self.assertEqual(c.tick(now="2026-11-02T09:00:00+00:00"), "ABORTED")


class VerifierDisagreementTests(unittest.TestCase):
    def receipt(self):
        return {
            "own_words": "I will only read and summarize",
            "constraint_check": [{"id": "C1", "preserved": True}],
            "assumptions": [], "questions": [], "context_used": [],
            "probe_answer": "read-only", "confidence": 0.9,
        }

    def constraint(self):
        from agi_sem import constraint_digest
        c = {"id": "C1", "kind": "MUST_NOT", "text": "no write", "machine_check": "no_write",
             "source": "task", "enforcement": "runtime"}
        c["digest"] = constraint_digest(c)
        return c

    def test_checker_pass_reviewer_fail_is_fail(self):
        r = verify_semantics(self.receipt(), intent_goal="read", constraints=[self.constraint()],
                             checker=lambda n, p: True, verifier_ref="v",
                             sender_ref="a", receiver_ref="b",
                             semantic_verifier=lambda r, g: "FAIL")
        self.assertEqual(r["result"], "FAIL")

    def test_checker_pass_reviewer_uncertain_is_uncertain(self):
        r = verify_semantics(self.receipt(), intent_goal="read", constraints=[self.constraint()],
                             checker=lambda n, p: True, verifier_ref="v",
                             sender_ref="a", receiver_ref="b",
                             semantic_verifier=lambda r, g: "UNCERTAIN")
        self.assertEqual(r["result"], "UNCERTAIN")


if __name__ == "__main__":
    unittest.main()
