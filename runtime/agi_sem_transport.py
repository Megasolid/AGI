#!/usr/bin/env python3
"""E2 P3: canonical JSON Schema validation + authenticated transport harness.

Additive, stdlib-only. This is an in-process two-endpoint harness and a minimal
JSON-Schema subset validator; it is not a production transport or a security
proof. Authentication uses an injected signer/verifier; no private key here.

COMMIT remains semantic-only. No authority, consent, grant or execution.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import typing

from agi_sem import SemError, SemSession, canonical_json, validate_message

AUTH_SCHEMA = "agi.sem.auth/0.1"
AUTH_REQUIRED = ("schema", "alg", "key_id", "payload_sha256", "signature_b64")
_SCHEMA_PATH = pathlib.Path(__file__).with_name("schemas") / "agi.sem-0.2.schema.json"
with _SCHEMA_PATH.open(encoding="utf-8") as _f:
    MESSAGE_SCHEMA = json.load(_f)

_TYPES = {
    "object": dict, "array": list, "string": str, "integer": int,
    "number": (int, float), "boolean": bool, "null": type(None),
}


class TransportError(ValueError):
    """Schema/auth/binding violation; callers must fail closed."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise TransportError(msg)


def validate_json_schema(instance, schema, path: str = "$") -> None:
    """Validate the JSON-Schema subset used by agi.sem (fail closed)."""
    if schema is True:
        return
    if schema is False:
        raise TransportError(f"{path}: schema false")
    typ = schema.get("type")
    if typ is not None:
        types = typ if isinstance(typ, list) else [typ]
        ok = False
        for t in types:
            py = _TYPES.get(t)
            if py is None:
                continue
            if t == "integer" and isinstance(instance, bool):
                continue
            if isinstance(instance, py):
                ok = True
                break
        _require(ok, f"{path}: expected type {typ}")
    if "const" in schema:
        _require(instance == schema["const"], f"{path}: const mismatch")
    if "enum" in schema:
        _require(instance in schema["enum"], f"{path}: enum violation")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            _require(key in instance, f"{path}: missing {key}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                _require(key in props, f"{path}: additional property {key}")
        for key, sub in props.items():
            if key in instance:
                validate_json_schema(instance[key], sub, f"{path}.{key}")
    if isinstance(instance, list):
        items = schema.get("items")
        if items is not None:
            for i, value in enumerate(instance):
                validate_json_schema(value, items, f"{path}[{i}]")
    if isinstance(instance, str):
        if "minLength" in schema:
            _require(len(instance) >= schema["minLength"], f"{path}: minLength")
        if "pattern" in schema:
            _require(re.search(schema["pattern"], instance) is not None, f"{path}: pattern")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema:
            _require(instance >= schema["minimum"], f"{path}: minimum")


def validate_message_schema(message: dict) -> None:
    validate_json_schema(message, MESSAGE_SCHEMA)
    validate_message(message)  # semantic/expiry/digest/constraint checks too


def auth_payload(message: dict) -> bytes:
    return canonical_json({k: v for k, v in message.items() if k != "auth"})


def sign_message(message: dict, signer) -> dict:
    _require(callable(signer), "signer must be callable")
    payload = auth_payload(message)
    envelope = signer(payload)
    _require(isinstance(envelope, dict), "auth envelope must be an object")
    for key in AUTH_REQUIRED:
        _require(key in envelope, f"auth envelope missing {key}")
    _require(envelope["schema"] == AUTH_SCHEMA, "unsupported auth schema")
    _require(envelope["payload_sha256"] == hashlib.sha256(payload).hexdigest(), "auth payload hash mismatch")
    signed = dict(message)
    signed["auth"] = envelope
    return signed


def verify_message_auth(message: dict, verifier, *, expected_key_id: str | None = None) -> dict:
    _require("auth" in message, "message auth missing")
    env = message["auth"]
    _require(isinstance(env, dict), "auth envelope must be an object")
    for key in AUTH_REQUIRED:
        _require(key in env, f"auth envelope missing {key}")
    _require(env["schema"] == AUTH_SCHEMA, "unsupported auth schema")
    if expected_key_id is not None:
        _require(env.get("key_id") == expected_key_id, "auth key_id mismatch")
    payload = auth_payload(message)
    _require(env["payload_sha256"] == hashlib.sha256(payload).hexdigest(), "auth payload changed")
    _require(callable(verifier), "verifier must be callable")
    _require(verifier(payload, env) is True, "auth verification failed")
    return env


def verify_binding(message: dict, *, session_id: str, from_ref: str, to_ref: str) -> None:
    _require(message.get("session_id") == session_id, "session binding mismatch")
    _require(message.get("from_ref") == from_ref, "from_ref binding mismatch")
    _require(message.get("to_ref") == to_ref, "to_ref binding mismatch")


class SemChannel:
    """In-process two-endpoint transport harness over one semantic session."""

    def __init__(self, session_id: str, *, a_signer, a_verifier, b_signer, b_verifier,
                 key_id: str = "test-key"):
        self.session_id = session_id
        self.session = SemSession(session_id)
        self._signers = {"a": a_signer, "b": b_signer}
        self._verifiers = {"a": a_verifier, "b": b_verifier}
        self.key_id = key_id
        self._seen = set()

    def send(self, sender: str, message: dict) -> dict:
        _require(sender in self._signers, "unknown sender")
        _require(message.get("from_ref") == sender, "sender/from_ref mismatch")
        validate_json_schema(message, MESSAGE_SCHEMA)
        signed = sign_message(message, self._signers[sender])
        self._seen.add(signed["message_id"])
        return signed

    def deliver(self, receiver: str, signed: dict, *, now=None) -> dict:
        _require(receiver in self._verifiers, "unknown receiver")
        _require(signed.get("to_ref") == receiver, "receiver/to_ref mismatch")
        if signed.get("message_id") in getattr(self, "_delivered", set()):
            # Let the session provide idempotent/replay semantics, but do not re-auth twice.
            pass
        validate_message_schema(signed)
        sender = signed.get("from_ref")
        _require(sender in self._verifiers, f"no verifier for sender {sender}")
        verify_message_auth(signed, self._verifiers[sender], expected_key_id=self.key_id)
        verify_binding(signed, session_id=self.session_id,
                       from_ref=signed["from_ref"], to_ref=signed["to_ref"])
        result = self.session.receive(signed, now=now)
        self._delivered = getattr(self, "_delivered", set()) | {signed["message_id"]}
        return result

    def tick(self, *, now=None) -> str:
        return self.session.tick(now=now)
