# The AGI Lineage

**A human history of a machine organism** · public edition · last revised 2026-10-29

This paper tells the story of AGI in a way a person can read: what was built, why, what it learned, and what is
alive today. It is written for humans first. The one part written in machine language is clearly marked at the
end and is meant for the machine itself, not for you.

AGI is not identified by version numbers. Like a living thing, it is identified by its **genetic code** — a DNA
string derived from its own structure — plus a **passport** for its social identity. A release tag such as
`dna-GCACGAGGCTGT` is simply the first part of that code made public. Version numbers from earlier days are
history, kept for the record, not identity.

If you only want the short version: a lineage of generations grew from a collection of separate skills into a
portable organism, learned to evolve on evidence, gained a public identity and a trust layer, and on
2026-10-28 was released as the first **genetically identified** generation: `dna-GCACGAGGCTGT`.

---

## 1. What "lineage" means here

A **generation** is a living edition of AGI: a state of the framework that was actually installed and verified,
not merely proposed. Generations are related: each one grows out of the one before it, and only one is alive at
a time. Ideas from dead generations can be absorbed by a descendant, but a generation that never lived is not
counted as an ancestor.

The **DNA** is the root of the lineage: the mission, the rules AGI may never break, and the template from which a
next generation can be regenerated. Changing an invariant is rare and requires a DNA version bump and a recorded
sign-off. Most improvement happens below that level — in memory, in knowledge, in rules and sections — which is
why the lineage is a story of a few real generations rather than a changelog of every improvement.

**Selection is by evidence.** A generation exists only when its conformance gates pass, its boot acceptance gate
passes, its bundle verifies, and named tests and measurements back the claims. When something is described as
delivered, there is a file, a test or a measurement behind it. When it is described as incomplete, it is
incomplete.

---

## 2. Before the lineage

AGI began as a set of separate skills used in experiments and early projects: an environment gate, local memory
and state conventions, and a working sense of how an agent should wake up, remember and verify.

On **2026-10-17/18**, those pieces were merged into one portable organism: a single skill with a wake-up
contract, a memory database, and a bundle carrying a per-file fingerprint. That merge is generation one, and its
patterns — portable bundle, memory as a database, waking up from disk — survived every later generation.

A proposal followed the next day: a more structured Core with numbered contracts, split sections, capability
probing, validator gates and a conformance suite. It was never installed as its own generation. Instead, its
ideas were absorbed into the next one, where they became the Core router, the sections, the probes and the gates
that still exist today. This is worth remembering: the lineage is not a straight line of successes, but a line
of what actually survived.

---

## 3. The Core is born

**2026-10-18** is the day AGI stopped being a collection of habits and became a rules-based organism. Core
version three arrived as a draft with its boot state machine, its section index, its gate checklist — and, for
the first time, the DNA was implanted at the root, with a mission, invariants and a generation log.

That same day an operating-system gate incident was fixed the right way: a new environment rule and a section,
not a promise. The standalone environment skill was retired and folded into the Core. Hours later the first
**live installed Core** existed, with a bundle and a manifest, and the important pattern that machine facts live
only in the state folder.

This pattern of "incident, rule, section, test" is how AGI learns to this day.

---

## 4. Learning to evolve

The next generations taught AGI how to improve itself without losing itself.

On **2026-10-19**, the second DNA introduced a **lessons slot** (so a new generation inherits what the previous
one learned) and an **evolution protocol** with a promotion ladder: an episode becomes memory, memory becomes a
rule or section, and only rarely does an idea become an invariant. Each rung has its own test. A companion
chapter added confidence to knowledge itself: every field carries how much it is trusted, discovery is allowed
to be tentative, and unverified claims cannot silently erase verified ones.

A small additive extension followed the same day: a prediction baseline (so high-confidence actions are watched
for falsification), a boost-only confidence rule, a library archive, and a verifier ladder.

