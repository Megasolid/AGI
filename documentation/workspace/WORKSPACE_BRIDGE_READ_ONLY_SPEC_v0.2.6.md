# WORKSPACE BRIDGE — READ-ONLY SPECIFICATION v0.2.6

**Status:** PROPOSED (design) — **no implementation, activation, or exposure.**
**Revision:** v0.2.6 — addresses KING v0.2.5 review findings R2, R3, R8 + secondary corrections.
**Labels:** PROPOSED · SILVERSTONE-VERIFIED (constraints) · UNRESOLVED (owner decisions) · NOT ESTABLISHED.
**Scope:** Separate, versioned, read-only Workspace Bridge for KING (ChatGPT) to inspect **approved** AGI project files. **Not** a filesystem server; **not** an extension of Web Bridge or H0.

**Change log:** see `WORKSPACE_BRIDGE_CHANGELOG_v0.2.6.md`. Sections marked `[R#]`.

---

## 1. Purpose and non-goals

**Purpose:** Bounded, read-only, audited view of **explicitly approved** project files to an external reviewer via MCP.

**Non-goals (MUST NOT):** no write/delete/move/rename/Git mutation; no shell/process execution; no signing/approval/credential issuance/policy admin; no access to `.reference`, `AGI.Original Data`, private archives/backups/memory/sessions, keys/tokens/secrets, or any unapproved path; no arbitrary absolute paths from caller.

---

## 2. Interface (versioned, `workspace-bridge/0.2.6`)

Five read-only methods preserved. All take **named root aliases + relative paths**, never caller-supplied absolute paths.

### 2.1 `workspace_roots`
- **Input:** `{}` (auth enforced by envelope).
- **Output:** `{roots: [{alias, description, max_depth, allowed_extensions, max_file_bytes}]}`.
- **Errors:** `E_UNAUTHORIZED`, `E_EXPIRED`, `E_REVOKED`, `E_REPLAY`, `E_RATE_LIMITED`, `E_CLIENT_MISMATCH`, `E_NO_POLICY`, `E_DENIED`.

### 2.2 `workspace_tree`
- **Input:** `{root_alias, path=".", max_depth=3, max_entries=200, cursor=null}`.
- **Output:** `{entries: [{path, type, size_bytes, sha256?}], next_cursor, truncated}`. `excluded_count` suppressed by default. Deny-matched subtrees omitted.
- **Limits:** depth ≤ 5 (deeper → `E_TOO_DEEP`), entries ≤ 200, response ≤ 256 KiB.
- **Errors:** `E_DENIED`, `E_NOT_FOUND`, `E_TOO_LARGE`, `E_UNSUPPORTED_TYPE`, `E_TRAVERSAL`, `E_PATH_RACE`, `E_TOO_DEEP`, `E_MOUNT_ID_INDETERMINATE`.

### 2.3 `workspace_search`
- **Input:** `{root_alias, path=".", query, max_results=50, case_sensitive=false}`.
- **Output:** `{matches: [{path, line, snippet, redacted}], truncated}`. `excluded_count` suppressed. Scan budget enforced (§3.3).
- **Limits:** query ≤ 200 chars, results ≤ 50, snippet ≤ 200 chars, text only, scan ≤ 10 MiB / 5000 files / 30 s.
- **Errors:** `E_DENIED`, `E_TOO_LARGE`, `E_UNSUPPORTED_TYPE`, `E_TRAVERSAL`, `E_PATH_RACE`, `E_SCAN_LIMIT`, `E_MOUNT_ID_INDETERMINATE`.

### 2.4 `workspace_read`
- **Input:** `{root_alias, path, offset=0, limit=200}`.
- **Output:** `{path, content, sha256, size_bytes, line_count, truncated}`.
- **Errors:** `E_DENIED`, `E_NOT_FOUND`, `E_TOO_LARGE`, `E_UNSUPPORTED_TYPE`, `E_TRAVERSAL`, `E_PATH_RACE`, `E_SENSITIVE_FILE`, `E_MOUNT_ID_INDETERMINATE`.

### 2.5 `workspace_git_status`
- **Input:** `{root_alias}`.
- **Output:** `{branch, head_commit, is_dirty, changed_files: [{path, status}], pygit2_version, libgit2_version, python_version}`.
- **Errors:** `E_DENIED`, `E_NOT_A_REPO`, `E_TOO_LARGE`, `E_PATH_RACE`, `E_GIT_UNAVAILABLE`.

**Common envelope (every request) `[R1][R7]`:**
```json
{
  "schema": "workspace-bridge/0.2.6",
  "request_id": "uuid",
  "request_digest": "hex (SHA-256 of JCS({method, params}))",
  "issued_at": "iso8601",
  "expires_at": "iso8601",
  "auth": {"token_id": "string", "client_id": "string", "nonce": "string", "tls_channel_id": "string|null", "signature": "base64"},
  "method": "...",
  "params": {...}
}
```
**D02 decision envelope `[R7]` (per request):**
```json
{
  "schema": "agi/d02-decision/1",
  "decision_id": "uuid",
  "request_id": "uuid (must match envelope request_id)",
  "request_digest": "hex (must match envelope request_digest AND server-recomputed digest)",
  "principal": "string (must equal auth.client_id)",
  "action": "workspace.<method>",
  "resource": "string (root_alias + normalized relative path, or \"*\" for workspace_roots)",
  "policy_version": "string",
  "decision": "allow|deny",
  "issued_at": "iso8601",
  "expires_at": "iso8601",
  "issuer_key_id": "string",
  "signature": "base64"
}
```

---

## 3. Required protections

### 3.1 Path safety `[R2]` — handle-relative traversal (POSIX + Windows)

**Normative principle:** every opened component (root, intermediate dirs, final file) is **pinned by handle** and **validated pre-open and post-open**. No pathname is re-resolved after validation. **If a reliable mount identity cannot be established, the operation fails closed (`E_MOUNT_ID_INDETERMINATE`).** `[R2]`

#### 3.1.1 Root pinning (both platforms) `[R2]`
1. Owner configures root by **canonical absolute path + expected identity (POSIX `(dev, ino, mnt_id)`; Windows `(volume_serial, file_id)`)** + expected **mount identity**, recorded out-of-band.
2. **Root reparse rejection `[R2]`:**
   - **POSIX:** `root_fd = open(root, O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW)`; if `S_ISLNK` → `E_PATH_RACE` (root must not be a symlink).
   - **Windows:** `hRoot = CreateFileW(root, GENERIC_READ, share, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS|FILE_FLAG_OPEN_REPARSE_POINT)`; **then** `GetFileInformationByHandleEx(hRoot, FileAttributeTagInfo, &buf, sizeof(buf))` → **`FILE_ATTRIBUTE_TAG_INFO { DWORD FileAttributes; DWORD ReparseTag; }`**; if **`ReparseTag != 0`** → **close + `E_PATH_RACE`** (root itself is a reparse point; reject). `[R2]`
