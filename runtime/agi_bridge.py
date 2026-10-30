#!/usr/bin/env python3
"""agi_bridge - AGI Entelechy beta.3 intent bridge (loopback HTTP + outbound relay mailbox + MCP transport).

Design (beta.3):
  * Loopback-only HTTP surface bound to 127.0.0.1 with bearer tokens and scopes (`read`, `write`).
    No inbound public port; a tunnel is expected to reach it only through an authenticated outbound relay.
  * Outbound relay mailbox: the bridge polls a directory of JSON requests and writes results back - this
    simulates a tunnel/relay without opening any ingress (used by tests and the Golden Circle simulation).
  * MCP Streamable HTTP (JSON response mode): POST /mcp with JSON-RPC 2.0 (initialize, tools/list, tools/call,
    ping). `approve_intent` is always denied remotely: approval is local-only (Master).

Endpoints:
  GET  /health                 (no auth)  -> generation, dna_version
  GET  /status                 (read)     -> runtime status
  GET  /intent/<id>            (read)     -> intent poll
  POST /intent {"action":...}  (write)    -> queue an intent (execute-once requires Master approval)
  POST /mcp    JSON-RPC 2.0    (read, write for write tools) -> MCP tools

The bridge never executes intents by itself; it only exposes the runtime's intent queue and remote approval is
forbidden by design.

CLI:
  python runtime/agi_bridge.py --root <sandbox> --init-token [--scopes read,write]
  python runtime/agi_bridge.py --root <sandbox> --serve [--port 8766]
  python runtime/agi_bridge.py --root <sandbox> --relay <dir> [--once]
"""
import argparse
import hashlib
import hmac
import json
import pathlib
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agi_runtime  # noqa: E402

SCHEMA = "agi-runtime-bridge/1"
SCOPES = ("read", "write")
MCP_PROTOCOL = "2025-06-18"
SSE_DEFAULT_WINDOW = 6.0   # bounded by default; ?window=0 means unbounded (client closes)
SSE_UNBOUNDED = 0.0

# scope required per tool; approve_intent is intentionally absent (local-only)
TOOL_SCOPES = {"status": "read", "recall": "read", "poll_intent": "read", "evolve_propose": "read",
               "remember": "write", "boot": "write", "propose_intent": "write", "fetch": "write",
               "snapshot": "write", "seat_challenge": "read", "seat_login": "read"}
TOOL_SPECS = [
    {"name": "status", "description": "runtime + sensorium status",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "recall", "description": "hybrid FTS5+vector memory recall",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "k": {"type": "integer"}},
                     "required": ["query"]}},
    {"name": "remember", "description": "queue a memory write intent (Master approval)",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "boot", "description": "write the boot-ready record",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "propose_intent", "description": "queue a write intent",
     "inputSchema": {"type": "object", "properties": {"action": {"type": "string"},
                                                       "args": {"type": "object"}, "nonce": {"type": "string"}}}},
    {"name": "poll_intent", "description": "poll an intent",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}}},
    {"name": "fetch", "description": "queue an outbound fetch intent (denied execution in beta)",
     "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}}},
    {"name": "snapshot", "description": "queue a snapshot intent",
     "inputSchema": {"type": "object", "properties": {"note": {"type": "string"}}}},
    {"name": "evolve_propose", "description": "validate a reactive-DNA genome proposal (read-only)",
     "inputSchema": {"type": "object", "properties": {"genome": {"type": "object"}}}},
    {"name": "seat_challenge", "description": "issue a device-key seat challenge (beta.7)",
     "inputSchema": {"type": "object", "properties": {"member": {"type": "string"}}, "required": ["member"]}},
    {"name": "seat_login", "description": "verify a seat signature over its challenge (beta.7)",
     "inputSchema": {"type": "object", "properties": {"member": {"type": "string"}, "nonce": {"type": "string"},
                                                       "proof": {"type": "string"}},
                     "required": ["member", "nonce", "proof"]}},
    {"name": "approve_intent", "description": "DENIED remotely: Master approval is local-only",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}}},
]


