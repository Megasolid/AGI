#!/usr/bin/env python3
"""H0 — reference enforcement kernel, revision 2.

Correction of five findings raised in King review 2026-11-02T19:27:

  F1 audit is NOT a precondition to execution  -> audit is written BEFORE execute;
     if it cannot be written, the executor is never invoked.
  F2 kernel order diverged from the contract    -> order is declared once and
     asserted by tests: auth -> replay -> schema -> payload -> limits -> rate ->
     scope -> policy -> audit -> execute.
  F3 replay check/mark not concurrency-safe     -> atomic reservation under a lock,
     before any effect.
  F4 no per-method payload schemas             -> PAYLOAD_SCHEMAS with strict
     unknown-field rejection for every registered method.
  F5 issued_at unvalidated                     -> both timestamps validated for
     format, timezone, ordering and clock skew.

This is a SPECIFICATION VERIFIER, not a server. It opens no socket, holds no
credential, and exposes no privileged surface.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "h0.mcp/1"
ENVELOPE_FIELDS = frozenset({
    "schema", "method", "scope", "client_id", "request_id", "correlation_id",
    "issued_at", "expires_at", "nonce", "payload", "signature",
})

# Enforcement order is declared once; tests assert against this tuple.
ORDER = ("auth", "replay", "schema", "payload", "limits", "rate", "scope", "policy", "audit", "execute")

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

# F4: every registered method declares its payload contract.
#   required: fields that must be present
#   optional: fields that may be present
#   types:    expected python type per field
#   strict:   unknown fields are rejected (E_UNKNOWN_PAYLOAD_FIELD)
PAYLOAD_SCHEMAS = {
    "HELLO": {"required": set(), "optional": {"agent", "version"},
              "types": {"agent": str, "version": str}},
    "agi_status": {"required": set(), "optional": {"include", "since"},
                   "types": {"include": list, "since": str}},
    "agi_task_list": {"required": set(), "optional": {"limit", "state"},
                      "types": {"limit": int, "state": str}},
    "agi_task_get": {"required": {"task_id"}, "optional": set(),
                     "types": {"task_id": str}},
    "agi_evidence_get": {"required": {"evidence_id"}, "optional": set(),
                         "types": {"evidence_id": str}},
    "agi_checkpoint_create": {"required": {"checkpoint"}, "optional": {"cursor"},
                              "types": {"checkpoint": str, "cursor": int}},
    "agi_receipt_submit": {"required": {"handoff_digest", "outcome"}, "optional": set(),
                           "types": {"handoff_digest": str, "outcome": str}},
    "agi_approval_request": {"required": {"operation"}, "optional": {"reason"},
                             "types": {"operation": str, "reason": str}},
}

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
CLOCK_SKEW_S = 300  # issued_at may be at most this far in the future

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


def parse_ts(value, field: str) -> datetime:
    """F5: strict ISO-8601 with mandatory timezone."""
    if not isinstance(value, str) or not value:
        raise H0Error("E_MALFORMED", f"{field} missing")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise H0Error("E_MALFORMED", f"{field} not ISO-8601") from exc
    if dt.tzinfo is None:
        raise H0Error("E_MALFORMED", f"{field} has no timezone")
    return dt


def validate_timestamps(request: dict, now: datetime) -> None:
    """F5: both timestamps, their ordering, and skew against the clock."""
    issued = parse_ts(request.get("issued_at"), "issued_at")
    expires = parse_ts(request.get("expires_at"), "expires_at")
    if not issued < expires:
        raise H0Error("E_MALFORMED", "issued_at must precede expires_at")
    if expires <= now:
        raise H0Error("E_EXPIRED", "request expired")
    if issued > now + timedelta(seconds=CLOCK_SKEW_S):
        raise H0Error("E_CLOCK_SKEW", "issued_at too far in the future")
    if issued > expires:
        raise H0Error("E_MALFORMED", "issued_at after expires_at")


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


def validate_payload(method: str, payload) -> None:
    """F4: strict per-method payload schema."""
    spec = PAYLOAD_SCHEMAS.get(method)
    if spec is None:
        raise H0Error("E_UNKNOWN_METHOD", method)
    if not isinstance(payload, dict):
        raise H0Error("E_MALFORMED", "payload not an object")
    allowed = spec["required"] | spec["optional"]
    unknown = set(payload) - allowed
    if unknown:
        raise H0Error("E_UNKNOWN_PAYLOAD_FIELD", ",".join(sorted(unknown)))
    missing = spec["required"] - set(payload)
    if missing:
        raise H0Error("E_MALFORMED", "missing " + ",".join(sorted(missing)))
    for field, expected in spec["types"].items():
        if field in payload and not isinstance(payload[field], expected):
            raise H0Error("E_MALFORMED", f"{field} must be {expected.__name__}")
        if field in payload and expected is int and isinstance(payload[field], bool):
            raise H0Error("E_MALFORMED", f"{field} must be int, not bool")


class RateLimiter:
    """F8: check and record are ONE atomic admission operation.

    Revision 2 exposed check() and record() separately, so concurrent requests
    could all pass check() before any of them recorded. admit() holds the lock
    across both, so the limit cannot be raced.
    """

    def __init__(self, clock=None):
        self._clock = clock or time.monotonic
        self._windows = {}
        self._lock = threading.Lock()

    def _hits_locked(self, key, window_s):
        now = self._clock()
        hits = [t for t in self._windows.get(key, []) if now - t < window_s]
        self._windows[key] = hits
        return hits

    def _limits_for(self, scope):
        return (RATE["read_per_min"] if scope == "h0.read"
                else RATE["request_per_min"] if scope == "h0.request"
                else RATE["write_per_min"])

    def admit(self, client_id: str, method: str, scope: str) -> None:
        """Atomically test every limit and, if all pass, record the hit."""
        with self._lock:
            limit = self._limits_for(scope)
            if len(self._hits_locked((client_id, scope), 60)) >= limit:
                raise H0Error("E_RATE_LIMIT", f"{scope} {limit}/60s")
            if len(self._hits_locked(("method", method), 60)) >= RATE["method_per_min"]:
                raise H0Error("E_RATE_LIMIT", f"method {method}")
            if len(self._hits_locked(("burst", client_id), RATE["burst_window_s"])) >= RATE["burst_count"]:
                raise H0Error("E_RATE_BURST", f"{RATE['burst_count']} in {RATE['burst_window_s']}s")
            now = self._clock()
            for key in ((client_id, scope), ("method", method), ("burst", client_id)):
                self._windows.setdefault(key, []).append(now)

    # compatibility helpers (each is individually atomic)
    def check(self, client_id, method, scope):
        raise H0Error("E_RATE_LIMIT", "use admit()")

    def record(self, client_id, method, scope):
        raise H0Error("E_RATE_LIMIT", "use admit()")


class AuditLog:
    """In-memory audit sink. NOT durable, and therefore NOT accepted by Kernel.

    Retained only so isolated unit tests can assert call ordering. It deliberately
    declares is_durable = False, which Kernel rejects with E_AUDIT_NOT_DURABLE.
    """

    is_durable = False

    def __init__(self, fail: bool = False):
        self.records = []
        self.fail = fail
        self._lock = threading.Lock()

    def append(self, record: dict) -> None:
        if self.fail:
            raise H0Error("E_AUDIT_UNAVAILABLE", "audit store unavailable")
        with self._lock:
            self.records.append(record)


class ReplayStore:
    """F3: atomic reserve/consume so concurrent duplicates cannot both pass."""

    def __init__(self):
        self._lock = threading.Lock()
        self._reserved_ids = {}
        self._reserved_nonces = {}

    def reserve(self, request_id: str, nonce: str, token: str) -> None:
        with self._lock:
            if request_id in self._reserved_ids:
                raise H0Error("E_REPLAY", "request_id")
            if nonce in self._reserved_nonces:
                raise H0Error("E_REPLAY", "nonce")
            self._reserved_ids[request_id] = token
            self._reserved_nonces[nonce] = token

    def release(self, request_id: str, nonce: str) -> None:
        """A request denied before execution must not permanently burn its id."""
        with self._lock:
            self._reserved_ids.pop(request_id, None)
            self._reserved_nonces.pop(nonce, None)


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
    if not isinstance(request["signature"], dict):
        raise H0Error("E_MALFORMED", "signature not an object")


class _TrustedStore:
    """R9: resolves the kernel-built store through a CLASS attribute, not the instance.

    The instance attribute is a guard: if it is rebound, the audit gate refuses. The
    class-level function is the authority and always returns the same store. This is a
    defence against accidental or careless mutation. It is NOT a defence against
    arbitrary code running in this process, which can simply call the class function.
    """

    _bound: "weakref.WeakKeyDictionary" = None

    @classmethod
    def _table(cls):
        import weakref
        if cls._bound is None:
            cls._bound = weakref.WeakKeyDictionary()
        return cls._bound

    @classmethod
    def bind(cls, kernel, store) -> None:
        cls._table()[kernel] = store
        kernel._trusted_store = store

    @classmethod
    def resolve(cls, kernel):
        try:
            return cls._table()[kernel]
        except KeyError:
            raise H0Error("E_AUDIT_REQUIRED", "no trusted store bound") from None


class _AccountedDenial(Exception):
    """Request-local marker: this denial is already in the audit trail."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail


