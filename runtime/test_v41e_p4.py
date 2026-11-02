import base64
import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path

from agi_sem import make_message
from agi_sem_ipc import cross_process_verify
from agi_sem_keys import KeyError, KeyRecord, KeyRegistry
from agi_sem_replay import ReplayError, ReplayStore
from agi_sem_roles import DurableChannel, RoleChannel, RoleError
from agi_sem_transport import sign_message

TS = "2026-11-02T00:00:00+00:00"
EXP = "2026-11-03T00:00:00+00:00"
NOW = TS
SECRET_A = b"p4-a-mock"
SECRET_B = b"p4-b-mock"


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


def message(mtype, seq, *, sender="a", receiver="b", body=None, session="s1"):
    return make_message(message_type=mtype, session_id=session,
                        message_id=f"m-{mtype}-{seq}-{sender}", sequence=seq,
                        from_ref=sender, to_ref=receiver, body=body or {},
                        ts=TS, expires_at=EXP)


def role_channel(session="s1"):
    return RoleChannel(session, roles={"a": "initiator", "b": "responder"},
                       a_signer=signer(SECRET_A), a_verifier=verifier(SECRET_A),
                       b_signer=signer(SECRET_B), b_verifier=verifier(SECRET_B))


def durable(session, path):
    return DurableChannel(session, replay_path=path,
                          roles={"a": "initiator", "b": "responder"},
                          a_signer=signer(SECRET_A), a_verifier=verifier(SECRET_A),
                          b_signer=signer(SECRET_B), b_verifier=verifier(SECRET_B))


class RoleTests(unittest.TestCase):
    def test_role_handshake(self):
        c = role_channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
        self.assertEqual(c.deliver("b", hello, now=NOW)["state"], "GREETING")
        ack = c.send("b", message("HELLO_ACK", 1, sender="b", receiver="a", body={"version": "0.2"}))
        self.assertEqual(c.deliver("a", ack, now=NOW)["state"], "NEGOTIATED")

    def test_responder_cannot_send_intent(self):
        c = role_channel()
        with self.assertRaisesRegex(RoleError, "role_violation"):
            c.send("b", message("INTENT", 1, sender="b", receiver="a", body={"goal": "x"}))

    def test_unknown_endpoint(self):
        c = role_channel()
        with self.assertRaisesRegex(RoleError, "unknown endpoint"):
            c.send("c", message("HELLO", 1, sender="c", body={}))

    def test_receiver_isolation(self):
        c = role_channel()
        hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
        with self.assertRaisesRegex(RoleError, "receiver"):
            c.deliver("c", hello, now=NOW)


class ReplayTests(unittest.TestCase):
    def test_store_idempotent_and_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            s = ReplayStore(Path(td) / "replay.jsonl")
            self.assertEqual(s.check_and_record("s1", "m1", "sha256:a"), "recorded")
            self.assertEqual(s.check_and_record("s1", "m1", "sha256:a"), "idempotent")
            with self.assertRaisesRegex(ReplayError, "replay"):
                s.check_and_record("s1", "m1", "sha256:b")

    def test_durable_channel_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "replay.jsonl"
            c = durable("s1", path)
            hello = c.send("a", message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}))
            c.deliver("b", hello, now=NOW)
            c2 = durable("s1", path)
            r = c2.deliver("b", hello, now=NOW)
            self.assertEqual(r["status"], "idempotent")
            self.assertEqual(r["state"], "INIT")

    def test_corrupt_store_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "replay.jsonl"
            p.write_text("not json\n", encoding="utf-8")
            with self.assertRaisesRegex(ReplayError, "corrupt"):
                ReplayStore(p)


class KeyTests(unittest.TestCase):
    def rec(self, kid="k1", status="active", after=None):
        return KeyRecord(key_id=kid, alg="ML-DSA-65", public_key_b64="cHVibGlj",
                         status=status, not_after=after, purpose="message-auth")

    def test_active_retired_revoked(self):
        r = KeyRegistry(); r.add(self.rec())
        self.assertEqual(r.authorize("k1", now=NOW).key_id, "k1")
        r.retire("k1")
        self.assertEqual(r.authorize("k1", now=NOW).status, "retired")
        r.revoke("k1")
        with self.assertRaisesRegex(KeyError, "revoked"):
            r.authorize("k1", now=NOW)

    def test_expiry_and_rotation(self):
        r = KeyRegistry()
        r.add(self.rec("old", after="2026-11-02T00:00:01+00:00"))
        r.add(self.rec("new"))
        with self.assertRaisesRegex(KeyError, "expired"):
            r.authorize("old", now="2026-11-02T00:00:02+00:00")
        self.assertEqual(r.authorize("new", now=NOW).key_id, "new")


class CrossProcessTests(unittest.TestCase):
    def test_cross_process_verify_and_tamper(self):
        m = message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"})
        signed = sign_message(m, signer(SECRET_A))
        self.assertTrue(cross_process_verify(signed, SECRET_A)["ok"])
        signed["body"]["min_version"] = "0.1"
        self.assertFalse(cross_process_verify(signed, SECRET_A)["ok"])


if __name__ == "__main__":
    unittest.main()
