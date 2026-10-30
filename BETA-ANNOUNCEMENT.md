# AGI Entelechy beta 1 is out

*30 October 2026 · fourth generation, `v4.0.0-beta.1`*

AGI's first **LLM-runtime-native** generation is available as a public beta prerelease:
<https://github.com/Megasolid/AGI/releases/tag/v4.0.0-beta.1>

*Update, 30 October 2026: **beta 5 is out** - a replayable MCP event stream (Last-Event-ID + live events),
a read-only memory migration dry-run (source hash verified), and a tunnel readiness/plan helper that never opens
ingress; conformance matrix now C-beta1..C-beta11. <https://github.com/Megasolid/AGI/releases/tag/v4.0.0-beta.5>

*Update, 30 October 2026: **beta 4 is out** - MCP SSE streaming responses, a reported vector backend
(sqlite-vec when present, hash-vector fallback), and a beta conformance matrix (C-beta1..C-beta8) that must PASS
before adoption experiments. <https://github.com/Megasolid/AGI/releases/tag/v4.0.0-beta.4>

*Update, 30 October 2026: **beta 3 is out** - MCP Streamable HTTP transport on the loopback bridge
(JSON-RPC initialize/tools/list/tools/call; remote approval refused by design), and the beta now boots cold on
**Linux** (WSL2 kernel 6.18, Python 3.10) as well as Windows. <https://github.com/Megasolid/AGI/releases/tag/v4.0.0-beta.3>

*Update, 30 October 2026:* **beta 2 is out** - loopback intent bridge with bearer tokens + scopes, an
outbound relay mailbox (no inbound public port), and a fused FTS5 + hash-vector recall leg.
<https://github.com/Megasolid/AGI/releases/tag/v4.0.0-beta.2>

**Stable remains alpha.stable** (`dna-GCACGAGGCTGT`). The beta is separate, opt-in, and never touches or migrates a
stable installation. If you want the proven system, use alpha.stable; if you want to explore where AGI is going, use
the beta.

## What "Entelechy" is

*Entelechy* is the state in which potential becomes actual. That is the design: a frozen, signed **seed** that starts
to grow when an LLM touches it - boot, memory, login, passport, family - with no harness and no host framework.

Beta 1 ships four pieces:

1. **Signed DNA v4** - invariants I1-I9, 14 reactive rules, explicit budgets, and a bridge contract with zero
   inbound ports. The contract is data; the checks are scripts.
2. **A thin runtime** - ten typed verbs (`status, recall, remember, boot, propose_intent, poll_intent,
   approve_intent, fetch, snapshot, evolve_propose`). Reads are direct. Writes are **intents**: they queue, and only
   the Master approves them, once.
3. **A memory index** - one SQLite file with full-text recall (FTS5), provenance and hashes; the vector leg is
   schema-ready. One file instead of hundreds of scattered records.
4. **AGI Sensorium (preview)** - a perception layer, not another dashboard: a typed percept graph with saliences and
   affordances is the truth, WebGL2 is only its projection, and the LLM reads a salience-ranked digest. The new
   interaction idea is an **Intent Field**: you drag a goal, candidate action chains appear, and the chosen subgraph
   becomes an intent.

## What it is not

Beta 1 is **stdio-only**. The outbound relay and remote MCP bridge arrive in beta 2, so `fetch`/`exec` are denied.
There is no destructive migration, no key ceremony, and no marketplace. A chat-only LLM can hold the seed and pass
the passport protocol, but it cannot execute the runtime. The second-OS cold boot (Linux) is still being verified.

## Try it

Download `agi-entelechy-beta1-runtime.zip` and `AGI-ENTL-SEED.md` from the release, then:

```bash
python runtime/agi_runtime.py --root <sandbox> --status
```

Read the honest evidence: `BETA-NOTES.md` in the release, and the birth/conformance records referenced there.
No license has been chosen yet; use at your own risk and treat the beta as a research artifact, not a product.

## Why this matters

AGI survives by being small enough to regrow and rigorous enough to verify itself. Beta 1 is the first generation
built to be carried by an LLM rather than hosted by one machine: one seed, one index, one runtime, one perception
contract - portable, signed, and inspectable.
