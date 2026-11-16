# AGI REPOSITORY SIZE AUDIT

**Status:** READ-ONLY INVESTIGATION — **no deletion, migration, staging, commit, or merge performed.**
**Branch:** `docs/silverstone-consolidated-readiness` · **HEAD:** `e7eb0ca` · **Date:** 2026-11-16
**Labels:** SILVERSTONE-VERIFIED (freshly measured this session) · PROPOSED.
**Units:** **1 MiB = 1,048,576 bytes**; **1 MB = 1,000,000 bytes**. Figures below are **MiB** (binary).
**Correction:** See `REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md` for authoritative byte counts, mutually-exclusive primary classification, and MB/MiB reconciliation. Headline total corrected to **2,306,286,254 bytes = 2,199.45 MiB**; git object DB corrected to **424.24 MiB** (git total 427.67 MiB; delta 3.43 MiB non-object metadata).

---

## 1. Measurement method

| Metric | Method |
|---|---|
| Logical size | `Get-ChildItem -Recurse -File` → sum of `Length` (uncompressed file bytes) |
| Allocated disk size | **Not measured** (would require per-cluster slack; logical size is the consistent definition used here) |
| Git object DB | `git count-objects -vH` (size-pack + size loose) |
| Git history blobs | `git rev-list --objects --all` → `git cat-file --batch-check` |
| Tracked / untracked / ignored | `git ls-files`, `git ls-files --others --exclude-standard`, `git ls-files --others --ignored --exclude-standard` |
| Git LFS | `git lfs ls-files` → **0 tracked, no `.gitattributes`** |

All measurements are **fresh** (this session, 2026-11-16) and supersede historical figures.

---

## 2. Headline measurements (SILVERSTONE-VERIFIED)

| Metric | Bytes | MiB | Notes |
|---|---:|---:|---|
| **Total working tree (logical)** | 2,306,286,254 | **2,199.45** | 23,460 files |
| Git object database | 444,847,882 | **424.24** | `size 41.05 MiB` + `size-pack 383.19 MiB` |
| Git total (`.git` via Get-ChildItem) | 448,448,486 | **427.67** | objects 424.24 + non-object 3.43 |
| Git pack files (largest) | 398,307,675 | **379.86** | single `.pack` |
| **Tracked logical size** | 1,665,481,339 | **1,588.33** | 19,643 tracked files |
| Untracked (not ignored) logical | 547,974,085 | **522.59** | 87 entries |
| Ignored logical | 92,830,830 | **88.53** | 278 ignored entries |
| Git LFS | 0 | 0 | no LFS |

**Formula check:** 1,588.33 + 522.59 + 88.53 = **2,199.45 MiB** ✓; 424.24 + 3.43 = **427.67 MiB** ✓.

**Note:** The `.git` directory (427.67 MiB) is **inside** the working-tree total. A lean V5 checkout without `.git` history would drop ~428 MiB immediately.

**Authoritative reconciliation, mutually-exclusive classification, and MB/MiB conversions:** see `REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md`.

---

## 3. Top 20 largest files (SILVERSTONE-VERIFIED)

| # | MB | Path |
|---:|---:|---|
| 1 | 379.86 | `.git/objects/pack/pack-3d722a65….pack` |
| 2 | 110.95 | `.reference/state_backup_v40_20261104_001710.zip` |
| 3 | 88.25 | `.reference/memory/tools/node/node.exe` |
| 4 | 88.25 | `.reference/backups/agi/stable-gen3.5-…/memory/tools/node/node.exe` |
| 5 | 88.25 | `.reference/backups/agi/phase2-…/memory/tools/node/node.exe` |
| 6 | 82.11 | `.reference/memory/tools/node/node_modules/bun/bin/bun.exe` |
| 7 | 82.11 | `.reference/memory/tools/node/node_modules/bun/bin/bunx.exe` |
| 8 | 82.11 | `.reference/backups/agi/stable-gen3.5-…/bun/bin/bun.exe` |
| 9 | 82.11 | `.reference/backups/agi/stable-gen3.5-…/bun/bin/bunx.exe` |
| 10 | 82.11 | `.reference/backups/agi/phase2-…/bun/bin/bun.exe` |
| 11 | 82.11 | `.reference/backups/agi/phase2-…/bun/bin/bunx.exe` |
| 12 | 52.82 | `.reference/tools/bin/cloudflared.exe` |
| 13 | 42.14 | `U0.1_output/gh_portable/bin/gh.exe` |
| 14 | 25.36 | `.reference/memory/index/embeddings.npy` |
| 15 | 24.50 | `.reference/agi_memory.tar.gz` |
| 16 | 14.90 | `.reference/AGI.Original Data/dsh/sessions/…/session-182488c1….json` |
| 17 | 14.08 | `.git/objects/9e/3170ab34…` (loose object) |
| 18 | 13.84 | `.reference/memory/index/chunks.json` |
| 19 | 13.68 | `.vs/agi.slnx/FileContentIndex/d7868273….vsidx` |
| 20 | 13.05 | `U0.1_output/gh.msi` |

**Observation:** 11 of the top 20 are **Node/Bun executables duplicated across three `memory/tools/` trees** (live + 2 backups). 1 is a Git pack. 1 is a VS index. 2 are GitHub CLI installers. 2 are generated embeddings/chunks.

---

## 4. Top 20 largest directories (SILVERSTONE-VERIFIED)

