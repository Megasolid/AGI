#!/usr/bin/env python3
"""H0 revision 5 adversarial tests — King findings G1..G5.

G1 durable audit MANDATORY: no implicit in-memory fallback in an execution-capable
   kernel; an in-memory sink is rejected with E_AUDIT_NOT_DURABLE.
G2 request-local accounting: concurrent executor failures and unrelated denials must
   not steal each other's audit records.
G3 lifecycle invariants validated during RECOVERY, not only append.
G4 the FULL on-disk chain is verified before appending, not just the tail digest.
G5 the single-writer bypass is not selectable from an enforcement configuration.

Run from runtime/: python test_h0_contract_v5.py
"""
import base64
import hashlib
import hmac
import json
import tempfile
import threading
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_audit_store import AuditStoreError, DurableAuditStore
from h0_kernel import AuditLog, H0Error, Kernel, canonical

SECRET = b"h0-test-secret"
KEY_ID = "test-key-h0"
NOW = datetime(2026, 11, 2, 16, 0, tzinfo=timezone.utc)


def sign(b):
    return {"alg": "test-hmac", "key_id": KEY_ID,
            "signature_b64": base64.b64encode(hmac.new(SECRET, b, hashlib.sha256).digest()).decode()}


def verify(b, env):
    want = hmac.new(SECRET, b, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode(), env.get("signature_b64", ""))


def envelope(method="agi_status", scope="h0.read", payload=None, request_id=None):
    req = {
        "schema": "h0.mcp/1", "method": method, "scope": scope,
        "client_id": "station-a", "request_id": request_id or str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "issued_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
        "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
        "payload": payload or {}, "signature": {},
    }
    req["signature"] = sign(canonical({k: v for k, v in req.items() if k != "signature"}))
    return req


def durable_store(td):
    return DurableAuditStore(Path(td) / "audit.jsonl")


def kernel_for(store, **kw):
    return Kernel(clients={"station-a": {"key_id": KEY_ID}},
                  verifier=verify, clock=lambda: NOW, audit=store, **kw)


class G1_DurableAuditMandatory(unittest.TestCase):
    def test_kernel_without_audit_is_refused(self):
        with self.assertRaises(H0Error) as ctx:
            Kernel(clients={"station-a": {"key_id": KEY_ID}}, verifier=verify,
                   clock=lambda: NOW, audit=None)
        self.assertEqual(ctx.exception.code, "E_AUDIT_REQUIRED")

    def test_in_memory_sink_is_refused(self):
        with self.assertRaises(H0Error) as ctx:
            Kernel(clients={"station-a": {"key_id": KEY_ID}}, verifier=verify,
                   clock=lambda: NOW, audit=AuditLog())
        self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")

    def test_store_not_declaring_durability_is_refused(self):
        class Sneaky:
            def append(self, rec):
                return rec

        with self.assertRaises(H0Error) as ctx:
            Kernel(clients={"station-a": {"key_id": KEY_ID}}, verifier=verify,
                   clock=lambda: NOW, audit=Sneaky())
        self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")

    def test_durable_store_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(durable_store(td))
            self.assertTrue(k.handle(envelope())["ok"])


