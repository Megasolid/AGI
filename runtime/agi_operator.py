#!/usr/bin/env python3
"""P5 Operator primitives: service lifecycle, monotonic guards, cancellation,
single-writer lease/epoch, approval bridge.

Additive, stdlib-only. Operator is a non-identity harness. These helpers do not
grant authority, consent or execution; approval is not authorization.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone


class OperatorError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise OperatorError(msg)


def _now(now=None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, str):
        try:
            dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        except ValueError as exc:
            raise OperatorError("invalid time") from exc
        _require(dt.tzinfo is not None, "time must include timezone")
        return dt
    return now


class ServiceRegistry:
    """Provider lifecycle: pending -> active -> draining -> removed, or failed."""

    def __init__(self):
        self._providers = {}

    def register(self, name: str, *, start, stop) -> dict:
        _require(name and name not in self._providers, "duplicate provider")
        _require(callable(start) and callable(stop), "start/stop must be callable")
        rec = {"name": name, "state": "pending", "start": start, "stop": stop}
        self._providers[name] = rec
        return rec

    def start(self, name: str) -> dict:
        rec = self._providers.get(name)
        _require(rec is not None, "unknown provider")
        _require(rec["state"] == "pending", "provider not pending")
        try:
            rec["start"]()
            rec["state"] = "active"
        except Exception:
            rec["state"] = "failed"
            raise
        return rec

    def drain(self, name: str) -> dict:
        rec = self._providers.get(name)
        _require(rec is not None, "unknown provider")
        _require(rec["state"] == "active", "provider not active")
        rec["state"] = "draining"
        return rec

    def stop(self, name: str) -> dict:
        rec = self._providers.get(name)
        _require(rec is not None, "unknown provider")
        _require(rec["state"] in {"active", "draining", "failed"}, "provider not stoppable")
        try:
            rec["stop"]()
            rec["state"] = "removed"
        except Exception:
            rec["state"] = "failed"
            raise
        return rec

    def state(self, name: str) -> str:
        rec = self._providers.get(name)
        _require(rec is not None, "unknown provider")
        return rec["state"]


class PolicyGate:
    """Monotonic deny: first deny wins; later guards cannot override it."""

    def __init__(self):
        self._guards = []

    def add_guard(self, guard) -> None:
        _require(callable(guard), "guard must be callable")
        self._guards.append(guard)

    def decide(self, request: dict) -> dict:
        for i, guard in enumerate(self._guards):
            try:
                result = guard(request)
            except Exception as exc:
                return {"result": "deny", "reason": f"guard_error:{type(exc).__name__}", "index": i}
            if result is False:
                return {"result": "deny", "reason": "guard_denied", "index": i}
            if isinstance(result, str) and result:
                return {"result": "deny", "reason": result, "index": i}
        return {"result": "allow", "reason": "ok"}


class CancellationController:
    STATES = {"idle", "requested", "accepted", "stopping", "quiesced", "recorded", "failed"}

    def __init__(self):
        self.state = "idle"
        self.effects = {}

    def request(self) -> str:
        _require(self.state == "idle", "cancel not idle")
        self.state = "requested"
        return self.state

    def accept(self) -> str:
        _require(self.state == "requested", "cancel not requested")
        self.state = "accepted"
        return self.state

    def stopping(self) -> str:
        _require(self.state == "accepted", "cancel not accepted")
        self.state = "stopping"
        return self.state

    def add_effect(self, effect_id: str) -> None:
        _require(self.state in {"stopping", "accepted"}, "effects only while cancelling")
        _require(effect_id not in self.effects, "duplicate effect")
        self.effects[effect_id] = {"stopped": False}

    def mark_stopped(self, effect_id: str) -> None:
        _require(effect_id in self.effects, "unknown effect")
        self.effects[effect_id]["stopped"] = True

    def quiesce(self) -> str:
        _require(self.state == "stopping", "cancel not stopping")
        _require(all(e["stopped"] for e in self.effects.values()), "effects not quiesced")
        self.state = "quiesced"
        return self.state

    def record(self) -> str:
        _require(self.state == "quiesced", "cancel not quiesced")
        self.state = "recorded"
        return self.state

    def fail(self, reason: str) -> str:
        self.state = "failed"
        self.reason = reason
        return self.state


class LeaseStore:
    """Single-writer lease with monotonically increasing epoch per branch."""

    def __init__(self):
        self._leases = {}

    def acquire(self, branch_id: str, operator: str, *, epoch: int, ttl_s: int = 14400, now=None) -> dict:
        current = _now(now)
        existing = self._leases.get(branch_id)
        if existing and not existing["released"] and existing["expires_at"] > current:
            raise OperatorError("branch already leased (split-brain refused)")
        if existing and epoch <= existing["epoch"]:
            raise OperatorError("epoch must increase")
        rec = {"branch_id": branch_id, "operator": operator, "epoch": int(epoch),
               "expires_at": current + timedelta(seconds=int(ttl_s)), "released": False}
        self._leases[branch_id] = rec
        return dict(rec)

    def check_write(self, branch_id: str, epoch: int, *, now=None) -> dict:
        rec = self._leases.get(branch_id)
        _require(rec is not None, "no lease")
        _require(not rec["released"], "lease released")
        _require(rec["epoch"] == int(epoch), "stale epoch")
        _require(rec["expires_at"] > _now(now), "lease expired")
        return rec

    def release(self, branch_id: str, *, operator: str, epoch: int) -> None:
        rec = self._leases.get(branch_id)
        _require(rec is not None, "no lease")
        _require(rec["operator"] == operator and rec["epoch"] == int(epoch), "lease ownership mismatch")
        rec["released"] = True


class ApprovalBridge:
    """Client approval request/record. It has no grant/authorize method."""

    def __init__(self):
        self._requests = {}

    def request(self, operation: str, reason: str = "") -> dict:
        _require(isinstance(operation, str) and operation, "operation required")
        approval_id = "appr-" + secrets.token_hex(8)
        rec = {"approval_id": approval_id, "operation": operation, "reason": reason, "status": "pending"}
        self._requests[approval_id] = rec
        return dict(rec)

    def record_client_decision(self, approval_id: str, decision: str) -> dict:
        rec = self._requests.get(approval_id)
        _require(rec is not None, "unknown approval")
        _require(decision in {"accept", "decline", "cancel"}, "invalid decision")
        rec["status"] = decision
        return {"approval_id": approval_id, "decision": decision,
                "note": "client decision is not consent or authorization"}
