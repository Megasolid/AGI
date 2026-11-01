# A-01 — Independent architecture assessment: Cordis and Codex App Server as AGI references

**Status:** assessment and design recommendation only. No implementation, no baseline change, no endpoint contact, no credentials, no package installation.
**Date:** 2026-11-02 (Asia/Tehran).
**Inputs:** AGI → DSH technical handoff (2026-11-02, untrusted); live DSH/Cordis Host inspection on this machine; Cordis 4.0.5 package and docs; OpenAI Codex App Server public documentation (commit `d9f6b7f`, plus current `main`).
**Controlling governance:** frozen S1–S6, DNA v4, and the DSH SSL/ACS review (`../dsh-review-ssl-acs-20261102.md`) and design package (`../design-sem-acx-v0.2-20261102/`).

---

## 1. Verdict

**Both are useful references; neither is an AGI dependency or an authority source.**

- **Cordis** is a strong model for **how the Operator is composed internally**: service definition/provider/consumer separation, dependency injection, fiber-scoped lifecycle, reversible effects, typed event modes, monotonic tool guards, loader/profile composition, and a durable session log distinct from live events.
- **Codex App Server** is a strong model for **how the Operator is controlled externally**: a long-lived bidirectional JSON-RPC server, initialization before operations, thread/turn/item identity, typed item lifecycles, server-initiated approval requests, interruption, bounded queues with an overload error, schema generation, and explicit experimental-API opt-in.
- **AGI governance** must remain the third, independent layer: identity, consent, grants, revocation, leases/fencing, evidence, and Station execution. Neither reference supplies these.

Recommended one-line separation:

> **Cordis informs composition. Codex App Server informs control. AGI governance decides what is permitted.**

**No frozen S1–S6 change is required by this assessment.** Everything recommended here can be specified as new Operator contracts and a shadow prototype; anything that would change a frozen carrier is listed as a stop condition (§ A-08).

## 2. Evidence classification used in this package

| Tag | Meaning | Example |
|---|---|---|
| **[V]** | **Directly verified** by live inspection or reading installed code/docs on this host | `tools.guard` monotonic denial; `PluginFiberPhase` enum; `sessionPersistence` append-only semantics |
| **[D]** | **Documentation-supported** by the reference project's own docs | Cordis `inject`/fiber disposal; Codex JSON-RPC/stdio/thread/turn/item |
| **[I]** | **Architectural inference** from verified facts, not a direct feature claim | "Context scope is not OS isolation" |
| **[P]** | **Proposed AGI design** (not implemented anywhere) | Operator Control Protocol v0.1, AGI governance layer |
| **[U]** | **Unverified assumption** or handoff claim not confirmed | Codex Unix-socket transport; Cordis `bail` mode in this deployment |

A claim without a tag is a synthesis statement and must be treated as [I]/[P].

## 3. Cordis: what was actually verified

**Version and packaging.** The installed framework is `@deepseek-ai/cordis` **4.0.5** (package.json, read 2026-11-02), MIT, ESM, plugin framework with optional loader/include packages. **[V]**

**Live composition.** The running Host exposes 216 loader entries (`plugin_manager list_plugins`, 2026-11-02), with `fiberPhase` values `active` or `null`; disabled entries show `enabled:false` and `fiberPhase:null`. The declared type is exactly `pending | loading | active | failed | unloading | null` (`PluginFiberPhase`). **[V]** This corrects the handoff's "PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED": there is **no `disposed` phase** in the live type; removal/disabled is `null`, and the loader entry disappears from the active set.

**Service model.** `ctx.<service>` services with explicit method contracts are visible through the Host `Service` provider: `tools`, `approval`, `sessions`, `sessionPersistence`, `pluginManager`, `connection`, `agentLoop`, `agents`, `systemPrompt`, `subagents`, etc. **[V]** Services are replaceable at the contract level: e.g. `fs`, `storage`, `subprocess`, `speechToText`, `plugins` are abstract/registry services. **[V]**

