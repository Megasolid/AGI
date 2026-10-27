# AGI.alpha v0.2.0 - portable identity and a one-prompt install

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
