#!/usr/bin/env python3
"""agi_seats - device-key seat ceremony for AGI Entelechy (beta.7: Ed25519 public-key seats + HMAC fallback).

A seat is a member device key. `ed25519` mode (default when `cryptography` is installed) generates the private key
on the device, stores only the PUBLIC key in the sandbox, and verifies a signature over the challenge. `hmac` mode is
the stdlib fallback (local secret stored) and is kept only for environments without `cryptography`.

Login is challenge-response; nonces are single-use and expire. Status never exposes key material.

CLI:
    python runtime/agi_seats.py --root <sandbox> --enroll NAME [--mode ed25519|hmac|auto]
    python runtime/agi_seats.py --root <sandbox> --challenge NAME
    python runtime/agi_seats.py --root <sandbox> --login NAME NONCE PROOF [--key DEVICE_KEY]
    python runtime/agi_seats.py --root <sandbox> --status
    python runtime/agi_seats.py --root <sandbox> --sign NAME NONCE --key DEVICE_KEY
"""
import argparse
import base64
import hashlib
import hmac
import json
import pathlib
import secrets
import sqlite3
import sys
import time

SCHEMA = "agi-seat/2"
NONCE_TTL = 120
PROOF_PREFIX = "agi-seat-login/v2:"

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover - stdlib fallback
    HAVE_CRYPTO = False


def challenge_message(member, nonce):
    return (PROOF_PREFIX + str(member) + ":" + str(nonce)).encode()


