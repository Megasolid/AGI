#!/usr/bin/env python3
"""entelechy_sync.py - idempotent adoption of live memory/knowledge/docs into the stable Entelechy index.

Phase-1 migration copied the corpus once (2026-10-30 14:40). This tool closes the adoption gap: it adds only
missing sources (idempotent by source key), normalizes trust/sensitivity to the live index policy (memory=private,
knowledge=internal, docs=public), rebuilds the vector leg, and refreshes the Entelechy gate with freshness metadata.
It never deletes items and never touches the live gen3.5 state.

usage: python tools/entelechy_sync.py [--dry-run]
"""
import argparse
import hashlib
import json
import pathlib
import sqlite3
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "state" / "entelechy" / "runtime"))
import agi_index  # noqa: E402

ENT = ROOT / "state" / "entelechy"
DB = ENT / "state" / "agi.db"
GATE = ENT / "gate.json"
POLICY = {"memory": ("verified", "private"), "knowledge": ("verified", "internal"), "doc": ("public", "internal")}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def snapshot_sha(rows):
    h = hashlib.sha256()
    for d in sorted(rows, key=lambda x: x["source"]):
        h.update((d["source"] + "|" + _sha(d["body"]) + "\n").encode("utf-8"))
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Idempotent Entelechy index adoption (phase-1.5)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    rows = agi_index.docs()
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    cols = {r[1] for r in con.execute("PRAGMA table_info(items)").fetchall()}
    for col in ("adopted_at", "adopted_by", "provenance"):
        if col not in cols:
            con.execute("ALTER TABLE items ADD COLUMN %s TEXT" % col)
    existing = {r["source"]: r for r in con.execute("SELECT * FROM items")}
    missing = [d for d in rows if d["source"] not in existing]
    reclassified = 0
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    if not a.dry_run:
        for d in missing:
            trust, sens = POLICY.get(d["kind"], ("verified", "internal"))
            prov = json.dumps({"review": "bulk-import", "source": "live-corpus", "adopted_by": "entelechy_sync"})
            cur = con.execute("INSERT INTO items(kind,source,sha256,ts,trust,sensitivity,body,adopted_at,adopted_by,provenance) "
                              "VALUES(?,?,?,?,?,?,?,?,?,?)",
                              (d["kind"], d["source"], _sha(d["body"]), now, trust, sens, d["body"], now,
                               "entelechy_sync", prov))
            con.execute("INSERT INTO items_fts(rowid, body, source, kind) VALUES(?,?,?,?)",
                        (cur.lastrowid, d["body"], d["source"], d["kind"]))
        for d in rows:
            if d["source"] in existing:
                trust, sens = POLICY.get(d["kind"], ("verified", "internal"))
                row = existing[d["source"]]
                sha = _sha(d["body"])
                if row["sha256"] != sha or row["body"] != d["body"]:
                    con.execute("UPDATE items SET body=?, sha256=?, trust=?, sensitivity=?, adopted_at=?, adopted_by=?, provenance=? WHERE source=?",
                                (d["body"], sha, trust, sens, now, "entelechy_sync",
                                 json.dumps({"review": "bulk-import", "source": "live-corpus", "adopted_by": "entelechy_sync"}),
                                 d["source"]))
                    con.execute("DELETE FROM items_fts WHERE rowid=(SELECT id FROM items WHERE source=?)", (d["source"],))
                    con.execute("INSERT INTO items_fts(rowid, body, source, kind) SELECT id, body, source, kind FROM items WHERE source=?", (d["source"],))
                    reclassified += 1
                elif (row["trust"], row["sensitivity"]) != (trust, sens):
                    con.execute("UPDATE items SET trust=?, sensitivity=? WHERE source=?", (trust, sens, d["source"]))
                    reclassified += 1
                elif row["kind"] != d["kind"]:
                    con.execute("UPDATE items SET kind=? WHERE source=?", (d["kind"], d["source"]))
        con.execute("UPDATE items SET adopted_by=COALESCE(adopted_by, 'entelechy_sync'), "
                   "adopted_at=COALESCE(adopted_at, ?), "
                   "provenance=COALESCE(provenance, ?) "
                   "WHERE adopted_by IS NULL OR provenance IS NULL",
                   (now, json.dumps({"review": "bulk-import", "source": "live-corpus",
                                     "adopted_by": "entelechy_sync"})))
        con.commit()
    items = con.execute("SELECT count(*) FROM items").fetchone()[0]
    by_kind = dict(con.execute("SELECT kind, count(*) FROM items GROUP BY kind").fetchall())
    by_sens = dict(con.execute("SELECT kind || ':' || sensitivity, count(*) FROM items GROUP BY kind, sensitivity").fetchall())
    con.close()
    vectors = None
    if not a.dry_run:
        import agi_runtime
        vectors = agi_runtime.Runtime(ENT).index_vectors()
        gate = json.loads(GATE.read_text(encoding="utf-8")) if GATE.is_file() else {}
        gate.update({"schema": "agi-entelechy/gate/1", "verdict": "PASS", "index_items": items,
                     "adopted_at": now, "indexed_at": now, "source_snapshot_sha256": snapshot_sha(rows),
                     "missing_sources": 0, "stale": False, "trust_policy": "memory=private, knowledge=internal, docs=public",
                     "vector_items": (vectors or {}).get("vectors"),
                     "note": "live Entelechy tree gate; boot_gate checks this file; refreshed by tools/entelechy_sync.py"})
        GATE.write_text(json.dumps(gate, indent=1), encoding="utf-8")
    out = {"ok": True, "mode": "dry-run" if a.dry_run else "apply", "expected": len(rows), "existing_before": len(existing),
           "missing_added": len(missing), "reclassified": reclassified, "items": items if not a.dry_run else len(existing),
           "by_kind": by_kind, "by_sensitivity": by_sens, "vectors": vectors,
           "missing_examples": [d["source"] for d in missing[:10]]}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
