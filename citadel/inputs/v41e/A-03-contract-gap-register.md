# A-03 — Contract gap register (AGI-OP-01..12)

**Status:** design requirements, not implemented. **No contract here is frozen or approved.**
**Purpose:** define what must be specified before an Operator prototype, and expose the gaps in the handoff's proposal.

Each contract lists: scope, owner, inputs/outputs, trust assumptions, failure behavior, security boundary, evidence, acceptance tests, S1–S6 traceability, and **gaps**. The traceability IDs are expanded in A-06.

---

## 1. Register summary

| ID | Contract | Primary owner | Blocking for prototype? | Gap severity |
|---|---|---|---|---|
| AGI-OP-01 | Service model | Operator architecture | Yes | High |
| AGI-OP-02 | Plugin lifecycle | Operator/plugin host | Yes | Critical |
| AGI-OP-03 | Event and policy model | Operator/policy | Yes | Critical |
| AGI-OP-04 | Control Protocol v0.1 | Control interface | Yes | Critical |
| AGI-OP-05 | Execution primitives | Operator/evidence | Yes | High |
| AGI-OP-06 | Approval and cancellation | Governance/Operator | Yes | Critical |
| AGI-OP-07 | Event durability and replay | Evidence/Operator | Yes | Critical |
| AGI-OP-08 | Security boundaries and threat model | Security/Owner | Yes | Critical |
| AGI-OP-09 | Baseline traceability | Architecture | Yes | High |
| AGI-OP-10 | Provider substitution | Operator/adapters | Yes | High |
| AGI-OP-11 | Recovery semantics | Operator/Station | Yes | Critical |
| AGI-OP-12 | Runtime profiles | Operator/governance | No (phase 2) | Medium |

**Rule:** a contract is not "done" until it has a schema/state machine, negative tests, an evidence artifact, and an S1–S6 mapping. Prose is not a contract.

## 2. AGI-OP-01 — Service model

- **Scope:** service definition/provider/consumer, injection, scoped resolution, lifecycle ownership, replacement.
- **Owner:** Operator architecture.
- **Inputs/outputs:** service interface schema; provider capability declaration; consumer dependency list; provider instance; disposal.
- **Trust:** providers are code, not authority; a service contract is not a grant.
- **Failure:** missing dependency → pending/failed, not silent fallback; provider loss → dependent unload/reload; no partial service.
- **Security boundary:** service resolution is not isolation; cross-Branch services are forbidden unless explicitly shared.
- **Evidence:** service graph snapshot, provider versions, degradation flags.
- **Tests:** injection order, missing dependency, provider swap with active consumer, duplicate provider, scoped shadowing, cross-scope isolation.
- **Traceability:** S1 T3; S5 §3/§4; S6 provenance.
- **Gaps:** no AGI service interface schema; no rule for *which* services may be replaced; no service-level authorization; no provider trust admission; no cross-Branch service policy; no versioning/compat rule.

## 3. AGI-OP-02 — Plugin lifecycle and cleanup

- **Scope:** phases, dependency tracking, partial startup, unload, failure, effect disposal, HMR.
- **Owner:** Operator/plugin host.
- **Inputs/outputs:** plugin manifest (id, version, deps, capabilities, permissions requested); load/unload events; phase; cleanup result.
- **Trust:** plugin code is untrusted; declared permissions are requests; admission is not approval.
- **Failure:** load failure → `failed`, no partial registrations; unload failure → quarantine + report; dependent unload ordering; crash during load → cleanup.
- **Security boundary:** plugin cannot mutate governance, identity, grants, evidence signing, sandbox policy; plugin runs with least privilege.
- **Evidence:** phase transitions, dependency graph, cleanup log, hash of plugin bundle.
- **Tests:** partial startup cleanup; provider removed with dependents; unload with active run; effect ordering; duplicate registration; HMR with live run; failed unload.
- **Traceability:** S5 §3/§7; S3 AT-S3-08/11; S6 E-level.
- **Gaps:** no explicit rule for **unload while a run is active**; no quiescence barrier; no cleanup ordering guarantee (Cordis async disposers may run concurrently); no plugin admission/trust model; no signed plugin manifest; no HMR-governance protection; no definition of "effect" that must be reversible.

