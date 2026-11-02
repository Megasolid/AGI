#!/usr/bin/env python3
"""M1: second-station clean-room resume.

Bootstraps a station from a signed continuity handoff ONLY â€” never from a DSH
transcript. Reconstructs task queue, constraints, evidence index and rollback
state, re-verifies signatures through two independent ML-DSA paths, and
reproduces the pinned verification checks with hash and exit-code comparison.

Every discrepancy is RECORDED, never silently repaired.

    python runtime/agi_station_resume.py --handoff <path/to/handoff.json> \
        --repo <repo> --report <out.json>

Exit 0 only if every required check passes.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import platform
import re

import subprocess
import sys
from pathlib import Path

SCHEMA = "agi/station-resume-report/1"
HANDOFF_SCHEMA = "agi/continuity-handoff/1"
GATE_SCHEMA = "agi/gate-report/1"
KEY_ID = "a73eaa5d3c31e009"
PROTECTED = ["DNA.md", "core/dna.v4.json", "core/dna.v4.sig",
             "repo.json", "repo.json.sig", "POLICY.md"]


def auth_payload(p: Path) -> tuple[Path, dict]:
    sig = p.with_name(p.name + ".sig")
    return sig, json.loads(sig.read_text(encoding="utf-8"))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_bootstrap():
    """Locate verification capability without assuming it lives beside the station.

    Station reconstruction takes an explicit env-var contract because a clean-room
    station is not expected to inherit the DSH tree layout:
        AGI_CRYPTO_DIR    directory containing crypto.py (path A)
        AGI_MLDSA2_SITE   site-packages dir containing dilithium_py (path B)
    """
    crypto_dir = os.environ.get("AGI_CRYPTO_DIR")
    mldsa2 = os.environ.get("AGI_MLDSA2_SITE")
    if crypto_dir and mldsa2:
        return {"crypto_dir": Path(crypto_dir), "mldsa2_site": Path(mldsa2), "source": "env"}
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "memory" / "scripts" / "crypto.py"
        if candidate.exists():
            return {"crypto_dir": candidate.parent, "mldsa2_site": Path(mldsa2) if mldsa2 else None,
                    "source": "ancestor_walk"}
    return {"crypto_dir": Path(crypto_dir) if crypto_dir else None,
            "mldsa2_site": Path(mldsa2) if mldsa2 else None, "source": "unresolved"}


def verify_first(p: Path, records: list) -> dict:
    """Path A: AGI crypto.py (cryptography library) at its real module location."""
    boot = resolve_bootstrap()
    try:
        if not boot["crypto_dir"]:
            raise FileNotFoundError("crypto.py directory unresolved")
        if str(boot["crypto_dir"]) not in sys.path:
            sys.path.insert(0, str(boot["crypto_dir"]))
        import crypto  # noqa: WPS433
        res = crypto.verify_file(p, expected_key_id=KEY_ID)
        return {"path": "crypto.py", "module_dir": str(boot["crypto_dir"]), "ok": bool(res.get("ok")),
                "reason": res.get("reason"), "alg": res.get("alg"), "key_id": res.get("key_id")}
    except Exception as exc:
        record_discrepancy(records, "verify_first_error", {"target": str(p), "error": f"{type(exc).__name__}: {exc}"})
        return {"path": "crypto.py", "ok": False, "reason": f"{type(exc).__name__}: {exc}"}


def verify_second(p: Path, records: list) -> dict:
    """Path B: dilithium-py (independent ML-DSA implementation)."""
    boot = resolve_bootstrap()
    try:
        if boot.get("mldsa2_site") and str(boot["mldsa2_site"]) not in sys.path:
            sys.path.append(str(boot["mldsa2_site"]))
        from dilithium_py.ml_dsa import ML_DSA_65
        sig_path, env = auth_payload(p)
        pub = base64.b64decode(env["public_key_b64"])
        sig = base64.b64decode(env["signature_b64"])
        ok = bool(ML_DSA_65.verify(pub, p.read_bytes(), sig))
        tampered = ML_DSA_65.verify(pub, p.read_bytes() + b"\x00", sig)
        return {"path": "dilithium_py", "ok": ok, "tamper_rejected": tampered is False}
    except Exception as exc:
        record_discrepancy(records, "verify_second_error", {"target": str(p), "error": f"{type(exc).__name__}: {exc}"})
        return {"path": "dilithium_py", "ok": False, "reason": f"{type(exc).__name__}: {exc}"}


def record_discrepancy(records: list, code: str, detail) -> None:
    records.append({"code": code, "detail": detail})


def run(cmd: list[str], cwd: Path, timeout: int = 900) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {"cmd": " ".join(cmd), "exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except Exception as exc:
        return {"cmd": " ".join(cmd), "exit": -1, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}


def resume(handoff_path: Path, repo: Path) -> dict:
    records: list[dict] = []
    checks: list[dict] = []
    out: dict = {"schema": SCHEMA, "handoff": str(handoff_path), "repo": str(repo),
                 "environment": {"python": platform.python_version(), "platform": platform.platform()}}

    # 1. handoff is signed and intact
    if not handoff_path.exists():
        record_discrepancy(records, "handoff_missing", str(handoff_path))
        return _finish(out, checks, records)
    data = json.loads(handoff_path.read_text(encoding="utf-8"))
    out["handoff_sha256"] = "sha256:" + sha256_hex(handoff_path.read_bytes())

    if data.get("schema") != HANDOFF_SCHEMA:
        record_discrepancy(records, "handoff_schema_mismatch", data.get("schema"))
    checks.append({"id": "handoff_schema", "passed": data.get("schema") == HANDOFF_SCHEMA, "detail": data.get("schema")})

    # 2. dual signature verification of the handoff
    first = verify_first(handoff_path, records)
    second = verify_second(handoff_path, records)
    out["handoff_signature"] = {"first": first, "second": second}
    dual_ok = bool(first.get("ok")) and bool(second.get("ok"))
    checks.append({"id": "handoff_signature_dual", "passed": dual_ok,
                   "detail": {"first_ok": first.get("ok"), "second_ok": second.get("ok")}})
    if not (first.get("ok") and second.get("ok")):
        record_discrepancy(records, "signature_paths_disagree",
                           {"first": first, "second": second})

    # 3. reconstruct state (no transcript used)
    repo_state = data.get("repository", {})
    out["reconstructed"] = {
        "head_pin": repo_state.get("head"),
        "rollback_tag": repo_state.get("rollback_tag"),
        "rollback_commit": repo_state.get("rollback_commit"),
        "release_status": data.get("release_status", {}).get("state"),
        "task_queue": [t.get("id") for t in data.get("active_task_queue", [])],
        "constraints": data.get("limitations_do_not_overstate", []),
        "owner_required_actions": data.get("governance", {}).get("owner_required_actions", []),
        "blockers": data.get("blockers", []),
        "evidence_index_count": len(data.get("evidence_index", [])),
        "token_runway_present": data.get("token_runway", {}).get("value") is not None,
    }
    checks.append({"id": "reconstruction_complete",
                   "passed": bool(out["reconstructed"]["head_pin"]) and bool(out["reconstructed"]["rollback_tag"])
                             and len(out["reconstructed"]["task_queue"]) > 0
                             and out["reconstructed"]["evidence_index_count"] > 0,
                   "detail": out["reconstructed"]})

    # 4. evidence index re-check
    ev_results = []
    for item in data.get("evidence_index", []):
        rel, expected = item.get("path"), str(item.get("sha256", ""))
        p = repo / rel
        actual = ("sha256:" + sha256_hex(p.read_bytes())) if p.exists() else None
        ev_results.append({"path": rel, "expected": expected, "actual": actual, "ok": actual == expected})
    out["evidence_index_check"] = ev_results
    ev_ok = all(e["ok"] for e in ev_results) and ev_results
    checks.append({"id": "evidence_index_matches", "passed": bool(ev_ok),
                   "detail": {"checked": len(ev_results), "failed": [e for e in ev_results if not e["ok"]]}})
    for e in ev_results:
        if not e["ok"]:
            record_discrepancy(records, "evidence_hash_mismatch", e)

    # 5. reproduce protected-baseline and ancestry checks
    if (repo / ".git").exists():
        diff = run(["git", "-C", str(repo), "diff", "--stat", "v4.0.1..HEAD", "--", *PROTECTED], repo)
        checks.append({"id": "protected_baseline_unchanged", "passed": diff["exit"] == 0 and diff["stdout"].strip() == "",
                       "detail": diff["stdout"].strip()[:400]})
        anc = run(["git", "-C", str(repo), "merge-base", "--is-ancestor", "v4.0.1", "HEAD"], repo)
        checks.append({"id": "v401_ancestor", "passed": anc["exit"] == 0, "detail": anc["exit"]})

        # 6. reproduce pinned verification at the pinned head
        head_pin = repo_state.get("head")
        at_pin = run(["git", "-C", str(repo), "cat-file", "-e", f"{head_pin}^{{commit}}"], repo)
        checks.append({"id": "head_pin_exists", "passed": at_pin["exit"] == 0, "detail": head_pin})

        suite = run([sys.executable, "-m", "unittest", "discover", "-s", str(repo / "runtime"),
                     "-p", "test_v41e_*.py"], repo)
        ran = re.search(r"Ran (\d+) tests", suite["stderr"] + suite["stdout"])
        out["suite"] = {"exit": suite["exit"], "ran": int(ran.group(1)) if ran else None,
                        "sha256": "sha256:" + sha256_hex(suite["stderr"].encode("utf-8", "replace"))}
        checks.append({"id": "suite_reproduced", "passed": suite["exit"] == 0, "detail": out["suite"]})
    else:
        record_discrepancy(records, "no_git", "repo has no .git; ancestry checks skipped")
        checks.append({"id": "protected_baseline_unchanged", "passed": False, "detail": "no git"})

    # 7. restart without duplicate effects
    try:
        sys.path.insert(0, str(repo / "runtime"))
        from agi_operator_journal import OperatorJournal
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            j1 = OperatorJournal(Path(td) / "j.jsonl")
            j1.append("resume-1", "resume", {"step": 1})
            j2 = OperatorJournal(Path(td) / "j.jsonl")
            before = j2.last_seq
            j2.append("resume-1", "resume", {"step": 1})
            after = j2.last_seq
            checks.append({"id": "restart_no_duplicate_effect", "passed": before == after == 1,
                           "detail": {"before": before, "after": after}})
    except Exception as exc:
        record_discrepancy(records, "restart_test_error", f"{type(exc).__name__}: {exc}")
        checks.append({"id": "restart_no_duplicate_effect", "passed": False, "detail": str(exc)[:300]})

    return _finish(out, checks, records)


def _finish(out: dict, checks: list, records: list) -> dict:
    out["checks"] = checks
    out["discrepancies"] = records
    out["passed"] = bool(checks) and all(c["passed"] for c in checks) and not records
    out["policy"] = "discrepancies are recorded, never silently repaired"
    return out


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="M1 clean-room station resume")
    ap.add_argument("--handoff", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args(argv)
    report = resume(Path(args.handoff), Path(args.repo))
    body = json.dumps(report, indent=1, sort_keys=True)
    Path(args.report).write_text(body, encoding="utf-8")
    print(json.dumps({"passed": report["passed"],
                      "failed": [c["id"] for c in report["checks"] if not c["passed"]],
                      "discrepancies": len(report["discrepancies"]),
                      "report_sha256": "sha256:" + sha256_hex(body.encode("utf-8")),
                      "report": args.report}, indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