class Bridge:
    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        self.rt = agi_runtime.Runtime(self.root)
        self.token_path = self.root / "state" / "bridge_token.json"
        self.events_path = self.root / "state" / "bridge_events.jsonl"
        self.seq_path = self.root / "state" / "bridge_events_seq.json"

    # ------------------------------------------------------------- tokens
    def init_token(self, scopes=("read", "write")):
        tok = "agi-" + secrets.token_urlsafe(24)
        rec = {"schema": "agi-bridge-token/1", "sha256": hashlib.sha256(tok.encode()).hexdigest(),
               "scopes": [s for s in scopes if s in SCOPES], "created": agi_runtime._now(),
               "note": "bearer token; only this hash is stored"}
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        return {"ok": True, "token": tok, "scopes": rec["scopes"], "token_file": str(self.token_path),
                "note": "shown once; keep it secret"}

    def _token_scopes(self, header):
        if not self.token_path.is_file():
            return False, "no token initialised", []
        rec = json.loads(self.token_path.read_text(encoding="utf-8"))
        if not header or not header.startswith("Bearer "):
            return False, "missing bearer token", []
        got = hashlib.sha256(header[7:].strip().encode()).hexdigest()
        if not hmac.compare_digest(got, rec.get("sha256", "")):
            return False, "invalid token", []
        return True, None, list(rec.get("scopes") or [])

    def _check(self, header, scope):
        ok, err, scopes = self._token_scopes(header)
        if not ok:
            return False, err
        if scope not in scopes:
            return False, "token lacks scope %r" % scope
        return True, None

    # --------------------------------------------------------- event bus
    def _next_seq(self):
        try:
            seq = int(json.loads(self.seq_path.read_text(encoding="utf-8")).get("seq") or 0)
        except Exception:
            seq = 0
        seq += 1
        self.seq_path.parent.mkdir(parents=True, exist_ok=True)
        self.seq_path.write_text(json.dumps({"seq": seq}), encoding="utf-8")
        return seq

    def publish(self, etype, data):
        rec = {"seq": self._next_seq(), "ts": agi_runtime._now(), "type": etype, "data": data}
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.events_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def replay(self, last_event_id=0, limit=100):
        out = []
        if not self.events_path.is_file():
            return out
        for line in self.events_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if int(rec.get("seq") or 0) > int(last_event_id):
                out.append(rec)
        return out[-int(limit):]

    # ------------------------------------------------------------- MCP
    def mcp(self, req, scopes):
        """One JSON-RPC request -> (response_dict_or_None, new_session_id_or_None)."""
        if not isinstance(req, dict):
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}, None
        rid = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}

        def ok(result):
            return {"jsonrpc": "2.0", "id": rid, "result": result}

        def err(code, msg):
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": msg}}

        if method == "initialize":
            sid = "mcp-" + secrets.token_hex(8)
            return ok({"protocolVersion": MCP_PROTOCOL,
                       "capabilities": {"tools": {"listChanged": False}},
                       "serverInfo": {"name": "agi-entelechy-beta", "version": "0.3",
                                      "generation": self.rt.dna.get("generation", {}).get("name"),
                                      "dna_version": self.rt.dna.get("generation", {}).get("dna_version")}}), sid
        if method == "notifications/initialized":
            return None, None
        if method == "ping":
            return ok({}), None
        if method == "tools/list":
            return ok({"tools": TOOL_SPECS}), None
        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            if name not in TOOL_SCOPES:
                if name == "approve_intent":
                    return err(-32003, "approve_intent is local-only: Master approval cannot be delegated over the bridge"), None
                return err(-32602, "unknown tool %r" % name), None
            need = TOOL_SCOPES[name]
            if need not in scopes:
                return err(-32001, "token lacks %r scope for tool %r" % (need, name)), None
            if name in ("seat_challenge", "seat_login"):
                import agi_seats
                s = agi_seats.Seats(self.root)
                if name == "seat_challenge":
                    res = s.challenge(args.get("member"))
                else:
                    res = s.login(args.get("member"), args.get("nonce"), args.get("proof"))
            else:
                res = self.rt.handle(name, args)
            if name in ("remember", "propose_intent", "snapshot", "fetch") and res.get("ok"):
                iid = res.get("id") or (res.get("queued") or {}).get("id")
                self.publish("tool_call", {"tool": name, "intent_id": iid, "status": res.get("status") or "queued"})
            return ok({"content": [{"type": "text", "text": json.dumps(res, sort_keys=True)}],
                       "isError": not bool(res.get("ok"))}), None
        return err(-32601, "method not found: %r" % method), None

    # ------------------------------------------------------------- routes
    def health(self):
        return {"ok": True, "schema": SCHEMA, "generation": self.rt.dna.get("generation", {}).get("name"),
                "dna_version": self.rt.dna.get("generation", {}).get("dna_version"),
                "mode": "loopback-only", "inbound_public_port": False}

    def status(self):
        return self.rt.handle("status")

    def queue_intent(self, body):
        res = self.rt.handle("propose_intent", {"action": body.get("action"),
                                                "args": body.get("args") or {},
                                                "nonce": body.get("nonce")})
        if res.get("ok"):
            self.publish("intent_queued", {"intent_id": res.get("id"), "action": res.get("action"),
                                           "status": res.get("status"), "idempotent": bool(res.get("idempotent"))})
        return res

    def poll(self, intent_id):
        return self.rt.handle("poll_intent", {"id": intent_id})

    # -------------------------------------------------------------- relay
    def relay_once(self, inbox):
        inbox = pathlib.Path(inbox)
        inbox.mkdir(parents=True, exist_ok=True)
        done = 0
        for req_path in sorted(inbox.glob("*.json")):
            if req_path.name.endswith(".result.json"):
                continue
            try:
                req = json.loads(req_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            rid = req.get("id") or req_path.stem
            method, params = req.get("method"), req.get("params") or {}
            if method == "health":
                res = self.health()
            elif method == "status":
                res = self.status()
            elif method == "propose_intent":
                res = self.queue_intent(params)
            elif method == "poll_intent":
                res = self.poll(params.get("id"))
            else:
                res = {"ok": False, "error": "unknown relay method %r" % method}
            (inbox / (str(rid) + ".result.json")).write_text(
                json.dumps({"schema": "agi-bridge-relay-result/1", "id": rid, "ts": agi_runtime._now(),
                            "result": res}, indent=1), encoding="utf-8")
            req_path.unlink(missing_ok=True)
            done += 1
        return {"ok": True, "handled": done}

    def serve_relay(self, inbox, once=False):
        while True:
            self.relay_once(inbox)
            if once:
                return 0
            time.sleep(2)


def make_handler(bridge):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AGIEntelechyBridge/0.3"

        def _send(self, code, obj, extra=None):
            body = json.dumps(obj, indent=1).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _loopback(self):
            host = self.client_address[0]
            return host in ("127.0.0.1", "::1", "localhost")

        def log_message(self, *args):
            pass

        def _send_sse(self, events, extra=None):
            """Server-Sent Events response: events = [(event_name, data_obj_or_str), ...]."""
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            for name, data in events:
                if not isinstance(data, str):
                    data = json.dumps(data, sort_keys=True)
                self.wfile.write(("event: %s\ndata: %s\n\n" % (name, data)).encode())
                self.wfile.flush()

        def _send_sse_stream(self, sid, last_event_id, window=None):
            """MCP event stream: replay from Last-Event-ID, then live events + heartbeats.
            window is a bounded number of seconds (default SSE_DEFAULT_WINDOW); 0 = unbounded until the client closes."""
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.send_header("Mcp-Session-Id", sid)
            self.end_headers()
            last = int(last_event_id or 0)
            win = SSE_DEFAULT_WINDOW if window is None else float(window)
            try:
                for rec in bridge.replay(last):
                    self.wfile.write(("id: %d\nevent: %s\ndata: %s\n\n"
                                      % (rec["seq"], rec["type"], json.dumps(rec, sort_keys=True))).encode())
                    last = rec["seq"]
                deadline = (time.time() + win) if win and win > 0 else None
                next_ping = time.time() + 2.0
                while deadline is None or time.time() < deadline:
                    fresh = bridge.replay(last)
                    for rec in fresh:
                        self.wfile.write(("id: %d\nevent: %s\ndata: %s\n\n"
                                          % (rec["seq"], rec["type"], json.dumps(rec, sort_keys=True))).encode())
                        last = rec["seq"]
                    if time.time() >= next_ping:
                        self.wfile.write(('event: ping\ndata: {"jsonrpc":"2.0","method":"ping"}\n\n').encode())
                        next_ping = time.time() + 2.0
                    self.wfile.flush()
                    time.sleep(0.2)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                self.close_connection = True

        def do_GET(self):
            if not self._loopback():
                return self._send(403, {"ok": False, "error": "loopback only"})
            path = self.path.split("?")[0]
            if path == "/health":
                return self._send(200, bridge.health())
            if path == "/status":
                ok, err = bridge._check(self.headers.get("Authorization"), "read")
                if not ok:
                    return self._send(401, {"ok": False, "error": err})
                return self._send(200, bridge.status())
            if path.startswith("/intent/"):
                ok, err = bridge._check(self.headers.get("Authorization"), "read")
                if not ok:
                    return self._send(401, {"ok": False, "error": err})
                return self._send(200, bridge.poll(path[len("/intent/"):]))
            if path == "/mcp":
                if "text/event-stream" not in (self.headers.get("Accept") or ""):
                    return self._send(405, {"ok": False, "error": "GET /mcp requires Accept: text/event-stream "
                                                                   "(SSE keepalive) or POST JSON-RPC"},
                                      extra={"Allow": "POST, GET"})
                ok, err, scopes = bridge._token_scopes(self.headers.get("Authorization"))
                if not ok:
                    return self._send(401, {"jsonrpc": "2.0", "id": None,
                                            "error": {"code": -32000, "message": err}})
                sid = self.headers.get("Mcp-Session-Id") or ("mcp-" + secrets.token_hex(8))
                last = self.headers.get("Last-Event-ID") or 0
                if not str(last).isdigit():
                    last = 0
                window = None
                if "?" in self.path:
                    from urllib.parse import parse_qs, urlparse
                    q = parse_qs(urlparse(self.path).query)
                    if "window" in q:
                        try:
                            window = float(q["window"][0])
                        except Exception:
                            window = None
                return self._send_sse_stream(sid, int(last), window)
            return self._send(404, {"ok": False, "error": "not found"})

        def do_POST(self):
            if not self._loopback():
                return self._send(403, {"ok": False, "error": "loopback only"})
            path = self.path.split("?")[0]
            if path == "/mcp":
                ok, err, scopes = bridge._token_scopes(self.headers.get("Authorization"))
                if not ok:
                    return self._send(401, {"jsonrpc": "2.0", "id": None,
                                            "error": {"code": -32000, "message": err}})
                try:
                    n = int(self.headers.get("Content-Length") or 0)
                    req = json.loads(self.rfile.read(n).decode() or "{}")
                except Exception:
                    return self._send(400, {"jsonrpc": "2.0", "id": None,
                                            "error": {"code": -32700, "message": "bad json"}})
                resp, new_sid = bridge.mcp(req, scopes)
                extra = {"Mcp-Session-Id": new_sid} if new_sid else (
                    {"Mcp-Session-Id": self.headers.get("Mcp-Session-Id")}
                    if self.headers.get("Mcp-Session-Id") else None)
                if "text/event-stream" in (self.headers.get("Accept") or ""):
                    if resp is None:
                        return self._send(202, {}, extra=extra)
                    return self._send_sse([("message", resp)], extra=extra)
                if resp is None:
                    return self._send(202, {}, extra=extra)
                return self._send(200, resp, extra=extra)
            if path != "/intent":
                return self._send(404, {"ok": False, "error": "not found"})
            ok, err = bridge._check(self.headers.get("Authorization"), "write")
            if not ok:
                return self._send(401, {"ok": False, "error": err})
            try:
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send(400, {"ok": False, "error": "bad json"})
            if not body.get("action"):
                return self._send(400, {"ok": False, "error": "action required"})
            return self._send(200, bridge.queue_intent(body))

    return Handler


def main(argv=None):
    ap = argparse.ArgumentParser(description="AGI Entelechy beta bridge (loopback + outbound relay)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--init-token", action="store_true")
    ap.add_argument("--scopes", default="read,write")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--relay", default=None, metavar="DIR")
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    b = Bridge(a.root)
    if a.init_token:
        print(json.dumps(b.init_token(tuple(s.strip() for s in a.scopes.split(","))), indent=1))
        return 0
    if a.relay:
        return b.serve_relay(a.relay, once=a.once)
    if a.serve:
        srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(b))
        print(json.dumps({"ok": True, "url": "http://127.0.0.1:%d/" % a.port, "loopback_only": True}, indent=1),
              flush=True)
        srv.serve_forever()
        return 0
    print(json.dumps(b.health(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
