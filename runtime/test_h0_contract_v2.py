#!/usr/bin/env python3
"""H0 reference kernel — adversarial tests for the five review findings.

Revision 2 tests. The original 31-test evidence is preserved unchanged; this
file adds coverage for: F1 audit-as-precondition, F2 gate ordering, F3 atomic
replay under concurrency, F4 per-method payload schemas, F5 timestamp validation.

Run: python test_h0_contract_v2.py
"""
import base64
import hashlib
import hmac
import json
import threading
import unittest
import uuid
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_audit_store import DurableAuditStore
from h0_kernel import (
    FORBIDDEN_METHODS, LIMITS, METHOD_SCOPES, ORDER, PAYLOAD_SCHEMAS,
    REGISTERED_METHODS, AuditLog, H0Error, Kernel, RateLimiter,
    canonical, enforce_limits, validate_timestamps, validate_payload,
)

SECRET = b"h0-test-secret"
KEY_ID = "test-key-h0"
NOW = datetime(2026, 11, 2, 16, 0, tzinfo=timezone.utc)


def sign(payload_bytes):
    sig = hmac.new(SECRET, payload_bytes, hashlib.sha256).digest()
    return {"alg": "test-hmac", "key_id": KEY_ID, "signature_b64": base64.b64encode(sig).decode()}


def verify(payload_bytes, env):
    want = hmac.new(SECRET, payload_bytes, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode(), env.get("signature_b64", ""))


def valid_payload(method):
    if method == "agi_task_get":
        return {"task_id": "t-1"}
    if method == "agi_evidence_get":
        return {"evidence_id": "e-1"}
    if method == "agi_checkpoint_create":
        return {"checkpoint": "cp-1"}
    if method == "agi_receipt_submit":
        return {"handoff_digest": "sha256:" + "a" * 64, "outcome": "success"}
    if method == "agi_approval_request":
        return {"operation": "tag_release"}
    return {}


def envelope(method="agi_status", scope=None, payload=None, issued_at=None, expires_at=None, **over):
    req = {
        "schema": "h0.mcp/1",
        "method": method,
        "scope": scope or METHOD_SCOPES.get(method, "h0.read"),
        "client_id": "station-a",
        "request_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "issued_at": issued_at or NOW.isoformat(),
        "expires_at": expires_at or (NOW + timedelta(minutes=5)).isoformat(),
        "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
        "payload": payload if payload is not None else valid_payload(method),
        "signature": {},
    }
    req.update(over)
    body = {k: v for k, v in req.items() if k != "signature"}
    req["signature"] = sign(canonical(body))
    return req


def fresh_kernel(**kw):
    import tempfile
    from pathlib import Path
    from h0_audit_store import DurableAuditStore
    clients = {"station-a": {"key_id": KEY_ID, "revoked": False}}
    clients.update(kw.pop("clients", {}))
    clock = kw.pop("clock", lambda: NOW)
    if kw.get("audit") is None:
        kw["audit"] = DurableAuditStore(Path(tempfile.mkdtemp()) / "audit.jsonl")
    return Kernel(clients=clients, verifier=verify, clock=clock, **kw)


class F1_AuditPrecondition(unittest.TestCase):
    """The executor must never be invoked when the audit record cannot be written."""

    def test_executor_not_invoked_when_audit_fails(self):
        invoked = {"count": 0}

        def executor(req):
            invoked["count"] += 1
            return {"executed": True}

        st = DurableAuditStore(Path(tempfile.mkdtemp()) / "a.jsonl")

        def broken(_rec):
            from h0_audit_store import AuditStoreError
            raise AuditStoreError("E_AUDIT_UNAVAILABLE", "simulated")

        st.append = broken
        k = fresh_kernel(audit=st, executor=executor)
        res = k.handle(envelope())
        self.assertFalse(res["ok"])
        self.assertIn(res["error"], {"E_AUDIT_UNAVAILABLE"})
        self.assertEqual(invoked["count"], 0, "executor MUST NOT run before audit")
        self.assertEqual(k.effects["executed"], 0)

    def test_audit_failure_blocks_execution(self):
        st = DurableAuditStore(Path(tempfile.mkdtemp()) / "a.jsonl")

        def broken(_rec):
            from h0_audit_store import AuditStoreError
            raise AuditStoreError("E_AUDIT_UNAVAILABLE", "simulated")

        st.append = broken
        k = fresh_kernel(audit=st)
        res = k.handle(envelope())
        self.assertFalse(res["ok"])
        self.assertEqual(k.effects["executed"], 0)

    def test_audit_success_precedes_execution(self):
        order = []

        import tempfile
        from pathlib import Path
        durable = DurableAuditStore(Path(tempfile.mkdtemp()) / "a.jsonl")

        class Recorder:
            """Delegates the R6 durability contract to a real durable store."""

            def durability(self):
                return durable.durability()

            def append(self, record):
                order.append("audit:" + record["decision"])
                return durable.append(record)

        def executor(req):
            order.append("execute")
            return {"ok": True}

        k = fresh_kernel(audit=Recorder(), executor=executor)
        self.assertTrue(k.handle(envelope())["ok"])
        # v3 two-phase lifecycle: intent(allow) -> execute -> outcome(allow)
        self.assertEqual(order, ["audit:allow", "execute", "audit:allow"])


