# WORKSPACE BRIDGE — CORRECTION TRACEABILITY MATRIX

**Status:** PROPOSED — **no implementation.**
**Purpose:** Map every KING v0.2.5 review finding to its v0.2.6 resolution, with evidence location and test coverage.

| KING finding | v0.2.6 resolution | Spec section | Runbook section | Register section | Test(s) | Status |
|---|---|---|---|---|---|---|
| **R8-a** pygit2 1.15 + libgit2 1.7 incompatible with Python 3.13 | Pinned **`pygit2 1.16.0` + `libgit2 1.8.x`** (Python 3.13 compatible); version recorded at startup | §3.10 | §12 (WB-U19) | WB-R-19, WB-U19 | N-129, N-132, P-20 | PROPOSED |
| **R8-b** `repo.status(flags=...)` not documented | **`repo.statuses(flags=StatusOption.GIT_STATUS_OPT_NO_REFRESH \| INCLUDE_UNTRACKED \| RECURSE_UNTRACKED_DIRS \| RENAMES_HEAD_TO_INDEX)`**; if `GIT_STATUS_OPT_NO_REFRESH` not exposed → `E_GIT_UNAVAILABLE` | §3.10 | §10 | WB-R-19 | N-125, N-133 | PROPOSED |
| **R2-a** Windows volume vs mount identity | `volume_serial` = **volume-identity validation, NOT mount**; same-volume mount = **accepted residual, unresolved (WB-U21)**; **cross-platform mount-boundary invariant NOT established** | §3.1.3, §3.1.4 | §10 | WB-R-01, WB-U21 | N-27 | UNRESOLVED (WB-U21) |
| **R2-b** `FILE_TYPE_REMOTE` as remote detector | **`FILE_TYPE_REMOTE` NOT used as remote detector** (Microsoft: unused); accept `FILE_TYPE_DISK` or `FILE_TYPE_REMOTE` (disk-backed); reject only `FILE_TYPE_CHAR`/`FILE_TYPE_PIPE` | §3.1.3, §3.1.6 | §10 | WB-R-04 | N-33 | PROPOSED |
| **R3-a** High-water not genuine anti-rollback | **External monotonic anchor (TSA / transparency log / WORM)** that bridge reads but does not control; local record NOT the authority; no anchor → refuse start (`E_EXTERNAL_ANCHOR_UNAVAILABLE`) | §3.8.4.2 | §12 (WB-U23) | WB-R-13, WB-U23 | N-109, A-13, I-13 | PROPOSED (anchor mechanism; WB-U23 owner) |
| **R3-b** Comparison rules + anchor_id binding | Exact comparisons (sink vs external head; local head vs external head; local-ahead must extend from external head hash); `anchor_id` binding (different anchor → `E_ANCHOR_MISMATCH`) | §3.8.4.3 | §10 | WB-R-13 | N-110..N-113 | PROPOSED |
| **R3-c** Auto-checkpoint blessing fabricated tail | **Bridge MUST NOT auto-checkpoint unanchored tail**; checkpoint only after independent reconciliation (owner-designated reconciler signs `reconciliation_signature`) or tail discarded; re-chained tail = untrusted | §3.8.4.5 | §10 | WB-R-12, WB-U24 | N-105, N-114, N-116, A-15 | PROPOSED (mechanism; WB-U24 owner) |
| **R3-d** Recovery deadlock | Background reconciliation/discard operates independently of protected-request blocking; if reconciler unavailable, tail discarded after WB-U24 window; protected blocked until reconciled/discarded; **liveness guaranteed** | §3.8.4.5 | §10 | WB-R-30 | N-115, A-16 | PROPOSED |
| **R3-e** P-13/N-79/N-102 consistency | **Startup acceptance ≠ permission to serve**: P-13 startup OK but protected blocked (`E_AUDIT_UNANCHORED`); N-83 older checkpoint allowed (startup); N-106 unanchored tail → no protected request | §3.8.4.3/3.8.4.4 | §10 | WB-R-12 | P-13, N-83, N-106 | PROPOSED |
| **R1** strict base64url | Charset `[A-Za-z0-9_-]`; length exactly 43; canonical re-encode must match; reject `+`/`/`/`=`/whitespace/wrong-length/non-canonical | §3.6.1 | §5 | WB-R-08 | N-71..N-75 | PROPOSED |
| **Assessment stale** | Revision v0.2.6; explicitly labeled historical assessment updated only for spec reference | — | — | — | — | CORRECTED |

---

## Review-root consistency
Spec §9 / Runbook §11 / Register §5 — **identical** (verified).

## Non-operation
No implementation, activation, tunnel, credential, endpoint, or Git operation to `main`. Only documentation revised.

**Awaiting KING's seventh document-level verdict.**