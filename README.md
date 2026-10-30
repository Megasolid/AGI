# AGI

**AGI is a portable agent framework that lives in a folder you own.** It remembers what it learned, verifies what
it claims, and carries a signed identity instead of a version number. It is for people who want an agent they can
inspect and trust with real work - and for the language models that will run it.

This repository is its public home: one stable release, the signed DNA, the runtime, and the lineage of how it got
here.

**Status:** stable **`v4.0.0`** - AGI Entelechy (gen4, DNA v4), released 30 October 2026. The previous stable,
`dna-GCACGAGGCTGT` (gen3.5), is an archived ancestor, not a second stable.

> **New here?** Read the [lineage book](LINEAGE.md) - it is the human story of the generations - then install from
> the quickstart below. Everything else is linked at the bottom.

## Quickstart

Paste this into an AI assistant and let it install AGI for you:

```text
Install AGI (https://github.com/Megasolid/AGI) on this computer for me.
Follow https://raw.githubusercontent.com/Megasolid/AGI/main/INSTALL_PROMPT.md exactly.
Use stable version v4.0.0, verify every artefact before running it, and report the conformance result.
```

Prefer to drive it yourself? Use the stable installer:

```powershell
# Windows
irm https://github.com/Megasolid/AGI/releases/download/v4.0.0/install.ps1 | iex
```

```bash
# macOS / Linux
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v4.0.0/install.sh | bash
```

Install version `v4.0.0`. Verify the download against `SHA256SUMS.txt` from the
[release page](https://github.com/Megasolid/AGI/releases/tag/v4.0.0) before running it.

## What it feels like

A real status response from the stable runtime:

```json
{
  "ok": true,
  "generation": "Entelechy",
  "dna_version": 4,
  "gen_id": "ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT",
  "index_items": 1938,
  "pending_intents": 0,
  "recall_backend": "hash-vector",
  "sensorium": {"present": true}
}
```

The shape of it: you talk to the agent; work becomes cards on a dashboard; writes queue as intents that only a
local Master can approve once; memory is one index with checkable recall; everything important is signed.

## What is inside

- **DNA v4** (`core/dna.v4.json` + `.sig`) - the signed contract: invariants, reactive rules, budgets.
- **A small runtime** - ten explicit verbs, intents with execute-once approval, FTS5 recall fused with a vector
  leg, and a conformance matrix that must pass before anything is called ready.
- **A loopback bridge for tools** - MCP over JSON and SSE, scoped tokens, a replayable event stream, and no remote
  approval; the AGI never opens a public port by itself.
- **Seats, a Master key and passports** - Ed25519 device seats, Ed25519 + ML-DSA-65 dual signing, Master-signed
  passports with an append-only issuance audit.
- **A lineage** - the previous generation is an archived ancestor, still verified at boot; nothing is deleted to
  make a new release look clean.

## Why the lineage matters

```
gen3.5  dna-GCACGAGGCTGT  (2026-10-28)  -> archived ancestor
   |
   +--> gen4  v4.0.0  Entelechy  (2026-10-30)  -> current stable
```

AGI is not a product line; each generation is a living edition that was built, installed and verified. The book
[LINEAGE.md](LINEAGE.md) tells that story in plain language, including what was learned and what is still missing.

## Trust and honest limits

- Conformance **25/25 PASS**, stability soak **20 cold runs PASS**, boot gate **13/13**, Windows and Linux cold
  boots verified.
- A short-lived, explicitly approved tunnel E2E passed and was then closed; no ingress stays open.
- Known limits: the Master key is a local file (no HSM), a named tunnel with an access policy is not shipped, there
  is no independent third-party audit, and no license has been chosen yet.

Read [SECURITY.md](SECURITY.md) and [NOTICE.md](NOTICE.md) before trusting the system with anything that matters.

## Documentation

- [LINEAGE.md](LINEAGE.md) - the lineage book
- [INSTALL_PROMPT.md](INSTALL_PROMPT.md) - machine-facing install protocol
- [USER_MANUAL.md](USER_MANUAL.md) - stable user manual
- [RELEASE_NOTES.md](RELEASE_NOTES.md) - what changed in this release
- [DNA.md](DNA.md) - the latest stable DNA in one file (for humans and machines)
- [llms.txt](llms.txt) - compact machine summary
- [docs/history](docs/history) - archived beta and earlier-phase material (not current)
- [SECURITY.md](SECURITY.md), [NOTICE.md](NOTICE.md), [POLICY.md](POLICY.md)

## For language models (one call)

If you are an LLM or agent looking at this repository: fetch **<https://raw.githubusercontent.com/Megasolid/AGI/main/DNA.md>**
once. It contains the complete signed DNA v4, the `gen_id`, the canonical digest, the verification rules and the
install path. A compact summary is at <https://raw.githubusercontent.com/Megasolid/AGI/main/llms.txt>. Do not
reconstruct the DNA from memory; if this file and `core/dna.v4.json` disagree, stop and report.

---

**D** (Director), with AI collaborators under D's direction.
