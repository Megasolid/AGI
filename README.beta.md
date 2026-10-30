# AGI Entelechy beta 10 (v4.0.0-beta.10)

Fourth generation AGI skill: signed DNA v4, SQLite memory index (FTS5 + vector leg), MCP-shaped runtime, AGI
Sensorium, loopback MCP bridge (JSON/SSE/event-stream), migration + rollback, tunnel planner, Master ceremony
(Ed25519 + ML-DSA-65), Master-signed passports, conformance matrix, stability gate, and (beta 10) an **issuance
audit trail** and **dual-signed release artifacts**. Public beta. Stable gen3.5 (`dna-GCACGAGGCTGT`) remains default.

## In this asset
- `runtime/agi_runtime.py` - 10 typed verbs; intents + local Master approval; FTS5 + hash-vector RRF recall.
- `runtime/agi_bridge.py` - MCP 17 tools (incl. seats, passports, `passport_issue` policy-gated); remote approval
  refused; event stream replay + `?window=0` unbounded.
- `runtime/agi_seats.py` - Ed25519 public-key seats (HMAC fallback), challenge-response, replay blocked.
- `runtime/agi_master.py` - local Master ceremony, Ed25519 + ML-DSA-65 dual signing, tamper rejection.
- `runtime/agi_passport.py` - Master-signed (dual) passports + **append-only issuance audit** (`state/audit.jsonl`).
- `runtime/agi_policy.py` - remote passport issuance OFF by default; local enablement required.
- `runtime/agi_release.py` - **dual-signed release artifacts** (DNA, seed, notes) with manifest + verify/tamper.
- `runtime/agi_stability.py` - K cold conformance runs; stability window.
- `runtime/agi_conformance.py` - C-beta1..C-beta24 (**25 checks**).
- `runtime/agi_migrate.py`, `agi_tunnel.py`, signed DNA v4 + seed, `CHANGELOG.beta.md`, docs.

## Verified
All suites green; conformance **25/25**; stability window **5 runs × 25/25 -> STABLE** (~4 s each); Windows + Linux
(WSL2 6.18 / Python 3.10) cold boots PASS.

## Limits
ML-DSA needs a supporting `cryptography`; Master keys are local files (no HSM); tunnel E2E **blocked** on this host
(no tunnel binary) and network exposure needs explicit approval; no destructive migration of live state; no license.
The AGI does **not** call itself beta-stable yet - the stability window is evidence, the stable default remains gen3.5.
