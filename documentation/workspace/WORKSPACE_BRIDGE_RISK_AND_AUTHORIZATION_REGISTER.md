# WORKSPACE BRIDGE — RISK AND AUTHORIZATION REGISTER

**Status:** PROPOSED — **no action executed.**
**Revision:** v0.2.6 — addresses KING v0.2.5 review corrections; **all residuals NOT ESTABLISHED**.
**Labels:** SILVERSTONE-VERIFIED · PROPOSED · OWNER-APPROVED · UNRESOLVED · NOT ESTABLISHED.

**Change log:** see `WORKSPACE_BRIDGE_CHANGELOG_v0.2.6.md`. Items marked `[R#]`.

---

## 1. Risks (residual = NOT ESTABLISHED where no implementation/test exists)

| ID | Risk | Severity | Mitigation (PROPOSED) | Residual | Note |
|---|---|---|---|---|---|
| WB-R-01 | Path traversal / symlink / mount escape `[R2]` | **Critical** | handle-relative open; pre/post-open assert; `NtCreateFile(...,RootDirectory)`; `statx(STATX_MNT_ID)` (POSIX) / `VolumeSerialNumber` volume-only (Windows); fail-closed | **NOT ESTABLISHED** | Windows mount boundary incomplete (WB-U21) |
| WB-R-02 | TOCTOU / rename / unlink / intermediate-dir race `[R2]` | **Critical** | fd chain pinned; pre/post-open compare; rename/unlink safe | **NOT ESTABLISHED** | design only |
| WB-R-03 | Windows reparse race `[R2]` | **Critical** | `NtCreateFile` + `FILE_OPEN_REPARSE_POINT` + `FileAttributeTagInfo`/`FILE_ATTRIBUTE_TAG_INFO` | **NOT ESTABLISHED** | design only |
| WB-R-04 | Final component non-regular | **High** | `S_ISREG`/`FILE_TYPE_DISK|REMOTE` (not char/pipe) + `O_NONBLOCK` | **NOT ESTABLISHED** | `FILE_TYPE_REMOTE` not a remote detector |
| WB-R-05 | `.reference`/private leak | **Critical** | unified deny D-1..D-8; cross-method omission | **NOT ESTABLISHED** | design only |
| WB-R-06 | Secret leak / silent transform | **High** | sensitive rejection; audit/snippet redaction; verbatim | **NOT ESTABLISHED** | design only |
| WB-R-07 | Write/shell/git-mutation method | **Critical** | read-only spec | **NOT ESTABLISHED** | design only |
| WB-R-08 | Auth compromise `[R1]` | **High** | bearer + HKDF (single formula) + verifier + strict base64url + expiry + rotation + kill-switch | **NOT ESTABLISHED** | design only |
| WB-R-09 | `client_id` not strong auth `[R1]` | **High** | documented limitation; WB-U16 | **NOT ESTABLISHED** | design only |
| WB-R-10 | Replay (incl. after restart) `[R1]` | **High** | durable atomic nonce; cache deletion → refuse start; reinit requires owner token | **NOT ESTABLISHED** | design only |
| WB-R-11 | Audit failure → unsafe allow `[R3]` | **High** | audit-write failure → `E_AUDIT_FAILED`; corrupt → refuse start | **NOT ESTABLISHED** | design only |
| WB-R-12 | Full-chain replacement / fabricated tail `[R3]` | **High** | external monotonic anchor + owner-pinned key + startup comparison + **unanchored tail → `E_AUDIT_UNANCHORED` (no protected request)** + **no auto-checkpoint of untrusted tail** | **NOT ESTABLISHED** | design only |
| WB-R-13 | Rollback `[R3]` | **High** | external monotonic anchor (TSA/log/WORM) + sink-vs-anchor-vs-local comparison | **NOT ESTABLISHED** | design only; depends on WB-U23 |
| WB-R-14 | Checkpoint sink unavailable | **High** | refuse start (`E_CHECKPOINT_UNAVAILABLE`) | **NOT ESTABLISHED** | design only |
| WB-R-15 | Audit concurrency / crash `[R3]` | **High** | single-writer lock; atomic append; crash recovery + sequence continuity | **NOT ESTABLISHED** | design only |
| WB-R-16 | G25-07 retention misclassification `[R4]` | **High** | classification PROPOSED; 90d not applied until WB-U4; default 30d | **NOT ESTABLISHED** | design only |
| WB-R-17 | Private-path/filename leakage | **High** | omission + `excluded_count` suppressed | **NOT ESTABLISHED** | design only |
| WB-R-18 | Oversized response / scan DoS | Medium | 256 KiB cap; scan budget; rate limit | **NOT ESTABLISHED** | design only |
| WB-R-19 | Git index refresh / fsmonitor / external driver `[R8]` | **High** | `pygit2 1.16.0` + `libgit2 1.8.x` + `repo.statuses(flags=StatusOption.GIT_STATUS_OPT_NO_REFRESH \| ...)`; no refresh/fsmonitor/drivers; else `E_GIT_UNAVAILABLE` | **NOT ESTABLISHED** | design only; version not tested |
| WB-R-20 | Tunnel/endpoint exposure | **High** | HTTPS + token+HMAC; conditional on §3 + owner approval | **NOT ESTABLISHED** | design only |
| WB-R-21 | ChatGPT caches content after revocation | Medium | minimize roots; accept residual | **NOT ESTABLISHED** | design only |
| WB-R-22 | Prompt-injection via file content | **High** | untrusted data; no tool chaining | **NOT ESTABLISHED** | design only |
| WB-R-23 | Web Bridge accidentally extended | **High** | boundary | **NOT ESTABLISHED** | design only |
| WB-R-24 | H0 metadata-only weakened | **High** | do not modify H0 | **NOT ESTABLISHED** | design only |
| WB-R-25 | D02 not enforced `[R7]` | **Critical** | per-request signed decision + request_id + request_digest binding + server-side recomputation + boundary enforcement + pre-access audit | **NOT ESTABLISHED** | design only; no test |
| WB-R-26 | D02 decision forged / replayed `[R7]` | **High** | Ed25519 over canonical (incl. request_id + request_digest); owner-pinned issuer; binding; expiry; `E_POLICY_MISMATCH` | **NOT ESTABLISHED** | design only; no test |
| WB-R-27 | ChatGPT account lacks MCP | Medium | verify account (NOT ESTABLISHED); fallback O-4 | **NOT ESTABLISHED** | account unverified |
| WB-R-28 | Missing audit sink / checkpoint sink / external anchor | **High** | refuse start | **NOT ESTABLISHED** | design only |
| WB-R-29 | Audit key compromise `[R3]` | **High** | owner-pinned key (WB-U17); external anchor | **NOT ESTABLISHED** | design only |
| WB-R-30 | Recovery deadlock (unanchored tail blocks forever) `[R3]` | **High** | reconciliation/discard liveness (background; discard after WB-U24 window) | **NOT ESTABLISHED** | design only |

