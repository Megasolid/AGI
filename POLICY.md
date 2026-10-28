# AGI content policy

*One official repository, one long-lived branch, immutable releases — and nothing private, ever.*

This repository is the official home of AGI. It exists so that anyone can read the releases, verify what they
download, and understand how the project is kept. The rules below are short on purpose: they are the things that
would be hard to undo if they were broken.

## One branch of truth

`main` is the only long-lived branch. An official repository with divergent histories is no longer official, so
there are no feature branches and no rewriting of published history (no force-push, no rebasing published work).

## Releases are immutable tags

Each release is identified by its **DNA tag** — for this generation, `dna-GCACGAGGCTGT` — with legacy semantic
version tags (`v0.1.0` … `v0.4.3`) kept only as history. A tag is a promise: the bytes it points at never change.

Content is organised by date and class so any past release can be read or cloned:

```
bundle/official/                  the official distributable bundle
pool/                             update pool: signed index and proofs
public/mirror/<tree_size>/        public mirror snapshot at one signed log head
releases/<class>/<date>/          release packages + SHA256SUMS
docs/                             public trust summary and milestone exports
repo.json + .sig                  signed manifest of the whole repository
POLICY.md                         this file
```

## Signed artefacts only

Binaries and bundles enter the repository only through the repository tooling, which verifies the package before
recording its hashes. Mirror snapshots are committed only after verification, and each snapshot stays pinned to
its own signed log head — a proof belongs to one head, never to "the latest".

## Nothing private

No secrets, no private key material, no member data, no personal information. The public repository carries
releases and public projections only.

## Verify before you push

`repo.py verify` must pass before anything is published, and the same checks run at every boot. The CI integrity
job repeats the hash checks on every push and pull request.

## Line endings and hashing

Text is stored with LF line endings, and hashes in `repo.json` and `releases/SHA256SUMS` are computed over
normalised text, so a Windows working tree and a Linux CI clone produce the same values. Binary artefacts are
hashed raw.
