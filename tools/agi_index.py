#!/usr/bin/env python3
"""agi_index.py - prototype of the beta memory index: one SQLite file, hybrid FTS5 + vector-ready schema.

Normalizes the current memory (MEMORY.md lines, knowledge docs, docs) into a single queryable index with
provenance and hashes. This is the "index database implementation" for the LLM-runtime-native core: the LLM
recalls via a small verb instead of loading scattered JSON/Markdown.

usage:
    python tools/agi_index.py --build [--db state/index/agi.db]
    python tools/agi_index.py --query "alive DNA" [--db state/index/agi.db]
"""
import argparse
import hashlib
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def docs():
    out = []
    mem = ROOT / "memory" / "MEMORY.md"
    if mem.is_file():
        for i, ln in enumerate(mem.read_text(encoding="utf-8").splitlines()):
            if ln.strip():
                out.append({"kind": "memory", "source": "memory/MEMORY.md:%d" % (i + 1), "body": ln.strip()})
    for p in sorted((ROOT / "memory" / "knowledge").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for i, chunk in enumerate([c.strip() for c in text.split("\n\n") if c.strip()]):
            out.append({"kind": "knowledge", "source": "%s:%d" % (p.relative_to(ROOT).as_posix(), i + 1),
                        "body": chunk})
    for p in sorted((ROOT / "docs").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        out.append({"kind": "doc", "source": p.relative_to(ROOT).as_posix(), "body": text})
    return out


def build(db_path=None):
    db = pathlib.Path(db_path or ROOT / "state" / "index" / "agi.db")
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db))
    con.executescript("""
      PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, kind TEXT, source TEXT, sha256 TEXT, ts TEXT,
                                       trust TEXT, sensitivity TEXT, body TEXT,
                                       adopted_at TEXT, adopted_by TEXT, provenance TEXT);
      CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(body, source, kind, tokenize='porter');
      CREATE TABLE IF NOT EXISTS items_vec(id INTEGER PRIMARY KEY, dim INTEGER, embedding BLOB);
      CREATE TABLE IF NOT EXISTS links(src TEXT, dst TEXT, rel TEXT);
      CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY, nonce TEXT UNIQUE, action TEXT, args_json TEXT,
                                         status TEXT, created TEXT, expires TEXT);
      DELETE FROM items; DELETE FROM items_fts;
    """)
    cols = {r[1] for r in con.execute("PRAGMA table_info(items)").fetchall()}
    for col in ("adopted_at", "adopted_by", "provenance"):
        if col not in cols:
            con.execute("ALTER TABLE items ADD COLUMN %s TEXT" % col)
    rows = docs()
    for d in rows:
        import time as _time
        prov = json.dumps({"review": "bulk-import", "source": "live-corpus", "adopted_by": "agi_index--build"})
        cur = con.execute("INSERT INTO items(kind,source,sha256,ts,trust,sensitivity,body,adopted_at,adopted_by,provenance) "
                          "VALUES(?,?,?,?,?,?,?,?,?,?)",
                          (d["kind"], d["source"], _sha(d["body"]), "", "verified" if d["kind"] != "doc" else "public",
                           "private" if d["kind"] == "memory" else "internal", d["body"],
                           _time.strftime("%Y-%m-%dT%H:%M:%S"), "agi_index--build", prov))
        con.execute("INSERT INTO items_fts(rowid, body, source, kind) VALUES(?,?,?,?)",
                    (cur.lastrowid, d["body"], d["source"], d["kind"]))
    con.commit()
    counts = dict(con.execute("SELECT kind, count(*) FROM items GROUP BY kind").fetchall())
    con.close()
    return {"ok": True, "db": str(db), "items": len(rows), "by_kind": counts, "fts5": True, "vector": "sqlite-vec ready (schema present)"}


def query(text, db_path=None, k=5):
    db = pathlib.Path(db_path or ROOT / "state" / "index" / "agi.db")
    con = sqlite3.connect(str(db))
    rows = con.execute("SELECT i.source, i.kind, i.body, bm25(items_fts) AS rank FROM items_fts "
                       "JOIN items i ON i.id = items_fts.rowid WHERE items_fts MATCH ? "
                       "ORDER BY rank LIMIT ?", (text, k)).fetchall()
    con.close()
    return {"ok": True, "query": text,
            "hits": [{"source": s, "kind": kd, "rank": round(r, 4), "snippet": body[:200]} for s, kd, body, r in rows]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="beta memory index prototype (SQLite FTS5 hybrid)")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--query", metavar="TEXT")
    ap.add_argument("--db", default=None)
    a = ap.parse_args(argv)
    if a.build:
        print(json.dumps(build(a.db), indent=1)); return 0
    if a.query:
        print(json.dumps(query(a.query, a.db), indent=1)); return 0
    print("usage: --build | --query TEXT"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
