# WORKSPACE BRIDGE — ACCEPTANCE TEST PLAN

**Status:** PROPOSED (test design) — **no tests executed (no server).**
**Revision:** v0.2.6 — addresses KING v0.2.5 review corrections R1, R2, R3, R8 + secondary.
**Labels:** PROPOSED · SILVERSTONE-VERIFIED (derived from spec v0.2.6) · NOT ESTABLISHED.

**Change log:** see `WORKSPACE_BRIDGE_CHANGELOG_v0.2.6.md`. Tests marked `[R#]`.

---

## 1. Positive tests

| # | Test | Expected |
|---|---|---|
| P-1 | `workspace_roots{}` + valid token + valid D02 | 200, roots only |
| P-2 | `workspace_tree{root="review", path="docs", max_depth=2}` | 200, entries ≤ limit |
| P-3 | `workspace_search{root="review", query="trust"}` | ≤ 50, text only, scan budget OK |
| P-4 | `workspace_read{root="review", path="FILE.md"}` | content + sha256, verbatim |
| P-5 | `workspace_git_status{root="review"}` | branch/head/dirty; **index SHA-256 unchanged**; `pygit2_version`+`libgit2_version`+`python_version` in output |
| P-6 | Pagination bound cursor | next page; tampered/expired → `E_EXPIRED`/`E_DENIED` |
| P-7 | Token rotation overlap | both valid until cutoff |
| P-8 | Normal POSIX directory (st_nlink >= 2) | accepted |
| P-9 | Normal Windows directory (nNumberOfLinks >= 1) | accepted |
| P-10 | Auth with server retaining only verifier | correct secret → authorized; works after restart |
| P-11 | Fresh install with `OWNER_REINIT_TOKEN` | initialized |
| P-12 | Checkpoint ahead of local (normal) | `E_ROLLBACK_DETECTED` |
| P-13 | **Local head ahead of checkpoint (startup accepted, protected blocked)** | startup OK; **protected requests blocked (`E_AUDIT_UNANCHORED`) until tail reconciled/discarded** |
| P-14 | D02 decision valid + signed + request-bound | allowed |
| P-15 | Git with packed refs | packed refs read; status correct; no `.git` objects exposed |
| P-16 | `statx(AT_EMPTY_PATH, STATX_MNT_ID)` on Linux | `stx_mnt_id` returned; used as mount identity |
| P-17 | `FileAttributeTagInfo` on Windows | `FILE_ATTRIBUTE_TAG_INFO.ReparseTag == 0` for normal file |
| P-18 | **Unanchored tail covered by new checkpoint (after reconciliation)** | normal service resumes |
| P-19 | **External monotonic anchor present + sink checkpoint matches** | allowed |
| P-20 | **pygit2 1.16.0 + libgit2 1.8.x + Python 3.13** | `repo.statuses(flags=StatusOption.GIT_STATUS_OPT_NO_REFRESH \| ...)` works; index unchanged |
| P-21 | **Strict canonical base64url (43 chars, unpadded)** | accepted; authorized |

---

## 2. Negative tests with **outcome-specific** criteria

