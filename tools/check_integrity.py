#!/usr/bin/env python3
"""Integrity check for the AGI.alpha repository (stdlib only, runs in CI).

Verifies what a stranger can verify from a clone: the signed manifest's hashes for the official
bundle, every mirror snapshot and every release zip; the releases/SHA256SUMS entries; and that no
distributed file leaks member identity or private material.

Signature authenticity (ML-DSA) is verified on the holder's machine by `repo.py verify` because that
needs the AGI cryptography module. This job catches the two failure modes that hurt when a repo is
shared: silent artefact tampering and identity leaks.
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "repo.json"
# patterns are assembled from fragments so this scanner never matches its own source
_ID = '"passport' + '_id"'
_GR = '"user_genome' + '_root"'
IDENTITY_PATTERNS = [
    (re.compile(_ID + r'\s*:\s*"[0-9a-fA-F-]{8,}"'), "passport id"),
    (re.compile(_GR + r'\s*:\s*"[0-9a-fA-F]{32,}"'), "genome root"),
    (re.compile("BEGIN " + "PRIVATE|PRIVATE " + "KEY|root_" + "shard|g" + "hp_[A-Za-z0-9]{20,}"),
     "private material or token"),
    (re.compile("megasolid" + "7|@g" + "mail"), "personal email"),
]


BINARY_SUFFIXES = (".zip", ".png", ".jpg", ".jpeg", ".gz", ".pdf", ".npy")


def sha(p):
    """Hash LF-normalised bytes: the same rule repo.py uses, so Windows and Linux agree."""
    p = pathlib.Path(p)
    raw = p.read_bytes()
    if p.suffix.lower() in BINARY_SUFFIXES:
        return hashlib.sha256(raw).hexdigest()
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def main():
    problems = []
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    official = man.get("official") or {}
    bundle = ROOT / "bundle" / "official" / "bundle.json"
    if not bundle.is_file():
        problems.append("official bundle missing")
    else:
        if sha(bundle) != official.get("manifest_sha256"):
            problems.append("official bundle hash differs from repo.json")
        bm = json.loads(bundle.read_text(encoding="utf-8"))
        if (bm.get("passport") or {}).get("passport_id"):
            problems.append("official bundle leaks a passport id")
        if (bm.get("genome") or {}).get("root"):
            problems.append("official bundle leaks a genome root")
    for m in (man.get("artifacts") or {}).get("mirrors") or []:
        mp = ROOT / "public" / "mirror" / str(m.get("tree_size")) / "manifest.json"
        if not mp.is_file():
            problems.append("mirror snapshot %s: manifest missing" % m.get("tree_size"))
        elif sha(mp) != m.get("manifest_sha256"):
            problems.append("mirror snapshot %s: hash differs from repo.json" % m.get("tree_size"))
    sums = ROOT / "releases" / "SHA256SUMS"
    sums_txt = sums.read_text(encoding="utf-8") if sums.is_file() else ""
    for r in (man.get("artifacts") or {}).get("releases") or []:
        rp = ROOT / str(r.get("path"))
        if not rp.is_file():
            problems.append("release %s: file missing" % r.get("package"))
            continue
        if sha(rp) != r.get("sha256"):
            problems.append("release %s: sha256 differs from repo.json" % r.get("package"))
        if ("%s  %s" % (r.get("sha256"), r.get("path"))) not in sums_txt:
            problems.append("release %s: not recorded in SHA256SUMS" % r.get("package"))
    for f in sorted(ROOT.rglob("*")):
        if not f.is_file() or f.suffix.lower() in (".zip", ".png", ".jpg", ".gz"):
            continue
        if ".git" in f.parts:
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat, label in IDENTITY_PATTERNS:
            if pat.search(txt):
                problems.append("%s: contains %s" % (f.relative_to(ROOT).as_posix(), label))
    result = {"ok": not problems, "problems": problems,
              "checked": {"mirrors": len((man.get("artifacts") or {}).get("mirrors") or []),
                          "releases": len((man.get("artifacts") or {}).get("releases") or [])}}
    print(json.dumps(result, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
