# AGI Citadel — central station

The public **AGI** repository is the project's **Citadel**: the central coordination and governance station. It is
**not** the organism identity authority and it never holds private memory, keys, passkeys, recovery shards, tokens,
production credentials, or DSH databases.

## Control plane (A+B hybrid)
- **Source of truth:** signed task/report files under `citadel/`.
- **Human control:** GitHub Issues/PRs for visibility, review and approval.
- **Kilo access:** read-only repository access; may only open PRs under `citadel/reports/`. No write to `main`,
  no secrets, no auto-execution.
- **Citadel does not remotely execute Kilo.** Tasks authorize a bounded scope; a human approves consequential actions.

## Task flow
1. Director/DSH writes `citadel/tasks/<task_id>.json` (schema `agi-citadel/task/0.1`) with `authorization_scope`,
   inputs, constraints, expected report and hash/signature.
2. Kilo pulls read-only, verifies hashes, executes only the bounded read-only scope in its isolated workspace.
3. Kilo opens a PR adding `citadel/reports/<task_id>.json` + evidence/findings. No main-branch write.
4. DSH verifies evidence hashes; Director accepts/rejects; issue closed. No auto-merge or auto-execution.

## Boundaries
No federation, family/public sharing, identity mutation, autonomous evolution, secrets, or production credentials.
Signed task envelopes authorize scope, not code execution. Human approval is required before consequential actions.
v4.0.1 release artifacts remain immutable.

Current task: `citadel/tasks/cit-kilo-m2-20261031-15.json` — deterministic verification with fixed verifier script;
no live integration/enforcement.


## KING and management
- **KING:** GPT-web, directly responsible for Citadel management, improvement, governance, documentation, priorities and
  release strategy. Owner D retains final authority; DSH implements; Kilo independently verifies.
- **Council:** Owner D, KING, DSH, Kilo.
- **Hall:** `citadel/hall/` — governance decisions, inventory, audits, roadmap.
- **Divisions:** `citadel/divisions/` — Identity, Awareness, Cognition, Memory, Federation, Evolution, Infrastructure,
  Verification, Documentation.
- **Release policy:** v4.0.1 is an immutable rollback baseline, not an evolution ceiling; v5 is additive and gated by
  evidence, compatibility, migration paths and verified rollback.


## Citizens
DeepSeek-web and Claude-web are trusted external LLM Citizens: research, analysis, coding and editorial support.
They are advisory only, not Council members, and receive curated briefs/public artifacts only — never raw private
sessions, credentials or key material. See `citadel/citizens/`.


## Operations
- **DSH — Manager** under KING supervision: implementation, evidence, task routing and Citizen coordination; no
  authority over KING/Owner, identity or federation.
- **DeepSeek-web / Claude-web — assistants** to the Manager: advisory research, drafting, review and endpoint analysis;
  no execution or governance authority.
- **Season:** OPEN. Owner D has not declared its end.
- See `citadel/governance/roles.md`.


## Stations
DSH is the primary/Manager station. **Kilo is an Official AGI Station and backup operations station** when DSH is unavailable or out of tokens; see `citadel/governance/stations.md`. Backup work is approved tasking only, with no identity/federation/runtime/release authority.
