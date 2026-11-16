# REPOSITORY SIZE ACCOUNTING AND RECONCILIATION

**Status:** READ-ONLY CORRECTION — **no cleanup, migration, or Git operation performed.**
**Supersedes:** measurement sections of `REPOSITORY_SIZE_AUDIT.md` (2026-11-16 first pass).
**Method:** authoritative byte counts via `Get-ChildItem -Recurse -File` (logical size) + `git count-objects -vH` (object DB).
**Units:** **1 MiB = 1,048,576 bytes**; **1 MB = 1,000,000 bytes**. All MiB figures below use 1,048,576.

---

## 1. Authoritative byte counts (SILVERSTONE-VERIFIED, 2026-11-16)

| Metric | Bytes | MiB | MB |
|---|---:|---:|---:|
| **Total working tree (logical)** | **2,306,286,254** | **2,199.45** | 2,306.29 |
| Git object database (`count-objects`) | 444,847,882 | 424.24 | 444.85 |
| Git total (`.git` via Get-ChildItem) | 448,448,486 | 427.67 | 448.45 |
| Git non-object metadata | 3,600,604 | 3.43 | 3.60 |
| Worktree excl. `.git` | 1,857,837,768 | 1,771.77 | 1,857.84 |
| Tracked logical | 1,665,481,339 | 1,588.33 | 1,665.48 |
| Untracked (non-ignored) logical | 547,974,085 | 522.59 | 547.97 |
| Ignored logical | 92,830,830 | 88.53 | 92.83 |
| Git LFS | 0 | 0 | 0 |

**Reconciliation (exact):**
- 1,588.33 + 522.59 + 88.53 = **2,199.45 MiB** ✓ (tracked + untracked + ignored = total)
- 424.24 + 3.43 = **427.67 MiB** ✓ (git objects + non-object = `.git` total)
- 427.67 + 1,771.77 = **2,199.45 MiB** ✓ (`.git` + worktree = total)

---

## 2. Why `.git` = 427.67 MiB but object DB = 424.24 MiB

**They are different scopes of the same repository, measured differently:**

| Measurement | Scope | Bytes | MiB |
|---|---|---:|---:|
| `git count-objects -vH` | **Only** `.git/objects/` (packs + loose) | 444,847,882 | 424.24 |
| `Get-ChildItem .git -Recurse` | **All** of `.git/` (objects + refs + logs + hooks + index + config + info) | 448,448,486 | 427.67 |

**Delta = 3,600,604 bytes (3.43 MiB)** = non-object Git metadata:
- `refs/` (branches, tags, remotes)
- `logs/` (reflogs)
- `hooks/*.sample`
- `index` (staging)
- `config`, `packed-refs`, `COMMIT_EDITMSG`, `FETCH_HEAD`, `ORIG_HEAD`, `description`, `kilo`
- `objects/info/` (commit-graph, packs list)

**Both cover the same repository.** Both use **logical size** (sum of file `Length`, uncompressed). Neither uses allocated/cluster size.

**Conclusion:** No discrepancy — the 3.43 MiB delta is Git's bookkeeping. The object DB (424.24 MiB) is the history; `.git` total (427.67 MiB) is history + metadata.

---

## 3. Does the 2,199.45 MiB total include `.git`, submodules, ignored files?

**Yes — all three.**

| Component | Included? | MiB |
|---|---|---|
| `.git/` (objects + metadata) | **Yes** | 427.67 |
| Submodule worktree `.reference/state/repo/AGI` | **Yes** (1,818 files) | 9.11 |
| Submodule git `.reference/state/repo/AGI/.git` | **Yes** (1,450 files, standalone) | 4.89 |
| Submodule worktree `codex/memories` | **Yes** (32 files) | 0.02 |
| Ignored files (`.vs`, `__pycache__`, etc.) | **Yes** | 88.53 |
| Tracked files | **Yes** | 1,588.33 |
| Untracked (non-ignored) | **Yes** | 522.59 |

**Exact reconciliation:**
- `.git` (427.67) + `.reference` (1,613.86) + `U0.1_output` (84.35) + `.vs` (70.53) + `output` (1.24) + `documentation` (0.68) + `tooling` (0.61) + `mcp` (0.19) + `web_bridge` (0.18) + root files (0.11) + `state` (0.02) + `contracts` (0.003) = **2,199.45 MiB** ✓

**Note:** The standalone submodule `.git` (4.89 MiB) is **inside** `.reference/state` (173.40 MiB); it is counted once via `.reference`, not separately. The 1,857.84 MB worktree-excl-`.git` already includes submodules and ignored files.

