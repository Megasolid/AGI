# AGI Entelechy beta 5 (v4.0.0-beta.5)

Fourth generation AGI skill: signed DNA v4, one SQLite memory index (FTS5 + vector leg), thin MCP-shaped runtime,
AGI Sensorium perception layer, loopback intent bridge, MCP JSON/SSE transport, beta conformance matrix, and
(beta 5) a **long-lived MCP event stream**, **memory migration dry-run**, and a **tunnel readiness planner**.
Public beta. Stable gen3.5 (`dna-GCACGAGGCTGT`) remains default; the beta never migrates live state.

## In this asset
- `runtime/agi_runtime.py` - 10 typed verbs; intents + Master approval; FTS5 + hash-vector RRF recall
  (backend reported; `sqlite-vec` when present).
- `runtime/agi_bridge.py` - loopback bridge: scoped bearer tokens, outbound relay mailbox, MCP JSON + SSE,
  `GET /mcp` event stream with `Last-Event-ID` replay + live events + heartbeats; remote approval refused.
- `runtime/agi_migrate.py` - gen3.5 memory -> beta index, **dry-run by default**, source read-only.
- `runtime/agi_tunnel.py` - tunnel readiness/plan only (cloudflared/tailscale), security policy printed, never
  opens ingress.
- `runtime/agi_conformance.py` - C-beta1..C-beta11 matrix (identity, integrity, contract, runtime, recall, intents,
  Sensorium, bridge, event bus, migration read-only, tunnel plan, budgets).
- `core/dna.v4.json` (+sig), signed seed, docs.

## Verified
Windows + Linux (WSL2 6.18 / Python 3.10) cold boots PASS. Suites: runtime 15/15, beta_2 13/13, beta_3 13/13,
beta_4 10/10, beta_5 10/10, proposal 12/12, sensorium 9/9. Conformance matrix PASS 12/12.

## Limits
SSE stream is a bounded keepalive window (6 s) with replay, not an unbounded push bus; migration is dry-run/apply
to a beta index only (no beta.1 destructive migration of live state); no tunnel is auto-started; no key ceremony;
no license chosen.
