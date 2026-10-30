#!/usr/bin/env python3
"""agi_seats - device-key seat ceremony for AGI Entelechy (stdlib HMAC-SHA256, local-only).

A seat is a member's device key. Enrollment shows the key once; the runtime stores the seat secret (local DB) and
its SHA-256 display hash. Login is challenge-response: the seat computes HMAC-SHA256(key, "agi-seat-login/v1:member:nonce");
the nonce is single-use and expires. This is the beta.6 key ceremony for simulation seats; Ed25519/ML-DSA seats and
remote seat tools over the bridge are beta.7.

CLI:
    python runtime/agi_seats.py --root <sandbox> --enroll NAME
    python runtime/agi_seats.py --root <sandbox> --challenge NAME
    python runtime/agi_seats.py --root <sandbox> --login NAME NONCE PROOF
    python runtime/agi_seats.py --root <sandbox> --status
"""
import argparse
import hashlib
import hmac
import json
import pathlib
import secrets
import sqlite3
import sys
import time

SCHEMA = "agi-seat/1"
NONCE_TTL = 120


class Seats:
    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        self.db = self.root / "state" / "agi.db"
        if not self.db.is_file():
            raise FileNotFoundError("beta sandbox state/agi.db missing")
        con = self._con()
        con.executescript("""
          CREATE TABLE IF NOT EXISTS seats(seat_id TEXT PRIMARY KEY, member TEXT UNIQUE, key_secret TEXT,
                                           key_sha256 TEXT, created TEXT, last_seen TEXT, status TEXT);
          CREATE TABLE IF NOT EXISTS seat_challenges(member TEXT, nonce TEXT PRIMARY KEY, created REAL,
                                                     used INTEGER DEFAULT 0);
        """)
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
    def proof(key, member, nonce):
        return hmac.new(str(key).encode(), ("agi-seat-login/v1:%s:%s" % (member, nonce)).encode(),
                        hashlib.sha256).hexdigest()

    def enroll(self, member):
        member = str(member or "").strip()
        if not member:
            return {"ok": False, "error": "member name required"}
        con = self._con()
        row = con.execute("SELECT seat_id FROM seats WHERE member=?", (member,)).fetchone()
        if row:
            con.close()
            return {"ok": False, "error": "%r already has a seat (rotate requires a new ceremony, beta.7)" % member}
        key = secrets.token_urlsafe(32)
        seat_id = "seat-" + secrets.token_hex(6)
        con.execute("INSERT INTO seats(seat_id,member,key_secret,key_sha256,created,last_seen,status) "
                    "VALUES(?,?,?,?,?,?, 'enrolled')",
                    (seat_id, member, key, self.key_hash(key), time.strftime("%Y-%m-%dT%H:%M:%S"), None))
        con.commit()
        con.close()
        return {"ok": True, "schema": SCHEMA, "member": member, "seat_id": seat_id, "device_key": key,
                "key_sha256": self.key_hash(key),
                "note": "device key shown once; keep it on the device; only the hash is displayed"}

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
                "proof_rule": "HMAC-SHA256(device_key, 'agi-seat-login/v1:<member>:<nonce>')"}

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
        expected = self.proof(seat["key_secret"], member, nonce)
        if not hmac.compare_digest(str(proof), expected):
            con.close()
            return {"ok": False, "error": "proof does not match the device key"}
        con.execute("UPDATE seat_challenges SET used=1 WHERE nonce=?", (str(nonce),))
        con.execute("UPDATE seats SET status='active', last_seen=? WHERE member=?",
                    (time.strftime("%Y-%m-%dT%H:%M:%S"), str(member)))
        con.commit()
        con.close()
        return {"ok": True, "schema": SCHEMA, "member": member, "seat_id": seat["seat_id"],
                "status": "active", "nonce": nonce, "replay": "blocked"}

    def status(self):
        con = self._con()
        rows = con.execute("SELECT seat_id,member,key_sha256,created,last_seen,status FROM seats").fetchall()
        con.close()
        return {"ok": True, "schema": SCHEMA, "seats": [dict(r) for r in rows],
                "active": sum(1 for r in rows if r["status"] == "active"),
                "note": "no key material leaves the seat; only hashes/status are listed"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="AGI seat device-key ceremony (beta.6)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--enroll", metavar="MEMBER")
    ap.add_argument("--challenge", metavar="MEMBER")
    ap.add_argument("--login", nargs=3, metavar=("MEMBER", "NONCE", "PROOF"))
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)
    s = Seats(a.root)
    if a.enroll:
        r = s.enroll(a.enroll)
    elif a.challenge:
        r = s.challenge(a.challenge)
    elif a.login:
        r = s.login(*a.login)
    else:
        r = s.status()
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
