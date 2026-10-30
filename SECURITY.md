# Security policy

**Current release:** `v4.0.0` - AGI Entelechy (gen4, DNA v4), released 30 October 2026. The previous
stable `dna-GCACGAGGCTGT` (gen3.5) is archived as its ancestor.

## Reporting a vulnerability

Report privately to the repository owner (GitHub Security Advisory, or the contact in the GitHub profile). Please
do not open a public issue for an unpatched vulnerability.

## What this repository guarantees

- every artefact is listed with a SHA-256 in `repo.json` and verified by `tools/check_integrity.py` in CI on every
  push and pull request;
- release packages are listed in `releases/SHA256SUMS` and carry a signed manifest (`RELEASE.json.sig`);
- no secrets, private key material, or personal data are published — CI fails if identity patterns appear in the
  tree.

## What it does not guarantee

- **Signature authenticity is verified on your machine**, by the AGI runtime (`repo.py verify`), not by CI: CI
  has no access to the signature implementation and only checks hashes.
- Branch protection on this repository is limited by the hosting plan. History is additionally protected by local
  gated pushes and CI, and by the fact that every artefact is hash-pinned in signed manifests.
- This software has not been through an independent third-party security audit.

## Threat model in one line

Trust is not in the host: it is in the signatures and proofs that travel with the content. Verify before you
install — check the download against the release's `SHA256SUMS.txt`, then run the runtime verifier.

```bash
python memory/scripts/release.py verify <zip>
python memory/scripts/repo.py verify
```
