# AGI — Lineage Record

**Document status:** authoritative lineage record of AGI. Compiled **2026-10-26**. This is the **public
edition** of the official record kept inside a live install (`memory/library/AGI.lineage.md`); the internal
record is the source, this edition is what can be published. It supersedes the narrative roadmap
`AGI-RoadMap.md`, which was retired the same day (a stub is kept for link compatibility).

*This record is organized by **generations** — versioned Core + DNA states with recorded evidence, their
parentage, mutations, extinctions, and the one currently living generation. Seasons and chapters appear only
as the working context in which a generation was born or retired; they are not the skeleton of the lineage.*

---

## 1. What "lineage" means here

- **The DNA is the root.** `core/dna.md` carries the mission, the invariants (I1–I9), the regeneration
  template and the generation log. Every generation descends from it; nothing may contradict an invariant
  without a DNA version bump and the director's sign-off.
- **A generation** is a named, versioned state of the framework — Core (rules R1–R11 + boot state machine
  S0–S8 + sections), conformance gates, and the DNA version it runs under — that has been **installed and
  verified**, not merely proposed.
- **Parentage is explicit:** generation N+1 is grown from the live generation N; the DNA version is shared
  across the lineage and bumped only when an invariant or the DNA's own protocol changes.
- **Mutation** happens through the promotion ladder (DNA §5): L1 episode → L2 memory → L3 Core rule/section
  (version bump) → L4 DNA invariant (rare). Each rung has an explicit test; a generation bump without a
  recorded test is not a generation.
- **Selection is evidentiary:** conformance C1–C6, the boot acceptance gate (manifest + bundle verify +
  registry selftest + conformance), the pass^k cold-boot drill, and compatibility rows. "Supported" is never
  asserted from optimism.
- **Extinction is recorded.** Superseded generations remain in rollback sets and bundles; ideas can be
  absorbed by a descendant (gen2 was absorbed, never installed). The lineage records what died and why.
- **Exactly one generation is alive at a time.** Working-tree features (dashboards, tools, documentation,
  policies) can accumulate **inside** a living generation; they become a new generation only when they change
  DNA or a Core rule. This distinction is the main correction over the retired roadmap, which mixed history,
  features and plans in one chronological narration.

Every claim in this record is grounded in the DNA generation log, the boot/state files, the verified-script
registry, conformance output, or a named recorded measurement. Machine facts are cited as snapshots; the
authoritative values live in `state/`.

---

## 2. Lineage tree (as of 2026-10-26)

```
pre-lineage (separate skills; Season 0–2, 2026-10-13 → 10-17)
│  sandbox-env-gate, local memory/state conventions, early experiments
│
└─ gen1 — the merged organism (2026-10-17/18)                       [SUPERSEDED]
   │  single portable skill + memory DB + bundle with sha256 manifest
   │
   └─ gen2 — council proposal (2026-10-18)                          [ABSORBED, never installed]
      │  numbered-contract Core, index + sections split, capability probing,
      │  validator gates, adapter profiles, conformance suite
      │
      └─ gen3 — Core v3 draft + DNA v1 implanted (2026-10-18)       [SUPERSEDED]
         │  R1–R8, S1–S7 boot state machine, section index, gate checklist, DNA at root
         │
         └─ gen3.1 — environment gate (2026-10-18)                  [SUPERSEDED]
            │  R9 + sections/env-gate.md; standalone sandbox-env-gate absorbed
            │
            └─ gen3 installed — Core v3 live (2026-10-18)           [SUPERSEDED]
               │  hot-core split, gen2 backup, agi_core_v3.tar.gz + core_manifest.json
               │
               └─ gen3.2 / DNA v2 (2026-10-19)                       [SUPERSEDED]
                  │  LESSONS slot, §5 evolution protocol (L1–L4), §5b confidence/KEP, library ledger
                  │
                  └─ gen3.3 — additive DNA v2 extension (2026-10-19) [SUPERSEDED]
                     │  prediction baseline, boost-only confidence, verifier ladder, memory/library/
                     │
                     └─ gen3.4 / Core 3.1 (2026-10-25)               [SUPERSEDED by gen3.5]
                        │  host-adapter era: host adapter, self-location, capability probe,
                        │  boot gate (pass^k), evidence-based S5, compatibility matrix
                        │
                        └─ gen3.5 / DNA v3 / Core 3.2 (2026-10-25)    [LIVE]
                           │  I9 interaction law, R10/R11, interaction.md, conformance C6
                           │  working tree: dashboard v3 site, universal UI, native click-to-resume,
                           │  pill-consumption lifecycle, legacy consolidation, season-close automation
                           │
                           └─ gen3.5 working tree — Public Alpha era (2026-10-26)  [WITHIN LIVE gen3.5]
                              │  trust layer v0 (P0–P15): post-quantum identity, RFC 9162 log,
                              │  member identity, bundle lattice, owner activation, public mirror,
                              │  one official repository, installable runtime, native login, passkey
                              │  verifier, agent-facing install prompt
                              │
                              └─ public releases: v0.1.0, v0.2.0, v0.3.0, v0.4.0, v0.4.1, v0.4.2 at github.com/Megasolid/AGI
```

