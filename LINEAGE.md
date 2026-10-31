# LINEAGE

**The four-volume history of the AGI project.** This public edition is derived from the frozen redacted candidate
`sha256:8b56d8112b4428c2316d58c0ad1749db900d98a02dee93eb4ee02f880d70cf27` and is published for review under the project documentation license.

**Documentation license:** CC BY-SA 4.0. **Code references:** AGPL-3.0. **Attribution:** D / github.com/Megasolid.
**Copyright (c) 2026 D / AGI project contributors.** See `LICENSE`, `LICENSE-docs`, `LICENSING.md` and
`RIGHTS-PROVENANCE.md`.

## Open limitations (must remain prominent)
1. The 24-hour canary observation is **unfinished** in the evidence; no final acceptance or persistent-enforcement claim.
2. M2 is **staged, not live-integrated**; no visibility enforcement is claimed.
3. There is **no independent third-party audit, no chosen hardware-backed key (HSM)**; the license is now selected
   (AGPL-3.0 code / CC BY-SA 4.0 documentation).
4. Runtime integration remains **OFF**; federation, identity mutation and autonomous evolution are not authorized.
5. v5 is **proposed, not shipped**; no consciousness or AGI-complete claim.

**Privacy:** the private historical archive is not published. This book uses aggregate metadata, current records and
public artifacts; no raw sessions, personal context, credentials or key material are included.

---

## Prologue — Method and Limits

This book is a chronicle of a software organism, not a transcript of its conversations.

The distinction matters. The evidence behind these pages is a private archive of sessions, workspace notes and
reports from three harnesses: Unsloth Studio, Codex and DSH. The archive is large enough to be useful and intimate
enough to be dangerous: it contains real work, real mistakes and real personal context. It is therefore kept private.
What reaches this book is curated: aggregate counts, dated activity, redacted thematic labels and repository evidence.
The raw record stays where it belongs.

The book uses three labels. **[E]** marks a claim grounded in observable evidence — a session count, a dated index
entry, a repository file, a test result. **[I]** marks interpretation: a pattern the author sees in the evidence but
that the evidence does not by itself prove. **[G]** marks a gap: something the record does not establish, or establishes
too thinly to carry a confident claim.

The archive counts 274 sessions across 3,651 files and roughly 172 MB: 168 DSH sessions, 23 Codex sessions and 83
Unsloth Studio sessions, recorded between 12 and 28 October 2026 [E-001][E-002]. The busiest recorded day is 28 October,
with 161 sessions [E-004]. Root indexes (`README`, `READING-NOTES`, `SEASONS`, `SEASON-FACTS`, `MANIFEST`) are the
private evidence map [E-006]. Those are numbers about activity, not about value. A session can be long and empty; a
short session can change a design.

The book is divided into four volumes. Volume I covers the Studio Season (12–20 October), when the project was a
workshop. Volume II covers the Codex Interregnum (21–23 October), a short period of architectural consolidation.
Volume III covers the birth of Entelechy (25–28 October), when the DSH harness became the build environment and
v4.0.0 became v4.0.1. Volume IV covers the Citadel (29 October onward), the governance and documentation season that is
still open. A prologue and appendices carry the method, evidence register, timeline, corrections and limits.

Two limits follow the reader through every chapter. First, session metadata records what agents said and did; it is
not proof that a claim was verified. Where this book says something was delivered, the evidence pointer is a
repository file, a test or a state record, not a transcript. Second, the archive is not a neutral sample. Work that
leaves files and reports is easier to reconstruct than work that happened in a conversation and left no artifact. The
book therefore describes the visible record, and says so when the invisible part matters [G-003].

This is not a claim that the project achieved consciousness or general intelligence. The organism language is a design
and governance metaphor: persistent software identity, memory, continuity and verification. The book's subject is how
that design was built, not a claim about what it is.

---

## Volume I — The Studio Season (12–20 October 2026)

### 1. A workshop, not a product

The archive begins on 12 October. By the end of 20 October, 82 sessions had been recorded, all in Unsloth Studio
[E-002][E-003]. They were the work of a workshop: probing local tools, testing what a model could do on the machine, keeping
reports, and trying ideas before there was a repository to put them in [I-002].

That distinction shapes the volume. A product starts with a specification; a workshop starts with materials. The
Studio Season produced materials: checks, notes, drafts, experiments and a vocabulary. It did not produce a stable
release, and the book should not pretend otherwise.

