# AGI Entelechy beta 6 (v4.0.0-beta.6)

Fourth generation AGI skill: signed DNA v4, one SQLite memory index (FTS5 + vector leg), thin MCP-shaped runtime,
AGI Sensorium perception layer, loopback intent bridge with MCP JSON/SSE/event-stream, read-only migration dry-run,
tunnel planner, beta conformance matrix, and (beta 6) a **device-key seat ceremony** and **unbounded event streams**.
Public beta. Stable gen3.5 (`dna-GCACGAGGCTGT`) remains default; the beta never migrates live state.

## In this asset
- `runtime/agi_runtime.py` - 10 typed verbs; intents + local Master approval; FTS5 + hash-vector RRF recall
  (backend reported; `sqlite-vec` when present).
- `runtime/agi_bridge.py` - loopback bridge: scoped bearer tokens, outbound relay, MCP JSON + SSE, event stream
  with `Last-Event-ID` replay and live events; `?window=0` keeps the stream open until the client closes
  (default bounded 6 s). Remote approval refused.
- `runtime/agi_seats.py` - **beta 6 device-key seats**: enrollment shows the key once, login is HMAC-SHA256
  challenge-response, nonces single-use/expiring, status never exposes key material.
- `runtime/agi_migrate.py` - gen3.5 memory -> beta index, dry-run default, source hash verified read-only.
- `runtime/agi_tunnel.py` - tunnel plan only; never opens ingress.
- `runtime/agi_conformance.py` - C-beta1..C-beta13 (14 checks), including seats and unbounded window.
- `core/dna.v4.json` (+sig), signed seed, docs.

## Verified
Windows + Linux (WSL2 6.18 / Python 3.10) cold boots PASS. Suites: runtime 15/15, beta_2 13/13, beta_3 13/13,
beta_4 10/10, beta_5 10/10, beta_6 9/9, proposal 12/12, sensorium 9/9. Conformance PASS 14/14.

## Limits
Seat keys are HMAC-SHA256 with the seat secret stored in the local sandbox DB (local-only ceremony; Ed25519/ML-DSA
seats are beta.7). SSE unbounded mode holds a thread per client. No destructive migration; no tunnel auto-start;
no key ceremony for the Master; no license chosen.