## 4. AGI-OP-03 — Event and policy model

- **Scope:** dispatch modes, listener ordering, waterfall transforms, monotonic denial, audit.
- **Owner:** Operator/policy.
- **Inputs/outputs:** event schema; mode; listener registration; decision (allow/deny/cancel/ask); audit event.
- **Trust:** ordinary event hooks are **not** authorization gates; only the designated S3 policy gate is.
- **Failure:** listener throws → contained; deny cannot be reversed; policy gate unavailable → deny; audit write failure → deny.
- **Security boundary:** monotonic denial; no plugin can force-allow; policy gate runs outside plugin code.
- **Evidence:** decision record, deny reason, audit chain, listener version.
- **Tests:** later listener tries to reverse deny; hook bypass attempt; policy gate unavailable; audit failure; waterfall transform; scoped listener leak; event replay.
- **Traceability:** S3 AT-S3-01..15; S5 §3; S6 provenance.
- **Gaps:** normative mode set (live: emit/serial/parallel/waterfall; `bail` unverified); no event schema/version; no ordering contract across modes; no rule for which hooks may transform vs veto; no guard-vs-policy precedence; no audit of listener identity.

## 5. AGI-OP-04 — Operator Control Protocol v0.1

- **Scope:** transport, framing, init, methods/notifications, correlation, errors, backpressure, versioning, schema.
- **Owner:** Control interface.
- **Inputs/outputs:** JSON-RPC-like request/notification schema; capability declaration; response/error; event stream; shutdown.
- **Trust:** clients untrusted; initialization required; capability declaration is not a grant; approval is not consent.
- **Failure:** pre-init request → error; unknown method → error; overload → retryable error; malformed → close/deny; version mismatch → refuse.
- **Security boundary:** loopback/stdio only in phase 1; no remote authorities; no credential in protocol; no authority fields.
- **Evidence:** connection log, init record, protocol version, request/response digests.
- **Tests:** pre-init, duplicate init, unknown method, malformed JSON, out-of-order, overload, shutdown, reconnect, schema downgrade, experimental field without opt-in.
- **Traceability:** S1 T2/T3; S3; S5; S6.
- **Gaps:** exact method set; transport scope (stdio only?); version negotiation; error code taxonomy; retry/idempotency; event sequence/cursor; schema generation/pinning; client identity vs authority; graceful shutdown admission.

## 6. AGI-OP-05 — Execution primitives and identifiers

- **Scope:** branch/run/turn/item/lease identifiers; ordering; checkpoints; correlation.
- **Owner:** Operator/evidence.
- **Inputs/outputs:** identifier schema; creation/close rules; correlation refs; checkpoint.
- **Trust:** identifiers are references, not identity or authority.
- **Failure:** unknown/duplicate id → deny; id reuse → reject; orphaned run → recover/abort; clock skew → sequence not wall clock.
- **Security boundary:** no identifier aliases a passport/root/grant; cross-Branch correlation forbidden without consent.
- **Evidence:** run manifest, item timeline, checkpoint digest.
- **Tests:** id collision, out-of-order item, turn close without item, run resume, cross-Branch correlation, thread/run confusion.
- **Traceability:** S1 T4/T7; S5; S6.
- **Gaps:** mapping from Codex thread/sessionId to AGI run/turn; no definition of run vs turn vs item boundaries; no checkpoint content; no ordering across concurrent runs; no retention.

## 7. AGI-OP-06 — Approval and cancellation

