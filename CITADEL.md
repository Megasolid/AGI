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

Current task: `citadel/tasks/cit-kilo-m2-20261031-01.json` — independent reproduction of the Kilo M2 adversarial
matrix, full 19-case breakdown, retest after fixes, and cross-host/private-recall isolation tests.
