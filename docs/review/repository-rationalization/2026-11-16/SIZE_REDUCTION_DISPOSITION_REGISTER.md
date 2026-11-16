# SIZE REDUCTION DISPOSITION REGISTER

**Status:** PROPOSED (dispositions only) — **nothing executed.** Protected items → **no disposition change**.
**Labels:** SILVERSTONE-VERIFIED (sizes) · PROPOSED (disposition).

**Dispositions:** KEEP · ADAPT · REGENERATE · EXTERNALIZE · ARCHIVE · INVESTIGATE · RETIRE CANDIDATE.

---

## 1. Ranked reduction opportunities (largest first; metadata only)

| Rank | Item | Size | Class | Disposition | Owner approval | Notes |
|---:|---|---:|---|---|---|---|
| 1 | `.reference/backups/` (phase2 + stable-gen3.5 + gen2) | 705.18 MB | F Historical | **ARCHIVE (protected)** | n/a (no change) | season backups; do not touch |
| 2 | `.git/` history (pack 380 MB) | 427.67 MB | G/history | **EXTERNALIZE (fresh history for lean repo)** | **Required** | lean repo starts fresh; history archived |
| 3 | Node/Bun toolchain (`memory/tools/node` ×3) | ~800 MB | H Third-party | **EXTERNALIZE** | **Required** | `node.exe`×3 (88 MB), `bun`/`bunx`×6 (82 MB) — exact duplicates |
| 4 | `state_backup_v40_20261104_001710.zip` | 110.95 MB | F Archive | **ARCHIVE (protected)** | n/a | largest tracked blob |
| 5 | `U0.1_output/` (gh installers + AGI_repo) | 84.35 MiB | H/I | **EXTERNALIZE / ARCHIVE** | **Required** | `gh.exe` 42 MB, `gh.msi` 13 MB, `gh.zip` 13 MB; untracked |
| 6 | `.vs/` | 70.53 MiB | G Generated | **REGENERATE** | **Required** | IDE cache; ignored |
| 7 | `cloudflared.exe` | 52.82 MB | H Third-party | **EXTERNALIZE / ADAPT** | **Required** | tunnel binary |
| 8 | `.reference/agi_memory.tar.gz` | 24.50 MB | F Archive | **ARCHIVE (protected)** | n/a (G25-02b) | do not touch |
| 9 | `embeddings.npy` + `chunks.json` (live + backups) | ~52 MiB | G Generated | **REGENERATE** | **Required** | reproducible; generator `memory_embed.py` present; pin model; see reconciliation §10 |
| 10 | `AGI.Original Data/` (dsh/codex sessions) | 164.09 MB | F Historical | **ARCHIVE (protected)** | n/a | session history; do not touch |
| 11 | `.reference/state/` (entelechy/family/…) | 173.40 MB | E Operational | **EXTERNALIZE / ARCHIVE (protected)** | **Required** | runtime/season state |
| 12 | `.reference/memory` (live) | 327.04 MB | E Operational | **KEEP (protected) + EXTERNALIZE toolchain** | **Required** for toolchain | operational authority |
| 13 | `.reference/tools/` (cloudflared) | 52.93 MB | H Third-party | **EXTERNALIZE** | **Required** | see #7 |
| 14 | `output/` (SILVERSTONE reports) | 1.24 MB | D Evidence | **KEEP** | — | review value high |
| 15 | `documentation/` | 0.68 MB | D Docs | **KEEP** | — | curated architecture |
| 16 | `tooling/`, `mcp/`, `web_bridge/`, `contracts/` | ~1.0 MB | B/C | **KEEP / ADAPT** | — | lean source |
| 17 | `__pycache__/` (22 dirs) | 2.81 MiB | G Generated | **REGENERATE** | **Required** | ignored; evidence in reconciliation §10 |
| 18 | `*.db-shm` / `*.db-wal` | <0.01 MB | G Generated | **REGENERATE** | — | SQLite sidecars |
| 19 | `U0.1_output/u0-1-curated-intake-handoff.tar.gz` + manifests | 5.0 MB | I Build | **ARCHIVE** | **Required** | handoff artifacts |
| 20 | `intake/` (empty), stray temp | 0 | J Unknown | **INVESTIGATE** | **Required** | empty; stray |

---

## 2. Protected material — **no disposition change**

| ID | Item | Size | Status |
|---|---|---:|---|
| P1 | `.reference/` (entire tree) | 1,613.82 MB | **PROTECTED — no change** |
| P2 | `agi.rar` | 462,324,138 B | **PROTECTED — preserve** (pending L6 + retirement) |
| P3 | `agi_memory.tar.gz` | 25,695,089 B (`e7196d2e…`) | **PROTECTED — preserve** (G25-02b unapproved) |
| P4 | Operational memory (`[REDACTED-LOCAL-PATH]/agi_runtime/memory`) | 342.9 MB | **PROTECTED — interim authority** |
| P5 | V4.0.1 (`6a0fb79` / `85a9225…`) | — | **PROTECTED — rollback floor** |
| P6 | Keys / shards / trust anchors | — | **PROTECTED — never commit** |
| P7 | Pre-existing uncommitted changes | — | **PRESERVE** |

---

## 3. Lean V5 subset (what the lean repo actually needs)

| Item | Size |
|---|---:|
| `contracts/` + U0 docs | ~0.2 MB |
| `tooling/` + `mcp/` + `web_bridge/` + `contracts/` | ~1.0 MB |
| `documentation/workspace/` (curated) | ~0.7 MB |
| `tests/` (lean) + `skills/` (text) | <0.1 MB |
| **Lean total (approx.)** | **~2–3 MB** |

**Result:** The lean V5 repository is **~2–3 MB**, **well under the 10 MB preferred target** and far under the 50 MB hard cap.

---

## 4. Rules

- **No disposition executed.** This register is a proposal only.
- **Protected material is never RETIRED.**
- Every EXTERNALIZE / ARCHIVE / REGENERATE action requires **separate owner approval**.
- Rollback floor = V4.0.1; documentation completion ≠ implementation authorization.

**Awaiting owner review.**

**Status:** **DISPOSITION PROPOSED — NOTHING EXECUTED.**