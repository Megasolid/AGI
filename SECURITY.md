# Security policy

## Reporting

Report a vulnerability privately to the repository owner (GitHub Security Advisory, or the contact in the
profile). Do not open a public issue for an unpatched vulnerability.

## What this repository guarantees

* every artefact is listed with a sha256 in `repo.json` and verified by `tools/check_integrity.py` in CI on
  every push and pull request;
* release packages are listed in `releases/SHA256SUMS` and carry a signed manifest (`RELEASE.json.sig`);
* no secrets, private material or personal data are published - CI fails if identity patterns
  appear in the tree.

## What it does NOT guarantee

* **signature authenticity is verified on your machine**, by the AGI runtime (`repo.py verify`), not by CI:
  CI has no access to the signature implementation and only checks hashes;
* branch protection on this repository is limited by the hosting plan - history is additionally protected by
  local gated pushes and CI, and by the fact that every artefact is hash-pinned in signed manifests.

## Threat model in one line

Trust is not in the host: it is in the signatures and proofs that travel with the content. Verify before you
install: `python memory/scripts/release.py verify <zip>` and `python memory/scripts/repo.py verify`.
