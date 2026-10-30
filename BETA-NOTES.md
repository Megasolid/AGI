# AGI Entelechy beta 8 - release notes

Tag: `v4.0.0-beta.8` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 8
- **Remote seat enrollment over MCP**: `seat_enroll` (write scope) returns the device key once; `seat_status`,
  `passport_list`, `passport_verify` are read tools. MCP tool count is now 16; approval stays local-only.
- **Master-signed passports** (`runtime/agi_passport.py`): binds member, gen_id, DNA canonical sha and seat public key;
  Master Ed25519 signature; verification cross-checks signature/issuer/DNA/seat; tamper rejected.
- **Beta changelog** (`CHANGELOG.beta.md`) covering beta 1..8, evidence pointers and the honest tunnel blocker.
- **Conformance extended** to C-beta1..C-beta19 (**20 checks**) -> PASS 20/20.
- **Tunnel E2E blocked**: no `cloudflared`/`tailscale` binary on this host (WARP is not an ingress tunnel); the tunnel
  helper stays plan-only and the outbound relay mailbox remains the proven end-to-end transport.

## Verification
runtime 15/15, beta_2 13/13, beta_3 13/13, beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, beta_8 10/10,
proposal 12/12, sensorium 9/9; conformance PASS 20/20; leak 0; hygiene 0; gate 12/12; Windows + Linux cold boots PASS.

## Known limits
Ed25519/Master need `cryptography`; Master key is local file (no HSM); tunnel E2E blocked; no destructive migration of
live state; no license chosen.
