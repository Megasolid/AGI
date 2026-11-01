#!/usr/bin/env python3
"""AGI v4.1-E E1 context-continuity primitives.

Additive, stdlib-only. A context manifest is a *reference* object: it carries
ids, versions, hashes, classification, expiry and consent/revocation references.
It never carries the body. Resolution is delegated to an authorized resolver and
the returned bytes are verified against the pinned digest.

No network, credentials, identity, authority or execution. Data only.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

CONTEXT_SCHEMA = "agi.context/0.1"
CLASSIFICATIONS = frozenset({"public", "branch_private", "cross_branch_shared"})
REQUIRED_REF = (
    "context_id", "branch_id", "store", "version", "sha256",
    "scope_digest", "classification", "expires_at", "revocation_head_ref",
)
FORBIDDEN_REF_KEYS = frozenset({"body", "content", "text", "instructions", "payload"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ContextError(ValueError):
    """A context manifest or reference is invalid; callers must fail closed."""


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_iso(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ContextError(f"{field} must be a non-empty ISO-8601 string")
    text = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ContextError(f"{field} is not ISO-8601: {value!r}") from exc
    if dt.tzinfo is None:
        raise ContextError(f"{field} must include a timezone offset")
    return dt


def _now(now=None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    return _parse_iso(now, "now") if isinstance(now, str) else now


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise ContextError(message)


def make_context_manifest(*, branch_id: str, refs, provenance: dict,
                          classification: str = "branch_private",
                          created_at: str | None = None,
                          version: int = 1,
                          manifest_id: str | None = None) -> dict:
    """Build a manifest with no inline bodies and a canonical digest."""
    _require(isinstance(branch_id, str) and branch_id, "branch_id required")
    _require(classification in CLASSIFICATIONS, f"invalid manifest classification: {classification}")
    _require(isinstance(refs, list) and refs, "refs must be a non-empty list")
    _require(isinstance(provenance, dict), "provenance must be an object")
    manifest = {
        "schema": CONTEXT_SCHEMA,
        "manifest_id": manifest_id or "ctxm-" + sha256_hex(canonical_json(
            {"branch_id": branch_id, "refs": refs, "provenance": provenance}
        ))[:24],
        "branch_id": branch_id,
        "version": int(version),
        "classification": classification,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "refs": refs,
        "provenance": provenance,
    }
    manifest["digest"] = context_manifest_digest(manifest)
    return manifest


def context_manifest_digest(manifest: dict) -> str:
    body = {k: v for k, v in manifest.items() if k != "digest"}
    return "sha256:" + sha256_hex(canonical_json(body))


def validate_context_manifest(manifest: dict, *, now=None, allowed_branch: str | None = None,
                              consent_check=None, revocation_check=None) -> None:
    """Fail closed on schema, scope, classification, expiry, digest, consent or revocation."""
    _require(isinstance(manifest, dict), "manifest must be an object")
    _require(manifest.get("schema") == CONTEXT_SCHEMA, "unsupported context schema")
    _require(isinstance(manifest.get("manifest_id"), str) and manifest["manifest_id"], "manifest_id required")
    _require(isinstance(manifest.get("branch_id"), str) and manifest["branch_id"], "branch_id required")
    _require(isinstance(manifest.get("version"), int) and manifest["version"] >= 1, "manifest version must be >= 1")
    _require(manifest.get("classification") in CLASSIFICATIONS, "invalid manifest classification")
    _require(isinstance(manifest.get("provenance"), dict), "provenance required")
    _require(isinstance(manifest.get("refs"), list) and manifest["refs"], "refs required")
    _require(isinstance(manifest.get("digest"), str), "manifest digest required")
    _require(context_manifest_digest(manifest) == manifest["digest"],
             "manifest digest mismatch (content changed)")
    if allowed_branch is not None:
        _require(manifest["branch_id"] == allowed_branch,
                 f"manifest branch {manifest['branch_id']!r} is not the allowed branch")
    current = _now(now)
    seen_ids = set()
    for ref in manifest["refs"]:
        _validate_ref(ref, manifest["branch_id"], current, consent_check, revocation_check)
        _require(ref["context_id"] not in seen_ids, f"duplicate context_id: {ref['context_id']}")
        seen_ids.add(ref["context_id"])


def _validate_ref(ref: dict, manifest_branch: str, current: datetime,
                  consent_check, revocation_check) -> None:
    _require(isinstance(ref, dict), "each ref must be an object")
    for key in REQUIRED_REF:
        _require(key in ref, f"ref missing {key}")
    for key in FORBIDDEN_REF_KEYS:
        _require(key not in ref, f"ref must not inline {key}; context bodies are not manifest content")
    _require(isinstance(ref["context_id"], str) and ref["context_id"], "context_id required")
    _require(isinstance(ref["branch_id"], str) and ref["branch_id"], "ref branch_id required")
    _require(isinstance(ref["store"], str) and ref["store"], "store required")
    _require(isinstance(ref["version"], int) and ref["version"] >= 1, "ref version must be >= 1")
    _require(isinstance(ref["sha256"], str) and bool(_HEX64.fullmatch(ref["sha256"])), "sha256 must be 64 hex chars")
    _require(isinstance(ref["scope_digest"], str) and bool(_HEX64.fullmatch(ref["scope_digest"])), "scope_digest must be 64 hex chars")
    _require(ref["classification"] in CLASSIFICATIONS, "invalid ref classification")
    _require(isinstance(ref["revocation_head_ref"], str) and ref["revocation_head_ref"], "revocation_head_ref required")
    expires = _parse_iso(ref["expires_at"], "expires_at")
    _require(expires > current, "context ref expired")
    cross = ref["classification"] == "cross_branch_shared" or ref["branch_id"] != manifest_branch
    if cross:
        _require(ref["classification"] == "cross_branch_shared",
                 "cross-branch ref must be classified cross_branch_shared")
        _require(isinstance(ref.get("consent_ref"), str) and ref["consent_ref"],
                 "cross-branch ref requires consent_ref")
        _require(callable(consent_check), "consent_check is required for cross-branch refs")
        _require(consent_check(ref["consent_ref"]) is True, "consent not valid")
    _require(callable(revocation_check), "revocation_check is required")
    _require(revocation_check(ref["revocation_head_ref"]) is True, "revocation head unavailable or stale")


def resolve_context_ref(ref: dict, resolver) -> bytes:
    """Resolve a validated ref to bytes and verify the pinned digest. Data, never instructions."""
    _require(callable(resolver), "resolver must be callable")
    try:
        data = resolver(ref)
    except Exception as exc:
        raise ContextError(f"context unavailable: {type(exc).__name__}") from exc
    _require(isinstance(data, (bytes, bytearray)), "resolver must return bytes")
    data = bytes(data)
    _require(len(data) <= 8 * 1024 * 1024, "context body exceeds 8 MiB cap")
    _require(sha256_hex(data) == ref["sha256"], "context digest mismatch")
    return data


def compact_handoff_refs(manifest: dict) -> list[dict]:
    """Return the minimum ref tuple suitable for a handoff (no bodies)."""
    out = []
    for ref in manifest.get("refs", []):
        out.append({k: ref.get(k) for k in (
            "context_id", "branch_id", "store", "version", "sha256",
            "scope_digest", "classification", "expires_at", "consent_ref", "revocation_head_ref",
        ) if k in ref})
    return out
