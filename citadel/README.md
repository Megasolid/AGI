# Citadel repository records

This directory contains project coordination and evidence records associated with the public AGI GitHub repository.

- `tasks/` — signed bounded task-envelope records (schema `agi-citadel/task/0.1`)
- `reports/` — report records submitted through pull requests (schema `agi-citadel/report/0.1`)
- `task.schema.json`, `report.schema.json` — record schemas
- `inputs/` — pinned source inputs, manifests and supporting evidence
- `governance/` — current repository governance documents

No secrets, private memory, credentials or executable payloads belong in these records. A task envelope records a
bounded request; its presence does not itself authorize code execution, publication, identity changes, federation or
deployment. The project owner retains final authority over protected and consequential decisions.

## Task versions

`cit-kilo-m2-20261031-01` is superseded because its canonical hash/pinned-input validation did not match.
The successor record is `tasks/cit-kilo-m2-20261031-02.json`, which contains a canonical task hash and detached
signature material, with pinned inputs under `citadel/inputs/`. Verify by removing `task_hash` and `signature`,
canonicalizing the remaining JSON (sorted keys, compact separators), then checking the SHA-256 and signature.
The superseded record remains in history for provenance.

## Canonical task hash convention (v6+)

`task_hash = sha256(utf8(json.dumps(task excluding task_hash and signature, sort_keys=True, separators=(',',':'), ensure_ascii=False)))`.

Task files use ASCII-only content to avoid encoder ambiguity. Historical task versions and their test/evidence records
remain available as provenance; do not treat old task instructions as current authority.
