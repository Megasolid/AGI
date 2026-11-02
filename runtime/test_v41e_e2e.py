import base64
import hashlib
import hmac
import unittest

from agi_context import make_context_manifest
from agi_context_adapter import AdapterError, resolve_authorized
from agi_handoff import completion_receipt, make_handoff, reconstruct_task
from agi_handoff_signing import sign_handoff, sign_receipt, verify_signed_handoff, verify_signed_receipt

NOW = "2026-11-02T00:00:00+00:00"
FUTURE = "2026-11-03T00:00:00+00:00"
BODY = b"bounded task context; data only"
SHA = hashlib.sha256(BODY).hexdigest()
SECRET = b"mock-secret-not-a-real-key"


def ctx():
    return make_context_manifest(
        branch_id="br-1",
        refs=[{
            "context_id": "ctx-1", "branch_id": "br-1", "store": "memory/knowledge",
            "version": 1, "sha256": SHA, "scope_digest": "f" * 64,
            "classification": "branch_private", "expires_at": FUTURE,
            "revocation_head_ref": "rh-1",
        }],
        provenance={"source": "e2e-mock"},
    )


def decision(result="allow"):
    return {
        "decision_id": "bd-1", "operation": "read_memory", "actor": "dsh",
        "subject": "ctx-1", "grant_id": "g-1", "result": result,
        "reason_code": "ok" if result == "allow" else "denied",
        "ts": "2026-11-02T00:00:00+00:00", "revocation_checked": True,
        "staleness_s": 0,
    }


def fake_sign(payload):
    sig = hmac.new(SECRET, payload, hashlib.sha256).digest()
    return {"schema": "agi-sig/1", "alg": "test-hmac", "key_id": "test-key",
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "signature_b64": base64.b64encode(sig).decode("ascii")}


def fake_verify(payload, envelope):
    return hmac.compare_digest(fake_sign(payload)["signature_b64"],
                               envelope.get("signature_b64", ""))


class EndToEndTests(unittest.TestCase):
    def test_fresh_agent_flow(self):
        m = ctx()
        ref = m["refs"][0]
        body = resolve_authorized(m, ref, allowed_branch="br-1",
                                  decide=lambda req: decision(),
                                  gateway=lambda r: BODY,
                                  revocation_check=lambda h: True)
        self.assertEqual(body, BODY)
        h = make_handoff(task_id="task-e2e", title="T", objective="bounded",
                         owner="dsh", branch_id="br-1", context_manifest=m,
                         acceptance_criteria=["a"], evidence_requirements=["sha256"],
                         non_goals=["no network"], permissions={"read": True})
        signed = sign_handoff(h, fake_sign)
        verify_signed_handoff(signed, fake_verify)
        rebuilt = reconstruct_task(signed, lambda r: BODY)
        self.assertEqual(rebuilt["context"]["ctx-1"], BODY)
        self.assertEqual(rebuilt["task_id"], "task-e2e")
        self.assertNotIn("original transcript", str(rebuilt).lower())
        receipt = completion_receipt(signed, outcome="success",
                                     evidence_refs=["sha256:" + SHA],
                                     constraints_met=["a"], residual_risks=[])
        verify_signed_receipt(sign_receipt(receipt, signed, fake_sign), signed, fake_verify)

    def test_deny_produces_no_body(self):
        m = ctx()
        with self.assertRaisesRegex(AdapterError, "not allow"):
            resolve_authorized(m, m["refs"][0], allowed_branch="br-1",
                               decide=lambda req: decision("deny"),
                               gateway=lambda r: BODY,
                               revocation_check=lambda h: True)

    def test_replay_after_signing(self):
        h = make_handoff(task_id="task-replay", title="T", objective="bounded",
                         owner="dsh", branch_id="br-1", context_manifest=ctx(),
                         acceptance_criteria=["a"], evidence_requirements=["e"],
                         non_goals=["no network"])
        signed = sign_handoff(h, fake_sign)
        seen = set()
        def nonce_check(n):
            if n in seen:
                return False
            seen.add(n)
            return True
        verify_signed_handoff(signed, fake_verify, nonce_check=nonce_check)
        with self.assertRaisesRegex(Exception, "replay"):
            verify_signed_handoff(signed, fake_verify, nonce_check=nonce_check)


if __name__ == "__main__":
    unittest.main()