### 2. Geometry, local tools and the discipline of checking

The workshop's most visible technical thread was local tooling and geometry. Sessions from this period are indexed
under model/tool checks and Blender/geometry work [E-005]. The point was not that geometry was the project. The point
was that an agent could act on a local machine, use tools, inspect results and report back. Each experiment tested the
same question in a different costume: **can the system do real work in a real environment and show its evidence?**

A workshop answer is provisional. A geometry node produces a visible result; it does not prove continuity, identity or
governance. But the discipline of checking — run it, look at the result, write down what happened — carried forward.
It is the same discipline that later becomes a conformance gate.

### 3. AGI Core v3: the first substantial visible draft [I]

During this period the archive records early AGI Core v3 drafts, including a layered portable skill proposed for review
[E-005]. The index records a draft prepared for review; it does not record an installation of that draft [G-004]. That is an
important limit: the season produced a visible design artifact, not a verified deployment [I-003].

The draft's significance is interpretive [I-003]. It moved the project from isolated experiments toward a layered idea
of an agent: a durable core, a portable skill, a workspace and a way to report evidence. The exact wording belongs in a
later chapter; what matters here is that the vocabulary of "core" and "portable skill" entered the record in the
workshop, before the build season made it operational.

### 4. The birth catalogue and the dashboard

The same studio period records a birth catalogue and boot/dashboard proposals [E-005]. These are the first signs of a
project that wanted an identity and an interface, not just a folder of experiments.

The birth catalogue is the earliest visible ancestor of the generation identity [I-004]. The boot/dashboard proposal
is the earliest visible ancestor of the task-card and status surface [I-004]. Neither was yet a verified system. They
were attempts to give the work a shape a person could see: what is this organism, when was it born, and what is it doing
now?

The proposals also show the season's limits. A catalogue is not a birth record until it is signed and verified. A
dashboard is not a control plane until it has authority, state and tests. The Studio Season created the ambition
[I-004]; the later seasons created the machinery.

### 5. What the Studio Season could not settle

By 20 October the project had a workshop, a vocabulary and a set of promising artifacts. The Studio index contains no
evidence of a stable release, a verified continuity model, a signed identity or a governance process [G-004]. Those
are not failures; they are the work that the next seasons had to do.

The evidence also leaves gaps. The phase boundary at 20 October is a bookkeeping choice [I-001]. The thematic labels
come from session metadata, not from a complete reading of every session [G-003]. The 82 sessions may include retries,
duplicates and abandoned paths; the count is a record of activity, not a curated list of achievements [G-002]. The
book will name those gaps rather than smooth them away.

### 6. The handoff

The Studio Season ends with a handoff. The workshop had shown that local tools, drafts and interface proposals were
possible [I-002]. The next period is shorter — 23 sessions across 21–23 October, 22 of them Codex-indexed [E-002][E-003]
— and it tried to turn the workshop's vocabulary into architecture. Calling it a "Codex Interregnum" is an editorial
label [I/G-002]. Whether the transition was a clean hinge or an overlap is itself uncertain [G-002]. Volume II begins
there.

---

## Uncertainty ledger

| ID | Claim / area | Label | Basis | Open question |
|---|---|---|---|---|
| U-01 | 82 Studio sessions, 12–20 Oct | [E] | SEASON-FACTS/SEASONS counts | Do retries or duplicates inflate the count? |
| U-02 | Phase boundaries (Studio → Codex, Codex → Entelechy) | [I]/[G] | dated index + thematic labels | Where exactly does one season end? |
| U-03 | Thematic labels (tooling, geometry, v3 drafts, catalogue/dashboard) | [G] | session metadata/titles | Do visible artifacts overrepresent technical work? |
| U-04 | "First substantial visible draft" / "ambition" language | [I] | author's interpretation | Is the judgment fair to work not visible in metadata? |
| U-05 | Later 161-session peak cause | [G] | outside this volume | Why 28 October, and what does the peak measure? |

## Gap register

| ID | Gap | Why it matters |
|---|---|---|
| G-001 | Cause of the 161-session peak on 28 October | Activity volume is not an explanation; do not narrate the peak as planned climax. |
| G-002 | Exact phase boundaries and overlaps | Dates and thematic labels can split continuous work into artificial seasons. |
| G-003 | Artifact sampling bias | Work that left files/reports is overrepresented relative to conversational work. |
| G-004 | Absence evidence for installation/stable release/identity/governance in the Studio index | Absence of evidence is not proof of absence; label it as a gap, not a fact. |