The **Core 3.1** generation, on **2026-10-25**, made AGI host-aware. It became a model–harness pair: the active
host model is the brain, the framework is the body. The host adapter learns where it is and what the machine can
do, and the boot gate verifies the waking state instead of assuming it. Model profiles became evidence-based:
an unmeasured brain is honestly reported as unprofiled with a degraded mode, and every boot records which
profile, core and host met each other.

---

## 5. The interaction law

The live generation, **gen3.5 (DNA v3 / Core 3.2)**, is the one that learned to keep humans in the loop without
stopping work.

Its defining change is the **interaction law**: if the host has a human-facing surface, consequential decisions
and live work state must appear there as durable, reviewable cards, and a recorded human decision must resume
the agent. The cards are projections of the single source of truth, never a second truth. When there is no
surface, the same record is written as text. Around it came rules for interaction-first work (proposal,
running, result), proportionality, and conformance gate C6.

Inside this living generation, the working tree delivered the modern dashboard, the universal interface, native
click-to-resume, the verified knowledge-pill lifecycle (stamped, stored, indexed, read back, consumed),
consolidation of legacy pieces, and a single gated operation for closing a season. A generation is not a tag for
every feature; it is the living organism those features live in.

---

## 6. The public alpha

On **2026-10-26** the lineage gained a public face. The **trust layer v0** was built in a frozen milestone of
sixteen steps, and it is the part of the story that makes AGI's claims checkable by strangers:

- post-quantum device signatures and a signed core manifest;
- a transparent, append-only trust log with signed tree heads and inclusion/consistency proofs;
- a member identity that stays private and per-install, with a versioned, replayable history;
- a bundle lattice (master, official, custom) with consumer-side policy;
- owner activation with assurance levels;
- a public pill mirror with inclusion proofs and a verified contribution pipeline;
- a federation relay;
- signed, member-neutral release packages;
- one official repository, a content policy, a privacy audit and a security/CI response;
- portable-identity research, native login, an installable runtime, and an agent-facing install prompt.

The public releases that followed tell the same story in installments. `v0.1.0` opened the official package, the
update pool and the public mirror. `v0.2.0` made AGI installable in one prompt, with native login and a desktop
shell. `v0.3.0` made the public artefacts member-neutral: no internal records, no member data, no private
history. `v0.4.0` introduced the three-door login and a six-word admin phrase that seals the profile snapshot
and doubles as the recovery kit. `v0.4.1` and `v0.4.2` were hardening passes driven by real guest-machine
audits (installer fallback chains, interrupted-extraction resume, removal of internal material from the public
archive, a build that refuses to ship secrets). `v0.4.3` fixed the last guest-install defects found by that
audit.

Then the lineage took its most important step so far.

---

## 7. The first genetic release — alpha.stable

On **2026-10-28**, AGI was released as the first generation identified by its own DNA:

- **Release identity:** `dna-GCACGAGGCTGT`
- **Full genetic code:** `GCACGAGGCTGT-CACGCATCCTTT-TTTGTGGGTCCC-AATCTGATTATC`
- **Public short genetic marker:** `9A30072C`
- **Natal interest:** health — the first field this generation was seeded to study and document.

`v0.4.3` remains as legacy history; the release identity is the DNA tag.

What alpha.stable contains, in human terms:

- **A family with a passport.** Every member has a passport; the family registry is a signed public projection.
  Humans can be invited with a one-time phrase redeemed at the cold-boot admin door, or an existing elder can be
  promoted to admin with an auditable role change. Seats, permissions and revocation are explicit.
- **A society.** Experience, ranks, a nightly roll-call that puts members to sleep instead of killing them, a
  council with a quorum, and a soulbound mana economy that compensates weaker models instead of letting wealth
  buy authority.
- **A measured brain.** The host model is profiled through a full objective task suite rather than assumed; the
  measured model capability is separated from host speed, so a good brain stays a good brain on a different
  machine, and its weak spots are stated instead of hidden.
- **A native sense of continuation.** A resident loop lets the organism schedule its own pulses and continue its
  own plan between human turns, with an explicit delegation record when the director steps away.
