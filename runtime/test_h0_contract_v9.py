#!/usr/bin/env python3
"""H0 revision 9 adversarial tests — King findings on R8.

R9-1 the same-probe substitution attack: a hostile store returning the EXACT expected
     probe string. R8 could not detect this because the probe was the whole check.
R9-2 instance-attribute reassignment of the audit binding is detected by OBJECT
     IDENTITY against the class-resolved store, not by a forgeable string.
R9-3 the honest limit: this is NOT a defence against arbitrary code in the same
     process. A test records what that attacker can do, so the guarantee is stated
     at the level the implementation actually enforces.

Run from runtime/: python test_h0_contract_v9.py
"""
import base64
import hashlib
import hmac
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_kernel import H0Error, Kernel, canonical

SECRET = b"h0-test-secret"
KEY_ID = "test-key-h0"
NOW = datetime(2026, 11, 2, 16, 0, tzinfo=timezone.utc)


def sign(b):
    return {"alg": "test-hmac", "key_id": KEY_ID,
            "signature_b64": base64.b64encode(hmac.new(SECRET, b, hashlib.sha256).digest()).decode()}


def verify(b, env):
    want = hmac.new(SECRET, b, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode(), env.get("signature_b64", ""))


def envelope():
    req = {"schema": "h0.mcp/1", "method": "agi_status", "scope": "h0.read",
           "client_id": "station-a", "request_id": str(uuid.uuid4()),
           "correlation_id": str(uuid.uuid4()), "issued_at": NOW.isoformat(),
           "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
           "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
           "payload": {}, "signature": {}}
    req["signature"] = sign(canonical({k: v for k, v in req.items() if k != "signature"}))
    return req


def kernel_for(path, **kw):
    return Kernel(clients={"station-a": {"key_id": KEY_ID}},
                  verifier=verify, clock=lambda: NOW, audit_path=path, **kw)


class R9_1_SameProbeSubstitution(unittest.TestCase):
    def test_substitute_returning_the_exact_probe_is_still_detected(self):
        """The R8 attack King named: forge the probe string so the string check passes."""
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            real_probe = k.audit.probe()

            class ForgedStore:
                def probe(self):
                    return real_probe  # exact match

                def append(self, record):
                    return record  # never persists

                def __getattr__(self, name):
                    return getattr(k.audit, name)

            k._trusted_store = ForgedStore()
            res = k.handle(envelope())
            self.assertFalse(res["ok"])
            self.assertEqual(res["error"], "E_AUDIT_STORE_SUBSTITUTED")

    def test_probe_is_documented_as_non_identity(self):
        doc = (Path(__file__).resolve().parents[1] / "runtime" / "h0_audit_store.py").read_text(
            encoding="utf-8")
        self.assertIn("NOT an identity guarantee", doc)


class R9_2_IdentityNotString(unittest.TestCase):
    def test_binding_is_compared_by_object_identity(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            self.assertIs(k._bound_store(), k.audit)
            k._trusted_store = object()
            with self.assertRaises(H0Error) as ctx:
                k._assert_store_identity()
            self.assertEqual(ctx.exception.code, "E_AUDIT_STORE_SUBSTITUTED")

    def test_bound_store_resolves_even_after_instance_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            real = k._bound_store()
            k._trusted_store = object()
            self.assertIs(k._bound_store(), real,
                          "resolution goes through the class table, not the instance")


class R9_3_StatedLimitIsReal(unittest.TestCase):
    def test_class_table_is_reachable_by_same_process_code(self):
        """This test RECORDS the limit rather than hiding it: code in this process can
        import the class and rebind. R9 does not claim otherwise."""
        from h0_kernel import _TrustedStore
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            real = k._bound_store()
            forged = object()
            _TrustedStore._table()[k] = forged
            self.assertIs(k._bound_store(), forged,
                          "same-process code CAN redirect resolution - this is the "
                          "documented limit of an in-process boundary")
            _TrustedStore._table()[k] = real

    def test_document_states_no_claim_against_same_process_code(self):
        doc = (Path(__file__).resolve().parents[1] / "citadel" / "h0"
               / "H0-CORRECTION-REPORT-R9-20261102.md").read_text(encoding="utf-8")
        self.assertIn("does not defend against arbitrary code", doc)
        self.assertIn("process or OS isolation", doc)


class R9_4_EvidenceConsistency(unittest.TestCase):
    def test_report_counts_match_suite_sizes(self):
        """R8 shipped a report claiming 12/12 against an artifact showing 10/10."""
        import re
        base = Path(__file__).resolve().parents[1]
        report = (base / "citadel" / "h0" / "H0-CORRECTION-REPORT-R9-20261102.md").read_text(encoding="utf-8")
        claims = dict(re.findall(r"`(test_h0_contract[^`]*)\.py`\| \*\*(\d+)/\d+", report.replace("\n", "")))
        actual = {}
        for path in sorted((base / "runtime").glob("test_h0_contract*.py")):
            n = len(re.findall(r"^\s+def test_", path.read_text(encoding="utf-8"), re.M))
            actual[path.stem] = n
        for name, count in claims.items():
            if name in actual:
                self.assertEqual(int(count), actual[name],
                                 f"{name}: report says {count}, suite has {actual[name]}")


if __name__ == "__main__":
    unittest.main()
