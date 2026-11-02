import hashlib
import unittest

from agi_context import make_context_manifest
from agi_context_adapter import AdapterError, require_boundary_allow, resolve_authorized

NOW = "2026-11-02T00:00:00+00:00"
FUTURE = "2026-11-03T00:00:00+00:00"
BODY = b"authorized context body"
SHA = hashlib.sha256(BODY).hexdigest()


def manifest():
    return make_context_manifest(
        branch_id="br-1",
        refs=[{
            "context_id": "ctx-1", "branch_id": "br-1", "store": "memory/knowledge",
            "version": 1, "sha256": SHA, "scope_digest": "c" * 64,
            "classification": "branch_private", "expires_at": FUTURE,
            "revocation_head_ref": "rh-1",
        }],
        provenance={"source": "test"},
    )


def decision(**over):
    value = {
        "decision_id": "bd-1", "operation": "read_memory", "actor": "dsh",
        "subject": "ctx-1", "grant_id": "g-1", "result": "allow",
        "reason_code": "ok", "ts": "2026-11-02T00:00:00+00:00",
        "revocation_checked": True, "staleness_s": 0,
    }
    value.update(over)
    return value


def run(dec=None, gateway=lambda r: BODY, rev=lambda h: True, consent=None):
    m = manifest()
    return resolve_authorized(m, m["refs"][0], allowed_branch="br-1",
                              decide=lambda req: dec or decision(), gateway=gateway,
                              revocation_check=rev, consent_check=consent)


class AdapterTests(unittest.TestCase):
    def test_allow_path_resolves_with_digest(self):
        self.assertEqual(run(), BODY)

    def test_deny_fails_closed(self):
        with self.assertRaisesRegex(AdapterError, "not allow"):
            run(decision(result="deny", reason_code="revoked"))

    def test_missing_revocation_checked_fails(self):
        d = decision(); d.pop("revocation_checked")
        with self.assertRaisesRegex(AdapterError, "revocation_checked"):
            run(d)

    def test_stale_revocation_fails(self):
        with self.assertRaisesRegex(AdapterError, "revocation"):
            run(rev=lambda h: False)

    def test_gateway_tamper_fails(self):
        with self.assertRaisesRegex(AdapterError, "digest mismatch"):
            run(gateway=lambda r: b"tampered")

    def test_operation_mismatch_fails(self):
        with self.assertRaisesRegex(AdapterError, "operation mismatch"):
            run(decision(operation="write_memory"))

    def test_cross_branch_without_consent_fails(self):
        m = make_context_manifest(
            branch_id="br-1",
            refs=[{
                "context_id": "ctx-x", "branch_id": "br-2", "store": "memory/knowledge",
                "version": 1, "sha256": SHA, "scope_digest": "d" * 64,
                "classification": "cross_branch_shared", "expires_at": FUTURE,
                "revocation_head_ref": "rh-1",
            }],
            provenance={"source": "test"},
        )
        with self.assertRaises(Exception):
            resolve_authorized(m, m["refs"][0], allowed_branch="br-1",
                               decide=lambda req: decision(), gateway=lambda r: BODY,
                               revocation_check=lambda h: True, consent_check=None)

    def test_require_boundary_allow_rejects_unknown_operation(self):
        with self.assertRaisesRegex(AdapterError, "operation mismatch"):
            require_boundary_allow(decision(operation="other"), operation="read_memory")


if __name__ == "__main__":
    unittest.main()
