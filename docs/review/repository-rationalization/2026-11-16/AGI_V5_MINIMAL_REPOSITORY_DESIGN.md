# AGI V5 MINIMAL REPOSITORY DESIGN

**Status:** PROPOSED (design only) — **no files created, moved, or deleted.**
**Labels:** PROPOSED · OWNER-APPROVED (U0 baseline) · NOT ESTABLISHED (implementation).
**Principle:** Design the lean V5 workspace **independently** of the current historical layout. Preserve provenance and recoverability by **externalizing** (not deleting) history, operational data, and toolchain.

---

## 1. Design goals

1. **Under 10 MB preferred; hard max 50 MB** for the lean repository (excluding `.git` history, external data, and third-party binaries).
2. **Support D0–D7**, versioned contracts/schemas, tests, portable skills, optional adapters.
3. **No mandatory OS / model provider / editor / IDE / shell / DB / vector store / agent framework.**
4. **Separate:** canonical architecture · V5 implementation · optional adapters · tests · generated artifacts · external operational data · historical references.
5. **Do not sacrifice provenance, recoverability, or architectural knowledge.** History is **externalized**, not destroyed.

---

## 2. Proposed V5 directory structure

```
agi-v5/
├── AGENTS.md / README.md / PROJECT_CONTEXT.md      # entry docs
├── contracts/                                       # canonical, versioned, immutable
│   ├── d0/                                          # constitution, DNA refs, governance
│   ├── d1-akms/                                     # akms/0.1 schema + interface
│   ├── d2-ssl/                                      # ssl/0.2 envelope + lifecycle
│   ├── d3-minds/
│   ├── d4-operator/                                 # operator + H0 contracts
│   ├── d5-capabilities/
│   ├── d6-evolution/
│   ├── d7-infra/
│   ├── shared/                                      # JCS, trust-record, approval contract
│   └── schemas/                                     # JSON Schema, examples
├── src/                                             # V5 implementation (thin, adapter-based)
│   ├── d0_governance/
│   ├── d1_akms/
│   ├── d2_ssl/
│   ├── d3_minds/
│   ├── d4_operator/
│   ├── d5_capabilities/
│   ├── d6_evolution/
│   ├── d7_infra/
│   └── adapters/                                    # platform, model, storage, transport, agent
│       ├── platform/  model/  storage/  transport/  agent/
├── skills/                                          # portable skills (optional adapters)
│   ├── portable/
│   └── optional/
├── tests/                                           # unit + conformance + fixtures
│   ├── unit/
│   ├── conformance/                                 # C-beta1..24 equivalents
│   ├── fixtures/                                    # small, synthetic
│   └── negative/                                    # fail-closed cases
├── tooling/                                         # build/dev metadata only (no binaries)
│   ├── specs/
│   └── scripts/
├── docs/                                            # architecture + research (curated)
│   ├── architecture/
│   ├── decisions/                                   # owner decision register
│   └── research/                                    # curated, not raw sessions
├── generated/                                       # .gitignored; reproducible
│   └── (index/, cache/, build/)
└── .gitignore
```

**External (outside the lean repo, referenced by config):**
- `AGI_EVIDENCE_ROOT` (restricted evidence)
- Operational memory (interim authority)
- RAG index + embeddings (regenerable; see `REPOSITORY_SIZE_ACCOUNTING_AND_RECONCILIATION.md` §10)
- Node/Bun runtime, cloudflared, gh CLI (toolchain; dependency manifest + adapter strategy in reconciliation §11)
- Historical archive (`.reference`, `agi.rar`, `agi_memory.tar.gz`, season backups)

---

## 3. Size budget (PROPOSED; target < 50 MB, preferred < 10 MB)

