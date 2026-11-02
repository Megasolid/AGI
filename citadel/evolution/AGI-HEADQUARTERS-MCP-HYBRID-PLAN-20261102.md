# AGI Headquarters MCP — Hybrid Implementation and Deployment Plan

**Date:** 2026-11-02  
**Status:** Design plan; not implemented, deployed, connected, or activated.  
**Branch:** `evolution/emergency-dsh-succession-20261102`  
**Repository base:** emergency DSH succession branch  
**Hosting decision:** Hybrid — local development/approval station plus persistent cloud coordination service.

## 1. Decision and operating model

Build one AGI-owned Headquarters service with two deployment profiles:

- **Local station:** private development workspace, repository checkout, test execution, local evidence generation, operator journal, and human approval interaction.
- **Cloud headquarters:** persistent task queue, handoff/context metadata, station registry, signed event/evidence references, model-provider routing metadata, and health/recovery coordination.
- **Authenticated bridge:** narrow RPC/MCP boundary between cloud and local station. The local station initiates outbound connectivity where practical. The cloud service never receives unrestricted filesystem, shell, repository-admin, signing-key, or desktop-control access.

ChatGPT/GPT, DSH, Kilo, and future models are replaceable clients/workers. They do not own AGI state, station identity, credentials, policy, or release authority. A client decision or semantic COMMIT is not execution authorization.

## 2. Existing repository foundations and gaps

Reuse and extend rather than duplicate:

- `runtime/agi_handoff.py`: E4 bounded handoff and receipt primitives; permissions are declarations, not grants; context references are resolved separately.
- `runtime/agi_operator.py`: provider lifecycle, monotonic-deny PolicyGate, cancellation controller, single-writer lease/epoch, and approval-request bridge.
- `runtime/agi_operator_journal.py`: append-only, sequence-numbered, hash-chained journal with fsync and event idempotency.
- `runtime/agi_tunnel.py`: tunnel readiness/planning only; it does not open ingress. Existing security notes require loopback binding, bearer-token scopes, access policy, local-only approval, token rotation, and remote-call logging.
- `runtime/agi_context.py` and `runtime/agi_context_adapter.py`: context resolution/adaptation; do not represent the injected adapter as a live S5 gateway or revocation service.
- `runtime/agi_policy.py`: beta policy file for remote passport issuance; do not treat it as a complete Headquarters policy engine.

Known gaps to resolve before deployment:
1. No verified, production-ready Headquarters MCP server implementation was identified in the reviewed files.
2. Existing lease/journal primitives are in-process/local abstractions; cloud multi-instance coordination needs durable transactional storage and atomic compare-and-swap/fencing.
3. No real S5 gateway or live revocation service is established by this plan.
4. The tunnel helper only reports readiness and prints a plan; a human must configure and operate ingress.
5. ChatGPT account/plan support for the required custom MCP capabilities must be tested in the actual account before making this a dependency.

## 3. Trust boundaries

### Local station may
- Read the approved local AGI checkout and designated working directories.
- Run allowlisted tests and static checks in a sandbox.
- Create patches only on explicitly authorized feature branches.
- Produce checkpoints, handoffs, test logs, and evidence digests.
- Receive cloud task envelopes and return signed/hash-addressed receipts.

### Cloud headquarters may
- Persist task metadata, station heartbeat/lease metadata, handoff references, and event/evidence digests.
- Route bounded tasks to registered stations and model providers.
- Return only context references authorized for that station and task.
- Record task state transitions and surface pending Owner decisions.

### Cloud headquarters must not
- Expose arbitrary local file reads/writes, shell execution, desktop control, or unrestricted Git operations.
- Hold production signing keys, personal secrets, raw credentials, or unrestricted private conversation archives.
- Approve its own requests, grant capabilities, modify S1–S6, merge protected branches, tag, publish, activate, or enable federation/live execution.
- Treat a model response, tool result, approval request, or semantic COMMIT as an authorization grant.

