#!/usr/bin/env python3
"""E1 integration adapters: S3 boundary decision + S5 memory gateway.

These are *interfaces*, not implementations of S3 or S5. The caller injects a
real boundary decision function and a real gateway; this module validates the
S3 decision, re-checks revocation freshness, verifies the returned bytes against
the pinned context digest, and fails closed on anything missing/unavailable.

No network, credentials, identity or authority. It never fabricates an allow.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from agi_context import ContextError, resolve_context_ref, validate_context_manifest

S3_DECISION_REQUIRED = (
    "decision_id", "operation", "actor", "subject", "grant_id",
    "result", "reason_code", "ts", "revocation_checked",
)


class AdapterError(ValueError):
    """Integration input/decision is invalid; caller must fail closed."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AdapterError(msg)


def require_boundary_allow(decision: dict, *, operation: str) -> dict:
    """Validate a real S3 boundary decision. Only an explicit allow proceeds."""
    _require(isinstance(decision, dict), "S3 decision must be an object")
    for key in S3_DECISION_REQUIRED:
        _require(key in decision, f"S3 decision missing {key}")
    _require(isinstance(decision["decision_id"], str) and decision["decision_id"], "decision_id required")
    _require(decision.get("result") == "allow", "S3 decision is not allow")
    _require(decision.get("operation") == operation, "S3 decision operation mismatch")
    _require(isinstance(decision.get("grant_id"), str) and decision["grant_id"], "grant_id required")
    _require(decision.get("reason_code") == "ok", "S3 allow must have reason_code ok")
    _require(decision.get("revocation_checked") is True, "S3 decision lacks revocation_checked")
    if "staleness_s" in decision:
        _require(decision["staleness_s"] == 0, "S3 allow must have staleness_s 0")
    return decision


def resolve_authorized(manifest: dict, ref: dict, *, allowed_branch: str, decide, gateway,
                       revocation_check, consent_check=None, operation: str = "read_memory") -> bytes:
    """Validate manifest/ref, obtain a real S3 allow, then resolve through S5.

    `decide(request)` must call the real S3 boundary gate; `gateway(ref)` must
    call the real S5 memory gateway. Missing/cached/stale decisions fail closed.
    """
    _require(callable(decide), "decide must be the real S3 boundary adapter")
    _require(callable(gateway), "gateway must be the real S5 memory gateway")
    _require(callable(revocation_check), "revocation_check is required")
    try:
        validate_context_manifest(manifest, allowed_branch=allowed_branch,
                                  consent_check=consent_check,
                                  revocation_check=revocation_check)
    except ContextError as exc:
        raise AdapterError(str(exc)) from exc
    _require(isinstance(ref, dict), "ref must be an object")
    _require(any(r.get("context_id") == ref.get("context_id") and r.get("sha256") == ref.get("sha256")
                 for r in manifest["refs"]), "ref is not a member of the manifest")
    request = {
        "operation": operation,
        "resource": {
            "branch_id": ref["branch_id"],
            "store": ref["store"],
            "context_id": ref["context_id"],
        },
        "scope_digest": ref["scope_digest"],
    }
    try:
        decision = decide(request)
    except Exception as exc:
        raise AdapterError(f"S3 boundary unavailable: {type(exc).__name__}") from exc
    require_boundary_allow(decision, operation=operation)
    # Re-check freshness after the decision; an allow may not cache revocation.
    _require(revocation_check(ref["revocation_head_ref"]) is True,
             "revocation head stale/unavailable after decision")
    try:
        return resolve_context_ref(ref, gateway)
    except ContextError as exc:
        raise AdapterError(str(exc)) from exc


def decision_age_seconds(decision: dict, *, now=None) -> float:
    """Operational helper for tests/observability; not an authorization decision."""
    ts = decision.get("ts")
    _require(isinstance(ts, str) and ts, "decision ts required")
    try:
        when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AdapterError("decision ts is not ISO-8601") from exc
    _require(when.tzinfo is not None, "decision ts must include timezone")
    current = now or datetime.now(timezone.utc)
    return (current - when).total_seconds()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