3. **Post-open verify:** identity equals pinned (POSIX `(dev,ino)`; Windows `(volume_serial, file_id)`). Mismatch → `E_PATH_RACE`.
4. **Mount identity of root `[R2]`:** obtained per §3.1.4. If indeterminate → **refuse start** (cannot establish root mount boundary).
5. `root_fd` / `hRoot` is the **only** traversal entry point.

#### 3.1.2 POSIX descriptor-relative algorithm `[R2]`
For path `p`:
1. `dir_fd = dup(root_fd)`; `components = split(p, '/')`.
2. For each non-final component `c`:
   - Reject `c == ".."`, `c == ""` (from `//`), null byte, absolute → `E_TRAVERSAL`/`E_DENIED`.
   - **Pre-open:** `fstatat(dir_fd, c, AT_SYMLINK_NOFOLLOW)` → `pre`; reject `S_ISLNK` (`E_PATH_RACE`).
   - **Open:** `next_fd = openat(dir_fd, c, O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK)`.
   - **Post-open verify:** `fstat(next_fd)` → `post`.
   - **Invariant:** `pre.dev == post.dev` AND `pre.ino == post.ino` (else `E_PATH_RACE`).
   - `post.dev == root_st_dev` → else `E_PATH_RACE` (device boundary).
   - **`post.ino` not in ancestor set** → else `E_PATH_RACE` (cycle).
   - **Directory link count:** do not require `st_nlink == 1`. Normal POSIX dirs have `st_nlink >= 2`. Reject only `st_nlink == 0` (corrupt) → `E_PATH_RACE`. (Hard-linked dirs are impossible on POSIX.)
   - **Mount identity of `next_fd` `[R2]`:** obtain per §3.1.4 (descriptor-based). **If indeterminate → close + `E_MOUNT_ID_INDETERMINATE`** (fail-closed). If differs from `root_mnt_id` → `E_PATH_RACE`.
   - `dir_fd = next_fd`.
3. Final component `f`:
   - **Pre-open:** `fstatat(dir_fd, f, AT_SYMLINK_NOFOLLOW)` → `pre`; reject `S_ISLNK`.
   - **Open:** `file_fd = openat(dir_fd, f, O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK)`.
   - **Post-open verify:** `fstat(file_fd)` → `post`.
   - **Invariant:** `pre == post` (dev, ino, size, mtime). Else `E_PATH_RACE`.
   - **`S_ISREG(post.mode)` must be true.** `S_ISFIFO`/`S_ISCHR`/`S_ISBLK`/`S_ISSOCK`/`S_ISDIR`/`S_ISLNK` → `E_UNSUPPORTED_TYPE` (never read non-regular). `O_NONBLOCK` prevents blocking on substituted FIFO/device.
   - `post.dev == root_st_dev` → else `E_PATH_RACE`.
   - `post.nlink == 1` → else `E_PATH_RACE` (hard link).
   - **Mount identity of `file_fd` `[R2]`:** per §3.1.4 (descriptor-based). **If indeterminate → `E_MOUNT_ID_INDETERMINATE`** (fail-closed). If differs from root → `E_PATH_RACE`.
4. **Read** via `read(file_fd, ...)`. **Re-`fstat` after read:** identity change → `E_PATH_RACE`.

#### 3.1.3 Windows handle-relative algorithm `[R2]` — `NtCreateFile` with `RootDirectory`

**`CreateFileW` does NOT accept a directory handle as a base.** Valid mechanism: **`NtCreateFile` with `OBJECT_ATTRIBUTES.RootDirectory`**.

**Reparse information — documented API `[R2]`:**
- **Normative:** `GetFileInformationByHandleEx(hFile, FileAttributeTagInfo, &buf, sizeof(buf))` where `buf` is **`FILE_ATTRIBUTE_TAG_INFO { DWORD FileAttributes; DWORD ReparseTag; }`**.
  - **`FileAttributeTagInfo`** is the **documented `FILE_INFO_BY_HANDLE_CLASS`** enumeration value.
  - **`ReparseTag != 0`** → the handle is a reparse point (symlink/junction) → reject.
  - **`FileAttributes & FILE_ATTRIBUTE_REPARSE_POINT`** also set for reparse points.
- **Fallback (if `FileAttributeTagInfo` unavailable):** `GetFileInformationByHandle` → `dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT` — **documented, valid**. `[R2]`
- **Do NOT use** a non-existent `FileReparsePointInfo` class or `FILE_REPARSE_POINT_INFO` structure. `[R2]`

