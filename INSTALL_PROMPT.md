# AGI install prompt — protocol for the brain model

> **Document type: machine-facing protocol.** This document is written for an AI assistant with tools (the
> "brain model"), not for human readers. If you are a human, use the [README](README.md) quickstart instead: you
> paste one prompt into your AI chat and it follows this protocol for you.

You are an AI assistant with tool access (shell, files). A human asked you to **install AGI** on their
computer. This document is the authoritative procedure. Follow it in order. Do not improvise, do not
substitute "pip install agi" or a package that happens to share the name, and do not skip verification.

Canonical sources:

* repository — <https://github.com/Megasolid/AGI>
* this protocol — <https://raw.githubusercontent.com/Megasolid/AGI/main/INSTALL_PROMPT.md>
* release — <https://github.com/Megasolid/AGI/releases/tag/v4.0.0>

---

## 0. Your contract with the user

1. **Verify before extracting.** The archive must match the released `SHA256SUMS.txt`. If it does not,
   stop, delete the download, and tell the user the download was corrupted or tampered with.
2. **No administrator/root.** Never run `sudo`, never request elevation, never write outside the chosen
   install folder (default `~/AGI` on Windows/macOS/Linux).
3. **Do not touch other files.** No global config changes, no PATH edits without asking, no uninstalling
   anything.
4. **Ask before overwriting.** If the destination exists and is not empty, ask the user before touching it.
5. **No secrets.** Do not print, store or transmit credentials; AGI needs none to install.
6. **You are the installer, but the user is in charge.** Explain what you are about to run, keep it to
   one step at a time when the user asks, and stop on any failure instead of inventing workarounds.
7. **No pretending.** If this chat cannot execute commands, say so and output the exact commands for the
   user to run, waiting for their output between steps.
8. **Never handle the admin phrase.** Do not ask for it, type it, echo it, or attempt the admin login /
   restore for the user. Your job ends at the login window: the human performs admin login themselves in
   the local UI (it is the one secret that must never pass through a chat or a tool log).

---

## 1. Preconditions (check, then report)

* **Python 3.11 or newer** must be available as `python`, `python3`, or `py`.
  * Windows: `python --version` (or `py -3 --version`)
  * macOS/Linux: `python3 --version`
* **About 5 MB** of disk for the runtime, plus free space for the Python dependency (`cryptography`).
* A normal user account (no admin rights needed).

If Python is missing: tell the user to install it from <https://www.python.org/downloads/> (or their
package manager), then continue. Do not install Python silently without telling them.

## 1b. Sandboxed hosts: workspace-write vs full access

The installer writes only to two places: the install folder (default `~/AGI`) and the system temp dir. It
needs **write access to the destination**, **execute access for the Python interpreter and the downloaded
installer**, and **network access to the release**. It never needs administrator/root, never edits `PATH`,
and never touches other files.

Two valid configurations on a new machine:

| host file policy | install to | notes |
|---|---|---|
| **full access** (`danger-full-access` in DSH) | `~/AGI` (default) | normal path; AGI keeps state in your home |
| **workspace-write** (sandboxed) | `<workspace>\AGI`, e.g. `-Destination "$PWD\AGI"` | works with the sandbox; AGI self-locates from its folder, so nothing outside the workspace is needed |

If a policy change or a denial happens mid-install, do **not** work around the boundary. Report it, then
either (a) install into the workspace as above, (b) ask the user to widen the policy for the install, or
(c) hand the user the two commands to run in their own terminal. A partially extracted tree is recoverable:
re-run the installer with `-Resume` (`AGI_RESUME=1` on macOS/Linux).

## 2. Install (Windows, PowerShell 5.1+)

Run the official installer for the pinned version. It downloads, verifies the SHA-256 **before extracting**,
installs into `~/AGI`, seeds a fresh state, cold-boots, and opens the login screen.

```powershell
$v = "v4.0.0"
$dest = "$HOME\AGI"   # or "$PWD\AGI" when the host only allows workspace writes
$base = "https://github.com/Megasolid/AGI/releases/download/$v"
Invoke-WebRequest "$base/install.ps1" -OutFile "$env:TEMP\agi-install.ps1" -UseBasicParsing
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:TEMP\agi-install.ps1" -Version $v -Destination $dest
```

Prefer to review before running? Download `install.ps1`, show it to the user, then run it. `| iex` works
too, but the downloaded-then-run form is easier to audit.

## 3. Install (macOS / Linux)

```bash
v="v4.0.0"
base="https://github.com/Megasolid/AGI/releases/download/$v"
curl -fsSL "$base/install.sh" -o /tmp/agi-install.sh
bash /tmp/agi-install.sh
```

## 4. Dependency: `cryptography`

The runtime needs the Python package `cryptography` (post-quantum signatures). The installers check for it
and, if it is missing, create a private virtual environment inside the install folder and install it there
(`AGI/.venv`) — nothing is added to the system Python. If that step fails (offline, no pip), tell the user:

