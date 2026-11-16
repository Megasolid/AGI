# AGI REPOSITORY CONTENT CLASSIFICATION

**Status:** PROPOSED (classification only) — **no disposition executed.**
**Labels:** SILVERSTONE-VERIFIED (sizes/paths) · PROPOSED (class/disposition). Protected items → **no disposition change**.
**Units:** 1 MiB = 1,048,576 bytes.
**Correction:** Functional groups A–J below **overlap** (`.reference` spans A/D/E/F; `memory/tools` spans E/H; `.git` spans G/history). For a **mutually-exclusive partition where every byte is counted once**, use the **primary classification** in `REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md` §6. Groups A–J here are retained as **secondary functional labels**.

**Groups:** A Canonical architecture/contracts · B Essential V5 source · C Tests/conformance · D Documentation/research · E Operational runtime/local state · F Historical references/immutable archives · G Generated artifacts/caches · H Third-party deps/executables · I Build/packaging outputs · J Unknown.

**Dispositions:** KEEP · ADAPT · REGENERATE · EXTERNALIZE · ARCHIVE · INVESTIGATE · RETIRE CANDIDATE.

---

## Group A — Canonical AGI architecture & contracts
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `documentation/workspace/AGI_U0_DOMAIN_RESPONSIBILITY_AND_INTERFACE_DESIGN.md` | <0.01 MB | U0 responsibility/interface baseline | OWNER-ACCEPTED baseline | **Essential** | **KEEP** |
| `documentation/workspace/AGI_U0_SECURITY_AUTHORIZATION_AND_TRUST_CONTRACTS.md` | <0.01 MB | U0 security/auth/trust (PROPOSED) | PROPOSED | **Essential** | **KEEP** |
| `documentation/workspace/AKMS_CONTRACT.md` + `SSL_CONTRACT.md` + integration/lifecycle/security/traceability/decisions (7 files) | ~0.1 MB | D1/D2 detailed contracts | PROPOSED | **Essential** | **KEEP** |
| `contracts/` (SSL_PROTOCOL_V1, D02_POLICY_ENFORCEMENT) | 0.003 MB | early contracts | ESTABLISHED | Supporting | **KEEP** |
| `.reference/contracts`, `.reference/core`, `.reference/runtime` | 0.10 MB | historical contract/core snapshots | FROZEN reference | Reference | **ARCHIVE (protected)** |
| **Total A** | **~0.2 MB** | | | | |

## Group B — Essential V5 source & implementation
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `tooling/` (specs, llm_harness_engine, conference_coordinator) | 0.61 MB | harness engine + specs | source | **Essential** | **KEEP / ADAPT** |
| `web_bridge/` (bridge.py, adapter.js, config.json, tests) | 0.18 MB | web bridge | source (partial) | Supporting | **KEEP / ADAPT** |
| `mcp/` (kilo-wrapper, codex-wrapper, verification-tools) | 0.19 MB | MCP adapters | source | Adapters | **ADAPT** |
| `harness.py`, `test_kilo_*.py` | 0.02 MB | harness + tests | source | Supporting | **KEEP** |
| `.reference/state/repo/AGI` (submodule) | 9.11 MB | V4 runtime snapshot | protected submodule | Reference | **ARCHIVE (do not touch)** |
| **Total B** | **~1.1 MB** (excluding protected submodule) | | | | |

## Group C — Tests & conformance assets
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `tooling/specs/*.json` (8 specs) | <0.01 MB | harness specs | source | **Essential** | **KEEP** |
| `web_bridge/test_contract.py`, `test_d02_live.py`, `selftest.py` | <0.01 MB | tests | source | **Essential** | **KEEP** |
| `.reference/tests` | 0.40 MB | historical tests | FROZEN | Reference | **ARCHIVE (protected)** |
| `U0.1_output/AGI_repo` (includes tests) | 11.73 MB | working copy | untracked | INVESTIGATE | **INVESTIGATE** |
| **Total C** | **~12.2 MB** | | | | |

## Group D — Documentation & research
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `documentation/workspace/**` (~100 files, G2.x, G2.5, G2.6, G3.x, Silverstone) | 0.68 MB | full investigation record | VERIFIED | **Essential knowledge** | **KEEP** |
| `output/` (SILVERSTONE_G3* reports, 40 md + 1 json) | 1.24 MB | evidence reports | VERIFIED | High (review) | **KEEP** |
| `*.md` at root (README, PROJECT_CONTEXT, AGI_DOCUMENT_*, U0_2_*) | 0.10 MB | project docs | VERIFIED | Supporting | **KEEP** |
| `.reference/docs`, `.reference/AGI.Original Data` | 164.15 MB | historical sessions | FROZEN/protected | Reference | **ARCHIVE (protected)** |
| **Total D** | **~166 MB** (dominated by protected) | | | | |

## Group E — Operational runtime & local state
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `state/` (root) | 0.02 MB | local runtime state | operational | ADAPT | **KEEP / ADAPT** |
| `.reference/memory` (operational memory authority + tools + index) | 327.04 MB | **live memory + 281 MB toolchain** | operational authority | **Externalize toolchain** | **EXTERNALIZE (toolchain) / KEEP (memory, protected)** |
| `.reference/state` (entelechy, family, attention, repo, genesis, agi5…) | 173.40 MB | season/runtime state | operational | ADAPT | **EXTERNALIZE / ARCHIVE (protected)** |
| `[REDACTED-LOCAL-PATH]/agi_runtime/memory` (outside repo) | 342.9 MB | interim operational authority (per G2) | operational | **EXTERNALIZE** | **EXTERNALIZE** |
| **Total E** | **~843 MB** | | | | |

