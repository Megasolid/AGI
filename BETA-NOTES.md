# AGI Entelechy beta 7 - release notes

Tag: `v4.0.0-beta.7` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 7
- **Ed25519 public-key seats**: the sandbox stores only the public key; login signs the challenge
  (`agi-seat-login/v2:<member>:<nonce>`); nonces single-use/expiring; replay and wrong signatures rejected.
  HMAC fallback retained for hosts without `cryptography`.
- **Master Ed25519 ceremony** (`runtime/agi_master.py`): local keypair in `state/master.key` (best-effort 0600) +
  `state/master_pub.json`; file signing/verification with tamper rejection.
- **Remote seat tools over MCP**: `tools/list` now returns 12 tools including `seat_challenge`/`seat_login`;
  `approve_intent` still refused remotely (-32003).
- **Migration rollback proof**: `snapshot_db`/`restore_db` + CLI flags; conformance verifies snapshot -> apply ->
  restore sha matches while the source stays unchanged.
- **Conformance matrix extended** to C-beta1..C-beta17 (**18 checks**) -> PASS 18/18.

## Verification
runtime 15/15, beta_2 13/13, beta_3 13/13, beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, proposal 12/12,
sensorium 9/9; conformance PASS 18/18; leak 0; hygiene 0; gate 12/12; Windows + Linux cold boots PASS.

## Known limits
Ed25519/Master features require `cryptography`; key is a local file (no HSM, no multi-device); no tunnel auto-start;
no destructive migration of live state; no license chosen.
