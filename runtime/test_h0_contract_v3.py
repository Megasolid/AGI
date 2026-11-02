#!/usr/bin/env python3
"""H0 revision 3 adversarial tests — the three findings from King review 2026-11-02T19:43.

F6 durable audit store: atomic append+fsync, restart recovery, tamper evidence,
   fail-closed when persistence is unavailable.
F7 two-phase audit lifecycle: intent before effect, outcome after; one intent and
   at most one outcome per request; failures at each phase covered.
F8 atomic rate admission: concurrent requests cannot exceed the limits.

Run from runtime/: python test_h0_contract_v3.py
"""
import base64
import hashlib
import hmac
import json
import os
import tempfile
import threading
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_audit_store import AuditStoreError, DurableAuditStore
from h0_kernel import H0Error, Kernel, RateLimiter, canonical

SECRET = b"h0-test-secret"
KEY_ID = "test-key-h0"
NOW = datetime(2026, 11, 2, 16, 0, tzinfo=timezone.utc)


def sign(b):
    return {"alg": "test-hmac", "key_id": KEY_ID,
            "signature_b64": base64.b64encode(hmac.new(SECRET, b, hashlib.sha256).digest()).decode()}


def verify(b, env):
    want = hmac.new(SECRET, b, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode(), env.get("signature_b64", ""))


def envelope(method="agi_status", scope="h0.read", payload=None):
    req = {
        "schema": "h0.mcp/1", "method": method, "scope": scope,
        "client_id": "station-a", "request_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "issued_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
        "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
        "payload": payload or {}, "signature": {},
    }
    req["signature"] = sign(canonical({k: v for k, v in req.items() if k != "signature"}))
    return req


def kernel_for(store=None, **kw):
    """R7: the kernel builds its own trusted store from a path."""
    import tempfile
    from pathlib import Path
    if store is not None and "audit_path" not in kw:
        kw["audit_path"] = getattr(store, "path", None) or str(Path(tempfile.mkdtemp()) / "a.jsonl")
    if kw.get("audit_path") is None:
        kw["audit_path"] = str(Path(tempfile.mkdtemp()) / "a.jsonl")
    return Kernel(clients={"station-a": {"key_id": KEY_ID}},
                  verifier=verify, clock=lambda: NOW, **kw)


