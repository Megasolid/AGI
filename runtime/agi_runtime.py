#!/usr/bin/env python3
"""agi_runtime - AGI Entelechy beta runtime adapter (MCP-shaped, stdlib only).

Thin stateless adapter: 10 typed verbs over the memory index. Reads are direct; writes are queued
INTENTS that require Master approval (execute-once). The DNA contract is data, not logic.

Transport for beta: newline-delimited JSON-RPC-like requests on stdio:
    {"id":1,"method":"recall","params":{"query":"alive DNA","k":3}}
    -> {"id":1,"result":{...}}
Optional: import Runtime and call handle() directly (tests do this).

Usage:
    python runtime/agi_runtime.py --root <beta-sandbox> --status
    python runtime/agi_runtime.py --root <beta-sandbox> --serve        # stdio loop
"""
import argparse
import array
import hashlib
import json
import math
import pathlib
import re
import secrets
import sqlite3
import sys
from datetime import datetime, timezone

SCHEMA = "agi-runtime/1"
VERBS = ("status", "recall", "remember", "boot", "propose_intent", "poll_intent", "approve_intent", "fetch",
         "snapshot", "evolve_propose", "export_metadata")
WRITE_ACTIONS = ("remember", "snapshot", "boot_note")
FORBIDDEN_ACTIONS = ("fetch", "exec", "shell")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


