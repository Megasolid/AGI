# WORKSPACE BRIDGE — CHANGELOG v0.2.5 → v0.2.6

**Status:** PROPOSED (revision mapping) — **no implementation.**
**Revision:** v0.2.5 → v0.2.6 (KING v0.2.5 review corrections R2, R3, R8 + secondary).
**Purpose:** Map KING v0.2.5 findings to exact sections changed.

---

## Correction mapping

| Finding | Requirement | Sections changed |
|---|---|---|
| **R8-a** (pygit2/libgit2/Python incompatibility) | Choose compatible combination for Python 3.13 | **Spec v0.2.6:** §3.10 **pygit2 1.15.0 + libgit2 1.7.x removed** (pygit2 1.15 supports Python 3.9–3.12; libgit2 1.7 is for pygit2 1.15); **pinned `pygit2 1.16.0` + `libgit2 1.8.x`** (Python 3.13 compatible); `pygit2.__version__`+`pygit2.LIBGIT2_VERSION`+`sys.version` recorded at startup. **Tests N-129, N-132, P-20.** |
| **R8-b** (invalid `repo.status(flags=...)`) | Valid Python-level no-refresh invocation | **Spec v0.2.6:** §3.10 **`repo.status(flags=...)` removed**; **`repo.statuses(flags=StatusOption.GIT_STATUS_OPT_NO_REFRESH \| INCLUDE_UNTRACKED \| RECURSE_UNTRACKED_DIRS \| RENAMES_HEAD_TO_INDEX)`** (documented pygit2 method accepting `StatusOption`); if `StatusOption.GIT_STATUS_OPT_NO_REFRESH` not exposed → `E_GIT_UNAVAILABLE`. **Tests N-125, N-133.** |
| **R2-a** (Windows volume vs mount identity) | Describe as volume-identity, not mount-ID; same-volume unresolved | **Spec v0.2.6:** §3.1.3/§3.1.4 **`volume_serial` = volume-identity validation, NOT mount-identity**; same-volume mount = **accepted residual, unresolved (WB-U21)**; **cross-platform mount-boundary invariant NOT established**; **do not claim Windows satisfies Linux guarantee**. **Tests N-27.** |
| **R2-b** (`FILE_TYPE_REMOTE` as remote detector) | Remove implication; documented as unused | **Spec v0.2.6:** §3.1.3/§3.1.6 **`FILE_TYPE_REMOTE` NOT used as remote-filesystem detector** (Microsoft: unused); **accept `FILE_TYPE_DISK` or `FILE_TYPE_REMOTE` (both disk-backed); reject only `FILE_TYPE_CHAR`/`FILE_TYPE_PIPE`**. **Tests N-33.** |
| **R3-a** (high-water not genuine anti-rollback) | External monotonic anchor, not signed local record | **Spec v0.2.6:** **new §3.8.4.2 — external monotonic anchor (RFC 3161 TSA / transparency log / WORM) that the bridge reads but does not control; bridge verifies external tree-head signature + inclusion; local record NOT the anti-rollback authority; no anchor → refuse start (`E_EXTERNAL_ANCHOR_UNAVAILABLE`)**. **Tests N-109, N-110, A-13, I-13.** |
| **R3-b** (comparison rules) | Exact sink vs high-water vs local comparisons; anchor_id binding | **Spec v0.2.6:** **new §3.8.4.3 — exact comparisons** (sink vs external head seq/hash; local head vs external head; local-ahead must extend from external head hash; `anchor_id` binding, different anchor → `E_ANCHOR_MISMATCH`). **Tests N-110..N-113.** |
| **R3-c** (auto-checkpoint blessing fabricated tail) | Prevent auto-checkpoint of untrusted tail | **Spec v0.2.6:** **new §3.8.4.5 — bridge MUST NOT automatically checkpoint an unanchored tail; checkpoint only after independent reconciliation (owner-designated reconciler signs `reconciliation_signature`) or tail discarded; re-chained tail = untrusted, cannot be checkpointed without reconciliation**. **Tests N-105, N-114, N-116, A-15.** |
| **R3-d** (recovery deadlock) | Liveness while protected blocked | **Spec v0.2.6:** **new §3.8.4.5 — background reconciliation/discard operates independently of protected-request blocking; if reconciler unavailable, tail discarded after WB-U24 window; protected requests remain blocked until reconciled/discarded; guarantees liveness**. **Tests N-115, A-16.** |
| **R3-e** (test-plan consistency P-13/N-79/N-102) | Distinguish startup acceptance vs permission to serve | **Spec §3.8.4.3/§3.8.4.4; Tests:** P-13 **startup OK, protected blocked (`E_AUDIT_UNANCHORED`)**; N-83 older checkpoint allowed (startup); N-106 unanchored tail → no protected request. |
| **R1** (strict base64url) | Strict canonical base64url validation | **Spec v0.2.6:** §3.6.1 **charset `[A-Za-z0-9_-]` only; length exactly 43; canonical re-encode must match; reject `+`/`/`/`=`/whitespace/wrong-length/non-canonical**. **Tests N-71..N-75.** |
| **Assessment stale revision** | Update revision/reference or label historical | **`AGI_SKILL_CONNECTION_ASSESSMENT_2026-11-17.md`:** revision **v0.2.6**; **explicitly labeled historical assessment updated only for spec reference**. |