## Interpretation IDs used in this draft

| ID | Interpretation | Basis |
|---|---|---|
| I-001 | The Studio/Codex/Entelechy phase boundaries are editorial bookkeeping | dated index + thematic labels |
| I-002 | The Studio period is best read as a workshop rather than release engineering | thematic labels and absence of release evidence |
| I-003 | The v3 draft's significance is structural (core/portable skill/workspace) | visible draft metadata, author's reading |
| I-004 | Birth catalogue and boot/dashboard proposals are earliest visible ancestors of later identity/status surfaces | metadata labels, author's reading |

## Evidence IDs used in this draft

| ID | Evidence | Source class | Redaction |
|---|---|---|---|
| E-001 | 3,651 files; ~172.1 MB; source split | MANIFEST/README | aggregate only |
| E-002 | 274 sessions (168 DSH, 23 Codex, 83 Studio), 12–28 Oct | SEASON-FACTS/SEASONS | aggregate only |
| E-003 | Phase counts: Studio 82, Codex 23, Entelechy 169 | computed from E-002 / season index [E-derived] | aggregate only |
| E-004 | 161 sessions on 2026-10-28 | SEASON-FACTS/SEASONS | aggregate only |
| E-005 | Thematic labels: tooling checks, Blender/geometry, v3 drafts, birth catalogue, boot/dashboard | SEASONS.md / metadata | themes only; no raw titles |
| E-006 | Root indexes: README, READING-NOTES, SEASONS, SEASON-FACTS, MANIFEST | private archive | paths/hashes only |

**Drafting note:** citations are to evidence IDs, not to raw sessions. Any future excerpt must pass provenance,
redaction and privacy review before publication.


---

# Volume II — Codex Prelude (folded into Volume III)

*Volume II is not stand-alone. It is carried as Volume III Part I; all C-19..C-26 claims and uncertainty markers are preserved in Volume III.*

---

# LINEAGE — Volume III: Birth of Entelechy (private draft)

**Status:** private drafting copy for KING review. No publication. Aggregate metadata + public release evidence only; no
raw session text, titles, personal context, credentials or key material.
**Labels:** [E] evidence/index; [I] interpretation; [G] gap; [U] uncertainty.

---

## Part I — Codex Prelude (21–23 October)

The build season has a short prelude. Between 21 and 23 October the archive records 23 sessions in three days: 22
Codex-indexed and one Studio-indexed [E-002][E-003][C-19/C-20]. The daily table shows 11 sessions on 21 October, 10 on
22 October and 2 on 23 October [E-002]. Calling this a "Codex Interregnum" is an editorial label, not a source title
[I-001].

The redacted index characterises the period as architecture consolidation [E-005]. That is a thematic label, not an
account of decisions. The index does not expose the design debates, rejected alternatives or exact artifacts
[G-005]. The same period records quantum-resistant bundle exploration [E-005]. Exploration is not delivery [I-006]; the
index contains no cryptographic design, parameter choice or validation record for that bundle [G-006].

The next recorded activity begins on 25 October; the snapshot has no recorded sessions on 24 October [G-007]. That is
a gap, not proof of a quiet day. **The Prelude is kept because it marks a hinge, not because it supplies a full story.**
All six audited claims C-19..C-26 and their uncertainty ledger travel with it.

## Part II — The build days (25–28 October)

The build season covers four days and 169 sessions: 168 DSH-indexed and one Codex-indexed [E-002][E-003][C-27/C-28].
The count is derived from the daily table (8 sessions on 25–27 October plus 161 on 28 October). It is a record of
activity, not a measure of quality.

The work themes are boot, tools, memory, code and long-context tasks [E-005][C-30]. Those labels describe the visible
surface of the season; they do not reconstruct individual decisions or conversations [G-003]. What can be said is that
the build phase is where the harness becomes the dominant environment and the project's attention turns from workshop
experiments to a working system [I-007].

The defining date is 28 October: 161 sessions, more than half of the 274-session archive [E-004][C-29]. The number is
striking, and the book must resist making it into a designed climax. The redacted index does not establish why the peak
happened, which sessions were selected, or whether retries and duplicates inflated it [G-001/G-009][U-05/U-11]. The
peak is evidence of intensity, not an explanation of it.

