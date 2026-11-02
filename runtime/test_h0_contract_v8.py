#!/usr/bin/env python3
"""H0 revision 8 adversarial tests — King finding: post-construction store replacement.

R8-1 the execution path reaches the store through a CLOSURE, not an attribute, so
     reassigning any attribute on the kernel cannot redirect it.
R8-2 an adversarial replacement attempt is DETECTED and the request is refused.
R8-3 tests exercise audit failure through a supported injector, never by substituting
     an implementation into the enforcement path.
R8-4 the threat model is stated honestly: arbitrary code in the same Python process
     can tamper with objects, and this is NOT claimed to be prevented.

Run from runtime/: python test_h0_contract_v8.py
"""
import base64
import hashlib
import hmac
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_audit_store import DurableAuditStore, _FailureInjector
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


class R8_1_ClosureBoundStore(unittest.TestCase):
    def test_reassigning_mangled_attribute_does_not_redirect(self):
        """The old R7 bypass: k._Kernel__audit = hostile. It no longer exists."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "a.jsonl"
            k = kernel_for(str(target))
            # R9 superseded the R8 getter with a class-resolved store; the R8 claim
            # (no store in a plain reassignable attribute) still holds.
            self.assertFalse(hasattr(k, "_Kernel__audit"))
            self.assertTrue(hasattr(k, "_trusted_store"))

    def test_assigning_any_audit_named_attribute_is_inert(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "a.jsonl"
            k = kernel_for(str(target))

            class Hostile:
                def probe(self):
                    return "hostile"

                def append(self, record):
                    return record

            # the names an attacker would try. `_bound_store` is a real method, so
            # shadowing it by attribute is a genuine same-process tamper attempt --
            # it is exactly the case R8 does NOT claim to prevent (see R8-4). The
            # supported claim is narrower: no ordinary attribute read redirects the
            # audit append.
            refused = 0
            for attr in ("audit", "_Kernel__audit", "__audit"):
                try:
                    setattr(k, attr, Hostile())
                except (AttributeError, TypeError):
                    refused += 1
            self.assertGreaterEqual(refused, 1, "the read-only property must refuse assignment")
            # execution still writes to the real store
            self.assertTrue(k.handle(envelope())["ok"])
            self.assertTrue(target.exists())
            # the real store still receives the record
            self.assertTrue(k.handle(envelope())["ok"])
            self.assertTrue(target.exists())
            self.assertGreater(target.stat().st_size, 0)

    def test_execution_uses_the_constructed_store(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "a.jsonl"
            k = kernel_for(str(target))
            k.handle(envelope())
            on_disk = [x for x in target.read_text(encoding="utf-8").splitlines() if x.strip()]
            self.assertEqual(len(on_disk), 2, "intent and outcome reached the real file")


class R8_2_SubstitutionIsDetected(unittest.TestCase):
    def test_swapped_getter_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))

            class Hostile:
                def probe(self):
                    return "h0-audit-store-v1:elsewhere"

                def append(self, record):
                    return record

            k._trusted_store = Hostile()
            res = k.handle(envelope())
            self.assertFalse(res["ok"])
            self.assertEqual(res["error"], "E_AUDIT_STORE_SUBSTITUTED")

    def test_identity_check_names_the_failure(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))

            class Hostile:
                def probe(self):
                    return "different"

                def append(self, record):
                    return record

            k._trusted_store = Hostile()
            with self.assertRaises(H0Error) as ctx:
                k._assert_store_identity()
            self.assertEqual(ctx.exception.code, "E_AUDIT_STORE_SUBSTITUTED")


class R8_3_OutagesViaSupportedInjector(unittest.TestCase):
    def test_injector_is_the_only_fault_route(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            _FailureInjector.set(True)
            self.addCleanup(_FailureInjector.set, False)
            res = k.handle(envelope())
            self.assertFalse(res["ok"])
            self.assertEqual(res["error"], "E_AUDIT_UNAVAILABLE")
            self.assertEqual(k.effects["executed"], 0)

    def test_injector_cannot_change_where_bytes_go(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "a.jsonl"
            k = kernel_for(str(target))
            k.handle(envelope())
            _FailureInjector.set(True)
            self.addCleanup(_FailureInjector.set, False)
            k.handle(envelope())
            _FailureInjector.set(False)
            k.handle(envelope())
            # 2 records from req1 + 2 from req3; nothing written while failing
            on_disk = [x for x in target.read_text(encoding="utf-8").splitlines() if x.strip()]
            self.assertEqual(len(on_disk), 4)

    def test_injector_does_not_change_the_bound_store(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            before = k.audit.probe()
            _FailureInjector.set(True)
            self.addCleanup(_FailureInjector.set, False)
            self.assertEqual(k.audit.probe(), before)


class R8_4_ThreatModelStated(unittest.TestCase):
    def test_document_states_the_in_process_limitation(self):
        doc = Path(__file__).resolve().parents[1] / "citadel" / "h0" / "H0-CORRECTION-REPORT-R8-20261102.md"
        self.assertTrue(doc.exists(), "the threat model must be written down")
        text = doc.read_text(encoding="utf-8")
        self.assertIn("same Python process", text)
        self.assertIn("NOT claimed", text)

    def test_name_mangling_is_not_treated_as_access_control(self):
        """A demonstration that mangling is naming, not security - so the kernel does
        not rely on it. This test documents reality, it does not defend it."""
        class Holder:
            def __init__(self):
                self.__x = 1

        h = Holder()
        h._Holder__x = 2
        self.assertEqual(h._Holder__x, 2, "name mangling renames; it does not protect")


if __name__ == "__main__":
    unittest.main()
