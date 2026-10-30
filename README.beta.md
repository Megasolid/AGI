# AGI Entelechy beta 8 (v4.0.0-beta.8)

Fourth generation AGI skill: signed DNA v4, one SQLite memory index (FTS5 + vector leg), thin MCP-shaped runtime,
AGI Sensorium, loopback MCP bridge with JSON/SSE/event-stream, migration dry-run + rollback, tunnel planner, and
(beta 8) **remote seat enrollment**, **Master-signed passports**, a **beta changelog**, and a conformance matrix that
now spans **C-beta1..C-beta19 (20 checks)**. Public beta. Stable gen3.5 (`dna-GCACGAGGCTGT`) remains default.

## In this asset
- `runtime/agi_runtime.py` - 10 typed verbs; intents + local Master approval; FTS5 + hash-vector RRF recall.
- `runtime/agi_bridge.py` - MCP with **16 tools** (incl. `seat_enroll`, `seat_status`, `passport_list`,
  `passport_verify`); remote `approve_intent` refused; event stream replay + `?window=0` unbounded.
- `runtime/agi_seats.py` - Ed25519 public-key seats (device private key; HMAC fallback), challenge-response,
  single-use nonces, replay blocked.
- `runtime/agi_master.py` - local Master Ed25519 ceremony (`state/master.key` 0600 + `state/master_pub.json`),
  file sign/verify, tamper rejected.
- `runtime/agi_passport.py` - **Master-signed passports** binding member + gen_id + DNA sha + seat public key;
  verification cross-checks signature, issuer, DNA and seat.
- `runtime/agi_migrate.py` - dry-run/apply + snapshot/restore rollback proof.
- `runtime/agi_tunnel.py` - plan-only tunnel helper (no ingress auto-opened).
- `runtime/agi_conformance.py` - C-beta1..C-beta19 (20 checks).
- `CHANGELOG.beta.md`, signed DNA v4 + seed, docs.

## Verified
Windows + Linux (WSL2 6.18 / Python 3.10) cold boots PASS. Suites: runtime 15/15, beta_2 13/13, beta_3 13/13,
beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, beta_8 10/10, proposal 12/12, sensorium 9/9; conformance 20/20.

## Limits
Ed25519/Master features need `cryptography`. Tunnel E2E remains **blocked** on this host (no cloudflared/tailscale
binary; WARP is not an ingress tunnel), so only the outbound relay mailbox is proven end-to-end. Master key is a
local file (no HSM). No destructive migration of live state; no license chosen.
