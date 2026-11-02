# H0 — Minimum MCP Security Contract (freeze candidate)

**Status:** SPECIFICATION ONLY. No MCP server, tunnel, credential or exposure exists or is created by this document.
**Authority:** King decision 2026-11-02T19:24 — "H0 authorized to begin; freeze and test before any MCP exposure."
**Date:** 2026-11-02T19:40+0330
**Companion negative-test suite:** `runtime/test_h0_contract.py` (proves prohibited operations are impossible, not merely prohibited on paper).

---

## 1. Principles (non-negotiable)

1. **Deny by default.** A request is rejected unless every gate below passes in order.
2. **Fail closed.** Any error, timeout, unknown state or missing policy result produces a denial, never an allow.
3. **No privileged surface.** The contract defines no tool that can execute shell, read/write arbitrary filesystem paths, mutate Git, sign, approve, or change policy.
4. **A caller is not an authority.** A model response, tool result, approval request, or semantic `COMMIT` is never an authorization grant.
5. **Nothing is exposed until this contract is reviewed and separately authorized.**

---

## 2. Schemas — versioned, strict

### 2.1 Envelope

```
schema            "h0.mcp/1"                       required, const
method            enum of REGISTERED_METHODS        required
scope             one of SCOPES                     required
client_id         string, 1..128, [A-Za-z0-9._-]    required
request_id        string, 1..128, same charset      required
correlation_id    uuid4 format                      required
issued_at         ISO-8601 with timezone            required
expires_at        ISO-8601, issued_at < expires_at  required
nonce             string, 16..128, base64url        required
payload           object                            required
signature         {alg,key_id,signature_b64}        required for every non-HELLO method
```

### 2.2 Unknown-field handling

- Any field not in the envelope schema → **REJECT** (no "ignore unknown"). Reason code `E_UNKNOWN_FIELD`.
- Any field not in the method's payload schema → **REJECT** (`E_UNKNOWN_PAYLOAD_FIELD`).
- Schemas are versioned by the `schema` constant; a request with any other value → `E_SCHEMA_VERSION`.

### 2.3 Compatibility rules

- Adding an **optional** field requires a new schema version.
- Removing or retyping a field is a breaking change and requires a new major version.
- A server must reject any `schema` value it does not explicitly implement. No silent acceptance of future or past versions.

---

## 3. Registered methods and scopes (least privilege)

| Method | Scope | Class | Notes |
|---|---|---|---|
| `HELLO` | `h0.read` | read | identity/version probe; only unsigned method |
| `agi_status` | `h0.read` | read | returns **digests only**, never diffs or file contents |
| `agi_task_list` | `h0.read` | read | task identifiers and states only |
| `agi_task_get` | `h0.read` | read | one task envelope + digest |
| `agi_evidence_get` | `h0.read` | read | evidence **hashes**; no artifact bodies |
| `agi_checkpoint_create` | `h0.write.metadata` | metadata write | checkpoint reference + digest only |
| `agi_receipt_submit` | `h0.write.metadata` | metadata write | receipt tied to a handoff digest |
| `agi_approval_request` | `h0.request` | **request only** | creates a pending request; **cannot approve** |

### 3.1 Explicitly absent (must remain absent)

`exec`, `shell`, `run`, `read_file`, `write_file`, `fs_list`, `git_push`, `git_merge`, `git_tag`,
`release`, `publish`, `sign`, `approve`, `grant`, `revoke`, `policy_set`, `admin`, `sql`, `eval`.

A registration attempt for any of these names must raise `E_FORBIDDEN_METHOD` **at construction**,
so the server cannot exist with a privileged surface even by mistake.

---

## 4. Payload limits (enforceable, with rejection behaviour)

| Limit | Value | Rejection |
|---|---|---|
| `payload` serialized bytes | 16,384 | `E_PAYLOAD_TOO_LARGE` |
| nesting depth | 8 | `E_PAYLOAD_TOO_DEEP` |
| total keys across payload | 256 | `E_PAYLOAD_TOO_WIDE` |
| single string value | 4,096 chars | `E_VALUE_TOO_LONG` |
| array length per field | 128 | `E_ARRAY_TOO_LONG` |
| envelope serialized bytes | 32,768 | `E_ENVELOPE_TOO_LARGE` |

