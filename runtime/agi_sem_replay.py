#!/usr/bin/env python3
"""P4 durable replay protection for `agi.sem`.

Append-only JSONL store keyed by (session_id, message_id). Same digest is
idempotent; different digest is replay and fails closed. A corrupt store refuses
to load. No network, credentials or authority.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


class ReplayError(ValueError):
    """Duplicate with different content, or corrupt store."""


class ReplayStore:
    def __init__(self, path, *, fsync: bool = True):
        self.path = Path(path)
        self.fsync = fsync
        self._seen = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    key = (rec["session_id"], rec["message_id"])
                    digest = rec["digest"]
                except Exception as exc:
                    raise ReplayError(f"corrupt replay store line {line_no}") from exc
                if key in self._seen and self._seen[key] != digest:
                    raise ReplayError(f"replay store conflict for {key}")
                self._seen[key] = digest

    def check_and_record(self, session_id: str, message_id: str, digest: str) -> str:
        key = (session_id, message_id)
        if key in self._seen:
            if self._seen[key] == digest:
                return "idempotent"
            raise ReplayError("replay: duplicate message_id with different content")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"session_id": session_id, "message_id": message_id, "digest": digest},
                          sort_keys=True, separators=(",", ":"))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            if self.fsync:
                os.fsync(f.fileno())
        self._seen[key] = digest
        return "recorded"