- **Scope:** approval request/decision/resolved; Owner consent projection; cancellation stages; cleanup barrier.
- **Owner:** Governance/Operator.
- **Inputs/outputs:** approval request (run/turn/item, reason, scope); decision (allow-once/reject/cancel/unavailable); consent ref (optional); cancellation request; final status.
- **Trust:** client approval ≠ Owner consent ≠ S3 authorization; approval is one input to a governed decision.
- **Failure:** timeout → unavailable (fail closed); disconnect → cancel/pending replay; cancellation ack ≠ stopped; cleanup failure → incident.
- **Security boundary:** approval bridge cannot mint grants; Owner decision is a durable record; no approval scope escalation.
- **Evidence:** ask/outcome pair, decision ref, cancellation stage log, quiescence proof.
- **Tests:** stale approval, forged approval, approval timeout, cancel during tool, cleanup barrier, cancel after effect, reconnect with pending approval, scope escalation.
- **Traceability:** S2 AT-S2-13; S3 AT-S3-01/10; S5 AT-S5-03/09; DNA I9.
- **Gaps:** no AGI approval state machine; no Owner-consent projection; no timeout values; no pending-approval replay across restart; no effect ledger; no quiescence proof; no rule for `acceptForSession` (must not exist in AGI).

## 8. AGI-OP-07 — Event durability, journal, replay

- **Scope:** append-only journal, sequence, cursor, replay, reconnect, idempotency, retention, evidence linkage.
- **Owner:** Evidence/Operator.
- **Inputs/outputs:** event record; seq; digest; checkpoint; cursor; evidence ref.
- **Trust:** live event stream is not evidence; journal is operational; evidence is hash-anchored/signed.
- **Failure:** torn tail → truncate/refuse; unknown event → fail closed; gap → refuse; replay duplicate → idempotent; corruption → recovery.
- **Security boundary:** journal is branch-scoped; no cross-Branch read; no secrets/private bodies; evidence separate.
- **Evidence:** journal manifest, checkpoint, evidence packet, replay report.
- **Tests:** crash mid-run, torn tail, replay, duplicate, gap, reconnect, evidence reconstruction, retention, tamper.
- **Traceability:** S1 T1/T4/T5; S5 §3; S6 AT-S6-03/13.
- **Gaps:** no cursor/ack contract; no fsync/durability point; no idempotency key; no retention policy; no evidence-vs-journal separation schema; no replay determinism requirement; no cross-host continuity.

## 9. AGI-OP-08 — Security boundaries and threat model

- **Scope:** TCB, plugin/model/client/station boundaries, supply chain, prompt injection, cross-Branch, network, credentials.
- **Owner:** Security/Owner.
- **Inputs/outputs:** trust boundary doc; threat model; mitigations; tests.
- **Trust:** only governance/evidence/sandbox/control parser are TCB; everything else untrusted.
- **Failure:** any boundary failure → fail closed, audit, no effect.
- **Security boundary:** as A-02 §3.
- **Evidence:** threat-model version, test evidence, residual risk accepted by Owner.
- **Tests:** A-07.
- **Traceability:** S1 T3/T6; S2 AT-S2-11; S3; S5; S6.
- **Gaps:** no plugin sandbox design; no prompt-injection model for skill/tool content; no supply-chain verification for plugins/providers; no network egress policy; no credential custody; no cross-Branch isolation test; no threat model acceptance.

## 10. AGI-OP-09 — Baseline traceability

- **Scope:** S1–S6 mapping for every contract/test; change control; evidence.
- **Owner:** Architecture.
- **Inputs/outputs:** matrix; acceptance criteria; revision refs.
- **Trust:** traceability is evidence, not proof.
- **Failure:** unmapped requirement → block; changed baseline → new revision; missing test → block.
- **Security boundary:** no contract may claim a baseline guarantee it does not implement.
- **Evidence:** matrix + hashes.
- **Tests:** audit that every contract has S1–S6 refs and every high-risk requirement has a test.
- **Traceability:** S1–S6.
- **Gaps:** A-06 is a first draft; no automated check; no change-control gate; no mapping for provider adapters or profiles yet.

## 11. AGI-OP-10 — Provider substitution

