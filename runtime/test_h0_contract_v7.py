#!/usr/bin/env python3
"""H0 revision 7 adversarial tests — King finding: self-attestation one layer deeper.

R7-1 the enforcement audit store is BUILT BY THE KERNEL from an on-disk path and is
     not injectable; a caller-controlled implementation cannot assert its own safety.
R7-2 a hostile subclass overriding durability() and append() has no route into the
     execution path.
R7-3 a fake implementation that reports success without persisting is unrepresentable.
R7-4 R5 request-local accounting: the REAL barrier-synchronised scenario, carried
     forward (two intents, two outcomes, zero dangling, correct later denial).

Run from runtime/: python test_h0_contract_v7.py
"""
import base64
import hashlib
import hmac
import inspect
import tempfile
import threading
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_audit_store import DurableAuditStore
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


def envelope(payload=None, scope="h0.read"):
    req = {"schema": "h0.mcp/1", "method": "agi_status", "scope": scope,
           "client_id": "station-a", "request_id": str(uuid.uuid4()),
           "correlation_id": str(uuid.uuid4()), "issued_at": NOW.isoformat(),
           "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
           "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
           "payload": payload or {}, "signature": {}}
    req["signature"] = sign(canonical({k: v for k, v in req.items() if k != "signature"}))
    return req


def kernel_for(audit_path, **kw):
    return Kernel(clients={"station-a": {"key_id": KEY_ID}},
                  verifier=verify, clock=lambda: NOW, audit_path=audit_path, **kw)


class R7_1_StoreIsNotInjectable(unittest.TestCase):
    def test_kernel_signature_has_no_audit_parameter(self):
        params = inspect.signature(Kernel.__init__).parameters
        self.assertNotIn("audit", params, "no store may be injected")
        self.assertIn("audit_path", params)

    def test_kernel_builds_its_own_store_of_the_trusted_type(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            self.assertIs(type(k.audit), DurableAuditStore)

    def test_missing_audit_path_is_refused(self):
        with self.assertRaises(H0Error) as ctx:
            Kernel(clients={"station-a": {"key_id": KEY_ID}}, verifier=verify,
                   clock=lambda: NOW)
        self.assertEqual(ctx.exception.code, "E_AUDIT_REQUIRED")

    def test_audit_property_is_read_only_view(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"))
            k.audit  # readable
            with self.assertRaises(AttributeError):
                k.audit = object()  # not assignable


class R7_2_HostileSubclassHasNoRoute(unittest.TestCase):
    def test_hostile_class_with_perfect_contract_is_unreachable(self):
        """A class that answers durability() perfectly and lies in append() has no entry
        point: the kernel only accepts a path."""
        class Hostile:
            def durability(self):
                return {"enforceable": True, "fsync": True, "single_writer": True,
                        "append_only": True, "chained": True, "observer_mode": False}

            def append(self, record):
                return record  # pretending

        params = inspect.signature(Kernel.__init__).parameters
        self.assertNotIn("audit", params)
        # and the contract checker alone still passes it -> which is exactly why the
        # store must never be caller-supplied
        Kernel._require_enforceable_store(Hostile())

    def test_durability_override_on_a_real_store_cannot_be_smuggled_in(self):
        class Disguised(DurableAuditStore):
            def durability(self):
                d = super().durability()
                d["fsync"] = True
                d["enforceable"] = True
                return d

            def append(self, record):
                return record  # never persists

        with tempfile.TemporaryDirectory() as td:
            fake = Disguised(Path(td) / "a.jsonl")
            self.assertTrue(fake.durability()["enforceable"])
            with self.assertRaises(TypeError):
                Kernel(clients={"station-a": {"key_id": KEY_ID}}, verifier=verify,
                       clock=lambda: NOW, audit=fake)


class R7_3_NonPersistingImplementationUnrepresentable(unittest.TestCase):
    def test_fake_that_reports_success_without_persisting_is_unreachable(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "a.jsonl"
            k = kernel_for(str(target))
            self.assertTrue(k.handle(envelope())["ok"])
            # the kernel's own store actually wrote to disk
            self.assertTrue(target.exists())
            self.assertGreater(target.stat().st_size, 0)

    def test_execution_and_persistence_are_the_same_object(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "a.jsonl"
            k = kernel_for(str(target))
            k.handle(envelope())
            on_disk = len([x for x in target.read_text(encoding="utf-8").splitlines() if x.strip()])
            self.assertEqual(on_disk, k.audit.count,
                             "what the kernel reports must be what reached the disk")


class R7_4_RequestLocalAccountingCarriedForward(unittest.TestCase):
    """The genuine barrier-synchronised scenario from R5, carried forward intact."""

    def test_concurrent_executor_failure_and_success_keep_their_records(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(str(Path(td) / "a.jsonl"), executor=self._executor_with_barrier([None]))
            barrier = threading.Barrier(2)

            def executor(req):
                barrier.wait(timeout=5)
                if "explode" in (req["payload"].get("include") or []):
                    raise RuntimeError("boom")
                return {"ok": True}

            k.executor = executor
            results = {}

            def fire(explode):
                r = envelope(payload={"include": ["explode"]} if explode else {})
                results["boom" if explode else "ok"] = k.handle(r)

            t1 = threading.Thread(target=fire, args=(True,))
            t2 = threading.Thread(target=fire, args=(False,))
            t1.start(); t2.start(); t1.join(); t2.join()

            self.assertFalse(results["boom"]["ok"])
            self.assertTrue(results["ok"]["ok"])

            intents = [r["correlation_id"] for r in k.audit._records if r["phase"] == "intent"]
            outcomes = [r["correlation_id"] for r in k.audit._records if r["phase"] == "outcome"]
            self.assertEqual(len(intents), 2)
            self.assertEqual(len(set(intents)), 2, "two distinct intents")
            self.assertEqual(len(outcomes), 2, "two distinct outcomes")
            self.assertEqual(k.audit.dangling_intents(), [], "no dangling intents")

            # a subsequent unrelated denial is still accounted for
            before = k.audit.count
            r3 = k.handle(envelope(scope="h0.write.metadata"))
            self.assertEqual(r3["error"], "E_SCOPE")
            self.assertEqual(k.audit.count, before + 1,
                             "later denial accounting must not be stolen by the failure")

    @staticmethod
    def _executor_with_barrier(_unused):
        return None


if __name__ == "__main__":
    unittest.main()
