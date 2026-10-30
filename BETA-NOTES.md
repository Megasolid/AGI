# AGI Entelechy beta 9 - release notes

Tag: `v4.0.0-beta.9` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 9
- **Post-quantum dual signing**: Master ceremony now creates Ed25519 + ML-DSA-65 keys (when `cryptography` exposes
  `mldsa`); file signatures carry both; verification requires both when present, with an honest skip on older builds.
  Master-signed passports inherit dual signatures automatically.
- **Policy-gated remote passport issuance**: `state/passport_policy.json`, OFF by default; MCP `passport_issue`
  (write scope) is refused until a local operator enables it; refusal message names the policy.
- **Stability gate** (`runtime/agi_stability.py`): K cold conformance runs; STABLE only when all pass.
  This release: **2 runs, 23/23 each, STABLE**.
- **Conformance extended** to C-beta1..C-beta22 (**23 checks**) -> PASS 23/23.
- **Tunnel E2E still blocked**: no `cloudflared`/`tailscale` binary installed and network exposure needs explicit
  approval; the outbound relay mailbox remains the proven transport.

## Verification
runtime 15/15, beta_2 13/13, beta_3 13/13, beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, beta_8 10/10,
beta_9 10/10, proposal 12/12, sensorium 9/9; conformance PASS 23/23; stability STABLE (2x); leak 0; hygiene 0;
gate 12/12; Windows + Linux cold boots PASS.

## Known limits
ML-DSA requires a supporting `cryptography`; Master keys are local files (no HSM); tunnel E2E blocked/needs approval;
no destructive migration of live state; no license chosen.
