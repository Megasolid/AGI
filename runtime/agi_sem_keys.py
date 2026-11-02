#!/usr/bin/env python3
"""P4 key lifecycle registry (metadata only).

Stores public key metadata and status; never private keys. `authorize` is a
verification policy helper, not an identity or authority grant. No network.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


class KeyError(ValueError):
    """Unknown, expired, revoked or malformed key."""


@dataclass(frozen=True)
class KeyRecord:
    key_id: str
    alg: str
    public_key_b64: str
    status: str = "active"          # active | retired | revoked
    not_before: str | None = None
    not_after: str | None = None
    purpose: str = "message-auth"


def _parse(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise KeyError("invalid key timestamp") from exc
    if dt.tzinfo is None:
        raise KeyError("key timestamp must include timezone")
    return dt


class KeyRegistry:
    def __init__(self):
        self._keys = {}

    def add(self, record: KeyRecord) -> None:
        if not record.key_id or not record.alg or not record.public_key_b64:
            raise KeyError("key_id/alg/public_key_b64 required")
        if record.status not in {"active", "retired", "revoked"}:
            raise KeyError("invalid key status")
        if record.key_id in self._keys:
            raise KeyError("duplicate key_id")
        self._keys[record.key_id] = record

    def retire(self, key_id: str) -> KeyRecord:
        rec = self._keys.get(key_id)
        if rec is None:
            raise KeyError("unknown key")
        updated = KeyRecord(**{**rec.__dict__, "status": "retired"})
        self._keys[key_id] = updated
        return updated

    def revoke(self, key_id: str) -> KeyRecord:
        rec = self._keys.get(key_id)
        if rec is None:
            raise KeyError("unknown key")
        updated = KeyRecord(**{**rec.__dict__, "status": "revoked"})
        self._keys[key_id] = updated
        return updated

    def authorize(self, key_id: str, *, now=None, purpose: str = "message-auth") -> KeyRecord:
        rec = self._keys.get(key_id)
        if rec is None:
            raise KeyError("unknown key")
        if rec.status == "revoked":
            raise KeyError("key revoked")
        if rec.purpose != purpose:
            raise KeyError("key purpose mismatch")
        current = now or datetime.now(timezone.utc)
        if isinstance(current, str):
            current = _parse(current)
        if rec.not_before and current < _parse(rec.not_before):
            raise KeyError("key not yet valid")
        if rec.not_after and current > _parse(rec.not_after):
            raise KeyError("key expired")
        return rec
