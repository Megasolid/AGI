# Kilo Control Adapter (one-hop)

DSH controls the running Kilo Desktop station by attaching to its local server/session; it does not spawn headless
clones or random API endpoints.

- **Server:** `http://127.0.0.1:4096` (loopback only).
- **Auth:** `KILO_SERVER_PASSWORD` read from the local Kilo process environment at runtime. Never written to repo,
  evidence or logs.
- **Session:** GUI session selected by title (`Initialize isolated AGI-KILO workspace`) or explicit session id.
- **Model:** GUI model (NVIDIA Nemotron 3.5 Super VL Instant; `kilo/nvidia/nemotron-3.5-super-vl:free`).
- **Command shape:** `kilo run --attach http://127.0.0.1:4096 -s <session> -m <model> ...`; no bare `kilo run` without
  `--attach`, no random free-model selection.
- **Evidence:** JSON/text/latency/exit captured; auth and secrets redacted.
- **Constraints:** local only; Kilo GUI must be running; no network exposure; no DSH state modification; timeouts;
  no federation/identity mutation/autonomous evolution.

Independent verification: Kilo must verify session attachment, GUI model identity, scope restriction and secret
redaction before this control path is treated as approved.
