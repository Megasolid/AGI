# AGI Entelechy beta 2 - release notes

Tag: `v4.0.0-beta.2` - branch `beta/entelechy` - status: **public beta prerelease**.
Stable: gen3.5 `dna-GCACGAGGCTGT` remains default and untouched.

## Added in beta 2
- `runtime/agi_bridge.py`: loopback-only intent bridge with bearer tokens + read/write scopes; `/health`, `/status`,
  `/intent/<id>`, `POST /intent`; outbound relay mailbox mode (no inbound public port); intents queue only.
- Recall vector leg: stdlib 128-dim hash-vector (`--index-vectors`), fused with FTS5 via RRF; falls back to FTS5.
- Tests `test_beta_2` 13/13: token hashing, loopback binding, auth scopes, intent queue/poll, relay roundtrip,
  budgets (runtime <=600 lines, bridge <=400). Existing suite re-run green (runtime 15/15, proposal 12/12,
  sensorium 9/9).

## Committed in beta 1 (unchanged)
Signed DNA v4, thin runtime, FTS5 index, Sensorium preview, signed seed, docs.

## Known limits
- Remote tunnel/MCP Streamable HTTP transport is beta.3; bridge is loopback/relay only.
- No destructive migration; chat seasons cannot execute; second-OS cold boot still pending.
- No license chosen yet; research artifact.