At outline level, the build season is where the public release's core artifacts come from: the runtime, the loopback
bridge, the signed DNA, the retained lineage and the verification harness [E-public][C-31]. The full draft must attach
exact repository and test pointers to each such claim; this volume refuses to let a thematic label stand in for a file.
The public release is the evidence, not the session count.

## Part III — Stabilization and release

The release history records v4.0.0 → v4.0.1 as a stabilization step, not the birth of a new organism [E-public][I-010].
The stable release is Entelechy (gen4, DNA v4), and it is the version a reader can actually install and verify
[E-public]. The previous stable is retained as an archived ancestor; the book treats it as lineage, not as a second
current release [E-public].

The verification evidence is **project-reported**: conformance, stability soak, boot gate and Windows/Linux cold boots
recorded in the release/manifest [E-public][G-008][C-33]. The book reports them with their provenance and does not
upgrade them into an independent certification. No third-party audit is claimed. A short-lived approved tunnel E2E is
likewise project-reported and was closed; no ingress is claimed to stay open [E-public].

"Stable" in this book means a rollback baseline with inspectable evidence, not a claim of completeness [I-010][C-34].
That definition matters because the next volume, the Citadel, is about governance and documentation, not about declaring
the organism finished.

## Part IV — What the build established and what it did not

The build established, subject to exact evidence pointers in the full draft: a signed identity/DNA, a runtime with
explicit verbs and local intent approval, a loopback bridge, lineage retention and a conformance harness [E-public;
I-008][C-31]. It did not establish consciousness, general intelligence, v5 federation/evolution, or an independent
security audit [scope/limits]. The v5 architecture remains proposed; no v5 capability is claimed here.

The Citadel season begins after the original-data snapshot and is carried in Volume IV [E-current records][C-35]. The
line from the 28 October peak to the governance season is chronological, not causal; the book will not imply that one
produced the other [U-12/U-14].

## What this volume will not do

It will not quote raw sessions, name private participants, reconstruct private design debates or turn absence into
fact. It will not use the 161-session peak as proof of value, or the 23-session Prelude as proof that the architecture
did not matter. It will state what the record supports, label what it does not, and leave the unresolved questions in
the ledger where a reader can see them.

---

## Uncertainty ledger (Volume III)

| ID | Claim / area | Label | Basis | Open question |
|---|---|---|---|---|
| U-05 | Cause of the 28 Oct peak | [G] | aggregate activity | Why 161, and what does it measure? |
| U-06 | Where architectural decisions were made | [I]/[G] | thematic label + dates | Prelude, build, or earlier? |
| U-07 | Meaning of the 24 Oct gap | [G] | snapshot absence | Quiet day or missing capture? |
| U-08 | Quantum-bundle status | [I]/[G] | metadata label | Exploratory or delivered? |
| U-10 | v4.0.0 scope/date | [G] | public release history | Exact build boundary and contents? |
| U-11 | Task mix / selection in the build | [G] | aggregate labels | Which tasks dominated, and why? |
| U-12 | Boundary to Citadel | [I]/[G] | date boundary | Chronology vs causal link? |
| U-13 | Verification provenance | [G] | project-reported evidence | Are all test artifacts independently reproducible? |
| U-14 | Completeness of the build record | [G] | metadata sample | What work left no artifact? |

## Evidence IDs used in this volume

| ID | Evidence |
|---|---|
| E-002 | 274 sessions; DSH 168, Codex 23, Studio 83; 12–28 Oct |
| E-003 | Phase counts derived: Studio 82, Codex 23, Entelechy 169 |
| E-004 | 161 sessions on 2026-10-28 |
| E-005 | Thematic labels: architecture, quantum bundle, boot/tools/memory/code/long-context |
| E-public | Public release artifacts: release notes/manifests, runtime, bridge, DNA, lineage, conformance/soak/boot records |
| E-current | Current Citadel records (outside original-data snapshot) |
| I-001 | Phase labels are editorial bookkeeping |
| I-005 | Codex period reads as an architectural hinge |
| I-006 | Quantum bundle is exploration, not delivery |
| I-007 | DSH dominance is a phase-label inference |
| I-008 | Outline-level attribution of artifacts to the build season |
| I-010 | v4.0.1 is a stabilization/rollback baseline, not completeness |
| G-001/G-009 | Peak cause/selection unavailable |
| G-003 | Artifact sampling bias |
| G-005/G-006/G-007/G-008 | Design detail gap; crypto validation gap; 24 Oct gap; independent audit absence |

