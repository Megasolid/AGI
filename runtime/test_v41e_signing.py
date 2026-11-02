import base64
import hashlib
import hmac
import unittest

from agi_context import make_context_manifest
from agi_handoff import completion_receipt, make_handoff
from agi_handoff_signing import (
    SigningError, sign_handoff, sign_receipt, verify_signed_handoff,
    verify_signed_receipt,
)

NOW = "2026-11-02T00:00:00+00:00"
FUTURE = "2026-11-03T00:00:00+00:00"
SHA = hashlib.sha256(b"body").hexdigest()
SECRET = b"mock-secret-not-a-real-key"


def ctx():
    return make_context_manifest(
        branch_id="br-1",
        refs=[{
            "context_id": "ctx-1", "branch_id": "br-1", "store": "memory/knowledge",
            "version": 1, "sha256": SHA, "scope_digest": "e" * 64,
            "classification": "branch_private", "expires_at": FUTURE,
            "revocation_head_ref": "rh-1",
        }],
        provenance={"source": "test"},
    )


def handoff():
    return make_handoff(
        task_id="task-1", title="T", objective="bounded", owner="dsh",
        branch_id="br-1", context_manifest=ctx(),
        acceptance_criteria=["a"], evidence_requirements=["e"],
        non_goals=["no network"], permissions={"read": True},
    )


def fake_sign(payload):
    sig = hmac.new(SECRET, payload, hashlib.sha256).digest()
    return {
        "schema": "agi-sig/1", "alg": "test-hmac", "key_id": "test-key",
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "signature_b64": base64.b64encode(sig).decode("ascii"),
    }


def fake_verify(payload, envelope):
    expected = fake_sign(payload)
    return hmac.compare_digest(expected["signature_b64"], envelope.get("signature_b64", ""))


class SigningTests(unittest.TestCase):
    def test_sign_and_verify_handoff(self):
        signed = sign_handoff(handoff(), fake_sign)
        verify_signed_handoff(signed, fake_verify)

    def test_tampered_handoff_fails(self):
        signed = sign_handoff(handoff(), fake_sign)
        signed["objective"] = "changed"
        with self.assertRaisesRegex(Exception, "digest mismatch"):
            verify_signed_handoff(signed, fake_verify)

    def test_tampered_signature_fails(self):
        signed = sign_handoff(handoff(), fake_sign)
        signed["signature"]["signature_b64"] = "AAAA"
        with self.assertRaisesRegex(SigningError, "verification failed"):
            verify_signed_handoff(signed, fake_verify)

    def test_replay_nonce_rejected(self):
        signed = sign_handoff(handoff(), fake_sign)
        with self.assertRaisesRegex(SigningError, "replay"):
            verify_signed_handoff(signed, fake_verify, nonce_check=lambda n: False)

    def test_missing_nonce_rejected_at_signing(self):
        h = handoff(); h.pop("nonce")
        with self.assertRaisesRegex(Exception, "nonce"):
            sign_handoff(h, fake_sign)

    def test_sign_and_verify_receipt(self):
        h = handoff()
        r = completion_receipt(h, outcome="success", evidence_refs=["sha256:abc"],
                               constraints_met=["a"], residual_risks=[])
        signed = sign_receipt(r, h, fake_sign)
        verify_signed_receipt(signed, h, fake_verify)

    def test_tampered_receipt_fails(self):
        h = handoff()
        r = completion_receipt(h, outcome="success", evidence_refs=["sha256:abc"],
                               constraints_met=["a"], residual_risks=[])
        signed = sign_receipt(r, h, fake_sign)
        signed["outcome"] = "failure"
        with self.assertRaisesRegex(Exception, "digest mismatch"):
            verify_signed_receipt(signed, h, fake_verify)


if __name__ == "__main__":
    unittest.main()