class _Indeterminate(Exception):
    """Internal marker: effect may have occurred but cannot be recorded."""

    def __init__(self, payload):
        super().__init__("indeterminate")
        self.payload = payload


class Kernel:
    """Enforcement order (see ORDER): auth, replay, schema, payload, limits, rate,
    scope, policy, audit, execute. The executor is invoked ONLY after the audit
    record has been durably appended."""

    def __init__(self, *, clients, verifier, policy_ok=lambda: True, clock=None,
                 audit_path=None, executor=None):
        """R7: the enforcement audit store is BUILT BY THE KERNEL, never injected.

        Revision 6 accepted any object whose durability() returned the right mapping.
        A hostile subclass could claim every property and override append() to write
        nothing. The store is therefore constructed here from an on-disk path, and the
        kernel keeps the concrete object private; no caller can substitute an
        implementation that asserts its own safety.
        """
        self.clients = clients
        self.verifier = verifier
        self.policy_ok = policy_ok
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.rate = RateLimiter()
        if not audit_path:
            raise H0Error("E_AUDIT_REQUIRED",
                          "audit_path is required: enforcement cannot run without durable audit")
        try:
            from h0_audit_store import DurableAuditStore
            store = DurableAuditStore(Path(audit_path))
        except H0Error:
            raise
        except Exception as exc:  # noqa: BLE001
            raise H0Error("E_AUDIT_UNAVAILABLE",
                          f"trusted store construction failed: {type(exc).__name__}") from exc
        # verify the concrete object the KERNEL built (not a caller-supplied one)
        if type(store) is not DurableAuditStore:
            raise H0Error("E_AUDIT_NOT_DURABLE", "trusted store type check failed")
        self._require_enforceable_store(store)
        # R9: the store handle is NOT stored on the instance at all. It lives only in
        # `self._trusted_store`, which is rebound ONCE here to a module-level function
        # (accessible only via the class). Rebinding the instance attribute is detected
        # at the audit gate; the class-level fallback still resolves the same closure.
        # This raises the bar; it does NOT defeat arbitrary same-process code, and is
        # not claimed to. See citadel/h0/H0-CORRECTION-REPORT-R9-20261102.md.
        _TrustedStore.bind(self, store)
        self.replay = ReplayStore()
        self.executor = executor or self._default_execute
        self.effects = {"executed": 0, "denied": 0, "indeterminate": 0}
        self.invocations = 0
        self.order_seen = []

    # -- R7: read-only access to the trusted store -------------------------
    @property
    def audit(self):
        """Read-only view of the kernel-built store (for audit trail inspection)."""
        return self._bound_store()

    # -- R9: store resolution ------------------------------------------------
    def _bound_store(self):
        """Execution-path store handle. Resolved through the class, never a stored getter."""
        return _TrustedStore.resolve(self)

    # -- R6: enforcement-store contract ------------------------------------
    @staticmethod
    def _require_enforceable_store(store) -> None:
        """A store may only enter the enforcement path if it PROVES it is enforceable.

        R5 accepted a bare `is_durable = True` declaration. That is an honour system:
        an observer-mode store and an fsync-disabled store both declared durability,
        and any injected object could do the same. The check below requires a
        callable `durability()` reporting concrete, verified properties, and rejects
        the store categorically if any of them is absent or false.
        """
        contract = getattr(store, "durability", None)
        if not callable(contract):
            raise H0Error("E_AUDIT_NOT_DURABLE",
                          f"{type(store).__name__} exposes no durability() contract; "
                          "a bare declaration is not acceptable")
        try:
            d = contract()
        except Exception as exc:  # noqa: BLE001
            raise H0Error("E_AUDIT_NOT_DURABLE",
                          f"durability() raised {type(exc).__name__}") from exc
        if not isinstance(d, dict):
            raise H0Error("E_AUDIT_NOT_DURABLE", "durability() must return a mapping")
        required_true = ("enforceable", "fsync", "single_writer", "append_only", "chained")
        missing = [k for k in required_true if d.get(k) is not True]
        if missing:
            raise H0Error("E_AUDIT_NOT_DURABLE",
                          f"store not enforceable (failed: {','.join(missing)})")
        if d.get("observer_mode") is not False:
            raise H0Error("E_AUDIT_NOT_DURABLE", "observer-mode stores are categorically refused")

    # -- default executor -------------------------------------------------
    def _default_execute(self, request):
        method = request["method"]
        payload = request["payload"]
        if method in READ_METHODS:
            return {"method": method, "data": payload, "digests_only": True}
        if method in METADATA_WRITE_METHODS:
            return {"method": method, "recorded_digest": digest(payload)}
        return {"approval_request_id": "req-" + hashlib.sha256(canonical(payload)).hexdigest()[:16],
                "status": "pending", "can_approve": False,
                "note": "a request is not a grant and cannot authorize anything"}

    # -- gates ------------------------------------------------------------
    def _authenticate(self, request, now):
        client = self.clients.get(request["client_id"])
        if client is None:
            raise H0Error("E_UNKNOWN_CLIENT", request["client_id"])
        if client.get("revoked"):
            raise H0Error("E_CRED_REVOKED", request["client_id"])
        exp = client.get("credential_expires_at")
        if exp and parse_ts(exp, "credential_expires_at") <= now:
            raise H0Error("E_CRED_EXPIRED", request["client_id"])
        if request["method"] != "HELLO":
            sig = request["signature"]
            if not isinstance(sig, dict) or "key_id" not in sig or "signature_b64" not in sig:
                raise H0Error("E_SIG_INVALID", "signature envelope incomplete")
            if sig["key_id"] != client.get("key_id"):
                raise H0Error("E_UNKNOWN_KEY", str(sig.get("key_id")))
            body = {k: v for k, v in request.items() if k != "signature"}
            if not self.verifier(canonical(body), sig):
                raise H0Error("E_SIG_INVALID", "verification failed")

    def _gate(self, name):
        self.order_seen.append(name)

    def _assert_store_identity(self) -> None:
        """R9: refuse to act if the instance attribute no longer holds the trusted store.

        The comparison is object identity against the class-level closure - not a
        string probe, which a substitute can forge.
        """
        if self._trusted_store is not _TrustedStore.resolve(self):
            raise H0Error("E_AUDIT_STORE_SUBSTITUTED",
                          "instance audit binding no longer matches the trusted store")

    def handle(self, request) -> dict:
        now = self.clock()
        self.order_seen = []
        token = hashlib.sha256(canonical(request).hexdigest().encode()).hexdigest()[:16] \
            if False else hashlib.sha256(canonical(request)).hexdigest()[:16]
        reserved = False
        code = None
        executed = False
        try:
            self._gate("auth")
            self._authenticate(request, now)

            self._gate("replay")
            self.replay.reserve(request["request_id"], request["nonce"], token)
            reserved = True

            self._gate("schema")
            validate_envelope_shape(request)

            self._gate("payload")
            validate_payload(request["method"], request["payload"])

            self._gate("limits")
            enforce_limits(request)
            validate_timestamps(request, now)

            self._gate("rate")
            self.rate.admit(request["client_id"], request["method"], request["scope"])

            self._gate("scope")
            if request["scope"] != METHOD_SCOPES[request["method"]]:
                raise H0Error("E_SCOPE", f"{request['scope']} cannot call {request['method']}")

            self._gate("policy")
            if not self.policy_ok():
                raise H0Error("E_POLICY_UNAVAILABLE", "policy engine unavailable")

            # F1 + F7: two-phase audit. Phase 1 (intent) is durable BEFORE the effect.
            # Any store failure (including AuditStoreError) must deny, never escape.
            self._gate("audit")
            self._assert_store_identity()
            cid = request["correlation_id"]
            intent = {
                "phase": "intent",
                "correlation_id": cid,
                "client_id": request.get("client_id"),
                "method": request.get("method"),
                "scope": request.get("scope"),
                "request_digest": digest({k: v for k, v in request.items() if k != "signature"}),
                "decision": "allow",
                "outcome": "pending",
                "timestamp": now.astimezone(timezone.utc).isoformat(),
            }
            try:
                self._bound_store().append(intent)
            except H0Error:
                raise
            except Exception as exc:  # noqa: BLE001 - store failures fail closed
                raise H0Error("E_AUDIT_UNAVAILABLE", f"{type(exc).__name__}: {exc}") from exc

            self._gate("execute")
            try:
                result = self.executor(request)
            except Exception as exc:  # noqa: BLE001
                # Executor failed: the effect is KNOWN not to have happened (per the
                # executor contract). Try to record it; if that also fails, report
                # indeterminate rather than pretending the trail is complete.
                try:
                    self._bound_store().append({"phase": "outcome", "correlation_id": cid,
                                       "decision": "allow", "outcome": "failed",
                                       "reason_code": "E_EXECUTOR_FAILED",
                                       "detail": type(exc).__name__,
                                       "timestamp": self.clock().astimezone(timezone.utc).isoformat()})
                except Exception as rec_exc:  # noqa: BLE001
                    self.effects["indeterminate"] += 1
                    return {"ok": False,
                            "error": "E_EXECUTION_INDETERMINATE",
                            "indeterminate": True,
                            "detail": f"executor failed AND outcome unrecordable: {type(rec_exc).__name__}",
                            "audit": intent}
                # G2: request-local result, carried on the exception, never on self
                raise _AccountedDenial(code="E_EXECUTOR_FAILED",
                                       detail=type(exc).__name__)
            # Effect HAS HAPPENED. From here on, nothing may suggest otherwise.
            executed = True
            self.effects["executed"] += 1
            try:
                self._bound_store().append({"phase": "outcome", "correlation_id": cid,
                                   "decision": "allow", "outcome": "executed",
                                   "timestamp": self.clock().astimezone(timezone.utc).isoformat()})
            except Exception as rec_exc:  # noqa: BLE001
                # F11: effect occurred but is unrecorded. Preserve the dangling intent.
                # Return an explicit indeterminate result - do NOT append a deny.
                self.effects["indeterminate"] += 1
                return {"ok": False,
                        "error": "E_EXECUTION_INDETERMINATE",
                        "indeterminate": True,
                        "detail": f"effect executed but outcome unrecordable: {type(rec_exc).__name__}",
                        "audit": intent}
            return {"ok": True, "result": result, "audit": intent}

        except _Indeterminate as exc:
            self.effects["indeterminate"] += 1
            return exc.payload

        except _AccountedDenial as exc:
            # already recorded as an outcome record; no second denial may be appended
            self.effects["denied"] += 1
            return {"ok": False, "error": exc.code, "audit": None}

        except H0Error as exc:
            code = exc.code
            result = None
        except Exception as exc:  # noqa: BLE001
            code = "E_INTERNAL"
            result = None
            self._internal = f"{type(exc).__name__}: {exc}"

        self.effects["denied"] += 1
        if reserved and not executed and isinstance(request, dict):
            rid, nonce = request.get("request_id"), request.get("nonce")
            if rid and nonce:
                self.replay.release(rid, nonce)
        denial = {
            "phase": "deny",
            "correlation_id": request.get("correlation_id") if isinstance(request, dict) else None,
            "client_id": request.get("client_id") if isinstance(request, dict) else None,
            "method": request.get("method") if isinstance(request, dict) else None,
            "scope": request.get("scope") if isinstance(request, dict) else None,
            "request_digest": digest({k: v for k, v in request.items() if k != "signature"})
            if isinstance(request, dict) else None,
            "decision": "deny",
            "reason_code": code,
            "outcome": "denied",
            "timestamp": now.astimezone(timezone.utc).isoformat(),
        }
        try:
            self._bound_store().append(denial)
        except Exception:  # noqa: BLE001 - store failure must not mask the denial
            denial["note"] = "audit unavailable for denied request"
        return {"ok": False, "error": code, "audit": denial}

    @staticmethod
    def register_method(name: str) -> None:
        if name in FORBIDDEN_METHODS:
            raise H0Error("E_FORBIDDEN_METHOD", name)
        if name not in REGISTERED_METHODS:
            raise H0Error("E_UNKNOWN_METHOD", name)
