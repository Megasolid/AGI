#!/usr/bin/env python3
"""P7 v14 machine-checkable Kilo findings validator.

King decision 2026-11-02T1647: "Kilo findings v12-v13 require metadata validation".
This validator makes defective metadata fail mechanically instead of being caught by hand.

Registered with citadel/registry.json and called by the Kilo task v41e-v-14:

    python runtime/agi_findings_validate.py <findings.json> \
        --task-hash sha256:... --bundle-sha256 sha256:... \
        --bundle-bytes N --manifest-count N --task-id v41e-v-14

Exit codes: 0 = valid, 1 = invalid, 2 = usage/IO error.
No network, no credentials, no AGI authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REQUIRED_TOP = (
    "schema", "task_id", "station", "decision", "checks", "findings", "evidence",
)
REQUIRED_EVIDENCE = (
    "task_hash", "bundle_sha256", "bundle_bytes", "manifest_count",
)
DECISIONS = {"PASS", "PASS_WITH_FINDINGS", "FAIL"}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
_V11 = "task_id"
_TASK = "v41e-v-14"


def _fail(errors, msg):
    errors.append(msg)


def validate(findings: dict, *, task_hash: str, bundle_sha256: str, bundle_bytes: int,
             manifest_count: int, task_id: str = _TASK) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(findings, dict):
        return {"ok": False, "errors": ["findings is not a JSON object"], "warnings": []}

    for key in REQUIRED_TOP:
        if key not in findings:
            _fail(errors, f"missing top-level key: {key}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    if findings.get("task_id") != task_id:
        _fail(errors, f"task_id mismatch: findings={findings.get('task_id')!r} expected={task_id!r}")
    if findings.get("station") != "kilo":
        _fail(errors, f"station must be 'kilo', got {findings.get('station')!r}")
    if findings.get("decision") not in DECISIONS:
        _fail(errors, f"decision must be one of {sorted(DECISIONS)}, got {findings.get('decision')!r}")
    if not isinstance(findings.get("checks"), list) or not findings["checks"]:
        _fail(errors, "checks must be a non-empty list")
    else:
        for i, chk in enumerate(findings["checks"]):
            if not isinstance(chk, dict):
                _fail(errors, f"checks[{i}] is not an object")
                continue
            for key in ("id", "decision", "evidence"):
                if key not in chk:
                    _fail(errors, f"checks[{i}] missing {key}")
            if chk.get("decision") not in DECISIONS:
                _fail(errors, f"checks[{i}].decision invalid: {chk.get('decision')!r}")
    if not isinstance(findings.get("findings"), list):
        _fail(errors, "findings must be a list")

    ev = findings.get("evidence")
    if not isinstance(ev, dict):
        _fail(errors, "evidence must be an object")
        return {"ok": False, "errors": errors, "warnings": warnings}

    for key in REQUIRED_EVIDENCE:
        if key not in ev:
            _fail(errors, f"evidence missing {key}")

    got_hash = str(ev.get("task_hash", ""))
    if task_hash not in got_hash:
        _fail(errors, f"evidence.task_hash does not contain pinned task hash {task_hash}; got {got_hash[:100]!r}")

    got_bundle = str(ev.get("bundle_sha256", ""))
    if bundle_sha256 not in got_bundle:
        _fail(errors, f"evidence.bundle_sha256 does not contain pinned bundle hash {bundle_sha256}; got {got_bundle[:100]!r}")

    if ev.get("bundle_bytes") != bundle_bytes:
        _fail(errors, f"evidence.bundle_bytes mismatch: got {ev.get('bundle_bytes')!r} expected {bundle_bytes}")
    if ev.get("manifest_count") != manifest_count:
        _fail(errors, f"evidence.manifest_count mismatch: got {ev.get('manifest_count')!r} expected {manifest_count}")

    sig = ev.get("signature")
    if isinstance(sig, dict):
        if sig.get("crypto_verified") is not False:
            warnings.append("signature.crypto_verified must be false for Kilo (no ML-DSA library); "
                            "set it explicitly false rather than true")
        if _HEX64.fullmatch(str(sig.get("key_id", ""))) is None and not re.fullmatch(r"[0-9a-f]{16}", str(sig.get("key_id", ""))):
            _fail(errors, f"signature.key_id malformed: {sig.get('key_id')!r}")
    else:
        warnings.append("evidence.signature missing; expected structural signature record")

    # Defect patterns observed in v12/v13
    stale = str(ev.get("bundle_sha256", ""))
    for known in ("205d22f39d128dd8666822a7d570bbd46f499b207d2ba48c2f36ad7f7d8651c1",):
        if known in stale and bundle_sha256 != "sha256:" + known:
            _fail(errors, "evidence.bundle_sha256 cites the stale v10 bundle hash for a v14 review")
    for key, value in ev.items():
        if key in ("signature_verification_file_sha256", "signature_file_sha256"):
            if not _SHA.fullmatch(str(value)):
                _fail(errors, f"evidence.{key} is not a sha256:<64hex> value")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Validate Kilo findings metadata against a pinned task/bundle")
    ap.add_argument("findings")
    ap.add_argument("--task-hash", required=True)
    ap.add_argument("--bundle-sha256", required=True)
    ap.add_argument("--bundle-bytes", type=int, required=True)
    ap.add_argument("--manifest-count", type=int, required=True)
    ap.add_argument("--task-id", default=_TASK)
    args = ap.parse_args(argv)
    try:
        data = json.loads(Path(args.findings).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [f"unreadable findings: {exc}"], "warnings": []}, indent=1))
        return 2
    result = validate(data, task_hash=args.task_hash, bundle_sha256=args.bundle_sha256,
                      bundle_bytes=args.bundle_bytes, manifest_count=args.manifest_count,
                      task_id=args.task_id)
    print(json.dumps(result, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
