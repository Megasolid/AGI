# AGI release notes

---
All public pre-stable releases in one place. Each section is the note published with that tag; install instructions always follow the latest release on the releases page.

---

## AGI alpha.stable - dna-GCACGAGGCTGT (genetic release)

2026-10-28 · first genetically identified release · Gen.ID `GCACGAGGCTGT-CACGCATCCTTT-TTTGTGGGTCCC-AATCTGATTATC` · genome 9A30072C · natal interest health

This release replaces version numbers with the DNA identity. Highlights:

* **Genetic release identity** - `dna-GCACGAGGCTGT` is the release tag; `v0.4.3` is legacy history.
* **Signed family & passport** - public family registry (alive+sleeping counts, seats 8/16/32/64, phrase
  promotion, birth ceremony, migration, rough red mode).
* **Measured brain layer** - 120-task objective benchmark through the harness host bridge: VCR 0.983, tier T4,
  cascade routing with confidence escalation.
* **Society foundation** - XP/rank, nightly roll-call (sleep, never auto-kill), Council quorum 17 ballots,
  dormant-now-active mana policy (fairness simulated).
* **Native autonomy** - resident self-continuation, explicit Master-proxy delegation, seeding rehearsal,
  verified rollback drill, executed next-generation seed.
* **Attention/aesthetic gate** - pixel-diff anomaly budget, a11y and reduced-motion, art-direction chromosome,
  and autonomy levels: the director has accepted L3 for attention-passing visual changes, while L4 stays earned
  through a longer evidence streak.
* **Clean-room migration** - signed export/import with fidelity, wired into the seeding path.

Install: use the install prompt/scripts from this tag. The runtime archive is
`agi-runtime-dna-GCACGAGGCTGT.zip` (SHA256SUMS published with the release).

---

## AGI v0.4.3 - guest-install fixes

2026-10-27 · pre-stable test build

A second guest-machine audit confirmed the v0.4.2 archive is clean (no internal tooling, no credentials) and
that a full install can run. It also caught three real defects in the surrounding plumbing, fixed here.

## Fixed

* **installer Python fallback.** On hosts where `Invoke-WebRequest` and `curl.exe` fail (broken schannel/CA),
  the v0.4.2 fallback passed Python code through `-c`; PowerShell 5.1 strips the inner quotes and the child
  dies with `NameError`. The fallback now writes a verbatim helper script and runs it - verified to download
  over TLS on a host whose shell curl/IWR are dead.
* **`app.py launch --login` URL.** The base URL came from the board server as `.../task_live.html`, so the
  login target was `.../task_live.html/login` (404). It now normalises to `scheme://host:port` and opens
  `http://127.0.0.1:8765/login`.
* **`repo.py verify` on a stock install.** No repository is initialised by the runtime; that is now a soft
  skip with a clear message instead of a failure.
* **non-Studio hosts get `root_fallback`** in `env_probe.json` (the AGI folder), so `bootstrap.py check` is
  honest on standalone machines instead of reporting "no root".

## Also in this release

* docs §7c: expected sandbox "gate noise" (tempfile denial, repo skip, root fallback, AGI_RAM_ROOT), and why
  not to weaken the gate to silence it.
* runtime `agi-runtime-v0.4.3.zip`: 152 files, 493,461 B, sha256 `3a66eeb3…`; cold boot READY + gate PASS;
  archive contains no agent pool, no credential files, no backups/logs.

## Install

```powershell
irm https://github.com/Megasolid/AGI/releases/download/v0.4.3/install.ps1 | iex
```
```bash
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v0.4.3/install.sh | bash
```

---

## AGI v0.4.2 - public-runtime cleanup (security review follow-up)

2026-10-27 · pre-stable test build

A guest-machine audit of the v0.4.1 archive found that the public runtime shipped **internal tooling it
should never have contained**. This release removes it and hardens the build so it cannot recur.

## Removed from the public runtime

* the internal **agent pool** (`memory/scripts/agents/`): provider routing config, a browser/CDP bridge and
  provider endpoints - none of it is part of the AGI runtime a member installs;
* **credential files** (`.env`), backups (`.bak`), logs (`.log`) and scratch output (`.out`);
* stale registry entries for those components (the archive's registry is sanitised so the verified-only
  gate still passes).

## Build guards

* `pack_runtime.build()` now **fails** if the assembled archive contains an assigned API key/token, an
  `ms-…`/`sk-…`/GitHub-token pattern, or a private-key block (also: no `.env`, `.bak`, `.log`, `.out`,
  no `agents/`);
* `repo.leak_scan()` gained the same credential patterns, so a leaked key cannot be committed.

