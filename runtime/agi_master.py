#!/usr/bin/env python3
"""agi_master - local Master key ceremony for AGI Entelechy beta.9 (Ed25519 + ML-DSA-65 dual signing).

Generates a local Master Ed25519 keypair and, when `cryptography` exposes ML-DSA (post-quantum), an ML-DSA-65
keypair as well. Private keys live in `state/master.key` (Ed25519 raw, best-effort 0600) and
`state/master_mldsa.key` (ML-DSA PKCS8 PEM); the public identity is `state/master_pub.json`. Files are signed with
both algorithms (dual signature) and verification requires both when present.

LOCAL beta ceremony: keys never leave the sandbox file system; no HSM, no multi-device key yet.

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
    serialization = None

try:  # post-quantum (cryptography >= 45 style module name)
    from cryptography.hazmat.primitives.asymmetric import mldsa
    HAVE_MLDSA = True
except Exception:  # pragma: no cover
    mldsa = None
    HAVE_MLDSA = False

SCHEMA = "agi-master/2"


def _paths(root):
    st = pathlib.Path(root).resolve() / "state"
    return st / "master.key", st / "master_mldsa.key", st / "master_pub.json"


def _fingerprint(data):
    return hashlib.sha256(data).hexdigest()[:32]


def identity(root):
    _, _, pubp = _paths(root)
    if not pubp.is_file():
        return {"ok": False, "error": "no master ceremony in this sandbox"}
    return {"ok": True, "ident": json.loads(pubp.read_text(encoding="utf-8"))}


def ceremony(root):
    if not HAVE_CRYPTO:
        return {"ok": False, "error": "cryptography not available; Master ceremony needs Ed25519"}
    keyp, mkeyp, pubp = _paths(root)
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
             "fingerprint": _fingerprint(pub),
             "created": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(
                 timespec="seconds"),
             "note": "private keys local only; this file is the public identity"}
    if HAVE_MLDSA:
        mp = mldsa.MLDSA65PrivateKey.generate()
        mpem = mp.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                serialization.NoEncryption())
        mkeyp.write_bytes(mpem)
        try:
            os.chmod(mkeyp, 0o600)
        except Exception:
            pass
        mpub = mp.public_key().public_bytes(serialization.Encoding.PEM,
                                            serialization.PublicFormat.SubjectPublicKeyInfo)
        ident["mldsa"] = {"algo": "ML-DSA-65", "public_key_pem": mpub.decode(),
                          "fingerprint": _fingerprint(mpub)}
    pubp.write_text(json.dumps(ident, indent=1), encoding="utf-8")
    return {"ok": True, "ident": ident, "private_key_file": str(keyp),
            "mldsa_private_key_file": str(mkeyp) if HAVE_MLDSA else None,
            "post_quantum": HAVE_MLDSA,
            "warning": "master.key / master_mldsa.key are the Master root; back them up offline and never commit"}


def _sign_mldsa(mkeyp, data):
    if not (HAVE_MLDSA and mkeyp.is_file()):
        return None
    priv = serialization.load_pem_private_key(mkeyp.read_bytes(), password=None)
    return base64.b64encode(priv.sign(data)).decode()


def sign_file(root, path, out=None):
    if not HAVE_CRYPTO:
        return {"ok": False, "error": "cryptography not available"}
    keyp, mkeyp, pubp = _paths(root)
    if not keyp.is_file():
        return {"ok": False, "error": "no master ceremony; run --ceremony first"}
    priv = Ed25519PrivateKey.from_private_bytes(base64.b64decode(keyp.read_bytes()))
    data = pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")
    rec = {"schema": "agi-master-sig/2", "file": pathlib.Path(path).name,
           "sha256": hashlib.sha256(data).hexdigest(), "algos": ["ed25519"],
           "signature": base64.b64encode(priv.sign(data)).decode(),
           "public_key": json.loads(pubp.read_text(encoding="utf-8"))["public_key"]}
    m_sig = _sign_mldsa(mkeyp, data)
    if m_sig:
        pub = json.loads(pubp.read_text(encoding="utf-8"))
        rec["algos"].append("ml-dsa-65")
        rec["mldsa_signature"] = m_sig
        rec["mldsa_public_key_pem"] = (pub.get("mldsa") or {}).get("public_key_pem")
    out = pathlib.Path(out) if out else pathlib.Path(str(path) + ".master.sig")
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return {"ok": True, "sig_file": str(out), "sha256": rec["sha256"], "algos": rec["algos"]}


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
        return {"ok": False, "error": "ed25519 signature invalid"}
    if rec.get("mldsa_signature"):
        if not HAVE_MLDSA:
            return {"ok": False, "error": "ML-DSA signature present but cryptography ML-DSA unavailable"}
        try:
            mpub = serialization.load_pem_public_key(rec["mldsa_public_key_pem"].encode())
            mpub.verify(base64.b64decode(rec["mldsa_signature"]), data)
        except Exception:
            return {"ok": False, "error": "ML-DSA signature invalid"}
    return {"ok": True, "file": pathlib.Path(path).name, "sha256": rec["sha256"],
            "algos": rec.get("algos") or ["ed25519"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="AGI Master key ceremony (beta.9: Ed25519 + ML-DSA-65)")
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