class Seats:
    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        self.db = self.root / "state" / "agi.db"
        if not self.db.is_file():
            raise FileNotFoundError("beta sandbox state/agi.db missing")
        con = self._con()
        con.executescript("""
          CREATE TABLE IF NOT EXISTS seats(seat_id TEXT PRIMARY KEY, member TEXT UNIQUE, key_secret TEXT,
                                           key_sha256 TEXT, created TEXT, last_seen TEXT, status TEXT,
                                           mode TEXT, public_key TEXT);
          CREATE TABLE IF NOT EXISTS seat_challenges(member TEXT, nonce TEXT PRIMARY KEY, created REAL,
                                                     used INTEGER DEFAULT 0);
        """)
        cols = {r[1] for r in con.execute("PRAGMA table_info(seats)").fetchall()}
        for col in ("mode", "public_key"):
            if col not in cols:
                con.execute("ALTER TABLE seats ADD COLUMN %s TEXT" % col)
        con.commit()
        con.close()

    def _con(self):
        con = sqlite3.connect(str(self.db))
        con.row_factory = sqlite3.Row
        return con

    @staticmethod
    def key_hash(key):
        return hashlib.sha256(("agi-seat-key/v1:" + str(key)).encode()).hexdigest()

    @staticmethod
    def hmac_proof(key, member, nonce):
        return hmac.new(str(key).encode(), challenge_message(member, nonce), hashlib.sha256).hexdigest()

    @staticmethod
    def sign_with_key(device_key, member, nonce):
        if HAVE_CRYPTO:
            priv = Ed25519PrivateKey.from_private_bytes(base64.b64decode(device_key))
            return base64.b64encode(priv.sign(challenge_message(member, nonce))).decode()
        return Seats.hmac_proof(device_key, member, nonce)

    def enroll(self, member, mode="auto"):
        member = str(member or "").strip()
        if not member:
            return {"ok": False, "error": "member name required"}
        mode = "ed25519" if (mode in ("auto", "ed25519") and HAVE_CRYPTO) else "hmac"
        con = self._con()
        row = con.execute("SELECT seat_id FROM seats WHERE member=?", (member,)).fetchone()
        if row:
            con.close()
            return {"ok": False, "error": "%r already has a seat (rotate requires a new ceremony, beta.7)" % member}
        seat_id = "seat-" + secrets.token_hex(6)
        key_secret = None
        if mode == "ed25519":
            priv = Ed25519PrivateKey.generate()
            device_key = base64.b64encode(priv.private_bytes(serialization.Encoding.Raw,
                                                             serialization.PrivateFormat.Raw,
                                                             serialization.NoEncryption())).decode()
            public_key = priv.public_key().public_bytes(serialization.Encoding.Raw,
                                                        serialization.PublicFormat.Raw).hex()
            key_hash = hashlib.sha256(bytes.fromhex(public_key)).hexdigest()
        else:
            device_key = secrets.token_urlsafe(32)
            key_secret = device_key
            public_key = None
            key_hash = self.key_hash(device_key)
        con.execute("INSERT INTO seats(seat_id,member,key_secret,key_sha256,created,last_seen,status,mode,public_key) "
                    "VALUES(?,?,?,?,?,?, 'enrolled', ?, ?)",
                    (seat_id, member, key_secret, key_hash, time.strftime("%Y-%m-%dT%H:%M:%S"), None, mode, public_key))
        con.commit()
        con.close()
        return {"ok": True, "schema": SCHEMA, "member": member, "seat_id": seat_id, "mode": mode,
                "device_key": device_key, "key_sha256": key_hash,
                "public_key": public_key,
                "note": "device key shown once; ed25519 keeps only the public key in the sandbox"}

    def challenge(self, member):
        con = self._con()
        row = con.execute("SELECT * FROM seats WHERE member=? AND status!='revoked'", (str(member),)).fetchone()
        if not row:
            con.close()
            return {"ok": False, "error": "no active seat for %r" % member}
        nonce = secrets.token_hex(16)
        con.execute("INSERT INTO seat_challenges(member,nonce,created,used) VALUES(?,?,?,0)",
                    (str(member), nonce, time.time()))
        con.commit()
        con.close()
        return {"ok": True, "schema": SCHEMA, "member": member, "nonce": nonce, "ttl_s": NONCE_TTL,
                "mode": row["mode"], "proof_rule": PROOF_PREFIX + "<member>:<nonce>"}

    def login(self, member, nonce, proof):
        con = self._con()
        seat = con.execute("SELECT * FROM seats WHERE member=?", (str(member),)).fetchone()
        ch = con.execute("SELECT * FROM seat_challenges WHERE nonce=?", (str(nonce),)).fetchone()
        if not seat or not ch:
            con.close()
            return {"ok": False, "error": "unknown seat or challenge"}
        if ch["used"]:
            con.close()
            return {"ok": False, "error": "challenge already used (replay blocked)"}
        if time.time() - float(ch["created"]) > NONCE_TTL:
            con.close()
            return {"ok": False, "error": "challenge expired"}
        mode = seat["mode"] or "hmac"
        if mode == "ed25519":
            ok = False
            if HAVE_CRYPTO and seat["public_key"]:
                try:
                    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(seat["public_key"]))
                    pub.verify(base64.b64decode(str(proof)), challenge_message(member, nonce))
                    ok = True
                except Exception:
                    ok = False
        else:
            ok = hmac.compare_digest(str(proof), self.hmac_proof(seat["key_secret"], member, nonce))
        if not ok:
            con.close()
            return {"ok": False, "error": "proof does not match the device key"}
        con.execute("UPDATE seat_challenges SET used=1 WHERE nonce=?", (str(nonce),))
        con.execute("UPDATE seats SET status='active', last_seen=? WHERE member=?",
                    (time.strftime("%Y-%m-%dT%H:%M:%S"), str(member)))
        con.commit()
        con.close()
        return {"ok": True, "schema": SCHEMA, "member": member, "seat_id": seat["seat_id"], "mode": mode,
                "status": "active", "nonce": nonce, "replay": "blocked"}

    def status(self):
        con = self._con()
        rows = con.execute("SELECT seat_id,member,key_sha256,created,last_seen,status,mode,public_key FROM seats").fetchall()
        con.close()
        return {"ok": True, "schema": SCHEMA, "seats": [dict(r) for r in rows],
                "active": sum(1 for r in rows if r["status"] == "active"),
                "mode_default": "ed25519" if HAVE_CRYPTO else "hmac",
                "note": "no key material leaves the seat; only hashes/status/public keys are listed"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="AGI seat device-key ceremony (beta.7: ed25519 + hmac fallback)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--enroll", metavar="MEMBER")
    ap.add_argument("--mode", default="auto")
    ap.add_argument("--challenge", metavar="MEMBER")
    ap.add_argument("--login", nargs=3, metavar=("MEMBER", "NONCE", "PROOF"))
    ap.add_argument("--key", default=None, help="device key to sign locally for --login/--sign")
    ap.add_argument("--sign", nargs=2, metavar=("MEMBER", "NONCE"))
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)
    s = Seats(a.root)
    if a.enroll:
        r = s.enroll(a.enroll, a.mode)
    elif a.challenge:
        r = s.challenge(a.challenge)
    elif a.sign:
        r = {"ok": True, "member": a.sign[0], "nonce": a.sign[1],
             "proof": s.sign_with_key(a.key, a.sign[0], a.sign[1])}
    elif a.login:
        member, nonce, proof = a.login
        if a.key and proof in ("-", "auto"):
            proof = s.sign_with_key(a.key, member, nonce)
        r = s.login(member, nonce, proof)
    else:
        r = s.status()
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
