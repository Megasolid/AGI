#!/usr/bin/env python3
"""Self-test for tools/check_public_sync.py (stdlib only, deterministic, no git needed).

The production check reads repo.json:current_tag first, so a temporary directory is enough. This test
covers both release identities: the genetic DNA tag and the legacy semantic version tag.
"""
import json
import tempfile
from pathlib import Path

import check_public_sync as cps

SHA = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"


def build(root, tag):
    root.mkdir(parents=True, exist_ok=True)
    (root / "repo.json").write_text(json.dumps({"current_tag": tag}), encoding="utf-8")
    (root / "README.md").write_text(
        "# What AGI is\n\nInstall: `install version %s`.\n\nSee https://github.com/Megasolid/AGI/releases/tag/%s\n"
        % (tag, tag), encoding="utf-8")
    (root / "INSTALL_PROMPT.md").write_text(
        "release — https://github.com/Megasolid/AGI/releases/tag/%s\n\n$v = \"%s\"\n\n"
        "AGI %s installed — sha256 %s… verified.\n" % (tag, tag, tag, SHA[:16]), encoding="utf-8")
    (root / "LINEAGE.md").write_text("# Lineage\n\nRelease identity: %s\n" % tag, encoding="utf-8")
    (root / "RELEASE_NOTES.md").write_text(
        "## AGI alpha - %s\n\nRuntime `agi-runtime-%s.zip` with sha256 %s…\n\n"
        "## AGI v0.4.3 - old release\n\nold sha256 11111111…\n" % (tag, tag, SHA[:16]),
        encoding="utf-8")
    (root / "install.ps1").write_text('[string]$Version = "%s"\n' % tag, encoding="utf-8")
    (root / "install.sh").write_text('VERSION="${AGI_VERSION:-%s}"\n' % tag, encoding="utf-8")
    (root / "releases").mkdir(exist_ok=True)
    (root / "releases" / "SHA256SUMS").write_text(
        "%s  releases/runtime/2026-10-28/agi-runtime-%s.zip\n" % (SHA, tag), encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        dna = base / "dna"
        build(dna, "dna-TESTTAG123")
        r = cps.scan(dna, quiet=True)
        assert r["ok"], "DNA-tag repo should pass: %s" % r["problems"]
        assert r["latest"] == "dna-TESTTAG123"
        assert r["runtime"]["file"].endswith("agi-runtime-dna-TESTTAG123.zip")

        (dna / "install.ps1").write_text('[string]$Version = "v0.4.3"\n', encoding="utf-8")
        r = cps.scan(dna, quiet=True)
        assert not r["ok"], "stale installer default must fail"
        assert any("installer default" in p for p in r["problems"]), r["problems"]

        (dna / "install.ps1").write_text('[string]$Version = "dna-TESTTAG123"\n', encoding="utf-8")
        (dna / "README.md").write_text("# What AGI is\n\nInstall: `install version v0.4.3`.\n", encoding="utf-8")
        r = cps.scan(dna, quiet=True)
        assert not r["ok"], "stale install pin must fail"
        assert any("install pin" in p for p in r["problems"]), r["problems"]

        semver = base / "semver"
        build(semver, "v9.9.9")
        r = cps.scan(semver, quiet=True)
        assert r["ok"], "legacy semver tag repo should pass: %s" % r["problems"]
        assert r["runtime"]["file"].endswith("agi-runtime-v9.9.9.zip")

        with open(semver / "releases" / "SHA256SUMS", "w", encoding="utf-8") as f:
            f.write("%s  releases/runtime/2026-10-28/agi-runtime-vNOPE.zip\n" % SHA)
        r = cps.scan(semver, quiet=True)
        assert not r["ok"], "missing runtime entry must fail"

    print("check_public_sync self-test: ok (DNA tag, semver tag, stale pin, stale installer, missing runtime)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
