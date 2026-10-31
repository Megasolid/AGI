# Host-auth/private-recall — canary proposal (review only; NO canary execution)

**Status:** proposal for Kilo independent review; enforcement OFF; no canary authorized.
**Preconditions:** shadow evidence 11/11 PASS; frozen shadow plan; fresh Owner D + Director GPT explicit canary approval;
Kilo review of this proposal.

## Canary scope (minimal)
- Host: **DSH local only**; no external/Kilo/Claude host, no network ingress.
- First path: **recall only** (read-only memories; no search/export/snapshot/adapter enforcement in Stage 1).
- Enforcement: host-auth proof + grant for DSH local; **private visibility only**; family/public/shared remain disabled.
- No federation, identity/DNA mutation, release-asset change, or autonomous evolution.
- One host grant, Master-signed, with explicit Owner+Director approval ID.

## Preconditions / migration
1. Freeze baseline; backup `state/index/agi.db`, `state/entelechy/state/agi.db`, runtime; record SHA-256.
2. Additive host-auth policy behind `AGI_M2_HOST_AUTH=canary`; flag default off; canary only after explicit approval.
3. Issue one DSH local grant after Owner+Director approval; no other hosts.
4. Verify boot 13/13, M1 40/40, remediation 11/11, prototype 27/27, shadow evidence; audit chain valid.

## Monitoring (canary)
- Recall requests: allow/deny by reason; forged/bad-proof/replay/revocation counters; rate/latency/error.
- Zero-leak: no private body in logs/export/snapshot/adapter; no count/rank leak; shared/family/public denied.
- Boot/M1/remediation checks periodic; audit chain; flag state.
- Owner+Director alerts on threshold breach; 5-min acknowledgement; 15-min rollback decision.

## Abort / rollback
Immediate abort/rollback: any unauthorized body/count leak, audit break, fail-open revocation, boot/M1 fail, flag drift,
error >0.5%, p95 >2x baseline, or missing/ambiguous auth returning data.
Rollback: flag off; restore backups; verify hashes; boot/M1/remediation; preserve audit/approvals; report.
Abort authority: Owner D + Director GPT.

## Duration / success criteria
- Canary window: 24 hours local recall traffic or a pre-agreed request count, whichever first.
- Success: zero leaks/bypasses, expected deny reasons, no boot/M1 regression, audit clean, latency/error within bounds.
- Exit: Owner+Director review; only then consider expanding to search/export or other hosts. No automatic expansion.

## Authorization
- [ ] Kilo independent review of this canary proposal.
- [ ] Fresh Owner D explicit approval for canary scope.
- [ ] Fresh Director GPT explicit approval for same scope.
- [ ] No federation/identity mutation/autonomous evolution.