Limits are measured on the **canonical serialization** of the request, so whitespace tricks
and key reordering cannot change the verdict. Depth and width are counted recursively.

---

## 5. Rate limits

| Dimension | Limit | Rejection |
|---|---|---|
| per client, `h0.read` | 120 / 60 s | `E_RATE_LIMIT` |
| per client, metadata writes | 30 / 60 s | `E_RATE_LIMIT` |
| per client, `agi_approval_request` | 10 / 60 s | `E_RATE_LIMIT` |
| burst | 20 in 5 s, any scope | `E_RATE_BURST` |
| per method, global | 600 / 60 s | `E_RATE_LIMIT` |

Sliding-window counters keyed by `(client_id, scope)` and `(method,)`. A limit violation
**must not** consume the request's effect: the method is never executed. Throttling is a
hard rejection, not a queue — a queued request that later fires would break the
"deny is final" property.

---

## 6. Audit records

Every request — allowed *and* denied — produces exactly one audit record:

```
audit_id         monotonic sequence
correlation_id   from the request
client_id        authenticated identity (never the claimed one)
method           requested method
scope            requested scope
request_digest   sha256 of canonical request bytes
decision         allow | deny
reason_code      set when deny
outcome          executed | denied | failed
timestamp        UTC ISO-8601
```

**Never logged:** payload contents, prompt text, model output, credentials, tokens, keys.
Payload is represented **only** by its digest.

If the audit append fails, the request **must fail closed** (`E_AUDIT_UNAVAILABLE`) and the
method must not execute. An unauditable action is a refused action.

---

## 7. Fail-closed matrix

| Condition | Reason code | Effect |
|---|---|---|
| missing/invalid signature | `E_SIG_INVALID` | deny |
| unknown `key_id` | `E_UNKNOWN_KEY` | deny |
| revoked/expired credential | `E_CRED_REVOKED` / `E_CRED_EXPIRED` | deny |
| unknown `client_id` | `E_UNKNOWN_CLIENT` | deny |
| replayed `request_id` or `nonce` | `E_REPLAY` | deny |
| `expires_at` in the past | `E_EXPIRED` | deny |
| unknown field / schema mismatch | `E_UNKNOWN_FIELD` / `E_SCHEMA_VERSION` | deny |
| malformed payload | `E_MALFORMED` | deny |
| limit violation | `E_*_TOO_*` | deny |
| rate/burst violation | `E_RATE_LIMIT` / `E_RATE_BURST` | deny, no execution |
| scope not granted for method | `E_SCOPE` | deny |
| policy engine unavailable | `E_POLICY_UNAVAILABLE` | deny |
| audit append fails | `E_AUDIT_UNAVAILABLE` | deny, no execution |
| anything raises | `E_INTERNAL` | deny |

**Order matters:** authentication → replay → schema → limits → rate → scope → policy →
audit → execute. No gate is skipped when an earlier one passes.

---

## 8. Negative-test requirements (H0 acceptance)

The suite must prove these are **impossible**, not merely documented:

1. Forbidden method registration raises.
2. Forbidden method in a request is denied.
3. Oversized payload, over-deep nesting, over-wide keys rejected.
4. Rate and burst limits reject and do **not** execute the method.
5. Replay of a `request_id` and of a `nonce` both denied; the first effect is not repeated.
6. Expired request, expired credential, revoked credential denied.
7. Wrong scope denied; correct scope allowed.
8. Invalid signature denied; tampered payload denied.
9. Unknown field denied; wrong schema version denied.
10. Audit failure denies **and** the method does not run (side-effect counter stays 0).
11. Policy-unavailable denies.
12. Approval method can **create a request** and can **never** approve, grant or execute.

---

## 9. Boundaries

No MCP server is exposed. No tunnel. No credentials issued. No protected-file change.
Publication BLOCKED; tagging OWNER_APPROVAL_REQUIRED; activation NOT_AUTHORIZED.
H0 completion requires separate review and explicit authorization before exposure.