1. **Root handle:** `hRoot` per §3.1.1 (reparse-rejected via `FileAttributeTagInfo`). Verify identity + mount identity (§3.1.4). If root mount indeterminate → **refuse start**.
2. **Per component `c`:**
   - Reject `c == ".."`, `c == ""`, `:` (ADS/drive), null byte, absolute → `E_TRAVERSAL`/`E_DENIED`.
   - Reject caller-supplied `\\?\` / `\\.\` → `E_DENIED`.
   - **`NtCreateFile` handle-relative open:**
     ```c
     UNICODE_STRING name;  // c as UNICODE_STRING (no separators)
     OBJECT_ATTRIBUTES oa;
     InitializeObjectAttributes(&oa, &name, OBJ_CASE_INSENSITIVE, hDir, NULL);
     IO_STATUS_BLOCK iosb;
     HANDLE hNext;
     NTSTATUS st = NtCreateFile(
         &hNext,
         FILE_READ_DATA | FILE_LIST_DIRECTORY | SYNCHRONIZE,
         &oa, &iosb, NULL, FILE_ATTRIBUTE_NORMAL,
         FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
         FILE_OPEN,
         FILE_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT | FILE_OPEN_REPARSE_POINT,
         NULL, 0);
     ```
     - **`RootDirectory = hDir`** (handle-relative, race-resistant).
     - **`FILE_OPEN_REPARSE_POINT`** opens the reparse point **without following** (inspect + reject).
   - **Post-open reparse check `[R2]`:** `GetFileInformationByHandleEx(hNext, FileAttributeTagInfo, ...)` → `ReparseTag != 0` → close + `E_PATH_RACE`. (Or `FILE_ATTRIBUTE_REPARSE_POINT` fallback.)
   - **Post-open identity:** `GetFileInformationByHandle(hNext)` → `(volume_serial, file_id, nNumberOfLinks)`.
   - **`volume_serial == root_volume` → else `E_PATH_RACE`** — **this is volume-identity validation, NOT mount-identity validation.** `[R2]`
   - **Directory link count:** reject only `nNumberOfLinks == 0` (corrupt); `>= 1` accepted (normal).
   - `file_id` not in ancestor set → else `E_PATH_RACE` (cycle; `file_id` used only for **cycle detection**, **not** as mount ID). `[R2]`
   - **Mount identity of `hNext` `[R2]`:** per §3.1.4. **If indeterminate → close + `E_MOUNT_ID_INDETERMINATE`** (fail-closed). If differs from root → `E_PATH_RACE`.
   - `hDir = hNext`.
3. **Final file:**
   - `NtCreateFile` with `RootDirectory = hDir`, `FILE_OPEN_REPARSE_POINT`, **without** `FILE_DIRECTORY_FILE`, `FILE_SYNCHRONOUS_IO_NONALERT | FILE_NON_DIRECTORY_FILE`.
   - Post-open reparse check → `E_PATH_RACE`.
   - **Final type `[R2]`:** `GetFileInformationByHandle` → `FILE_ATTRIBUTE_DIRECTORY` must be **false**. **Do NOT use `FILE_TYPE_REMOTE` as a remote-filesystem detector** — Microsoft documents `FILE_TYPE_REMOTE` as **unused**; SMB filesystems are supported by `GetFileType`. `[R2]` **Normative:** accept `GetFileType(hFile) == FILE_TYPE_DISK` OR `FILE_TYPE_REMOTE` (both are disk-backed); **reject only** `FILE_TYPE_CHAR` (character device) and `FILE_TYPE_PIPE` (named pipe). `[R2]`
   - `volume_serial == root_volume` → else `E_PATH_RACE` (volume-identity validation, not mount).
   - `nNumberOfLinks == 1` → else `E_PATH_RACE`.
   - **Mount identity of `hFile` `[R2]`:** per §3.1.4. **If indeterminate → `E_MOUNT_ID_INDETERMINATE`** (fail-closed). If differs from root → `E_PATH_RACE`.
4. **Read** via `ReadFile`. **Re-`GetFileInformationByHandle` after read:** identity change → `E_PATH_RACE`.

**No `FindFirstFileW`-then-`CreateFileW`. No `CreateFileW(hDir, ...)`. The handle is opened via `NtCreateFile(..., RootDirectory=hDir, ...)`, then validated.**

#### 3.1.4 Mount identity — descriptor-based, fail-closed `[R2]`

**POSIX (Linux):**
- **Normative:** **`statx(fd, "", AT_EMPTY_PATH, STATX_MNT_ID, &stx)`** — returns **`stx.stx_mnt_id`** (mount ID of the filesystem containing the **opened descriptor**). **Descriptor-based, no pathname re-resolution.** `[R2]`
  - **`AT_EMPTY_PATH`** ensures `statx` operates on the **fd itself**, not a path.
  - **`STATX_MNT_ID`** is the **mount ID**, not filesystem ID. `[R2]`
- **Fallback (if `statx` / `STATX_MNT_ID` unavailable):** **`E_MOUNT_ID_INDETERMINATE`** (fail-closed). **Do NOT use `statfs`/`fstatfs` `f_fsid` as a mount ID** — `f_fsid` identifies the **filesystem**, not the **mount**. `[R2]`
- **Invariant:** every opened component's `stx_mnt_id` must equal `root_mnt_id`. Mismatch → `E_PATH_RACE` (bind mount / mount crossing).
- **Pathname-based `/proc/self/mountinfo` lookup is NOT used as a security guarantee.** `[R2]`

**Windows `[R2]`:**
- **`GetFileInformationByHandle`** → `dwVolumeSerialNumber` (volume identity, per-handle).
- **This is volume-identity validation, NOT mount-identity validation.** `[R2]`
- **Mount identity:** **`FILE_ID_INFO.VolumeSerialNumber`** (per-handle). **Do NOT use `FileId` as a mount identifier** — `FileId` identifies the **file**, not the mount. `[R2]`
- **Same-volume mount points / bind mounts:** **NOT distinguishable via volume serial alone** → **accepted residual** → **explicitly unresolved (WB-U21)**. `[R2]`
- **If `FILE_ID_INFO` unavailable** → **`E_MOUNT_ID_INDETERMINATE`** (fail-closed). `[R2]`

**Cross-platform invariant:** POSIX achieves **mount-identity** validation via `statx(STATX_MNT_ID)`; Windows achieves only **volume-identity** validation. **The cross-platform mount-boundary invariant is NOT established** — Windows same-volume mount detection is **unresolved (WB-U21)**. **Do not claim the Windows implementation satisfies the same mount-boundary guarantee as Linux.** `[R2]`

#### 3.1.5 Rename/unlink races and same-volume mount-boundary `[R2]`

- **Rename/unlink race `[R2]`:**
  - The **opened handle** continues to reference the **original inode** even if the pathname is renamed/unlinked. **This is safe** (no escape).
  - **Pre/post-open identity equality** (`pre == post`) detects a **replacement between `fstatat` and `openat`**. Mismatch → `E_PATH_RACE`.
  - **Parent-directory replacement:** `openat(dir_fd, ...)` from the **pinned `dir_fd`** prevents escape; if the parent dir itself is swapped after `dup`/`openat`, the fd still references the original dir. **Post-open `fstat` dev/ino check** on each component detects parent swap.
  - **Invariant:** the **validated handle** is read; pathname races never redirect the read. `[R2]`
- **Same-volume mount-boundary `[R2]`:**
  - POSIX: `st_dev` + `statx(STATX_MNT_ID)` detect mount crossing; same-`st_dev` different-mount → `stx_mnt_id` mismatch → `E_PATH_RACE`. `[R2]`
  - Windows: `VolumeSerialNumber` detects volume crossing; **same-volume mount points are an accepted residual** (not detected) → **WB-U21 unresolved**. `[R2]`

#### 3.1.6 Symlink / hard-link / reparse policy

| Type | Policy |
|---|---|
| Symlink (POSIX) | `O_NOFOLLOW`; `S_ISLNK` → `E_PATH_RACE`. Never follow. |
| Hard link (POSIX/Windows, file) | `st_nlink > 1` / `nNumberOfLinks > 1` → `E_PATH_RACE`. |
| Directory link count | `== 0` → `E_PATH_RACE`; `>= 2` (POSIX) / `>= 1` (Windows) accepted. |
| Mount crossing | `stx_mnt_id` (POSIX) / `VolumeSerialNumber` (Windows, volume only) mismatch → `E_PATH_RACE`; same-volume mount (Windows) = accepted residual (WB-U21). |
| Reparse point (Windows) | `FileAttributeTagInfo.ReparseTag != 0` / `FILE_ATTRIBUTE_REPARSE_POINT` → `E_PATH_RACE`. Never follow. |
| Root reparse point | **Reject root if `ReparseTag != 0`** → `E_PATH_RACE`. `[R2]` |
| Windows file type | `FILE_TYPE_DISK` or `FILE_TYPE_REMOTE` accepted; `FILE_TYPE_CHAR`/`FILE_TYPE_PIPE` rejected. **`FILE_TYPE_REMOTE` is NOT a remote-filesystem detector** (Microsoft: unused). `[R2]` |
| ADS (`::$DATA`) | `:` in component → `E_DENIED`. |
| Caller `\\?\` / `\\.\` | **Reject** (`E_DENIED`). |

### 3.2 Unified normalization and deny precedence
Single algorithm, identical across all five methods.

1. **Normalization:**
   - Reject absolute paths (`E_DENIED`); null bytes/control chars (`E_DENIED`); caller `\\?\`/`\\.\` (`E_DENIED`); `:` (ADS) (`E_DENIED`).
   - Split on `/` (POSIX) or `\` (Windows); collapse `.`; reject `..` (`E_TRAVERSAL`).
   - **Windows:** ordinal case-insensitive (`CompareStringOrdinal(..., TRUE)`); no locale.
   - **POSIX:** byte-exact case-sensitive.
   - **Unicode:** input must be valid UTF-8; **no NFC/NFD normalization** (reject non-UTF-8 `E_DENIED`); comparison codepoint-exact (POSIX) / ordinal (Windows).
2. **Deny (first-match wins, deny-before-allow):** D-1..D-8 on normalized path. Nested: D-1 `.reference`, `.reference/**`; D-6 `.git`, `.git/**` — same `/**` semantics (deny `X` + descendants). No override.
3. **Allow:** only if no deny and under approved root.
4. **Error resolution:**
   - Deny on `workspace_read` → `E_DENIED` (`reason_code=D-#`).
   - D-4 sensitive on `workspace_read` → `E_SENSITIVE_FILE`.
   - Deny on `workspace_tree`/`workspace_search`/`workspace_git_status`/`workspace_roots` → omit + `excluded_count` suppressed (0 default), no error, no name leak. Cross-method exclusion applies to all five.

**Deny table (D-1..D-8):** D-1 `.reference`, `.reference/**`; D-2 `**/AGI.Original Data`, `**/AGI.Original Data/**`; D-3 `**/*.zip|.rar|.7z|.tar|.tar.gz|.tgz`; D-4 `**/state/keys/**`, `**/.env`, `**/*.key|.pem|.p12`, `**/credentials*`, `**/token*`, `**/*secret*`; D-5 `**/memory/**`, `**/sessions/**`, `**/attention/**`; D-6 `.git`, `.git/**` (except `workspace_git_status` metadata); D-7 `**/node_modules/**`, `**/__pycache__/**`, `**/.vs/**`; D-8 any path not under approved root.

**Aggregate-count leakage:** `excluded_count` suppressed by default (0); owner may enable (WB-U15).

**Git metadata:** `workspace_git_status` reads only the metadata enumerated in §3.10; deny-matched paths excluded; `excluded_count` suppressed.

### 3.3 Limits
Max file 1 MiB; response 256 KiB; depth ≤ 5 (deeper `E_TOO_DEEP`); entries 200; search results 50; read lines 500; scan budget ≤ 10 MiB / 5000 files / 30 s → `E_SCAN_LIMIT`; rate 60/60s; cursor = HMAC-signed blob binding `(root_alias, path, policy_version, issued_at, expires_at)`; expiry ≤ 5 min; tampered/expired → `E_DENIED`/`E_EXPIRED`.

### 3.4 Content type
Text-only; binary → `E_UNSUPPORTED_TYPE`.

### 3.5 Sensitive rejection and redaction
D-4 on read → `E_SENSITIVE_FILE`, no content. D-4 on tree/search/git/roots → omit + suppressed count. Audit/snippet redaction. **Source never silently transformed** (verbatim for non-sensitive).

### 3.6 Authentication `[R1]`

#### 3.6.1 Enrollment and verification (single normative derivation) `[R1]`
- **Per-token salt: NOT USED.** `[R1]` Single normative derivation formula with **no per-token salt**.
- **`token_secret` byte encoding `[R1]`:**
  - **Generation:** `token_secret` = **32 bytes from a CSPRNG** (`/dev/urandom` / `BCryptGenRandom`). `[R1]`
  - **Bearer presentation:** `token_secret` is encoded as **unpadded base64url (RFC 4648 §5)** in `Authorization: Bearer <token_id>.<token_secret_b64url>`. **No padding (`=`).** `[R1]`
  - **Strict canonical base64url validation `[R1]`:**
    - **Character set:** `[A-Za-z0-9_-]` only. **Reject** `+`, `/`, `=`, whitespace, or any other char → `E_UNAUTHORIZED`.
    - **Length:** `token_secret_b64url` must be exactly **43 characters** (32 bytes → `ceil(32*4/3) = 43` unpadded base64url chars). **Reject** any other length → `E_UNAUTHORIZED`.
    - **Decoding:** server base64url-decodes → **32 raw bytes** (reject if decoded length != 32 → `E_UNAUTHORIZED`).
    - **Canonical re-encode check `[R1]`:** after decoding, server re-encodes to unpadded base64url and compares to the presented string. **Mismatch → `E_UNAUTHORIZED`** (rejects alternate/non-canonical encodings). `[R1]`
  - **Derivation:** HKDF `ikm` = the **32 raw bytes** (decoded), **not** the base64url string. `[R1]`
- **Enrollment (owner, out-of-band):**
  1. Owner generates `token_secret` (32 bytes CSPRNG) and `client_id` (UUID).
  2. Server derives **`auth_key = HKDF-SHA256(ikm = token_secret_raw_bytes, salt = token_id (UTF-8), info = "workspace-bridge/0.2.6 auth key", L = 32)`** at enrollment. `[R1]`
  3. Server stores **`verifier = SHA-256(auth_key)`** + `token_id` + `client_id` + `token_expires_at` + `scope` + `max_requests`. **No per-token salt; no raw `token_secret`.** `[R1]`
- **Verification (per request):**
  1. Client presents `Authorization: Bearer <token_id>.<token_secret_b64url>`.
  2. Server **strictly validates** base64url (charset, length 43, canonical re-encode) → `token_secret_raw_bytes` (32 bytes; else `E_UNAUTHORIZED`). `[R1]`
  3. Server computes `auth_key' = HKDF-SHA256(ikm = token_secret_raw_bytes, salt = token_id, info = "workspace-bridge/0.2.6 auth key", L = 32)`.
  4. Server computes `verifier' = SHA-256(auth_key')`.
  5. **Constant-time compare** `verifier' == verifier`. Mismatch → `E_UNAUTHORIZED`.
  6. **HMAC** computed with `auth_key'` (derived on-the-fly). Server **does not store** `auth_key` or `token_secret`; it stores only `verifier`. `[R1]`

**Single normative formula `[R1]`:** `auth_key = HKDF-SHA256(ikm = token_secret_raw_bytes (32 bytes, strictly base64url-decoded), salt = token_id (UTF-8), info = "workspace-bridge/0.2.6 auth key", L = 32)`. **No per-token salt.** Reproduced identically in runbook, tests, register.

#### 3.6.2 Canonical signed bytes `[R1]`
`canonical = JCS({schema, request_id, request_digest, issued_at, expires_at, auth:{token_id, client_id, nonce, tls_channel_id}, method, params})`. **NFC enforced:** non-NFC string → `E_NORMALIZATION` (reject; no silent normalize). `signature = HMAC-SHA256(auth_key', "agi/sig/v1:" ‖ canonical)`, base64.

#### 3.6.3 Client binding `[R1]`
`client_id` is signed, **not strong device proof** (token theft = impersonation). **Owner options (WB-U16):** channel binding (`tls_channel_id` = `tls-exporter` RFC 9266, verified against TLS session, included in canonical bytes) or client-held proof key. If neither → **documented limitation**.

#### 3.6.4 Nonce `[R1]`
Durable SQLite (WAL) at restricted path. Atomic: `INSERT OR IGNORE` into `nonces(token_id, nonce, request_id, seen_at, expires_at, PRIMARY KEY(token_id, nonce))`; `changes()==0` → `E_REPLAY`. Survives restart. Cache loss/corruption → **refuse start**.

#### 3.6.5 Install marker vs cache deletion `[R1]`
- **Owner-controlled bootstrap marker:** `install_id` (UUID) + `install_signature` (Ed25519 by **owner audit key**) recorded **outside** the nonce store, at owner-designated restricted location.
- **Startup logic:**
  - `install_id` + `install_signature` present + nonce store present + non-empty → normal.
  - `install_id` present + nonce store missing/empty → **cache deletion/corruption** → **refuse start** (`E_NONCE_CACHE_LOST`).
  - `install_id` absent + nonce store absent → **genuine first install only if owner re-initialization authorization is presented** (`OWNER_REINIT_TOKEN`, signed by owner audit key). Without it → **refuse start** (`E_INSTALL_UNAUTHORIZED`).
  - `install_id` absent + nonce store present → inconsistent → **refuse start**.
- **Rationale:** deleting both marker + store is **not** indistinguishable from fresh install (requires owner-signed reinit token). `[R1]`

#### 3.6.6 Expiry
Credential `token_expires_at` ≤ 90 days → `E_EXPIRED`. Request `expires_at` ≤ 5 min → `E_EXPIRED`. Both enforced. Clock skew ≤ 30 s.

#### 3.6.7 Rotation
≤ 90 days; overlap ≤ 24 h; compromise → immediate revoke + reissue, overlap disabled.

#### 3.6.8 Revocation
Kill-switch (durable) checked **before** HMAC; `E_REVOKED` ≤ 1 s.

#### 3.6.9 Rate limit
60/60s per `token_id`; `max_requests` cap → `E_RATE_LIMITED`.

### 3.7 Fail-closed
Unknown policy, invalid scope, audit-write failure, auth failure, path violation, path race, sensitive file, unsupported type, nonce cache loss, normalization failure, scan-limit exceed, missing install marker, unauthorized reinit, **mount identity indeterminate**, **unanchored audit tail present** → **deny** / **refuse start**. Never broaden.

### 3.8 Durable audit `[R3]`

#### 3.8.1 Classification
`class`: `AUTH`, `ACCESS`, `DENY`, `ADMIN`. Determines retention.

#### 3.8.2 Trusted integrity anchoring + checkpoint `[R3]`
- **Genesis anchor:** `anchor_id` (UUID) + `anchor_hash` (SHA-256 of genesis record) + `anchor_signature` (Ed25519 by **audit signing key**).
- **Audit signing key custody:** **owner-pinned** public key, recorded out-of-band (WB-U17).
- **Mandatory external checkpoints `[R3]`:** exported to a **separate, owner-controlled sink** (not served root) at **every N records (default 100) or T seconds (default 60)**.
- **Checkpoint record `[R3]`:**
  ```json
  {
    "schema": "agi/audit-checkpoint/1",
    "anchor_id": "uuid (binds to audit stream identity)",
    "checkpoint_seq": "integer (monotonic, starts at 1)",
    "head_seq": "integer (last audit_seq covered)",
    "head_hash": "hex (record_hash of last covered record)",
    "issued_at": "iso8601",
    "signature": "base64 (Ed25519 over JCS(checkpoint minus signature) by audit signing key)"
  }
  ```
  - **Signature covers:** `anchor_id`, `checkpoint_seq`, `head_seq`, `head_hash`, `issued_at`.
  - **Sink records:** verifier stores each checkpoint with `checkpoint_seq`; **monotonicity enforced** (strictly increasing; older/conflicting → `E_CHECKPOINT_CONFLICT`).
- **Checkpoint export failure** → **deny new requests** (`E_ANCHOR_FAILED`) until export succeeds.

#### 3.8.3 Atomic append / concurrency
Single-writer lock (`flock`/`LockFileEx`); queue bounded; full → `E_AUDIT_FAILED`. Atomic append + `fsync`. Monotonic `audit_seq` per anchor.

#### 3.8.4 Crash recovery, anti-rollback, unanchored-tail policy `[R3]`

**3.8.4.1 Startup verification:**
- Verify chain from `anchor_hash`.
- **Truncated last line** → truncate to last valid; log recovery.
- **Sequence continuity:** `audit_seq` strictly monotonic, no gaps. Gap → **refuse start**.

**3.8.4.2 Anti-rollback — external monotonic anchor `[R3]` (NEW — genuine, not a signed local record):**
- **Problem:** a signed local record does **not** prove it is the newest one. An attacker with local write access can replace the current record with an older, previously valid signed record.
- **Normative mechanism `[R3]`:** the **latest checkpoint `checkpoint_seq` + `head_hash`** is anchored to an **external, independently monotonic source** that the bridge **reads but does not control**:
  - **Option A (owner-approved, preferred):** an **external timestamping authority** (RFC 3161 TSA) or **transparency log** (e.g., a Merkle-tree log with signed tree heads) that the bridge queries. The bridge verifies the external tree head signature and that the checkpoint is **included** in the log.
  - **Option B (fallback, owner-approved):** a **write-once / append-only medium** (e.g., a separate owner-controlled host, a WORM store, or a signed append-only file on a different device) that the bridge **cannot rewrite**. The bridge verifies the external head signature + sequence monotonicity across restarts.
- **Both options require owner approval (WB-U23).** **The bridge must NOT rely on a locally writable record as the anti-rollback authority.** `[R3]`
- **If no external monotonic anchor is provisioned** → **the bridge refuses to start** (`E_EXTERNAL_ANCHOR_UNAVAILABLE`). **No protected request proceeds without genuine anti-rollback.** `[R3]`

**3.8.4.3 Startup comparison rules `[R3]` (exact):**
- Read **latest checkpoint** from external sink (per §3.8.4.2).
- Read **external monotonic head** (per §3.8.4.2).
- **Comparison:**
  - **If sink latest `checkpoint_seq` < external head `checkpoint_seq`** → **sink rollback detected** → **refuse start** (`E_CHECKPOINT_ROLLBACK`).
  - **If sink latest `checkpoint_seq` == external head `checkpoint_seq` but `head_hash` differs** → **conflict** → **refuse start** (`E_CHECKPOINT_CONFLICT`).
  - **If local log `head_seq` < external head `head_seq`** → **local rollback** → **refuse start** (`E_ROLLBACK_DETECTED`).
  - **If local log `head_seq` == external head `head_seq`:**
    - **Must** have `local head_hash == external head head_hash`. If differs → **refuse start** (`E_CHECKPOINT_CONFLICT`).
  - **If local log `head_seq` > external head `head_seq`** (local ahead):
    - **Allowed for startup**, **but** the local tail beyond `external head head_seq` is **unanchored** (see §3.8.4.4). **Protected requests remain blocked** until the tail is independently authenticated (§3.8.4.5).
    - **The local chain must be proven to extend from `external head head_hash`** (i.e., `local[external_head_head_seq].record_hash == external_head_head_hash` and subsequent records chain correctly). If not → **refuse start** (`E_ROLLBACK_DETECTED`). `[R3]`
- **If external anchor unavailable at startup** → **refuse start** (`E_EXTERNAL_ANCHOR_UNAVAILABLE`). `[R3]`
- **`anchor_id` binding:** the external anchor must bind the **`anchor_id`** (audit stream identity), not merely sequence/hash. A checkpoint for a different `anchor_id` is **rejected** (`E_ANCHOR_MISMATCH`). `[R3]`

**3.8.4.4 Unanchored-tail operational rule `[R3]`:**
- **Definition:** records after the latest **independently authenticated** checkpoint (external head) are **unanchored** (locally chained, not independently authenticated).
- **Normative rule:** **while any unanchored tail exists, the bridge refuses to serve protected requests** (`E_AUDIT_UNANCHORED`). The bridge may serve **only** `workspace_roots` (metadata) if owner explicitly approves a read-only-metadata exemption; otherwise **all requests fail closed** until a new checkpoint covers the tail. `[R3]`
  - **Rationale:** an audit system cannot claim reliable evidence of protected reads if recent records may have been fabricated. **No protected operation proceeds on an unauthenticated audit tail.**
  - **Recovery:** when the tail is covered by a new valid checkpoint (per §3.8.4.5), normal service resumes.

**3.8.4.5 Checkpointing an untrusted tail `[R3]` (NEW — prevent auto-blessing):**
- **Problem:** if the bridge automatically signs and exports a checkpoint over an unanchored tail, it can turn fabricated local records into independently signed evidence.
- **Normative rule `[R3]`:** **the bridge MUST NOT automatically checkpoint an unanchored tail.**
  - **A checkpoint may be created over a tail ONLY after one of:**
    1. **Independent reconciliation (owner-approved):** an **owner-designated reconciler** (separate from the bridge) reviews the tail, verifies each record against expected protected-read evidence, and **signs a reconciliation record** (`reconciliation_signature`) that authorizes checkpointing. **The bridge does not self-approve.**
    2. **Tail discarded:** if reconciliation is not performed within the owner-defined window (WB-U24), the **unanchored tail is discarded** (truncated to the latest independently authenticated checkpoint), and the bridge resumes from that checkpoint. **Discarded records are not evidence.**
  - **Until reconciliation or discard, the tail remains unanchored and protected requests remain blocked.** `[R3]`
  - **A re-chained but untrusted tail** (fabricated valid chain) is **treated as untrusted**; it **cannot be checkpointed** without independent reconciliation. `[R3]`
- **Recovery deadlock prevention `[R3]`:**
  - The **background checkpoint mechanism** operates **independently of protected-request blocking**: it attempts reconciliation/discard per §3.8.4.5 even while protected requests are blocked.
  - **If reconciliation is unavailable** (reconciler offline), the bridge **discards the tail after the owner-defined window (WB-U24)** and resumes from the last independently authenticated checkpoint. **This guarantees liveness** (no permanent deadlock). `[R3]`
  - **Protected requests remain blocked** until the tail is either reconciled (checkpointed) or discarded. `[R3]`

**3.8.4.6 Local `last_seq`/`last_record_hash` supplementary; external anchor + checkpoint are authoritative. `[R3]`**

#### 3.8.5 Durable sync
`fsync()` after every record; directory fsync after anchor + checkpoint export + external-anchor update.

#### 3.8.6 Retention — G25-07 (PROPOSED — owner decision required)
**G25-07 (owner-approved):** raw evidence 30 days; approved sanitized summaries/manifests/disposal records 3 years after milestone.

**Proposed classification (PROPOSED, NOT owner-approved — WB-U4):**
- `AUTH`, `DENY`, `ADMIN` → raw operational evidence → **30 days** (G25-07 raw).
- `ACCESS` → operational log (no content, relative paths) → **proposed 90 days** (WB-U4; **not approved; not applied**).
- Sanitized audit summary → **3 years after milestone** (G25-07).
- **Until WB-U4 owner approval, all classes default to 30 days (raw period).**
- **Disposal:** owner approval per G25-07; no auto-delete.
- **Location:** restricted sink (`AGI_EVIDENCE_ROOT` if provisioned; else owner-designated). **Missing sink → refuse start.**

#### 3.8.7 Verification
Startup full chain verify from `anchor_hash` + external anchor; on-demand; periodic background verify; mismatch → refuse new requests.

#### 3.8.8 Redaction
No prompt contents; `token=`/`password=`/`secret=`/`ghp_`/`sk-` → `[REDACTED]`; relative paths only.

#### 3.8.9 Fail-closed
Audit-write failure → `E_AUDIT_FAILED`; corrupt → refuse start; missing sink → refuse start; **external anchor unavailable → refuse start (`E_EXTERNAL_ANCHOR_UNAVAILABLE`)**; checkpoint rollback/conflict → refuse start; **unanchored tail present → `E_AUDIT_UNANCHORED` (no protected request)**; discarded tail not accepted as evidence; **auto-checkpointing an untrusted tail is prohibited** (requires reconciliation or discard).

### 3.9 Search / Git leakage
Search: deny subtrees never searched; no filenames; snippets redacted; relative only; scan budget. Git: deny excluded; `excluded_count` suppressed; no log/diff/blobs; no remote URLs; `head_commit` hash only. Tree: omit deny; suppressed count. **`workspace_roots`: deny-matched roots omitted; suppressed count.**

### 3.10 Git read-only implementation `[R8]`

**Selected library: `pygit2` pinned to a version compatible with the runtime Python + libgit2.** `[R8]`

**Version compatibility `[R8]` (corrected — KING R8):**
- **Runtime Python: 3.13** (SILVERSTONE-VERIFIED: 3.13.15).
- **pygit2 1.15.0 supports Python 3.9–3.12 only** — **incompatible with Python 3.13**. **pygit2 1.16+ is required for Python 3.13.** `[R8]`
- **Normative pin `[R8]`:** **`pygit2 1.16.0`** (supports Python 3.13) + its bundled **`libgit2 1.8.x`** (pygit2 1.16 bundles libgit2 1.8). **Do NOT use pygit2 1.15 + libgit2 1.7** (incompatible with Python 3.13; libgit2 1.7 is for pygit2 1.15). `[R8]`
- **Owner approval required (WB-U19):** confirm `pygit2 1.16.0` + `libgit2 1.8.x` is the approved combination. **If a different combination is approved, the exact `pygit2.__version__` + `pygit2.LIBGIT2_VERSION` + `sys.version` must be recorded at startup in output.** `[R8]`

**Valid Python-level no-refresh invocation `[R8]` (corrected — KING R8):**
- **Problem:** `pygit2.Repository.status()` (high-level) takes `untracked_files` and `ignored`, **not** a `flags` argument. `GIT_STATUS_OPT_NO_REFRESH` is a **libgit2 C-level** status option; the high-level Python method does **not** accept it. `[R8]`
- **Normative `[R8]`:** use the **explicit libgit2 status options** via pygit2's **lower-level API**:
  - **pygit2 ≥ 1.14 exposes `pygit2.enums.StatusOption`** with `GIT_STATUS_OPT_NO_REFRESH`. **Normative call:**
    ```python
    import pygit2
    from pygit2.enums import StatusOption
    opts = (StatusOption.GIT_STATUS_OPT_NO_REFRESH
            | StatusOption.GIT_STATUS_OPT_INCLUDE_UNTRACKED
            | StatusOption.GIT_STATUS_OPT_RECURSE_UNTRACKED_DIRS
            | StatusOption.GIT_STATUS_OPT_RENAMES_HEAD_TO_INDEX)
    status = repo.statuses(opts)   # pygit2.Repository.statuses(file_status_cb=None, flags=opts)
    ```
    - **`repo.statuses(flags=opts)`** is the **documented pygit2 method** that accepts `StatusOption` flags (including `GIT_STATUS_OPT_NO_REFRESH`). `[R8]`
  - **If the pinned pygit2 version does not expose `StatusOption.GIT_STATUS_OPT_NO_REFRESH`** → **`workspace_git_status` returns `E_GIT_UNAVAILABLE`** (do not fall back to `repo.status()` default, which may refresh). `[R8]`
- **No-refresh guarantee `[R8]`:**
  - `GIT_STATUS_OPT_NO_REFRESH` bypasses the default **soft index reload** (documented libgit2 behavior). **Index file not written.**
  - **Verification:** test asserts `.git/index` SHA-256 unchanged before/after `workspace_git_status`.
- **fsmonitor `[R8]`:** libgit2 does **not** execute `fsmonitor` for `git_status_list` by default; **no `git_futils_fsync` / index refresh**.
- **External drivers `[R8]`:** libgit2 `git_status_list` does **not** invoke external diff/merge drivers; **no helper execution**.
- **No `system()`/`popen()`** in bridge. `[R8]`

**Exact metadata + object reads required for status `[R8]`:**
- **Metadata:**
  - `.git/HEAD` (symbolic ref).
  - `.git/refs/heads/*` (loose refs).
  - `.git/packed-refs` (packed refs — **required**).
  - `.git/index` — **read only** (no refresh, no write).
  - **`.git/config`** — **read only** (for `core.repositoryformatversion`, `core.filemode`, `core.ignorecase`; **required** for status semantics). `[R8]`
  - **`.git/info/exclude`** — **read only** (ignore rules; **required** for accurate untracked detection). `[R8]`
  - **`.gitignore`** files in worktree — **read only** (per-directory ignore rules; **required** for accurate status). `[R8]`
- **Object reads (required for status calculation) `[R8]`:**
  - **`git_status_list` internally reads** commits (HEAD, refs), trees, blobs (for diff HEAD vs index vs workdir). **These object reads are read-only** (libgit2 reads objects, never writes). `[R8]`
  - **`.git/objects/**`** — read only (commits/trees/blobs). **No object writes.**
- **No other `.git` content exposed** (no hooks, no logs beyond HEAD/refs, no `index` writes). `[R8]`

**`.git` read boundary `[R5][R8]`:** `.git/**` deny (D-6) applies to **all methods except `workspace_git_status`**; `workspace_git_status` reads **only** the metadata + objects enumerated above. **Narrowly scoped.**

**If no-refresh guarantee cannot be established for the pinned version:** `workspace_git_status` returns **`E_GIT_UNAVAILABLE`** — **no shell fallback**. `[R8]`

### 3.11 D02 policy enforcement `[R7]`

#### 3.11.1 Per-operation decision
Every request requires a **D02 decision** (envelope per §2). Input: `{principal, action, resource, policy_version}` → `allow/deny` + `decision_id` + `request_id` + `request_digest` + `issuer_key_id` + `signature` + `expires_at`.

#### 3.11.2 Decision authenticity + request binding `[R7]`
- **Signed decision envelope (§2):**
  - `canonical = JCS({schema, decision_id, request_id, request_digest, principal, action, resource, policy_version, decision, issued_at, expires_at, issuer_key_id})`.
  - `signature = Ed25519_sign(issuer_privkey, "agi/d02-decision/v1:" ‖ canonical)`, base64.
  - **Issuer trust:** verifier holds **owner-pinned D02 issuer public key** (`issuer_key_id` → pinned key). Unknown → `E_POLICY_UNVERIFIABLE`.
  - **Expiry:** `expires_at` enforced (≤ 5 min); expired → `E_POLICY_EXPIRED`.
  - **Server-side request-digest recomputation `[R7]`:**
    - Server **recomputes** `request_digest' = SHA-256(JCS({method, params}))` from the **received** method + params (after normalization/validation).
    - **Reject** if `request_digest' != envelope.request_digest` → `E_DIGEST_MISMATCH`.
    - **Reject** if `decision.request_digest != request_digest'` → `E_POLICY_MISMATCH`.
  - **Request binding `[R7]`:**
    - `decision.request_id == envelope.request_id` (else `E_POLICY_MISMATCH`).
    - `decision.principal == auth.client_id` (else `E_POLICY_MISMATCH`).
    - `decision.action == "workspace.<method>"` (else `E_POLICY_MISMATCH`).
    - `decision.resource == (root_alias + normalized path)` or `"*"` for `workspace_roots` (else `E_POLICY_MISMATCH`).
  - **Replay of a decision with a different request ID/digest `[R7]`:** mismatch → `E_POLICY_MISMATCH` (deny).
  - **Stale:** `issued_at` older than `policy_max_age` (default 300 s) → `E_POLICY_STALE`.
  - **Revoked:** `issuer_key_id` or `decision_id` on revocation list → `E_POLICY_REVOKED`.

#### 3.11.3 `workspace_roots` resource semantics `[R7]`
`workspace_roots` has no caller-supplied path. Its **resource** = `"*"`. D02 decision: `action = "workspace.workspace_roots"`, `resource = "*"`. Deny → `E_DENIED`.

#### 3.11.4 Boundary enforcement
No D02 decision → `E_NO_POLICY`. D02 `deny` → `E_DENIED`. Decision for different `(principal, action, resource, request_id, request_digest)` → `E_POLICY_MISMATCH`.

#### 3.11.5 Stale/expired/revoked/unverifiable
`E_POLICY_STALE`, `E_POLICY_EXPIRED`, `E_POLICY_REVOKED`, `E_POLICY_UNVERIFIABLE` (fail-closed).

#### 3.11.6 Audit-before-access
1. **Pre-access:** durable intent + authorization record (`fsync`) **before** any filesystem access.
2. **Access:** filesystem read.
3. **Post-access:** durable effect/result record.
4. **Audit-write failure at step 1 → `E_AUDIT_FAILED` → deny; read never occurs.**

### 3.12 Untrusted data
File contents returned as **untrusted data**, never executable instructions.

---

## 4. Excluded from exposure (non-negotiable)
`.reference`, `AGI.Original Data`, private archives/backups/memory/sessions, keys/tokens/secrets, any unapproved path.

---

## 5. What the bridge MUST NOT do
No shell/process execution, writes, Git mutation, signing/approval/credential issuance/policy admin; no extension of H0/Web Bridge; no `.git` internals beyond `workspace_git_status` metadata; **no silent transformation of source content**; **no automatic checkpointing of an untrusted tail**.

---

## 6. Relationship to H0 / FCC / D02 (preserved)
H0 metadata-only; FCC policy/validation; D02 independent enforcement + per-request authorization (§3.11); Web Bridge (transport) ≠ Workspace Bridge (filesystem read). Do not merge.

---

## 7. Versioning
Schema `workspace-bridge/0.2.6`. Unknown → `E_VERSION`.

---

## 8. Unresolved owner decisions (reconciled)

| ID | Decision | Blocks |
|---|---|---|
| WB-U1 | Approved root aliases + contents | All |
| WB-U2 | Token issuance/rotation ceremony | Auth |
| WB-U3 | Rate-limit values (default 60/60s) | Ops |
| WB-U4 | Audit sink + per-class retention (**PROPOSED: AUTH/DENY/ADMIN 30d raw; ACCESS 90d operational; sanitized 3y — NOT approved; default 30d**) | Audit |
| WB-U5 | Git metadata scope | `workspace_git_status` |
| WB-U6 | Text-only vs future binary | Scope |
| WB-U7 | Revocation SLA (≤ 1s) | Auth |
| WB-U8 | Tunnel provider + host (conditional on account check) | Deployment |
| WB-U9 | ChatGPT account MCP capability (NOT ESTABLISHED) | Connection |
| WB-U10 | Review-root layout + contents | Deployment |
| WB-U11 | POSIX vs Windows fd-API implementation | Implementation |
| WB-U12 | Nonce cache backend (SQLite WAL) | Replay |
| WB-U13 | Audit verify cadence | Audit |
| WB-U14 | Token overlap exact (≤ 24h) | Rotation |
| WB-U15 | `excluded_count` (default suppressed) | Leakage |
| WB-U16 | Client binding: channel binding / proof key / documented limitation | Auth |
| WB-U17 | Audit signing key custody + pin location | Audit trust |
| WB-U18 | D02 policy source + `policy_max_age` + issuer key pin | Policy |
| WB-U19 | Read-only Git library (**pygit2 1.16.0 + libgit2 1.8.x for Python 3.13**; `repo.statuses(flags=...)`) | Git |
| WB-U20 | Search scan budget values | Search |
| WB-U21 | Same-volume Windows mount-point residual (unresolved) | Mount boundary |
| WB-U22 | Post-checkpoint unanchored tail disposition (**fail-closed; metadata-only exemption optional**) | Audit trust |
| WB-U23 | External monotonic anchor for anti-rollback (TSA / transparency log / WORM) | Audit trust |
| WB-U24 | Reconciliation window + reconciler identity (before tail discard) | Audit recovery |

**WB-U1..U24 reconciled across spec, runbook, register.**

---

## 9. Minimal sanitized review-root layout
```
review-root/                      # alias: "review"
├── docs/review/repository-rationalization/2026-11-16/   # 6 sanitized audit docs
├── contracts/                    # D02, SSL (sanitized)
├── AGI_SKILL_CONNECTION_ASSESSMENT_2026-11-17.md
└── WORKSPACE_BRIDGE_SPEC_v0.2.6.md
```
Only sanitized, owner-approved files; no `.reference`/private/secrets; relative paths; read-only; `excluded_count` suppressed; names never listed. Owner approves exact roots (WB-U10).

---

## 10. Status
**PROPOSED SPEC v0.2.6 — NOT IMPLEMENTED, NOT ACTIVATED, NOT EXPOSED.**

**Awaiting owner authorization to implement and expose.**