**Dependency injection and scoping.** The composition reference documents `inject`, `isolate`, `intercept`, groups, and per-profile patch layers; scoped registrations shadow globals; a service can be isolated to a realm. **[D]** The live `tools` service confirms scoped registration and scope-filtered event dispatch (`@deepseek-ai/dsh-scope`), with scoped tools shadowing global ones. **[V]**

**Plugin lifecycle and cleanup.** `ctx.plugin()` returns a `Fiber`; effects, listeners and services are removed when the owning fiber is disposed (Cordis README). **[D]** The loader tracks `pending/loading/active/failed/unloading/null`. **[V]** The live `agent/disposed` event fires "after driver quiescence and scoped-registration unwind, but before session detachment" — an explicit quiescence-before-cleanup ordering. **[V]** The handoff's warning about asynchronous disposers running concurrently is consistent with fiber-scoped cleanup; it is not directly measured here. **[D]/[U]**

**Event modes.** The live Host event catalog uses exactly four modes: `emit`, `serial`, `parallel`, `waterfall`. **[V]** Waterfall events can transform or veto (e.g. `tools/pre-execute`, `approval/request`, `system-prompt/assemble`); serial events are ordered awaited (`agent/created`); parallel events are concurrent awaited (`session/flush`); emit is fire-and-forget (`session/event`). **[V]** The handoff's `bail` mode is **not present in the live catalog**; treat it as unverified/optional until a concrete need and a verified implementation exist. **[U]**

**Monotonic denial.** `tools.guard` is registered **after** the extensible `tools/pre-execute` waterfall; it is synchronous, any matching guard may deny, and **no guard can force-allow a call another guard denied**, with an exact disposer for ordered ownership/HMR cleanup. **[V]** This is direct evidence that the handoff's "monotonic tool guard" pattern is real in this deployment. **[V]**

**Tool execution pipeline and cancellation.** `tools.execute` runs pre-policy, guards, around-dispatch, post-policy, content finalization, and final notification. Cancellation after entry but before result materialization either skips a not-yet-started body (`ABORTED_BEFORE_DISPATCH`) or replaces a successful started outcome with `ABORTED`; already-started work is still drained and may retain a tool-owned structured error. **[V]** This is more precise than the handoff's generic cancellation discussion and is directly relevant to AGI's cleanup barrier.

**Approval service.** `approval.request` applies session policy **before** answerers, logs every ask/outcome pair to the requesting session's durable log, requires an open turn, and returns a closed outcome: `allowed-once | rejected | cancelled | unavailable`; a missing/throwing answerer yields `unavailable` (fail closed); `allowed-once` is the only grant. **[V]** This is an excellent pattern for AGI's approval bridge — but it is **not** an S2 consent record or an S3 `boundary_decision`.

**Session and durability model.** `sessions` is an in-memory store; persistence is attached by the agent lifecycle, not by the store. `sessionPersistence` is append-only, contiguous from seq 0, never rewrites, truncates a torn physical tail before first append, refuses unknown vocabulary fail-closed, and exposes `flush` as the durability barrier. **[V]** `session/event` is post-commit fire-and-forget; `session/flush` is an awaited parallel durability checkpoint. **[V]** This directly supports the handoff's distinction between operational events, durable continuity, and tamper-evident evidence — and shows the mechanism to copy.

**Connection/control substrate.** `connection` exposes a transport-independent RPC channel registry, exact fetch routes, peer admission with a single `owner` principal kind, loopback authority gating (`allowsRemoteAuthorities` true only for a validated non-loopback trusted host), and `createPeer` with `interactions: 'answer' | 'none'`. **[V]** This is relevant prior art for the Control Interface: DSH already separates transport, peer, and principal.

**What Cordis does not supply for AGI.** Identity, consent, grants/revocation, branch continuity, evidence signing, station leases/fencing, sandbox execution, and human decision cards. **[I]** Context/service isolation is a **logical resolution boundary**, not an OS/process security boundary; the handoff is right to say so. **[I]**