| # | MB | Path |
|---:|---:|---|
| 1 | 1,613.82 | `.reference` |
| 2 | 705.18 | `.reference/backups` |
| 3 | 693.07 | `.reference/backups/agi` |
| 4 | 427.67 | `.git` |
| 5 | 424.29 | `.git/objects` |
| 6 | 383.24 | `.git/objects/pack` |
| 7 | 344.61 | `.reference/backups/agi/phase2-20261030-180040` |
| 8 | 338.98 | `.reference/backups/agi/stable-gen3.5-20261030-144023` |
| 9 | 327.04 | `.reference/memory` |
| 10 | 303.71 | `.reference/backups/agi/phase2-…/memory` |
| 11 | 303.09 | `.reference/backups/agi/stable-gen3.5-…/memory` |
| 12 | 281.11 | `.reference/memory/tools` |
| 13 | 280.81 | `.reference/backups/agi/phase2-…/memory/tools` |
| 14 | 280.81 | `.reference/backups/agi/stable-gen3.5-…/memory/tools` |
| 15 | 264.74 | `.reference/…/memory/tools/node` (×3 trees) |
| 16 | 176.24 | `.reference/…/node_modules` (×3 trees) |
| 17 | 173.40 | `.reference/state` |
| 18 | 164.09 | `.reference/AGI.Original Data` |
| 19 | 84.35 | `U0.1_output` |
| 20 | 70.53 | `.vs` |

---

## 5. Storage breakdown by category (SILVERSTONE-VERIFIED)

| Category | MB | % of working tree | Definition |
|---|---:|---:|---|
| **Tracked** | 1,588.33 | 72.2% | `git ls-files` |
| **Untracked (not ignored)** | 522.56 | 23.8% | new/uncaptured work |
| **Ignored** | 88.53 | 4.0% | `.vs/`, `__pycache__`, etc. |
| **Git object DB** | 447.72 | (overlaps `.git`) | history, packs, loose objects |
| **Git LFS** | 0 | 0% | none |

---

## 6. Submodules (SILVERSTONE-VERIFIED)

| Path | Commit | Size | Notes |
|---|---|---:|---|
| `.reference/state/repo/AGI` | `cfdc835` | 9.11 MB | modified content; **protected, do not touch** |
| `.reference/AGI.Original Data/codex/memories` | `dac97f3` | 0.02 MB | **stale `.gitmodules` mapping missing** (warning) — **UNRESOLVED** |

`.gitmodules` at root is **absent/empty**; gitlinks exist in the index (`git ls-files -s` shows `160000` entries). `git submodule status` warns about the missing mapping.

---

## 7. Filesystem vs Git

- **No Git LFS.** Large binaries (`.exe`, `.npy`, `.zip`, `.tar.gz`) are stored as **regular Git blobs**, inflating history.
- **Filesystem cluster slack** (allocated vs logical) not measured; on NTFS with ~4 KB clusters and many small files, allocated may exceed logical by a few percent. Not material to conclusions.
- `.git/objects` (424 MB) is the single largest Git consumer; one pack is 380 MB.

---

## 8. Duplicate / near-duplicate candidates (metadata only; **not** assumed disposable)

| Candidate | Evidence | Disposition |
|---|---|---|
| `node.exe` ×3 (92,534,088 bytes, same digest prefix `9a4eb5f1…`) | exact size match across `.reference/memory/tools/node` + 2 backups | **INVESTIGATE** (protected `.reference` → no change) |
| `bun.exe`/`bunx.exe` ×6 (86,096,984 bytes) | exact match across 3 trees | **INVESTIGATE** (protected) |
| `embeddings.npy` / `chunks.json` in `.reference/memory/index` + 2 backups | generated; sizes differ (25.36 vs 13.68 vs 12.93 MB) → **different snapshots** | **INVESTIGATE** (not exact duplicates) |
| `U0.1_output/AGI_repo` (v4.0.1-114) vs `.reference/state/repo/AGI` (v4.0.1-107) | different snapshots | **INVESTIGATE/ARCHIVE** |
| `agi_runtime-v0.4.3.zip` / `agi-runtime-dna-*.zip` in `state/release` + `state/repo/AGI/releases` | mirrored release dirs | **INVESTIGATE** |
| `.vs/` vs `__pycache__` | generated | **REGENERATE** |

**No exact duplicates were deleted or assumed disposable.** All `.reference` items are **protected → no disposition change**.

---

## 9. Key findings

1. **`.reference/` alone is 1,613.82 MB (73% of the working tree)** and is **protected** — it cannot be reduced under current constraints.
2. **Git history (`.git`) is 427.67 MB** — the pack file alone is 380 MB. A lean V5 repo with fresh history would not carry this.
3. **Node/Bun toolchain duplicates** consume ~800 MB across three `memory/tools/` trees (live + 2 backups).
4. **`state_backup_v40_*.zip` (110.95 MB)** is the largest single tracked blob.
5. **`U0.1_output/` (84.35 MB)** is untracked and dominated by GitHub CLI installers (`gh.exe` 42 MB, `gh.msi` 13 MB, `gh.zip` 13 MB).
6. **`.vs/` (70.53 MB)** is ignored, generated IDE cache.
7. **`AGI.Original Data/` (164.09 MB)** is tracked session history (dsh/codex) — **protected**.
8. **`output/` (1.24 MB)** is small SILVERSTONE evidence — keep.
9. **`documentation/`, `tooling/`, `mcp/`, `web_bridge/`, `contracts/`** are all **< 1 MB combined** — the actual lean source.
10. **Target feasibility:** a lean V5 workspace containing **only** source + contracts + tests + docs (excluding `.reference`, `.git`, `U0.1_output`, `.vs`) is **~5–8 MB** — comfortably under 10 MB.

---

## 10. Non-operation

Read-only measurement only. No deletion, migration, staging, commit, merge, `git gc`, prune, `git add`, or history rewrite. `.reference`, V4.0.1, keys, `agi.rar`, `agi_memory.tar.gz`, operational memory, and pre-existing uncommitted changes **untouched**. Protected submodule state preserved.

**End of size audit.**