- **Scope:** model/tool/storage provider adapters; capability probe; degraded mode; substitution disclosure.
- **Owner:** Operator/adapters.
- **Inputs/outputs:** provider manifest; capabilities; endpoint ref; probe result; degradation; evidence.
- **Trust:** provider is external/untrusted; advertised capability is a claim; no provider name in core.
- **Failure:** unavailable → degraded/refuse; capability mismatch → explicit degrade; silent substitution → defect.
- **Security boundary:** endpoint authorization, network guard, numeric caps, no credentials in logs.
- **Evidence:** probe result, model/version, substitution event, E-level.
- **Tests:** provider swap, missing capability, model substitution, endpoint deny, cost cap, fallback, stale capability.
- **Traceability:** S5 AT-S5-01/10/13; S1 T2; S4/S6.
- **Gaps:** no AGI adapter contract; no parity definition; no substitution audit; no endpoint authorization integration; no cost metering; no offline mock contract.

## 12. AGI-OP-11 — Recovery semantics

- **Scope:** crash detection, journal recovery, checkpoint rollback, effect reconciliation, cleanup barrier, resume.
- **Owner:** Operator/Station.
- **Inputs/outputs:** last checkpoint; journal; effect ledger; lease/epoch; recovery report.
- **Trust:** a restarted process is not automatically the same Operator; lease/fencing required.
- **Failure:** stale lease → deny; unrecorded effect → incident; digest mismatch → refuse; partial recovery → degraded, not silent success.
- **Security boundary:** no split-brain; no rollback of emitted effects without reconciliation; no authority change.
- **Evidence:** recovery report, effect ledger, digest, lease ref.
- **Tests:** crash mid-tool, crash mid-handoff, stale epoch, duplicate effect, torn journal, resume on new Station, cleanup timeout.
- **Traceability:** S1 T4/T7; S5 addendum 02; S6.
- **Gaps:** no effect ledger contract; no quiescence proof; no recovery state machine; no handoff integration; no idempotency boundary.

## 13. AGI-OP-12 — Runtime profiles

- **Scope:** ordered composition, protected governance rows, defaults, validation.
- **Owner:** Operator/governance.
- **Inputs/outputs:** profile manifest; patch layers; protected rows; resolved composition hash.
- **Trust:** profile author is not authority; profile cannot alter governance.
- **Failure:** profile attempts protected change → refuse; dependency missing → pending/failed; unknown plugin → refuse.
- **Security boundary:** governance rows are non-overridable; default deny; profiles are signed/hashed.
- **Evidence:** resolved composition, patch hashes, protected-row check.
- **Tests:** protected row tamper, profile overlay, disabled governance, unknown plugin, default drift, restore.
- **Traceability:** S1 T3; S3; S5; S6.
- **Gaps:** no profile schema; no protected-row list; no signature; no default policy; no rollback.

## 14. Cross-contract gaps (must be closed before prototype)

1. **Authority is still only referenced, not wired** — every contract says "calls S3", but no contract defines the exact `boundary_decision` request/response mapping and audit record. **[Critical]**
2. **Evidence is undefined** — no packet schema, no E-level rule, no hash/signature binding across journal/approval/execution. **[Critical]**
3. **Plugin trust is undefined** — install ≠ approve; no admission pipeline, no sandbox profile, no code review. **[Critical]**
4. **Provider substitution has no parity test** — "same contract set" is not measurable. **[High]**
5. **Cancellation has no quiescence proof** — an interrupt acknowledgement is not a stopped tool/subprocess. **[Critical]**
6. **Control protocol has no version/compat policy** — experimental fields, schema drift, client mismatch. **[High]**
7. **No Owner decision projection** — approval bridge needs an I9 card/durable record, not just a UI accept. **[Critical]**
8. **No cross-Branch isolation contract** — context, journal, evidence, service graph all need branch scope. **[High]**
9. **No test harness spec** — offline mocks, deterministic fixtures, network guard, fault injection. **[High]**
10. **No change-control rule** — what forces a baseline revision vs an implementation change. **[High]**

## 15. Non-authorization

This register is design analysis only. It does not authorize implementation, installation, endpoint contact, credentials, federation, identity mutation, capability activation, or any frozen-baseline change.