## 4. Codex App Server: what the documentation supports

**Protocol and transport.** Bidirectional **JSON-RPC 2.0** messages (the `jsonrpc` header is omitted on the wire); default **stdio** with newline-delimited JSON (JSONL); **WebSocket** is experimental/unsupported; `unix://` is **WebSocket-over-Unix-socket with HTTP Upgrade**, not raw JSONL; `off` disables the local transport. The WS listener also serves `/readyz` and `/healthz` (requests carrying `Origin` are rejected 403), and WS auth modes are enforced before `initialize`. **[D]** The handoff's "Unix socket transport" is **confirmed with the protocol nuance** that it is WS-over-UDS. In-process/embedded app-server and outbound remote-control transports are also present but were not mentioned in the handoff. **[D]**

**Backpressure.** Bounded queues between transport ingress, request processing, and outbound writes; ingress saturation returns JSON-RPC error **-32001** `"Server overloaded; retry later."`; clients should retry with exponential backoff and jitter. **[D]** The official docs scope the explicit wording to WebSocket, while the inspected source uses a fixed `CHANNEL_CAPACITY = 128` bounded channel and the same overload code for stdio as well; there is no documented maximum-retry count, deadline, or retry-idempotency contract. **[D]/[U]**

**Initialization.** One `initialize` request per connection with `clientInfo` and optional `capabilities` (including `experimentalApi`, `optOutNotificationMethods`, and others), then an `initialized` notification; any other request before handshake is rejected; repeated initialize is rejected. This is **client capability declaration plus server-side gating**, not symmetric negotiation, and `experimentalApi` is fixed for the process lifetime. **[D]**

**Core primitives.** **Thread** (durable conversation), **Turn** (unit of work), **Item** (typed user input, reasoning, message, command, file edit, tool call, approval request, diff). Item lifecycle: `item/started` → zero or more item-specific deltas → `item/completed`; turn lifecycle: `turn/started` → `turn/completed`; `thread/started`. **[D]** Internal components (stdio reader, message processor, thread manager, per-thread core thread) are **source-level facts**, not an official documented contract: `message_processor.rs`, `app-server-transport/src/transport/stdio.rs`, `core/src/thread_manager.rs` at commit `cb1bc0a` (2026-11-01). **[D]/[V-source]**

**Thread operations.** `thread/start`, `thread/resume`, `thread/fork` (ephemeral option), `thread/read`, `thread/list`, `thread/archive`, `thread/unsubscribe`, `thread/name/set`, `thread/compact/start`, `thread/shellCommand`, `thread/rollback` (older docs; current docs say removed in favor of `thread/revert`), `thread/status/changed`, `thread/closed`. **[D]**

**Turn operations.** `turn/start`, `turn/steer` (add input to an in-flight turn), `turn/interrupt` (cancellation; turn ends `status:"interrupted"`). **[D]**

**Approvals.** The server sends a server-initiated JSON-RPC **request** to the client (e.g. `item/commandExecution/requestApproval`, `item/fileChange/requestApproval`, `item/permissions/requestApproval`); the turn pauses; client responds with a decision (`accept`, `acceptForSession`, `decline`, `cancel`, plus experimental variants); `serverRequest/resolved` confirms resolution; `item/completed` is the authoritative result. **[D]**

**Durability and reconnect.** Threads are stored as JSONL rollouts plus SQLite metadata; `thread/read` reads history without resuming; `thread/resume` re-attaches and auto-subscribes; `thread/fork` copies history; paginated `thread/turns/list` and `thread/items/list` provide history catch-up; pending approvals use a replay flow when a capable client reconnects. **[D]** A general **live-notification replay cursor / last-event-id / ack** protocol was **not documented**; "disconnect stops delivery", and recovery is re-resume plus pagination. This is a correction to the handoff's "reconnect/catch-up" framing. **[D]/[U]** `thread.sessionId` is a session-tree root distinct from `threadId`; forks inherit it. A no-subscriber/no-activity grace period of ~30 minutes ends with `thread/status/changed → notLoaded` and `thread/closed`. **[D]**

