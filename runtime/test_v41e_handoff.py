import hashlib
import unittest

from agi_context import make_context_manifest, validate_context_manifest
from agi_handoff import (
    HandoffError, completion_receipt, make_handoff, reconstruct_task, validate_handoff,
    validate_receipt,
)

NOW = "2026-11-02T00:00:00+00:00"
FUTURE = "2026-11-03T00:00:00+00:00"
SHA = hashlib.sha256(b"body").hexdigest()


def ctx():
    m = make_context_manifest(
        branch_id="br-1",
        refs=[{
            "context_id": "ctx-1", "branch_id": "br-1", "store": "memory/knowledge",
            "version": 1, "sha256": SHA, "scope_digest": "b" * 64,
            "classification": "branch_private", "expires_at": FUTURE,
            "revocation_head_ref": "rh-1",
        }],
        provenance={"source": "test"},
    )
    validate_context_manifest(m, now=NOW, allowed_branch="br-1",
                              revocation_check=lambda h: True,
                              consent_check=lambda c: True)
    return m


def handoff(**over):
    kwargs = dict(
        task_id="task-1", title="Test task", objective="Do a bounded thing",
        owner="dsh", branch_id="br-1", context_manifest=ctx(),
        acceptance_criteria=["criterion"], evidence_requirements=["hash"],
        dependencies=["task-0"], permissions={"read": True, "write": False},
        non_goals=["no network"],
    )
    kwargs.update(over)
    return make_handoff(**kwargs)


class HandoffTests(unittest.TestCase):
    def test_valid_roundtrip(self):
        h = handoff()
        validate_handoff(h, now=NOW)
        self.assertTrue(h["handoff_digest"].startswith("sha256:"))

    def test_missing_acceptance_fails(self):
        with self.assertRaisesRegex(HandoffError, "acceptance"):
            handoff(acceptance_criteria=[])

    def test_missing_non_goals_fails(self):
        with self.assertRaisesRegex(HandoffError, "non-goals"):
            handoff(non_goals=[])

    def test_authority_field_rejected(self):
        with self.assertRaisesRegex(HandoffError, "must not carry"):
            validate_handoff({**handoff(), "grant": "root"})

    def test_tamper_digest_fails(self):
        h = handoff()
        h["objective"] = "changed"
        with self.assertRaisesRegex(HandoffError, "digest mismatch"):
            validate_handoff(h)

    def test_receipt_roundtrip_and_match(self):
        h = handoff()
        r = completion_receipt(h, outcome="success", evidence_refs=["sha256:abc"],
                               constraints_met=["criterion"], residual_risks=[])
        validate_receipt(r, handoff=h)
        self.assertEqual(r["handoff_digest"], h["handoff_digest"])

    def test_receipt_tamper_fails(self):
        h = handoff()
        r = completion_receipt(h, outcome="partial", evidence_refs=["sha256:abc"],
                               constraints_met=[], residual_risks=["risk"])
        r["outcome"] = "success"
        with self.assertRaisesRegex(HandoffError, "digest mismatch"):
            validate_receipt(r, handoff=h)

    def test_handoff_expiry_fails(self):
        h = handoff(expires_at="2026-11-01T00:00:00+00:00")
        with self.assertRaisesRegex(HandoffError, "expired"):
            validate_handoff(h, now=NOW)

    def test_fresh_agent_reconstructs_from_context_refs(self):
        h = handoff()
        rebuilt = reconstruct_task(h, lambda ref: b"body")
        self.assertEqual(rebuilt["task_id"], "task-1")
        self.assertEqual(rebuilt["objective"], "Do a bounded thing")
        self.assertEqual(rebuilt["context"]["ctx-1"], b"body")
        self.assertNotIn("original transcript", str(rebuilt).lower())

    def test_missing_context_refs_rejected(self):
        h = handoff()
        h["context_refs"] = []
        h["handoff_digest"] = __import__("agi_handoff").handoff_digest(h)
        with self.assertRaisesRegex(HandoffError, "context refs required"):
            validate_handoff(h)

    def test_declared_permission_is_not_a_grant(self):
        h = handoff(permissions={"write": True})
        validate_handoff(h, now=NOW)
        self.assertNotIn("grant", h)
        self.assertNotIn("authority", h)


if __name__ == "__main__":
    unittest.main()
