# AGI Entelechy beta 3 - release notes

Tag: `v4.0.0-beta.3` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 3
- **MCP Streamable HTTP (JSON-response mode)** on the loopback bridge: `POST /mcp` JSON-RPC 2.0
  (`initialize` with `Mcp-Session-Id`, `tools/list` 10 typed tools, `tools/call`, `ping`).
  Remote `approve_intent` is refused (`-32003`): Master approval cannot be delegated over the bridge.
- **Linux second-OS cold boot PASS**: WSL2 kernel 6.18.54.1, Python 3.10.12, isolated cold copy - Entelechy,
  1,874 items, `rrf(fts5,hash-vector)` recall, bridge health/status loopback.
- Tests `test_beta_3` 13/13 (MCP lifecycle, session header, tools, scopes, approval denial, SSE refusal, Linux evidence,
  budget). Existing beta suites re-run green: runtime 15/15, beta_2 13/13, proposal 12/12, sensorium 9/9.
- Tracked `__pycache__` removed from the beta tree; hygiene 0.

## Known limits
- JSON-response MCP only (no SSE streaming); tunnel requires an authenticated relay; `fetch`/`exec` denied.
- No destructive migration; no key ceremonies; no marketplace; chat seasons remain protocol members.
- No license chosen; research artifact.
