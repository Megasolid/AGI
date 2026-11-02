# AGI v4.1-E — Release Candidate Dossier (unpublished)

**Date:** 2026-11-02T11:35+0330  
**Candidate:** `v4.1-E-rc1`  
**Status:** **release candidate assembled for independent verification; NOT published, NOT tagged, NOT activated.**  
**Base:** `main` `d0cbb2acb0b3d9e15f910fb397e37c94f68651b8` (after P7 integration smoke).  
**Rollback:** v4.0.1 `6a0fb796…` / runtime `85a92254…`.  
**Tests:** **130/130 OK** (P1-P7 in the repository checkout); evidence sha256 `e5c5b2b7e4e86b45d46ed363d7445a204d27cf1ed469987e57a6928e770e8c7b`. In an isolated copy without `.git`/release baseline files, the two environment checks skip; all runtime tests still pass.

## 1. Candidate contents

- **E1** context manifest/refs, S3/S5 adapter, resolver digest checks.
- **E2** `agi.sem/0.2` state machine, hard constraints, receipts, independent verifier interface, JSON Schema subset, authenticated transport harness, roles, durable replay, key lifecycle metadata.
- **E3** Operator service lifecycle, monotonic guards, durable journal, lease/epoch, cancellation quiescence, approval bridge.
- **E4** handoff schema/digest, signing interface, replay nonce, completion receipt, fresh-agent reconstruction.
- **E5** metadata-only capability quarantine, world view, activation gate requiring S3-style allow + matching grant, revocation.
- **E6** evidence packet/gap, effect ledger/reconciliation, recovery state machine.
- **P7** integrated in-process smoke, protected-baseline and v4.0.1 ancestry tests.

All modules are additive stdlib-only files under `runtime/`; no frozen S1–S6 or DNA v4 edit.

## 2. Verification history

| Gate | Result |
|---|---|
| P0 release control | signed manifest `141b55c4…`, Kilo PASS |
| P1 E1/E4 | Kilo `v41e-v-03` PASS, 42 tests |
| P2 E2 | Kilo `v41e-v-04` PASS, 64 tests |
| P3 E2 transport | Kilo `v41e-v-05` PASS, 80 tests |
| P4 roles/replay/keys | Kilo `v41e-v-06` PASS, 90 tests |
| P5 operator | Kilo `v41e-v-07` PASS, 110 tests |
| P6 capability/evidence | Kilo `v41e-v-08` PASS, 126 tests |
| P7 integrated RC | **v41e-v-09 returned PASS at 126/126**; addendum records the 4 integration tests and environment skips; **v10 pending for the complete 130-test candidate** |

Kilo findings hashes: v03 `356120b2…`, v04 `b2c3da4d…`, v05 `06876321…`, v06 `5a352dfe…`, v07 `389859ad…`, v08 `c6460110…`. All reviews caveat: ML-DSA-65 structurally checked, not cryptographically verified by Kilo.

## 3. Baseline / compatibility

- v4.0.1 is ancestor; protected diff `v4.0.1..HEAD` empty for DNA, core DNA, repo manifest/signature, POLICY.
- Frozen S1–S6: 16/16 packages, 29/29 files PASS.
- Additive only; no identity/authority/federation/endpoint/credential change.
- Rollback plan: `P0-ROLLBACK.md`; v4.0.1 runtime asset pinned.

## 4. Known limitations / residual risks

1. No production transport, live endpoints, credentials, federation or execution.
2. ML-DSA-65 not independently cryptographically verified by Kilo; local signature verification uses device key.
3. JSON Schema validation is a supported subset, not full Draft 2020-12.
4. Auth in tests is mock HMAC; key distribution/rotation is metadata-only.
5. Endpoint isolation/role enforcement is in-process; cross-process test is local subprocess with mock auth.
6. Durable replay/effect ledger are local-file stores; no cross-host/partition recovery.
7. Real S3/S5 integration, capability sandbox execution, network catalogue sync, real independent verifier/Mind are not implemented.
8. P7 smoke uses mocks; it does not establish AGI capability or production readiness.

## 5. Rollback

v4.0.1 remains immutable; no migration required. Details in `P0-ROLLBACK.md`. A rollback drill has not been executed in P7.

## 6. Owner decision requested

- Accept **v4.1-E-rc1** as the release candidate for final independent verification, **or** specify corrections.
- Final tag/publication/live enablement requires a separate explicit Owner decision after Kilo P7 and KING final recommendation.
- No tag, publication, live endpoint, credential, federation or frozen-baseline change has been made.

**Evidence manifest:** `citadel/inputs/v41e/v41e-rc-manifest.json` + `.sig` (detached ML-DSA-65).