**Note:** All residuals are **NOT ESTABLISHED** because **zero tests were executed** and **no implementation exists**. Design estimates are not operational residuals.

---

## 2. Authorization register (PROPOSED — none granted)

| ID | Proposed action | Status |
|---|---|---|
| WB-A-01 | Approve spec v0.2.6 | UNRESOLVED |
| WB-A-02 | Approve root allowlist (WB-U10) | UNRESOLVED |
| WB-A-03 | Approve token ceremony + overlap (WB-U2/U14) | UNRESOLVED |
| WB-A-04 | Approve tunnel/endpoint (WB-U8) | UNRESOLVED |
| WB-A-05 | Approve audit sink + per-class retention (WB-U4) | UNRESOLVED |
| WB-A-06 | Authorize implementation of `workspace_bridge/` v0.2.6 | NOT ESTABLISHED |
| WB-A-07 | Authorize activation (after WB-U9) | NOT ESTABLISHED |
| WB-A-08 | Approve revocation SLA (WB-U7) | UNRESOLVED |
| WB-A-09 | Approve POSIX vs Windows fd-API (WB-U11) | UNRESOLVED |
| WB-A-10 | Approve nonce cache backend (WB-U12) | UNRESOLVED |
| WB-A-11 | Approve `excluded_count` enable (WB-U15) | UNRESOLVED |
| WB-A-12 | Approve client binding (WB-U16) | UNRESOLVED |
| WB-A-13 | Approve audit signing key custody + pin (WB-U17) | UNRESOLVED |
| WB-A-14 | Approve D02 policy source + max age + issuer key pin (WB-U18) | UNRESOLVED |
| WB-A-15 | Approve read-only Git library + version (WB-U19) | UNRESOLVED |
| WB-A-16 | Approve search scan budget (WB-U20) | UNRESOLVED |
| WB-A-17 | Approve same-volume Windows mount residual (WB-U21) | UNRESOLVED |
| WB-A-18 | Approve post-checkpoint unanchored tail disposition (WB-U22) | UNRESOLVED |
| WB-A-19 | Approve external monotonic anchor (WB-U23) | UNRESOLVED |
| WB-A-20 | Approve reconciliation window + reconciler (WB-U24) | UNRESOLVED |

