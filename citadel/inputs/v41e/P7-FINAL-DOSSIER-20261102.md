# AGI v4.1-E — Final Release Dossier (unpublished candidate)

**Date:** 2026-11-02T12:12+0330  
**Candidate:** `v4.1-E-rc1`  
**Status:** **UNPUBLISHED — NOT TAGGED — NOT ACTIVATED.** KING recommends acceptance; Owner D final approval pending.  
**Base:** `main` `d0cbb2acb0b3d9e15f910fb397e37c94f68651b8`; rollback v4.0.1 `6a0fb796…`.

## 1. Evidence chain

| Item | Value |
|---|---|
| RC manifest | `sha256:c6f17fe358e8b063738039674c1ec63a9233277495ba54e73205f167149e77ff` |
| RC manifest signature | detached `agi-sig/1`, ML-DSA-65, key_id `a73eaa5d3c31e009` |
| RC artifacts | 61 |
| Kilo v11 findings | `sha256:2058547b46cbbd010a0aace824831dc1d8b44c7677df0d537de219317d16923a` (PASS, 8/8 checks) |
| Correction record | `P7-CORR-01` — stale v10 bundle hash in v11 evidence metadata; v11 bundle c482b969…; decision unchanged |
| Local tests | **130/130 OK in repository checkout**; evidence `P7-TEST-OUTPUT.txt` sha256 `e5c5b2b7…` |
| Isolated-copy tests | **128 pass + 2 environment skips** (no `.git` / baseline files); not a clean 130 claim |
| Protected baseline | v4.0.1 ancestor; protected diff empty; frozen S1–S6 16/16 packages, 29/29 files |
| Publication | **No tag, no publication, no live endpoint, no credentials, no federation** |

## 2. Signature verification evidence

- Local device-key verification of the RC manifest: `ok=true`, alg ML-DSA-65, key_id `a73eaa5d3c31e009`.
- **Independent cryptographic ML-DSA-65 verification is outstanding**; Kilo confirmed structure/key_id/payload binding only (no ML-DSA-65 library).
- The detached signature file hash is recorded in the Kilo v11 evidence; its structure and payload binding were checked.

## 3. Correction

`P7-CORR-01` corrects the v11 findings `evidence.zip_bundle` field from v10 hash `205d22f3…` to v11 hash `c482b969…`; check `PV-02` already used the correct v11 hash. The Kilo report file is not altered.

## 4. Known limitations / residual risks

1. No production transport/live endpoints/credentials/federation/execution.
2. ML-DSA-65 independent cryptographic verification outstanding.
3. JSON Schema validation is a subset; auth in tests is mock HMAC; key registry metadata-only.
4. Endpoint isolation is in-process; replay/effect ledgers are local files.
5. Real S3/S5 integration, sandbox execution, network sync and a real independent verifier are not implemented.
6. Two environment checks skip in isolated copies; release-baseline/ancestry are validated via pinned manifests by Kilo.
7. P7 smoke uses mocks; it does not establish AGI capability.

## 5. Rollback

v4.0.1 immutable; no migration; `P0-ROLLBACK.md`; drill not executed in P7.

## 6. Owner decision requested

**Approve or reject** tagging/publication/live enablement of `v4.1-E-rc1`. Until explicit approval: no tag, no publication, no live execution. If approved, a separate final tag/publication step and any required signature-verification upgrade must be recorded.
