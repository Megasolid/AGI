#!/usr/bin/env python3
"""GATE-1: deterministic verification report for an AGI head.

Anyone can run this and compare. It executes fix-point checks and emits a JSON
report with exact commands, exit codes, and hashes. It does not tag, publish,
activate, or touch protected baselines.

    python runtime/agi_gate_report.py --head <commit> --out report.json

Exit code: 0 if every required check passes, 1 otherwise.
No network, no credentials, no AGI authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCHEMA = "agi/gate-report/1"
PROTECTED = ["DNA.md", "core/dna.v4.json", "core/dna.v4.sig",
             "repo.json", "repo.json.sig", "POLICY.md"]
KEY_ID = "a73eaa5d3c31e009"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                              capture_output=True, text=True, timeout=timeout)
        return {"cmd": " ".join(cmd), "exit": proc.returncode,
                "stdout_sha256": sha256_bytes(proc.stdout.encode("utf-8", "replace")),
                "stdout_tail": proc.stdout.strip().splitlines()[-12:],
                "stderr_tail": proc.stderr.strip().splitlines()[-6:]}
    except Exception as exc:
        return {"cmd": " ".join(cmd), "exit": -1, "error": f"{type(exc).__name__}: {exc}"}


def check(name: str, passed: bool, detail) -> dict:
    return {"id": name, "passed": bool(passed), "detail": detail}


def git(repo: Path, *args: str) -> dict:
    return run(["git", "-C", str(repo), *args])


def _crypto_module():
    """Locate the AGI crypto module by walking ancestors (repo may be relocated)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "memory" / "scripts" / "crypto.py"
        if candidate.exists():
            if str(candidate.parent) not in sys.path:
                sys.path.insert(0, str(candidate.parent))
            import crypto  # noqa: WPS433
            return crypto
    raise FileNotFoundError("memory/scripts/crypto.py not found in ancestor directories")


def verify_signature(p: Path, key_id: str) -> dict:
    """Verify in-process with the asset's own crypto module (exact path, no shelling out)."""
    try:
        crypto = _crypto_module()
        result = crypto.verify_file(p, expected_key_id=key_id)
        return {"ok": bool(result.get("ok")), "reason": result.get("reason"),
                "alg": result.get("alg"), "key_id": result.get("key_id")}
    except Exception as exc:
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}"}


def build_report(repo: Path, head: str) -> dict:
    checks: list[dict] = []
    info: dict = {}

    has_git = shutil.which("git") is not None and (repo / ".git").exists()
    if has_git:
        head_now = git(repo, "rev-parse", "HEAD")
        info["head_actual"] = head_now["stdout_tail"][-1] if head_now["stdout_tail"] else None
        checks.append(check("head_matches_pin", info["head_actual"] == head,
                            {"pinned": head, "actual": info["head_actual"]}))

        status = git(repo, "status", "--porcelain")
        info["working_tree_clean"] = status["stdout_tail"] == []
        checks.append(check("working_tree_clean", info["working_tree_clean"],
                            {"porcelain": status["stdout_tail"]}))

        protected_diff = git(repo, "diff", "--stat", "v4.0.1..HEAD", "--", *PROTECTED)
        info["protected_diff"] = protected_diff["stdout_tail"]
        checks.append(check("protected_baseline_unchanged", protected_diff["stdout_tail"] == [],
                            {"diff_stat": protected_diff["stdout_tail"]}))

        ancestor = git(repo, "merge-base", "--is-ancestor", "v4.0.1", "HEAD")
        checks.append(check("v401_ancestor", ancestor["exit"] == 0, {"exit": ancestor["exit"]}))

        tags = git(repo, "tag", "--list")
        info["tags"] = tags["stdout_tail"]
        checks.append(check("published_tags_present", "v4.0.1" in tags["stdout_tail"],
                            {"tags_count": len(tags["stdout_tail"])}))
    else:
        checks.append(check("git_available", False, {"reason": "no git or not a checkout"}))

    # Test suite
    suite = run([sys.executable, "-m", "unittest", "discover", "-s",
                 str(repo / "runtime"), "-p", "test_v41e_*.py", "-v"],
                cwd=repo, timeout=900)
    suite_text = "\n".join(suite.get("stdout_tail", []) + suite.get("stderr_tail", []))
    ran = re.search(r"Ran (\d+) tests", suite_text)
    info["tests_ran"] = int(ran.group(1)) if ran else None
    info["tests_ok"] = suite["exit"] == 0 and "OK" in suite_text
    checks.append(check("test_suite", info["tests_ok"],
                        {"exit": suite["exit"], "ran": info["tests_ran"], "tail": suite["stdout_tail"][-3:]}))

    # Signature verification (first path: crypto.py)
    sig_targets = [
        "citadel/inputs/v41e/v41e-rc-manifest.json",
        "citadel/handoff/DSH-CONTINUITY-HANDOFF-20261102T1750.json",
    ]
    sig_results = []
    for rel in sig_targets:
        p = repo / rel
        if not p.exists():
            sig_results.append({"path": rel, "ok": False, "reason": "missing"})
            continue
        res = verify_signature(p, KEY_ID)
        res["path"] = rel
        sig_results.append(res)
    info["signature_first_path"] = sig_results
    checks.append(check("signatures_first_path", all(s["ok"] for s in sig_results), sig_results))

    # Kilo findings preserved as advisory (not a gate)
    kilo = []
    for state_dir in (repo.parent.parent / "state" / "agi5" / "pilot" / "v41e",):
        if state_dir.exists():
            for f in sorted(state_dir.glob("kilo-v41e-v-*-findings.json")):
                kilo.append({"file": f.name, "sha256": sha256_bytes(f.read_bytes())})
    info["kilo_findings_advisory"] = kilo

    report = {
        "schema": SCHEMA,
        "head": head,
        "base": {"repo": str(repo)},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git": (run(["git", "--version"])["stdout_tail"] or [None])[0],
        },
        "checks": checks,
        "info": info,
        "gate_model": "DSH deterministic report is the gate; Kilo is advisory corroboration only",
        "no_actions": ["no tag", "no publication", "no activation", "no protected-baseline change"],
    }
    report["passed"] = all(c["passed"] for c in checks)
    return report


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Deterministic AGI gate report")
    ap.add_argument("--head", required=True)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    report = build_report(Path(args.repo), args.head)
    body = json.dumps(report, indent=1, sort_keys=True)
    Path(args.out).write_text(body, encoding="utf-8")
    print(json.dumps({"passed": report["passed"],
                      "failed": [c["id"] for c in report["checks"] if not c["passed"]],
                      "report_sha256": sha256_bytes(body.encode("utf-8")),
                      "out": args.out}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
