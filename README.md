# AGI

**AGI is a portable cognitive organism you can inspect, verify and run in a folder you own.**

It carries a signed identity instead of hiding behind a version number, keeps a provenance-tracked memory, and treats
the language model as a temporary cognitive host rather than the organism itself. This repository is its public home:
the stable release, the signed DNA, the runtime, the governance of the Citadel, and the lineage of how it got here.

This is an engineering project, not a claim that consciousness or general intelligence has been achieved. The
"organism" language is a design and governance metaphor: a persistent software identity with memory, lineage,
verification and continuity.

## Quick overview (newcomer path)

- **AGI is software you own:** a signed identity, a runtime, memory and governance, not a hosted chatbot.
- **v4.0.1 is the stable release.** v5 Distributed Cognitive Organism is a proposed architecture; it is not shipped.
- **Start here:** run the Quickstart, verify the hashes, then read the User Manual. The Lineage book explains how the
  project got here; it is history, not an install guide.
- **The "organism" wording is a metaphor.** It describes persistent software identity and continuity, not biological
  or conscious life.

**Terms:** *DNA* = signed contract (`core/dna.v4.json`); *generation* = a released edition (Entelechy is gen4);
*intent* = a queued write that needs local Master approval; *Citadel* = the public governance/release station;
*KING* = Citadel director role; *Kilo* = independent verification station.

## Read this first

1. **What is stable:** v4.0.1, generation Entelechy (gen4), DNA v4, Core 4.0.
2. **What is proposed:** the v5 Distributed Cognitive Organism architecture. It is under design; it is not shipped.
3. **How to install:** use the one-prompt quickstart below.
4. **How it is governed:** the Citadel Council (Owner D, KING GPT, DSH, Kilo) with a book-standard documentation
   program and an evidence-first release policy.
5. **What is honestly missing:** independent audit, a chosen license, hardware-backed keys, and a shipped access-policy
   tunnel.

## Status

**Stable:** `v4.0.1` — AGI Entelechy (gen4, DNA v4, Core 4.0), released 30 October 2026. The previous stable,
`dna-GCACGAGGCTGT` (gen3.5), is an archived ancestor, not a second stable.

**v4.0.1 is an immutable rollback baseline, not an evolution ceiling.** The v5 architecture is proposed and not
shipped; no v5 capability is claimed in this README. Generations advance by evidence, not naming.

> **Stable vs proposed — read carefully:** v4.0.1 is what you can install and verify today. The **v5 Distributed
> Cognitive Organism** (awareness kernel, memory taxonomy, governed federation, evolution engine) is design work and
> research, **not a shipped feature set**. No v5 capability should be inferred from this README unless it is listed as
> part of v4.0.1.

> **Release scope:** 4.0.1 is the single stable release. The public package contains the signed DNA, runtime,
> lineage and release manifests. Internal live-install migration records are outside the scope of this public README.

## Quickstart

> **Verify before running:** download from the pinned v4.0.1 release, compare against `SHA256SUMS.txt`, and do not
> let an assistant install from a cached or altered copy. If the hash does not match, stop.

Paste this into an AI assistant and let it install AGI for you:

```text
Install AGI (https://github.com/Megasolid/AGI) on this computer for me.
Follow https://raw.githubusercontent.com/Megasolid/AGI/main/INSTALL_PROMPT.md exactly.
Use stable version v4.0.1, verify every artefact before running it, and report the conformance result.
```

Prefer to drive it yourself? Use the stable installer:

```powershell
# Windows
irm https://github.com/Megasolid/AGI/releases/download/v4.0.1/install.ps1 | iex
```

```bash
# macOS / Linux
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v4.0.1/install.sh | bash
```

