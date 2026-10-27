# AGI v0.4.0 - three-door login, paper-free admin phrase

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
  still needs the D-touch 2-of-3 shards.
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