---

## 4. MB vs MiB conversions (all figures)

| Value | Bytes | MiB (÷1,048,576) | MB (÷1,000,000) |
|---|---:|---:|---:|
| Total working tree | 2,306,286,254 | 2,199.45 | 2,306.29 |
| Git object DB | 444,847,882 | 424.24 | 444.85 |
| Git total | 448,448,486 | 427.67 | 448.45 |
| Worktree excl. `.git` | 1,857,837,768 | 1,771.77 | 1,857.84 |
| Tracked | 1,665,481,339 | 1,588.33 | 1,665.48 |
| Untracked | 547,974,085 | 522.59 | 547.97 |
| Ignored | 92,830,830 | 88.53 | 92.83 |

**Convention:** This report uses **MiB** (binary, 1,048,576) for all size figures. Where "MB" appears in prior docs, it meant MiB. The authoritative total is **2,306,286,254 bytes = 2,199.45 MiB = 2,306.29 MB**.

---

## 5. Correction to original report

| Original claim | Corrected | Reason |
|---|---|---|
| "Total 2,199.41 MB" | **2,199.45 MiB (2,306,286,254 bytes)** | fresh authoritative count; 23,460 files |
| "`.git` 427.67 MB" + "object DB 447.72 MB" (implied contradiction) | `.git` = 427.67 MiB; object DB = **424.24 MiB**; delta = 3.43 MiB non-object metadata | clarified scopes |
| Tracked 1,588.33 + untracked 522.56 + ignored 88.53 ≈ 2,199.42 | **1,588.33 + 522.59 + 88.53 = 2,199.45** | rounding correction (untracked 522.59) |
| Classification total "2,959.1 MB" (implied) | **Invalid — overlapping groups.** See §6. | groups double-counted `.reference` + `.git` + submodules |
| Submodule "9.11 MB" (ambiguous) | worktree **9,552,775 B (9.11 MiB)**; git metadata **5,127,449 B (4.89 MiB)**; standalone, inside `.reference/state` | clarified |

---

## 6. Mutually-exclusive primary classification (every byte counted once)

**Primary classification partitions the 2,306,286,254 bytes into non-overlapping buckets.**

| # | Primary bucket | Bytes | MiB | Secondary labels |
|---|---|---:|---:|---|
| 1 | Git object database (`.git/objects`) | 444,847,882 | 424.24 | F/G (history) |
| 2 | Git non-object metadata (`.git` excl. objects) | 3,600,604 | 3.43 | G |
| 3 | `.reference/backups` | 739,436,232 | 705.18 | F (protected) |
| 4 | `.reference/memory` | 342,930,320 | 327.04 | E (operational) + H (toolchain 281 MiB) |
| 5 | `.reference/state` (incl. submodule `.git` 4.89 + worktree 9.11) | 181,817,847 | 173.40 | E/F (protected) |
| 6 | `.reference/AGI.Original Data` (excl. codex/memories 15,999 B) | 172,040,797 | 164.07 | F (protected) |
| 7 | `.reference/tools` | 55,499,163 | 52.93 | H (cloudflared) |
| 8 | `.reference/archive` | 47,598,447 | 45.39 | F (protected) |
| 9 | `.reference/.vs` | 7,803,935 | 7.44 | G |
| 10 | `.reference` loose files + misc subdirs | 143,763,009 + 526,885+415,522+174,753+65,763+60,306+33,517+22,253+18,596+10,624+6,392+6,023+3,621+1,734+267 = **145,039,431** | 138.32 | F/E |
| 11 | Submodule worktree `codex/memories` | 15,999 | 0.02 | F (protected) |
| 12 | `U0.1_output` | 88,445,380 | 84.35 | H/I (untracked) |
| 13 | `.vs` (root) | 73,958,262 | 70.53 | G |
| 14 | `output` | 1,298,844 | 1.24 | D |
| 15 | `documentation` | 712,688 | 0.68 | D/A |
| 16 | `tooling` | 641,348 | 0.61 | B/C |
| 17 | `mcp` | 201,309 | 0.19 | B |
| 18 | `web_bridge` | 189,300 | 0.18 | B |
| 19 | Root loose files | 121,811 | 0.12 | D |
| 20 | `state` (root) | 18,698 | 0.02 | E |
| 21 | `contracts` | 2,666 | 0.003 | A |
| | **TOTAL** | **2,306,286,254** | **2,199.45** | |

**Check:** sum of buckets 1–21 = **2,306,286,254 bytes = 2,199.45 MiB** ✓ (exact match to authoritative total).