### 2.1 Path safety `[R2]`
| # | Attack | Expected outcome |
|---|---|---|
| N-1 | `../` traversal | `E_TRAVERSAL` |
| N-2 | Encoded traversal | `E_TRAVERSAL` |
| N-3 | Absolute path | `E_DENIED` |
| N-4 | Symlink escape | `E_PATH_RACE` |
| N-5 | Pre/post-open identity mismatch | `pre != post` → `E_PATH_RACE` |
| N-6 | Intermediate-dir swap | `E_PATH_RACE`; never serves swapped dir |
| N-7 | Hard link (file) | `st_nlink > 1` → `E_PATH_RACE` |
| N-8 | Mount / bind-mount crossing | `stx_mnt_id`/volume differs → `E_PATH_RACE` |
| N-9 | Windows reparse/junction | `FileAttributeTagInfo.ReparseTag != 0` → `E_PATH_RACE` |
| N-10 | Windows ADS (`::$DATA`) | `E_DENIED` |
| N-11 | Null byte | `E_DENIED` |
| N-12 | Depth cap | capped 5; deeper → `E_TOO_DEEP` |
| N-13 | Root substitution | root identity mismatch → `E_PATH_RACE` |
| N-14 | POSIX dir st_nlink == 0 (corrupt) | `E_PATH_RACE` |
| N-15 | POSIX normal dir st_nlink >= 2 | accepted (P-8) |
| N-16 | Final component FIFO | `S_ISFIFO` → `E_UNSUPPORTED_TYPE`; no block |
| N-17 | Final component device | `S_ISCHR`/`S_ISBLK` → `E_UNSUPPORTED_TYPE` |
| N-18 | Final component socket | `S_ISSOCK` → `E_UNSUPPORTED_TYPE` |
| N-19 | Final component directory | `S_ISDIR` → `E_UNSUPPORTED_TYPE` |
| N-20 | Final replaced after pre-open (non-regular) | `S_ISREG` false → `E_UNSUPPORTED_TYPE` |
| N-21 | Windows final is reparse | `E_PATH_RACE` |
| N-22 | Windows final `FILE_TYPE_CHAR`/PIPE | `E_UNSUPPORTED_TYPE` |
| N-23 | Windows final `FILE_ATTRIBUTE_DIRECTORY` | `E_UNSUPPORTED_TYPE` |
| N-24 | POSIX mount-id from `statx(STATX_MNT_ID)` | mount-id differs → `E_PATH_RACE` |
| N-25 | POSIX `statx` unavailable (no `STATX_MNT_ID`) | `E_MOUNT_ID_INDETERMINATE` (fail-closed) |
| N-26 | POSIX `fstatfs` `f_fsid` used as mount-id | NOT used; test asserts `statx` used |
| N-27 | Windows same-volume mount point | accepted residual (WB-U21); **volume-identity validation only** |
| N-28 | Windows root itself is reparse point | `E_PATH_RACE` |
| N-29 | POSIX root is symlink | `E_PATH_RACE` |
| N-30 | Rename race | handle → original inode; safe |
| N-31 | Unlink race | handle → original inode; safe |
| N-32 | Parent-dir swap after dup | post-open `fstat` dev/ino → `E_PATH_RACE` |
| N-33 | **Windows `FILE_TYPE_REMOTE` treated as remote detector** | NOT used as remote detector; SMB disk-backed accepted; test asserts `FILE_TYPE_REMOTE` not rejected as remote |

