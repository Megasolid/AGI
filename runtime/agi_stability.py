#!/usr/bin/env python3
"""agi_stability - beta stability gate: run the conformance matrix K times on fresh clones (beta.9).

A beta release is not called "stable" because it works once. This gate copies the sandbox K times, runs the full
C-beta matrix on each cold copy, and reports verdicts + timing. The stability verdict is PASS only when every run
passes; nested conformance runs skip the stability check itself to avoid recursion.

CLI:
    python runtime/agi_stability.py --root <sandbox> [--runs 2] [--out state/archive/evolution/beta-stability.json]
"""
import argparse
import json
import pathlib
import shutil
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agi_conformance  # noqa: E402

SCHEMA = "agi-stability/1"


def run(root, runs=2):
    runs = max(1, int(runs or 1))
    results = []
    for i in range(runs):
        with tempfile.TemporaryDirectory() as td:
            cold = pathlib.Path(td) / "sandbox"
            shutil.copytree(str(root), cold)
            t0 = time.time()
            res = agi_conformance.run(cold, include_stability=False)
            results.append({"run": i + 1, "verdict": res.get("verdict"), "passed": res.get("passed"),
                            "total": res.get("total"),
                            "failed": [c["id"] for c in res.get("checks", []) if not c["ok"]],
                            "seconds": round(time.time() - t0, 2)})
    ok = all(r["verdict"] == "PASS" for r in results)
    return {"ok": ok, "schema": SCHEMA, "runs": runs, "results": results,
            "verdict": "STABLE" if ok else "ATTENTION",
            "note": "every run is a fresh cold copy; the stability check itself is excluded from nested runs"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Beta stability gate (K cold conformance runs)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--out", default="state/archive/evolution/beta-stability.json")
    a = ap.parse_args(argv)
    r = run(a.root, a.runs)
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": r["verdict"], "runs": r["runs"],
                      "results": [{"run": x["run"], "passed": x["passed"], "total": x["total"],
                                   "seconds": x["seconds"]} for x in r["results"]], "out": str(out)}, indent=1))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