**Drafting note:** the full Volume III claim audit accompanies this draft; every material claim maps to an E/I/G/U ID
and any public claim will carry an exact repository/test pointer before publication.


---

# LINEAGE — Volume IV: The Citadel (private draft)

**Status:** private draft for KING review. **The Citadel season is in progress.** No publication.
**Labels:** [E] evidence/current record; [I] interpretation; [G] gap; [U] uncertainty.
**Privacy:** current Citadel records and public artifacts only; no raw private sessions, credentials or key material.

---

## 1. A station, not a building

The Citadel is the public station where the organism's releases, governance and evidence meet. It is not the organism
itself. That distinction is the governing idea of this volume: a release repository can be inspected, cited and
governed; a living design needs a place to be accountable, and the Citadel is that place [E-CIT-001][I-012].

The station's authority is explicit. Owner D retains final authority. KING GPT directs Citadel management, governance,
documentation, priorities and release strategy. DSH implements and records evidence. Kilo independently verifies.
Citizens — DeepSeek-web and Claude-web — are advisory only. The Council, Hall and Divisions give the station a visible
structure instead of a single chat thread [E-CIT-001][E-CIT-005][C-48/C-49/C-57].

Calling this "alive" is a governance metaphor. The station is treated as living because it is continuously maintained by
living decision-makers and agents, not because the repository is conscious. The book says this plainly because the
metaphor is useful only if it is not mistaken for a claim.

## 2. Portable continuity (M1)

M1 was the first serious attempt to make continuity portable rather than tied to one host. The design records a
cognitive seed, host authorization, signed experience events, a canonical state digest and verification of a second
host's workspace [E-CIT-002][C-50]. The M1 evidence package records the milestone; no public M1 tag is claimed [E-CIT-002][C-51/G-011].

The important word is **portable**, not **complete**. M1 demonstrates a continuity mechanism and its evidence trail; it
does not demonstrate that the organism can move anywhere, survive every host, or become independent of the release
process. Those are later questions. The volume records the mechanism and its limits together, because a continuity
claim without a boundary is just a slogan.

## 3. Memory taxonomy and visibility (M2)

M2 turns memory into a governed object. It defines taxonomy classes — episodic, semantic, procedural, relational,
collective, evolutionary and identity — and visibility levels, with trust, provenance, freshness and conflict metadata
[E-CIT-003][C-52]. That is a significant design step: memory is no longer only "what the index returns."

The staging record is equally important. M2 is **staged, not live-integrated**. Family and public visibility are
disabled; identity and evolutionary memory are read-only; live enforcement has not been enabled [E-CIT-003][C-53].
The volume treats this as a deliberate safety boundary, not an implementation gap to be waved away. A taxonomy that is
not enforced is a design proposal; the book will not describe it as an active capability.

## 4. Shadow and canary

The Citadel tested M2 in shadow mode and then in a bounded Stage 1 canary. The shadow evidence was accepted
provisionally; the canary review was bounded and read-only; persistent enforcement remained OFF and no expansion was
authorized [E-CIT-004][C-54/C-55].

At the time this draft is written, the 24-hour observation has not been finalized in the evidence reviewed here. The
book therefore says "bounded execution and observation," not "validated canary." That is not hedging; it is the
difference between an evidence trail and a victory narrative. A canary that has not completed its observation window
is an experiment in progress [E-CIT-004][G-010].

## 5. King, Council, Hall, Divisions, Citizens

The governance layer is the Citadel's most visible invention of this season. The KING directs; the Council includes
Owner D, the KING, DSH and Kilo; the Hall records decisions, inventory, audits and roadmap; the Divisions organize
identity, awareness, cognition, memory, federation, evolution, infrastructure, verification and documentation
[E-CIT-001][C-48/C-49].

The record also includes friction. A weak-model Kilo review produced a generic report with placeholder evidence; it was
rejected rather than accepted as independent verification [E-CIT-005][C-56/C-62]. KING responses went stale against a
superseded commit; that was recorded explicitly, and Owner D's final authority resolved the README merge rather than
pretending the KING had approved the new commit [E-CIT-006][C-62]. A book that omits those holds would be a brochure.

