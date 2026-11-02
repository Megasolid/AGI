#!/usr/bin/env python3
"""AGI v4.1-E E2 `agi.sem/0.2` semantic protocol primitives.

Semantic-only: this module carries intent, context references, constraint sets,
receipts, verification outcomes and bounded correction. It has **no** identity,
grant, consent, authorization or execution operation. `COMMIT` changes semantic
state only; it never authorizes an effect.

Stdlib only; no network, credentials or execution.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone

SEM_SCHEMA = "agi.sem/0.2"
MESSAGE_TYPES = frozenset({
    "HELLO", "HELLO_ACK", "CAPABILITIES", "INTENT", "CONTEXT_REF", "ACK",
    "SEMANTIC_RECEIPT", "CHALLENGE", "CLARIFY", "CORRECTION", "COMMIT",
    "RESULT", "VERIFY", "VERIFIED", "REJECT", "ABORT", "SYNC", "CLOSE",
})
TERMINAL = frozenset({"REJECTED", "ABORTED", "CLOSED"})
HARD_KINDS = frozenset({"MUST", "MUST_NOT"})
VERDICTS = frozenset({"PASS", "UNCERTAIN", "FAIL"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class SemError(ValueError):
    """Protocol violation; callers must fail closed."""


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now(now=None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, str):
        return _parse_iso(now, "now")
    return now


def _parse_iso(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise SemError(f"{field} required")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SemError(f"{field} is not ISO-8601") from exc
    if dt.tzinfo is None:
        raise SemError(f"{field} must include a timezone")
    return dt


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SemError(msg)


def constraint_digest(constraint: dict) -> str:
    return "sha256:" + sha256_hex(canonical_json({k: v for k, v in constraint.items() if k != "digest"}))


def validate_constraints(constraints) -> None:
    _require(isinstance(constraints, list), "constraints must be a list")
    _require(len(constraints) <= 64, "too many constraints")
    seen = set()
    for c in constraints:
        _require(isinstance(c, dict), "constraint must be an object")
        for key in ("id", "kind", "text", "machine_check", "source", "digest", "enforcement"):
            _require(key in c, f"constraint missing {key}")
        _require(isinstance(c["id"], str) and c["id"], "constraint id required")
        _require(c["id"] not in seen, f"duplicate constraint id {c['id']}")
        seen.add(c["id"])
        _require(c["kind"] in HARD_KINDS | {"MAY"}, "invalid constraint kind")
        _require(isinstance(c["machine_check"], str) and c["machine_check"], "machine_check required")
        _require(isinstance(c["digest"], str) and c["digest"].startswith("sha256:"), "constraint digest required")
        _require(constraint_digest(c) == c["digest"], f"constraint digest mismatch: {c['id']}")


def check_constraints(constraints, checker) -> dict:
    """Deterministic hard-constraint check; any missing/false check is a FAIL."""
    validate_constraints(constraints)
    _require(callable(checker), "checker must be callable")
    results = []
    ok = True
    for c in constraints:
        if c["kind"] not in HARD_KINDS:
            continue
        try:
            passed = checker(c["machine_check"], c.get("params") or {}) is True
        except Exception:
            passed = False
        results.append({"id": c["id"], "check": c["machine_check"], "passed": passed})
        if not passed:
            ok = False
    return {"ok": ok, "results": results}


def make_message(*, message_type: str, session_id: str, message_id: str, sequence: int,
                 from_ref: str, to_ref: str, body: dict | None = None,
                 in_reply_to: str | None = None, constraints=None,
                 context_refs=None, uncertainty=None, evidence_refs=None,
                 ts: str | None = None, expires_at: str | None = None) -> dict:
    _require(message_type in MESSAGE_TYPES, f"unknown message type: {message_type}")
    now = datetime.now(timezone.utc)
    return {
        "schema": SEM_SCHEMA,
        "session_id": session_id,
        "message_id": message_id,
        "sequence": int(sequence),
        "in_reply_to": in_reply_to,
        "type": message_type,
        "from_ref": from_ref,
        "to_ref": to_ref,
        "ts": ts or now.isoformat(),
        "expires_at": expires_at or (now + timedelta(minutes=15)).isoformat(),
        "context_refs": context_refs or [],
        "constraints": constraints or [],
        "body": body or {},
        "uncertainty": uncertainty or {"state": "known", "reason": None},
        "evidence_refs": evidence_refs or [],
    }


def message_digest(message: dict) -> str:
    return "sha256:" + sha256_hex(canonical_json(message))


def validate_message(message: dict, *, now=None) -> None:
    _require(isinstance(message, dict), "message must be an object")
    for key in ("schema", "session_id", "message_id", "sequence", "type", "from_ref", "to_ref",
                "ts", "expires_at", "context_refs", "constraints", "body", "uncertainty", "evidence_refs"):
        _require(key in message, f"message missing {key}")
    _require(message["schema"] == SEM_SCHEMA, "unsupported sem schema")
    _require(message["type"] in MESSAGE_TYPES, "unknown message type")
    _require(isinstance(message["sequence"], int) and message["sequence"] >= 1, "sequence must be >= 1")
    _require(isinstance(message["from_ref"], str) and message["from_ref"], "from_ref required")
    _require(isinstance(message["to_ref"], str) and message["to_ref"], "to_ref required")
    _require(_parse_iso(message["expires_at"], "expires_at") > _now(now), "message expired")
    _require(message["uncertainty"].get("state") in {"known", "uncertain", "unknown"}, "invalid uncertainty")
    if message["constraints"]:
        validate_constraints(message["constraints"])


def validate_receipt(receipt: dict, *, intent_goal: str, constraints) -> None:
    _require(isinstance(receipt, dict), "receipt must be an object")
    for key in ("own_words", "constraint_check", "assumptions", "questions",
                "context_used", "probe_answer", "confidence"):
        _require(key in receipt, f"receipt missing {key}")
    _require(isinstance(receipt["own_words"], str) and receipt["own_words"].strip(), "own_words required")
    _require(receipt["own_words"].strip() != intent_goal.strip(), "receipt is a copy of sender intent")
    _require(isinstance(receipt["probe_answer"], str) and receipt["probe_answer"].strip(), "probe_answer required")
    _require(isinstance(receipt["constraint_check"], list), "constraint_check must be a list")
    checks = {c.get("id"): c for c in receipt["constraint_check"] if isinstance(c, dict)}
    for c in constraints:
        if c["kind"] in HARD_KINDS:
            _require(c["id"] in checks, f"hard constraint not checked: {c['id']}")
            _require(checks[c["id"]].get("preserved") is True, f"hard constraint not preserved: {c['id']}")
    _require(isinstance(receipt["context_used"], list), "context_used must be a list")
    _require(isinstance(receipt["assumptions"], list), "assumptions must be a list")
    _require(isinstance(receipt["questions"], list), "questions must be a list")


def verify_semantics(receipt: dict, *, intent_goal: str, constraints, checker,
                     verifier_ref: str, sender_ref: str, receiver_ref: str,
                     semantic_verifier=None) -> dict:
    """Deterministic constraint check first, then independent semantic review."""
    _require(verifier_ref not in {sender_ref, receiver_ref}, "verifier must be independent of sender/receiver")
    validate_receipt(receipt, intent_goal=intent_goal, constraints=constraints)
    hard = check_constraints(constraints, checker)
    if not hard["ok"]:
        return {"result": "FAIL", "reason": "hard_constraint_failed", "hard": hard, "semantic": None}
    if semantic_verifier is None:
        return {"result": "UNCERTAIN", "reason": "independent_verifier_unavailable", "hard": hard, "semantic": None}
    verdict = semantic_verifier(receipt, intent_goal)
    _require(verdict in VERDICTS, "semantic verifier returned invalid verdict")
    return {"result": verdict, "reason": "ok" if verdict == "PASS" else "semantic_review", "hard": hard, "semantic": verdict}


class SemSession:
    """Single-session state machine. Semantic only; no authorize/execute method."""

    ALLOWED = {
        "INIT": {"HELLO"},
        "GREETING": {"HELLO_ACK"},
        "NEGOTIATED": {"CAPABILITIES"},
        "IDLE": {"INTENT", "CLOSE", "SYNC"},
        "INTENT_SENT": {"SEMANTIC_RECEIPT", "REJECT", "ABORT"},
        "INTERPRETED": {"CHALLENGE", "SEMANTIC_RECEIPT", "CLARIFY", "CORRECTION", "COMMIT", "REJECT", "ABORT", "SYNC"},
        "CHALLENGE_PENDING": {"CLARIFY", "CORRECTION", "REJECT", "ABORT"},
        "COMMITTED": {"RESULT", "REJECT", "ABORT"},
        "RESULT_SENT": {"VERIFY", "SYNC", "REJECT", "ABORT"},
        "VERIFYING": {"VERIFIED", "REJECT", "ABORT"},
        "VERIFIED": {"CLOSE", "SYNC"},
        "REJECTED": {"CLOSE"},
        "ABORTED": {"CLOSE"},
        "CLOSED": set(),
    }

    def __init__(self, session_id: str, *, idle_timeout_s: int = 900):
        self.session_id = session_id
        self.state = "INIT"
        self.idle_timeout_s = idle_timeout_s
        self.last_activity = datetime.now(timezone.utc)
        self._seq = {}
        self._seen = {}
        self.correction_count = 0
        self.intent = None
        self.intent_goal = None
        self.constraints = []
        self.receipt = None
        self.verification = None
        self.commits = 0

    def receive(self, message: dict, *, now=None) -> dict:
        validate_message(message, now=now)
        _require(message["session_id"] == self.session_id, "session mismatch")
        _require(self.state not in TERMINAL, "session is terminal")
        current = _now(now)
        digest = message_digest(message)
        mid = message["message_id"]
        if mid in self._seen:
            if self._seen[mid] == digest:
                return {"status": "idempotent", "state": self.state}
            raise SemError("replay: duplicate message_id with different content")
        sender = message["from_ref"]
        expected = self._seq.get(sender, 1)
        _require(message["sequence"] == expected, f"sequence gap: expected {expected}")
        mtype = message["type"]
        if mtype in {"ABORT", "REJECT"}:
            self.state = "ABORTED" if mtype == "ABORT" else "REJECTED"
            self._seq[sender] = expected + 1
            self._seen[mid] = digest
            self.last_activity = current
            return {"status": "accepted", "state": self.state, "type": mtype}
        if mtype in {"ACK", "CONTEXT_REF"}:
            self._seq[sender] = expected + 1
            self._seen[mid] = digest
            self.last_activity = current
            return {"status": "accepted", "state": self.state, "type": mtype}
        allowed = self.ALLOWED.get(self.state, set())
        _require(message["type"] in allowed, f"state_violation: {message['type']} in {self.state}")
        if mtype == "HELLO":
            body = message["body"]
            _require(isinstance(body.get("min_version"), str) and isinstance(body.get("max_version"), str),
                     "HELLO versions required")
            if body["max_version"] < "0.2" or body["min_version"] > "0.2":
                raise SemError("version downgrade/no overlap")
            self.state = "GREETING"
        elif mtype == "HELLO_ACK":
            _require(message["body"].get("version") == "0.2", "HELLO_ACK version mismatch")
            self.state = "NEGOTIATED"
        elif mtype == "CAPABILITIES":
            _require(isinstance(message["body"].get("classes"), list), "CAPABILITIES classes required")
            self.state = "IDLE"
        elif mtype == "INTENT":
            self.intent = message["body"]
            self.intent_goal = str(message["body"].get("goal") or "")
            _require(bool(self.intent_goal), "INTENT goal required")
            self.constraints = message["constraints"]
            validate_constraints(self.constraints)
            self.state = "INTENT_SENT"
        elif mtype == "SEMANTIC_RECEIPT":
            validate_receipt(message["body"], intent_goal=self.intent_goal, constraints=self.constraints)
            self.receipt = message["body"]
            self.state = "INTERPRETED"
        elif mtype == "CHALLENGE":
            _require(self.correction_count < 1, "correction budget exhausted")
            self.correction_count += 1
            self.state = "CHALLENGE_PENDING"
        elif mtype in {"CLARIFY", "CORRECTION"}:
            self.state = "INTERPRETED"
        elif mtype == "COMMIT":
            _require(self.receipt is not None, "COMMIT without receipt")
            # Semantic agreement only: this is not consent or authorization.
            self.commits += 1
            self.state = "COMMITTED"
        elif mtype == "RESULT":
            self.state = "RESULT_SENT"
        elif mtype == "VERIFY":
            self.state = "VERIFYING"
        elif mtype == "VERIFIED":
            self.verification = message["body"].get("result")
            _require(self.verification in VERDICTS, "invalid VERIFIED result")
            self.state = "VERIFIED" if self.verification != "FAIL" else "REJECTED"
        elif mtype == "REJECT":
            self.state = "REJECTED"
        elif mtype == "ABORT":
            self.state = "ABORTED"
        elif mtype == "CLOSE":
            self.state = "CLOSED"
        elif mtype == "SYNC":
            pass
        elif mtype in {"ACK", "CONTEXT_REF"}:
            pass
        self._seq[sender] = expected + 1
        self._seen[mid] = digest
        self.last_activity = current
        return {"status": "accepted", "state": self.state, "type": mtype}

    def tick(self, *, now=None) -> str:
        if self.state in TERMINAL:
            return self.state
        current = _now(now)
        if (current - self.last_activity).total_seconds() > self.idle_timeout_s:
            self.state = "ABORTED"
        return self.state

    # Intentionally absent: authorize(), execute(), grant(), consent().
