# Kilo Backup Station — Runbook

**Purpose:** let Owner D continue approved AGI work through the Official Kilo Station when DSH is unavailable or out of
tokens. Kilo remains independent and backup-only; it does not gain governance, release, identity or federation authority.

## 1. Trigger and authority
Use this runbook only when:
- DSH is unavailable/out of tokens, or
- Owner D or KING explicitly hands off a task.

Owner D retains final authority. A backup task never authorizes release, merge, identity mutation, federation, runtime
integration or enforcement.

## 2. Station access
- Open **Kilo Desktop** on the local machine; use the isolated workspace `C:\Users\D\AGI\AGI-KILO`.
- Use the GUI session/model shown in Kilo Desktop (currently the NVIDIA Nemotron station model); do not substitute random
  free endpoints for station work.
- No API keys, passwords, private tokens or private archive material are placed in prompts or Kilo workspace.

## 3. Task handoff format
Write a task envelope (JSON/Markdown) with:
- `task_id`, `objective`, `scope`, `constraints`;
- input paths/hashes (public/approved only);
- allowed actions and forbidden actions;
- acceptance checks and evidence format;
- deadline and stop conditions.
Use [backup-handoff-template.json](backup-handoff-template.json).

## 4. Execution
1. Kilo reads the envelope and confirms the scope.
2. Kilo works only inside `AGI-KILO`; no DSH/state/repo writes.
3. Kilo records JSON/evidence under `state/kilo/` and returns a report.
4. Owner/DSH/KING verifies the report; no output is canon automatically.

## 5. Evidence return
Report must include:
- task_id, station=Kilo, decision, findings;
- exact files/hashes inspected/created;
- commands run and whether they were read-only;
- unresolved gaps/uncertainty;
- no secrets/private data.

## 6. Hard limits
- No identity/federation/runtime/release/governance authority.
- No credentials/private archive/personal data.
- No live API-key use beyond an approved task; no network propagation.
- No merge/publication; no direct main push from Kilo.
- Stop on privacy, credential, scope or safety violation; preserve evidence and notify Owner/KING.

## 7. Recovery
When DSH returns, DSH ingests the Kilo report, verifies hashes/evidence, updates the Citadel record, and returns to normal
supervision. Kilo's backup role ends when the handoff is closed.