---

## Document-level changes

| Document | v0.2.5 → v0.2.6 |
|---|---|
| `WORKSPACE_BRIDGE_READ_ONLY_SPEC_v0.2.5.md` → **`WORKSPACE_BRIDGE_READ_ONLY_SPEC_v0.2.6.md`** | Schema 0.2.6; §3.1.3/3.1.4/3.1.6 Windows volume-identity + `FILE_TYPE_REMOTE` fix; §3.6.1 strict base64url; §3.8.4.2 external monotonic anchor; §3.8.4.3 exact comparisons + `anchor_id`; §3.8.4.4 unanchored tail; §3.8.4.5 no auto-checkpoint + reconciliation/discard liveness; §3.10 pygit2 1.16.0 + `repo.statuses(flags=...)`; §8 U23/U24 |
| `CHATGPT_MCP_CONNECTION_RUNBOOK.md` | §5 strict base64url; §10 checklist; §12 U1..U24 |
| `WORKSPACE_BRIDGE_ACCEPTANCE_TEST_PLAN.md` | N-1..N-138; P-13/P-18/P-20/P-21; N-24..N-33 (statx/mount/FILE_TYPE_REMOTE); N-71..N-76 (base64url); N-104..N-116 (tail/anchor/reconciliation); N-125..N-133 (Git); A-13..A-16; I-13/I-14; §7 outcome-specific |
| `WORKSPACE_BRIDGE_RISK_AND_AUTHORIZATION_REGISTER.md` | All residuals NOT ESTABLISHED; WB-R-01..R-30; WB-A-01..A-20; WB-U1..U24 |
| `AGI_SKILL_CONNECTION_ASSESSMENT_2026-11-17.md` | revision v0.2.6; historical label |
| `WORKSPACE_BRIDGE_CHANGELOG_v0.2.6.md` | **new** (this file) |
| `WORKSPACE_BRIDGE_TRACEABILITY_MATRIX_v0.2.5.md` → **`WORKSPACE_BRIDGE_TRACEABILITY_MATRIX_v0.2.6.md`** | R2/R3/R8/R1 rows updated; WB-U23/U24 added |

---

## Review-root consistency (preserved)
**Spec §9 / Runbook §11 / Register §5** — **identical** (verified).

---

## Non-operation
No implementation, activation, tunnel, credential, endpoint, or Git operation to `main`. Only documentation revised.

**Awaiting KING's seventh document-level verdict.**