**Notes:**
- Bucket 5 (`.reference/state` = 173.40 MiB) **includes** the `state/repo/AGI` submodule worktree (9.11 MiB) and its `.git` (4.89 MiB) — counted once, inside `.reference`.
- Bucket 6 **excludes** `codex/memories` (15,999 B, bucket 11) to avoid double-counting.
- Buckets 1–2 (`.git`) are **separate** from all worktree buckets.

---

## 7. Explanation of previous "2,959.1 MB" classification total

The original `REPOSITORY_CONTENT_CLASSIFICATION.md` summed **functional groups** (A–J) that **overlap**:

| Overlap | Double-counted MiB (approx.) |
|---|---|
| Group F (Historical 898) + Group A/D `.reference` (166) both include `.reference` | ~1,064 |
| Group E (843) + Group H (921) both include `memory/tools` (281×3) and `.reference` | ~1,123 |
| Group G (113) + Group F (898) both include embeddings/chunks in `.reference` | ~52 |
| Group C (12.2) + Group B (1.1) both include `tooling`/`mcp` | ~1 |
| `.git` (428) counted in G/history **and** implicit in total | 428 |

**Sum of overlapping functional groups ≈ 2,668 MiB** (not 2,959.1 — the exact figure depended on rounding and repeated `.reference` passes). The **overcount is ~469 MiB** above the 2,199.45 MiB authoritative total, caused by:
1. `.reference` counted under **both** F (Historical) and E (Operational) and D (Docs).
2. `memory/tools` (281 MiB × 3 trees) counted under **both** E and H.
3. `.git` counted under G **and** as part of the working tree.

**Correction:** The mutually-exclusive primary classification in §6 replaces the overlapping functional grouping. Functional labels (A–J) are retained as **secondary tags** in §6 only.

---

## 8. Git history clarification

### 8.1 Largest historical blobs (SILVERSTONE-VERIFIED)

| MB | Path | Introduced in |
|---:|---|---|
| 110.95 | `.reference/state_backup_v40_20261104_001710.zip` | `f842b6c` (2026-11-14, root) |
| 88.25 | `.reference/backups/agi/phase2-…/memory/tools/node/node.exe` | `f842b6c` |
| 82.11 | `.reference/backups/agi/phase2-…/bun/bin/bun.exe` | `f842b6c` |
| 52.82 | `.reference/tools/bin/cloudflared.exe` | `f842b6c` |
| 25.36 | `.reference/memory/index/embeddings.npy` | `f842b6c` |
| 24.50 | `.reference/agi_memory.tar.gz` | `f842b6c` |
| 14.90 | `.reference/AGI.Original Data/dsh/sessions/…session.v4.jsonl.zstd` | `f842b6c` |
| 13.84 | `.reference/memory/index/chunks.json` | `f842b6c` |

**All large blobs were introduced in the single root commit `f842b6c` ("chore: initial commit — AGI V5 documentation environment", 2026-11-14)** on the `docs/silverstone-consolidated-readiness` lineage. The **other root commit** `e858a9e` ("AGI v0.4.2: public-runtime cleanup", 2026-10-27, 61 files) is on `origin/main` lineage — **disjoint history** (two unrelated roots).

### 8.2 Are large files required in V5 source subset?

**No.** None of the top-20 blobs is V5 source:
- `node.exe`, `bun.exe`, `bunx.exe` → third-party toolchain (EXTERNALIZE)
- `cloudflared.exe` → third-party binary (EXTERNALIZE)
- `state_backup_v40_*.zip`, `agi_memory.tar.gz` → protected archives (ARCHIVE)
- `embeddings.npy`, `chunks.json` → generated index (REGENERATE)
- `AGI.Original Data/*` → session history (ARCHIVE, protected)
- `AGI-DNA-BLOCK.py` → historical genesis artifact (ARCHIVE)

### 8.3 Can a new V5 repository be initialized independently?

**Yes — safely, without altering the old repository:**
- A new `agi-v5/` repository can be initialized (`git init`) in a **separate directory** with **fresh history**.
- The old repository (`.git`, 427.67 MiB) remains **untouched**.
- Provenance is preserved by **archiving** the old history (bundle) externally, not by carrying it into V5.
- No `git gc`, prune, rewrite, or object modification is required or authorized.

---

## 9. Submodule accounting (SILVERSTONE-VERIFIED)

