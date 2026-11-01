#!/usr/bin/env python3
"""AGI v4.1-E E4 development-handoff primitives.

Additive, stdlib-only. A handoff is a bounded task statement with context
references, acceptance criteria, evidence requirements, dependencies, ownership,
explicit permissions (declarations, not grants) and non-goals. It carries no
authority, identity, consent or execution permission.

No network, credentials or execution.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

HANDOFF_SCHEMA = "agi.handoff/0.1"
RECEIPT_SCHEMA = "agi.handoff.receipt/0.1"
OUTCOMES = frozenset({"success", "partial", "failure"})
PERMISSION_KEYS = frozenset({"read", "write", "execute", "network", "tools"})
FORBIDDEN_KEYS = frozenset({"grant", "grants", "authority", "identity", "consent_record", "passport", "key"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class HandoffError(ValueError):
    """A handoff or receipt is invalid; callers must fail closed."""


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise HandoffError(msg)


def _now(now=None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, str):
        try:
            dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HandoffError("now must be ISO-8601") from exc
        _require(dt.tzinfo is not None, "now must include a timezone")
        return dt
    return now


def _parse_iso(value: str, field: str) -> datetime:
    _require(isinstance(value, str) and value, f"{field} required")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HandoffError(f"{field} is not ISO-8601") from exc
    _require(dt.tzinfo is not None, f"{field} must include a timezone")
    return dt


def make_handoff(*, task_id: str, title: str, objective: str, owner: str,
                 branch_id: str, context_manifest: dict,
                 acceptance_criteria, evidence_requirements,
                 dependencies=(), permissions=None, non_goals=(),
                 created_at: str | None = None, expires_at: str | None = None,
                 version: int = 1) -> dict:
    _require(isinstance(task_id, str) and task_id, "task_id required")
    _require(isinstance(title, str) and title, "title required")
    _require(isinstance(objective, str) and objective, "objective required")
    _require(isinstance(owner, str) and owner, "owner required")
    _require(isinstance(branch_id, str) and branch_id, "branch_id required")
    _require(isinstance(context_manifest, dict) and context_manifest.get("digest"),
             "context_manifest with digest required")
    _require(isinstance(acceptance_criteria, list) and acceptance_criteria, "acceptance criteria required")
    _require(isinstance(evidence_requirements, list) and evidence_requirements, "evidence requirements required")
    _require(isinstance(non_goals, list) and non_goals, "explicit non-goals required")
    perms = dict(permissions or {})
    _require(set(perms).issubset(PERMISSION_KEYS), "unknown permission key")
    for k, v in perms.items():
        _require(isinstance(v, bool), f"permission {k} must be boolean")
    handoff = {
        "schema": HANDOFF_SCHEMA,
        "task_id": task_id,
        "version": int(version),
        "title": title,
        "objective": objective,
        "owner": owner,
        "branch_id": branch_id,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at,
        "context_manifest": context_manifest,
        "context_refs": context_manifest.get("refs", []),
        "acceptance_criteria": acceptance_criteria,
        "evidence_requirements": evidence_requirements,
        "dependencies": list(dependencies),
        "permissions": perms,
        "non_goals": non_goals,
    }
    handoff["handoff_digest"] = handoff_digest(handoff)
    return handoff


def handoff_digest(handoff: dict) -> str:
    body = {k: v for k, v in handoff.items() if k not in ("handoff_digest", "signature")}
    return "sha256:" + _sha(canonical_json(body))


def validate_handoff(handoff: dict, *, now=None) -> None:
    _require(isinstance(handoff, dict), "handoff must be an object")
    for key in ("schema", "task_id", "version", "title", "objective", "owner", "branch_id",
                "created_at", "context_manifest", "context_refs", "acceptance_criteria",
                "evidence_requirements", "dependencies", "permissions", "non_goals", "handoff_digest"):
        _require(key in handoff, f"handoff missing {key}")
    _require(handoff["schema"] == HANDOFF_SCHEMA, "unsupported handoff schema")
    for key in FORBIDDEN_KEYS:
        _require(key not in handoff, f"handoff must not carry {key}")
    _require(handoff_digest(handoff) == handoff["handoff_digest"], "handoff digest mismatch")
    _require(isinstance(handoff["acceptance_criteria"], list) and handoff["acceptance_criteria"], "acceptance criteria required")
    _require(isinstance(handoff["evidence_requirements"], list) and handoff["evidence_requirements"], "evidence requirements required")
    _require(isinstance(handoff["non_goals"], list) and handoff["non_goals"], "non-goals required")
    _require(isinstance(handoff["context_refs"], list) and handoff["context_refs"], "context refs required")
    _require(handoff["context_manifest"].get("digest") == handoff["context_manifest"].get("digest"), "context digest required")
    if handoff.get("expires_at"):
        _require(_parse_iso(handoff["expires_at"], "expires_at") > _now(now), "handoff expired")
    for ref in handoff["context_refs"]:
        _require(isinstance(ref, dict) and "sha256" in ref, "each context ref needs sha256")
        _require(isinstance(ref["sha256"], str) and bool(_HEX64.fullmatch(ref["sha256"])), "invalid context sha256")
        for key in ("body", "content", "text", "instructions"):
            _require(key not in ref, f"context ref must not inline {key}")
    perms = handoff["permissions"]
    _require(isinstance(perms, dict) and set(perms).issubset(PERMISSION_KEYS), "invalid permissions object")
    _require(all(isinstance(v, bool) for v in perms.values()), "permissions must be boolean")
    # Permission declarations are not grants; no authority object is accepted.


def completion_receipt(handoff: dict, *, outcome: str, evidence_refs,
                       constraints_met, residual_risks=(), completed_at: str | None = None) -> dict:
    validate_handoff(handoff)
    _require(outcome in OUTCOMES, "invalid outcome")
    _require(isinstance(evidence_refs, list) and evidence_refs, "evidence refs required")
    _require(isinstance(constraints_met, list), "constraints_met must be a list")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "task_id": handoff["task_id"],
        "handoff_digest": handoff["handoff_digest"],
        "outcome": outcome,
        "evidence_refs": evidence_refs,
        "constraints_met": constraints_met,
        "residual_risks": list(residual_risks),
        "completed_at": completed_at or datetime.now(timezone.utc).isoformat(),
    }
    receipt["receipt_digest"] = receipt_digest(receipt)
    return receipt


def receipt_digest(receipt: dict) -> str:
    body = {k: v for k, v in receipt.items() if k not in ("receipt_digest", "signature")}
    return "sha256:" + _sha(canonical_json(body))


def validate_receipt(receipt: dict, *, handoff: dict | None = None) -> None:
    _require(isinstance(receipt, dict), "receipt must be an object")
    for key in ("schema", "task_id", "handoff_digest", "outcome", "evidence_refs",
                "constraints_met", "residual_risks", "completed_at", "receipt_digest"):
        _require(key in receipt, f"receipt missing {key}")
    _require(receipt["schema"] == RECEIPT_SCHEMA, "unsupported receipt schema")
    _require(receipt["outcome"] in OUTCOMES, "invalid receipt outcome")
    _require(receipt_digest(receipt) == receipt["receipt_digest"], "receipt digest mismatch")
    _require(isinstance(receipt["evidence_refs"], list) and receipt["evidence_refs"], "evidence refs required")
    if handoff is not None:
        _require(receipt["handoff_digest"] == handoff.get("handoff_digest"), "receipt does not match handoff")
        _require(receipt["task_id"] == handoff.get("task_id"), "receipt task mismatch")


def reconstruct_task(handoff: dict, resolver) -> dict:
    """A fresh agent path: validate the handoff, resolve refs, return task data only."""
    from agi_context import resolve_context_ref
    validate_handoff(handoff)
    context = {}
    for ref in handoff["context_refs"]:
        context[ref["context_id"]] = resolve_context_ref(ref, resolver)
    return {
        "task_id": handoff["task_id"],
        "objective": handoff["objective"],
        "acceptance_criteria": handoff["acceptance_criteria"],
        "evidence_requirements": handoff["evidence_requirements"],
        "non_goals": handoff["non_goals"],
        "permissions": handoff["permissions"],
        "context": context,
    }