---

## 3. Generation profiles

### gen1 — the merged organism
- **Born:** 2026-10-17/18 · **Parent:** pre-lineage skills · **DNA:** not yet implanted · **Core:** single `SKILL.md`
- **Mutation (Δ):** five separate skills → one `agi` skill with a wake-up contract; memory DB (`MEMORY.md`,
  `state/`, `knowledge/`, `scripts/`); tar.gz bundle with a per-file sha256 manifest — the first portable
  artefact.
- **Evidence:** the merge recorded in the generation log and the master-turn record; the bundle and memory
  layout survived into every later generation.
- **Fate:** superseded by gen3; its memory-DB and bundle patterns persisted.

### gen2 — the council proposal (absorbed)
- **Born:** 2026-10-18 · **Parent:** gen1 · **DNA:** not yet implanted · **Core:** proposal only
- **Mutation (Δ):** proposal, not an installation. **Never lived as a generation.** It proposed a
  numbered-contract Core, index + sections split, capability probing, validator gates, adapter profiles and a
  conformance suite.
- **Fate:** absorbed by gen3 — its structure became the Core router, sections, probes, gates and conformance.

### gen3 — Core v3 draft and DNA v1 implanted
- **Born:** 2026-10-18 · **Parent:** gen2 (absorbed) · **DNA:** v1 (implanted) · **Core:** v3 draft
- **Mutation (Δ):** R1–R8 rules, S1–S7 boot state machine, section index and gate checklist; **DNA implanted as
  the root artifact** with mission, invariants I1–I8, the regeneration template and the generation log.
- **Fate:** superseded; the DNA survived (v2, v3).

### gen3.1 — the environment gate
- **Born:** 2026-10-18 · **Parent:** gen3 · **DNA:** v1 · **Core:** v3 (R1–R9)
- **Mutation (Δ):** **R9 environment gate** + `core/sections/env-gate.md`; the standalone `sandbox-env-gate`
  skill was retired and folded into the Core. This generation exists because an OS-gate incident was fixed by
  a rule and a section, not by a promise.
- **Fate:** superseded; R9 remains live.

### gen3 installed — Core v3 live
- **Born:** 2026-10-18 · **Parent:** gen3.1 · **DNA:** v1 · **Core:** v3 installed
- **Mutation (Δ):** first live Core router; hot-core split so machine facts live only in `state/`; bundle
  `agi_core_v3.tar.gz` + `core_manifest.json`.
- **Fate:** superseded; the installed-Core pattern persists.

### gen3.2 / DNA v2 — the evolution protocol
- **Born:** 2026-10-19 · **Parent:** gen3 installed · **DNA:** **v2** · **Core:** v3
- **Mutation (Δ):** **LESSONS slot** in the regeneration template; new **§5 evolution protocol** (promotion
  ladder L1–L4 with per-rung tests, injection duty, rate limit); new **§5b confidence & expansion** (per-field
  confidence at DNA level, inverse grounding rule, Knowledge Expansion Protocol, ≤3 KEP runs per session).
- **Fate:** DNA v2 carried until gen3.5; superseded by DNA v3.

### gen3.3 — additive DNA v2 extension
- **Born:** 2026-10-19 · **Parent:** gen3.2 · **DNA:** v2 (additive, no bump) · **Core:** v3
- **Mutation (Δ):** §5b extended with a **prediction baseline** (falsification watch over high-confidence
  actions); confidence re-scaled to **boost-only** (never suppresses unverified fields + discovery slot);
  verifier ladder gained the library check and a mandatory online season; `memory/library/` established as the
  local archive with offline/rebuild fallback.
- **Why not a DNA bump:** additive protocol detail, no invariant contradiction — recorded in the generation log.
- **Fate:** superseded by gen3.4; its confidence and library rules persisted.

