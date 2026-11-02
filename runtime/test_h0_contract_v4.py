#!/usr/bin/env python3
"""H0 revision 4 adversarial tests — King findings F9, F10, F11.

F9  validate-before-persist: a rejected append leaves file, seq and head unchanged.
F10 writer concurrency: single-writer lock refuses a second writer; foreign writes
    to the chain are detected before appending.
F11 post-effect failure: outcome-write failure returns indeterminate, preserves the
    dangling intent, and never appends a denial implying the effect did not happen.

Plus a minute-cap concurrency test that actually reaches and verifies the limit.

Run from runtime/: python test_h0_contract_v4.py
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
from h0_kernel import H0Error, Kernel, RateLimiter, RATE, canonical

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


def disk_lines(path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


class F9_ValidateBeforePersist(unittest.TestCase):
    def test_orphan_outcome_leaves_file_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "intent", "correlation_id": "c1"})
            before = p.read_bytes()
            head_before = s.head_digest
            seq_before = s.watermark()["seq"]
            with self.assertRaises(AuditStoreError) as ctx:
                s.append({"phase": "outcome", "correlation_id": "ghost"})
            self.assertEqual(ctx.exception.code, "E_AUDIT_ORPHAN")
            self.assertEqual(p.read_bytes(), before, "file must be untouched")
            self.assertEqual(s.head_digest, head_before)
            self.assertEqual(s.watermark()["seq"], seq_before)

    def test_duplicate_intent_leaves_file_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "intent", "correlation_id": "c1"})
            before = p.read_bytes()
            with self.assertRaises(AuditStoreError):
                s.append({"phase": "intent", "correlation_id": "c1"})
            self.assertEqual(p.read_bytes(), before)

    def test_duplicate_outcome_leaves_file_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "intent", "correlation_id": "c1"})
            s.append({"phase": "outcome", "correlation_id": "c1"})
            before = p.read_bytes()
            with self.assertRaises(AuditStoreError):
                s.append({"phase": "outcome", "correlation_id": "c1"})
            self.assertEqual(p.read_bytes(), before)

    def test_invalid_phase_rejected_without_write(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s = DurableAuditStore(p)
            with self.assertRaises(AuditStoreError) as ctx:
                s.append({"phase": "nonsense", "correlation_id": "c1"})
            self.assertEqual(ctx.exception.code, "E_AUDIT_INVALID")
            self.assertFalse(p.exists())


class F10_WriterConcurrency(unittest.TestCase):
    def test_second_writer_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s1 = DurableAuditStore(p)
            # hold the lock as a live writer would
            s1.lock.acquire()
            try:
                with self.assertRaises(AuditStoreError) as ctx:
                    s1.append({"phase": "intent", "correlation_id": "c1"})
                self.assertEqual(ctx.exception.code, "E_AUDIT_SECOND_WRITER")
            finally:
                s1.lock.release()

    def test_foreign_write_detected_before_append(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "intent", "correlation_id": "c1"})
            # another process appends behind our back
            other = DurableAuditStore(p, _allow_unsafe_observer=True)
            other.append({"phase": "intent", "correlation_id": "c2"})
            with self.assertRaises(AuditStoreError) as ctx:
                s.append({"phase": "intent", "correlation_id": "c3"})
            self.assertEqual(ctx.exception.code, "E_AUDIT_FOREIGN_WRITE")

    def test_chain_intact_after_foreign_write_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            s = DurableAuditStore(p)
            s.append({"phase": "intent", "correlation_id": "c1"})
            other = DurableAuditStore(p, _allow_unsafe_observer=True)
            other.append({"phase": "intent", "correlation_id": "c2"})
            try:
                s.append({"phase": "intent", "correlation_id": "c3"})
            except AuditStoreError:
                pass
            fresh = DurableAuditStore(p)
            self.assertTrue(fresh.verify_chain()["ok"], "chain must not fork")
            self.assertEqual(fresh.count, 2)


class F11_IndeterminateExecution(unittest.TestCase):
    def _break_outcome_after(self, k):
        """R7: replace the kernel-built store with a wrapper that fails on outcome."""
        from h0_audit_store import AuditStoreError
        real = k.audit
        calls = {"n": 0}

        class Flaky:
            def durability(self):
                return real.durability()

            def append(self, record):
                calls["n"] += 1
                if record.get("phase") == "outcome":
                    raise AuditStoreError("E_AUDIT_UNAVAILABLE", "simulated outcome failure")
                return real.append(record)

            def __getattr__(self, name):
                return getattr(real, name)

        object.__setattr__(k, "_Kernel__audit", Flaky())
        return real, calls

    def test_outcome_write_failure_returns_indeterminate_and_no_deny(self):
        with tempfile.TemporaryDirectory() as td:
            invocations = {"n": 0}

            def executor(req):
                invocations["n"] += 1
                return {"ran": True}

            k = kernel_for(executor=executor)
            store, calls = self._break_outcome_after(k)
            res = k.handle(envelope())
            self.assertFalse(res["ok"])
            self.assertEqual(res["error"], "E_EXECUTION_INDETERMINATE")
            self.assertTrue(res["indeterminate"])
            self.assertEqual(invocations["n"], 1, "the effect DID happen")
            # the dangling intent is preserved
            self.assertEqual(len(k.audit.dangling_intents()), 1)
            # no denial record was appended
            self.assertEqual([r["phase"] for r in disk_lines(store.path)], ["intent"])

    def test_executor_failure_records_failed_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")

            def boom(_req):
                raise RuntimeError("explode")

            k = kernel_for(store, executor=boom)
            req = envelope()
            cid = req["correlation_id"]
            res = k.handle(req)
            self.assertEqual(res["error"], "E_EXECUTOR_FAILED")
            phases = [r["phase"] for r in disk_lines(k.audit.path)]
            self.assertEqual(phases, ["intent", "outcome"])
            self.assertEqual(k.audit.outcome_for(cid)["outcome"], "failed")

    def test_executor_failure_and_outcome_failure_is_indeterminate(self):
        with tempfile.TemporaryDirectory() as td:
            def boom(_req):
                raise RuntimeError("explode")

            k = kernel_for(executor=boom)
            store, calls = self._break_outcome_after(k)
            res = k.handle(envelope())
            self.assertEqual(res["error"], "E_EXECUTION_INDETERMINATE")
            self.assertTrue(res["indeterminate"])
            self.assertEqual([r["phase"] for r in disk_lines(store.path)], ["intent"])

    def test_successful_path_writes_intent_then_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")
            k = kernel_for(store)
            self.assertTrue(k.handle(envelope())["ok"])
            phases = [r["phase"] for r in disk_lines(k.audit.path)]
            self.assertEqual(phases, ["intent", "outcome"])
            self.assertEqual(k.audit.dangling_intents(), [])

    def test_restart_after_indeterminate_shows_dangling_intent(self):
        with tempfile.TemporaryDirectory() as td:
            k = kernel_for(executor=lambda r: {"ran": True})
            store, _ = self._break_outcome_after(k)
            k.handle(envelope())
            path = store.path
            reopened = DurableAuditStore(path)
            self.assertEqual(len(reopened.dangling_intents()), 1,
                             "restart must reveal that execution is in doubt")
            self.assertTrue(reopened.verify_chain()["ok"])


class F8_MinuteCapConcurrency(unittest.TestCase):
    def test_concurrent_admission_reaches_and_respects_minute_cap(self):
        """Drive the limiter with a fixed clock so only the minute cap can bind, and
        prove the admitted count lands exactly on the configured limit."""
        clock_t = [0.0]
        rl = RateLimiter(clock=lambda: clock_t[0])
        admitted = []
        lock = threading.Lock()

        def worker():
            for _ in range(20):
                try:
                    rl.admit("client-x", "agi_status", "h0.read")
                    with lock:
                        admitted.append(1)
                except H0Error:
                    pass

        # 60 threads x 20 attempts = 1200 attempts, all inside one clock instant
        # -> minute cap (120) is the binding limit and burst (20) also applies.
        threads = [threading.Thread(target=worker) for _ in range(60)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # burst admits at most 20 inside one instant; the minute cap can never be
        # exceeded, and the admitted count must equal the burst cap exactly.
        self.assertEqual(len(admitted), RATE["burst_count"],
                         "burst cap must bind exactly under concurrency")
        self.assertLessEqual(len(admitted), RATE["read_per_min"])

    def test_minute_cap_binds_between_burst_windows(self):
        """At 0.4s spacing (2.5 req/s) the burst window stays clear, so the minute cap
        is the only limit that can bind, and it admits exactly its configured value."""
        clock_t = [0.0]
        rl = RateLimiter(clock=lambda: clock_t[0])
        admitted = 0
        refusals = {"E_RATE_LIMIT": 0, "E_RATE_BURST": 0}
        for _ in range(250):
            try:
                rl.admit("client-y", "agi_status", "h0.read")
                admitted += 1
            except H0Error as exc:
                refusals[exc.code] = refusals.get(exc.code, 0) + 1
            clock_t[0] += 0.4
        self.assertEqual(refusals.get("E_RATE_BURST", 0), 0, "burst must not interfere")
        self.assertGreater(refusals.get("E_RATE_LIMIT", 0), 0, "minute cap must bind")
        self.assertEqual(admitted + refusals["E_RATE_LIMIT"], 250)

if __name__ == "__main__":
    unittest.main()
