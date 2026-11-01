import hashlib
import unittest

from agi_context import (
    ContextError, canonical_json, compact_handoff_refs, context_manifest_digest,
    make_context_manifest, resolve_context_ref, validate_context_manifest,
)

NOW = "2026-11-02T00:00:00+00:00"
FUTURE = "2026-11-03T00:00:00+00:00"
BODY = b"context body bytes"
SHA = hashlib.sha256(BODY).hexdigest()
SCOPE = "a" * 64


def ref(**over):
    value = {
        "context_id": "ctx-1",
        "branch_id": "br-1",
        "store": "memory/knowledge",
        "version": 1,
        "sha256": SHA,
        "scope_digest": SCOPE,
        "classification": "branch_private",
        "expires_at": FUTURE,
        "revocation_head_ref": "rh-1",
    }
    value.update(over)
    return value


def manifest(**over):
    kwargs = dict(branch_id="br-1", refs=[ref()], provenance={"source": "test"})
    kwargs.update(over)
    return make_context_manifest(**kwargs)


def check(m):
    validate_context_manifest(m, now=NOW, allowed_branch="br-1",
                              revocation_check=lambda h: h == "rh-1",
                              consent_check=lambda c: c == "consent-1")


class ContextTests(unittest.TestCase):
    def test_valid_roundtrip(self):
        m = manifest()
        check(m)
        self.assertEqual(m["digest"], context_manifest_digest(m))
        self.assertEqual(len(compact_handoff_refs(m)), 1)

    def test_tamper_digest_fails(self):
        m = manifest()
        m["refs"][0]["version"] = 2
        with self.assertRaisesRegex(ContextError, "digest mismatch"):
            check(m)

    def test_inline_body_rejected(self):
        with self.assertRaisesRegex(ContextError, "must not inline body"):
            check(manifest(refs=[ref(body="inline")]))

    def test_expired_fails(self):
        with self.assertRaisesRegex(ContextError, "expired"):
            check(manifest(refs=[ref(expires_at="2026-11-01T00:00:00+00:00")]))

    def test_cross_branch_requires_consent(self):
        with self.assertRaisesRegex(ContextError, "consent_ref"):
            check(manifest(refs=[ref(branch_id="br-2", classification="cross_branch_shared")]))

    def test_cross_branch_with_consent_passes(self):
        check(manifest(refs=[ref(branch_id="br-2", classification="cross_branch_shared",
                                 consent_ref="consent-1")]))

    def test_revocation_unavailable_fails(self):
        with self.assertRaisesRegex(ContextError, "revocation"):
            validate_context_manifest(manifest(), now=NOW, allowed_branch="br-1",
                                      revocation_check=lambda h: False,
                                      consent_check=lambda c: True)

    def test_resolver_verifies_digest(self):
        r = ref()
        self.assertEqual(resolve_context_ref(r, lambda _r: BODY), BODY)
        with self.assertRaisesRegex(ContextError, "digest mismatch"):
            resolve_context_ref(r, lambda _r: b"tampered")

    def test_manifest_branch_denied(self):
        with self.assertRaisesRegex(ContextError, "allowed branch"):
            validate_context_manifest(manifest(), now=NOW, allowed_branch="br-other",
                                      revocation_check=lambda h: True,
                                      consent_check=lambda c: True)


if __name__ == "__main__":
    unittest.main()