**Schema and compatibility.** `codex app-server generate-ts` / `generate-json-schema` produce version-specific schemas; experimental API is opt-in at initialization; `optOutNotificationMethods` suppresses exact notification methods. **[D]**

**What Codex App Server does not supply for AGI.** S2 consent, S3 authorization/revocation, branch identity/continuity, hash-anchored AGI evidence, station leases/fencing, or Owner decision records. A client UI approval is **not** Owner consent. **[I]/[P]**

## 5. Comparison, corrected

| Dimension | Cordis (verified in this deployment) | Codex App Server (documented) |
|---|---|---|
| Primary role | Internal runtime composition | External runtime control |
| Core abstraction | Context, Service, plugin, Fiber | Thread, Turn, Item, request/notification |
| Extension | Plugins, providers, loader patch layers | Client protocol, experimental fields, dynamic tools |
| Dependency handling | `inject`, scopes, isolation realms | Runtime configuration, thread config |
| Lifecycle | plugin phases `pending/loading/active/failed/unloading/null`; fiber effects | thread/turn/item lifecycle; thread status |
| Event dispatch | `emit`, `serial`, `parallel`, `waterfall` (live) | JSON-RPC notifications; item deltas |
| Interception | waterfall + monotonic `guard` (verified) | server-initiated approvals; policy config |
| Cleanup | fiber-scoped effects; quiescence-before-detach | `turn/interrupt`; item completion; thread unload |
| Persistence | in-memory session + append-only `sessionPersistence` with flush barrier | thread rollout + `thread/read`/`resume` |
| Backpressure | Host/runtime-specific; `session/flush` barrier | bounded queues; `-32001` overload |
| Client integration | not primary | first-class |
| Provider replacement | service contract seam (verified abstract services) | runtime-level; not a governance seam |

## 6. What to adopt, what to reject

### Adopt from Cordis (as patterns, not code)

1. **Service contract/provider/consumer separation** with abstract services and replaceable providers. **[V]/[P]**
2. **Injection + scoped registration** so a plugin declares dependencies and cannot silently grab a global. **[D]/[V]**
3. **Fiber-scoped effects and explicit lifecycle phases** for deterministic cleanup and partial-startup recovery. **[V]**
4. **Monotonic denial guards after the extensible pre-execute waterfall** — copy the ordering, not the authority. The independent governance gate must remain outside plugin code. **[V]/[P]**
5. **Four verified dispatch modes** (`emit`, `serial`, `parallel`, `waterfall`) as the initial normative set; add `bail` only if a verified need appears. **[V]/[P]**
6. **Durable session log + flush barrier distinct from live event feed** — copy the separation; AGI evidence is a separate, signed layer. **[V]/[P]**
7. **Profiles as ordered patch layers** with governance-protected rows. **[D]/[P]**
8. **Scope-filtered events** for per-agent/per-Branch isolation. **[V]/[P]**

### Adopt from Codex App Server (as protocol patterns, not code)

1. **Long-lived bidirectional control server** with initialization before any operation. **[D]/[P]**
2. **Thread/turn/item-like hierarchy** mapped to AGI `run_id/turn_id/item_id`, never to Branch identity. **[D]/[P]**
3. **Typed item lifecycle** (`started → delta → completed`) for a structured live timeline. **[D]/[P]**
4. **Server-initiated approval requests** with a closed decision vocabulary and a resolved notification; project them into an S2/S3 bridge, never treat them as consent. **[D]/[P]**
5. **Interrupt + final status** with an explicit cleanup/quiescence stage added by AGI (Codex alone does not prove tool/subprocess quiescence). **[D]/[P]**
6. **Bounded queues + overload error + retry/backoff contract.** **[D]/[P]**
7. **Schema generation + explicit experimental opt-in + notification opt-out.** **[D]/[P]**
8. **Thread read/resume/fork as history operations** — not as Branch continuity. **[D]/[P]**