### Owner-only actions
Protected merge, identity/trust-root/consent/authority changes, production signing policy, release tagging/publication/activation, live federation, and external execution remain outside model and remote-client authority. Approval must be explicit, scoped, attributable, time-bounded where applicable, and checked at the local write/execution chokepoint.

## 4. Service topology

```text
Owner / KING
    | explicit decisions
    v
ChatGPT UI ---- MCP client ---- Cloud Headquarters API
                                  | task queue / metadata DB
                                  | append-only event records
                                  | context-reference catalog
                                  | station registry + lease epochs
                                  |
                           authenticated bridge
                                  |
                         Local AGI station agent
                                  |
                      policy gate + local journal
                                  |
                 isolated AGI checkout / test sandbox
                                  |
                    branch patches + evidence bundles
```

Deployment profiles:
- Cloud: one logical Headquarters API, managed persistent database, encrypted object storage for non-secret evidence, backups, monitoring, and restricted operator access.
- Local: one station agent and workspace, durable local journal/checkpoints, outbound authenticated connection to cloud, and local approval UI/CLI.
- Development: docker-compose or equivalent local-only profile for API + database + test station; no public ingress and no production credentials.

Avoid split-brain: one active writer per branch/workspace. Every consequential write carries station ID, branch ID, lease epoch, task ID, and idempotency key. Stale epochs are rejected at the local write boundary, not merely at the cloud API.

## 5. Initial MCP tool contract

Start read-only and metadata-only. Tool names are provisional; publish only after schema review.

| Tool | Initial behavior | Risk |
|---|---|---|
| `agi_status` | Return service/station health, branch heads, queue counts, policy version, and known blockers | Read-only |
| `agi_task_list` | List tasks visible to the caller's station and scope | Read-only |
| `agi_task_get` | Fetch one task envelope and its digest | Read-only |
| `agi_context_resolve` | Resolve explicitly authorized context references; return provenance and digest | Read-only, classified |
| `agi_handoff_submit` | Submit a bounded E4 handoff; validate schema, digest, expiry, and scope | Metadata write |
| `agi_checkpoint_create` | Record a checkpoint reference and digest; never upload secrets | Metadata write |
| `agi_receipt_submit` | Submit completion/recovery receipt tied to handoff digest | Metadata write |
| `agi_evidence_get` | Retrieve authorized evidence metadata or approved artifact | Read-only, classified |
| `agi_approval_request` | Create a pending request for a human decision; cannot approve | Request only |

Do not expose general-purpose `run_shell`, `read_file(path)`, `write_file(path)`, `git_push`, `merge`, `release`, `sign`, or `approve` tools in the initial server. If later required, expose narrow task-specific operations with local policy enforcement and separate Owner authorization.

Every tool call must authenticate the client, authorize tool + resource + task scope, validate input schema/size, enforce rate limits, append an audit event, and return a correlation ID. Fail closed on missing identity, policy, lease, context provenance, or storage availability.

## 6. Data and persistence model

Minimum logical records:
- `Station`: station_id, station_type, software_version, public_key_id, status, last_seen, capabilities (descriptive only).
- `Task`: task_id, schema_version, owner, branch_id, objective, constraints, acceptance criteria, evidence requirements, state, expiry, handoff_digest.
- `ContextRef`: context_id, content_digest, source/provenance, classification, allowed_station/task scope, expiry, revocation status. Store content separately under the applicable access policy.
- `Lease`: branch_id, station_id, monotonic_epoch, expires_at, released_at; update transactionally.
- `Event`: event_id, sequence, event_type, task_id, station_id, timestamp, payload_digest, previous_digest, digest.
- `Checkpoint`: checkpoint_id, task_id, branch/head, journal cursor, context manifest digest, artifact references, created_at.
- `Receipt`: task_id, handoff_digest, outcome, constraints_met, evidence_refs, residual_risks, receipt_digest.
- `ApprovalRequest`: request_id, operation, scope, requester, expiry, status; a request is not a grant.

