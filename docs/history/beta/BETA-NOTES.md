# AGI Entelechy beta 10 - release notes

Tag: `v4.0.0-beta.10` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 10
- **Issuance audit trail**: passport issuance (local or MCP) appends an append-only `state/audit.jsonl` event with
  sequence, timestamp, member, actor, passport sha and signature algos; `agi_passport.py --audit` lists it.
- **Dual-signed release artifacts** (`runtime/agi_release.py`): DNA / seed / notes signed with the Master
  Ed25519 + ML-DSA-65 keys, recorded in `state/release_signatures.json`; verify re-hashes and checks both signatures;
  tamper rejected.
- **Stability window evidence**: 5 cold conformance runs, **25/25 each -> STABLE** (about 4 s per run).
- **Conformance extended** to C-beta1..C-beta24 (**25 checks**) -> PASS 25/25.
- **Tunnel E2E still blocked**: no tunnel binary installed and network exposure needs explicit approval; the relay
  mailbox remains the proven transport. The beta does not claim beta-stable; stable remains gen3.5.

## Verification
runtime 15/15, beta_2 13/13, beta_3 13/13, beta_4 10/10, beta_5 10/10, beta_6 9/9, beta_7 10/10, beta_8 10/10,
beta_9 10/10, beta_10 9/9, proposal 12/12, sensorium 9/9; conformance 25/25; stability window STABLE (5x);
leak 0; hygiene 0; gate 12/12; Windows + Linux cold boots PASS.

## Known limits
ML-DSA requires a supporting `cryptography`; Master keys local (no HSM); tunnel E2E blocked/needs approval; no
destructive migration of live state; no license chosen.
