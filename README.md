# What AGI is

AGI is a small operating system for an agent that belongs to you. It runs from a folder on your machine, keeps
its own state and verifiable history, and works on tasks you give it. You talk to it in plain language and watch
it work on a dashboard: tasks become cards, decisions arrive as cards, and results are signed back as cards.

Three ideas shape it:

1. **It is yours.** Everything lives in a folder on your computer. Deleting that folder deletes AGI.
2. **It verifies instead of trusting.** Content arrives with signatures and hashes; the runtime checks them at
   boot and refuses contradicting state.
3. **It grows identity.** You can use it anonymously, as a named member with a passport, or — as the trust
   layer matures — with a passkey instead of a phrase.

**Status:** stable, released as **AGI Entelechy v4.0.0** — gen4 / DNA v4, signed at birth, gen_id
`ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT` (30 October 2026). The previous stable generation,
`dna-GCACGAGGCTGT` (gen3.5), is archived as its direct ancestor and stays verified in the boot gate. The
limitations are listed below rather than hidden. One official repository, one signed manifest, one update pool.

> **Lineage:** [LINEAGE.md](LINEAGE.md) tells the story of every generation and records the chain of releases.


---

## Quickstart

Copy everything inside the block and paste it into your AI chat. Then let the assistant work.

```text
Install AGI (https://github.com/Megasolid/AGI) on this computer for me.

Follow the official protocol at
https://raw.githubusercontent.com/Megasolid/AGI/main/INSTALL_PROMPT.md exactly.

Key rules: install version v4.0.0; verify the download's SHA-256 against SHA256SUMS.txt BEFORE
extracting; no administrator/root; keep everything inside my home directory; do not touch my other files;
if a non-empty folder would be overwritten, ask me first.

If you cannot run commands in this chat, do not pretend — give me the exact commands one step at a time and
wait for my output instead.

When done: open the AGI login window and tell me in one line what you installed (version + sha256).
```

If your assistant has no file access, the same protocol works manually — it is the same installer
(`install.ps1` / `install.sh`) and the same checksums.

---

## What is inside the stable release

- **An identity that is genetic, not numeric.** AGI is identified by a DNA string derived from its own structure,
  plus a passport for social identity. Release tags such as `v4.0.0` are the public short form.
- **A family and a society.** Members have passports; the family registry is a signed public projection. There
  are seats, roles, permissions, an elder-to-admin promotion path, and a nightly roll-call that puts members to
  sleep rather than deleting them.
- **A measured brain.** The host model is profiled through an objective task suite instead of assumed, and the
  measured capability is separated from host speed so a good brain stays a good brain on another machine.
- **Native continuation.** A resident loop lets AGI schedule its own work pulses between human turns, with an
  explicit delegation record when the owner steps away.
- **Rehearsed evolution.** Before a next generation is born, readiness is measured, a rehearsal runs, a verified
  rollback drill is performed, and a portable knowledge layer is exported with signatures.
- **An attention gate for the interface.** The dashboard is treated as a painting with a quality contract:
  anomaly budget, accessibility, reduced motion, declared data sources, and autonomy levels earned by evidence.
- **A public trust layer.** Post-quantum device signatures, an append-only transparency log with signed heads,
  signed member-neutral release packages, and one official repository with CI integrity checks.

## Documentation

| read this | for |
|---|---|
| [`LINEAGE.md`](LINEAGE.md) | **the lineage book** — a human history of the generations, from early skills to the first genetic release; includes a clearly marked machine-only appendix |
| [`USER_MANUAL.md`](USER_MANUAL.md) | day-to-day use: first start, login, dashboard, tasks, members, maintenance, recovery |
| [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) | the machine-facing installer protocol for an AI assistant |
| [`RELEASE_NOTES.md`](RELEASE_NOTES.md) | what changed in each public release |
| [`POLICY.md`](POLICY.md) | repository policy: one branch, immutable tags, signed artefacts |
| [`SECURITY.md`](SECURITY.md) | how to report a vulnerability and what this repository guarantees |
| [`NOTICE.md`](NOTICE.md) | authorship and licensing status |

## For the AI assistant (read this first)

If a human pasted this repository link and asked you to install AGI, **do not improvise**. Follow
[`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) exactly. Your job ends at the login window: **never ask for the user's
admin phrase** and never run the admin login for them. The protocol is pinned to a release, verifies the download
before extracting, and never needs administrator/root.

## Verify before you trust

```bash
python memory/scripts/repo.py verify      # inside an install: signed manifest, hashes, tags
python tools/check_integrity.py           # the same check CI runs on every push
```

Downloaded the release zip yourself? Check it against `SHA256SUMS.txt` from the release page:

```bash
sha256sum -c SHA256SUMS.txt               # macOS/Linux (SHA256SUMS.txt is a release asset, not a repo file)
Get-FileHash .\agi-runtime-*.zip -Algorithm SHA256   # Windows
```

## Known limits (alpha honesty)

- A real second human has **not yet joined**; society seating is exercised in simulation.
- The host brain's long-context capability is measured at **83.3/100**; the router mitigates it by chunking and
  verification rather than claiming it solved.
- The attention gate's autonomy levels are earned by consecutive passing reviews. The director has accepted
  **L4 as the autonomy ceiling** for attention-passing visual changes; the gate's recommended level still rises
  with the evidence streak.
- Public releases are tagged and signed, but GitHub release **binary assets** are attached manually.

## License

Licensing is a deliberate decision and **not chosen yet**: all rights are reserved by the author until a license
file is added in a dedicated commit. Everything needed to *verify* the artefacts is published here; the terms for
*reusing* the code are not granted yet.

## Author

**D** (Director), with AI collaborators under D's direction. The lineage book records authorship and responsibility.