| Group | Path | Target | Rationale |
|---|---|---:|---|
| Constitution & contracts | `contracts/` + `docs/architecture/` | **2 MB** | versioned JSON/Schemas + U0 docs; no binaries |
| Core V5 source | `src/` (all domains + adapters) | **8 MB** | thin adapters; heavy logic behind interfaces |
| Tests & fixtures | `tests/` | **8 MB** | unit + conformance + small synthetic fixtures |
| Documentation & research | `docs/` (curated) | **5 MB** | decisions, architecture, selected evidence; **not** raw 164 MB sessions |
| Portable skills & adapters | `skills/` | **5 MB** | text-based skills; binaries externalized |
| Tooling & build metadata | `tooling/` | **2 MB** | specs + scripts; no `node.exe`/`bun.exe` |
| Allowance & growth | — | **10 MB** | reserve |
| **Total** | | **40 MB** | 10 MB below hard cap |

**Current lean-subset reality check:** today’s canonical A + lean B + lean C + lean D + `tooling/` + `skills/` (text) is **~3 MB** — **well under budget**. The 40 MB budget is generous and accommodates future V5 implementation growth.

**If essential implementation cannot fit:** report why (e.g., bundled model runtime). Do **not** manipulate measurements. A bundled LLM runtime would be **externalized** (model provider adapter), not committed.

---

## 4. What must remain external (PROPOSED)

| Item | Reason | Adapter / reference |
|---|---|---|
| Operational memory (342.9 MB) | runtime authority; not source | `storage.root()` adapter + `AGI_WORKSPACE` |
| RAG embeddings/chunks (39 MB) | generated, large | regenerate via `model.resolve()` |
| Node/Bun (800 MB) | third-party toolchain | `process.launch()` adapter; not committed |
| cloudflared (53 MB) | third-party binary | external tool |
| gh CLI (68 MB) | third-party installer | external tool |
| `.reference/` (1.6 GB) | protected historical reference | **unchanged, external to lean repo** |
| `agi.rar` (462 MB) | protected archive | preserved; pending L6 + separate retirement |
| `agi_memory.tar.gz` (24.5 MB) | protected archive | preserved (G25-02b unapproved) |
| V4.0.1 (`6a0fb79`) | rollback floor | preserved; not in lean repo |
| Keys / trust anchors / custody | protected | never committed |
| Season backups (705 MB) | historical | ARCHIVE (protected) |

---

## 5. What can be regenerated (PROPOSED)

| Artifact | Regeneration path |
|---|---|
| `.vs/` | IDE rebuild (ignored) |
| `__pycache__/` | Python import (ignored) |
| `embeddings.npy` / `chunks.json` | `memory_embed.py` / indexer (verified inputs) |
| `*.db-shm` / `*.db-wal` | SQLite runtime |
| `generated/` | build tooling |

---

## 6. What requires owner approval before any change

| Action | Approval |
|---|---|
| Moving/copying/deleting any `.reference` content | **Required** (protected) |
| Touching `agi.rar`, `agi_memory.tar.gz`, V4.0.1, keys, operational memory | **Required** (protected) |
| Externalizing toolchain (Node/Bun/cloudflared/gh) | **Required** |
| Creating lean repo / fresh history | **Required** |
| Any consolidation/RETIRE | **Required** (see disposition register) |
| Provisioning `AGI_EVIDENCE_ROOT` | **Required** |

---

## 7. Portability (invariant)

- No mandatory OS / model provider / editor / IDE / shell / DB / vector store / agent framework.
- Platform specifics behind **replaceable adapters** (`platform`, `model`, `storage`, `transport`, `agent`).
- **Capability negotiation** + **fail-closed on unsupported**.
- Config externalized (`AGI_*` env, not hardcoded paths).
- Known violations to avoid in V5 (VERIFIED in current stack): hardcoded HF cache path, DPAPI host-bound key, hardcoded chrome path, venv path.

---

## 8. Non-operation

Design only. No directory created, no file moved/copied/deleted, no Git operation, no implementation. Pre-existing uncommitted changes and protected material untouched.

**Status:** **PROPOSED V5 DESIGN — NOT ESTABLISHED.**