# Host-auth/private-recall — final live-enable package (review only; flag OFF)

**Status:** package for Director/Kilo review. `AGI_M2_HOST_AUTH=off`. No live integration.
**Prerequisite:** Kilo prototype audit 27/27 PASS (all six critical gates independently re-executed); explicit owner +
Director authorization required.

## 1. Exact target scope (staged; local only)
- Phase A (shadow): policy layer evaluates every **local** read path, logs would-deny, returns current data; no enforcement.
  Paths: `runtime/agi_runtime.recall`, `tools/agi_index` search, `agi_bridge` read tools/export_metadata, snapshot,
  logging/audit, adapters. Paths outside these are out of scope.
- Phase B (canary): enforce for **DSH local host only** on recall/search/export; no external host yet.
- Phase C (full local): enforce all listed local paths after shadow/canary evidence.
- Explicitly excluded: federation, family/public sharing, external host grants, identity/DNA mutation, network ingress,
  release-asset changes, autonomous evolution.
- First external host (Claude or Kilo) requires separate grant review and Director approval.

## 2. Migration steps
1. Freeze v4.0.1/M2 baseline; backup `state/index/agi.db`, `state/entelechy/state/agi.db`, runtime files; record SHA-256.
2. Deploy additive policy layer + host/grant schemas behind `AGI_M2_HOST_AUTH=off`; issue one local DSH host grant
   (Master-signed); do not modify DNA/identity.
3. Run boot gate 13/13, M1 40/40, remediation tests, prototype matrix in isolated copy.
4. Shadow mode: flag off, `AGI_M2_HOST_AUTH_MODE=shadow`; compare would-deny vs current; no enforcement.
5. Canary mode: enforce DSH local host for recall/search/export; verify positive/negative controls.
6. Full local enforce only after review of shadow/canary evidence + Director explicit approval.
7. No release asset change; no network.

## 3. Health indicators
- boot gate 13/13, conformance 25/25, M1 40/40, remediation 11/11, prototype 27/27.
- Deny/allow counts by reason; replay/revocation counters; forged/bad-proof counts.
- **Leak indicators must be zero:** cross-host private bodies, shared/private boundary, denied-search count/rank,
  export/snapshot/log/adapter private bodies.
- Audit chain valid (seq + prev_hash); no payloads/secrets in audit.
- Latency p95 and error rate vs baseline; flag/mode state; grants/hosts/revocation store availability.

## 4. Abort thresholds / kill switch
Immediate abort + rollback if any:
- unauthorized private/shared body leak, count/rank leak, audit-chain break, fail-open revocation, boot/conformance fail;
- error rate > 0.5% or p95 latency > 2x baseline for 5 minutes;
- missing/ambiguous auth returns data, or any enforcement bypass.
Kill switch: set `AGI_M2_HOST_AUTH=off`; restore backups; verify hashes, boot 13/13, M1 40/40; document incident.

## 5. Rollback procedure
1. Set flag off / stop enforcement.
2. Restore runtime + index backups; verify SHA-256 manifests.
3. Run boot gate, M1, remediation tests, prototype matrix.
4. Confirm no live data loss/no federation/identity change; report to Director/owner.
5. Keep evidence and incident audit.

## 6. Authorization gates
- Kilo independent review of this package and shadow/canary plan.
- Owner + Director explicit authorization before each enforcement stage.
- No federation/family/public sharing/identity mutation/autonomous evolution.
- v4.0.1 stable and M1 freeze preserved.

## 7. Acceptance checklist
- [ ] Kilo review of package complete.
- [ ] Backups + hashes recorded.
- [ ] Shadow mode evidence reviewed; no leak indicators.
- [ ] Canary positive/negative controls pass; abort thresholds green.
- [ ] Director explicit approval for each stage.
- [ ] Rollback tested on copy and ready.
