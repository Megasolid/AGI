# AGI user manual

*Alpha software. This manual describes what exists today, not what is planned.*

---

## 1. What AGI is

AGI is a personal agent system that runs on **your** computer. It keeps its own state, its own verifiable history,
and its own identity — no account, no cloud, no telemetry. You talk to it in plain language and watch it work on a
dashboard: tasks appear as cards, decisions are requested as cards, results are signed back as cards.

Three ideas it is built around:

1. **It is yours.** Everything lives in a folder on your machine. Deleting that folder deletes AGI.
2. **It verifies instead of trusting.** Content arrives with signatures and hashes; the runtime checks them on
   boot and refuses contradicting state.
3. **It can grow identity.** You can use it anonymously (default profile), as a named member with a passport, or
   — as the trust layer matures — with a passkey instead of a phrase.

This release is the first **genetically identified** generation: `v4.0.0`. Version numbers from earlier
releases (`v0.1.0` … `v0.4.3`) are history, not identity.

---

## 2. First start

After installation (see the README / `INSTALL_PROMPT.md`), start the desktop shell:

```bash
python memory/scripts/app.py launch --login      # Windows: py memory\scripts\app.py launch --login
```

You get a **login screen** served locally at `http://127.0.0.1:8765/login`. It has three doors:

* **Default user** — starts the default profile: fully usable, no personal identity, no authority.
* **Custom user / organization** — creates or signs in a named member profile on this machine.
* **Admin** — proves this computer's device key, or restores access with a six-word admin phrase on a new
  machine. The admin phrase is shown once when created and is never stored in readable form; it also seals the
  profile snapshot, so it doubles as the recovery kit. **AGI never asks for it in normal use.**

After login the **dashboard** opens: <http://127.0.0.1:8765/>.

## 3. The dashboard

The dashboard is the operations surface. It is generated from your state, so it is always an honest projection of
what the system knows.

| area | what it shows |
|---|---|
| top bar | live health: boot gate, trust head, pending decisions, release identity |
| Operations & system state | family and admins, society, mana, seeding readiness, curriculum, attention gate, resident, release |
| Surfaces | one click to Family, Society, Mana, Seeding, Curriculum, Attention, Onboarding, Release, Migration, Simulation, Brains, Resident |
| whole-body scan | every instrument with the file it reads from — no invented numbers |
| work / activity | recent work items and the grouped event stream |
| UI playground | the evolving interface concept, compared as real-data iterations |
| Docs | the local document library, including this manual and the lineage book |

A **Master (Gold)** badge appears when you are signed in as the owner; guest views are read-only. Actions that
change the system (promote an admin, run a review, arm the resident loop) are Master-gated and audited.

## 4. Giving AGI a task

Write the task as you would to a colleague: what you want, any constraint that matters (do not touch X, keep it
read-only, finish before Y), and how you will judge the result. If a decision is needed, AGI asks on a card and
waits — nothing is assumed on your behalf.

A good request is specific about **the outcome**, not the method. If the task is big, AGI splits it into steps
with an estimate, shows you the plan first, and only then works.

## 5. Members, family, and roles

AGI can be used anonymously, or as a family of members.

* Every member has a **passport**; the family registry is a signed public projection (counts, seats and roles —
  never private material).
* The owner can **invite a human**: the Master hands them a one-time phrase, and the human redeems it on the
  cold-boot admin door to create their admin passport and profile.
* The owner can **promote an elder to admin** from the Family page: role changes are explicit, confirmable,
  revocable, and recorded in an audit trail.
* Seats are capped (masters, admins, council, hall); permissions are listed per role, so nobody has to guess what
  an admin may do.

## 6. Society and mana

The Society page shows members, experience, ranks, the nightly roll-call, council seats and ballots. A roll-call
puts inactive members to **sleep** — it never deletes anyone.

Mana is a soulbound credit: daily grants, plus extra compensation for members whose model is weaker than the
family median, so capability gaps do not become permanent disadvantage. Mana can be spent on services. Gifting
between members is a policy decision and is **off** in this release; a fairness simulation is available on the
Mana page.

## 7. Knowledge and the natal curriculum

Each generation is seeded with a natal interest — this one is **health**. The curriculum is a small, guarded study
plan (foundations, measurement, prevention, nutrition, mental wellbeing, safety, systems access) with evidence
documents rather than claims. The Curriculum page shows progress and can verify that every evidence document
exists.

## 8. Continuation

AGI can continue some of its own work between your turns through a **resident loop**: a scheduled pulse wakes it,
works the next plan item, and re-arms. It is off unless armed, and disarms on your return. The Resident page shows
its state, cadence, and plan. The owner can arm, disarm, or run a pulse manually.

## 9. Maintenance and updates

* Watch the repository's **releases** and the lineage book for new tags.
* Updates are installed the same way as the first install; the installer refuses a non-empty destination, so
  install alongside and copy your state, or use the repository update path when it ships.
* Verify after every update: `python memory/scripts/boot_gate.py` must print `PASS`.
* The boot gate checks manifest, bundle, signature, trust log, passport, bundles, activation, public artefacts,
  install role and identity — twelve checks in total.

## 10. Privacy and safety

* No account, no telemetry, no outbound connection by default.
* The dashboard binds to `127.0.0.1` only; it is not reachable from the network.
* The public repository contains releases only: no state, no member data, no private key material.
* Back up your install folder if you want to keep profiles and history: it is just files.
* The trust log records events as a transparency log. It is append-only; rewriting it breaks verification.

## 11. Verifying what you have

Inside an install:

```bash
python memory/scripts/boot_gate.py              # twelve boot acceptance checks
python tests/conformance/test_conformance.py    # conformance gates
python memory/scripts/repo.py verify            # signed repository manifest and hashes
python tools/check_integrity.py                 # the CI integrity check
```

If a downloaded package is ever in doubt, compare its SHA-256 with the release page's `SHA256SUMS.txt` before
extracting.

## 12. Known limits (honesty section)

* **Alpha** — expect rough edges; the boot gate catches contradictions, not bad design.
* A real second human has not yet joined this install; society seating is exercised in simulation.
* Passkeys: the verifier exists and is tested; the browser ceremony is still in progress. Until it lands, login
  is per-install, not portably across machines.
* The host brain's long-context capability is measured at 83.3/100 and is mitigated by chunking and verification.
* The attention gate's autonomy is accepted through L4 for attention-passing visual changes; the recommended
  level still rises with the consecutive-review streak.
* A license has not been chosen yet: all rights reserved until a license file is added.

## 13. Troubleshooting

| symptom | fix |
|---|---|
| `no device key` on login | `python memory/scripts/crypto.py keygen`, then log in again |
| boot gate FAIL | read `state/boot_gate.json`; the failing check names the contradiction |
| port 8765 busy | another AGI UI is already running; open it instead, or stop it |
| `cryptography` missing | create the venv described in `INSTALL_PROMPT.md` |
| dashboard looks stale | regenerate the site: `python memory/scripts/sitegen.py` |
| a page appears read-only | you are in a guest session; sign in as Master to act |

## 14. Uninstall

Delete the install folder (default `~/AGI`). Nothing is registered elsewhere — no services, no registry entries, no
scheduled tasks. Your data goes with the folder, which is the point.
