#!/usr/bin/env python3
"""P5 durable operator event journal.

Append-only, hash-chained, sequence-numbered event journal for the Operator.
The journal is operational evidence input, not AGI evidence by itself; no
network, credentials or authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class JournalError(ValueError):
    pass


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "digest"}
    return "sha256:" + hashlib.sha256(canonical_json(body)).hexdigest()


class OperatorJournal:
    def __init__(self, path, *, fsync: bool = True):
        self.path = Path(path)
        self.fsync = fsync
        self._records = []
        self._by_event = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        prev = None
        with self.path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    seq = rec["seq"]
                    event_id = rec["event_id"]
                    digest = rec["digest"]
                except Exception as exc:
                    raise JournalError(f"corrupt journal line {line_no}") from exc
                if seq != len(self._records) + 1:
                    raise JournalError("journal sequence gap")
                if prev is not None and rec.get("prev_digest") != prev:
                    raise JournalError("journal chain mismatch")
                if _digest(rec) != digest:
                    raise JournalError("journal digest mismatch")
                if event_id in self._by_event:
                    raise JournalError("duplicate event_id in journal")
                self._records.append(rec)
                self._by_event[event_id] = rec
                prev = digest

    def append(self, event_id: str, event_type: str, payload: dict) -> dict:
        if event_id in self._by_event:
            rec = self._by_event[event_id]
            candidate = {"seq": rec["seq"], "event_id": event_id, "type": event_type,
                         "payload": payload, "prev_digest": rec["prev_digest"]}
            if _digest(candidate) == rec["digest"]:
                return rec
            raise JournalError("duplicate event_id with different content")
        seq = len(self._records) + 1
        prev = self._records[-1]["digest"] if self._records else None
        rec = {"seq": seq, "event_id": event_id, "type": event_type,
               "payload": payload, "prev_digest": prev}
        rec["digest"] = _digest(rec)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
            f.flush()
            if self.fsync:
                os.fsync(f.fileno())
        self._records.append(rec)
        self._by_event[event_id] = rec
        return rec

    @property
    def last_seq(self) -> int:
        return len(self._records)

    def read_from(self, cursor: int) -> list[dict]:
        if cursor < 1:
            raise JournalError("cursor must be >= 1")
        if cursor > self.last_seq + 1:
            raise JournalError("event loss: cursor beyond last sequence")
        return [r for r in self._records if r["seq"] >= cursor]

    def verify(self) -> dict:
        prev = None
        for rec in self._records:
            if rec.get("prev_digest") != prev or _digest(rec) != rec.get("digest"):
                return {"ok": False, "seq": rec.get("seq")}
            prev = rec["digest"]
        return {"ok": True, "records": len(self._records), "head": prev}