### Reject / do not import

- **Cordis context isolation as a security boundary.** Use OS/process/sandbox isolation for untrusted plugins and skills. **[I]**
- **Codex thread as AGI Branch.** A thread is runtime conversation state; a Branch is the durable continuity/evidence unit. **[I]**
- **Client approval as Owner consent or S3 authorization.** A UI acceptance is an input to an approval bridge, not a grant. **[I]/[P]**
- **Codex event stream as durable evidence.** Use AGI's hash-anchored, signed evidence recorder. **[I]**
- **WebSocket as production transport** while the reference calls it experimental. **[D]/[P]**
- **Assuming `bail` exists** in this Cordis deployment or that `disposed` is a phase. **[V]/[U]**
- **Assuming Unix-socket transport** in Codex without a version-specific source. **[U]**

## 7. Corrections to the handoff's technical claims

| Handoff claim | Assessment | Evidence |
|---|---|---|
| Cordis lifecycle `PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED` | **Refined:** live enum is `pending/loading/active/failed/unloading/null`; no `disposed` phase | **[V]** `PluginFiberPhase` |
| Cordis event modes include `bail` | **Not observed** in live catalog; four modes observed | **[V]/[U]** |
| Codex supports Unix socket transport | **Confirmed with nuance:** `unix://` is WebSocket-over-UDS with HTTP Upgrade, not raw JSONL | **[D]** |
| Codex reconnect/catch-up | **Partially confirmed:** thread read/resume + paginated turns/items; no live-event replay cursor | **[D]/[U]** |
| Codex internal components | **Source-level fact only**, not a documented contract | **[D-source]** |
| Codex capability negotiation | **Client declaration + server gating**, not symmetric | **[D]** |
| Bounded queues | Docs scope to WebSocket; source uses 128-length bounded channels for stdio too | **[D]/[U]** |
| Session vs thread | `thread.sessionId` is a session-tree root distinct from `threadId`; forks inherit it | **[D]** |
| Codex approvals pause the turn | **Confirmed** | **[D]** |
| Cordis context scopes are not security isolation | **Correct** (inference) | **[I]** |
| Monotonic tool guard | **Confirmed** in live `tools.guard` | **[V]** |
| Session events vs durable evidence distinction | **Confirmed** in live session/event + flush | **[V]** |

## 8. Uncertainties and limits

- This assessment inspected **one running DSH profile** on Windows. Cordis behavior in other profiles/hosts (Linux, headless, sdk) was not exercised. **[U]**
- The Cordis lifecycle was observed only at `active`/`null`; the `pending/loading/failed/unloading` transitions are typed but not induced here. **[D]/[U]**
- Codex behavior is **documentation-supported**, not executed. No Codex server was installed or run; no endpoint or credential was used. **[D]**
- Codex documentation is fast-moving; the current `main` README is largely a feature changelog. The core protocol description is from the older README at commit `8fe5066b`; code facts are from commit `cb1bc0a` (2026-11-01T20:41:58Z); current behavior may differ. A separate research report is at `_codex_research/REPORT.md`. **[D]/[U]**
- No static review proves runtime security. Plugin code, Node runtime, native modules, and the transport stack remain in the TCB. **[I]**

## 9. Bottom line

Use Cordis as the **internal composition blueprint** and Codex App Server as the **external control blueprint**, but put an AGI-owned governance boundary between the Operator and every consequential effect. The strongest directly verified patterns to copy are: **monotonic guard after the pre-execute waterfall**, **closed approval outcomes including fail-closed `unavailable`**, **append-only session persistence with a flush barrier**, **agent-disposal after quiescence**, and **scoped service/event registration**. The strongest Codex patterns are: **initialize-before-operate**, **thread/turn/item timeline**, **server-initiated approval requests with a resolved notification**, **interrupt with final status**, and **bounded queues with an overload error**.

No implementation is authorized by this document.