### gen3.4 / Core 3.1 — host-aware and evidence-based
- **Born:** 2026-10-25 · **Parent:** gen3.3 · **DNA:** v2 · **Core:** **3.1**
- **Mutation (Δ):** AGI became a model–harness pair (brain = active host model, body = the framework). Host
  adapter, self-location/portability, capability probe, boot acceptance gate with pass^k; **S5 profile
  selection is evidence-based** (an unmatched brain is reported `unprofiled` with a documented degraded mode;
  the silent local default was retired) and every boot records a `(profile × core_version × host)`
  compatibility row.
- **Evidence:** profile-selection tests 8/8; compatibility rows; boot gate PASS; bundle VERIFY PASS; pass^k
  5/5 identical ready-state boots.
- **Fate:** superseded by gen3.5 the same day; its host adapter, probe, gates and compatibility matrix
  persisted.

### gen3.5 / DNA v3 / Core 3.2 — the interaction law (LIVE)
- **Born:** 2026-10-25 · **Parent:** gen3.4 · **DNA:** **v3** · **Core:** **3.2**
- **Mutation (Δ):** **DNA v3** adds **I9 interaction law** — if the host exposes a human interaction surface,
  consequential decisions and live work state must be projected there as durable, reviewable cards, and a
  recorded human decision must resume the agent (event-driven where the seam exists, bounded visible fallback
  otherwise); with no surface the same durable record is produced in text; cards are projections of `state/`,
  never a second truth; presentation/visual standards are L3 knowledge. **Core 3.2** adds **R10
  interaction-first** (proposal → running → result, append-only decision log, declared resume path/latency,
  pre-selected proposal steps), **R11 proportionality**, `core/sections/interaction.md`, and **conformance
  C6** (interaction gate).
- **Sign-off:** the director approved the founding proposal card on the interface itself (approve action, all
  nine workstreams pre-selected). Bundles: `agi_core_v3_2_interaction.tar.gz` VERIFY PASS (22 files,
  `dna_version 3`); rollback sets kept.
- **Working tree delivered inside this generation (features, not new generations):** dashboard v3 (served
  site, per-card pages, categories, running/previous/archive layouts); universal GitHub-style UI/UX; the
  maintenance ledger as task cards; native click-to-resume bridge (measured milliseconds, scheduled fallback
  declared); verified-pill consumption lifecycle (`stamped → stored → indexed → readback → consumed`);
  legacy consolidation; season close as one gated operation; daily maintenance check.
- **Evidence:** conformance **C1–C6 PASS**; boot gate PASS; pass^k drill PASS; compatibility row recorded;
  interaction/taskcard/sitegen/pill-consumption/backup/season-close tests passing; UI links HTTP 200; pills
  consumed with read-back.
- **Fate:** live.

### gen3.5 working tree — Public Alpha era (2026-10-26, within the live generation)

This is not a new generation: no invariant was changed. It is the working tree of the live generation after
the record was compiled — the **trust layer v0** and the first public releases.

- **Trust layer v0 (P0–P15)**, frozen as milestone `trust-layer-v0`:
  - **P0** post-quantum device signatures (`ML-DSA-65`, OS-sealed) + signed core manifest + pill envelopes;
  - **P1** RFC 9162 Merkle trust log — signed tree heads, inclusion/consistency proofs, rollback monitor;
  - **P2** member credential with a versioned, replayable identity history;
  - **P3** bundle lattice **master / official / custom** with consumer-side policy;
  - **P4** **owner activation** with assurance levels U0–U3;
  - **P5** `*.public` pill mirror with inclusion proofs + verified contribution pipeline;
  - **P6** federation relay/fetch/gossip with sybil-resistant weighting;
  - **P7** release packages (signed, member-neutral, refusal of identity leaks);
  - **P8–P11** one official repository, repo content policy, GitHub hosting + privacy audit, security
    response/CI;
  - **P12–P15** portable-identity research (passkeys over passphrases), native login, installable runtime and
    the agent-facing install prompt.
