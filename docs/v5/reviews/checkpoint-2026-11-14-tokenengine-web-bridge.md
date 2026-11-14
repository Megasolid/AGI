# AGI V5 checkpoint — TokenEngine D04 and Web Bridge review

**Date:** 2026-11-14  
**Branch:** `review/v5-web-bridge-checkpoint-20261114`  
**Base:** `main` at `98a53250181173815eddf1bc137b2c2f2d995b60`  
**Status:** Review checkpoint only — no implementation approval, merge, activation or release  
**Stable baseline:** v4.0.1 remains unchanged  
**V5 status:** Proposed architecture, not shipped

## 1. Owner checkpoint: TokenEngine D04

The Owner selected:

- **Scope:** `all` — all internal AGI operations are in scope where token/context optimization is relevant.
- **Optimization:** `adaptive` — select the most efficient representation that satisfies the task's preservation and quality requirements.

Human-facing communication remains natural language and normal conversational context behavior. Internal operations use adaptive structured/context/token optimization by default. TokenEngine is a cross-cutting service, not a ninth functional domain, identity tier, memory database, semantic protocol or authorization authority.

Boundary rules:
- AKMS remains owner of persistent knowledge and memory.
- SSL remains the semantic communication contract; JSON/UTF-8 remains its proposed normative transport.
- Harness/Operator retains orchestration and task lifecycle.
- DNA/Governance and protected execution boundaries retain authorization authority/enforcement.
- Exact preservation is mandatory for identity, authorization, evidence, cryptographic material, canonical records and hard constraints.
- Provider-specific tokenizer measurements must be distinguished from estimates.
- Optimization failure falls back to a validated representation.
- Token savings must be assessed alongside task quality, semantic preservation, recovery cost and reliability.

This records the Owner's architectural direction; it does not authorize implementation.

## 2. DSH Web Bridge handoff — source-supported status

The 14 November handoff reports a standalone Python HTTP bridge at `skills/agi/web_bridge/`, exposing an Anthropic-compatible `POST /v1/messages` endpoint and using `cm_daemon` → Chrome CDP → DeepSeek web chat. It reports that JavaScript editor injection, assistant-message detection, response-stability polling, rate limiting, SHA-256 prompt deduplication and per-chat bootstrap tracking were ported from the earlier working bridge.

The handoff reports passing local self-tests and end-to-end examples. These are project-reported results, not independently reproduced by this review.

The handoff says the implementation is on a local branch `feat/web-bridge-complete-fix`, with a push attempt that timed out. That branch was not present in the connected official repository branch listing at this checkpoint. The actual implementation files were not included in the handoff material available for this review. Consequently, no source-level correctness or security certification is made here.

## 3. Preliminary architecture assessment

### Recommended role

Treat the Web Bridge as a **provider transport/adapter**, not as an AGI authority, memory service, tool executor or general-purpose workspace agent.

Proposed request path:

`Mind / Harness → FCC policy and request validation → provider adapter interface → Web Bridge → cm_daemon / browser session → provider UI`

Responses return through the same boundary and must be treated as untrusted provider output until validated by the caller.

The bridge must not bypass FCC authorization, task budgets, evidence capture, provider selection policy or result validation. It should transport prompts and responses, not own AGI Season RAM or canonical context.

### Placement recommendation