class Runtime:
    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        self.state = self.root / "state"
        self.state.mkdir(parents=True, exist_ok=True)
        self.db = self.state / "agi.db"
        self._init_db()
        self.dna = self._load_dna()

    # ---------------------------------------------------------------- db
    def _con(self):
        con = sqlite3.connect(str(self.db))
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self):
        con = self._con()
        con.executescript("""
          PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, kind TEXT, source TEXT, sha256 TEXT, ts TEXT,
                                           trust TEXT, sensitivity TEXT, body TEXT);
          CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(body, source, kind, tokenize='porter');
          CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY, nonce TEXT UNIQUE, action TEXT, args_json TEXT,
                                             status TEXT, created TEXT, decided TEXT, decision TEXT, result_json TEXT);
          CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY, intent_id TEXT, actor TEXT, decision TEXT,
                                               note TEXT, ts TEXT);
          CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY, ts TEXT, digest TEXT, note TEXT);
          CREATE TABLE IF NOT EXISTS items_vec(id INTEGER PRIMARY KEY, dim INTEGER, embedding BLOB);
        """)
        # migrate older index-prototype DBs that already had a bare intents table
        cols = {r[1] for r in con.execute("PRAGMA table_info(intents)").fetchall()}
        for col in ("decided", "decision", "result_json", "expires"):
            if col not in cols:
                con.execute("ALTER TABLE intents ADD COLUMN %s TEXT" % col)
        con.commit()
        con.close()

    def _load_dna(self):
        p = self.root / "core" / "dna.v4.json"
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            d = {}
        if not d and (self.root / "dna.v4.json").is_file():
            d = json.loads((self.root / "dna.v4.json").read_text(encoding="utf-8"))
        return d

    # ------------------------------------------------------------- verbs
    def status(self):
        con = self._con()
        items = con.execute("SELECT count(*) FROM items").fetchone()[0]
        pending = con.execute("SELECT count(*) FROM intents WHERE status='pending'").fetchone()[0]
        con.close()
        perc = self.root / "sensorium" / "scene.digest.txt"
        perc_text = perc.read_text(encoding="utf-8") if perc.is_file() else ""
        return {"ok": True, "schema": SCHEMA, "generation": self.dna.get("generation", {}).get("name"),
                "dna_version": self.dna.get("generation", {}).get("dna_version"),
                "gen_id": self.dna.get("generation", {}).get("gen_id"),
                "index_items": items, "pending_intents": pending,
                "recall_backend": self._vec_backend(),
                "sensorium": {"present": bool(perc_text), "digest_first_line": perc_text.splitlines()[0] if perc_text else None,
                              "digest_sha256": _sha(perc_text.encode()) if perc_text else None},
                "ts": _now()}

    def _vec_backend(self):
        con = self._con()
        try:
            con.execute("SELECT vec_version()").fetchone()
            return "sqlite-vec"
        except sqlite3.Error:
            pass
        try:
            n = con.execute("SELECT count(*) FROM items_vec").fetchone()[0]
        except sqlite3.Error:
            n = 0
        finally:
            con.close()
        return "hash-vector" if n else "fts5"

    def recall(self, query, k=5):
        if not query:
            return {"ok": False, "error": "query required"}
        con = self._con()
        rows = con.execute("SELECT i.source, i.kind, i.body, bm25(items_fts) AS rank FROM items_fts "
                           "JOIN items i ON i.id = items_fts.rowid WHERE items_fts MATCH ? "
                           "ORDER BY rank LIMIT ?", (str(query), int(k))).fetchall()
        con.close()
        fts = [{"source": r["source"], "kind": r["kind"], "rank": round(r["rank"], 4),
                "snippet": (r["body"] or "")[:200]} for r in rows]
        vec = self._vector_hits(query, int(k))
        if vec:
            return {"ok": True, "query": query, "k": int(k), "fusion": "rrf(fts5,hash-vector)",
                    "hits": self._rrf(fts, vec, int(k))}
        return {"ok": True, "query": query, "k": int(k), "fusion": "fts5", "hits": fts}

    # --- optional vector leg (stdlib hash-vector; sqlite-vec can replace it) ---
    def _embed(self, text, dim=128):
        vec = [0.0] * dim
        for tok in re.findall(r"[a-z0-9_]+", str(text).lower()):
            h = hashlib.sha256(tok.encode()).digest()
            vec[int.from_bytes(h[:2], "big") % dim] += 1.0 if h[2] & 1 else -1.0
        n = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / n for v in vec]

    def index_vectors(self):
        con = self._con()
        items = con.execute("SELECT id, body FROM items").fetchall()
        con.execute("DELETE FROM items_vec")
        for it in items:
            v = array.array("f", self._embed(it["body"]))
            con.execute("INSERT INTO items_vec(id, dim, embedding) VALUES(?,?,?)",
                        (it["id"], len(v), v.tobytes()))
        con.commit()
        n = con.execute("SELECT count(*) FROM items_vec").fetchone()[0]
        con.close()
        return {"ok": True, "vectors": n, "dim": 128, "backend": self._vec_backend()}

    def _vector_hits(self, query, k=5):
        con = self._con()
        try:
            rows = con.execute("SELECT v.id, v.embedding, i.source, i.kind, i.body FROM items_vec v "
                               "JOIN items i ON i.id = v.id").fetchall()
        except sqlite3.Error:
            rows = []
        con.close()
        if not rows:
            return []
        q = self._embed(query)
        scored = []
        for r in rows:
            v = array.array("f")
            v.frombytes(r["embedding"])
            if len(v) != len(q):
                continue
            cos = sum(a * b for a, b in zip(q, v))
            if cos > 0.05:
                scored.append((cos, r))
        scored.sort(key=lambda x: -x[0])
        return [{"source": r["source"], "kind": r["kind"], "rank": round(-cos, 4),
                 "snippet": (r["body"] or "")[:200], "vector_score": round(cos, 3)}
                for cos, r in scored[:k]]

    def _rrf(self, fts, vec, k=5):
        scores = {}
        for lst in (fts, vec):
            for i, h in enumerate(lst):
                key = (h["source"], h["kind"])
                scores[key] = scores.get(key, 0.0) + 1.0 / (60 + i + 1)
        merged, seen = [], set()
        for h in fts + vec:
            key = (h["source"], h["kind"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(dict(h, fused_score=round(scores[key], 5)))
        merged.sort(key=lambda x: -x["fused_score"])
        return merged[:k]

    def propose_intent(self, action, args=None, nonce=None):
        action = str(action or "")
        if action not in WRITE_ACTIONS and action not in FORBIDDEN_ACTIONS and action != "evolve":
            return {"ok": False, "error": "unknown action %r" % action}
        nonce = str(nonce or secrets.token_hex(8))
        con = self._con()
        row = con.execute("SELECT id FROM intents WHERE nonce=?", (nonce,)).fetchone()
        if row:
            con.close()
            return {"ok": True, "id": row["id"], "nonce": nonce, "idempotent": True}
        iid = "int-" + secrets.token_hex(6)
        con.execute("INSERT INTO intents(id,nonce,action,args_json,status,created) VALUES(?,?,?,?, 'pending', ?)",
                    (iid, nonce, action, json.dumps(args or {}, sort_keys=True), _now()))
        con.commit()
        con.close()
        return {"ok": True, "id": iid, "nonce": nonce, "action": action, "status": "pending",
                "note": "write queued; requires Master approval"}

    def poll_intent(self, intent_id=None):
        con = self._con()
        if intent_id:
            row = con.execute("SELECT * FROM intents WHERE id=?", (str(intent_id),)).fetchone()
            con.close()
            return {"ok": bool(row), "intent": dict(row) if row else None}
        rows = con.execute("SELECT * FROM intents ORDER BY created DESC LIMIT 20").fetchall()
        con.close()
        return {"ok": True, "intents": [dict(r) for r in rows]}

    def approve_intent(self, intent_id, actor="Master"):
        con = self._con()

        def _deny(iid, reason):
            aid = "dec-" + secrets.token_hex(6)
            con.execute("INSERT INTO decisions(id,intent_id,actor,decision,note,ts) VALUES(?,?,?,?,?,?)",
                        (aid, str(iid) if iid else None, str(actor), "denied", str(reason)[:500], _now()))
            con.commit()
            return {"ok": False, "error": reason, "denied": True, "reason": reason, "audit_id": aid}

        try:
            if str(actor) != "Master":
                return _deny(intent_id, "only Master may approve intents")
            row = con.execute("SELECT * FROM intents WHERE id=?", (str(intent_id),)).fetchone()
            if not row:
                return _deny(intent_id, "unknown intent")
            if row["status"] != "pending":
                return _deny(row["id"], "intent already %s" % row["status"])
            action, args = row["action"], json.loads(row["args_json"] or "{}")
            if action in FORBIDDEN_ACTIONS:
                con.execute("UPDATE intents SET status='denied', decided=?, decision=? WHERE id=?",
                            (_now(), "denied (unsafe action in beta)", row["id"]))
                con.execute("INSERT INTO decisions(id,intent_id,actor,decision,note,ts) VALUES(?,?,?,?,?,?)",
                            ("dec-" + secrets.token_hex(6), row["id"], "Master", "denied", "fetch/exec disabled in beta.1", _now()))
                con.commit()
                return {"ok": False, "error": "action %r is not executable in beta.1 (bridge arrives later)" % action,
                        "intent": row["id"], "status": "denied"}
            if action == "remember":
                body = str(args.get("text") or "").strip()
                if not body:
                    return _deny(row["id"], "remember needs text")
                kind = str(args.get("kind") or "memory")
                source = str(args.get("source") or "runtime-intent:" + row["id"])
                cur = con.execute("INSERT INTO items(kind,source,sha256,ts,trust,sensitivity,body) VALUES(?,?,?,?,?,?,?)",
                                  (kind, source, _sha(body.encode()), _now(), "verified", "internal", body))
                con.execute("INSERT INTO items_fts(rowid, body, source, kind) VALUES(?,?,?,?)",
                            (cur.lastrowid, body, source, kind))
                result = {"stored": True, "source": source, "sha256": _sha(body.encode())}
            elif action == "snapshot":
                sid = "snap-" + secrets.token_hex(5)
                raw_note = str(args.get("note") or "")
                note_sha = _sha(raw_note.encode()) if raw_note else None
                ts_now = _now()
                digest = _sha(json.dumps({"ts": ts_now, "note_sha256": note_sha}).encode())
                con.execute("INSERT INTO snapshots(id,ts,digest,note) VALUES(?,?,?,?)",
                            (sid, ts_now, digest, "[redacted]" if raw_note else ""))
                result = {"snapshot": sid, "digest": digest, "note_redacted": True}
            else:
                result = {"noted": True, "action": action}
            con.execute("UPDATE intents SET status='approved', decided=?, decision=?, result_json=? WHERE id=?",
                        (_now(), "approved by Master", json.dumps(result), row["id"]))
            con.execute("INSERT INTO decisions(id,intent_id,actor,decision,note,ts) VALUES(?,?,?,?,?,?)",
                        ("dec-" + secrets.token_hex(6), row["id"], "Master", "approved", action, _now()))
            con.commit()
            return {"ok": True, "intent": row["id"], "action": action, "executed": True, "result": result}
        finally:
            con.close()

    def export_metadata(self, kind=None, limit=200):
        """Metadata-only export: allowlisted fields, never bodies or private memory."""
        allow = ("id", "kind", "source", "sha256", "ts", "trust", "sensitivity")
        con = self._con()
        try:
            lim = max(1, min(int(limit or 200), 1000))
            sql = "SELECT " + ", ".join(allow) + " FROM items"
            args = []
            if kind:
                sql += " WHERE kind=?"
                args.append(str(kind))
            sql += " ORDER BY id LIMIT ?"
            args.append(lim)
            rows = con.execute(sql, args).fetchall()
            items = [{k: row[k] for k in allow} for row in rows]
            return {"ok": True, "schema": "agi-export-metadata/1", "mode": "metadata_only",
                    "redacted": True, "private_bodies": False, "count": len(items), "items": items}
        finally:
            con.close()

    def fetch(self, url):
        return {"ok": True, **self.propose_intent("fetch", {"url": str(url)}, nonce="fetch-" + _sha(url.encode())[:16]),
                "bridge": "inbound disabled; queued for the outbound relay (beta.2)"}

    def snapshot(self, note=""):
        r = self.propose_intent("snapshot", {"note": note})
        return {"ok": True, "queued": r, "note": "snapshot is a write -> needs Master approval"}

    def evolve_propose(self, genome):
        rules = (genome or {}).get("rules") if isinstance(genome, dict) else None
        if not isinstance(rules, list) or not rules:
            return {"ok": False, "error": "genome.rules list required"}
        problems = []
        for r in rules:
            if not isinstance(r, dict) or not all(k in r for k in ("trigger", "env", "reaction")):
                problems.append("rule must have trigger/env/reaction")
        if len(rules) < 12:
            problems.append("DNA v4 requires >=12 reactive rules")
        return {"ok": not problems, "problems": problems, "rules": len(rules),
                "note": "proposal only; DNA mutation requires Master sign-off (dna_version bump)"}

    def boot(self):
        p = self.state / "boot.json"
        rec = {"schema": "agi-runtime/boot/1", "state": "ready", "boot": "S0-S8", "ts": _now(),
               "gen_id": self.dna.get("generation", {}).get("gen_id"),
               "dna_sha256": _sha(json.dumps(self.dna, sort_keys=True).encode()) if self.dna else None}
        p.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        return {"ok": True, **rec}

    # ------------------------------------------------------------ dispatch
    def handle(self, method, params=None):
        params = params or {}
        try:
            if method == "status":
                return self.status()
            if method == "recall":
                return self.recall(params.get("query", ""), params.get("k", 5))
            if method == "remember":
                return {"ok": True, "queued": self.propose_intent("remember", params,
                                                                  nonce=params.get("nonce"))}
            if method == "boot":
                return self.boot()
            if method == "propose_intent":
                return self.propose_intent(params.get("action"), params.get("args"), params.get("nonce"))
            if method == "poll_intent":
                return self.poll_intent(params.get("id"))
            if method == "approve_intent":
                return self.approve_intent(params.get("id"), params.get("actor", "Master"))
            if method == "fetch":
                return self.fetch(params.get("url", ""))
            if method == "snapshot":
                return self.snapshot(params.get("note", ""))
            if method == "evolve_propose":
                return self.evolve_propose(params.get("genome"))
            if method == "export_metadata":
                return self.export_metadata(params.get("kind"), params.get("limit", 200))
            return {"ok": False, "error": "unknown method %r (known: %s)" % (method, ",".join(VERBS))}
        except Exception as e:
            return {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}


def serve(root):
    rt = Runtime(root)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            print(json.dumps({"error": "bad json"}), flush=True)
            continue
        res = rt.handle(req.get("method"), req.get("params"))
        print(json.dumps({"id": req.get("id"), "result": res}), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="AGI Entelechy beta runtime (MCP-shaped, stdlib)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--index-vectors", action="store_true", help="build the optional hash-vector recall leg")
    a = ap.parse_args(argv)
    if a.serve:
        serve(a.root)
        return 0
    rt = Runtime(a.root)
    if a.index_vectors:
        print(json.dumps(rt.index_vectors(), indent=1))
        return 0
    print(json.dumps(rt.handle("status"), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
