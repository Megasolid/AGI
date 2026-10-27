# AGI v0.4.1 - installer hardening (field-test fix)

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
