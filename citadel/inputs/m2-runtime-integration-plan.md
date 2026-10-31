# M2 runtime integration plan (for Director approval; runtime integration NOT enabled)

**Status:** plan only. M2 limited schema/classification apply is complete for 1,957 items; 10 docs untouched.
**Director decision:** `APPROVED_FOR_RUNTIME_INTEGRATION_EVIDENCE_REVIEW_ONLY` — submit isolated test evidence before
enabling runtime integration. No federation, family/public sharing, identity mutation, or autonomous evolution.

## Goal
Wire the M2 memory policy centrally into every read/export path behind a default-off feature flag; fail closed; prove
with isolated tests on a copy of the post-apply database before any live enablement.

## Integration points
| Path | Required behavior |
|---|---|
| `runtime/agi_runtime.recall()` | derive context from host authorization; filter FTS/vector candidates before top-k; deny if no context; audit denials |
| `tools/agi_index.py` search | SQL predicate + post-filter; no unfiltered candidates; public docs remain untouched/private until approval |
| `state/entelechy/runtime/agi_bridge.py` MCP `recall` | context from M1 host authorization; no context → deny; no private body in tool responses |
| export | only allowed items; redact sensitive/secret; no private bodies |
| snapshot | hashes/metadata only above caller visibility; no private body |
| logging/audit | ids/classes/outcomes only; never bodies, secrets, or private payloads |
| adapters | never receive private memory; only allowed shared/public material |
| entelechy_sync/adoption | never auto-promote private→shared; keep classes/visibility on refresh |

## Context + fail-closed rules
`ctx = {organism_id, host_instance_id, host_id, family_role, scopes, request_kind}` from M1 host authorization.
Default deny; family/public disabled; private same-host or Master; shared_authorized requires approved recipient +
approval id; sensitive/secret redacted unless Master. Missing/ambiguous authorization → no data + audit.

## Isolated test harness (no live enable)
1. Copy `state/index/agi.db` to a temp root (post-apply, 1,967 rows) + copy M1 host records.
2. Start a local **shadow policy server**/CLI wrapper (not the live bridge) exposing recall/search/export/snapshot/
   adapter read paths with context injection.
3. Run negative bypass matrix: private cross-host, family/public deny, shared wrong-host/no approval, FTS/vector
   top-k leak, MCP missing auth, export/snapshot/log redaction, adapter no-private, direct-SQL static check.
4. Run positive controls: same-host private recall, Master access, approved shared recall.
5. Run v4/M1 regression (boot 13/13, M1 40/40) and hash/row-count integrity.
6. Produce evidence JSON + logs; no live runtime modified.

## Rollout gate
- Feature flag `AGI_M2_POLICY=off` (default). Isolated tests PASS → Director reviews evidence → approval → shadow mode
  (log-only compare) → canary on live read paths with backup → full enable. Rollback: restore pre-integration DB/runtime
  hashes; feature flag off; no deletes.

## Deliverables for approval
- Policy module + tests; isolated harness evidence; enforcement matrix; audit-redaction evidence; v4/M1 regression;
  rollback evidence. No live runtime enablement until Director approval.