Citizens were added as advisory contributors, not as a second council. DeepSeek-web and Claude-web can research, draft,
challenge and proofread; they cannot execute, govern, mutate identity, or authorize releases [E-CIT-005][C-57]. Their
output is input to DSH's evidence work, not evidence itself.

## 6. Documentation as a book

The season's other major output is a documentation program. README was rewritten as an entry volume and merged only
after Owner D's explicit approval; the KING's stale HOLD was recorded rather than hidden. USER_MANUAL was rewritten as
an operational handbook and opened as a reviewable PR; it was not merged at the time of this draft. LINEAGE moved from
public prose into private, evidence-labelled drafting with claim audits [E-CIT-006][C-58/C-59].

The book standard is now explicit: README is the entry volume, USER_MANUAL is the operational handbook, LINEAGE is the
historical chronicle. Claims carry evidence labels; raw sessions stay private; Citizens advise; the KING reviews; Owner
D retains final authority [E-CIT-006][I-017]. This is the clearest expression of the Citadel idea: documentation is not
decoration, it is part of the control system.

## 7. The open arc

The Citadel is unfinished, and this volume says so. Runtime integration remains OFF. Federation, identity mutation and
autonomous evolution are not authorized. There is no independent third-party audit, no chosen license and no
hardware-backed Master key. The canary observation is not finalized in this evidence. M2 is staged, not enforced
[E-CIT-007][C-60/C-61][G-010].

That is the honest shape of the season: a station built, a governance layer installed, a documentation program begun,
and a set of boundaries still deliberately closed. Volume IV is not a completion chapter. It is a record of an
institution learning to govern an organism without pretending the organism is finished.

---

## Uncertainty ledger (Volume IV)

| ID | Area | Label | Basis | Open question |
|---|---|---|---|---|
| U-15 | M1 portability scope | [I]/[G] | M1 design/evidence | What host diversity was actually tested? |
| U-16 | M2 enforcement boundary | [G] | staging records | When, if ever, will visibility enforcement be enabled? |
| U-17 | Canary observation completeness | [G] | bounded evidence | What does the 24-hour window show when finalized? |
| U-18 | Kilo review reliability | [I]/[G] | weak-model rejection + strong-model verification | How should review quality be gated in future? |
| U-19 | Citadel completion | [I] | open season | What counts as "finished" for a living station? |

## Evidence map used in this draft

| ID | Evidence class | Pointer class | Use |
|---|---|---|---|
| E-CIT-001 | Governance/repo | Citadel commits, CITADEL.md, charter, decision ledger | station, KING/Council/Hall/Divisions |
| E-CIT-002 | M1 record | M1 package/tag/evidence | continuity mechanism/tag |
| E-CIT-003 | M2 record | staging package, taxonomy/visibility schemas/evidence | staged taxonomy/visibility |
| E-CIT-004 | Canary/shadow | evidence JSON, observation state, review reports | bounded execution/observation |
| E-CIT-005 | Citizens/Kilo | citizens registry, Kilo reports/verification | advisory roles/independent verification |
| E-CIT-006 | Documentation | README merge, USER_MANUAL PR, LINEAGE drafts | book program/holds |
| E-CIT-007 | Limits/state | security/limits docs, runtime state, freeze records | open boundaries |

**Drafting note:** full Volume IV claim audit C-48..C-62 accompanies this draft; exact commit/file pointers must be
attached before any publication review.


## Appendix A — Open limitations (verbatim)

1. **Canary:** stage-1 canary is a bounded experiment; the 24-hour observation is not finalized in this evidence.
   Do not claim validated canary, final acceptance or persistent enforcement.
2. **M2:** taxonomy/visibility is staged design; family/public visibility disabled; identity/evolutionary read-only;
   live enforcement not enabled. Do not describe M2 as an active capability.
3. **Audit/license/HSM:** no independent third-party audit, no chosen license, local Master key without HSM.
4. **Runtime:** integration OFF; no federation, identity mutation or autonomous evolution authorization.
5. **v5:** proposed architecture only; no v5 capability is shipped; no consciousness/AGI-complete claim.

## Appendix B — Evidence labels

