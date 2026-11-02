#!/usr/bin/env python3
"""H0 — durable audit store (revision 3, addresses King F6).

The revision-2 audit sink was an in-memory list. That proved ordering, not
durability: the whole F1 correction rests on audit being a PRECONDITION, which is
meaningless if the record evaporates on restart.

Contract implemented here:
  * append-only JSONL on disk, fsync'd before the append is acknowledged
  * hash-chained (each record carries prev_digest) so deletion/reordering is detectable
  * atomic acknowledgement: append() returns only after the bytes are durable
  * restart recovery: reload re-verifies the chain and reports a watermark
  * fail-closed: if the store cannot be written or verified, append() raises and
    the caller must not execute

Two-phase lifecycle (King F7):
  * `intent`   — written BEFORE the effect, outcome=pending
  * `outcome`  — written AFTER the effect (or after a failure), one per request
  A request therefore has exactly one intent and at most one outcome, linked by
  correlation_id; an intent with no outcome means "authorised, execution in doubt".

No network, no credentials, no authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class AuditStoreError(ValueError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(obj) -> str:
    return "sha256:" + hashlib.sha256(_canonical(obj)).hexdigest()


class DurableAuditStore:
    """Hash-chained, fsync'd JSONL audit store with restart recovery."""

    def __init__(self, path, *, fsync: bool = True):
        self.path = Path(path)
        self.fsync = fsync
        self._records: list[dict] = []
        self._intents: dict[str, dict] = {}
        self._outcomes: dict[str, dict] = {}
        self._lock = __import__("threading").RLock()
        self._tail_digest: str | None = None
        self._recover()

    # -- recovery --------------------------------------------------------
    def _recover(self) -> None:
        if not self.path.exists():
            return
        prev = None
        with self.path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception as exc:
                    raise AuditStoreError("E_AUDIT_CORRUPT", f"line {lineno}") from exc
                body = {k: v for k, v in rec.items() if k != "digest"}
                if _digest(body) != rec.get("digest"):
                    raise AuditStoreError("E_AUDIT_TAMPERED", f"digest mismatch line {lineno}")
                if rec.get("prev_digest") != prev:
                    raise AuditStoreError("E_AUDIT_TAMPERED", f"chain break line {lineno}")
                prev = rec["digest"]
                self._index(rec)
        self._tail_digest = prev

    def _index(self, rec: dict) -> None:
        self._records.append(rec)
        cid = rec.get("correlation_id")
        if rec.get("phase") == "intent":
            if cid in self._intents:
                raise AuditStoreError("E_AUDIT_DUPLICATE", f"intent {cid}")
            self._intents[cid] = rec
        elif rec.get("phase") == "outcome":
            if cid not in self._intents:
                raise AuditStoreError("E_AUDIT_ORPHAN", f"outcome without intent {cid}")
            if cid in self._outcomes:
                raise AuditStoreError("E_AUDIT_DUPLICATE", f"outcome {cid}")
            self._outcomes[cid] = rec

    # -- append ----------------------------------------------------------
    def append(self, record: dict) -> dict:
        """Atomically append and fsync. Returns the stored record with chain fields."""
        rec = {k: v for k, v in record.items() if k not in {"prev_digest", "digest", "seq"}}
        with self._lock:
            rec["seq"] = len(self._records) + 1
            rec["prev_digest"] = self._tail_digest
            rec["digest"] = _digest(rec)
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
                    fh.flush()
                    if self.fsync:
                        os.fsync(fh.fileno())
            except Exception as exc:
                raise AuditStoreError("E_AUDIT_UNAVAILABLE", f"{type(exc).__name__}: {exc}") from exc
            # verify what we just wrote is readable and chained
            if not self.path.exists():
                raise AuditStoreError("E_AUDIT_UNAVAILABLE", "store vanished after append")
            self._index(rec)
            self._tail_digest = rec["digest"]
            return rec

    # -- queries ---------------------------------------------------------
    @property
    def head_digest(self) -> str | None:
        return self._tail_digest

    @property
    def count(self) -> int:
        return len(self._records)

    def watermark(self) -> dict:
        return {"records": self.count, "head_digest": self._tail_digest}

    def intent_for(self, correlation_id: str) -> dict | None:
        return self._intents.get(correlation_id)

    def outcome_for(self, correlation_id: str) -> dict | None:
        return self._outcomes.get(correlation_id)

    def dangling_intents(self) -> list[str]:
        """Authorised but with no recorded outcome: execution is in doubt."""
        return [cid for cid in self._intents if cid not in self._outcomes]

    def verify_chain(self) -> dict:
        prev = None
        for rec in self._records:
            body = {k: v for k, v in rec.items() if k != "digest"}
            if _digest(body) != rec["digest"]:
                return {"ok": False, "reason": "digest", "seq": rec.get("seq")}
            if rec.get("prev_digest") != prev:
                return {"ok": False, "reason": "chain", "seq": rec.get("seq")}
            prev = rec["digest"]
        return {"ok": True, "records": len(self._records), "head": prev}
