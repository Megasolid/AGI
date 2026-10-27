# AGI — one prompt, any AI, your machine

**AGI is a personal agent system that lives on your own computer.** You do not install it by hand: you paste
one prompt into any AI chat window (or just paste this repository link), and the assistant you are already
talking to installs it for you — version-pinned, checksum-verified, no administrator rights, no account, no
telemetry.

Status: **alpha, pre-stable test run.** This repository is being prepared, not announced: expect tags
to move and artefacts to be rebuilt until the first stable release.
 One official repository, one signed manifest, one update pool.

---

## For the AI assistant (read this first)

If a human pasted this repository link and asked you to install AGI, **do not improvise**. Follow
[`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) exactly. Your job ends at the login window: **never ask for the
user's admin phrase** and never run the admin login for them. It is pinned to a release, it verifies the download before
extracting, and it never needs administrator/root.

---

## Install prompt

Copy everything inside the block and paste it into your AI chat. Then let the assistant work.

```text
Install AGI (https://github.com/Megasolid/AGI) on this computer for me.

Follow the official protocol at
https://raw.githubusercontent.com/Megasolid/AGI/main/INSTALL_PROMPT.md exactly.

Key rules: install version v0.4.2; verify the download's SHA-256 against SHA256SUMS.txt BEFORE
extracting; no administrator/root; keep everything inside my home directory; do not touch my other
files; if a non-empty folder would be overwritten, ask me first.

If you cannot run commands in this chat, do not pretend - give me the exact commands one step at a
time and wait for my output instead.

When done: open the AGI login window and tell me in one line what you installed (version + sha256).
```

If your assistant has no file access, the same protocol works manually — it is the same installer
(`install.ps1` / `install.sh`) and the same checksums.

---

## User manual

Short version: after install, AGI opens a **login screen**; you can sign in (device-key, no password),
use a passkey, or **skip** and use the default profile. After login you get the **dashboard** — the
desktop surface where every task, card, decision and result of your AGI appears.

Full manual: [`USER_MANUAL.md`](USER_MANUAL.md) — first start, profiles and login, dashboard, giving AGI
a task, maintenance, privacy, updating, uninstalling.

---

## Lineage (public)

[`LINEAGE.md`](LINEAGE.md) is the **official AGI lineage record** — the document behind this repository's
existence. It records what AGI descends from: the DNA root and its invariants, every generation from gen1 to
the live **gen3.5**, the parentage and mutations between them, what was absorbed or retired, the obligations every generation inherits, and the protocol for reproducing the next generation.

It also covers the public era: the trust layer (post-quantum identity, Merkle trust log, member identity, bundle lattice,
owner activation, public mirror, one official repository) and the public releases
`v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.4.0`, `v0.4.1` and `v0.4.2`.

Release artefacts, tags and hashes live on the releases page — the lineage explains why each exists and
what it descends from.

---

## Verify before you trust

```bash
python memory/scripts/repo.py verify      # inside an install: signed manifest, hashes, tags
python tools/check_integrity.py           # the same check CI runs on every push
# downloaded the release zip yourself? verify it against SHA256SUMS.txt *from the release page*:
sha256sum -c SHA256SUMS.txt               # macOS/Linux (SHA256SUMS.txt is a release asset, not a repo file)
Get-FileHash .\agi-runtime-*.zip -Algorithm SHA256   # Windows
```

## License

Not chosen yet — see [`NOTICE.md`](NOTICE.md). All rights reserved until a license is added.