class G2_RequestLocalAccounting(unittest.TestCase):
    def test_concurrent_requests_keep_their_own_records(self):
        """Two concurrent requests: one executor fails (denial already recorded),
        one is an unrelated success. Neither may steal or suppress the other's record."""
        with tempfile.TemporaryDirectory() as td:
            store = durable_store(td)
            barrier = threading.Barrier(2)

            def executor(req):
                barrier.wait(timeout=5)
                if ("explode" in (req["payload"].get("include") or [])):
                    raise RuntimeError("boom")
                return {"ok": True}

            k = kernel_for(store, executor=executor)
            results = {}

            def fire(explode):
                r = envelope(payload={"include": ["explode"]} if explode else {})
                results["boom" if explode else "ok"] = k.handle(r)

            t1 = threading.Thread(target=fire, args=(True,))
            t2 = threading.Thread(target=fire, args=(False,))
            t1.start(); t2.start(); t1.join(); t2.join()

            self.assertFalse(results["boom"]["ok"])
            self.assertTrue(results["ok"]["ok"])
            # exactly two intents and two outcomes, for two distinct correlations
            cids = [r["correlation_id"] for r in store._records if r["phase"] == "intent"]
            self.assertEqual(len(cids), 2)
            self.assertEqual(len(set(cids)), 2)
            self.assertEqual(len(store.dangling_intents()), 0)

    def test_executor_failure_does_not_suppress_unrelated_denial(self):
        with tempfile.TemporaryDirectory() as td:
            store = durable_store(td)

            def executor(req):
                if ("explode" in (req["payload"].get("include") or [])):
                    raise RuntimeError("boom")
                return {"ok": True}

            k = kernel_for(store, executor=executor)
            r1 = k.handle(envelope(payload={"include": ["explode"]}))
            self.assertEqual(r1["error"], "E_EXECUTOR_FAILED")
            before = store.count
            r2 = k.handle(envelope(scope="h0.write.metadata"))  # unrelated scope denial
            self.assertEqual(r2["error"], "E_SCOPE")
            self.assertEqual(store.count, before + 1, "the unrelated denial must be recorded")

    def test_repeated_failures_do_not_leak_state(self):
        with tempfile.TemporaryDirectory() as td:
            store = durable_store(td)

            def executor(req):
                raise RuntimeError("boom")

            k = kernel_for(store, executor=executor)
            for _ in range(5):
                self.assertEqual(k.handle(envelope())["error"], "E_EXECUTOR_FAILED")
            self.assertEqual(len([r for r in store._records if r["phase"] == "deny"]), 0,
                             "no duplicate deny records for accounted failures")


class G3_RecoveryValidation(unittest.TestCase):
    def _write_log(self, path, records):
        prev = None
        with path.open("w", encoding="utf-8") as fh:
            for i, rec in enumerate(records, 1):
                rec = dict(rec)
                rec["seq"] = i
                rec["prev_digest"] = prev
                body = {k: v for k, v in rec.items() if k != "digest"}
                rec["digest"] = "sha256:" + hashlib.sha256(
                    json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
                prev = rec["digest"]

    def test_digest_consistent_orphan_outcome_is_rejected_on_load(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            self._write_log(p, [{"phase": "outcome", "correlation_id": "ghost"}])
            with self.assertRaises(AuditStoreError) as ctx:
                DurableAuditStore(p)
            self.assertEqual(ctx.exception.code, "E_AUDIT_ORPHAN")

    def test_duplicate_intent_rejected_on_load(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            self._write_log(p, [{"phase": "intent", "correlation_id": "c1"},
                                {"phase": "intent", "correlation_id": "c1"}])
            with self.assertRaises(AuditStoreError):
                DurableAuditStore(p)

    def test_unknown_phase_rejected_on_load(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            self._write_log(p, [{"phase": "nonsense", "correlation_id": "c1"}])
            with self.assertRaises(AuditStoreError):
                DurableAuditStore(p)


class G4_FullChainBeforeAppend(unittest.TestCase):
    def test_altered_earlier_record_detected_before_append(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            store = DurableAuditStore(p)
            store.append({"phase": "intent", "correlation_id": "c1"})
            store.append({"phase": "outcome", "correlation_id": "c1"})
            # rewrite the FIRST record but keep the final record intact
            lines = p.read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            first["correlation_id"] = "forged"
            lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(AuditStoreError) as ctx:
                store.append({"phase": "intent", "correlation_id": "c2"})
            self.assertIn(ctx.exception.code, {"E_AUDIT_TAMPERED", "E_AUDIT_CORRUPT"})

    def test_truncation_detected_before_append(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            store = DurableAuditStore(p)
            store.append({"phase": "intent", "correlation_id": "c1"})
            store.append({"phase": "outcome", "correlation_id": "c1"})
            lines = p.read_text(encoding="utf-8").splitlines()
            p.write_text(lines[0] + "\n", encoding="utf-8")
            with self.assertRaises(AuditStoreError):
                store.append({"phase": "intent", "correlation_id": "c2"})


class G5_WriterBypassIsolated(unittest.TestCase):
    def test_no_public_bypass_keyword(self):
        import inspect
        sig = inspect.signature(DurableAuditStore.__init__)
        self.assertNotIn("enforce_single_writer", sig.parameters,
                         "the lock bypass must not be a public enforcement option")
        self.assertIn("_allow_unsafe_observer", sig.parameters)
        self.assertTrue(sig.parameters["_allow_unsafe_observer"].default is False)

    def test_default_store_enforces_lock(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")
            self.assertTrue(store.enforce_single_writer)


if __name__ == "__main__":
    unittest.main()
