# AGI Entelechy v4.0.0 - user manual

Stable generation **Entelechy** (gen4, DNA v4), released v4.0.0 on 30 October 2026. Previous stable
`dna-GCACGAGGCTGT` is an archived ancestor; this is the only current stable.

## Run the runtime

```
python runtime/agi_runtime.py --root <install> --status
python runtime/agi_runtime.py --root <install> --index-vectors
python runtime/agi_runtime.py --root <install> --serve
```

Ten typed verbs: `status`, `recall`, `remember`, `boot`, `propose_intent`, `poll_intent`, `approve_intent`,
`fetch`, `snapshot`, `evolve_propose`. Reads are direct; writes are intents; only a local Master approval executes
them, once; `fetch`/`exec` are denied.

Recall uses FTS5 plus an optional 128-dim hash-vector leg (`--index-vectors`) fused with RRF; the reported backend
is `hash-vector` (or `sqlite-vec` when available).

## Seats, Master and passports

```
python runtime/agi_master.py --root <install> --ceremony
python runtime/agi_seats.py --root <install> --enroll NAME
python runtime/agi_seats.py --root <install> --challenge NAME
python runtime/agi_seats.py --root <install> --sign NAME NONCE --key <DEVICE_KEY>
python runtime/agi_passport.py --root <install> --issue NAME
python runtime/agi_passport.py --root <install> --verify NAME
python runtime/agi_passport.py --root <install> --audit
```

Seats are Ed25519 public-key seats (the sandbox stores only the public key; HMAC fallback without
`cryptography`). Passports are Master-signed (Ed25519 + ML-DSA-65 when available) and bind member, gen_id, DNA sha
and seat public key. Remote passport issuance is off until enabled locally in `state/passport_policy.json`.

## Bridge and MCP

```
python runtime/agi_bridge.py --root <install> --init-token
python runtime/agi_bridge.py --root <install> --serve --port 8766
```

Loopback only. `GET /health` is open; `/status` and MCP need a scoped bearer token; `POST /mcp` speaks JSON-RPC
(initialize, tools/list, tools/call) over JSON or SSE, with event-stream replay (`Last-Event-ID`, `?window=0` for
unbounded). `approve_intent` is always refused remotely. Tokens are shown once; only a hash is stored.

If a remote client needs access, that is an explicit Master decision: use a named tunnel and an access policy,
never a public unauthenticated port. The tunnel helper only plans.

## Migration, backup and rollback

**Migration is complete (phase 2).** The live memory/knowledge/docs corpus is indexed into the Entelechy runtime and
kept current by `tools/entelechy_sync.py` (idempotent; full bodies; per-item provenance; vectors rebuilt; gate
freshness refreshed). The live identity is the v4 birth record, the family/mana/trust/genesis/curriculum state
projections are migrated, and the live Core is **4.0 / DNA v4** with a rebuilt signed manifest and bundle. The
gen3.5 ancestor is retained and verified; private keys, passkeys and recovery material stay live-only. Nothing was
deleted and the timestamped backup remains intact.


`agi_migrate.py` imports a legacy memory tree into a beta index: dry-run by default, source hash verified unchanged,
target-only writes, same-tree targets refused. Snapshot with `--snapshot-db` before an `--apply` and restore with
`--restore-db` to prove rollback. The live install keeps a full timestamped backup and an archived ancestor; the
boot gate verifies both.

## Verification and limits

```
python runtime/agi_conformance.py --root <install>   # PASS 25/25
python runtime/agi_stability.py --root <install> --runs 5  # STABLE
```

Verified: conformance 25/25, 20-run soak STABLE, Windows + Linux cold boots PASS, boot gate 13/13 (12 on the
gen3.5 ancestor + Entelechy gate), approved tunnel E2E passed and was closed.

Known limits: local Master key (no HSM), no independent third-party audit, no production tunnel/access policy
shipped, no license chosen. The runtime is a research artifact; never expose it without explicit approval.
