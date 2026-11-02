#!/usr/bin/env python3
"""H0 — durable audit store, revision 4.

Revision 3 fixes carried forward:
  * append-only JSONL, fsync before acknowledgement, hash-chained
  * tamper evidence on reload (digest + chain)
  * two-phase lifecycle: intent before the effect, outcome after

Revision 4 corrections (King review 2026-11-02T19:46):

  F9  VALIDATE BEFORE PERSIST: lifecycle invariants are checked before any byte is
      appended. A rejected append leaves the file, the sequence and the chain head
      exactly as they were.

  F10 WRITER CONCURRENCY: a single-writer contract is enforced by an OS-level lock
      file. A second writer is refused rather than silently forking the chain. On
      every append the store re-reads the on-disk tail and compares it with its own
      head; a mismatch means another writer touched the file and the append is
      refused (E_AUDIT_FOREIGN_WRITE).

  The store never appends a record it would reject.

No network, no credentials, no authority. This is not a server.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path


class AuditStoreError(ValueError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(obj) -> str:
    return "sha256:" + hashlib.sha256(_canonical(obj)).hexdigest()


class _SingleWriterLock:
    """OS-level advisory lock; refuses a second live writer in this process or another."""

    def __init__(self, lock_path: Path):
        self.path = lock_path
        self._fh = None

    def acquire(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fh = self.path.open("a+")
        except Exception as exc:  # noqa: BLE001
            raise AuditStoreError("E_AUDIT_UNAVAILABLE", f"lock open: {type(exc).__name__}") from exc
        try:
            if os.name == "nt":
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            fh.close()
            raise AuditStoreError("E_AUDIT_SECOND_WRITER", "another writer holds the store") from exc
        self._fh = fh

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if os.name == "nt":
                import msvcrt
                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            self._fh.close()
            self._fh = None


class _FailureInjector:
    """Test-only fault injection that cannot be repurposed as a substitution route.

    A simulation may make the store report failure; it can never supply a different
    implementation or change where the bytes go. This is the ONLY supported way to
    simulate an audit outage in tests (R8).
    """

    _MODE = {"fail": False}

    @classmethod
    def set(cls, failing: bool) -> None:
        cls._MODE["fail"] = bool(failing)

    @classmethod
    def failing(cls) -> bool:
        return bool(cls._MODE["fail"])


class DurableAuditStore:
    """Hash-chained, fsync'd, single-writer JSONL audit store.

    R6: durability is DERIVED from configuration, never declared. `durability()`
    reports exactly what this instance does; there is no class-level constant that
    could claim durability for an instance that does not have it.
    """

    def __init__(self, path, *, fsync: bool = True, _allow_unsafe_observer: bool = False):
        """Single-writer enforcement is ALWAYS on for a writable store.

        `_allow_unsafe_observer=True` disables the lock, the pre-append chain check
        AND fsync. Such an instance reports itself non-enforceable, and the Kernel
        refuses it categorically (R6).
        """
        self.path = Path(path)
        self.fsync = bool(fsync) and not _allow_unsafe_observer
        self.enforce_single_writer = not _allow_unsafe_observer
        self._observer_mode = bool(_allow_unsafe_observer)
        self.lock = _SingleWriterLock(self.path.with_suffix(self.path.suffix + ".lock"))
        self._records: list[dict] = []
        self._intents: dict[str, dict] = {}
        self._outcomes: dict[str, dict] = {}
        self._lock = threading.RLock()
        self._tail_digest: str | None = None
        self._tail_seq = 0
        self._recover()

    # -- R6: verifiable enforcement-store contract ------------------------
    def durability(self) -> dict:
        """Report what this instance actually guarantees. Derived, not asserted."""
        return {
            "store_type": "DurableAuditStore",
            "enforceable": (self.fsync and self.enforce_single_writer and not self._observer_mode),
            "fsync": bool(self.fsync),
            "single_writer": bool(self.enforce_single_writer),
            "observer_mode": bool(self._observer_mode),
            "append_only": True,
            "chained": True,
        }

    # -- R8: identity probe ----------------------------------------------
    def probe(self) -> str:
        """Cheap, side-effect-free identity marker used to verify the bound store."""
        return "h0-audit-store-v1:" + str(self.path)

    # -- validation BEFORE persistence (F9) ------------------------------
    def _validate(self, rec: dict) -> None:
        phase = rec.get("phase")
        cid = rec.get("correlation_id")
        if phase == "intent":
            if not cid:
                raise AuditStoreError("E_AUDIT_INVALID", "intent without correlation_id")
            if cid in self._intents:
                raise AuditStoreError("E_AUDIT_DUPLICATE", f"intent {cid}")
        elif phase == "outcome":
            if not cid:
                raise AuditStoreError("E_AUDIT_INVALID", "outcome without correlation_id")
            if cid not in self._intents:
                raise AuditStoreError("E_AUDIT_ORPHAN", f"outcome without intent {cid}")
            if cid in self._outcomes:
                raise AuditStoreError("E_AUDIT_DUPLICATE", f"outcome {cid}")
        elif phase in {"deny", "indeterminate"}:
            if not cid:
                raise AuditStoreError("E_AUDIT_INVALID", f"{phase} without correlation_id")
            if phase == "indeterminate" and cid not in self._intents:
                raise AuditStoreError("E_AUDIT_ORPHAN", f"indeterminate without intent {cid}")
        else:
            raise AuditStoreError("E_AUDIT_INVALID", f"unknown phase {phase!r}")

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
                # G3: a digest-consistent but semantically invalid log must not load
                self._validate(rec)
                self._index(rec)
        self._tail_digest = prev

    def _index(self, rec: dict) -> None:
        self._records.append(rec)
        self._tail_seq = rec.get("seq", self._tail_seq)
        cid = rec.get("correlation_id")
        if rec.get("phase") == "intent":
            self._intents[cid] = rec
        elif rec.get("phase") == "outcome":
            self._outcomes[cid] = rec

    # -- durability check (F10) ------------------------------------------
    def _disk_chain(self) -> tuple[str | None, int]:
        """G4: re-read and fully re-verify the on-disk chain before appending.

        Revision 4 compared only the final digest, so an altered earlier record with
        an unchanged tail went undetected. Every record's digest and linkage is now
        checked, and the record count is returned so a truncation is also caught.
        """
        if not self.path.exists():
            return None, 0
        prev = None
        count = 0
        with self.path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except Exception as exc:  # noqa: BLE001
                    raise AuditStoreError("E_AUDIT_CORRUPT", f"line {lineno}") from exc
                body = {k: v for k, v in rec.items() if k != "digest"}
                if _digest(body) != rec.get("digest"):
                    raise AuditStoreError("E_AUDIT_TAMPERED", f"digest mismatch line {lineno}")
                if rec.get("prev_digest") != prev:
                    raise AuditStoreError("E_AUDIT_TAMPERED", f"chain break line {lineno}")
                prev = rec["digest"]
                count += 1
        return prev, count

    # -- append ----------------------------------------------------------
    def append(self, record: dict) -> dict:
        """Validate, then atomically append and fsync. Never persists a rejected record."""
        rec = {k: v for k, v in record.items() if k not in {"prev_digest", "digest", "seq"}}
        with self._lock:
            # R8 test-only fault injection (never a substitution route)
            if _FailureInjector.failing():
                raise AuditStoreError("E_AUDIT_UNAVAILABLE", "injected failure (test mode)")
            # F9: validate before touching the file
            self._validate(rec)

            if self.enforce_single_writer:
                self.lock.acquire()
            try:
                # F10 + G4: fully re-verify the on-disk chain before appending
                disk_tail, disk_count = self._disk_chain()
                if disk_tail != self._tail_digest or disk_count != self._tail_seq:
                    raise AuditStoreError("E_AUDIT_FOREIGN_WRITE",
                                          "chain head or length changed outside this writer")

                rec["seq"] = self._tail_seq + 1
                rec["prev_digest"] = self._tail_digest
                rec["digest"] = _digest(rec)
                try:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    with self.path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
                        fh.flush()
                        if self.fsync:
                            os.fsync(fh.fileno())
                except Exception as exc:  # noqa: BLE001
                    raise AuditStoreError("E_AUDIT_UNAVAILABLE",
                                          f"{type(exc).__name__}: {exc}") from exc
                self._index(rec)
                self._tail_digest = rec["digest"]
                return rec
            finally:
                if self.enforce_single_writer:
                    self.lock.release()

    # -- queries ---------------------------------------------------------
    @property
    def head_digest(self) -> str | None:
        return self._tail_digest

    @property
    def count(self) -> int:
        return len(self._records)

    def watermark(self) -> dict:
        return {"records": self.count, "head_digest": self._tail_digest, "seq": self._tail_seq}

    def intent_for(self, correlation_id: str) -> dict | None:
        return self._intents.get(correlation_id)

    def outcome_for(self, correlation_id: str) -> dict | None:
        return self._outcomes.get(correlation_id)

    def dangling_intents(self) -> list[str]:
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
