# AGI content policy (D, 2026-10-26)

One official repository, **one long-lived branch (`main`)**. No feature branches, no forks of truth:
an official repo with divergent histories is not official. Versions are **immutable git tags**; content
is organised by **versioned directories**, so a member can clone and read any past release.

```
bundle/official/                  the official bundle (the only distributable bundle)
pool/                             update pool: pills from all bundles + signed index + proofs
public/mirror/<tree_size>/        snapshot of the *.public pill mirror at one signed log head
releases/<class>/<YYYY-MM-DD>/    release zips (official, custom) + SHA256SUMS
docs/                             public trust summary / milestone exports
repo.json + .sig                  signed manifest: official bundle, pool head, artifact index
POLICY.md                         this file
```

Rules:
1. `main` is the only branch; history is never rewritten (no force-push, no rebase of published commits).
2. Every release is a tag `release/<YYYY-MM-DD>[-n]` on a commit that contains its zip; the tag is the
   version a member pins.
3. Binaries (zips) are committed only through `repo.py publish-release`, which verifies the package first
   (signature + every hash) and records its sha256 in `releases/SHA256SUMS`.
4. Mirror snapshots are committed through `repo.py snapshot-mirror`, which verifies the mirror first and
   keeps each snapshot at its own tree size (a proof belongs to one head, never to "the latest").
5. Nothing private is ever committed: no secrets, no private material, no personal data.
6. `repo.py verify` must pass before any push; the boot gate repeats the same checks at every boot.

## Line endings and hashing

The repo stores text with LF (`* text=auto eol=lf`). Artefact hashes in `repo.json` and
`releases/SHA256SUMS` are computed over **LF-normalised** bytes, so a Windows working tree
and a Linux CI clone produce the same hashes. Binary artefacts (zips) are hashed raw.