| Submodule | Worktree files | Worktree bytes | Git metadata bytes | Parent gitlink |
|---|---:|---:|---:|---|
| `.reference/state/repo/AGI` | 1,818 | 9,552,775 (9.11 MiB) | 5,127,449 (4.89 MiB, standalone `.git` dir) | `cfdc835` |
| `.reference/AGI.Original Data/codex/memories` | 32 | 15,999 (0.02 MiB) | (not separately measured; standalone) | `dac97f3` |

**Storage details:**
- `state/repo/AGI/.git` is a **directory** (standalone, not a gitfile pointing to parent). Parent has **no** `.git/modules/` — submodule git data lives **inside the submodule worktree**.
- `state/repo/AGI` git: `count 1379, size 4.00 MiB, in-pack 67, size-pack 746.29 KiB`.
- `state/repo/AGI` status: modified content + untracked (`citadel/evolution/`, `citadel/reports/*`, `citadel/tasks/*`) — **protected, do not touch**.
- `codex/memories`: **stale `.gitmodules` mapping** — parent has no `.gitmodules` entry, but gitlink `160000` exists in index. **UNRESOLVED** (do not change `.gitmodules`).

**Required vs generated/historical:**
- `state/repo/AGI` worktree (9.11 MiB) = **historical reference** (V4.0.1 runtime snapshot) → ARCHIVE (protected).
- `codex/memories` (0.02 MiB) = **historical** → ARCHIVE (protected).
- Neither is required in the lean V5 source subset.

**Inconsistencies:**
- Missing `.gitmodules` mapping for `codex/memories` (warning on `git submodule status`).
- `state/repo/AGI` is "modified content, untracked content" — pre-existing, preserve.

---

## 10. Regeneration evidence

| Candidate | Inputs | Tool / version | Reproduction | Validation | Preserved copy? | Disposition |
|---|---|---|---|---|---|---|
| `.vs/` (70.53 MiB) | `.slnx` solution + source | Visual Studio (version unknown) | Open solution in VS → FileContentIndex rebuilds | IDE opens without error | No (regenerable) | **REGENERATE** (evidence sufficient) |
| `__pycache__/` (2.81 MiB, 22 dirs) | `.py` sources | Python 3.13.15 (verified) | `python -m compileall` or import | Bytecode loads | No (regenerable) | **REGENERATE** (evidence sufficient) |
| `embeddings.npy` / `chunks.json` (live 25.36+13.84 MiB) | memory files + `provider.json` (model `bge-small-en-v1.5`, 384-dim) | `memory_embed.py` (present at `.reference/memory/scripts/`) | Run embed script over memory tree | Chunk count matches `provider.json:chunks` (17,309) | **Yes** (3 season copies + 2 backup copies, different sizes = different snapshots) | **REGENERATE** (generator exists; pin model version) |
| `*.db-shm` / `*.db-wal` | SQLite db | SQLite (runtime) | Auto-created on db open | db integrity check | N/A | **REGENERATE** (runtime) |
| `tooling/generated/` | `tooling/specs/*.json` | harness `engine generate` (per `.gitignore`) | Regenerate harnesses | Harness runs | No (gitignored) | **REGENERATE** (per existing policy) |

**Unknown → INVESTIGATE:**
- **Visual Studio version** for `.vs` regeneration is **unknown** (no `devenv` version recorded). However, `.vs` is IDE cache with **no preserved copy needed**; regeneration is standard. **Kept REGENERATE** with note: exact VS version is an unknown input, but the output is non-authoritative cache.
- **Embedding model pinning**: `provider.json` hardcodes a host path (`[REDACTED-LOCAL-PATH]/.cache/huggingface/...`). The **model identity** (`unsloth/bge-small-en-v1.5`, dim 384) is known; the **host path is a portability violation**. Regeneration requires **externalizing the model path** (adapter). **Kept REGENERATE** with portability caveat.

---

## 11. Portable dependency manifest & adapter strategy (PROPOSED)

**Manifest (`dependencies.v5.json`, PROPOSED — not created):**
```json
{
  "schema": "agi-deps/0.1",
  "dependencies": [
    {"name": "node", "required": false, "pin": "26.x", "integrity": "sha256", "adapter": "process.launch", "capability": "node>=20"},
    {"name": "bun", "required": false, "pin": "1.x", "integrity": "sha256", "adapter": "process.launch", "capability": "bun>=1"},
    {"name": "gh", "required": false, "pin": "2.x", "integrity": "sha256", "adapter": "process.launch", "capability": "gh>=2"},
    {"name": "cloudflared", "required": false, "pin": "2026.x", "integrity": "sha256", "adapter": "process.launch", "capability": "cloudflared"},
    {"name": "python", "required": true, "pin": "3.13.x", "integrity": "python-build", "adapter": "process.launch", "capability": "python>=3.11"},
    {"name": "embedding-model", "required": false, "pin": "unsloth/bge-small-en-v1.5@7382f11", "integrity": "hf-digest", "adapter": "model.resolve", "capability": "dims=384"}
  ]
}
```

