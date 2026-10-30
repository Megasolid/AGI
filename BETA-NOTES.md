# AGI Entelechy beta 5 - release notes

Tag: `v4.0.0-beta.5` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 5
- **Long-lived MCP event stream**: `GET /mcp` (SSE) replays the event log from `Last-Event-ID`, then emits live
  events and heartbeats for a bounded window; intents publish `intent_queued` events (bridge + relay + MCP tool calls).
- **Memory migration** `runtime/agi_migrate.py`: collects MEMORY.md lines + knowledge + docs, dry-run default,
  source read-only (hash checked before/after), target-index only on `--apply`, same-tree target refused.
- **Tunnel readiness planner** `runtime/agi_tunnel.py`: detects cloudflared/tailscale, prints a reviewed plan
  (access policy, token, rotation, local approval), never opens ingress.
- **Conformance matrix extended** to C-beta1..C-beta11 (adds event bus, migration read-only, tunnel plan) -> PASS 12/12.

## Verification
runtime 15/15, beta_2 13/13, beta_3 13/13, beta_4 10/10, beta_5 10/10, proposal 12/12, sensorium 9/9; conformance
PASS 12/12; leak 0; hygiene 0; gate 12/12; Linux cold boot PASS. Windows + Linux both proven.

## Known limits
SSE stream bounded to 6 s per connection (reconnect via Last-Event-ID); migration targets a beta index only;
tunnel is a plan, not an automatic process; no key ceremony yet; no license chosen.
