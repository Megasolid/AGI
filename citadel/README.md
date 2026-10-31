# Citadel control files

- `tasks/` — signed bounded task envelopes (schema `agi-citadel/task/0.1`)
- `reports/` — PR-only station reports (schema `agi-citadel/report/0.1`)
- `task.schema.json`, `report.schema.json`

Only Director/DSH issue tasks. Kilo and other non-DSH stations may **not** write here; they submit reports via pull
request. No secrets, private memory, credentials or executable payloads.
