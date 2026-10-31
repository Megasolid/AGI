# Citadel control files

- `tasks/` — signed bounded task envelopes (schema `agi-citadel/task/0.1`)
- `reports/` — PR-only station reports (schema `agi-citadel/report/0.1`)
- `task.schema.json`, `report.schema.json`

Only Director/DSH issue tasks. Kilo and other non-DSH stations may **not** write here; they submit reports via pull
request. No secrets, private memory, credentials or executable payloads.

## Task versions
`cit-kilo-m2-20261031-01` is **superseded** (canonical hash/pinned input mismatch discovered by Kilo).
Use `tasks/cit-kilo-m2-20261031-02.json`: self-contained canonical task hash + embedded ML-DSA signature, and pinned
inputs under `citadel/inputs/`. Verify by removing `task_hash` and `signature`, canonicalizing the remaining JSON
(sort_keys, separators), checking the SHA-256 and signature. Kilo: do not retry v1.