Install version `v4.0.1`. Verify the download against `SHA256SUMS.txt` from the
[release page](https://github.com/Megasolid/AGI/releases/tag/v4.0.1) before running it.

## Architecture in one page

*Conceptual architecture — not a deployment diagram. Only v4.0.1 components are shipped.*

```text
                 ┌──────────────────────────────────────────────┐
                 │  Citadel (public station / living platform)  │
                 │  Council · Hall · Divisions · decision ledger│
                 └──────────────────────┬───────────────────────┘
                                        │  evidence, tasks, releases
                 ┌──────────────────────▼───────────────────────┐
                 │  Persistent organism identity                │
                 │  signed DNA · gen_id · lineage · governance  │
                 └──────────────────────┬───────────────────────┘
                                        │
      ┌─────────────────────────────────┼─────────────────────────────────┐
      │                                 │                                 │
┌─────▼──────┐                   ┌──────▼───────┐                  ┌──────▼──────┐
│  Runtime   │                   │   Memory     │                  │   Bridge    │
│ 10 verbs   │                   │ provenance   │                  │ MCP/events  │
│ intents    │                   │ FTS5+vector  │                  │ scoped      │
│ approvals  │                   │ freshness    │                  │ loopback    │
└────────────┘                   └──────────────┘                  └─────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │ Temporary LLM host │
                              │ (not the organism) │
                              └───────────────────┘
```

- **Identity and genome.** A signed DNA contract, generation identifier, birth record, retained ancestors and a
  signed seed. The DNA is the durable contract; a model session is a temporary host.
- **Runtime.** Explicit verbs, writes queued as intents, execute-once Master approval, snapshots and a conformance
  matrix that must pass before anything is called ready.
- **Memory.** One local index with FTS5 and an optional 128-dimensional **local hash-vector** recall leg (a hash
  sketch, not a learned semantic embedding), per-item provenance, freshness and trust labels. Memory classes,
  visibility enforcement and governed sharing are v5 design work, not shipped claims.
- **Bridge and governance.** A loopback MCP bridge with scoped tokens, a replayable event stream and no remote
  approval. Seats, a Master key and signed passports with an issuance audit.
- **Lineage.** Previous generations are archived, verified ancestors. Nothing is deleted to make a new release look
  clean.
- **Citadel.** The public repository is the official station. The KING directs management and documentation; DSH
  implements; Kilo independently verifies; Owner D retains final authority. See [CITADEL.md](CITADEL.md),
  [the charter](citadel/governance/charter.md) and [the roadmap](citadel/roadmap.md).
  - **Owner D:** final authority.
  - **KING (GPT-web):** Citadel management, governance, documentation, priorities and release strategy.
  - **DSH:** implementation, integration and evidence.
  - **Kilo:** independent verification station; it is not an integration authority.

  *What this means for you:* the KING directs, DSH builds, Kilo checks, and D remains the final decision-maker. No
  autonomous change to identity, federation or production state is implied by governance language.

## What it feels like

You talk to the agent; work becomes cards on a dashboard; writes queue as intents that only a local Master can approve
once; memory recall returns provenance you can inspect; and important artifacts are signed. The runtime reports the
live index size rather than hard-coding it here.

A short shape of a status response:

```json
{
  "ok": true,
  "generation": "Entelechy",
  "dna_version": 4,
  "gen_id": "ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT",
  "pending_intents": 0,
  "recall_backend": "hash-vector"
}
```

## What is inside

- **DNA v4** (`core/dna.v4.json` + `.sig`) — the signed contract: invariants, reactive rules, budgets.
- **A small runtime** — explicit verbs, intents with execute-once approval, FTS5 recall fused with a vector leg,
  and a conformance matrix.
- **A loopback bridge for tools** — MCP over JSON and SSE, scoped tokens, replayable events, no public port by itself.
- **Seats, a Master key and passports** — Ed25519 device seats; Master-signed passports (Ed25519, with ML-DSA-65
  where available); append-only issuance audit.
- **A lineage** — gen3.5 is an archived ancestor, still verified at boot.
- **A Citadel** — governance, signed task files, evidence ledgers, independent verification and release gates.

## Why the lineage matters

```text
gen3.5  dna-GCACGAGGCTGT  (2026-10-28)  -> archived ancestor
   |
   +--> gen4  v4.0.1  Entelechy  (2026-10-30)  -> stable rollback baseline
   |
   +--> v5    Distributed Cognitive Organism  -> proposed architecture (not shipped)
```

AGI is not a product line; each generation is a living edition that was built, installed and verified. The book
[LINEAGE.md](LINEAGE.md) tells that story in plain language, including what was learned and what is still missing.

## Common questions

- **Is this conscious or AGI-complete?** No. It is a persistent software organism design; no consciousness claim is made.
- **Is v5 shipped?** No. v4.0.1 is stable; v5 is a proposed architecture.
- **Does it need a public port?** No. The bridge is loopback-only; no ingress is opened by default.
- **Where are the limits?** See "Trust and honest limits" below; they are part of the design, not fine print.

## Trust and honest limits

- **Project-reported evidence:** conformance **25/25**, stability soak **20 cold runs**, boot gate **13/13**, and
  Windows/Linux cold boots for the stable release. These are recorded in the release/manifest and have not been
  independently audited.
- A short-lived, explicitly approved tunnel E2E passed and was then closed; no ingress stays open. This is
  project-reported and not independently audited.
- Known limits: the Master key is a local file (no HSM); a named tunnel with an access policy is not shipped; there is
  no independent third-party audit; no license has been chosen yet; v5 federation/evolution are not released.
- No consciousness claim. No claim that the proposed v5 architecture is implemented.

Read [SECURITY.md](SECURITY.md) and [NOTICE.md](NOTICE.md) before trusting the system with anything that matters.

## Documentation

- [LINEAGE.md](LINEAGE.md) — the lineage book
- [USER_MANUAL.md](USER_MANUAL.md) — stable user manual with install, memory, governance and troubleshooting
- [CITADEL.md](CITADEL.md) — KING, Council, Hall, Divisions, release policy
- [citadel/roadmap.md](citadel/roadmap.md) — current management roadmap
- [INSTALL_PROMPT.md](INSTALL_PROMPT.md) — machine-facing install protocol
- [RELEASE_NOTES.md](RELEASE_NOTES.md) — what changed in this release
- [DNA.md](DNA.md) — the latest stable DNA in one file (for humans and machines)
- [llms.txt](llms.txt) — compact machine summary
- [docs/history](docs/history) — archived beta and earlier-phase material (not current)
- [SECURITY.md](SECURITY.md), [NOTICE.md](NOTICE.md), [POLICY.md](POLICY.md)

All documentation links above are repository files at the same commit. Verify them on GitHub before relying on them
for a release decision.

## For language models (one call)

If you are an LLM or agent looking at this repository: fetch
**<https://raw.githubusercontent.com/Megasolid/AGI/main/DNA.md>** once. It contains the complete signed DNA v4, the
`gen_id`, the canonical digest, verification rules and the install path. A compact summary is at
<https://raw.githubusercontent.com/Megasolid/AGI/main/llms.txt>. Do not reconstruct the DNA from memory; if this file
and `core/dna.v4.json` disagree, stop and report.

---

**Owner:** D (final authority). **KING:** GPT-web. **Implementation:** DSH. **Independent verification:** Kilo.