Use a transactional relational database for cloud coordination state. Use append-only event records and content-addressed artifact storage for evidence. Local station keeps a durable journal and atomic checkpoint files. Backups must be encrypted, tested by restore drills, and retain provenance. Do not store secrets in task payloads or evidence bundles.

## 7. Security requirements before any remote write

1. TLS for all remote transport; private service-to-service identity; short-lived scoped tokens or mutually authenticated station credentials.
2. Separate credentials by environment and station; least privilege; rotation and revocation procedure.
3. Cloud Access policy or private network ACL in front of ingress. No unauthenticated public quick tunnel.
4. Local bridge remains loopback-bound; remote calls are forwarded only through an authenticated, scope-checking bridge.
5. Human approval stays local and cannot be called remotely as an approval action.
6. Validate handoff/context/evidence schemas and digests; reject expired, revoked, mismatched, or out-of-scope references.
7. Enforce station lease epochs at the actual local write chokepoint; stale or duplicate requests are rejected.
8. Idempotency keys for every state-changing request; replay must not duplicate effects.
9. Redact secrets from logs; log actor, station, task, tool, scope, decision, correlation ID, and result digest.
10. Dependency pinning, SBOM, vulnerability scanning, signed build artifacts, backup/restore test, and incident/credential-rotation runbook.
11. No production signing key in cloud or model context. The existing pure-Python ML-DSA implementation remains offline verification-only.
12. Preserve frozen S1–S6 byte-for-byte and keep v4.1-E additive and shadow-mode until separately authorized.

## 8. Implementation phases and acceptance gates

### H0 — Contract and threat-model freeze
Deliver: MCP tool schemas, threat model, data classification map, trust-boundary diagram, and tool-to-policy matrix.
Pass: every tool has an owner, scope, input/output schema, audit event, failure mode, and explicit forbidden operations. Independent review before coding remote writes.

### H1 — Local-only vertical slice
Implement: MCP server process bound to loopback; read-only `agi_status`, `agi_task_list`, `agi_task_get`; adapter over existing handoff/journal primitives.
Pass: unit/schema tests; no network ingress; malformed/oversized inputs rejected; no filesystem path supplied by caller; journal corruption detected; restart restores state.

### H2 — Local durable workflow
Implement: task submission, checkpoint metadata, receipts, idempotency, cancellation, and local lease fencing. Writes restricted to a disposable feature branch and allowlisted workspace.
Pass: kill/restart/replay tests; duplicate request produces one effect; stale epoch denied; failed policy/storage denies write; handoff reconstructs task without original model transcript.

### H3 — Cloud coordination shadow mode
Implement: cloud API + database + station registry + task metadata replication. Local station initiates outbound authenticated connection; cloud cannot issue arbitrary local commands.
Pass: cloud outage does not corrupt local state; reconnect reconciles by event cursor/digest; duplicate/out-of-order messages are rejected or safely reconciled; no protected operation exposed.

### H4 — Authenticated hybrid pilot
Implement: named tunnel/private access policy, scoped station credentials, remote read-only MCP tools, monitoring, backups, and credential rotation drill.
Pass: external security review; unauthorized station denied; token revocation effective; no local approval endpoint reachable; penetration tests for authz bypass, replay, SSRF, path traversal, and oversized payloads.

### H5 — Narrow remote writes
Only after H4 passes: allow handoff/receipt/checkpoint metadata writes, never arbitrary repository or shell operations. Local station independently revalidates policy and lease before accepting.
Pass: adversarial tests, idempotency/fencing tests, independent Kilo review, Owner approval for pilot. Keep branch writes local and feature-scoped.

### H6 — Headquarters succession acceptance
Run a clean-room drill: DSH produces signed/hash-addressed handoff; local station and a second model reconstruct tasks; cloud coordination recovers after restart; evidence is reproduced; Kilo independently reviews; Owner accepts transition.
Pass: no dependence on DSH transcript, no missing constraints, no duplicate effects, full recovery evidence, S1–S6 unchanged, rollback demonstrated.