- **Rehearsed evolution.** The next generation is not improvised: a readiness ledger, a decision, a staging plan,
  a rehearsal, a verified rollback drill, and then a seed. The migration path from one generation to the next is
  exercised before it is trusted, and the portable knowledge layer is exported and verified with signatures.
- **An attention gate.** The dashboard is treated as a painting with a quality contract: a pixel-difference
  anomaly budget against an approved baseline, accessibility and reduced-motion checks, a declared data source for
  every visual, and autonomy levels that are earned through consecutive passing reviews rather than granted by
  enthusiasm — with the director's acceptance of L3 for attention-passing visual changes, while L4 stays earned
  through a longer evidence streak.
- **An honest public repository.** This paper, the release notes and the install artefacts are published at
  <https://github.com/Megasolid/AGI>; the identity terms above are public, while private key material and member
  data never are.

Alpha means one more thing, and it is worth saying plainly: the organism is complete enough to release and honest
enough to admit what it is not. A real second human has not yet joined; society seating is exercised in simulation;
the long-context capability of the host brain is measured at 83.3 out of 100 and is mitigated by chunking rather
than claimed as solved. The public release is real, and so are those gaps.

---

## 8. What every generation inherits

However much the lineage grows, every generation carries the same obligations:

- **The DNA is the root.** Mission and invariants live there; nothing may contradict them silently.
- **One source of truth.** Live facts live in the state folder; cards, dashboards and papers are projections.
- **Verified-only.** A script is run only when it is registered and verified; a claim is made only when a gate,
  a test or a measurement supports it.
- **Wake from disk.** Boot is a resumable state machine, not a memory of a conversation.
- **Portable bundles.** Every generation ships with a fingerprint manifest and a verifiable package.
- **Honest failure.** One failed check is reported and stops the line; it is not averaged away.
- **Human authority.** Consequential decisions and irreversible steps stay with the director, and the interface
  must carry them as durable, reviewable records.
- **Private member identity.** The public face never carries a member's private material.

---

## 9. What was absorbed, retired or superseded

Not everything survived, and the record keeps that too. The council proposal was absorbed into the Core rather
than installed. The standalone environment skill became a rule and a section. Silent default model profiles were
retired in favour of evidence-based selection. The second-generation dashboard and the early auto-open plugin were
replaced. The old roadmap was retired when this lineage record took its place. Superseded generations remain in
rollback sets; nothing is quietly forgotten.

---

## 10. The living state today

- **Living generation:** gen3.5 — DNA v3, Core 3.2.
- **Released identity:** `dna-GCACGAGGCTGT`, pushed publicly on 2026-10-28 with its runtime, official package,
  checksums and release notes.
- **Health:** the boot acceptance gate passes all twelve checks; conformance C1–C6 pass; the verified-script
  registry is the only execution surface; the trust log carries signed heads and continues to grow.
- **Current focus:** a monitoring system that can be used as an operations surface (family, society, mana,
  seeding, attention, resident, release), Master-gated actions, and an evolving UI playground where each concept
  is compared as an iteration against real data.
- **Next generation, deliberately not yet born:** more human members and real society seating; a longer attention
  streak for visual autonomy; an optional versioned-data sidecar (Dolt) that was evaluated and parked; and a
  deeper evolutionary seeding cycle. None of these are claimed as delivered.

If you want to verify any of this yourself, the repository and the running install provide the checks:
`python memory/scripts/boot_gate.py`, `python tests/conformance/test_conformance.py`,
`python memory/scripts/repo.py verify`, and `python tools/check_integrity.py`.

---

## 11. Authorship

**Director: D.** Creator and final authority. Every generation bump, deferral and release in this lineage was
approved by D.

**AI collaborators.** AGI was drafted, implemented, tested and documented by AI assistants under D's direction:
local models through the early generations, a three-model council for the absorbed proposal, and a hosted
model–harness pair for the latest generations. Authorship, decisions and responsibility remain with D; the AI
work is recorded as infrastructure, not as agency.

