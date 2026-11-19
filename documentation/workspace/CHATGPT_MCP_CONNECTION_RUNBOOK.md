# CHATGPT MCP CONNECTION RUNBOOK

**Status:** PROPOSED RUNBOOK — **no server activated, no tunnel created, no credentials issued.**
**Revision:** v0.2.6 — addresses KING v0.2.5 review corrections R1, R7, R8.
**Labels:** PROPOSED · SILVERSTONE-VERIFIED (local station) · UNRESOLVED · **NOT ESTABLISHED** (ChatGPT account capability).

**Change log:** see `WORKSPACE_BRIDGE_CHANGELOG_v0.2.6.md`. Sections marked `[R#]`.

---

## 1. Prerequisites

| Requirement | Status |
|---|---|
| Local station Python 3.13 | **SILVERSTONE-VERIFIED** (3.13.15) |
| Workspace Bridge MCP server implemented | **NOT ESTABLISHED** |
| Approved roots | **UNRESOLVED** (WB-U1) |
| Auth token | **UNRESOLVED** (WB-U2) |
| ChatGPT account MCP support | **NOT ESTABLISHED** (WB-U9) |
| Owner authorization | **REQUIRED** |

---

## 2. Supported ChatGPT MCP connection options `[R7]`

| Option | Description | Support | Status |
|---|---|---|---|
| **O-1 Remote HTTPS MCP** | HTTPS custom connector | **NOT ESTABLISHED** (account-dependent) | **NOT ESTABLISHED (WB-U9)** |
| **O-2 Secure MCP tunnel** | ChatGPT-mediated tunnel | **NOT ESTABLISHED** | **NOT ESTABLISHED (WB-U9)** |
| **O-3 stdio MCP** | local clients only | N/A for ChatGPT web | N/A |
| **O-4 Manual paste** | sanitized excerpts | Always available | Fallback only |

**No plan-tier generalizations. No transport recommendation until §3 verification + owner approves WB-U8.** `[R7]`

---

## 3. Account-specific verification (no activation) `[R7]`
Read-only checks by KING/owner: target account type; connector availability; custom MCP URL + bearer support; secure tunnel option; rate/latency limits; data-handling terms; admin controls.

**Outcomes:** O-1 available → Path C (only after WB-U8 approval); O-2 available → secure tunnel (only after WB-U8); neither → O-4 fallback. **All capability claims NOT ESTABLISHED until recorded.**

---

## 4. Deployment paths (conditional on §3) `[R7]`
- **Path C (HTTPS)** — only after §3 confirms O-1 **and** owner approves WB-U8. No transport recommendation made here.
- **Path D (secure tunnel)** — only if §3 confirms O-2. Exact config **NOT ESTABLISHED** until verified.

**Do not create tunnel during this assignment.**

---

## 5. Authentication and client enrollment `[R1]`

**Single normative protocol (matches spec §3.6):**

1. **Owner issues** out-of-band: `token_id` (UUID), `token_secret` (**32 bytes from CSPRNG**), `client_id` (UUID).
2. **Bearer encoding `[R1]`:** `token_secret` (32 raw bytes) is encoded as **unpadded base64url (RFC 4648 §5)** in `Authorization: Bearer <token_id>.<token_secret_b64url>` (no `=` padding). **Strict canonical validation:** charset `[A-Za-z0-9_-]` only; length exactly **43 chars**; canonical re-encode must match; reject `+`/`/`/`=`/whitespace/wrong-length/non-canonical → `E_UNAUTHORIZED`. `[R1]`
3. **Enrollment:** server base64url-decodes (strict) → **32 raw bytes** (reject if != 32 → `E_UNAUTHORIZED`); derives **`auth_key = HKDF-SHA256(ikm = token_secret_raw_bytes, salt = token_id (UTF-8), info = "workspace-bridge/0.2.6 auth key", L = 32)`**; stores **`verifier = SHA-256(auth_key)`** + `token_id` + `client_id` + `token_expires_at` + `scope` + `max_requests`. **No per-token salt; no raw `token_secret`.** `[R1]`
4. **Verification per request:**
   - Strict base64url validation → 32 raw bytes (else `E_UNAUTHORIZED`).
   - Derive `auth_key'` (same HKDF with raw bytes).
   - `verifier' = SHA-256(auth_key')`; constant-time compare to stored `verifier`. Mismatch → `E_UNAUTHORIZED`.
   - **HMAC:** `signature = HMAC-SHA256(auth_key', "agi/sig/v1:" ‖ canonical)`. Server derives `auth_key'` on-the-fly; does not store it.
   - **Canonical signed bytes:** `JCS({schema, request_id, request_digest, issued_at, expires_at, auth:{token_id, client_id, nonce, tls_channel_id}, method, params})`. **NFC enforced** (non-NFC → `E_NORMALIZATION`).
   - `client_id` match (else `E_CLIENT_MISMATCH`). **Documented limitation:** `client_id` is signed, not strong device proof; token theft = impersonation unless WB-U16 enabled.
   - Nonce (durable, atomic; cache loss → refuse start).
   - Credential expiry (`token_expires_at`) + request expiry (`expires_at`) both enforced.