## 9. Deployment plan

### Local development
- Python environment with pinned dependencies and lockfile.
- Local database/container profile; bind MCP listener to `127.0.0.1` only.
- Dedicated unprivileged OS account; workspace allowlist; no home-directory-wide access.
- Test fixtures and synthetic credentials only.
- Start with read-only tools; write operations disabled by default.
- Run test suite and integrity checks before every station build.

### Cloud staging
- Separate staging account/project and database; no production secrets.
- Deploy API behind authenticated access proxy; private object storage; encrypted backups.
- Restrict administrative access; enable structured audit logs and alerting.
- Connect one disposable local station using a staging-only identity.
- Run H3/H4 acceptance suite before any production consideration.

### Production candidate
- Promote immutable, reviewed build artifact only after H4/H5 and Owner authorization.
- Separate production credentials from staging; documented rotation/revocation and restore drill.
- Roll out read-only first, then metadata writes; immediate rollback to local-only mode.
- No release tag, publication, activation, federation, or live execution is implied by this plan.

### Operational commands (illustrative; adapt to the implemented package)
- Local tests: `python -m unittest discover -s runtime -p 'test_*.py'`
- Tunnel readiness only: `python runtime/agi_tunnel.py --check`
- Review tunnel plan only: `python runtime/agi_tunnel.py --plan --port 8766`
These commands do not deploy, open a tunnel, or authorize remote access.

## 10. Observability, recovery, and rollback

Track: service health, station heartbeats, queue age, task state transitions, handoff validation failures, context digest failures, lease conflicts, idempotency hits, journal head/cursor, backup age, authz denials, and credential expiry.

Recovery procedure:
1. Stop remote writes and revoke affected station credentials if compromise is suspected.
2. Preserve local journal, cloud event log, checkpoints, and relevant audit records.
3. Verify hash chains, task/handoff digests, branch HEADs, and lease epochs.
4. Restore cloud metadata from a tested backup; replay only verified idempotent events.
5. Reconcile local/cloud cursors; never infer success from a missing response.
6. Resume in read-only mode; require Owner approval before re-enabling metadata writes.

Rollback: disable remote MCP exposure, revoke cloud/station tokens, stop tunnel, retain local-only operation and evidence. Never delete evidence to make a failed deployment appear clean.

## 11. Immediate work queue

| Priority | Task | Exit evidence |
|---|---|---|
| P0 | DSH continuity handoff and runway snapshot | Validated handoff digest + task queue |
| P0 | H0 MCP contract, threat model, classification, policy matrix | Reviewed schemas and threat model |
| P0 | Inventory current beta bridge/MCP implementation and tests | File-level inventory; reuse/replace decision |
| P0 | H1 local read-only MCP vertical slice | Test report and loopback binding proof |
| P0 | Clean-room resume from handoff | Reconstructed task and replay report |
| P1 | Durable local checkpoints and fencing integration | Restart, duplicate, stale-epoch tests |
| P1 | Cloud coordination shadow mode | Reconciliation and outage test report |
| P1 | Security review and authenticated hybrid pilot | Independent findings + remediation |
| P2 | Narrow metadata writes and model-provider adapters | Scope and compatibility evidence |

## 12. Non-claims and release status

This document is a plan, not implementation evidence. No MCP server has been created or deployed by this commit. No custom plugin has been installed or connected. No tunnel or cloud endpoint has been opened. No credentials have been issued. No real S5/revocation integration is claimed. No tests are claimed as run by this plan.

Publication remains BLOCKED; tagging remains OWNER_APPROVAL_REQUIRED; activation remains NOT_AUTHORIZED unless Owner D separately changes those decisions through the established governance process.

**North Star:** the Headquarters owns durable coordination and verified continuity; local AGI stations enforce policy at the point of effect; models remain replaceable workers.