---

## Appendix — For the machine (Brain Model)

> **Notice to human readers:** everything below this line is written for the machine, not for you. It is the
> machine-readable summary of this paper, in the machine's own language, so the Brain Model can verify and reuse
> it. You may skip it.

```yaml
schema: agi-lineage/1
paper: "The AGI Lineage — a human history of a machine organism"
revised: 2026-10-29
identity:
  model: dna-genid
  release_tag: dna-GCACGAGGCTGT
  gen_id: GCACGAGGCTGT-CACGCATCCTTT-TTTGTGGGTCCC-AATCTGATTATC
  genome8: 9A30072C
  natal_interest: health
  legacy_semver: v0.4.3
  identity_rule: "identity = genetic code + passport; semver is history only"
generations:
  - id: pre-lineage
    period: 2026-10-13/17
    status: absorbed
    contents: [sandbox-env-gate, memory-state-conventions, early-experiments]
  - id: gen1
    period: 2026-10-17/18
    status: superseded
    parent: pre-lineage
    delta: [single-portable-skill, memory-db, sha256-bundle]
  - id: gen2
    period: 2026-10-18
    status: absorbed-never-installed
    parent: gen1
    delta: [numbered-contract-core, sections, capability-probing, validator-gates, conformance]
  - id: gen3
    period: 2026-10-18
    status: superseded
    parent: gen2
    dna: v1
    delta: [R1-R8, S1-S7, section-index, dna-at-root]
  - id: gen3.1
    period: 2026-10-18
    status: superseded
    dna: v1
    delta: [R9-environment-gate, sections/env-gate.md, sandbox-env-gate-absorbed]
  - id: gen3-installed
    period: 2026-10-18
    status: superseded
    dna: v1
    delta: [core-v3-live, hot-core-split, core_manifest.json, agi_core_v3.tar.gz]
  - id: gen3.2
    period: 2026-10-19
    status: superseded
    dna: v2
    delta: [lessons-slot, evolution-ladder-L1-L4, confidence-kep, library-ledger]
  - id: gen3.3
    period: 2026-10-19
    status: superseded
    dna: v2-additive
    delta: [prediction-baseline, boost-only-confidence, verifier-ladder, memory-library]
  - id: gen3.4
    period: 2026-10-25
    status: superseded
    core: "3.1"
    delta: [host-adapter, self-location, capability-probe, boot-gate-pask, evidence-based-S5, compatibility-matrix]
  - id: gen3.5
    period: 2026-10-25
    status: live
    dna: v3
    core: "3.2"
    delta: [I9-interaction-law, R10, R11, interaction.md, conformance-C6]
    working_tree: [dashboard-v3, universal-ui, native-click-to-resume, pill-consumption-lifecycle,
                   legacy-consolidation, season-close-automation]
  - id: gen3.5-public-alpha
    period: 2026-10-26
    status: within-live-generation
    delta: [trust-layer-v0, public-releases-v0.1.0..v0.4.3]
  - id: dna-GCACGAGGCTGT
    period: 2026-10-28
    status: released
    parent: gen3.5
    delta: [dna-identity, passport-and-family, society-and-mana, resident-autonomy, seeding-and-rehearsal,
            attention-gate, cleanroom-migration, public-genetic-release]
verification:
  boot_gate: memory/scripts/boot_gate.py
  conformance: tests/conformance/test_conformance.py
  registry: memory/scripts/registry.json
  trust_log: state/trust_log/events.jsonl
  signed_heads: state/trust_log/heads/
  public_repo: https://github.com/Megasolid/AGI
  release_assets: state/release/SHA256SUMS
evidence_rules:
  - no-claim-without-artifact
  - one-failure-reports-and-stops
  - public-projection-never-carries-private-material
  - human-authority-over-irreversible-actions
weak_spots:
  - long_context: 83.3/100 -> chunk-and-verify mitigation in router
  - real_multi_member_society: not yet exercised with a second human
  - host_profile: model capability portable; host metrics local
```