## Group F — Historical references & immutable archives
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `.reference/backups/` (phase2 + stable-gen3.5 + gen2) | 705.18 MB | season backups | protected | Reference | **ARCHIVE (protected, no change)** |
| `.reference/state_backup_v40_20261104_001710.zip` | 110.95 MB | full V4 state backup | protected | Reference | **ARCHIVE (protected)** |
| `.reference/agi_memory.tar.gz` | 24.50 MB | memory archive | protected (G25-02b) | Reference | **ARCHIVE (protected)** |
| `.reference/archive/` | 45.39 MB | core bundles, retired stages | protected | Reference | **ARCHIVE (protected)** |
| `.reference/state/archive`, `state/release` zips | ~12 MB | release/beta archives | protected | Reference | **ARCHIVE (protected)** |
| **Total F** | **~898 MB** | | | | |

## Group G — Generated artifacts & caches
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `.vs/` | 70.53 MB | VS/IDE FileContentIndex | generated | none | **REGENERATE** |
| `__pycache__/` (22 dirs) | 2.81 MB | Python bytecode | generated | none | **REGENERATE** |
| `.reference/memory/index/embeddings.npy` + `chunks.json` | 39.20 MB | RAG index | generated (reproducible) | ADAPT | **REGENERATE / ADAPT** |
| `*.db-shm` / `*.db-wal` | <0.01 MB | SQLite sidecars | generated | none | **REGENERATE** |
| **Total G** | **~113 MB** | | | | |

## Group H — Third-party dependencies & executables
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `.reference/memory/tools/node/` (node.exe ×3 + bun ×6) | ~800 MB | Node/Bun runtime | third-party | **EXTERNALIZE** | **EXTERNALIZE / ADAPT** |
| `.reference/tools/bin/cloudflared.exe` | 52.82 MB | tunnel binary | third-party | ADAPT | **EXTERNALIZE / ADAPT** |
| `U0.1_output/gh_portable/bin/gh.exe` + `gh.msi` + `gh.zip` | 68 MB | GitHub CLI | third-party | none for V5 | **EXTERNALIZE** |
| `.reference/archive/bundle_stage/.../chrome-mcp` | (within archive) | MCP bundle | third-party | ADAPT | **ADAPT** |
| **Total H** | **~921 MB** | | | | |

## Group I — Build & packaging outputs
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `U0.1_output/u0-1-curated-intake-handoff.tar.gz` | 0.39 MB | handoff bundle | generated | none | **ARCHIVE** |
| `U0.1_output/*.json` (INCLUDED/EXCLUSION manifests) | 4.22 MB | intake manifests | generated | INVESTIGATE | **ARCHIVE** |
| `.reference/state/cleanroom/exports/*.zip` | ~1 MB | cleanroom exports | generated | none | **ARCHIVE** |
| **Total I** | **~5.6 MB** | | | | |

## Group J — Unknown / unclassified
| Path | Size | Purpose | Authority | V5 necessity | Disposition |
|---|---:|---|---|---|---|
| `intake/` (empty dir) | 0 | unknown (empty) | UNKNOWN | none | **INVESTIGATE** |
| `UsersDAppDataLocalTempdsh-asar-extract/` (empty) | 0 | stray temp | UNKNOWN | none | **INVESTIGATE** |
| `codex-mcp` deletion (staged? no — ` D` in status) | 0 | deleted file | pre-existing | none | **INVESTIGATE (preserve)** |
| **Total J** | **~0 MB** | | | | |

---

## Storage summary by group (overlapping; **not** a partition)

> **Do not sum these.** Groups overlap; the authoritative mutually-exclusive partition is in `REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md` §6 (total **2,199.45 MiB**).

| Group | Approx MiB (incl. protected) | Lean-V5 relevance | Overlaps with |
|---|---:|---|---|
| A Canonical | 0.2 | **KEEP** | D (docs) |
| B V5 source | 1.1 (+9.1 protected submodule) | **KEEP/ADAPT** | C (tooling) |
| C Tests | 12.2 | **KEEP** (lean: <0.1) | B |
| D Docs/research | 166 (0.7 lean + 164 protected) | **KEEP lean; ARCHIVE protected** | A, F (`.reference`) |
| E Operational | 843 | **EXTERNALIZE toolchain; KEEP/ARCHIVE memory** | F, H (`.reference`) |
| F Historical | 898 | **ARCHIVE (protected)** | D, E, G (`.reference`) |
| G Generated | 113 | **REGENERATE** | F, `.git` |
| H Third-party | 921 | **EXTERNALIZE** | E (`memory/tools`) |
| I Build outputs | 5.6 | **ARCHIVE** | C, U0.1 |
| J Unknown | ~0 | **INVESTIGATE** | — |

**Why the previous 2,959.1 MiB total was wrong:** it summed overlapping groups. `.reference` (1,613.86 MiB) was counted under **F + E + D**; `memory/tools` (~281 MiB × 3) under **E + H**; `.git` (427.67) under **G + history**. Overcount ≈ 469 MiB above the 2,199.45 MiB authoritative total. See reconciliation doc §7.

**Lean V5 subset:** A + B(lean) + C(lean) + D(lean) + `tooling/` + `skills/`(text) ≈ **2–3 MiB** — well under 10 MiB preferred.

**No disposition executed. Protected material (`.reference`, V4.0.1, keys, `agi.rar`, `agi_memory.tar.gz`, operational memory) → no change.**