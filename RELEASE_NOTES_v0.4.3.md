# AGI v0.4.3 - guest-install fixes

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
