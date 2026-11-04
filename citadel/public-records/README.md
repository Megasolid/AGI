# Public-safe derivatives of historical handoff records

**Status:** proposed public derivatives for review; not replacements for source records.  
**Prepared:** 2026-11-04  
**Source snapshot:** `main` at `5d0f2849995a4dc0deb6324091698022ba189350`.

These documents preserve selected historical project facts while omitting operational and personal metadata that is not needed for public understanding. They are summaries, not byte-for-byte redacted copies and not independent verification of the claims in the source records.

## Derivative index

| Public derivative | Original source |
|---|---|
| [Handoff summary](handoff-20261103-public.md) | [DSH → Claude Code state handoff](https://github.com/Megasolid/AGI/blob/5d0f2849995a4dc0deb6324091698022ba189350/citadel/handoff/DSH-TO-CLAUDE-CODE-STATE-20261103.md) |
| [Season checkpoint summary](season-checkpoint-20261103-public.md) | [Season checkpoint](https://github.com/Megasolid/AGI/blob/5d0f2849995a4dc0deb6324091698022ba189350/citadel/handoff/SEASON-CHECKPOINT-20261103T0415.md) |
| [Station acknowledgement summary](station-ack-20261103-public.md) | [Station acknowledgement JSON](https://github.com/Megasolid/AGI/blob/5d0f2849995a4dc0deb6324091698022ba189350/citadel/handoff/CLAUDE-CODE-STATION-ACK-20261103.json) |
| [Initialization report summary](report-00-initialization-20261102-public.md) | [REPORT-00 initialization](https://github.com/Megasolid/AGI/blob/5d0f2849995a4dc0deb6324091698022ba189350/citadel/inputs/v41e/REPORT-00-station-initialization.md) |
| [Backup runbook summary](backup-runbook-public.md) | [Kilo backup runbook](https://github.com/Megasolid/AGI/blob/5d0f2849995a4dc0deb6324091698022ba189350/citadel/stations/kilo-backup-runbook.md) |

## Redaction policy applied

The derivatives omit:
- workstation usernames, absolute local paths, machine-specific workspace locations, and local filesystem layout;
- session, season, conversation, process, and resume identifiers;
- loopback/private network addresses, ports, gateway URLs, environment-variable names, and control-adapter locations;
- credential-adjacent details, key identifiers, signing-key storage details, and operational access mechanics;
- incidental host diagnostics and local execution metadata that do not affect the public project summary.

The derivatives retain relevant project/version labels, source dates, reported status, limitations, and explicit non-authorization statements. Historical role/station names are retained only when needed to explain what a source record said; their appearance here does not establish current governance roles or authority. Current governance documents and the Owner's decisions remain controlling.

## Important limitations

1. The source records are historical snapshots and contain claims made by their authors. These summaries do not upgrade those claims to independently verified facts.
2. The summaries do not establish that a session, endpoint, credential, service, test result, or release candidate is currently active or valid.
3. Signed originals and their sidecars are intentionally untouched. The existence of a signature sidecar is not a claim that its cryptographic validity has been independently checked.
4. This proposal does not rewrite Git history, delete originals, revoke sessions, rotate credentials, or change release/governance state.
5. Review this PR before merging. If any derivative is inaccurate or too revealing, amend or omit it rather than altering the original record.
