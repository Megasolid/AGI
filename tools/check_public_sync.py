#!/usr/bin/env python3
"""check_public_sync.py - fail when public docs/installers drift from the latest release tag.

Root cause this guards against (2026-10-27): version numbers were hardcoded in several public files
(README install prompt, INSTALL_PROMPT.md, installer defaults, LINEAGE release list) and the release
process only bumped the installers and release notes - so the front page kept advertising an old version.

The release identity is no longer only semantic version. Since the genetic release, tags look like
`dna-GCACGAGGCTGT`; older releases use `vX.Y.Z`. This check is tag-format agnostic: it reads the current
release tag from `repo.json` (the signed manifest is the source of truth) and falls back to the newest tag.

Checks (repo root = parent of tools/):
  1. latest tag = `repo.json:current_tag`, else the newest tag by creation date;
  2. every `releases/download/<tag>` and `releases/tag/<tag>` URL in public docs/installers equals it;
  3. every install pin ("install version <tag>", `$v = "<tag>"`, `-Version <tag>`) equals it;
  4. installer defaults equal it (`$Version = "<tag>"`, `AGI_VERSION:-<tag>`);
  5. LINEAGE.md lists it; README's lineage summary (if present) mentions it;
  6. RELEASE_NOTES.md mentions it;
  7. the released runtime archive for that tag exists in `releases/SHA256SUMS`, and any SHA cited in
     INSTALL_PROMPT.md / RELEASE_NOTES.md matches it.

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

# A release tag: DNA tags (`dna-GCACGAGGCTGT`) or legacy semver (`v0.4.3`). Keep the character class
# deliberately conservative so a stray word after a URL is not mistaken for a tag.
TAG = r"[A-Za-z0-9][A-Za-z0-9._-]*"
URL_TAG = re.compile(r"releases/(?:download|tag)/(" + TAG + r")")
PIN_PATTERNS = [
    re.compile(r"install version\s+[`\"']?(" + TAG + r")", re.I),
    re.compile(r"\$v\s*=\s*[\"'](" + TAG + r")[\"']"),
    re.compile(r"\bv\s*=\s*[\"'](" + TAG + r")[\"']"),
    re.compile(r"-Version\s+[\"']?(" + TAG + r")"),
]
PS_DEFAULT = re.compile(r'\$Version\s*=\s*["\'](' + TAG + r')["\']')
SH_DEFAULT = re.compile(r"AGI_VERSION:-(" + TAG + r")")
CITED_SHA = re.compile(r"sha256[^0-9a-fA-F]{0,12}([0-9a-fA-F]{8,64})")


def _run_git(root, *args):
    try:
        out = subprocess.run(["git"] + list(args), cwd=str(root), capture_output=True, text=True, timeout=20)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


def latest_tag(root):
    """Current release tag: repo.json first (source of truth), then newest tag by creation date."""
    manifest = Path(root) / "repo.json"
    if manifest.is_file():
        try:
            tag = str(json.loads(manifest.read_text(encoding="utf-8")).get("current_tag") or "").strip()
            if tag:
                return tag
        except Exception:
            pass
    out = _run_git(root, "for-each-ref", "--sort=-creatordate", "--format=%(refname:short)", "refs/tags")
    if out:
        return out.split()[0].strip()
    return _run_git(root, "describe", "--tags", "--abbrev=0")


def latest_runtime(root, latest):
    """(path, sha256) of the runtime archive for the latest release, from releases/SHA256SUMS."""
    sums = Path(root) / "releases" / "SHA256SUMS"
    if not sums.is_file():
        return None, None, ["releases/SHA256SUMS is missing"]
    wanted = "agi-runtime-%s.zip" % latest
    for line in sums.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].endswith(wanted):
            return parts[-1], parts[0].lower(), []
    return None, None, ["releases/SHA256SUMS has no entry for %s" % wanted]


def _line(text, start):
    return text.count("\n", 0, start) + 1


def scan(root=None, quiet=False):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    latest = latest_tag(root)
    problems = []
    refs = {}
    if not latest:
        return {"ok": False, "latest": None, "problems": ["no release tag found in the repository"]}

    docs = [p for p in (root / n for n in PUBLIC_DOCS) if p.is_file()]
    notes = root / "RELEASE_NOTES.md"
    if not notes.is_file():
        problems.append("no RELEASE_NOTES.md in the repository")
    elif latest not in notes.read_text(encoding="utf-8", errors="ignore"):
        problems.append(f"RELEASE_NOTES.md does not mention the latest release {latest}")

    # 2) release URLs in public docs and installers must point at the current tag
    for p in docs + [root / n for n in INSTALLERS if (root / n).is_file()]:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in URL_TAG.finditer(text):
            tag = m.group(1)
            refs.setdefault(p.name, []).append(("url", tag))
            if tag != latest:
                problems.append(f"{p.name}:{_line(text, m.start())}: release URL points at {tag}, latest is {latest}")

    # 3) explicit install pins in public docs must be the current tag
    for p in docs:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for rx in PIN_PATTERNS:
            for m in rx.finditer(text):
                tag = m.group(1)
                refs.setdefault(p.name, []).append(("pin", tag))
                if tag != latest:
                    problems.append(f"{p.name}:{_line(text, m.start())}: install pin {tag} is stale (latest {latest})")

    # 4) installer defaults must equal the current tag
    for name in INSTALLERS:
        p = root / name
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        seen = False
        for rx in (PS_DEFAULT, SH_DEFAULT):
            for m in rx.finditer(text):
                seen = True
                tag = m.group(1)
                refs.setdefault(name, []).append(("default", tag))
                if tag != latest:
                    problems.append(f"{name}:{_line(text, m.start())}: installer default {tag} is stale "
                                    f"(latest {latest})")
        if not seen:
            problems.append(f"{name}: no release default found (expected {latest})")

    # 5) LINEAGE must record the latest release; README's lineage summary, if present, must too.
    lin = root / "LINEAGE.md"
    if lin.is_file() and latest not in lin.read_text(encoding="utf-8", errors="ignore"):
        problems.append(f"LINEAGE.md does not list the latest release {latest}")
    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"## Lineage \(public\)(.*?)(?:\n## |\Z)", text, re.S)
        if m and latest not in m.group(1):
            problems.append(f"README.md lineage section does not mention {latest}")

    # 7) runtime consistency: the released archive must be listed and quoted hashes must match it.
    runtime_file, runtime_sha, runtime_problems = latest_runtime(root, latest)
    problems += runtime_problems
    if runtime_file:
        sha_docs = [root / "INSTALL_PROMPT.md"]
        # Only the section of the release notes that belongs to the latest release is current. Historical
        # sections legitimately cite their own old runtime hashes and must not be rewritten.
        if notes.is_file():
            sections = re.split(r"(?m)^##\s+", notes.read_text(encoding="utf-8", errors="ignore"))
            current = [s for s in sections if latest in s.split("\n", 1)[0]]
            for s in current:
                text = s
                for m in CITED_SHA.finditer(text):
                    cited = m.group(1).lower()
                    if not runtime_sha.startswith(cited):
                        problems.append(f"RELEASE_NOTES.md (latest section): cites sha256 {cited}… but the released "
                                        f"runtime is {runtime_sha[:12]}… ({runtime_file})")
        for p in sha_docs:
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in CITED_SHA.finditer(text):
                cited = m.group(1).lower()
                if not runtime_sha.startswith(cited):
                    problems.append(f"{p.name}:{_line(text, m.start())}: cites sha256 {cited}… but the released "
                                    f"runtime is {runtime_sha[:12]}… ({runtime_file})")
    else:
        # keep the reason visible even when no sha is quoted
        problems += runtime_problems


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
