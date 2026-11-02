#!/usr/bin/env python3
"""P4 cross-process auth verification (local subprocess; mock HMAC only).

This proves serialization/verification across a process boundary. It is not a
production transport, key distribution or ML-DSA implementation. No network.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

RUNTIME = pathlib.Path(__file__).resolve().parent

_CHILD = r'''
import base64, hashlib, hmac, json, os, sys
sys.path.insert(0, r"%s")
from agi_sem_transport import verify_message_auth
secret = bytes.fromhex(os.environ["AGI_TEST_SECRET_HEX"])
def verifier(payload, env):
    want = hmac.new(secret, payload, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode("ascii"), env.get("signature_b64", ""))
msg = json.load(sys.stdin)
try:
    verify_message_auth(msg, verifier, expected_key_id="test-key")
    print(json.dumps({"ok": True}))
except Exception as exc:
    print(json.dumps({"ok": False, "error": type(exc).__name__ + ": " + str(exc)[:200]}))
''' % str(RUNTIME)


def cross_process_verify(message: dict, secret: bytes, *, timeout: int = 15) -> dict:
    env = dict(os.environ)
    env["AGI_TEST_SECRET_HEX"] = secret.hex()
    proc = subprocess.run([sys.executable, "-c", _CHILD], input=json.dumps(message),
                          capture_output=True, text=True, timeout=timeout, env=env)
    if proc.returncode != 0:
        return {"ok": False, "error": f"child exit {proc.returncode}: {proc.stderr[-200:]}"}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "error": "child output unparsable"}
