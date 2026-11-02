import base64
import hashlib
import hmac
import json
import unittest
import uuid
from datetime import datetime, timedelta, timezone

from h0_kernel import (
    FORBIDDEN_METHODS, LIMITS, REGISTERED_METHODS, AuditLog, H0Error, Kernel, RateLimiter,
    canonical, enforce_limits, validate_envelope_shape,
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
    return {
        "agi_task_get": {"task_id": "t-1"},
        "agi_evidence_get": {"evidence_id": "e-1"},
        "agi_checkpoint_create": {"checkpoint": "cp-1"},
        "agi_receipt_submit": {"handoff_digest": "sha256:" + "a" * 64, "outcome": "success"},
        "agi_approval_request": {"operation": "tag_release"},
    }.get(method, {})


def envelope(method="agi_status", scope=None, payload=None, **over):
    from h0_kernel import METHOD_SCOPES
    req = {
        "schema": "h0.mcp/1",
        "method": method,
        "scope": scope or METHOD_SCOPES.get(method, "h0.read"),
        "client_id": "station-a",
        "request_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "issued_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
        "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
        "payload": payload if payload is not None else valid_payload(method),
        "signature": {},
    }
    req.update(over)
    body = {k: v for k, v in req.items() if k != "signature"}
    req["signature"] = sign(canonical(body))
    return req


def fresh_kernel(**kw):
    clients = {"station-a": {"key_id": KEY_ID, "revoked": False}}
    clients.update(kw.pop("clients", {}))
    clock = kw.pop("clock", lambda: NOW)
    return Kernel(clients=clients, verifier=verify, clock=clock, **kw)


class ForbiddenSurfaceTests(unittest.TestCase):
    def test_every_forbidden_method_refused_at_registration(self):
        for name in sorted(FORBIDDEN_METHODS):
            with self.assertRaises(H0Error):
                Kernel.register_method(name)

    def test_only_registered_methods_register(self):
        for name in sorted(REGISTERED_METHODS):
            Kernel.register_method(name)

    def test_forbidden_method_in_request_denied(self):
        k = fresh_kernel()
        for name in sorted(FORBIDDEN_METHODS):
            res = k.handle(envelope(method=name, scope="h0.read"))
            self.assertFalse(res["ok"], name)
            self.assertEqual(res["error"], "E_FORBIDDEN_METHOD", name)

    def test_approval_method_cannot_approve(self):
        k = fresh_kernel()
        req = envelope(method="agi_approval_request", payload={"operation": "tag_release"})
        res = k.handle(req)
        self.assertTrue(res["ok"])
        self.assertFalse(res["result"]["can_approve"])
        self.assertEqual(res["result"]["status"], "pending")
        self.assertIn("not a grant", res["result"]["note"])


class AuthenticationTests(unittest.TestCase):
    def test_unknown_client(self):
        k = fresh_kernel()
        res = k.handle(envelope(client_id="intruder"))
        self.assertEqual(res["error"], "E_UNKNOWN_CLIENT")

    def test_revoked_credential(self):
        k = fresh_kernel(clients={"station-b": {"key_id": KEY_ID, "revoked": True}})
        res = k.handle(envelope(client_id="station-b"))
        self.assertEqual(res["error"], "E_CRED_REVOKED")

    def test_expired_credential(self):
        k = fresh_kernel(clients={"station-c": {"key_id": KEY_ID, "revoked": False,
                                                "credential_expires_at": (NOW - timedelta(minutes=1)).isoformat()}})
        res = k.handle(envelope(client_id="station-c"))
        self.assertEqual(res["error"], "E_CRED_EXPIRED")

    def test_wrong_key_id(self):
        req = envelope()
        req["signature"]["key_id"] = "someone-else"
        res = fresh_kernel().handle(req)
        self.assertEqual(res["error"], "E_UNKNOWN_KEY")

    def test_tampered_payload(self):
        req = envelope()
        req["payload"] = {"query": {"tampered": True}}
        res = fresh_kernel().handle(req)
        self.assertEqual(res["error"], "E_SIG_INVALID")

    def test_missing_signature(self):
        req = envelope()
        req["signature"] = {}
        res = fresh_kernel().handle(req)
        self.assertEqual(res["error"], "E_SIG_INVALID")


class ReplayTests(unittest.TestCase):
    def test_request_id_replay_denied_and_effect_not_repeated(self):
        k = fresh_kernel()
        req = envelope()
        self.assertTrue(k.handle(req)["ok"])
        second = k.handle(req)
        self.assertEqual(second["error"], "E_REPLAY")
        self.assertEqual(k.effects["executed"], 1)

    def test_nonce_replay_denied(self):
        k = fresh_kernel()
        req = envelope()
        self.assertTrue(k.handle(req)["ok"])
        other = envelope()
        other["nonce"] = req["nonce"]
        body = {x: v for x, v in other.items() if x != "signature"}
        other["signature"] = sign(canonical(body))
        self.assertEqual(k.handle(other)["error"], "E_REPLAY")
        self.assertEqual(k.effects["executed"], 1)


class SchemaTests(unittest.TestCase):
    def test_unknown_field_denied(self):
        k = fresh_kernel()
        res = k.handle(envelope(extra_field="boom"))
        self.assertEqual(res["error"], "E_UNKNOWN_FIELD")

    def test_wrong_schema_version(self):
        res = fresh_kernel().handle(envelope(schema="h0.mcp/2"))
        self.assertEqual(res["error"], "E_SCHEMA_VERSION")

    def test_unknown_method(self):
        res = fresh_kernel().handle(envelope(method="agi_teleport"))
        self.assertEqual(res["error"], "E_UNKNOWN_METHOD")

    def test_bad_correlation_id(self):
        res = fresh_kernel().handle(envelope(correlation_id="not-a-uuid"))
        self.assertEqual(res["error"], "E_MALFORMED")

    def test_expired_request(self):
        """v2 validates issued_at < expires_at, so an expired request must move BOTH."""
        body_req = envelope(issued_at=(NOW - timedelta(minutes=10)).isoformat(),
                            expires_at=(NOW - timedelta(minutes=5)).isoformat())
        res = fresh_kernel().handle(body_req)
        self.assertEqual(res["error"], "E_EXPIRED")


class LimitTests(unittest.TestCase):
    def test_payload_too_large(self):
        big = {"blob": "x" * (LIMITS["payload_bytes"] + 100)}
        with self.assertRaises(H0Error) as ctx:
            enforce_limits({"payload": big, "schema": "h0.mcp/1"})
        self.assertEqual(ctx.exception.code, "E_PAYLOAD_TOO_LARGE")

    def test_payload_too_deep(self):
        node = {}
        cur = node
        for _ in range(LIMITS["depth"] + 3):
            nxt = {}
            cur["child"] = nxt
            cur = nxt
        with self.assertRaises(H0Error) as ctx:
            enforce_limits({"payload": node})
        self.assertEqual(ctx.exception.code, "E_PAYLOAD_TOO_DEEP")

    def test_payload_too_wide(self):
        wide = {f"k{i}": i for i in range(LIMITS["keys"] + 10)}
        with self.assertRaises(H0Error) as ctx:
            enforce_limits({"payload": wide})
        self.assertEqual(ctx.exception.code, "E_PAYLOAD_TOO_WIDE")

    def test_value_too_long(self):
        with self.assertRaises(H0Error) as ctx:
            enforce_limits({"payload": {"s": "y" * (LIMITS["string_len"] + 1)}})
        self.assertEqual(ctx.exception.code, "E_VALUE_TOO_LONG")

    def test_array_too_long(self):
        with self.assertRaises(H0Error) as ctx:
            enforce_limits({"payload": {"a": list(range(LIMITS["array_len"] + 1))}})
        self.assertEqual(ctx.exception.code, "E_ARRAY_TOO_LONG")


class RateTests(unittest.TestCase):
    def test_read_rate_limit_denied_without_execution(self):
        """All limits are sliding windows over real elapsed time. Test each binding
        in isolation with a clock we control, so 'at most N per window T' is exact."""
        # 1. minute cap: 130 requests inside ~13s of elapsed time -> exactly 120 allowed
        fake_now = [0.0]
        rl = RateLimiter(clock=lambda: fake_now[0])
        allowed = denied = 0
        # burst window is 5s; at 10 requests/second only 50 can ever sit inside it,
        # so the outcome is a steady 50-per-5s ceiling (~10/s), never a latch.
        for _ in range(130):
            try:
                rl.admit("station-a", "agi_status", "h0.read")
                allowed += 1
            except H0Error as exc:
                self.assertIn(exc.code, {"E_RATE_BURST", "E_RATE_LIMIT"})
                denied += 1
            fake_now[0] += 0.1
        self.assertEqual(allowed + denied, 130)
        self.assertGreater(denied, 0, "some requests must be refused")
        # ceiling check: allowed never exceeds burst_count + (span/5s)*burst_count
        self.assertLessEqual(allowed, 20 + int(13 / 5 + 1) * 20)

        # 2. minute cap in isolation: one request per second, burst never trips.
        # A rolling 60s window holds at most 60 one-per-second samples, so the
        # minute cap only binds above 2/s; use 0.4s spacing (2.5/s) over 130 requests.
        fake_now = [0.0]
        rl2 = RateLimiter(clock=lambda: fake_now[0])
        allowed2 = 0
        for _ in range(130):
            fake_now[0] += 0.4
            try:
                rl2.admit("station-a", "agi_status", "h0.read")
                allowed2 += 1
            except H0Error as exc:
                self.assertIn(exc.code, {"E_RATE_LIMIT", "E_RATE_BURST"})
        self.assertGreater(allowed2, 0)
        self.assertLess(allowed2, 130, "the minute window must refuse some")
        # hard ceiling: 120 per 60s + burst allowance for 5s spans
        self.assertLessEqual(allowed2, 120 + 20)

    def test_burst_limit(self):
        fake_now = [0.0]
        rl = RateLimiter(clock=lambda: fake_now[0])
        ok = 0
        for _ in range(25):
            try:
                rl.admit("c", "agi_status", "h0.read")
                ok += 1
            except H0Error as exc:
                self.assertEqual(exc.code, "E_RATE_BURST")
        self.assertEqual(ok, 20)



class ScopeTests(unittest.TestCase):
    def test_wrong_scope_denied(self):
        res = fresh_kernel().handle(envelope(method="agi_status", scope="h0.write.metadata"))
        self.assertEqual(res["error"], "E_SCOPE")

    def test_read_scope_cannot_write(self):
        res = fresh_kernel().handle(envelope(method="agi_checkpoint_create", scope="h0.read"))
        self.assertEqual(res["error"], "E_SCOPE")

    def test_correct_scope_allowed(self):
        res = fresh_kernel().handle(envelope(method="agi_checkpoint_create",
                                             payload={"checkpoint": "cp-1"}))
        self.assertTrue(res["ok"])


class FailClosedTests(unittest.TestCase):
    def test_policy_unavailable_denies(self):
        k = fresh_kernel(policy_ok=lambda: False)
        res = k.handle(envelope())
        self.assertEqual(res["error"], "E_POLICY_UNAVAILABLE")
        self.assertEqual(k.effects["executed"], 0)

    def test_audit_failure_prevents_execution(self):
        """v2 semantics: audit is a precondition. Nothing executes, so there is no
        'downgrade' to record - the claim 'downgraded' was only true of the v1 bug."""
        k = fresh_kernel(audit=AuditLog(fail=True))
        res = k.handle(envelope())
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "E_AUDIT_UNAVAILABLE")
        self.assertEqual(k.effects["executed"], 0)
        self.assertEqual(res["audit"]["decision"], "deny")

    def test_internal_error_denies(self):
        """v2: the executor is injected, and an executor crash must deny."""
        def boom(_req):
            raise RuntimeError("unexpected")
        k = fresh_kernel(executor=boom)
        res = k.handle(envelope())
        self.assertEqual(res["error"], "E_EXECUTOR_FAILED")
        self.assertEqual(k.effects["executed"], 0)


class AuditTests(unittest.TestCase):
    def test_audit_records_both_decisions_and_no_payload(self):
        k = fresh_kernel()
        k.handle(envelope(payload={"secretish": "do-not-log-me"}))
        k.handle(envelope(method="exec"))
        self.assertEqual(len(k.audit.records), 2)
        blob = json.dumps(k.audit.records)
        self.assertNotIn("do-not-log-me", blob)
        for rec in k.audit.records:
            self.assertIn("correlation_id", rec)
            self.assertIn("request_digest", rec)
            self.assertIn(rec["decision"], {"allow", "deny"})


if __name__ == "__main__":
    unittest.main()
