#!/usr/bin/env python3
"""agi_release - dual-signed release artifacts for the Entelechy beta tree (beta.10).

Signs release artifacts (DNA canonical JSON, the signed seed, release notes/manifests) with the local Master
Ed25519 + ML-DSA-65 keys, records the signatures in `<sandbox>/state/release_signatures.json`, and verifies them.
This extends post-quantum signing from passports to the release line itself.

CLI:
    python runtime/agi_release.py --root <sandbox> --sign [FILE ...]
    python runtime/agi_release.py --root <sandbox> --verify
"""
import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agi_master  # noqa: E402

SCHEMA = "agi-release/1"
DEFAULT_ARTIFACTS = ["core/dna.v4.json", "beta/AGI-ENTL-SEED.md", "BETA-NOTES.md"]


def _sigdir(root):
    d = pathlib.Path(root).resolve() / "state" / "release_sigs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _manifest_path(root):
    return pathlib.Path(root).resolve() / "state" / "release_signatures.json"


def sign_artifacts(root, paths=None):
    root = pathlib.Path(root).resolve()
    if not agi_master.identity(root).get("ok"):
        return {"ok": False, "error": "master ceremony required before signing release artifacts"}
    candidates = paths or DEFAULT_ARTIFACTS
    chosen = [rel for rel in candidates if (root / rel).is_file()]
    if not chosen:
        return {"ok": False, "error": "no releasable artifacts present (looked for %s)" % ", ".join(candidates)}
    arts = []
    for rel in chosen:
        p = root / rel
        rec = agi_master.sign_file(root, p, out=str(_sigdir(root) / (rel.replace("/", "_") + ".sig.json")))
        if not rec.get("ok"):
            return {"ok": False, "error": "sign failed for %s: %s" % (rel, rec.get("error"))}
        arts.append({"artifact": rel, "sha256": rec["sha256"], "algos": rec["algos"],
                     "sig_file": rec["sig_file"]})
    manifest = {"schema": SCHEMA, "artifacts": arts, "signed": len(arts),
                "note": "dual-signed release artifacts (Ed25519 + ML-DSA-65 when available)"}
    _manifest_path(root).write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return {"ok": True, **manifest, "manifest": str(_manifest_path(root))}


def verify_artifacts(root):
    root = pathlib.Path(root).resolve()
    mp = _manifest_path(root)
    if not mp.is_file():
        return {"ok": False, "error": "no release signature manifest; run --sign first"}
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    results = []
    for a in manifest.get("artifacts") or []:
        p = root / a["artifact"]
        if not p.is_file():
            results.append({"artifact": a["artifact"], "ok": False, "error": "missing"})
            continue
        v = agi_master.verify_file(root, p, a["sig_file"])
        results.append({"artifact": a["artifact"], "ok": bool(v.get("ok")), "algos": a.get("algos"),
                        "error": v.get("error")})
    ok = bool(results) and all(r["ok"] for r in results)
    return {"ok": ok, "schema": SCHEMA, "artifacts": results, "count": len(results),
            "verdict": "SIGNED+VERIFIED" if ok else "ATTENTION"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Dual-sign release artifacts (beta.10)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--sign", nargs="*", default=None, metavar="FILE")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.sign is not None:
        r = sign_artifacts(a.root, a.sign or None)
    else:
        r = verify_artifacts(a.root)
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