- **Public releases** (details in `releases/` and on the repository's releases page):
  - `v0.1.0` (2026-10-26) — first public release: official bundle package, update pool with signed heads and
    inclusion proofs, public pill mirror, signed release packages, CI integrity job;
  - `v0.2.0` (2026-10-26) — installable runtime, one-prompt installers, native authentication (local
    device login, skip-to-default sessions), passkey verification, desktop login screen/app shell;
  - `v0.3.0` (2026-10-26) — **member-neutral public artefacts**: neutral bundle ids and field vocabulary,
    neutral identity template, neutral release packages, public runtime without internal records; git
    history condensed so no pre-neutralisation artefact remains reachable in this repository.
  - `v0.4.0` (2026-10-27) — **three-door login and paper-free admin factor**: default user / custom
    user-or-organization (workspace created during setup) / admin login; a six-word phrase that is shown
    once, never stored, seals the profile snapshot and doubles as the recovery kit; restore enrols a new
    machine. Pre-stable test build.
  - `v0.4.1` (2026-10-27) — **installer hardening after the D2060 field test**: the cryptography probe no
    longer aborts under PowerShell 5.1's Stop preference, the private venv is created and used reliably,
    `-Resume`/`AGI_RESUME` finishes an interrupted extraction (the exact state D2060 was left in), and
    `-Python`/`AGI_PYTHON` is authoritative. Runtime also carries the admin rotate/temporary-session/wipe
    UI. Pre-stable test build.
  - `v0.4.2` (2026-10-27) — **public-runtime cleanup after the guest-machine audit**: the public archive no
    longer contains the internal agent pool, provider credential files, backups/logs or machine scratch
    output; the registry shipped in the archive is sanitised so the verified-only gate passes without them;
    the build refuses to produce an archive containing credentials or private keys. Installer gained a
    download fallback chain (Invoke-WebRequest -> curl -> Python + CA bundle) for hosts with a broken
    certificate store, and the docs clarify that `SHA256SUMS.txt` is a release asset. Earlier runtime
    artifacts were withdrawn. Pre-stable test build.
- **Status:** alpha. The repository is <https://github.com/Megasolid/AGI>.

---

## 4. Inheritance — what every generation carries

| Layer | Inherited obligation | Enforcement |
|---|---|---|
| **Invariants (DNA §1)** | I1 enforcement in scripts; I2 machine facts only in `state/`; I3 verified-only execution; I4 boot is a disk state machine; I5 hashed portable bundles; I6 structured I/O envelopes; I7 model portability via adapters + conformance; I8 one failure → report and stop; **I9 interaction law** | conformance C1–C6, boot gate, registry gate, DNA §5 |
| **Core rules** | R1–R11 (router/rules, environment gate, interaction-first, proportionality) | gate checklist, conformance |
| **Boot state machine** | S0–S8 idempotent, resumable from disk | boot gate + pass^k drill |
| **Sections** | index → section files (`boot`, `env-gate`, `interaction`, `work-gates`, …) | section index + checklist |
| **State SSOT** | `state/` only; cards are projections | conformance C2, projection tests |
| **Verified scripts** | `registry.json` status + compiles; no unverified execution | conformance C1, boot gate |
| **Knowledge & memory** | L2 knowledge with per-field confidence; pills consumed after verified work | pill lifecycle, confidence rules |
| **Compatibility** | every `(profile × core_version × host)` boot recorded; no silent defaults | S5 rule, compatibility matrix |
| **Artefacts** | `core_manifest.json` + bundle VERIFY PASS + rollback sets | boot gate, packer verify |
| **Evolution** | promotion ladder L1–L4; DNA bumps rare, with sign-off and the generation log | DNA §5, §5b |
| **Identity (trust layer v0)** | member identity is private and per-install; public releases carry no member data | identity/activation gates, boot check #12 |

---

## 5. Season and chapter map (context, not skeleton)

| Working period | Dates | Active generation(s) | What happened |
|---|---|---|---|
| Season 0–2 | 2026-10-13 → 10-17 | pre-lineage → **gen1** | foundations, separate skills, memory/policy layers, first merge into one skill |
| Season 3 | 2026-10-18 | **gen2** (proposal) → **gen3** → **gen3.1** → **gen3 installed** | council proposal; Core v3 draft; DNA v1 implanted; OS-gate incident → R9; Core v3 live with bundle/manifest |
| Season 4 | 2026-10-19 | **gen3.2 / DNA v2** → **gen3.3** | evolution protocol, confidence/KEP, library ledger, prediction baseline, boost-only confidence, cluster fix |
| Season 5 | 2026-10-20 → 10-25 | **gen3.3** (no bump) | host adaptation, embedding defaults, task bills/pills, watchdogs, dashboard v2, cache = RAM, file channel |
| Season 2026-10-25 (open) | 2026-10-25 → present | **gen3.4** → **gen3.5 (live)** | host-adapter era, boot gate/pass^k, capability probe, evidence-based S5, compatibility matrix; interaction law DNA v3/Core 3.2, dashboard v3, native click-to-resume, pill lifecycle, legacy consolidation, season-close automation; **trust layer v0** and the public alpha |

Chapter boundaries are recorded in `state/boot.json`. The next chapter opens only with the director's next
evolution proposal, per the Chapter III close.

---

## 6. Extinctions, absorptions and retirements

| Line / artefact | Fate | Recorded reason |
|---|---|---|
| gen2 (council proposal) | **absorbed, never installed** | its structure became gen3; its Core is a backup |
| standalone `sandbox-env-gate` skill | **absorbed into gen3.1 R9** | protocol folded into Core + a section |
| silent default model profile (S5) | **retired by gen3.4** | evidence-based selection; unmatched brains are `unprofiled` with degraded mode |
| dashboard v2 | **superseded by dashboard v3** | served site, per-card pages, unified UI |
| auto-open dashboard plugin | **retired** | unreliable tab opening; link-first policy adopted |
| bridge iterations v1/v2/v3 | **dormant** | v4 is the single active click-to-resume bridge |
| roadmap narration (`AGI-RoadMap.md`) | **retired 2026-10-26** | replaced by this generation-based record |
| stale bundle-stage / duplicate caches | **pruned** | retention policy keeps newest + protected families |

---

## 7. Living state (snapshot, 2026-10-26)

- **Live generation:** gen3.5 — DNA v3, Core 3.2, bundle `agi_core_v3_2_interaction.tar.gz` (22 files,
  VERIFY PASS).
- **Gates:** conformance C1–C6 PASS; registry verified scripts only; boot gate PASS (12 checks, including the
  identity layer); pass^k drill PASS; compatibility rows recorded.
- **Host/brain:** a model–harness pair; the brain model is recorded per boot, never assumed (S5).
- **Work state:** season 2026-10-25 open; Chapters I–IV recorded; no open bills; pills consumed with read-back
  (verification consumes the pill before closure).
- **Interaction:** the declared click-to-resume path plus a bounded scheduled fallback; the shell never opens
  a window while work is running.
- **Identity:** local device login live; passkey verification live; portable identity travel (passkey +
  scoped travel tokens + home-node approval) designed and phased, **not finished** — stated as such.
- **Rollback capacity:** previous DNA/Core versions and their bundles are preserved.

---

## 8. Reproduction protocol (next generation)

1. Run the **DNA §2 regeneration template** against any agent (local or hosted). Its output is a **proposal**.
2. A proposal becomes a generation only when: invariants preserved → conformance C1–C6 passes → boot gate
   passes → the director signs off → `core_version`/`dna_version` bump and the **DNA generation log is
   appended**.
3. Rebuild the manifest and bundle; keep the previous generation's rollback set; record the compatibility row
   for every host the new generation boots on.
4. Record the mutation in this lineage record and retire/absorb the superseded lines above.
5. Chapters are declared by the director; a chapter closes only with explicit acceptance.

Open decisions that belong to the next evolution, not to the live generation: browser passkey enrolment
pages, the home-node threshold share, host compaction policy, browser/MCP retirement, and any new host
adapter. None of them may be claimed as delivered until recorded.

---

## 9. Authorship

**Director — D.** Creator and final authority. Every generation bump, deferral and chapter close in this
lineage was made by D; the latest recorded decisions are the DNA v3 sign-off, keeping R11 a separate rule,
approving the interaction phase, approving the trust-layer bill and the public release.

**AI collaborators.** AGI was drafted, implemented, tested and documented with AI assistants under D's
direction: local models hosted locally through gen1–gen3.3, a three-model council for the gen2 proposal, and
a hosted host-model/brain pair for gen3.4–gen3.5. Authorship, decisions and responsibility remain with D; AI
assistance is recorded as infrastructure, not agency.

---

## Appendix A — evidence index

- **Generations:** `core/dna.md` §3 (generation log); `state/boot.json` (chapter/generation blocks).
- **Gates & tests:** `tests/conformance/test_conformance.py`, `tests/test_*.py`, `state/boot_gate.json`,
  `state/compatibility_matrix.json`, `state/boot_runs.jsonl`, `memory/scripts/registry.json`.
- **Artefacts:** `core_manifest.json`, `core/…bundle…tar.gz`, rollback sets, `releases/` (signed packages),
  `repo.json` (signed manifest of the public repository).
- **History:** decision log `state/taskboard_actions.jsonl`, maintenance ledger, archived roadmap text.

## Appendix B — verifying this record

Inside an install:

```bash
python tests/conformance/test_conformance.py     # C1–C6 gates
python memory/scripts/boot_gate.py              # the 12-check boot acceptance gate
python memory/scripts/repo.py verify            # signed public manifest + artefact hashes
python tools/check_integrity.py                 # the CI check, runnable by anyone
```

---

*Compiled from the DNA generation log, verified state files, conformance output and recorded measurements.
Historical claims that were not machine-verified are marked as records of intent or outcome, never as
implementation. No unverified claim is presented as delivered.*
