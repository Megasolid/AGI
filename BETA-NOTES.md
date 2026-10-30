# AGI Entelechy beta 6 - release notes

Tag: `v4.0.0-beta.6` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 6
- **Device-key seat ceremony** (`runtime/agi_seats.py`): enroll shows a device key once (only SHA-256 displayed,
  local DB stores the seat secret), challenge-response login with HMAC-SHA256, single-use/expiring nonces,
  replay and wrong-proof rejection, status without key material.
- **Unbounded MCP event stream**: `GET /mcp?window=0` streams live events until the client closes (default stays
  bounded at 6 s); replay via `Last-Event-ID`; per-connection thread with heartbeat pings.
- **Conformance matrix extended** to C-beta1..C-beta13 (14 checks; adds seat ceremony and unbounded window) -> PASS 14/14.

## Verification
runtime 15/15, beta_2 13/13, beta_3 13/13, beta_4 10/10, beta_5 10/10, beta_6 9/9, proposal 12/12, sensorium 9/9;
conformance PASS 14/14; leak 0; hygiene 0; gate 12/12; Windows + Linux cold boots PASS.

## Known limits
Seat secrets stored locally (HMAC ceremony only; Ed25519/ML-DSA seats beta.7); unbounded SSE holds a thread per
client; no destructive migration; no tunnel auto-start; no Master key ceremony; no license chosen.