## Installer

* download fallback: `Invoke-WebRequest` -> `curl.exe` -> Python (using Git for Windows' CA bundle when the
  host's certificate store is unusable). A host-wide TLS/CA failure no longer fails blind; the error names
  the manual path.
* docs: `SHA256SUMS.txt` is a **release asset**, not a repo file - verification instructions corrected;
  §7b documents the CA-bundle recovery path and forbids disabling certificate verification.

## Action required by the operator

The revoked/leaked third-party key that appeared in earlier archives is the operator's own; it must be
revoked in the provider's console. No member data was ever in a public archive (ciphertext only).

## Install

```powershell
irm https://github.com/Megasolid/AGI/releases/download/v0.4.2/install.ps1 | iex
```
```bash
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v0.4.2/install.sh | bash
```

---

## AGI v0.4.1 - installer hardening (field-test fix)

2026-10-27 · pre-stable test build (not announced)

This patch release fixes the failure seen on the second test machine (D2060) and ships the admin UI work
that landed after v0.4.0.

## Fixed

* **cryptography probe no longer aborts the install.** Under PowerShell 5.1 with
  `$ErrorActionPreference = "Stop"`, the native `import cryptography` stderr became a terminating error, so
  the installer died before creating its private venv - on exactly the machines the venv exists for. The
  probe now runs with local `Continue`, captures all streams and returns a boolean; failures produce a clear
  message plus the venv fallback.
* **`-Resume` (PowerShell) / `AGI_RESUME=1` (bash)** finishes an interrupted install: if the destination
  already contains the extracted runtime (`.agi-runtime-manifest.json`), download/extract are skipped and the
  dependency + bootstrap + cold boot steps run. A non-empty destination without `-Resume` is refused with
  guidance.
* **`-Python` / `AGI_PYTHON` is authoritative** - no silent fallback to another interpreter.
* **venv handling is idempotent** and reports pip failures with the exact retry command.

## Also in the runtime

* admin phrase **rotate** in the browser (current phrase -> new phrase shown once -> publish);
* **temporary session** mode (4 h, no enrolment) with **wipe identity from this machine**;
* admin API (`/api/admin/setup|train|publish|restore|rotate|wipe`) with `X-AGI-UI` guard.

## Install

```powershell
irm https://github.com/Megasolid/AGI/releases/download/v0.4.1/install.ps1 | iex
```
```bash
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v0.4.1/install.sh | bash
```

Interrupted install already extracted? `install.ps1 -Version v0.4.1 -Destination <dir> -Resume`

## Verification

`test_installer_deps.py` reproduces the D2060 condition (a Python without `cryptography`) and requires:
probe returns "missing" instead of aborting, venv created, package installed, cold boot READY, gate PASS,
resume finishes a pre-extracted tree, and a non-empty destination without `-Resume` is refused.

---

## AGI v0.4.0 - three-door login, paper-free admin phrase

2026-10-27

Pre-stable test build (not announced).

## New

* **three-door login** at `/login`: 1 default user (anonymous, no authority); 2 custom user / organization
  (`workspace.py init` interviews the user, classifies the place, proposes policies and task presets);
  3 admin login (enrolled machine: device key; unknown machine: the memorised phrase restores the profile
  and enrols the machine).
* **paper-free admin phrase** (`adminfactor.py`): six words generated once, shown once, never stored;
  the profile snapshot is sealed with PBKDF2-HMAC-SHA256 x600000 + AES-256-GCM and published as ciphertext
  (`recovery/<member>.json`); the phrase doubles as the recovery kit. Login is a session/U1 - root access
  still needs the owner confirmation multi-party key shares.
* **workspaces** (`workspace.py`): not a fixed catalogue - AGI interviews and classifies (personal, office,
  hospital, repair shop, car wash, school, custom), then the user confirms.
* expired sessions are no longer a boot-gate failure (normal TTL).

## Install

```powershell
irm https://github.com/Megasolid/AGI/releases/download/v0.4.0/install.ps1 | iex
```
```bash
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v0.4.0/install.sh | bash
```

After install, the operator mints the admin phrase in their own terminal:
`python memory/scripts/adminfactor.py setup` (shown once), `train`, then `publish --push`.

---

## AGI v0.3.0 - member-neutral public artefacts

2026-10-26

This release does one thing: **the public repository and its release packages now describe only public
facts.** Nothing in a public artefact names, characterises or enumerates private internals.

## What changed

* **Public bundle manifest** - neutral `bundle_id` (`agi-official`), neutral field vocabulary (no
  identity record/identity record/credential blocks), neutral policy text; the manifest still pins the core hashes and the
  generation, so it remains verifiable.
* **Identity template** - the public bundle and release packages ship a neutral identity template instead
  of a template describing the owner's private internals; owner activation is verified by the runtime.
* **Trust summary in packages** - rewritten to state the guarantees (signed content, append-only log,
  local identity, member-neutral artefacts) without naming any private material.
* **Release packages** - neutral package names (`agi-official-<date>`, `agi-custom-<date>`), rebuilt and
  re-signed; no root or device public-key records are distributed.
* **Public runtime archive** - ships code, core and templates only; the internal knowledge record and the
  memory ledger are no longer part of a public download. `agi-runtime-v0.3.0.zip` is 157 files / 477,592 B,
  cold-booted from a fresh extract before publication.
* **Guard in CI and publish** - `leak_scan` now fails on private-internal vocabulary in public prose **and**
  in distributed JSON artefacts; a runtime build fails if its documents/manifests carry such vocabulary.
* **History condensed** - the pre-neutralisation tree is not reachable from this repository any more; the
  public record starts from this release.

## Verification

```bash
python memory/scripts/repo.py verify       # signed manifest + hashes + tag
python memory/scripts/repo.py leak-scan    # public-page/artefact hygiene
python tools/check_integrity.py            # what CI runs
```

## Honest note

This is alpha: the interface is the repository content and the install path, not a stable API. If you
already installed `v0.2.0`, install `v0.3.0` into a fresh folder and copy your state across; the runtime
format is compatible.

---

## AGI.alpha v0.2.0 - portable identity and a one-prompt install

2026-10-26

This release makes AGI **installable in one prompt** and adds the identity layer the system needs to
recognise a user.

## Install (single prompt)

Windows (PowerShell 5.1+), version-pinned and checksum-verified before anything is extracted:

```powershell
$v = "v0.2.0"
irm "https://github.com/Megasolid/AGI/releases/download/$v/install.ps1" | iex
```

macOS / Linux:

```bash
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v0.2.0/install.sh | bash
```

The installer: requires Python 3.11+ (no admin/root), downloads `agi-runtime-v0.2.0.zip`, verifies its
SHA-256 against the released `SHA256SUMS`, extracts to `~/AGI`, seeds the fresh state, runs the cold
boot (BIOS S0-S8, which must reach `READY` with a passing gate), then opens the **desktop login screen**.

Prefer reviewing before running: download `install.ps1` / `install.sh` from the release, read it, then
run it. `| iex` and `| bash` are supply-chain surfaces; pin the version and verify the script hash.

## What is new

* **installable runtime archive** - `agi-runtime-v0.2.0.zip`: core, scripts, models, templates,
  conformance tests, harness; **no state, no keys, no personal data**; verified by cold-booting it from
  a fresh extract before publication.
* **native user authentication** - profiles; login by signing a one-time challenge with the install's
  local device signature (ML-DSA-65); `skip` to a default profile with no authority; time-boxed sessions; a member
  profile bound to a local identity carries member authority.
* **third-party federation** - optional Google (etc.) links stored only as a **keyed hash** of the
  handle, for onboarding and recovery; a federated session is **never** authority and verification
  fails closed if one is active.
* **passkey verification (FIPS-grade presence)** - WebAuthn registration and assertion verification
  (ES256/EdDSA, rpIdHash, user-presence flag, challenge/origin binding, sign-count clone detection).
  The browser ceremony page is the next slice; the verifier is here and tested.
* **desktop login screen + app shell** - `/login` served by the local UI, `app.py launch --login`
  opens it as an app window (Chromium `--app`, browser fallback); the cold-boot sequence is
  `boot -> login -> dashboard`.
* **bootstrap script** - a fresh install has no state by design; `bootstrap.py` seeds the minimum
  (template state, canonical empty ledger, interaction template, machine probe) and is idempotent.

## Verification you can repeat

```bash
python memory/scripts/repo.py verify          # signed manifest, hashes, tags
python tools/check_integrity.py               # CI does exactly this on every push
python memory/scripts/bootstrap.py check
python memory/scripts/passkey.py state
```

## Known limitations (published on purpose)

* passkey **browser ceremony** (credential creation/assertion pages) lands next; today the verifier is
  exercised by tests and can be driven by any WebAuthn client payload.
* authenticator metadata is recorded but **not validated** - documented in `SECURITY.md`.
* identity is per-install today; the portable-D travel model (passkey + travel tokens + home-node
  threshold) is the next research/implementation step.
* license: still **not chosen** (`NOTICE.md`); all rights reserved until a license is added.
