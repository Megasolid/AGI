#!/usr/bin/env python3
"""P6 E5 capability metadata + quarantine + activation contract.

Metadata-only: manifests carry hashes, permissions, evaluation and governance
references, never executable instructions or scripts. Registration/approval is
not authority; activation requires an explicit S3-style allow decision and a
grant. No network, credentials or execution.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re

CAP_SCHEMA = "agi.capability/0.1"
CLASSES = frozenset({"A", "B", "C"})
STATUSES = frozenset({"quarantined", "evaluated", "approved", "revoked"})
FORBIDDEN = frozenset({"instructions", "skill_md", "body", "scripts", "content_text"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class CapabilityError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise CapabilityError(msg)


def _hex(value) -> bool:
    return isinstance(value, str) and bool(_HEX64.fullmatch(value))


def make_capability(*, capability_id: str, version: str, cls: str, publisher: str,
                    source: str, tree_sha256: str, files, requested_permissions=None,
                    evaluation_ref=None, governance_card_ref=None) -> dict:
    _require(capability_id and version, "capability_id/version required")
    _require(cls in CLASSES, "invalid capability class")
    _require(_hex(tree_sha256), "tree_sha256 must be 64 hex")
    _require(isinstance(files, list) and files, "files required")
    for f in files:
        _require(isinstance(f, dict) and isinstance(f.get("path"), str) and _hex(f.get("sha256")),
                 "each file needs path + sha256")
    return {
        "schema": CAP_SCHEMA,
        "capability_id": capability_id,
        "version": version,
        "class": cls,
        "publisher": publisher,
        "source": source,
        "tree_sha256": tree_sha256,
        "files": files,
        "requested_permissions": requested_permissions or {},
        "evaluation_ref": evaluation_ref,
        "governance_card_ref": governance_card_ref,
        "no_identity_authority": True,
        "status": "quarantined",
    }


def validate_manifest(cap: dict) -> None:
    _require(isinstance(cap, dict), "capability must be an object")
    for key in ("schema", "capability_id", "version", "class", "publisher", "source",
                "tree_sha256", "files", "requested_permissions", "no_identity_authority", "status"):
        _require(key in cap, f"capability missing {key}")
    for key in FORBIDDEN:
        _require(key not in cap, f"capability must not carry {key} (instructions/scripts are quarantined)")
    _require(cap["schema"] == CAP_SCHEMA, "unsupported capability schema")
    _require(cap["class"] in CLASSES, "invalid capability class")
    _require(_hex(cap["tree_sha256"]), "invalid tree hash")
    _require(isinstance(cap["files"], list) and cap["files"], "files required")
    for f in cap["files"]:
        _require(isinstance(f, dict) and isinstance(f.get("path"), str) and _hex(f.get("sha256")),
                 "invalid file entry")
    _require(cap["no_identity_authority"] is True, "capability must not claim identity/authority")
    _require(cap["status"] in STATUSES, "invalid capability status")


def evaluate(cap: dict, *, evaluation_ref: str, scan_ref: str, local_eval_ref: str) -> dict:
    validate_manifest(cap)
    _require(cap["status"] == "quarantined", "only quarantined capabilities can be evaluated")
    _require(all(isinstance(x, str) and x for x in (evaluation_ref, scan_ref, local_eval_ref)),
             "evaluation/scan/local refs required")
    out = copy.deepcopy(cap)
    out["status"] = "evaluated"
    out["evaluation_ref"] = evaluation_ref
    out["scan_ref"] = scan_ref
    out["local_eval_ref"] = local_eval_ref
    return out


def approve(cap: dict, *, approval_ref: str) -> dict:
    validate_manifest(cap)
    _require(cap["status"] == "evaluated", "capability not evaluated")
    _require(isinstance(approval_ref, str) and approval_ref, "approval_ref required")
    out = copy.deepcopy(cap)
    out["status"] = "approved"
    out["approval_ref"] = approval_ref
    return out


def revoke(cap: dict, *, revocation_ref: str) -> dict:
    validate_manifest(cap)
    _require(isinstance(revocation_ref, str) and revocation_ref, "revocation_ref required")
    out = copy.deepcopy(cap)
    out["status"] = "revoked"
    out["revocation_ref"] = revocation_ref
    return out


def world_view(capabilities) -> list[dict]:
    """Metadata-only projection; no instructions, bodies or implicit authorization."""
    out = []
    for cap in capabilities:
        validate_manifest(cap)
        out.append({
            "capability_id": cap["capability_id"],
            "version": cap["version"],
            "class": cap["class"],
            "publisher": cap["publisher"],
            "source": cap["source"],
            "tree_sha256": cap["tree_sha256"],
            "requested_permissions": copy.deepcopy(cap.get("requested_permissions", {})),
            "evaluation_ref": cap.get("evaluation_ref"),
            "governance_card_ref": cap.get("governance_card_ref"),
            "status": cap["status"],
            "authorized": False,
            "note": "listing is not authorization; activation requires a separate grant/decision",
        })
    return out


def activation(cap: dict, *, decision: dict, grant: dict, sandbox) -> dict:
    """Validate S3 allow + grant, then call the sandbox activation hook.

    The capability instructions are never loaded; the sandbox receives metadata
    only. `sandbox(token)` must perform its own isolation and return an activation id.
    """
    validate_manifest(cap)
    _require(cap["status"] == "approved", "capability not approved")
    _require(isinstance(decision, dict), "S3 decision required")
    _require(decision.get("result") == "allow", "S3 decision is not allow")
    _require(decision.get("operation") == "activate_capability", "wrong operation")
    _require(decision.get("revocation_checked") is True, "revocation not checked")
    _require(decision.get("grant_id"), "grant_id required")
    _require(isinstance(grant, dict), "grant required")
    _require(grant.get("capability_id") == cap["capability_id"], "grant capability mismatch")
    _require(grant.get("version") == cap["version"], "grant version mismatch")
    _require(grant.get("grant_id") == decision.get("grant_id"), "decision/grant mismatch")
    _require(callable(sandbox), "sandbox must be callable")
    token = {
        "schema": "agi.capability.activation/0.1",
        "capability_id": cap["capability_id"],
        "version": cap["version"],
        "grant_id": grant["grant_id"],
        "decision_id": decision.get("decision_id"),
        "class": cap["class"],
        "instructions_loaded": False,
        "authorization": "S3-decision-bound; not an authority grant",
    }
    activation_id = sandbox(token)
    _require(isinstance(activation_id, str) and activation_id, "sandbox must return activation id")
    token["activation_id"] = activation_id
    return token
