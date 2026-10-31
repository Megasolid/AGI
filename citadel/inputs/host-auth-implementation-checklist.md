# Cross-host auth + private-recall — final implementation checklist

**Status:** checklist for Director/Kilo review; no implementation or runtime integration.
**Amendments from Director:** host/resource-bound grants, no wildcards; nonce/clock/canonical request signing + atomic
replay cache; immediate/fail-closed revocation; audit without payloads/secrets; shared access separate.

## A. Contracts/schema
- [ ] Host-grant schema: grant_id, host_id, host_instance_id, organism_id, resource_class, permitted_operations,
      allowed_visibility (private/shared_authorized only), allowed_classes/tags, issued_at, expires_at, revoked,
      Master signature. Reject wildcard/empty/ambiguous grants.
- [ ] Request-proof schema: host_instance_id, request_id, nonce, timestamp, canonical args_digest, Ed25519 signature.
- [ ] Revocation schema: Master-signed revoke record + reason; grant/host lookup checks it on every request.
- [ ] Document canonical JSON, clock-skew window, and nonce/replay cache table.

## B. Enforcement
- [ ] `runtime/agi_host_auth.py` (prototype) verifies host proof, grant binding, expiry/revocation, resource/class/visibility.
- [ ] Deny by default; missing/ambiguous/forged host => structured denial + audit; no data returned.
- [ ] Atomic replay cache (`INSERT OR IGNORE` on nonce/request_id) with bounded window; duplicates rejected and audited.
- [ ] Private recall only same host_instance_id; shared only approved recipient + grant; family/public disabled.
- [ ] Filter FTS/vector candidates before top-k; no count/rank leak; export metadata only with grant scope.
- [ ] MCP/bridge derives context from verified request; bearer alone insufficient; all tools fail closed.
- [ ] Revocation state unavailable => deny all (fail closed), audit.
- [ ] Audit records host/request/decision/resource ids/counts only; no bodies/secrets; tamper-evident.

## C. Tests (adversarial)
- [ ] forged host -> deny + audit
- [ ] replayed nonce/request -> deny + audit; atomic race test
- [ ] expired/revoked grant -> deny; immediate revocation; revocation-state-unavailable -> deny
- [ ] cross-host private recall/search -> no data/no count leak; same-host allowed
- [ ] shared approved cross-host recall allowed only with grant; missing/wrong recipient denied
- [ ] family/public denied placeholders
- [ ] shared/private boundary: no private body in shared store/export/snapshot/log/adapters
- [ ] MCP bypass: missing/spoofed context, wrong token binding, direct tool calls denied
- [ ] clock-skew bounds (past/future), malformed signature
- [ ] v4/M1 regression + rollback on copy; Kilo independent review/retest

## D. Rollout
- [ ] Feature flag off; isolated prototype; shadow log-only; Director approval; canary; rollback restore.
- [ ] v4.0.1/M1/M2 preserved; no federation/identity mutation/autonomous evolution.