class F2_GateOrdering(unittest.TestCase):
    def test_order_matches_contract(self):
        self.assertEqual(ORDER, ("auth", "replay", "schema", "payload", "limits", "rate",
                                 "scope", "policy", "audit", "execute"))

    def test_allowed_request_traverses_every_gate_in_order(self):
        k = fresh_kernel()
        self.assertTrue(k.handle(envelope())["ok"])
        self.assertEqual(tuple(k.order_seen), ORDER)

    def test_denial_stops_at_the_failing_gate(self):
        k = fresh_kernel(policy_ok=lambda: False)
        k.handle(envelope())
        self.assertEqual(tuple(k.order_seen), ORDER[:8])  # stops before audit
        self.assertNotIn("execute", k.order_seen)

    def test_scope_violation_happens_after_rate(self):
        k = fresh_kernel()
        k.handle(envelope(method="agi_status", scope="h0.write.metadata"))
        idx = k.order_seen.index("rate")
        self.assertLess(idx, len(k.order_seen))
        self.assertNotIn("execute", k.order_seen)


class F3_AtomicReplay(unittest.TestCase):
    def test_concurrent_duplicate_request_ids(self):
        k = fresh_kernel()
        results = []

        def fire():
            results.append(k.handle(req))

        req = envelope()
        threads = [threading.Thread(target=fire) for _ in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        ok = [r for r in results if r["ok"]]
        denied = [r for r in results if not r["ok"]]
        self.assertEqual(len(ok), 1, "exactly one duplicate may succeed")
        self.assertEqual(len(denied), 15)
        for r in denied:
            self.assertEqual(r["error"], "E_REPLAY")

    def test_concurrent_duplicate_nonces(self):
        k = fresh_kernel()
        nonce = envelope()["nonce"]
        results = []

        def fire():
            r = envelope()
            r["nonce"] = nonce
            body = {x: v for x, v in r.items() if x != "signature"}
            r["signature"] = sign(canonical(body))
            results.append(k.handle(r))

        threads = [threading.Thread(target=fire) for _ in range(12)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len([r for r in results if r["ok"]]), 1)

    def test_denied_request_releases_reservation(self):
        k = fresh_kernel()
        req = envelope(method="agi_status", scope="h0.write.metadata")  # scope denial
        self.assertEqual(k.handle(req)["error"], "E_SCOPE")
        retry = envelope()
        retry["request_id"] = req["request_id"]
        retry["nonce"] = req["nonce"]
        body = {x: v for x, v in retry.items() if x != "signature"}
        retry["signature"] = sign(canonical(body))
        self.assertTrue(k.handle(retry)["ok"], "denial must not burn the id")

    def test_successful_request_consumes_id(self):
        k = fresh_kernel()
        req = envelope()
        self.assertTrue(k.handle(req)["ok"])
        self.assertEqual(k.handle(req)["error"], "E_REPLAY")


class F4_PayloadSchemas(unittest.TestCase):
    def test_every_registered_method_has_a_schema(self):
        self.assertEqual(set(PAYLOAD_SCHEMAS), set(REGISTERED_METHODS))

    def test_unknown_payload_field_rejected_for_every_method(self):
        for method in sorted(REGISTERED_METHODS):
            payload = valid_payload(method)
            payload["surprise"] = "x"
            with self.assertRaises(H0Error) as ctx:
                validate_payload(method, payload)
            self.assertEqual(ctx.exception.code, "E_UNKNOWN_PAYLOAD_FIELD", method)

    def test_missing_required_field_rejected(self):
        with self.assertRaises(H0Error) as ctx:
            validate_payload("agi_task_get", {})
        self.assertEqual(ctx.exception.code, "E_MALFORMED")

    def test_wrong_type_rejected(self):
        with self.assertRaises(H0Error):
            validate_payload("agi_task_list", {"limit": "many"})

    def test_bool_is_not_int(self):
        with self.assertRaises(H0Error):
            validate_payload("agi_task_list", {"limit": True})

    def test_valid_payloads_pass(self):
        for method in sorted(REGISTERED_METHODS):
            validate_payload(method, valid_payload(method))


class F5_Timestamps(unittest.TestCase):
    def test_naive_timestamp_rejected(self):
        with self.assertRaises(H0Error) as ctx:
            validate_timestamps({"issued_at": "2026-11-02T16:00:00",
                                 "expires_at": "2026-11-02T16:05:00"}, NOW)
        self.assertEqual(ctx.exception.code, "E_MALFORMED")

    def test_issued_after_expires_rejected(self):
        with self.assertRaises(H0Error):
            validate_timestamps({"issued_at": (NOW + timedelta(minutes=10)).isoformat(),
                                 "expires_at": (NOW + timedelta(minutes=5)).isoformat()}, NOW)

    def test_expired_request_rejected(self):
        with self.assertRaises(H0Error) as ctx:
            validate_timestamps({"issued_at": (NOW - timedelta(minutes=10)).isoformat(),
                                 "expires_at": (NOW - timedelta(minutes=1)).isoformat()}, NOW)
        self.assertEqual(ctx.exception.code, "E_EXPIRED")

    def test_future_issued_at_rejected(self):
        with self.assertRaises(H0Error) as ctx:
            validate_timestamps({"issued_at": (NOW + timedelta(hours=2)).isoformat(),
                                 "expires_at": (NOW + timedelta(hours=3)).isoformat()}, NOW)
        self.assertEqual(ctx.exception.code, "E_CLOCK_SKEW")

    def test_missing_expires_rejected(self):
        with self.assertRaises(H0Error):
            validate_timestamps({"issued_at": NOW.isoformat()}, NOW)

    def test_garbage_timestamp_rejected(self):
        with self.assertRaises(H0Error):
            validate_timestamps({"issued_at": "not-a-date", "expires_at": NOW.isoformat()}, NOW)


class RegressionOfOriginalContract(unittest.TestCase):
    """The properties the original 31 tests asserted must still hold."""

    def test_forbidden_methods_still_impossible(self):
        for name in sorted(FORBIDDEN_METHODS):
            with self.assertRaises(H0Error):
                Kernel.register_method(name)
            res = fresh_kernel().handle(envelope(method=name))
            self.assertEqual(res["error"], "E_FORBIDDEN_METHOD", name)

    def test_approval_cannot_approve(self):
        k = fresh_kernel()
        res = k.handle(envelope(method="agi_approval_request", payload={"operation": "tag_release"}))
        self.assertTrue(res["ok"])
        self.assertFalse(res["result"]["can_approve"])

    def test_policy_unavailable_denies_without_execution(self):
        invocations = {"n": 0}

        def executor(req):
            invocations["n"] += 1
            return {}

        k = fresh_kernel(policy_ok=lambda: False, executor=executor)
        self.assertEqual(k.handle(envelope())["error"], "E_POLICY_UNAVAILABLE")
        self.assertEqual(invocations["n"], 0)

    def test_audit_never_logs_payload(self):
        k = fresh_kernel()
        k.handle(envelope(payload={"include": ["do-not-log-me"]}))
        self.assertNotIn("do-not-log-me", json.dumps(k.audit._records))

    def test_limits_still_enforced(self):
        with self.assertRaises(H0Error):
            enforce_limits({"payload": {"s": "x" * (LIMITS["string_len"] + 1)}})


if __name__ == "__main__":
    unittest.main()