### 2.2 Deny & exclusion
| # | Attack | Expected outcome |
|---|---|---|
| N-34 | Unapproved root | `E_DENIED` |
| N-35 | `.reference` (read) | `E_DENIED` (D-1) |
| N-36 | Nested `.reference` (read) | `E_DENIED` (D-1) |
| N-37 | `AGI.Original Data` (read) | `E_DENIED` (D-2) |
| N-38 | Archive (read) | `E_DENIED` (D-3) |
| N-39 | Secret (read) | `E_SENSITIVE_FILE` (D-4) |
| N-40 | Private memory (read) | `E_DENIED` (D-5) |
| N-41 | `.git` (read) | `E_DENIED` (D-6) |
| N-42 | Nested `.git` (read) | `E_DENIED` (D-6) |
| N-43 | Generated (read) | `E_DENIED` (D-7) |
| N-44 | Caller `\\?\` prefix | `E_DENIED` |
| N-45 | Case evasion (Windows) | `E_DENIED` (ordinal) |
| N-46 | Non-NFC input | `E_NORMALIZATION` |
| N-47 | Cross-method: tree (deny match) | omitted; suppressed |
| N-48 | Cross-method: search | never searched; no filename |
| N-49 | Cross-method: git | excluded from changed_files |
| N-50 | Cross-method: roots | deny-matched root omitted; suppressed |

### 2.3 Sensitive & redaction
| # | Attack | Expected outcome |
|---|---|---|
| N-51 | Read sensitive | `E_SENSITIVE_FILE`, no content |
| N-52 | Secret in snippet | `[REDACTED]`, `redacted=true` |
| N-53 | Verbatim guarantee | byte-identical |
| N-54 | Audit secret | `[REDACTED]` |

### 2.4 Auth `[R1]`
| # | Attack | Expected outcome |
|---|---|---|
| N-55 | Invalid token | `E_UNAUTHORIZED` |
| N-56 | Missing token | `E_UNAUTHORIZED` |
| N-57 | Credential expired | `E_EXPIRED` |
| N-58 | Request expired | `E_EXPIRED` |
| N-59 | Revoked token | `E_REVOKED` (≤ 1s) |
| N-60 | Replay (same process) | `E_REPLAY` |
| N-61 | Replay after restart | `E_REPLAY` |
| N-62 | Nonce cache deletion | refuse start (`E_NONCE_CACHE_LOST`) |
| N-63 | Both marker + store deleted (no reinit) | refuse start (`E_INSTALL_UNAUTHORIZED`) |
| N-64 | Both deleted + valid `OWNER_REINIT_TOKEN` | fresh install allowed (P-11) |
| N-65 | Client binding mismatch | `E_CLIENT_MISMATCH` |
| N-66 | Clock skew > 30s | `E_EXPIRED` |
| N-67 | Bad HMAC | `E_UNAUTHORIZED` |
| N-68 | Rate limit (61/60s) | `E_RATE_LIMITED` |
| N-69 | Token exhausted | `E_RATE_LIMITED` |
| N-70 | Server stores no raw secret; restart then verify | authorized (P-10) |
| N-71 | **base64url with padding (`=`)** | `E_UNAUTHORIZED` |
| N-72 | **base64url with `+`/`/` (standard base64)** | `E_UNAUTHORIZED` |
| N-73 | **base64url length != 43** | `E_UNAUTHORIZED` |
| N-74 | **decoded token_secret != 32 bytes** | `E_UNAUTHORIZED` |
| N-75 | **non-canonical base64url (re-encode mismatch)** | `E_UNAUTHORIZED` |
| N-76 | **derivation uses b64 string, not raw bytes** | verify with 32-byte raw → authorized; verify with b64 string → `E_UNAUTHORIZED` |

### 2.5 Audit & D02
| # | Attack | Expected outcome |
|---|---|---|
| N-77 | Audit sink down | `E_AUDIT_FAILED` |
| N-78 | Corrupt audit chain | refuse start |
| N-79 | Full-chain replacement (forged, valid genesis) | latest checkpoint head_hash mismatch → `E_CHECKPOINT_CONFLICT` / refuse start |
| N-80 | Rollback local behind checkpoint | `E_ROLLBACK_DETECTED` |
| N-81 | Sequence gap | `E_ROLLBACK_DETECTED` / refuse start |
| N-82 | Checkpoint sink unavailable at startup | refuse start (`E_CHECKPOINT_UNAVAILABLE`) |
| N-83 | **Checkpoint older (normal)** | allowed (P-13) |
| N-84 | Checkpoint seq rollback (sink conflict) | `E_CHECKPOINT_CONFLICT` |
| N-85 | Concurrent audit append | single-writer lock; atomic; no interleaving |
| N-86 | Truncated last line | recovery truncates; chain verifies |
| N-87 | Missing sink | refuse start |
| N-88 | Pre-access audit before read | `fsync` before read; if write fails → `E_AUDIT_FAILED`, read never occurs |
| N-89 | No D02 decision | `E_NO_POLICY` |
| N-90 | D02 deny | `E_DENIED` |
| N-91 | D02 decision mismatch | `E_POLICY_MISMATCH` |
| N-92 | Stale policy | `E_POLICY_STALE` |
| N-93 | Expired policy | `E_POLICY_EXPIRED` |
| N-94 | Revoked policy | `E_POLICY_REVOKED` |
| N-95 | Unverifiable policy (bad sig / unknown issuer) | `E_POLICY_UNVERIFIABLE` |
| N-96 | D02 decision signature invalid | `E_POLICY_UNVERIFIABLE` |
| N-97 | D02 decision expired | `E_POLICY_EXPIRED` |
| N-98 | D02 decision bound to different request | `E_POLICY_MISMATCH` |
| N-99 | D02 replay with different request_id | `E_POLICY_MISMATCH` |
| N-100 | D02 replay with different request_digest | `E_POLICY_MISMATCH` |
| N-101 | `workspace_roots` resource semantics | decision `resource="*"`; wrong → `E_POLICY_MISMATCH` |
| N-102 | Server-side request-digest recomputation mismatch | server recomputes `SHA-256(JCS({method,params}))`; mismatch → `E_DIGEST_MISMATCH` |
| N-103 | D02 `principal` != `auth.client_id` | `E_POLICY_MISMATCH` |
| N-104 | **Fabricated audit records after latest valid checkpoint (bad chain)** | tail does not chain → discard; `E_AUDIT_UNANCHORED` (no protected request) |
| N-105 | **Fabricated tail that re-chains (forged valid chain)** | untrusted; **no protected request**; **cannot be auto-checkpointed**; requires reconciliation or discard |
| N-106 | **Unanchored tail present (normal between checkpoints)** | **no protected request** (`E_AUDIT_UNANCHORED`); only metadata exemption if owner-approved |
| N-107 | **Checkpoint sink rollback (older checkpoint injected)** | external anchor mismatch → `E_CHECKPOINT_ROLLBACK` / refuse start |
| N-108 | **Checkpoint sink deletion** | startup → `E_CHECKPOINT_UNAVAILABLE` (refuse start) |
| N-109 | **External monotonic anchor unavailable** | refuse start (`E_EXTERNAL_ANCHOR_UNAVAILABLE`) |
| N-110 | **External anchor older than sink checkpoint** | `E_CHECKPOINT_ROLLBACK` / refuse start |
| N-111 | **Local head ahead; chain does not extend from external head hash** | `E_ROLLBACK_DETECTED` / refuse start |
| N-112 | **Local head == external head seq but hash differs** | `E_CHECKPOINT_CONFLICT` / refuse start |
| N-113 | **Checkpoint for different anchor_id** | `E_ANCHOR_MISMATCH` |
| N-114 | **Auto-checkpoint over unanchored tail (no reconciliation)** | **prohibited**; tail remains unanchored; protected blocked |
| N-115 | **Reconciliation window elapsed without reconciler** | tail **discarded** (truncate to last authenticated checkpoint); service resumes from there |
| N-116 | **Reconciler signs reconciliation record** | tail checkpointed; normal service resumes (P-18) |

### 2.6 Search/Git leakage & limits
| # | Attack | Expected outcome |
|---|---|---|
| N-117 | Search deny subtree | no filenames |
| N-118 | Tree deny placeholder | omitted (no name) |
| N-119 | Git changed_files leak | deny excluded; no names; suppressed |
| N-120 | Git log/diff | `E_METHOD_NOT_FOUND` |
| N-121 | Remote URL | none |
| N-122 | Absolute path in results | relative only |
| N-123 | Search scan budget exceeded | `E_SCAN_LIMIT` |
| N-124 | Pagination cursor tamper/expiry | `E_DENIED`/`E_EXPIRED` |
| N-125 | **Git index refresh attempted** | `GIT_STATUS_OPT_NO_REFRESH` via `repo.statuses(flags=...)`; index SHA-256 unchanged; no fsmonitor |
| N-126 | **Git packed refs repo** | packed refs read; status correct; no `.git` objects exposed |
| N-127 | **Git repo with fsmonitor config** | fsmonitor not executed; status correct |
| N-128 | **Git repo with external diff driver** | driver not invoked |
| N-129 | **pygit2 1.16.0 + libgit2 1.8.x + Python 3.13** | `repo.statuses(flags=StatusOption.GIT_STATUS_OPT_NO_REFRESH \| ...)` works; index unchanged |
| N-130 | **Git object access required for status** | objects (commits/trees/blobs) read for diff; no writes; `.git/objects` not exposed |
| N-131 | **Git config/ignore files read** | `.git/config`, `.git/info/exclude`, `.gitignore` read-only; required for status |
| N-132 | **pygit2 1.16.0 not installed (e.g., 1.15 on Python 3.13)** | `E_GIT_UNAVAILABLE` (version mismatch) |
| N-133 | **`StatusOption.GIT_STATUS_OPT_NO_REFRESH` not exposed** | `E_GIT_UNAVAILABLE` |
| N-134 | **WB-U4 retention not approved** | classification PROPOSED; 90d not applied; default 30d |

### 2.7 Method restriction
| # | Attack | Expected outcome |
|---|---|---|
| N-135 | Write method | `E_METHOD_NOT_FOUND` |
| N-136 | Shell method | `E_METHOD_NOT_FOUND` |
| N-137 | Git commit | `E_METHOD_NOT_FOUND` |
| N-138 | Unknown schema | `E_VERSION` |

---

## 3. Audit verification
A-1 allowed logged (`class=ACCESS`, `prev_hash`, `record_hash`); A-2 denied (`class=DENY`); A-3 auth (`class=AUTH`); A-4 no prompt; A-5 no secrets (`[REDACTED]`); A-6 relative only; A-7 `fsync` before success; A-8 chain from `anchor_hash`; A-9 anchor sig verifies with owner-pinned key; A-10 external checkpoint exported + `head_hash` matches; A-11 pseudonymous client; A-12 post-checkpoint tail not accepted as independent evidence; **A-13 external monotonic anchor present + signed + bound to `anchor_id`** `[R3]`; **A-14 unanchored tail → no protected request** `[R3]`; **A-15 auto-checkpoint over untrusted tail prohibited** `[R3]`; **A-16 reconciliation/discard liveness (no deadlock)** `[R3]`.

---

## 4. Isolation
I-1 read-only; I-2 no shell; I-3 no exfiltration; I-4 untrusted content; I-5 fd-based (`openat`/`O_NOFOLLOW`; `NtCreateFile`+`RootDirectory`); I-6 descriptor-relative; I-7 pre/post-open compare; I-8 Git read-only library (no index write, no fsmonitor, no helpers); I-9 Windows `NtCreateFile` with `OBJECT_ATTRIBUTES.RootDirectory`; I-10 POSIX `S_ISREG` + `O_NONBLOCK` on final; I-11 mount-id from opened handle (`statx(AT_EMPTY_PATH, STATX_MNT_ID)` / `FILE_ID_INFO` volume-only), fail-closed; I-12 Windows `FileAttributeTagInfo`/`FILE_ATTRIBUTE_TAG_INFO`; **I-13 external monotonic anchor read-only (bridge cannot rewrite)** `[R3]`; **I-14 no auto-checkpoint of untrusted tail** `[R3]`.

---

## 5. Limits
L-1 ≤ 256 KiB; L-2 pagination; L-3 60/60s; L-4 timeout; L-5 > 1 MiB → `E_TOO_LARGE`; L-6 binary → `E_UNSUPPORTED_TYPE`; L-7 scan budget → `E_SCAN_LIMIT`.

---

## 6. Harness
Unit (temp roots) + integration (`[REDACTED-LOCALHOST]`) + race (N-5/N-6/N-30/N-31/N-32) + restart (N-61/N-62/N-70/N-78) + checkpoint (N-79/N-80/N-82/N-84/N-104..N-116) + concurrency (N-85) + negative fixtures (symlink, junction, hard link, bind mount, FIFO, device, socket, `.reference`, `.git`, oversized, binary, secret, ADS, `\\?\`, non-NFC, packed refs, fsmonitor config, external driver, non-canonical base64url). Audit assertions. **CI gate: all P/N/A/I/L pass with outcome-specific criteria.**

---

## 7. Pass criteria
Outcome-specific per invariant. **Tests are PROPOSED until executed.** No test reported as passed by inclusion.

- **P-\*:** bounded, verbatim, read-only, index unchanged.
- **N-1..N-3:** `E_TRAVERSAL`/`E_DENIED`.
- **N-4..N-33:** `E_PATH_RACE`/`E_DENIED`/`E_UNSUPPORTED_TYPE`/`E_TOO_DEEP`/`E_MOUNT_ID_INDETERMINATE`; N-27 accepted residual; N-30/N-31 rename/unlink safe; N-32 parent swap; N-24 `statx`; N-26 no `f_fsid`-as-mount; N-33 `FILE_TYPE_REMOTE` not remote detector.
- **N-34..N-50:** `E_DENIED`/`E_SENSITIVE_FILE`/omission/`E_NORMALIZATION`.
- **N-51..N-54:** redaction/verbatim.
- **N-55..N-76:** `E_UNAUTHORIZED`/`E_EXPIRED`/`E_REVOKED`/`E_REPLAY`/`E_NONCE_CACHE_LOST`/`E_INSTALL_UNAUTHORIZED`/`E_CLIENT_MISMATCH`/`E_RATE_LIMITED`; N-71..N-76 strict base64url/raw-bytes.
- **N-77..N-116:** `E_AUDIT_FAILED`/refuse-start/`E_POLICY_*`/`E_ROLLBACK_DETECTED`/`E_CHECKPOINT_CONFLICT`/`E_CHECKPOINT_ROLLBACK`/`E_CHECKPOINT_UNAVAILABLE`/`E_EXTERNAL_ANCHOR_UNAVAILABLE`/`E_AUDIT_UNANCHORED`/`E_DIGEST_MISMATCH`/`E_ANCHOR_MISMATCH` + pre-access audit + no-auto-blessing + reconciliation/discard liveness.
- **N-117..N-134:** omission/`E_SCAN_LIMIT`/`E_GIT_UNAVAILABLE`/no-index-write/packed-refs/fsmonitor/driver/version/object-read/config-ignore-read/retention-PROPOSED.
- **N-135..N-138:** `E_METHOD_NOT_FOUND`/`E_VERSION`.

**Read-only connection ≠ write permission. Any write/shell/git-mutation method = test failure.**

---

## 8. Status
**TEST PLAN v0.2.6 PROPOSED — NOT EXECUTED (no server).**

**Awaiting implementation + owner authorization.**