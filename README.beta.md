# AGI Entelechy beta 7 (v4.0.0-beta.7)

Fourth generation AGI skill: signed DNA v4, one SQLite memory index (FTS5 + vector leg), thin MCP-shaped runtime,
AGI Sensorium perception layer, loopback intent bridge with MCP JSON/SSE/event-stream, migration dry-run + rollback,
tunnel planner, beta conformance matrix, and (beta 7) **Ed25519 public-key seats**, a **Master Ed25519 ceremony**,
**remote seat tools over MCP**, and **migration rollback proof**. Public beta. Stable gen3.5 (`dna-GCACGAGGCTGT`)
remains default; the beta never migrates live state.

## In this asset
- `runtime/agi_seats.py` - seats in **ed25519 mode** (device private key stays on the device; only the public key is
  stored; signed challenge-response, single-use nonces, replay blocked). `hmac` fallback remains for environments
  without `cryptography`.
- `runtime/agi_master.py` - local **Master Ed25519 ceremony**: private key in `state/master.key` (best-effort 0600),
  public identity in `state/master_pub.json`, sign/verify files (passports, seeds, manifests), tamper rejected.
- `runtime/agi_bridge.py` - MCP now exposes **12 tools** including `seat_challenge` / `seat_login`; remote approval
  still refused; event stream with `Last-Event-ID` replay and `?window=0` unbounded.
- `runtime/agi_migrate.py` - dry-run/apply plus **snapshot/restore rollback proof** (`--snapshot-db`, `--restore-db`).
- `runtime/agi_conformance.py` - C-beta1..C-beta17 (**18 checks**) PASS required before adoption.
- `runtime/agi_runtime.py`, `runtime/agi_tunnel.py`, signed DNA v4 + seed, docs.

## Verify
```
python runtime/agi_conformance.py --root <sandbox> --out conformance.json   # PASS 18/18
python runtime/agi_master.py --root <sandbox> --ceremony
python runtime/agi_seats.py --root <sandbox> --enroll NAME                   # key once, public key only
```
Windows + Linux (WSL2 6.18 / Python 3.10) cold boots PASS. Suites: runtime 15/15, beta_2 13/13, beta_3 13/13,
beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, proposal 12/12, sensorium 9/9.

## Limits
Ed25519 features need `cryptography` (stdlib HMAC seats fallback otherwise). Master key is a local file, no HSM.
No tunnel auto-start; no destructive migration of live state; no license chosen.
