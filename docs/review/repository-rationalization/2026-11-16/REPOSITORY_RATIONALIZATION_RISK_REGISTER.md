# REPOSITORY RATIONALIZATION RISK REGISTER

**Status:** PROPOSED (risk analysis only) — **nothing executed.**
**Labels:** SILVERSTONE-VERIFIED · PROPOSED · OWNER-APPROVED · UNRESOLVED · NOT ESTABLISHED.

---

## 1. Risks

| ID | Risk | Severity | Likelihood | Mitigation | Residual | Owner approval |
|---|---|---|---|---|---|---|
| R-01 | Retiring a still-referenced component breaks runtime/boot | **High** | Medium | reference/consumer scan before any RETIRE; keep protected `.reference` intact | Medium | Required |
| R-02 | Deleting/moving protected `.reference` / `agi.rar` / `agi_memory.tar.gz` / V4.0.1 loses rollback floor | **Critical** | Low (if rules obeyed) | protected → **no change**; backup verification | Low | Required (should not be requested) |
| R-03 | Externalizing toolchain (Node/Bun/cloudflared) breaks local dev without adapter | Medium | Medium | adapter + config (`AGI_*`); capability detection; fail-closed | Medium | Required |
| R-04 | Regenerating embeddings/chunks produces different index (non-determinism) | Medium | Medium | pin model + version; verify digests; keep old index until verified; generator `memory_embed.py` present | Medium | Required |
| R-05 | Fresh Git history loses provenance / lineage evidence | **High** | High (if done) | archive old history (bundle) before any new repo; keep `.reference` | Medium | Required |
| R-06 | Lean repo accidentally commits keys / private sessions | **High** | Low | never bundle `.reference`, `AGI.Original Data`, keys; `.gitignore` + review | Low | Required |
| R-07 | Host-specific lock-in persists (DPAPI, chrome path, HF path, venv) | Medium | High (current) | portability adapters; externalize config | Medium | Required |
| R-08 | Claims of "under 50 MB" based on cherry-picked measurements | Medium | Low | consistent logical-size method; report allocated vs logical | Low | — |
| R-09 | Removing `.vs/` / `__pycache__` while IDE/process holds locks | Low | Medium | close editors; delete only when unlocked | Low | Required |
| R-10 | `codex-mcp` deletion / pre-existing uncommitted changes lost during cleanup | Medium | Medium | preserve untouched; snapshot before any operation | Medium | Required |
| R-11 | Submodule `.reference/state/repo/AGI` modified content lost | Medium | Low | do not touch; preserve submodule state | Low | — |
| R-12 | Stale `.gitmodules` mapping (codex/memories) causes future checkout failure | Low | Medium | fix mapping separately (owner) | Low | Required |

---

## 2. Protected data & blockers

| ID | Protected item | Blocker |
|---|---|---|
| P1 | `.reference/` (1.6 GB) | **No modification, enumeration, extraction, or inspection of contents.** Metadata/aggregate size only. |
| P2 | `agi.rar` (462 MB) | **Do not alter.** Pending L6 + separate retirement. |
| P3 | `agi_memory.tar.gz` (24.5 MB) | **Do not alter.** G25-02b unapproved. |
| P4 | Operational memory | **Do not migrate/modify.** Interim authority. |
| P5 | V4.0.1 | **Do not alter.** Rollback floor. |
| P6 | Keys / shards / trust anchors | **Do not access/change.** |
| P7 | Scheduled tasks | **Do not change.** |
| P8 | Pre-existing uncommitted work | **Preserve.** |
| P9 | Submodule state | **Preserve.** |

---

## 3. Unresolved questions (owner decisions required)

| ID | Question | Blocks |
|---|---|---|
| Q-01 | Approve lean-repo creation with **fresh history** (old history archived externally)? | Lean V5 repo |
| Q-02 | Approve **externalizing** Node/Bun/cloudflared/gh toolchain? | Size target |
| Q-03 | Approve **regenerating** `.vs/`, `__pycache__`, embeddings/chunks? | Cleanup |
| Q-04 | Approve **archiving** `U0.1_output/` (gh installers, AGI_repo)? | Size target |
| Q-05 | Confirm `agi.rar` disposition (preserve vs separate retirement)? | Archive policy |
| Q-06 | Confirm retention for `AGI.Original Data/` sessions (164 MB)? | History policy |
| Q-07 | Fix stale `.gitmodules` mapping for `codex/memories`? | Repo integrity |
| Q-08 | Approve degraded-mode / externalization policy for V5 adapters? | Portability |
| Q-09 | Approve `dependencies.v5.json` manifest + integrity/acquisition policy (reconciliation §11)? | Dependency externalization |
| Q-10 | Confirm VS version + embedding model pin for regeneration (reconciliation §10)? | Regeneration fidelity |

**None resolved by this register.**

---

## 4. Non-authorization

Read-only investigation + documentation only. No cleanup, deletion, archive movement, migration, packaging, staging, commit, merge, `git gc`, prune, or implementation. `.reference` contents **not enumerated/inspected**. Protected material untouched. Pre-existing uncommitted changes preserved.

**Awaiting owner review.**

**Status:** **RISK REGISTER PROPOSED — NOTHING EXECUTED.**