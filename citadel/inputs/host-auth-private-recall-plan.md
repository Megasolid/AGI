# M2 security blocker — cross-host authorization + private-recall isolation design/test plan

**Status:** design for Director approval; no implementation/runtime integration.
**Trigger:** Kilo M2 adversarial findings: v4.0.1 recall derives no host context; no private-memory/context isolation;
missing/ambiguous auth returns data; cross-host/family/shared controls blocked. M2 apply + remediation accepted; runtime
integration remains OFF.

## Goal
Make every memory read/export host-bound and deny-by-default. Prove forged hosts, replay, revoked grants, cross-host
search/recall, private/shared boundary leaks and MCP bypasses are rejected with audit evidence.

## Identities and grants
- Reuse M1 Master-signed **host authorization** (host_id, host_instance_id, Ed25519 public key, scopes, expiry, revoked).
- Add Master-signed **per-host memory grant**:
  `{schema, grant_id, host_instance_id, organism_id, allowed_visibility:["private"|"shared_authorized"],
    allowed_classes:[...], allowed_tags:[...], scopes:["recall","search","export_metadata"], expires_at, revoked,
    master_signature}`.
- Private access is **only** for the same host_instance_id; no grant may grant another host's private items unless the
  owner explicitly edits identity/Master policy (out of M2 scope).
- Family/public remain disabled deny-by-default placeholders. Shared requires approved recipient + grant.
- **Host-bound request proof:** request carries host_instance_id, request_id, nonce, timestamp and an Ed25519 signature
  over canonical `{method, args_digest, host_instance_id, nonce, ts}`. Bearer token alone is insufficient.
- Revocation: Master-signed revoke record checked on every request; short TTL cache; denied + audited.

## Enforcement map
| Path | Rule |
|---|---|
| runtime recall | verify host proof+grant; filter visibility/class before FTS/vector top-k; no context => deny |
| search/index | same policy predicate; no unfiltered candidates; vector rank leak prevention |
| MCP bridge tools | token bound to host_instance; derive context from verified request; missing/ambiguous => err + audit |
| export_metadata | grant must include export scope; metadata allowlist only; no bodies |
| snapshot | host-scoped metadata/hash only; no private bodies |
| adapters | no private memory; only allowed shared/public material |
| audit/log | host_instance, request_id, decision, resource ids/counts; never bodies/secrets |
| shared store | separate `state/agi5/shared.db`; never join to private items for unrestricted reads |

## Threat tests (adversarial matrix)
1. forged host_instance (no record / bad signature) -> deny + audit
2. replay same nonce/request_id -> deny; idempotency audit
3. expired/revoked grant -> deny; revocation immediate
4. cross-host private recall -> deny; same-host allowed
5. cross-host search for private term -> no results, no count leak
6. shared approved cross-host recall -> allowed only with recipient+grant; otherwise deny
7. family/public -> deny (placeholders)
8. shared/private boundary: shared store returns no private body; private DB inaccessible from other host
9. MCP bypass: missing/spoofed context, wrong token binding, direct tool calls -> deny
10. export/snapshot/log redaction + denial audit integrity
11. v4/M1 regression (boot 13/13, M1 40/40, remediation tests) and rollback.

## Implementation plan (after approval)
1. Prototype `runtime/agi_host_auth.py` + grant schema in isolated copy; host request proof verify, grant/revocation, deny audit.
2. Wire behind `AGI_M2_HOST_AUTH=off` feature flag; shadow mode log-only; canary; rollback restore backup/flag.
3. Tests: policy unit + isolated integration + adversarial matrix; Kilo independent review/retest; Director approval before live enable.
4. No federation/family/public/identity mutation/autonomous evolution. Keep v4.0.1 stable and M1/M2 restrictions.

## Deliverables
Host-auth/grant schemas, request-proof verifier, enforcement map, adversarial matrix results, audit-redaction evidence,
v4/M1 regression, rollback test, Kilo review.

## Director amendments (2026-10-31) — incorporated
1. Grants bind **host_id, host_instance_id, organism_id, resource_class, permitted_operations, expiry**; wildcard grants rejected.
2. Request proof: **nonce uniqueness**, bounded clock skew, canonical request signing, **atomic replay-cache enforcement**.
3. Revocation takes effect **immediately** at every enforcement point; **fail closed** if revocation state is unavailable.
4. Audit denials/grants **without private payloads or secrets**; tamper-evident records.
5. Shared-memory access is **separate** from private-memory authorization; no implicit fallback.
