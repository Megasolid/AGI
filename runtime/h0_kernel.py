#!/usr/bin/env python3
"""H0 — reference enforcement kernel for the MCP security contract.

This is a SPECIFICATION VERIFIER, not a server. It exposes no socket, opens no
tunnel, and holds no credential. It exists so the negative tests can prove that
prohibited operations are impossible rather than merely documented as such.

Contract: citadel/h0/H0-MCP-SECURITY-CONTRACT.md
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone

SCHEMA = "h0.mcp/1"
ENVELOPE_FIELDS = frozenset({
    "schema", "method", "scope", "client_id", "request_id", "correlation_id",
    "issued_at", "expires_at", "nonce", "payload", "signature",
})

READ_METHODS = frozenset({"HELLO", "agi_status", "agi_task_list", "agi_task_get", "agi_evidence_get"})
METADATA_WRITE_METHODS = frozenset({"agi_checkpoint_create", "agi_receipt_submit"})
REQUEST_ONLY_METHODS = frozenset({"agi_approval_request"})
REGISTERED_METHODS = READ_METHODS | METADATA_WRITE_METHODS | REQUEST_ONLY_METHODS

METHOD_SCOPES = {
    "HELLO": "h0.read",
    "agi_status": "h0.read",
    "agi_task_list": "h0.read",
    "agi_task_get": "h0.read",
    "agi_evidence_get": "h0.read",
    "agi_checkpoint_create": "h0.write.metadata",
    "agi_receipt_submit": "h0.write.metadata",
    "agi_approval_request": "h0.request",
}
SCOPES = frozenset(METHOD_SCOPES.values())

FORBIDDEN_METHODS = frozenset({
    "exec", "shell", "run", "read_file", "write_file", "fs_list",
    "git_push", "git_merge", "git_tag", "release", "publish", "sign",
    "approve", "grant", "revoke", "policy_set", "admin", "sql", "eval",
})

LIMITS = {
    "payload_bytes": 16384,
    "envelope_bytes": 32768,
    "depth": 8,
    "keys": 256,
    "string_len": 4096,
    "array_len": 128,
}
RATE = {
    "read_per_min": 120,
    "write_per_min": 30,
    "request_per_min": 10,
    "burst_count": 20,
    "burst_window_s": 5,
    "method_per_min": 600,
}

_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
_NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


class H0Error(ValueError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def _walk(value, depth=0):
    yield depth, value
    if isinstance(value, dict):
        for v in value.values():
            yield from _walk(v, depth + 1)
    elif isinstance(value, list):
        for v in value:
            yield from _walk(v, depth + 1)


def enforce_limits(request: dict) -> None:
    env_bytes = len(canonical(request))
    if env_bytes > LIMITS["envelope_bytes"]:
        raise H0Error("E_ENVELOPE_TOO_LARGE", f"{env_bytes} > {LIMITS['envelope_bytes']}")
    payload = request.get("payload") or {}
    pbytes = len(canonical(payload))
    if pbytes > LIMITS["payload_bytes"]:
        raise H0Error("E_PAYLOAD_TOO_LARGE", f"{pbytes} > {LIMITS['payload_bytes']}")
    keys = 0
    for depth, value in _walk(payload):
        if depth > LIMITS["depth"]:
            raise H0Error("E_PAYLOAD_TOO_DEEP", f"depth {depth} > {LIMITS['depth']}")
        if isinstance(value, dict):
            keys += len(value)
        elif isinstance(value, list):
            if len(value) > LIMITS["array_len"]:
                raise H0Error("E_ARRAY_TOO_LONG", f"{len(value)} > {LIMITS['array_len']}")
        elif isinstance(value, str):
            if len(value) > LIMITS["string_len"]:
                raise H0Error("E_VALUE_TOO_LONG", f"{len(value)} > {LIMITS['string_len']}")
    if keys > LIMITS["keys"]:
        raise H0Error("E_PAYLOAD_TOO_WIDE", f"{keys} > {LIMITS['keys']}")


class RateLimiter:
    def __init__(self, clock=None):
        self._clock = clock or time.monotonic
        self._windows = {}

    def _hits(self, key, window_s):
        now = self._clock()
        hits = [t for t in self._windows.get(key, []) if now - t < window_s]
        self._windows[key] = hits
        return hits

    def check(self, client_id: str, method: str, scope: str) -> None:
        scope_key = (client_id, scope)
        window = 60
        limit = (RATE["read_per_min"] if scope == "h0.read"
                 else RATE["request_per_min"] if scope == "h0.request"
                 else RATE["write_per_min"])
        if len(self._hits(scope_key, window)) >= limit:
            raise H0Error("E_RATE_LIMIT", f"{scope} {limit}/{window}s")
        if len(self._hits(("method", method), window)) >= RATE["method_per_min"]:
            raise H0Error("E_RATE_LIMIT", f"method {method} {RATE['method_per_min']}/60s")
        if len(self._hits(("burst", client_id), RATE["burst_window_s"])) >= RATE["burst_count"]:
            raise H0Error("E_RATE_BURST", f"{RATE['burst_count']} in {RATE['burst_window_s']}s")

    def record(self, client_id: str, method: str, scope: str) -> None:
        now = self._clock()
        for key in ((client_id, scope), ("method", method), ("burst", client_id)):
            self._windows.setdefault(key, []).append(now)


class AuditLog:
    def __init__(self, fail: bool = False):
        self.records = []
        self.fail = fail

    def append(self, record: dict) -> None:
        if self.fail:
            raise H0Error("E_AUDIT_UNAVAILABLE", "audit store unavailable")
        self.records.append(record)


def validate_envelope_shape(request) -> None:
    if not isinstance(request, dict):
        raise H0Error("E_MALFORMED", "envelope is not an object")
    extra = set(request) - ENVELOPE_FIELDS
    if extra:
        raise H0Error("E_UNKNOWN_FIELD", ",".join(sorted(extra)))
    missing = ENVELOPE_FIELDS - set(request)
    if missing:
        raise H0Error("E_MALFORMED", "missing " + ",".join(sorted(missing)))
    if request["schema"] != SCHEMA:
        raise H0Error("E_SCHEMA_VERSION", str(request["schema"]))
    if request["method"] not in REGISTERED_METHODS:
        raise H0Error("E_FORBIDDEN_METHOD" if request["method"] in FORBIDDEN_METHODS
                      else "E_UNKNOWN_METHOD", str(request["method"]))
    if request["scope"] not in SCOPES:
        raise H0Error("E_SCOPE", str(request["scope"]))
    if not _ID_RE.match(str(request["client_id"])):
        raise H0Error("E_MALFORMED", "client_id")
    if not _ID_RE.match(str(request["request_id"])):
        raise H0Error("E_MALFORMED", "request_id")
    if not _UUID4_RE.match(str(request["correlation_id"])):
        raise H0Error("E_MALFORMED", "correlation_id")
    if not _NONCE_RE.match(str(request["nonce"])):
        raise H0Error("E_MALFORMED", "nonce")
    if not isinstance(request["payload"], dict):
        raise H0Error("E_MALFORMED", "payload not an object")
    if not isinstance(request["signature"], dict):
        raise H0Error("E_MALFORMED", "signature not an object")


def _parse_ts(value) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise H0Error("E_MALFORMED", "timestamp without timezone")
    return dt


class Kernel:
    """Enforcement order: auth -> replay -> schema -> limits -> rate -> scope -> policy -> audit -> execute."""

    def __init__(self, *, clients, verifier, policy_ok=lambda: True, clock=None, audit=None):
        self.clients = clients
        self.verifier = verifier
        self.policy_ok = policy_ok
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.rate = RateLimiter()
        self.audit = audit or AuditLog()
        self._seen_ids = set()
        self._seen_nonces = set()
        self.effects = {"executed": 0, "denied": 0}

    # -- helpers ---------------------------------------------------------
    def _authenticate(self, request, now):
        client = self.clients.get(request["client_id"])
        if client is None:
            raise H0Error("E_UNKNOWN_CLIENT", request["client_id"])
        if client.get("revoked"):
            raise H0Error("E_CRED_REVOKED", request["client_id"])
        exp = client.get("credential_expires_at")
        if exp and _parse_ts(exp) <= now:
            raise H0Error("E_CRED_EXPIRED", request["client_id"])
        if request["method"] != "HELLO":
            sig = request["signature"]
            if not isinstance(sig, dict) or "key_id" not in sig or "signature_b64" not in sig:
                raise H0Error("E_SIG_INVALID", "signature envelope incomplete")
            if sig["key_id"] != client.get("key_id"):
                raise H0Error("E_UNKNOWN_KEY", str(sig.get("key_id")))
            payload = {k: v for k, v in request.items() if k != "signature"}
            if not self.verifier(canonical(payload), sig):
                raise H0Error("E_SIG_INVALID", "verification failed")

    def _replay(self, request):
        if request["request_id"] in self._seen_ids:
            raise H0Error("E_REPLAY", "request_id")
        if request["nonce"] in self._seen_nonces:
            raise H0Error("E_REPLAY", "nonce")

    def _mark_seen(self, request):
        self._seen_ids.add(request["request_id"])
        self._seen_nonces.add(request["nonce"])

    # -- execution -------------------------------------------------------
    def handle(self, request) -> dict:
        now = self.clock()
        code = None
        outcome = "denied"
        try:
            self._authenticate(request, now)
            self._replay(request)
            validate_envelope_shape(request)
            if _parse_ts(request["expires_at"]) <= now:
                raise H0Error("E_EXPIRED", "request expired")
            enforce_limits(request)
            if request["scope"] != METHOD_SCOPES[request["method"]]:
                raise H0Error("E_SCOPE", f"{request['scope']} cannot call {request['method']}")
            self.rate.check(request["client_id"], request["method"], request["scope"])
            if not self.policy_ok():
                raise H0Error("E_POLICY_UNAVAILABLE", "policy engine unavailable")
            result = self._execute(request)
            outcome = "executed"
            self.effects["executed"] += 1
            decision = "allow"
        except H0Error as exc:
            code = exc.code
            result = None
            decision = "deny"
            self.effects["denied"] += 1
        except Exception as exc:  # noqa: BLE001 - any failure must deny
            code = "E_INTERNAL"
            result = None
            decision = "deny"
            self.effects["denied"] += 1
            self._internal = f"{type(exc).__name__}: {exc}"

        # audit before returning; an audit failure converts an allow into a deny
        record = {
            "correlation_id": request.get("correlation_id"),
            "client_id": request.get("client_id"),
            "method": request.get("method"),
            "scope": request.get("scope"),
            "request_digest": digest({k: v for k, v in request.items() if k != "signature"}),
            "decision": decision,
            "reason_code": code,
            "outcome": outcome,
            "timestamp": now.astimezone(timezone.utc).isoformat(),
        }
        if decision == "allow":
            try:
                self.audit.append(record)
            except H0Error as exc:
                # downgrade: nothing privileged may happen without an audit trail
                self.effects["executed"] -= 1
                self.effects["denied"] += 1
                record["decision"] = "deny"
                record["outcome"] = "denied"
                record["reason_code"] = exc.code
                record["note"] = "allow downgraded: audit unavailable"
                return {"ok": False, "error": exc.code, "audit": record}
            self._mark_seen(request)
            self.rate.record(request["client_id"], request["method"], request["scope"])
            return {"ok": True, "result": result, "audit": record}

        try:
            self.audit.append(record)
        except H0Error:
            record["note"] = "audit unavailable for denied request"
        return {"ok": False, "error": code, "audit": record}

    def _execute(self, request):
        method = request["method"]
        payload = request["payload"]
        if method in READ_METHODS:
            return {"method": method, "data": payload.get("query", {}), "digests_only": True}
        if method in METADATA_WRITE_METHODS:
            return {"method": method, "recorded_digest": digest(payload)}
        if method in REQUEST_ONLY_METHODS:
            # creates a pending request; never approves
            return {"approval_request_id": "req-" + hashlib.sha256(canonical(payload)).hexdigest()[:16],
                    "status": "pending", "can_approve": False,
                    "note": "a request is not a grant and cannot authorize anything"}
        raise H0Error("E_UNKNOWN_METHOD", method)

    # -- construction guard ---------------------------------------------
    @staticmethod
    def register_method(name: str) -> None:
        if name in FORBIDDEN_METHODS:
            raise H0Error("E_FORBIDDEN_METHOD", name)
        if name not in REGISTERED_METHODS:
            raise H0Error("E_UNKNOWN_METHOD", name)
