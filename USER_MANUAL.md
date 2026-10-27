# AGI user manual

*alpha software — this manual describes what exists today, not what is planned.*

---

## 1. What AGI is

AGI is a personal agent system that runs on **your** computer. It keeps its own state, its own verifiable
history, and its own identity — no account, no cloud, no telemetry. You talk to it in plain language and
watch it work on a dashboard: tasks appear as cards, decisions are requested as cards, results are signed
back as cards.

Three ideas it is built around:

1. **It is yours.** Everything lives in a folder on your machine. Deleting that folder deletes AGI.
2. **It verifies instead of trusting.** Content arrives with signatures and hashes; the runtime checks them
   on boot and refuses contradicting state.
3. **It can grow identity.** You can use it anonymously (default profile), as a named member (your profile
   bound to a local identity), and — as the trust layer matures — with a passkey instead of a password.

---

## 2. First start

After installation (see the README / `INSTALL_PROMPT.md`), start the desktop shell:

```bash
python memory/scripts/app.py launch --login      # Windows: py memory\scripts\app.py launch --login
```

You get a **login screen** served locally at `http://127.0.0.1:8765/login`:

* **Sign in** — proves this computer's device key (there is no password to type or lose).
* **Skip** — starts the **default profile**: fully usable, no personal identity, no authority.
* **Passkey** — verifier is built; the browser ceremony is still in progress (see §8).

Then the **dashboard** opens: <http://127.0.0.1:8765/>.

## 3. The dashboard

| area | what it shows |
|---|---|
| chips (top) | machine facts, current profile + session level, pending decisions |
| cards | one card per live task/subtask: context, steps, status, links |
| Live Task (`/board`) | the active task card, decisions, results |
| System (`/system`) | host facts, capability map, script registry |
| Maintenance (`/maintenance`) | fixed issues and the maintenance ledger |
| Inbox (`/inbox`) | proposals and reports addressed to you |
| Login (`/login`) | session state, profiles, exact commands |

Every card is a plain page you can open; the dashboard is generated from your state, so it is always an
honest projection of what the system knows.

## 4. Giving AGI a task

Write the task as you would to a colleague: what you want, any constraint that matters (do not touch X,
keep it read-only, finish before Y), and how you will judge the result. If a decision is needed, AGI asks
on a card and waits — nothing is assumed on your behalf.

A good request is specific about **the outcome**, not the method. If the task is big, AGI splits it into
steps with a bill (estimate), shows you the plan first, and only then works.

## 5. Logging in and profiles

* `identity.py whoami` — who is signed in, at what level.
* `identity.py login` — sign in as a profile (device-key challenge).
* `identity.py skip` — boot as the default profile.
* `identity.py logout` — end the session.
* `identity.py list` — profiles on this machine.
* `identity.py create --name Alex` — add a member profile; bind a local identity to give it member authority.

Sessions expire (12 h by default). The default profile has **no authority** by design: it can use AGI but
cannot change its identity.

## 6. Updating

* Watch the repository's **Lineage** (`LINEAGE.md`) for new tags.
* Update by installing the new release the same way you installed this one (the installer refuses a
  non-empty destination, so install alongside and copy your state, or use the repo's update path once it
  ships).
* Verify after every update: `python memory/scripts/boot_gate.py` must print `PASS`.

## 7. Privacy and safety

* No account, no telemetry, no outbound connection by default.
* The desktop shell binds to `127.0.0.1` only — it is not reachable from the network.
* The public repository contains releases only: no state and no personal data.
* Back up your install folder if you want to keep your profiles and history: it is just files.

## 8. Known limits (honesty section)

* **alpha** — expect rough edges; the boot gate catches contradictions, not bad design.
* Passkeys: the verifier exists and is tested; browser enrolment (Create passkey / Sign in with passkey
  buttons) is in progress. Until it lands, login is per-install, not portable across machines.
* The travel/portable-D model (passkey + scoped travel tokens + home-node threshold) is designed and
  phased, not finished.
* License not chosen yet: all rights reserved until a license file exists.

## 9. Troubleshooting

| symptom | fix |
|---|---|
| `no device key` on login | `python memory/scripts/crypto.py keygen` then log in again |
| boot gate FAIL | read `state/boot_gate.json`; the failing check names the contradiction |
| port 8765 busy | another AGI UI is already running; open it instead, or stop it (`board_serve.py --stop`) |
| `cryptography` missing | create the venv described in `INSTALL_PROMPT.md` §4 |
| nothing appears on the dashboard | regenerate: `python memory/scripts/dashboards.py` |

## 10. Uninstall

Delete the install folder (default `~/AGI`). Nothing is registered elsewhere — no services, no registry
entries, no scheduled tasks. Your data goes with the folder, which is the point.