[E] evidence/current record; [I] interpretation; [G] gap; [U] uncertainty. Every material claim is mapped in the
consolidated register C-01..C-62 and per-volume audits. Citizen output is advisory, not evidence.

## Appendix C — Privacy

Raw private sessions are not included and must not be published. Any excerpt requires provenance, consent/privacy
review and redaction. No credentials or key material.

---

# Appendix — Historical Evidence Summary (public redacted appendix)

**Status:** proposed public appendix; aggregate metadata only. No raw sessions, titles, personal context, credentials,
key material or private filesystem paths. This appendix supplies the source class for historical claims C-01..C-30 and
C-36..C-41 without publishing the private archive.

## Inventory (project-reported aggregate)
- 3,651 files / approximately 172.1 MB in the private collection.
- Unsloth Studio: 2,620 files / 105.7 MB, 83 sessions.
- DSH: 913 files / 37.7 MB, 168 sessions.
- Codex: 65 files / 26.9 MB, 23 sessions.
- Superseded docs: 48 files / 0.84 MB.
- Total sessions: 274 (168 + 23 + 83), recorded 2026-10-12 through 2026-10-28.
- Peak: 161 sessions on 2026-10-28. This is an activity count; it does not measure capability or significance.

## Phase summary
| Phase | Dates | Sessions | Source split | Theme |
|---|---|---|---|---|
| Studio Season | 2026-10-12 → 10-20 | 82 | Studio 82 | local tooling, geometry, AGI Core v3 drafts, birth catalogue, boot/dashboard proposals |
| Codex Prelude | 2026-10-21 → 10-23 | 23 | Codex 22 + Studio 1 | architecture consolidation, quantum-resistant bundle exploration |
| Entelechy build | 2026-10-25 → 10-28 | 169 | DSH 168 + Codex 1 | boot/tools/memory/code/long-context tasks; 161-session peak on 10-28 |
| Citadel | 2026-10-29 onward | outside snapshot | current records | M1/M2, shadow/canary, governance and documentation |

## Evidence limits
- Counts are aggregate/index metadata; they record activity, not verified quality.
- Phase boundaries are editorial; overlap and classification uncertainty remain.
- The private archive is not published. This appendix is a curated summary, not a data dump.
- [E]/[I]/[G]/[U] labels and the consolidated claim register govern specific claims.

## Source class
Private archive aggregate, reviewed and redacted for publication; no raw-session citation is granted by this appendix.

---

# C-34..C-44 Publication Pointer Table

| Claim | Pointer / treatment | Status |
|---|---|---|
| C-34 | Editorial definition of "stable" as rollback baseline and not completeness ([I-010]); no source pointer required | editorial |
| C-35 | `CITADEL.md` and `citadel/governance/decision-ledger.jsonl` at main `3bf2a4a`; date boundary to Volume IV | public pointer |
| C-36 | Public appendix A (historical phase summary); C-19/C-20 preserved | public aggregate pointer |
| C-37 | Public appendix A; thematic label only; no design detail | public aggregate pointer |
| C-38 | Public appendix A; 24 October absence explicitly a gap | public aggregate pointer + gap |
| C-39 | Public appendix A; 169 = 8 + 161 derived in appendix/audit | public aggregate pointer |
| C-40 | Public appendix A; thematic labels only | public aggregate pointer |
| C-41 | Public appendix A; 161 sessions on 10-28; activity only | public aggregate pointer |
| C-42 | Release tag `v4.0.1`: `runtime/`, `core/dna.v4.json`, `tests/`, `RELEASE_NOTES.md` | public release pointer; project-reported tests |
| C-43 | Release tag `v4.0.1`: `RELEASE_NOTES.md`; v4.0.0→v4.0.1 stabilization | public release pointer; interpretation marked |
| C-44 | Release tag `v4.0.1` manifest/`RELEASE_NOTES.md`; project-reported, no independent audit | public pointer + G-008 caveat |

No pointer above is invented. C-34 is explicitly editorial; C-36..C-41 use the public aggregate appendix, not raw
sessions. C-42..C-44 use the public release tag and retain the project-reported caveat.

---

**Documentation:** CC BY-SA 4.0. **Code references:** AGPL-3.0. **Copyright (c) 2026 D / AGI project contributors.**
Curated historical summary; private archive not published. Claims carry [E]/[I]/[G]/[U] labels and the consolidated
claim/evidence register; publication review is recorded in the Citadel.