For an initial implementation, prefer a provider-integration location such as `integrations/llm-providers/deepseek-web/` (or the repository's eventual equivalent provider-adapter directory), rather than placing the whole HTTP bridge under `mcp/`.

Rationale: the described bridge exposes an Anthropic-compatible HTTP provider endpoint; `cm_daemon` is its current browser-control dependency. Keep the DSH-specific adapter and desktop-profile patch local to the DSH environment unless/until a supported, reproducible plugin distribution contract is defined.

This is a placement recommendation only; the official repository's final V5 source tree remains subject to the U0 architecture and review process.

### cm_daemon dependency

Acceptable as an initial transport dependency if its interface, version, lifecycle, permissions and failure behavior are documented and pinned. Do not add a raw CDP fallback merely for architectural neatness. First define a transport interface and test contract; add another backend only if there is a demonstrated portability, reliability or maintenance need.

## 4. Security and reliability gates before acceptance

Loopback binding alone is not a complete security boundary. Source review and tests must establish at least:

1. Explicit authentication for local callers; no unauthenticated state-changing or prompt-submission endpoint.
2. Strict loopback-only bind and peer/Host validation; assess browser-origin, DNS-rebinding and CSRF exposure.
3. Strict route, method, content-type, body-size, timeout and concurrency limits.
4. No exposure of Chrome CDP or `cm_daemon` control ports beyond the intended local boundary.
5. Allowlisted browser target and origin; do not execute injected JavaScript against arbitrary tabs.
6. Safe handling of transcript endpoints, logs and prompts; avoid leaking private conversation content or credentials.
7. Bootstrap state bound to the correct chat/session identity and verified by an explicit protocol, not a weak UI heuristic alone.
8. Deduplication keys scoped to the target/session and request semantics; define behavior for concurrent in-flight duplicates, expiry and errors.
9. Response polling handles streaming/partial responses, stale messages, multiple assistant blocks, tool messages, retries and timeout without returning incomplete or unrelated content.
10. Anthropic-compatible request/response behavior is tested for supported content forms, errors, stop reasons, token-usage semantics and unsupported options.
11. Provider web output is treated as untrusted data; prompt injection in page content must not gain access to local tools, files, credentials or AGI authority.
12. Logs redact secrets and define retention; tests cover failure and restart behavior.

The reported two-stable-poll heuristic is useful but is not by itself proof that a response is complete. Likewise, a SHA-256 dedupe key prevents accidental duplicate work only within the implemented scope; it is not authentication or authorization.

## 5. Generalizing toward direct project-file access

The current Web Bridge, as described, provides browser-based LLM transport. It does **not** provide direct project filesystem access.

Do not expand it into an unrestricted filesystem or shell endpoint. If direct project access is desired, design a separate **Workspace Bridge / Project Agent** with a narrow, auditable API:

- Read-only discovery and file listing within explicitly approved project roots.
- Bounded file reads and content search.
- Structured diffs and proposed edits.
- Explicit write operations behind owner-controlled approval.
- Path canonicalization and symlink/traversal protection.
- No arbitrary shell execution by default.
- Per-operation authorization, audit records, size limits and rollback/recovery.
- A dry-run mode and a clear separation between reading, proposing, writing and committing.
- Git operations constrained to feature branches and pull requests; never silently write to `main`.

The Workspace Bridge should integrate with FCC and the Harness as a capability. The provider Web Bridge can then be one model endpoint among several, while file access remains a separately permissioned capability.

## 6. Official repository synchronization

The official repository's governance requires bounded changes on a branch, review and required approval before merge. The v4.0.1 stable baseline must remain protected.

The local implementation branch reported by the handoff was not found on the connected remote at this checkpoint. Do not recreate or publish its source from this summary. First supply the actual source files or successfully push the branch. Then:

1. Compare the implementation against the original working bridge and the reported local commit.
2. Review `bridge.py`, `adapter.js`, `config.json`, `cordis.patch.yml`, `selftest.py` and README.
3. Re-run tests from a clean environment and record exact versions and test evidence.
4. Resolve the security gates above.
5. Prepare a focused PR to an approved V5 proposal branch; do not merge or deploy without required review and Owner approval.

## 7. Current decision register

| Item | Checkpoint status |
|---|---|
| TokenEngine D04 scope = all | Owner decision recorded |
| TokenEngine D04 optimization = adaptive | Owner decision recorded |
| Web Bridge functionality | Reported by handoff; not independently reproduced |
| Web Bridge source-level review | Pending actual source files |
| Web Bridge security acceptance | Not accepted; gates listed above |
| DSH adapter deployment | Not authorized by this checkpoint |
| FCC integration | Architectural direction proposed; interface not verified |
| Direct project-file access | Separate Workspace Bridge design required |
| Official repo merge/release | Not authorized |

## 8. Required next evidence

Provide the implementation bundle (source and tests, with secrets and private tokens removed), plus the DSH handoff and any current FCC interface contract. The minimum source set is:

- `web_bridge/bridge.py`
- `web_bridge/adapter.js`
- `web_bridge/config.json` with secrets redacted
- `web_bridge/cordis.patch.yml`
- `web_bridge/selftest.py`
- `web_bridge/README.md`
- The relevant `cm_daemon` tool contract/version and FCC gateway interface

**Checkpoint conclusion:** the Web Bridge is a promising provider-adapter direction and may become a useful model-access path for AGI development. It is not yet evidence of a secure general-purpose project bridge. Keep browser transport and project filesystem access as separate capabilities, route both through FCC policy enforcement, and preserve the V4 baseline and repository review workflow.