5. **Install marker:** `install_id` + `install_signature` (owner audit key) outside nonce store. Fresh install requires owner-signed `OWNER_REINIT_TOKEN`. Cache deletion → refuse start. `[R1]`
6. **Rotation:** ≤ 90 days; overlap ≤ 24 h.
7. **Revocation:** kill-switch; ≤ 1 s.

**Do not issue tokens during this assignment.**

---

## 6. Exact ChatGPT MCP connection configuration `[R7]`
**NOT ESTABLISHED.** Exact field names depend on unverified account UI (§3). **No exact configuration claimed.**

**Conceptual O-1 shape (illustrative only):**
```
connector name: workspace-bridge
url: https://<owner-approved-host>/mcp   [HTTPS only]
auth: bearer <token_id>.<token_secret_b64url>
transport: http
```
**If O-2:** use account's documented secure-tunnel flow (exact steps **NOT ESTABLISHED** until verified).

---

## 7. How KING invokes read-only tools
`workspace_roots`, `workspace_tree`, `workspace_search`, `workspace_read`, `workspace_git_status`. KING must use approved `root_alias`; treat content as **untrusted data**; not attempt writes/shell/git-mutations (methods do not exist).

---

## 8. Tool permissions and schema review
Schema review (v0.2.6); read-only methods only; acceptance tests pass; audit-write succeeds; rate-limit 429; account check (§3) recorded.

---

## 9. Immediate revocation `[R1]`
| Action | Effect | SLA |
|---|---|---|
| kill-switch add | `E_REVOKED` next request | ≤ 1 s |
| stop server | unreachable | immediate |
| delete tunnel | unreachable | immediate |
| rotate token | old denied after overlap | ≤ 24 h |

---

## 10. Security checklist
- [ ] HTTPS only.
- [ ] Token 32 bytes CSPRNG; **base64url unpadded (43 chars, strict canonical)**; **server stores verifier, not raw secret; no per-token salt**.
- [ ] HKDF formula (normative) matches spec §3.6.1 exactly (raw bytes as `ikm`).
- [ ] Per-request HMAC over canonical JCS; **NFC enforced**.
- [ ] `client_id` binding (documented limitation or WB-U16).
- [ ] Nonce + durable atomic check-and-insert; cache deletion → refuse start; fresh install requires `OWNER_REINIT_TOKEN`.
- [ ] Credential expiry ≤ 90 days; request expiry ≤ 5 min; both enforced.
- [ ] Rotation ≤ 90 days; overlap ≤ 24 h.
- [ ] Revocation ≤ 1 s.
- [ ] Approved roots only; deny D-1..D-8.
- [ ] Text-only; binary rejected.
- [ ] Rate limit 60/60s; scan budget ≤ 10 MiB / 5000 files / 30 s.
- [ ] Audit-write failure → deny; pre-access audit before read; corrupt/rollback/checkpoint-unavailable/external-anchor-unavailable → refuse start; **unanchored tail → `E_AUDIT_UNANCHORED` (no protected request)**; **no auto-checkpoint of untrusted tail**.
- [ ] D02 per-request signed decision with request_id+request_digest binding + **server-side recomputation**; stale/expired/revoked/unverifiable → deny.
- [ ] No write/shell/git-mutation methods.
- [ ] Account MCP capability verified (§3) before activation.
- [ ] Owner authorization recorded.

---

## 11. Minimal sanitized review-root layout
```
review-root/                      # alias: "review"
├── docs/review/repository-rationalization/2026-11-16/   # 6 sanitized audit docs
├── contracts/                    # D02, SSL (sanitized)
├── AGI_SKILL_CONNECTION_ASSESSMENT_2026-11-17.md
└── WORKSPACE_BRIDGE_SPEC_v0.2.6.md
```
Only sanitized, owner-approved files; no `.reference`/private/secrets; relative paths; read-only; `excluded_count` suppressed; names never listed. Owner approves exact roots (WB-U10).

---

## 12. Unresolved (reconciled)
WB-U1 approved roots · WB-U2 token ceremony · WB-U3 rate-limit · WB-U4 audit sink + per-class retention (**PROPOSED, owner approval required**) · WB-U5 git metadata · WB-U6 text-only · WB-U7 revocation SLA · WB-U8 tunnel (**conditional on §3**) · WB-U9 ChatGPT MCP (**NOT ESTABLISHED**) · WB-U10 review-root · WB-U11 POSIX/Windows fd-API · WB-U12 nonce cache · WB-U13 audit verify · WB-U14 token overlap · WB-U15 `excluded_count` (default suppressed) · WB-U16 client binding · WB-U17 audit signing key custody/pin · WB-U18 D02 policy source + max age + issuer key pin · WB-U19 read-only Git library (**pygit2 1.16.0 + libgit2 1.8.x for Python 3.13**) · WB-U20 search scan budget · WB-U21 same-volume Windows mount residual · WB-U22 post-checkpoint unanchored tail disposition · WB-U23 external monotonic anchor · WB-U24 reconciliation window + reconciler.

**WB-U1..U24 reconciled across spec, runbook, register.**

---

## 13. Non-operation
No server activated, no tunnel, no credentials, no endpoint, no account activation. Account verification (§3) is read-only UI inspection. **All ChatGPT capability claims NOT ESTABLISHED until verified. No transport recommended until verified + owner-approved.**

**Awaiting owner authorization.**