**No approval granted.**

---

## 3. Protected / excluded (non-negotiable)
`.reference`, `AGI.Original Data`, private archives/backups/memory/sessions, keys/tokens/secrets, H0 metadata-only, Web Bridge, FCC/D02, V4.0.1.

---

## 4. Unresolved owner decisions (reconciled)

| ID | Question |
|---|---|
| WB-U1 | Approved root aliases + contents |
| WB-U2 | Token issuance/rotation ceremony |
| WB-U3 | Rate-limit values |
| WB-U4 | Audit sink + **per-class retention (PROPOSED: AUTH/DENY/ADMIN 30d raw; ACCESS 90d operational; sanitized 3y) — NOT approved; default 30d** |
| WB-U5 | Git metadata scope |
| WB-U6 | Text-only vs binary |
| WB-U7 | Revocation SLA (≤ 1s) |
| WB-U8 | Tunnel provider + host (conditional on account check) |
| WB-U9 | ChatGPT account MCP capability (NOT ESTABLISHED) |
| WB-U10 | Review-root layout |
| WB-U11 | POSIX vs Windows fd-API |
| WB-U12 | Nonce cache backend (SQLite WAL) |
| WB-U13 | Audit verify cadence |
| WB-U14 | Token overlap exact (≤ 24h) |
| WB-U15 | `excluded_count` (default suppressed) |
| WB-U16 | Client binding: channel binding / proof key / documented limitation |
| WB-U17 | Audit signing key custody + pin location |
| WB-U18 | D02 policy source + `policy_max_age` + issuer key pin |
| WB-U19 | Read-only Git library (**pygit2 1.16.0 + libgit2 1.8.x for Python 3.13**; `repo.statuses(flags=...)`) |
| WB-U20 | Search scan budget values |
| WB-U21 | Same-volume Windows mount-point residual (unresolved) |
| WB-U22 | Post-checkpoint unanchored tail disposition (**fail-closed; metadata-only exemption optional**) |
| WB-U23 | External monotonic anchor for anti-rollback (TSA / transparency log / WORM) |
| WB-U24 | Reconciliation window + reconciler identity (before tail discard) |

**WB-U1..U24 reconciled across spec, runbook, register.**

---

## 5. Minimal sanitized review-root layout
```
review-root/                      # alias: "review"
├── docs/review/repository-rationalization/2026-11-16/   # 6 sanitized audit docs
├── contracts/                    # D02, SSL (sanitized)
├── AGI_SKILL_CONNECTION_ASSESSMENT_2026-11-17.md
└── WORKSPACE_BRIDGE_SPEC_v0.2.6.md
```
Only sanitized, owner-approved files; no `.reference`/private/secrets; relative paths; read-only; `excluded_count` suppressed; names never listed.

---

## 6. Smallest safe implementation (RECOMMENDED)
Standalone `workspace_bridge/` MCP server; 5 read-only methods; bearer + HKDF (single formula, strict base64url `token_secret`) + verifier (no raw secret) + HMAC + durable nonce + owner-signed install marker; descriptor-relative traversal (`openat`/`O_NOFOLLOW`; `NtCreateFile`+`RootDirectory`) + pre/post-open assert + `S_ISREG`/`FILE_TYPE_DISK|REMOTE` + `O_NONBLOCK` + `statx(STATX_MNT_ID)`/`VolumeSerialNumber` mount-id (volume-only on Windows, fail-closed); unified deny; sensitive rejection; **external monotonic anchor + anti-rollback + unanchored tail → no protected request + no auto-checkpoint of untrusted tail + reconciliation/discard liveness**; per-class retention (PROPOSED); **D02 per-request signed decision with request_id+request_digest binding + server-side recomputation**; `pygit2 1.16.0` read-only Git (`repo.statuses(flags=...)`); text-only bounded; transport conditional; activation only after owner auth + tests pass.

---

## 7. Non-authorization
Read-only inspection + documentation only. No source modification, installation, activation, tunnel, credential, endpoint, `.reference` access, H0/FCC/D02/V4.0.1 changes, commits to `main`, pushes, merges, deployments. Pre-existing changes preserved.

**Awaiting owner review and authorization.**

**Status:** **RISK & AUTHORIZATION REGISTER v0.2.6 PROPOSED — NOTHING EXECUTED; RESIDUAL RISK NOT ESTABLISHED.**