#!/usr/bin/env python3
"""agi_migrate - normalize a gen3.5 live memory into the beta Entelechy index (dry-run by default).

The source tree is read-only. The target is a beta sandbox: dry-run reports what would be imported;
`--apply` writes only into `<target>/state/agi.db` and never touches the source or any live state.
This is the first step of the normalization plan (MEMORY.md lines + knowledge docs -> one SQLite index).

CLI:
    python runtime/agi_migrate.py --source <live AGI> --target <beta sandbox>
    python runtime/agi_migrate.py --source <live AGI> --target <beta sandbox> --apply [--limit N]
"""
import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agi_runtime  # noqa: E402

SCHEMA = "agi-migrate/1"


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def collect(source, limit=None):
    src = pathlib.Path(source).resolve()
    items = []
    mem = src / "memory" / "MEMORY.md"
    if mem.is_file():
        for i, ln in enumerate(mem.read_text(encoding="utf-8", errors="ignore").splitlines()):
            if ln.strip():
                items.append({"kind": "memory", "source": "memory/MEMORY.md:%d" % (i + 1), "body": ln.strip()})
    for p in sorted((src / "memory" / "knowledge").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for i, chunk in enumerate([c.strip() for c in text.split("\n\n") if c.strip()]):
            items.append({"kind": "knowledge", "source": "%s:%d" % (p.relative_to(src).as_posix(), i + 1),
                          "body": chunk[:4000]})
    for p in sorted((src / "docs").glob("*.md")):
        items.append({"kind": "doc", "source": p.relative_to(src).as_posix(),
                      "body": p.read_text(encoding="utf-8", errors="ignore")[:8000]})
    if limit:
        items = items[: int(limit)]
    return src, items


def run(source, target, apply=False, limit=None):
    src, items = collect(source, limit)
    tgt = pathlib.Path(target).resolve()
    if not (tgt / "core" / "dna.v4.json").is_file():
        return {"ok": False, "error": "target is not a beta sandbox (core/dna.v4.json missing)"}
    if src == tgt:
        return {"ok": False, "error": "source and target must differ; live tree is read-only for beta"}
    src_mem = (src / "memory" / "MEMORY.md")
    before = _sha(src_mem.read_text(encoding="utf-8", errors="ignore")) if src_mem.is_file() else None
    rt = agi_runtime.Runtime(tgt)
    db_items = rt.status().get("index_items", 0)
    applied = 0
    if apply:
        con = rt._con()
        for it in items:
            cur = con.execute("INSERT INTO items(kind,source,sha256,ts,trust,sensitivity,body) VALUES(?,?,?,?,?,?,?)",
                              (it["kind"], it["source"], _sha(it["body"]), agi_runtime._now(), "verified", "internal",
                               it["body"]))
            con.execute("INSERT INTO items_fts(rowid, body, source, kind) VALUES(?,?,?,?)",
                        (cur.lastrowid, it["body"], it["source"], it["kind"]))
            applied += 1
        con.commit()
        con.close()
    after = _sha(src_mem.read_text(encoding="utf-8", errors="ignore")) if src_mem.is_file() else None
    return {"ok": True, "schema": SCHEMA, "mode": "apply" if apply else "dry-run",
            "source": str(src), "target": str(tgt), "collected": len(items), "applied": applied,
            "target_items_before": db_items,
            "by_kind": {k: sum(1 for i in items if i["kind"] == k) for k in ("memory", "knowledge", "doc")},
            "preview": [{k: i[k] for k in ("kind", "source")} for i in items[:3]],
            "source_unchanged": before == after, "live_state_touched": False,
            "note": "imports only into the target index; source tree never written"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Normalize gen3.5 memory into a beta index (dry-run default)")
    ap.add_argument("--source", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    r = run(a.source, a.target, a.apply, a.limit)
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
