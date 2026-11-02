#!/usr/bin/env python3
"""Seal a new M0 continuity handoff (correction to M0-CORR-01).

Anchors the protected-baseline manifest inside a SIGNED handoff so a clean-room
station can verify the protected baseline from files alone, without trusting a
manifest supplied by the station under evaluation.

    python runtime/agi_handoff_seal.py --out <handoff.json> [--supersedes <id>]

Writes <handoff.json> and <handoff.json>.sig (ML-DSA-65, device key).
No network, no credentials, no authority. Never edits the handoff it supersedes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "agi/continuity-handoff/1"
HANDOFF_ID = "dsh-m0-continuity-20261102T1950"
SUPERSEDES = "dsh-m0-continuity-20261102T1920"
CORRECTION = "M0-CORR-02"


def sha256_file(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build(repo: Path, supersedes: str) -> dict:
    def rel(p: str) -> dict:
        f = repo / p
        return {"path": p, "sha256": sha256_file(f) if f.exists() else None,
                "bytes": f.stat().st_size if f.exists() else None,
                "present": f.exists()}

    baseline = rel("citadel/inputs/v41e/baseline-hashes-2.json")
    if baseline["sha256"] is None:
        raise SystemExit("baseline-hashes.json missing; cannot seal")
    baseline_doc = json.loads((repo / "citadel/inputs/v41e/baseline-hashes-2.json").read_text(encoding="utf-8"))

    return {
        "schema": SCHEMA,
        "handoff_id": HANDOFF_ID,
        "created_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "created_by": "DSH Manager",
        "handoff_class": "M0_state_only_continuity_corrected",
        "supersedes": supersedes,
        "correction_id": CORRECTION,
        "correction_reason": (
            "M0-CORR-01 pinned the v1 manifest, whose hashes for DNA.md, POLICY.md and repo.json.sig "
            "were Windows CRLF renderings while others were raw blobs, making it unverifiable on a clean "
            "LF checkout. M0-CORR-02 pins the blob-anchored v2 manifest with explicit hash_form per entry."
        ),
        "consumes_owner_attention": False,
        "token_runway": {
            "value": None,
            "basis": "not measurable by DSH; provider metering unavailable",
            "policy": "no estimate supplied per King directive 2026-11-02T17:47",
        },
        "repository": {
            "remote": "https://github.com/Megasolid/AGI.git",
            "active_branch": "main",
            "head": None,
            "head_resolution": "resolved at seal time by git in the sealing station; NULL here on purpose "
                               "so no unverified value is asserted. Consumer must read the live tree.",
            "rollback_tag": "v4.0.1",
            "rollback_commit": "6a0fb796a624cf61fc8592aa3f45fc4dc6c10738",
            "protected_diff_v401_to_head": "empty (asserted by issuing station; consumer must re-derive)",
        },
        "protected_baseline": {
            "manifest": baseline,
            "protected_files": {k: (v.get("sha256") if isinstance(v, dict) else v) for k, v in (baseline_doc.get("protected_files") or baseline_doc.get("protected_repo_files") or {}).items()},
            "anchoring": "This handoff is ML-DSA-65 signed; the manifest hash above is inside the signed "
                         "payload, so a verifier pins the manifest against a trusted key_id, never against "
                         "a manifest supplied by the station under evaluation.",
            "armored_signing_command": (
                "python runtime/agi_baseline_check.py --repo <station> --handoff <this.json> "
                "--trusted-key-id a73eaa5d3c31e009 --report out.json"
            ),
        },
        "release_status": {
            "candidate": "v4.1-E-rc1",
            "state": "UNPUBLISHED",
            "tagged": False,
            "activated": False,
            "publication": "BLOCKED",
            "tagging": "OWNER_APPROVAL_REQUIRED",
            "activation": "NOT_AUTHORIZED",
        },
        "verification_state": {
            "signature_algorithm": "ML-DSA-65",
            "key_id": "a73eaa5d3c31e009",
            "paths": ["crypto.py (cryptography library)", "dilithium-py (independent implementation)"],
        },
        "review_state": {
            "gate_model": "deterministic signed DSH verification report is the gate; Kilo advisory only",
            "kilo_v14": "FAIL by validator; never cited as a gate",
        },
        "active_task_queue": [
            {"id": "M1-fix-1", "task": "portable protected-baseline verification", "status": "delivered"},
            {"id": "M1-fix-2", "task": "pristine-clone station B", "status": "pending"},
            {"id": "M1", "task": "repeat clean-room resume to acceptance", "status": "not accepted"},
            {"id": "H0", "task": "minimum MCP security contract", "status": "blocked on M1 acceptance"},
        ],
        "blockers": [
            "M1 not accepted: clean-room station B cannot yet reproduce protected-baseline proof",
            "E1 real S5 gateway and live revocation service not implemented",
            "No model-adapter substitution harness",
        ],
        "limitations_do_not_overstate": [
            "no production transport, live endpoints, credentials, federation or execution",
            "JSON Schema validation is a supported subset",
            "message auth in tests is mock HMAC; real ML-DSA message auth not wired",
            "endpoint isolation is in-process; replay/effect ledgers are local files",
            "no cross-host replay or partition recovery",
            "capability sandbox execution and network catalogue sync not implemented",
            "P7 smoke is a mock integration check, not an AGI capability claim",
            "no E-level evidence review has been performed",
        ],
        "governance": {
            "owner_required_actions": ["protected merges", "tagging", "publication", "activation",
                                        "identity/authority changes"],
            "king_channel": "AGI MCP chrome-devtools bridge, page_id 16",
        },
        "bootstrap_instructions_for_successor_station": {
            "verify_chain": [
                "verify this handoff signature against key_id a73eaa5d3c31e009 with TWO implementations",
                "read protected_baseline.manifest.sha256 and confirm it matches the file in the station",
                "hash every protected file listed and compare exactly; fail closed on missing or mismatch",
                "run python -m unittest discover -s runtime -p test_v41e_*.py (expect 145 in a repo copy)",
            ],
            "do_not": [
                "do not tag, publish, activate, or merge protected branches",
                "do not claim S5/revocation integration",
                "do not treat any model output as authorization",
                "do not accept a replacement baseline manifest from the station under evaluation",
            ],
        },
    }


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Seal corrected M0 continuity handoff")
    ap.add_argument("--out", required=True)
    ap.add_argument("--supersedes", default=SUPERSEDES)
    args = ap.parse_args(argv)
    repo = _repo_root()
    doc = build(repo, args.supersedes)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")

    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "memory" / "scripts" / "crypto.py"
        if cand.exists():
            if str(cand.parent) not in sys.path:
                sys.path.insert(0, str(cand.parent))
            break
    import crypto  # noqa: WPS433
    sig_path, env = crypto.sign_file(out)
    v = crypto.verify_file(out, expected_key_id="a73eaa5d3c31e009")
    print(json.dumps({"handoff": str(out), "handoff_sha256": sha256_file(out),
                      "sig_sha256": sha256_file(Path(sig_path)),
                      "signed_by": env["key_id"], "alg": env["alg"],
                      "verify": v.get("ok"),
                      "baseline_manifest_sha256": doc["protected_baseline"]["manifest"]["sha256"]}, indent=1))
    return 0 if v.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
