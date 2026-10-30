# AGI Entelechy beta 4 - user manual (minimal)

## Runtime
```
python runtime/agi_runtime.py --root <sandbox> --status
python runtime/agi_runtime.py --root <sandbox> --index-vectors
```
10 verbs; writes are intents; Master approval is local-only; fetch/exec denied; recall fuses FTS5 + vector
(hash-vector fallback, `sqlite-vec` when present) and reports the backend.

## Bridge & MCP
```
python runtime/agi_bridge.py --root <sandbox> --init-token
python runtime/agi_bridge.py --root <sandbox> --serve --port 8766
```
Loopback only; bearer tokens with read/write scopes. POST /mcp JSON-RPC: initialize (session header), tools/list
(10 tools), tools/call, ping. JSON by default; add `Accept: text/event-stream` for SSE responses
(`event: message`); GET /mcp with SSE Accept returns a keepalive ping stream. Remote approve_intent is refused.

## Conformance
```
python runtime/agi_conformance.py --root <sandbox> --out conformance.json
```
C-beta1..C-beta8: identity, DNA integrity, contract, runtime, recall, intents, Sensorium, bridge/approval
locality/scopes/loopback, budgets. Verdict PASS required before adoption experiments.

## Safety
No inbound public port, no remote approval, no destructive migration. Beta is a research artifact.
