#!/usr/bin/env python3
"""P4 endpoint roles + durable replay channel.

Role policy is a semantic message-type restriction: initiator may propose,
responder may interpret/return results, verifier may return verification. It
does not grant authority, consent or execution. Durable replay protection uses
an append-only store; cross-session replay is rejected by session binding.
"""
from __future__ import annotations

import hashlib

from agi_sem_replay import ReplayError, ReplayStore
from agi_sem_transport import (
    SemChannel, TransportError, auth_payload, validate_message_schema, verify_binding,
    verify_message_auth,
)

ROLE_TYPES = {
    "initiator": {"HELLO", "CAPABILITIES", "INTENT", "CHALLENGE", "COMMIT", "VERIFY",
                  "CLOSE", "REJECT", "ABORT", "ACK", "CONTEXT_REF", "SYNC"},
    "responder": {"HELLO_ACK", "CAPABILITIES", "SEMANTIC_RECEIPT", "CLARIFY",
                  "CORRECTION", "RESULT", "CLOSE", "REJECT", "ABORT", "ACK",
                  "CONTEXT_REF", "SYNC"},
    "verifier": {"VERIFIED", "REJECT", "ABORT", "ACK", "CLOSE"},
}


class RoleError(TransportError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise RoleError(msg)


class RoleChannel(SemChannel):
    def __init__(self, session_id: str, *, roles: dict, **kwargs):
        super().__init__(session_id, **kwargs)
        _require(isinstance(roles, dict) and roles, "roles required")
        for endpoint, role in roles.items():
            _require(role in ROLE_TYPES, f"unknown role {role}")
            _require(endpoint in self._signers and endpoint in self._verifiers,
                     f"endpoint {endpoint} lacks signer/verifier")
        _require(len(set(roles)) == len(roles), "duplicate endpoints")
        self.roles = dict(roles)

    def send(self, sender: str, message: dict) -> dict:
        _require(sender in self.roles, "unknown endpoint")
        _require(message.get("from_ref") == sender, "sender/from_ref mismatch")
        _require(message.get("type") in ROLE_TYPES[self.roles[sender]],
                 f"role_violation: {self.roles[sender]} may not send {message.get('type')}")
        return super().send(sender, message)

    def deliver(self, receiver: str, signed: dict, *, now=None) -> dict:
        _require(receiver in self.roles, "unknown receiver")
        sender = signed.get("from_ref")
        _require(sender in self.roles, "unknown sender endpoint")
        _require(signed.get("to_ref") == receiver, "receiver/to_ref mismatch")
        _require(signed.get("type") in ROLE_TYPES[self.roles[sender]],
                 f"role_violation: {self.roles[sender]} may not send {signed.get('type')}")
        return super().deliver(receiver, signed, now=now)


class DurableChannel(RoleChannel):
    """Role-enforced channel with a durable replay store (JSONL)."""

    def __init__(self, session_id: str, *, replay_path, **kwargs):
        super().__init__(session_id, **kwargs)
        self.replay = ReplayStore(replay_path)

    def deliver(self, receiver: str, signed: dict, *, now=None) -> dict:
        _require(receiver in self.roles, "unknown receiver")
        sender = signed.get("from_ref")
        _require(sender in self.roles, "unknown sender endpoint")
        _require(signed.get("to_ref") == receiver, "receiver/to_ref mismatch")
        validate_message_schema(signed)
        verify_message_auth(signed, self._verifiers[sender], expected_key_id=self.key_id)
        verify_binding(signed, session_id=self.session_id,
                       from_ref=signed["from_ref"], to_ref=signed["to_ref"])
        digest = hashlib.sha256(auth_payload(signed)).hexdigest()
        status = self.replay.check_and_record(self.session_id, signed["message_id"], digest)
        if status == "idempotent":
            return {"status": "idempotent", "state": self.session.state, "replay": status}
        result = super().deliver(receiver, signed, now=now)
        result["replay"] = status
        return result
