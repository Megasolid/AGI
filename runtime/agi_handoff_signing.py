#!/usr/bin/env python3
"""E4 handoff/receipt signature interfaces.

The module defines the signed-artifact contract and replay guard but does NOT
hold a private key and does NOT implement ML-DSA itself. The caller injects a
real signer/verifier (for example the AGI device-key ML-DSA-65 tooling).

A signature authenticates the artifact and signer. It never grants authority,
consent or execution permission.
"""
from __future__ import annotations

import hashlib
import json

from agi_handoff import (HandoffError, canonical_json, handoff_digest,
                         receipt_digest, validate_handoff, validate_receipt)

SIG_SCHEMA = "agi-sig/1"
SIGNED_HANDOFF_SCHEMA = "agi.handoff.signed/0.1"


class SigningError(ValueError):
    """Signature envelope invalid, verifier failed, or replay detected."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SigningError(msg)


def _payload(handoff: dict) -> bytes:
    body = {k: v for k, v in handoff.items() if k != "signature"}
    return canonical_json(body)


def _validate_envelope(envelope: dict, payload: bytes) -> None:
    _require(isinstance(envelope, dict), "signature envelope must be an object")
    _require(envelope.get("schema") == SIG_SCHEMA, "unsupported signature schema")
    _require(isinstance(envelope.get("alg"), str) and envelope["alg"], "signature alg required")
    _require(isinstance(envelope.get("key_id"), str) and envelope["key_id"], "signature key_id required")
    _require(isinstance(envelope.get("signature_b64"), str) and envelope["signature_b64"], "signature_b64 required")
    _require(envelope.get("payload_sha256") == hashlib.sha256(payload).hexdigest(),
             "signature payload hash mismatch")


def sign_handoff(handoff: dict, signer) -> dict:
    """Attach an injected signer's envelope to a valid, nonce-bearing handoff."""
    validate_handoff(handoff)
    _require(isinstance(handoff.get("nonce"), str) and handoff["nonce"], "handoff nonce required for signing")
    _require(callable(signer), "signer must be callable")
    payload = _payload(handoff)
    envelope = signer(payload)
    _validate_envelope(envelope, payload)
    signed = dict(handoff)
    signed["signature"] = envelope
    return signed


def verify_signed_handoff(signed: dict, verifier, *, nonce_check=None) -> dict:
    """Validate handoff + signature envelope + injected verifier + replay nonce."""
    _require(isinstance(signed, dict), "signed handoff must be an object")
    _require("signature" in signed, "signature missing")
    validate_handoff(signed)
    _require(callable(verifier), "verifier must be callable")
    payload = _payload(signed)
    _validate_envelope(signed["signature"], payload)
    try:
        ok = verifier(payload, signed["signature"])
    except Exception as exc:
        raise SigningError(f"verifier failed: {type(exc).__name__}") from exc
    _require(ok is True, "signature verification failed")
    if nonce_check is not None:
        _require(callable(nonce_check), "nonce_check must be callable")
        _require(nonce_check(signed["nonce"]) is True, "replay: nonce already used")
    return signed


def sign_receipt(receipt: dict, handoff: dict, signer) -> dict:
    validate_receipt(receipt, handoff=handoff)
    _require(callable(signer), "signer must be callable")
    payload = canonical_json({k: v for k, v in receipt.items() if k != "signature"})
    envelope = signer(payload)
    _validate_envelope(envelope, payload)
    signed = dict(receipt)
    signed["signature"] = envelope
    return signed


def verify_signed_receipt(signed: dict, handoff: dict, verifier) -> dict:
    _require("signature" in signed, "receipt signature missing")
    validate_receipt(signed, handoff=handoff)
    payload = canonical_json({k: v for k, v in signed.items() if k != "signature"})
    _validate_envelope(signed["signature"], payload)
    _require(verifier(payload, signed["signature"]) is True, "receipt signature verification failed")
    return signed
