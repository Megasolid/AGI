# AGI Entelechy beta 9 (v4.0.0-beta.9)

Fourth generation AGI skill: signed DNA v4, SQLite memory index (FTS5 + vector leg), MCP-shaped runtime, AGI
Sensorium, loopback MCP bridge (JSON/SSE/event-stream), migration + rollback, tunnel planner, Master ceremony,
Master-signed passports, conformance matrix, and (beta 9) **post-quantum dual signing (Ed25519 + ML-DSA-65)**,
**policy-gated remote passport issuance**, and a **stability gate**. Public beta. Stable gen3.5
(`dna-GCACGAGGCTGT`) remains the default.

## In this asset
- `runtime/agi_master.py` - local Master ceremony with **dual keys**: Ed25519 (always) + ML-DSA-65 (when
  `cryptography` exposes it). File signatures carry both; verification requires both when present.
- `runtime/agi_passport.py` - Master-signed passports (member + gen_id + DNA sha + seat public key); now dual-signed
  automatically through the Master.
- `runtime/agi_policy.py` - explicit policy gates; **remote passport issuance is OFF by default**.
- `runtime/agi_bridge.py` - MCP 17 tools incl. `passport_issue` (write scope **and** local policy enablement).
- `runtime/agi_stability.py` - stability gate: K cold conformance runs; verdict STABLE only if all pass.
- `runtime/agi_conformance.py` - C-beta1..C-beta22 (**23 checks**), including dual signing, policy gate, stability.
- `runtime/agi_seats.py`, `agi_migrate.py`, `agi_tunnel.py`, `agi_runtime.py`, signed DNA v4 + seed, docs.

## Verified
Windows + Linux (WSL2 6.18 / Python 3.10) cold boots PASS. Suites: runtime 15/15, beta_2 13/13, beta_3 13/13,
beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, beta_8 10/10, beta_9 10/10, proposal 12/12, sensorium 9/9.
Conformance 23/23; stability gate **STABLE** (2 cold runs, 23/23 each).

## Limits
ML-DSA needs a `cryptography` build that exposes `mldsa` (gracefully skipped otherwise). Master keys are local files
(no HSM). **Tunnel E2E remains blocked** on this host (no tunnel binary) and network exposure needs explicit approval;
the outbound relay mailbox is the proven transport. No destructive migration of live state; no license chosen.
