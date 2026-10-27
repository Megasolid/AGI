#!/usr/bin/env python3
"""check_public_sync.py - fail when public docs/installers drift from the latest release tag.

Root cause this guards against (2026-10-27): version numbers were hardcoded in several public files
(README install prompt, INSTALL_PROMPT.md, installer defaults, LINEAGE release list) and the release
process only bumped the installers and release notes - so the front page kept advertising an old version.

Checks (repo root = parent of tools/):
  1. latest tag = `git describe --tags --abbrev=0` (or the newest tag by creation date);
  2. every `releases/download/vX` and `releases/tag/vX` URL in the public docs equals the latest tag;
  3. every "install version vX" / `-Version vX` / `$v = "vX"` / `v="vX"` pin equals the latest tag;
  4. the installer defaults (`param(... "vX" ...)`, `VERSION="${AGI_VERSION:-vX}"`) equal the latest tag;
  5. LINEAGE.md lists the latest tag in its release section;
  6. README's lineage summary contains the latest tag.

Usage: python tools/check_public_sync.py [--repo <path>] [--quiet]
Exit: 0 = in sync, 1 = drift (prints every stale reference).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PUBLIC_DOCS = ("README.md", "INSTALL_PROMPT.md", "USER_MANUAL.md", "LINEAGE.md",
               "SECURITY.md", "NOTICE.md", "POLICY.md")
INSTALLERS = ("install.ps1", "install.sh")
RELEASE_NOTE_GLOB = "RELEASE_NOTES*.md"

URL_VERSION = re.compile(r"releases/(?:download|tag)/v(\d+\.\d+\.\d+)")
PIN_VERSION = re.compile(r'(?:install version|-Version|\$v\s*=\s*"|v="|AGI )\s*"?v?(\d+\.\d+\.\d+)')
PS_DEFAULT = re.compile(r'\$Version\s*=\s*"v(\d+\.\d+\.\d+)"')
SH_DEFAULT = re.compile(r"AGI_VERSION:-v(\d+\.\d+\.\d+)")


def latest_tag(root):
    for cmd in (["git", "describe", "--tags", "--abbrev=0"],
                ["git", "tag", "--sort=-creatordate"]):
        try:
            out = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=20)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.split()[0].strip()
        except Exception:
            continue
    return None


def _version(s):
    return tuple(int(x) for x in s.split("."))


RUNTIME_NAME = re.compile(r"agi-runtime-v(\d+\.\d+\.\d+)\.zip")
CITED_SHA = re.compile(r"sha256[^0-9a-fA-F]{0,12}([0-9a-fA-F]{8,64})")


def latest_runtime(root, latest):
    """(filename, sha256) of the runtime archive for the latest release, from releases/SHA256SUMS."""
    sums = Path(root) / "releases" / "SHA256SUMS"
    if not sums.is_file():
        return None, None, ["releases/SHA256SUMS is missing"]
    wanted = "agi-runtime-%s.zip" % latest
    problems = []
    for line in sums.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].endswith(wanted):
            return parts[-1], parts[0].lower(), problems
    problems.append("releases/SHA256SUMS has no entry for %s" % wanted)
    return None, None, problems


def scan(root=None, quiet=False):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    latest = latest_tag(root)
    problems = []
    refs = {}
    if not latest:
        return {"ok": False, "latest": None, "problems": ["no release tag found in the repository"]}

    latest_num = latest.lstrip("v")
    docs = [p for p in (root / n for n in PUBLIC_DOCS) if p.is_file()]
    # release notes are historical by nature: they pin their own version and links, so they are only
    # required to exist for the latest release, never rewritten.
    notes = sorted(root.glob(RELEASE_NOTE_GLOB))
    if not any(latest in p.name for p in notes):
        problems.append(f"no release notes file for {latest} (RELEASE_NOTES_{latest}.md)")
    for p in docs:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in URL_VERSION.finditer(text):
            refs.setdefault(p.name, []).append(("url", m.group(1)))
            if m.group(1) != latest_num:
                line = text.count("\n", 0, m.start()) + 1
                problems.append(f"{p.name}:{line}: release URL points at v{m.group(1)}, latest is {latest}")
        if p.name not in ("LINEAGE.md", "README.md"):
            for m in PIN_VERSION.finditer(text):
                refs.setdefault(p.name, []).append(("pin", m.group(1)))
                if m.group(1) != latest_num:
                    line = text.count("\n", 0, m.start()) + 1
                    problems.append(f"{p.name}:{line}: pinned version v{m.group(1)} is stale (latest {latest})")

    for name in INSTALLERS:
        p = root / name
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for rx in (PS_DEFAULT, SH_DEFAULT):
            for m in rx.finditer(text):
                refs.setdefault(name, []).append(("default", m.group(1)))
                if m.group(1) != latest_num:
                    line = text.count("\n", 0, m.start()) + 1
                    problems.append(f"{name}:{line}: installer default v{m.group(1)} is stale (latest {latest})")

    # LINEAGE must record the latest release; README's lineage summary must mention it.
    lin = root / "LINEAGE.md"
    if lin.is_file() and latest not in lin.read_text(encoding="utf-8", errors="ignore"):
        problems.append(f"LINEAGE.md does not list the latest release {latest}")
    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"## Lineage \(public\)(.*?)(?:\n## |\Z)", text, re.S)
        if m and latest not in m.group(1):
            problems.append(f"README.md lineage section does not mention {latest}")

    # runtime sha consistency: docs that quote a runtime sha must quote the *released* one
    runtime_file, runtime_sha, runtime_problems = latest_runtime(root, latest)
    problems += runtime_problems
    if runtime_file:
        sha_docs = [p for p in docs if p.name in ("INSTALL_PROMPT.md",)]
        sha_docs += [p for p in notes if latest in p.name]
        for p in sha_docs:
            text = p.read_text(encoding="utf-8", errors="ignore")
            cited = [m.group(1).lower() for m in CITED_SHA.finditer(text)]
            for c in cited:
                if not runtime_sha.startswith(c):
                    line = text[:text.lower().find(c)].count("\n") + 1
                    problems.append(f"{p.name}:{line}: cites sha256 {c}… but the released runtime is "
                                    f"{runtime_sha[:12]}… ({runtime_file})")

    result = {"ok": not problems, "latest": latest, "problems": problems,
              "runtime": {"file": runtime_file, "sha256": runtime_sha},
              "files_checked": [p.name for p in docs] + list(INSTALLERS),
              "references": {k: len(v) for k, v in refs.items()}}
    if not quiet:
        print(json.dumps(result, indent=1))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    r = scan(args.repo, quiet=args.quiet)
    if not args.quiet and not r["ok"]:
        print("\nFix: python memory/scripts/repo.py public-sync --fix  (or edit the files)", file=sys.stderr)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
