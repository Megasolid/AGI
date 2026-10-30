# AGI Entelechy beta 4 - release notes

Tag: `v4.0.0-beta.4` - branch `beta/entelechy` - **public beta prerelease**. Stable gen3.5 `dna-GCACGAGGCTGT` untouched.

## Added in beta 4
- **MCP SSE streaming**: POST /mcp with `Accept: text/event-stream` returns `event: message` + JSON-RPC response;
  GET /mcp with SSE Accept returns a keepalive `event: ping` stream (Mcp-Session-Id set). JSON mode unchanged.
- **Vector backend reporting**: `status.recall_backend` / `index_vectors.backend` report `sqlite-vec` when the
  extension is present, otherwise `hash-vector` (FTS5-only before indexing).
- **Beta conformance matrix** `runtime/agi_conformance.py` (C-beta1..C-beta8): identity, DNA integrity, I1-I9 +
  reactive rules, runtime, FTS5+vector recall, intent safety, Sensorium digest, bridge approval-locality/scopes/
  loopback, and budgets (runtime<=600, bridge<=520, DNA<=200 lines).
- Docs updated; Windows + Linux cold boots remain PASS.

## Verification
test_beta_runtime 15/15, test_beta_2 13/13, test_beta_3 13/13, test_beta_4 10/10, test_beta_proposal 12/12,
test_sensorium 9/9; conformance matrix PASS (8 checks); leak scan 0; hygiene 0; repo verify PASS; gate 12/12.

## Known limits
SSE is response/keepalive streaming, not a long-lived server-push bus; no tunnel helper shipped; no destructive
migration; no key ceremonies; chat seasons remain protocol members; no license chosen.