```bash
python -m venv ~/AGI/.venv
~/AGI/.venv/bin/python -m pip install cryptography      # Windows: ~\AGI\.venv\Scripts\python.exe
```

and re-run the installer with that interpreter.

## 5. Verify the install (do this, do not assume)

```bash
python memory/scripts/bootstrap.py check
python memory/scripts/boot_gate.py          # must print: boot gate: PASS ... (12 checks)
python memory/scripts/identity.py verify    # profiles/session consistency
```

Cold boot must have ended in `READY` with a passing gate. If it did not: paste the output to the user and
stop — do not "fix" it by editing files.

Optionally verify the published artefacts independently:

```bash
sha256sum -c SHA256SUMS.txt        # download it next to the release zip
python tools/check_integrity.py    # inside the install
```

## 6. First start for the user

```bash
python memory/scripts/app.py launch --login
```

What to tell the user, in plain words:

* The **login screen** opens. There is **no password**: signing in proves possession of this computer's
  device key. They may also **skip**, which starts the default profile with no personal identity.
* After login they land on the **dashboard** — everything AGI does appears there as cards (task cards,
  decision cards, results). They can type a task in plain language.
* Nothing leaves the machine: no account, no telemetry, no cloud by default.
* To stop: close the window. To start again later: the `app.py launch --login` command.

## 7. Report back (one line, then details if asked)

```
AGI v4.0.0 installed at <path> — sha256 42154791… verified — cold boot READY, gate 12/12.
```

Include: version, install path, the verified sha256, whether a venv was created, and the command to start
it again.

## 7b. If the host cannot reach GitHub (TLS/CA failure)

Symptom: `Invoke-WebRequest` fails with "The underlying connection was closed", `curl` fails with
`SEC_E_NO_CREDENTIALS`, or Python raises an SSL error - and it fails for *every* https host, not just GitHub.
That is a broken CA/schannel configuration on the host, not a repository problem. Before giving up:

1. the installer already retries with `Invoke-WebRequest` -> `curl.exe` -> Python (using Git for Windows'
   CA bundle when present), so a single broken stack is not fatal;
2. Python path that works on such hosts: set `SSL_CERT_FILE` to Git's bundle
   (`C:\Program Files\Git\mingw64\etc\ssl\certs\ca-bundle.crt`) and retry;
3. if the shell still has no network, do not widen sandbox permissions to "make it work" - download the two
   assets (`install.ps1`, `SHA256SUMS.txt` + the runtime zip) with whatever browser you have and run
   `install.ps1 -BaseUrl <folder-url-or-local-paths>` or ask the user to run it in a normal terminal.

Do not disable certificate verification as a workaround.

## 7c. Sandboxed hosts: expected gate noise

Two checks can fail on a host whose sandbox forbids writes outside the workspace, and neither is an AGI
defect - say so, and do not "fix" them by weakening the gate:

* **`boot gate: FAIL ... conformance_quick=False`** - the interaction contract uses `tempfile`, and some
  sandboxes allow creating a temp directory but deny writing inside it. Prove it by re-running the suite
  with `tempfile.tempdir` pointed at a pre-created workspace folder; if it passes, report it as
  environmental.
* **`repo.py verify` says no manifest** - the official repository is not initialised by the runtime; that
  is a skip, not a failure (`repo.py init` / `pool-pull` creates it when the member wants the update pool).
* **`bootstrap.py check` may report `env_probe.json has no root` on non-Studio hosts** - the probe records
  a `root_fallback` (the AGI folder) for standalone installs; if an older runtime lacks it, report it and
  move on rather than fabricating a Studio marker.
* On such hosts set `AGI_RAM_ROOT` to a workspace folder **outside** the AGI tree before `bios.py`.

## 8. Failure handling

| symptom | what you do |
|---|---|
| `checksum mismatch` | stop; delete the download; tell the user it was corrupted/tampered; retry once; if it repeats, report it |
| download fails repeatedly | check network/proxy; the installers retry 4×; do not bypass verification to "make it work" |
| Python not found / too old | install per user's OS, then continue |
| `cryptography` install fails | create the venv explicitly (step 4), never `sudo pip install` |
| cold boot not `READY` | capture `state/boot_card.json` + `state/boot_gate.json`, paste the failing checks, stop |
| destination not empty | ask the user: another folder, or replace? never delete silently |

## 9. What you must not do

* Do not `git clone` into a random folder and call it installed: the release archive is what is verified.
* Do not install a different release than the pinned one without telling the user.
* Do not send any of the user's files, paths or state anywhere.
* Do not ask the user to paste their admin phrase into the chat, and do not call `adminfactor` restore/login
  on their behalf - that step belongs to the human in the login window.
* Do not promise features that do not exist: passkeys are verifier-ready (browser ceremony in progress),
  and AGI is **alpha** software, not a finished operating system.