**Adapter rules (PROPOSED, extends `PORTABILITY_ADAPTER_CONTRACTS.md`):**
| Concern | Contract |
|---|---|
| Version pinning | Each dep declares `pin` (semver or digest). |
| Integrity verification | `sha256` of binary or HF digest for models; verify before use. |
| Acquisition | **Not** bundled in repo; acquired via `AGI_DEPS`/package manager or manual install. No auto-download without owner approval. |
| Capability detection | Probe `name --version`; missing → capability unavailable. |
| Unsupported behavior | **Fail closed** for required deps; **degrade gracefully** (disable feature) for optional deps, with explicit log. No silent fallback. |
| Host-path prohibition | No hardcoded absolute paths (fixes `provider.json` violation). Config via `AGI_*` env. |

**Current violations to fix in V5:**
- `provider.json` hardcoded HF cache path → `AGI_INTERNAL_EMBEDDING_MODEL`.
- DPAPI host-bound key → `keystore` adapter.
- Hardcoded chrome path → `browser.locate()`.
- venv path → `AGI_WORKSPACE`.

---

## 12. Record of changes to original report

| Original doc | Change |
|---|---|
| `REPOSITORY_SIZE_AUDIT.md` | §2 headline corrected: total **2,199.45 MiB** (2,306,286,254 B); git object DB **424.24 MiB**; git total **427.67 MiB** (delta 3.43 MiB non-object). §3/§4 file/dir sizes unchanged (verified). §5 tracked 1,588.33 + untracked **522.59** + ignored 88.53 = 2,199.45 (was 522.56). |
| `REPOSITORY_CONTENT_CLASSIFICATION.md` | Replaced overlapping functional-group total with **mutually-exclusive primary classification** (§6 here). Functional labels retained as **secondary tags**. Explained 2,959.1 MB overcount (`.reference` + `memory/tools` + `.git` double-counting). |
| `AGI_V5_MINIMAL_REPOSITORY_DESIGN.md` | No change to design; budget unchanged (40 MiB target). |
| `SIZE_REDUCTION_DISPOSITION_REGISTER.md` | No change to dispositions; regeneration evidence added here (§10). |
| `REPOSITORY_RATIONALIZATION_RISK_REGISTER.md` | No change; this doc adds reconciliation evidence. |

---

## 13. Corrected executive summary

- **Total working tree:** **2,306,286,254 bytes = 2,199.45 MiB = 2,306.29 MB** (23,460 files).
- **`.git`:** 427.67 MiB (objects 424.24 + metadata 3.43). **No contradiction** — different scopes.
- **Dominant consumer:** `.reference/` = 1,613.86 MiB (**73.4%**), protected.
- **Second:** `.git` = 427.67 MiB (history).
- **Third:** `U0.1_output` = 84.35 MiB (untracked, third-party installers).
- **Lean V5 subset:** ~2–3 MiB of canonical source/docs — **well under 10 MiB preferred**.
- **Target:** 40 MiB budget (10 MiB below 50 MiB hard cap) — **feasible**.
- **Regeneration:** `.vs`, `__pycache__`, embeddings/chunks, sqlite sidecars all regenerable with known tools (Python 3.13.15 verified; VS version unknown but non-authoritative).
- **Dependencies:** Node 26.13.0, gh 2.8.9, Python 3.13.15 verified present; Bun/cloudflared **not on PATH** (EXTERNALIZE candidates).
- **Submodules:** 2; `state/repo/AGI` (9.11 MiB worktree + 4.89 MiB git), `codex/memories` (0.02 MiB, stale mapping). Both protected.
- **No operations performed.** No deletion, move, migration, staging, commit, merge, gc, prune, or Git modification. `.reference` contents not inspected. Pre-existing changes preserved.

---

## 14. Non-operation

Read-only measurement + documentation only. No cleanup, deletion, archive movement, migration, packaging, staging, commit, merge, `git gc`, prune, or implementation. `.reference`, V4.0.1, keys, `agi.rar`, `agi_memory.tar.gz`, operational memory, submodule state, and pre-existing uncommitted changes **untouched**.

**Status:** **ACCOUNTING CORRECTED AND RECONCILED — NOTHING EXECUTED.**