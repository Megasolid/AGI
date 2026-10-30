#!/usr/bin/env python3
"""agi_master - local Master key ceremony for AGI Entelechy beta.7 (Ed25519).

Generates a local Master Ed25519 keypair, writes the private key to `<sandbox>/state/master.key` (best-effort 0600)
and the public identity to `state/master_pub.json`, then signs/verifies files (passports, seeds, release manifests).

This is a LOCAL beta ceremony: the private key never leaves the sandbox file system; there is no HSM and no
multi-device key yet. Requires `cryptography` (announced at install time).

CLI:
    python runtime/agi_master.py --root <sandbox> --ceremony
    python runtime/agi_master.py --root <sandbox> --sign FILE [--out SIGFILE]
    python runtime/agi_master.py --root <sandbox> --verify FILE SIGFILE
    python runtime/agi_master.py --root <sandbox> --ident
"""
import argparse
import base64
import hashlib
import json
import os
import pathlib
import sys

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover
    HAVE_CRYPTO = False

SCHEMA = "agi-master/1"


def _paths(root):
    st = pathlib.Path(root).resolve() / "state"
    return st / "master.key", st / "master_pub.json"


def identity(root):
    _, pubp = _paths(root)
    if not pubp.is_file():
        return {"ok": False, "error": "no master ceremony in this sandbox"}
    return {"ok": True, "ident": json.loads(pubp.read_text(encoding="utf-8"))}


def ceremony(root):
    if not HAVE_CRYPTO:
        return {"ok": False, "error": "cryptography not available; beta.7 Master ceremony needs Ed25519"}
    keyp, pubp = _paths(root)
    if keyp.exists() or pubp.exists():
        return {"ok": False, "error": "master ceremony already exists (refusing to overwrite)"}
    priv = Ed25519PrivateKey.generate()
    raw = priv.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                             serialization.NoEncryption())
    pub = priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    keyp.parent.mkdir(parents=True, exist_ok=True)
    keyp.write_bytes(base64.b64encode(raw))
    try:
        os.chmod(keyp, 0o600)
    except Exception:
        pass
    ident = {"schema": SCHEMA, "algo": "ed25519", "public_key": pub.hex(),
             "fingerprint": hashlib.sha256(pub).hexdigest()[:32], "created": __import__("datetime").datetime.now(
                 __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
             "note": "private key in state/master.key (local only); public identity here"}
    pubp.write_text(json.dumps(ident, indent=1), encoding="utf-8")
    return {"ok": True, "ident": ident, "private_key_file": str(keyp),
            "warning": "state/master.key is the Master root; back it up offline and never commit it"}


def sign_file(root, path, out=None):
    if not HAVE_CRYPTO:
        return {"ok": False, "error": "cryptography not available"}
    keyp, pubp = _paths(root)
    if not keyp.is_file():
        return {"ok": False, "error": "no master ceremony; run --ceremony first"}
    priv = Ed25519PrivateKey.from_private_bytes(base64.b64decode(keyp.read_bytes()))
    data = pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")
    sig = priv.sign(data)
    rec = {"schema": "agi-master-sig/1", "file": pathlib.Path(path).name,
           "sha256": hashlib.sha256(data).hexdigest(), "signature": base64.b64encode(sig).decode(),
           "public_key": json.loads(pubp.read_text(encoding="utf-8"))["public_key"], "algo": "ed25519"}
    out = pathlib.Path(out) if out else pathlib.Path(str(path) + ".master.sig")
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return {"ok": True, "sig_file": str(out), "sha256": rec["sha256"]}


def verify_file(root, path, sig_path):
    if not HAVE_CRYPTO:
        return {"ok": False, "error": "cryptography not available"}
    rec = json.loads(pathlib.Path(sig_path).read_text(encoding="utf-8"))
    data = pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(data).hexdigest() != rec.get("sha256"):
        return {"ok": False, "error": "sha256 mismatch"}
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(rec["public_key"])).verify(
            base64.b64decode(rec["signature"]), data)
    except Exception:
        return {"ok": False, "error": "signature invalid"}
    return {"ok": True, "file": pathlib.Path(path).name, "sha256": rec["sha256"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="AGI Master key ceremony (beta.7, Ed25519 local)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--ceremony", action="store_true")
    ap.add_argument("--sign", metavar="FILE")
    ap.add_argument("--out", default=None)
    ap.add_argument("--verify", nargs=2, metavar=("FILE", "SIG"))
    ap.add_argument("--ident", action="store_true")
    a = ap.parse_args(argv)
    if a.ceremony:
        r = ceremony(a.root)
    elif a.sign:
        r = sign_file(a.root, a.sign, a.out)
    elif a.verify:
        r = verify_file(a.root, *a.verify)
    else:
        r = identity(a.root)
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
