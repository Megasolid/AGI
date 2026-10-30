# AGI Entelechy beta 3 - user manual (minimal)

## Run
```
python runtime/agi_runtime.py --root <sandbox> --status
python runtime/agi_runtime.py --root <sandbox> --index-vectors
python runtime/agi_bridge.py --root <sandbox> --init-token
python runtime/agi_bridge.py --root <sandbox> --serve --port 8766
```

## HTTP surface (loopback only)
- `GET /health` open; `GET /status`, `GET /intent/<id>` need read scope; `POST /intent` needs write scope.
- `POST /mcp` JSON-RPC 2.0: `initialize`, `tools/list`, `tools/call`, `ping`; responses carry `Mcp-Session-Id`.
- `GET /mcp` returns 405 (SSE streaming not in beta.3).

## Safety
Intents queue; only a local Master approves them; MCP `approve_intent` is refused by design. No inbound public port;
the outbound relay mailbox (`--relay <dir>`) simulates a tunnel. fetch/exec remain denied.

## Recall
FTS5 always; after `--index-vectors` recall fuses a 128-dim hash-vector with RRF and reports
`fusion: rrf(fts5,hash-vector)`.

## Verified environments
Windows (project venv) and Linux WSL2 kernel 6.18 / Python 3.10.12 - cold-copy boot PASS on both.
