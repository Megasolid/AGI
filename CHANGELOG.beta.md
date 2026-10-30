# AGI Entelechy beta changelog

## v4.0.0 - stable promotion (30 October 2026)

The beta line is promoted to **stable AGI Entelechy v4.0.0**: 25-check conformance PASS, 20-run stability soak
STABLE, dual post-quantum signing, Master-signed passports, issuance audit, MCP transports, Ed25519 seats.
Live migration completed with a full backup; ancestor `dna-GCACGAGGCTGT` archived and still verified by the boot
gate. Assets: `agi-runtime-v4.0.0.zip`, seed, SHA256SUMS, stable manifest, LINEAGE.

Public beta line of **AGI Entelechy** (gen4 / DNA v4). Stable gen3.5 (`dna-GCACGAGGCTGT`) remains the default and
is never migrated by the beta. Releases are GitHub prereleases; each ships a runtime zip, the signed seed,
SHA256SUMS and a manifest. Detailed notes live in `BETA-NOTES.md`; evidence lives under
`state/archive/evolution/` in the working tree.

## v4.0.0-beta.10 - audit trail + dual-signed release artifacts + stability window
- Append-only issuance audit (state/audit.jsonl, actor local/mcp, passport sha, algos).
- Dual-signed release artifacts (DNA/seed/notes, Ed25519 + ML-DSA-65) with manifest + tamper verification.
- Stability window: 5 cold conformance runs, 25/25 each -> STABLE. Conformance C-beta1..C-beta24 (25 checks).
- Not beta-stable; stable remains gen3.5. Tunnel E2E blocked (no binary; needs explicit approval).

## v4.0.0-beta.9 - ML-DSA dual signing + policy gate + stability gate
- Master Ed25519 + ML-DSA-65 dual signing; passports inherit dual signatures.
- Remote passport issuance OFF by default (state/passport_policy.json), MCP policy gate.
- Stability gate (K cold runs); conformance C-beta22 (23 checks at the time).

## v4.0.0-beta.8 - remote enrollment + Master-signed passports
- `seat_enroll` / `seat_status` / `passport_list` / `passport_verify` over MCP (16 tools total); enrollment needs
  `write` scope, key shown once.
- `runtime/agi_passport.py`: Master-signed passports binding member, gen_id, DNA sha and seat public key;
  verification cross-checks signature, issuer, DNA and seat. Tamper rejected.
- Conformance **C-beta1..C-beta19 (20 checks)** PASS.
- Transport E2E: outbound relay mailbox (no public ingress). **Tunnel E2E is blocked** on this host - no
  `cloudflared`/`tailscale` binary is installed (Cloudflare WARP is not an ingress tunnel), so a public end-to-end
  test remains pending. The tunnel helper remains plan-only.

## v4.0.0-beta.7 - ed25519 seats + Master ceremony + rollback proof
- Ed25519 public-key seats (private key device-only; HMAC fallback), local Master Ed25519 ceremony
  (`state/master.key` 0600, `state/master_pub.json`), remote seat challenge/login over MCP, migration
  snapshot/restore rollback proof, conformance 18/18.

## v4.0.0-beta.6 - device-key seats + unbounded event stream
- HMAC device-key seats (superseded by ed25519 in beta 7), `GET /mcp?window=0` unbounded SSE, conformance 14/14.

## v4.0.0-beta.5 - event stream + migration + tunnel plan
- Replayable MCP event stream (`Last-Event-ID`, live events), read-only memory migration dry-run, tunnel
  readiness/plan helper (never opens ingress), conformance 12/12.

## v4.0.0-beta.4 - MCP SSE + conformance matrix
- MCP SSE responses/keepalive, vector-backend reporting (`sqlite-vec` when present, hash-vector fallback),
  beta conformance matrix, conformance 12/12.

## v4.0.0-beta.3 - MCP Streamable HTTP + Linux cold boot
- MCP JSON-RPC (`initialize`, `tools/list`, `tools/call`, `ping`), remote approval refused, Linux WSL2 cold boot
  PASS (kernel 6.18, Python 3.10), conformance 12/12.

## v4.0.0-beta.2 - intent bridge + vector recall
- Loopback intent bridge (bearer tokens/scopes, outbound relay, no inbound public port), hash-vector recall leg
  fused with FTS5 via RRF, checkout-safe seed signing.

## v4.0.0-beta.1 - first public prerelease
- Signed DNA v4, thin 10-verb runtime, intents + Master-only execute-once approval, FTS5 memory index,
  AGI Sensorium preview, signed compact seed, beta docs.

## Known limits
- Tunnel E2E blocked (no tunnel binary installed); no public ingress is opened by the AGI itself.
- Master key is a local file (no HSM, no multi-device keys yet).
- Ed25519 features require `cryptography`; seats fall back to HMAC otherwise.
- No destructive migration of live state; no key ceremony for anything beyond the local Master.
- No license chosen yet - research artifact.
