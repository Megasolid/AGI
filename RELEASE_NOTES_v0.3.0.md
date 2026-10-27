# AGI v0.3.0 - member-neutral public artefacts

2026-10-26

This release does one thing: **the public repository and its release packages now describe only public
facts.** Nothing in a public artefact names, characterises or enumerates private internals.

## What changed

* **Public bundle manifest** - neutral `bundle_id` (`agi-official`), neutral field vocabulary (no
  genome/passport/credential blocks), neutral policy text; the manifest still pins the core hashes and the
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
