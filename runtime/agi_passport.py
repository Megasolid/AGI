#!/usr/bin/env python3
"""agi_passport - Master-signed member passports for the Entelechy beta tree (beta.8).

A passport binds a member to the generation identity (gen_id / DNA sha) and to the member's seat public key, then is
signed with the local Master Ed25519 key. Passports live in `<sandbox>/state/passports/`; verification re-checks the
signature and cross-checks the seat public key and DNA digest. No passport is issued without a seat and a Master
ceremony.

CLI:
    python runtime/agi_passport.py --root <sandbox> --issue MEMBER [--note TEXT]
    python runtime/agi_passport.py --root <sandbox> --verify MEMBER
    python runtime/agi_passport.py --root <sandbox> --list
"""
import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agi_master  # noqa: E402
import agi_seats  # noqa: E402

SCHEMA = "agi-passport/1"


def _canonical_dna_sha(dna):
    body = {k: v for k, v in dna.items() if k != "digest_sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(member):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in str(member))


def _paths(root):
    return pathlib.Path(root).resolve() / "state" / "passports"


def issue(root, member, note="", actor="local"):
    root = pathlib.Path(root).resolve()
    member = str(member or "").strip()
    if not member:
        return {"ok": False, "error": "member required"}
    ident = agi_master.identity(root)
    if not ident.get("ok"):
        return {"ok": False, "error": "master ceremony required before issuing passports"}
    dna = json.loads((root / "core" / "dna.v4.json").read_text(encoding="utf-8"))
    seats = agi_seats.Seats(root).status().get("seats", [])
    seat = next((s for s in seats if s.get("member") == member), None)
    if not seat:
        return {"ok": False, "error": "member %r has no seat; enroll a device key first" % member}
    pub = ident["ident"]
    payload = {"schema": SCHEMA, "member": member,
               "generation": dna.get("generation", {}).get("name"),
               "gen_id": dna.get("generation", {}).get("gen_id"),
               "dna_version": dna.get("generation", {}).get("dna_version"),
               "dna_sha256": _canonical_dna_sha(dna),
               "dna_signed_sha256": dna.get("digest_sha256"),
               "seat_id": seat.get("seat_id"), "seat_mode": seat.get("mode"),
               "seat_public_key": seat.get("public_key") or seat.get("key_sha256"),
               "issuer": {"algo": "ed25519", "public_key": pub.get("public_key"),
                          "fingerprint": pub.get("fingerprint")},
               "issued_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(
                   timespec="seconds"),
               "note": str(note or "")}
    outdir = _paths(root)
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / (_slug(member) + ".json")
    p.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    sig = agi_master.sign_file(root, p)
    if not sig.get("ok"):
        return {"ok": False, "error": "master signing failed: %s" % sig.get("error")}
    audit = _audit_append(root, {"event": "passport_issued", "member": member, "actor": str(actor or "local"),
                                 "passport": p.name, "passport_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                 "algos": sig.get("algos"), "gen_id": payload["gen_id"], "note": str(note or "")})
    return {"ok": True, "schema": SCHEMA, "member": member, "passport": str(p), "signature": sig.get("sig_file"),
            "passport_sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "gen_id": payload["gen_id"],
            "dna_sha256": payload["dna_sha256"], "issuer_fingerprint": pub.get("fingerprint"),
            "algos": sig.get("algos"), "audit_seq": audit.get("seq")}


def _audit_path(root):
    return pathlib.Path(root).resolve() / "state" / "audit.jsonl"


def _audit_append(root, entry):
    p = _audit_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    seq = 1
    if p.is_file():
        try:
            seq = sum(1 for _ in p.open("r", encoding="utf-8")) + 1
        except Exception:
            seq = 1
    rec = {"seq": seq, "ts": __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat(timespec="seconds"), **entry}
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def list_audit(root, limit=50):
    p = _audit_path(root)
    rows = []
    if p.is_file():
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return {"ok": True, "schema": "agi-audit/1", "events": rows[-int(limit):], "count": len(rows),
            "note": "append-only issuance audit; seq is monotonic per sandbox"}


def verify(root, member):
    root = pathlib.Path(root).resolve()
    p = _paths(root) / (_slug(member) + ".json")
    if not p.is_file():
        return {"ok": False, "error": "no passport for %r" % member}
    payload = json.loads(p.read_text(encoding="utf-8"))
    sigpath = str(p) + ".master.sig"
    if not pathlib.Path(sigpath).is_file():
        return {"ok": False, "error": "passport signature missing"}
    mv = agi_master.verify_file(root, p, sigpath)
    if not mv.get("ok"):
        return {"ok": False, "error": "signature invalid: %s" % mv.get("error")}
    dna = json.loads((root / "core" / "dna.v4.json").read_text(encoding="utf-8"))
    ident = agi_master.identity(root)
    checks = {"gen_id_matches": payload.get("gen_id") == dna.get("generation", {}).get("gen_id"),
              "dna_sha_matches": payload.get("dna_sha256") == _canonical_dna_sha(dna),
              "issuer_is_local_master": payload.get("issuer", {}).get("public_key") ==
                                        (ident.get("ident") or {}).get("public_key"),
              "member_matches_file": payload.get("member") == member}
    seats = agi_seats.Seats(root).status().get("seats", [])
    seat = next((s for s in seats if s.get("member") == member), None)
    if seat:
        checks["seat_public_key_matches"] = (payload.get("seat_public_key") ==
                                             (seat.get("public_key") or seat.get("key_sha256")))
    return {"ok": all(checks.values()), "schema": SCHEMA, "member": member, "checks": checks,
            "passport": str(p), "gen_id": payload.get("gen_id"),
            "signed_at": payload.get("issued_at")}


def list_passports(root):
    root = pathlib.Path(root).resolve()
    out = []
    for p in sorted(_paths(root).glob("*.json")):
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        v = verify(root, payload.get("member", ""))
        out.append({"member": payload.get("member"), "gen_id": payload.get("gen_id"),
                    "verified": v.get("ok"), "file": str(p)})
    return {"ok": True, "schema": SCHEMA, "passports": out, "count": len(out),
            "note": "passports are Master-signed; verification cross-checks seat + DNA"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Master-signed passports for the beta tree (beta.8)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--issue", metavar="MEMBER")
    ap.add_argument("--verify", metavar="MEMBER")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    if a.issue:
        r = issue(a.root, a.issue, a.note)
    elif a.verify:
        r = verify(a.root, a.verify)
    elif a.audit:
        r = list_audit(a.root)
    else:
        r = list_passports(a.root)
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
