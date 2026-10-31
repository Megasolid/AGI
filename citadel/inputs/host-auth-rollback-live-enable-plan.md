# Host-auth/private-recall — rollback + live-enable plan (for later Director review)

**Status:** plan only; `AGI_M2_HOST_AUTH=off`; no live integration.
**Prerequisite:** Kilo independent verification of the 27-case prototype + Director explicit decision.

## Rollback
- Backup live `state/index/agi.db`, `state/entelechy/state/agi.db`, runtime files, and flag/config prior to any change.
- Record SHA-256 manifests; deploy only with feature flag off; enable behind flag after shadow validation.
- Rollback: set flag off → restore runtime/index backups → verify hashes, boot gate 13/13, M1 40/40, remediation tests.
- No destructive migration in this phase; host grants/audit live in additive state/agi5 stores.

## Live-enable stages
1. Isolated prototype verified by Kilo (27 cases, six critical gates).
2. Shadow mode: policy evaluates every read, logs would-deny, returns current data; compare, no enforcement.
3. Canary: enforce on one local host; verify positive/negative controls; monitor audit.
4. Full local enable: flag on for all read paths; keep family/public disabled; shared separate.
5. Director review/approval before any release asset change.
- Stop rule: any cross-host/private leak, fail-open revocation, or count/rank leak → flag off + rollback.
- No federation, family/public sharing, identity mutation, autonomous evolution.