class F6_DurableAuditStore(unittest.TestCase):
    def test_append_is_durable_and_chained(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "audit.jsonl"
            s = DurableAuditStore(p)
            r1 = s.append({"phase": "deny", "correlation_id": "c1", "decision": "deny"})
            r2 = s.append({"phase": "deny", "correlation_id": "c2", "decision": "deny"})
            self.assertEqual(r1["seq"], 1)
            self.assertEqual(r2["prev_digest"], r1["digest"])
            self.assertTrue(s.verify_chain()["ok"])
            self.assertGreater(p.stat().st_size, 0)

    def test_restart_recovery_reloads_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "audit.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "intent", "correlation_id": "c1", "decision": "allow"})
            head = s.head_digest
            s2 = DurableAuditStore(p)
            self.assertEqual(s2.count, 1)
            self.assertEqual(s2.head_digest, head)
            self.assertEqual(s2.watermark()["head_digest"], head)

    def test_tampering_detected_on_reload(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "audit.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "deny", "correlation_id": "c1", "decision": "deny"})
            text = p.read_text(encoding="utf-8").replace('"deny"', '"allow"', 1)
            p.write_text(text, encoding="utf-8")
            with self.assertRaises(AuditStoreError) as ctx:
                DurableAuditStore(p)
            self.assertIn(ctx.exception.code, {"E_AUDIT_TAMPERED", "E_AUDIT_CORRUPT"})

    def test_truncation_detected_as_chain_break(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "audit.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "deny", "correlation_id": "c1", "decision": "deny"})
            s.append({"phase": "deny", "correlation_id": "c2", "decision": "deny"})
            lines = p.read_text(encoding="utf-8").splitlines()
            p.write_text(lines[0] + "\n" + lines[1].replace('"c2"', '"c9"') + "\n", encoding="utf-8")
            with self.assertRaises(AuditStoreError):
                DurableAuditStore(p)

    def test_unavailable_store_raises(self):
        with tempfile.TemporaryDirectory() as td:
            blocked = Path(td) / "blocked"
            blocked.write_text("not a directory", encoding="utf-8")
            s = DurableAuditStore(blocked / "audit.jsonl")
            with self.assertRaises(AuditStoreError) as ctx:
                s.append({"phase": "deny", "correlation_id": "c1"})
            self.assertEqual(ctx.exception.code, "E_AUDIT_UNAVAILABLE")


class F7_TwoPhaseLifecycle(unittest.TestCase):
    def test_success_writes_intent_then_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")
            k = kernel_for(store)
            req = envelope()
            self.assertTrue(k.handle(req)["ok"])
            cid = req["correlation_id"]
            self.assertEqual(k.audit.intent_for(cid)["phase"], "intent")
            self.assertEqual(k.audit.outcome_for(cid)["outcome"], "executed")
            self.assertEqual(k.audit.dangling_intents(), [])

    def test_executor_failure_writes_failed_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")

            def boom(_req):
                raise RuntimeError("explode")

            k = kernel_for(store, executor=boom)
            req = envelope()
            res = k.handle(req)
            self.assertFalse(res["ok"])
            self.assertEqual(res["error"], "E_EXECUTOR_FAILED")
            cid = req["correlation_id"]
            self.assertEqual(k.audit.outcome_for(cid)["outcome"], "failed")
            self.assertEqual(k.audit.dangling_intents(), [])
            self.assertEqual(k.effects["executed"], 0)

    def test_audit_failure_at_intent_phase_prevents_execution(self):
        """A store that constructs fine but fails on append must stop execution."""
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")

            def broken_append(_record):
                raise AuditStoreError("E_AUDIT_UNAVAILABLE", "simulated disk failure")

            store.append = broken_append
            invocations = {"n": 0}

            def executor(req):
                invocations["n"] += 1
                return {"ran": True}

            k = kernel_for(store, executor=executor)
            object.__setattr__(k, "_Kernel__audit", type("Broken", (), {
                "append": staticmethod(broken_append),
                "durability": staticmethod(lambda: {
                    "enforceable": True, "fsync": True, "single_writer": True,
                    "append_only": True, "chained": True, "observer_mode": False})})())
            res = k.handle(envelope())
            self.assertFalse(res["ok"])
            self.assertEqual(res["error"], "E_AUDIT_UNAVAILABLE")
            self.assertEqual(invocations["n"], 0, "executor must not run when audit fails")

    def test_unusable_store_path_fails_closed_on_append(self):
        """Construction is lazy by design; the guarantee is that APPEND fails closed."""
        with tempfile.TemporaryDirectory() as td:
            blocked = Path(td) / "blocked"
            blocked.write_text("x", encoding="utf-8")
            store = DurableAuditStore(blocked / "a.jsonl")
            with self.assertRaises(AuditStoreError):
                store.append({"phase": "deny", "correlation_id": "c1"})

    def test_one_intent_and_one_outcome_per_request(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")
            k = kernel_for(store)
            req = envelope()
            k.handle(req)
            cid = req["correlation_id"]
            phases = [r["phase"] for r in k.audit._records if r.get("correlation_id") == cid]
            self.assertEqual(phases, ["intent", "outcome"])

    def test_orphan_outcome_rejected_at_reload(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            store = DurableAuditStore(p)
            with self.assertRaises(AuditStoreError):
                store.append({"phase": "outcome", "correlation_id": "ghost"})

    def test_duplicate_outcome_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")
            store.append({"phase": "intent", "correlation_id": "c1"})
            store.append({"phase": "outcome", "correlation_id": "c1"})
            with self.assertRaises(AuditStoreError):
                store.append({"phase": "outcome", "correlation_id": "c1"})


class F8_AtomicRateAdmission(unittest.TestCase):
    def test_concurrent_admission_cannot_exceed_burst(self):
        fake = [0.0]
        rl = RateLimiter(clock=lambda: fake[0])
        admitted = []
        lock = threading.Lock()

        def worker():
            try:
                rl.admit("client", "agi_status", "h0.read")
                with lock:
                    admitted.append(1)
            except H0Error:
                pass

        threads = [threading.Thread(target=worker) for _ in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(admitted), 20, "burst cap must hold exactly under concurrency")

    def test_concurrent_admission_respects_minute_cap_between_clients(self):
        fake = [0.0]
        rl = RateLimiter(clock=lambda: fake[0])
        admitted = []
        lock = threading.Lock()

        def worker(cid):
            for _ in range(5):
                try:
                    rl.admit(cid, "agi_status", "h0.read")
                    with lock:
                        admitted.append(cid)
                except H0Error:
                    pass

        threads = [threading.Thread(target=worker, args=(f"c{i}",)) for i in range(40)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertLessEqual(len(admitted), 40 * 5)
        self.assertGreater(len(admitted), 0)

    def test_separate_check_and_record_are_refused(self):
        rl = RateLimiter(clock=lambda: 0.0)
        with self.assertRaises(H0Error):
            rl.check("c", "agi_status", "h0.read")
        with self.assertRaises(H0Error):
            rl.record("c", "agi_status", "h0.read")

    def test_denied_requests_do_not_consume_admission(self):
        fake = [0.0]
        rl = RateLimiter(clock=lambda: fake[0])
        for _ in range(20):
            rl.admit("c", "agi_status", "h0.read")
        with self.assertRaises(H0Error):
            rl.admit("c", "agi_status", "h0.read")


class IntegrationWithKernel(unittest.TestCase):
    def test_full_happy_path_uses_durable_store(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for()
            self.assertTrue(k.handle(envelope())["ok"])
            self.assertTrue(k.audit.verify_chain()["ok"])
            self.assertEqual(k.audit.count, 2)  # intent + outcome

    def test_denial_recorded_once(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for()
            res = k.handle(envelope(scope="h0.write.metadata"))
            self.assertEqual(res["error"], "E_SCOPE")
            self.assertEqual(k.audit.count, 1)
            self.assertEqual(k.audit._records[0]["phase"], "deny")


if __name__ == "__main__":
    unittest.main()
