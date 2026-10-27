# AGI v0.4.2 - public-runtime cleanup (security review follow-up)

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
