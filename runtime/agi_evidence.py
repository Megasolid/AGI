#!/usr/bin/env python3
"""P6 E6 evidence completeness + recovery/effect reconciliation.

Evidence packets are hash-anchored metadata, not logs. The effect ledger records
externally visible actions; recovery never silently discards emitted effects.
No network, credentials or execution.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

EVIDENCE_SCHEMA = "agi.evidence.packet/0.1"
E_LEVELS = frozenset({"E0", "E1", "E2", "E3", "E4"})


class EvidenceError(ValueError):
    pass


class RecoveryError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise EvidenceError(msg)


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_packet(*, run_id: str, claim: str, evidence_refs, environment: dict,
                e_level: str, artifact_hashes: dict, review_refs=None) -> dict:
    _require(run_id and claim, "run_id/claim required")
    _require(isinstance(evidence_refs, list) and evidence_refs, "evidence refs required")
    _require(isinstance(environment, dict) and environment, "environment fingerprint required")
    _require(e_level in E_LEVELS, "invalid E-level")
    _require(isinstance(artifact_hashes, dict) and artifact_hashes, "artifact hashes required")
    packet = {
        "schema": EVIDENCE_SCHEMA,
        "run_id": run_id,
        "claim": claim,
        "evidence_refs": evidence_refs,
        "environment": environment,
        "e_level": e_level,
        "artifact_hashes": artifact_hashes,
        "review_refs": review_refs or [],
    }
    packet["digest"] = packet_digest(packet)
    return packet


def packet_digest(packet: dict) -> str:
    body = {k: v for k, v in packet.items() if k != "digest"}
    return "sha256:" + _sha(canonical_json(body))


def validate_packet(packet: dict) -> None:
    _require(isinstance(packet, dict), "packet must be an object")
    for key in ("schema", "run_id", "claim", "evidence_refs", "environment",
                "e_level", "artifact_hashes", "review_refs", "digest"):
        _require(key in packet, f"packet missing {key}")
    _require(packet["schema"] == EVIDENCE_SCHEMA, "unsupported evidence schema")
    _require(packet["e_level"] in E_LEVELS, "invalid E-level")
    _require(isinstance(packet["evidence_refs"], list) and packet["evidence_refs"], "evidence refs required")
    _require(isinstance(packet["artifact_hashes"], dict) and packet["artifact_hashes"], "artifact hashes required")
    _require(isinstance(packet["environment"], dict) and packet["environment"], "environment required")
    _require(packet_digest(packet) == packet["digest"], "evidence digest mismatch")


def gap_check(packet: dict, required_refs) -> dict:
    validate_packet(packet)
    have = set(packet["evidence_refs"])
    missing = [r for r in required_refs if r not in have]
    return {"ok": not missing, "missing": missing}


class EffectLedger:
    def __init__(self, path):
        self.path = Path(path)
        self._records = []
        self._by_id = {}
        if self.path.exists():
            for line_no, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    eid = rec["effect_id"]
                except Exception as exc:
                    raise EvidenceError(f"corrupt effect ledger line {line_no}") from exc
                if eid in self._by_id:
                    raise EvidenceError("duplicate effect id in ledger")
                self._records.append(rec)
                self._by_id[eid] = rec

    def append(self, effect_id: str, kind: str, status: str = "emitted", ref: str | None = None) -> dict:
        if effect_id in self._by_id:
            rec = self._by_id[effect_id]
            if rec["kind"] == kind and rec["status"] == status and rec.get("ref") == ref:
                return rec
            raise EvidenceError("duplicate effect id with different content")
        rec = {"effect_id": effect_id, "kind": kind, "status": status, "ref": ref}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
        self._records.append(rec)
        self._by_id[effect_id] = rec
        return rec

    def effects(self) -> list[dict]:
        return list(self._records)


def reconcile(checkpoint_effects, ledger_effects) -> dict:
    checkpoint = {e["effect_id"] for e in checkpoint_effects}
    emitted = [e for e in ledger_effects if e.get("status") == "emitted" and e["effect_id"] not in checkpoint]
    return {"ok": not emitted, "emitted_not_in_checkpoint": emitted,
            "note": "emitted effects are never silently discarded"}


class RecoveryController:
    STATES = {"detected", "isolated", "replaying", "verified", "resumed", "degraded", "incident"}

    def __init__(self):
        self.state = "detected"

    def isolate(self) -> str:
        _require(self.state == "detected", "recovery not detected")
        self.state = "isolated"
        return self.state

    def replay(self) -> str:
        _require(self.state == "isolated", "recovery not isolated")
        self.state = "replaying"
        return self.state

    def verify(self, *, state_digest_ok: bool, effects_reconciled: bool, lease_valid: bool) -> str:
        _require(self.state == "replaying", "recovery not replaying")
        if state_digest_ok and effects_reconciled and lease_valid:
            self.state = "verified"
        else:
            self.state = "incident"
        return self.state

    def resume(self) -> str:
        _require(self.state == "verified", "recovery not verified")
        self.state = "resumed"
        return self.state

    def degrade(self) -> str:
        self.state = "degraded"
        return self.state
