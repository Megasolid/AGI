# The AGI Lineage

### Anatomy of an Artificial Mind

**Stable Edition** · covers generations through **Entelechy v4.0.0** · 30 October 2026

**D**, Director, with AI collaborators under D's direction.

---

## About this edition

This book is the lineage record of AGI: what each generation tried to do, what it kept, what it left behind, and
what is alive now. It was rewritten for the stable **v4.0.0** release so that a single current edition replaces the
earlier beta-era framing. Historical detail stays in git history and in [`docs/history/beta/`](docs/history/beta/).

AGI is a portable agent framework that lives in a folder you own. It carries a signed identity (DNA), its own
state, a verifiable history, and a small operating runtime. The lineage is the point: generations are living
editions that were actually built, installed and verified, not marketing numbers.

## The chain

```
gen1..gen3   early skills and operating-system layers (see git history)
   |
gen3.5       dna-GCACGAGGCTGT   first genetically identified generation   (2026-10-28)
   |                             archived ancestor: backup kept, still verified by the boot gate
   +--> gen4  v4.0.0  Entelechy   current stable                              (2026-10-30)
```

**Only one stable version exists: `v4.0.0`.** The beta line (`v4.0.0-beta.1` … `beta.10`) is preserved as
history in the GitHub prereleases and in [`docs/history/beta/`](docs/history/beta/).

## What each generation was for

| Generation | Identity | What it established |
|---|---|---|
| gen1 | early skill format | a portable, file-based agent habit |
| gen2 | layered skill | state, gates, manifests, self-checks |
| gen3 | AGI Core v3 | boot contract, verified-only gates, DNA root, family/passport |
| gen3.5 | `dna-GCACGAGGCTGT` | first genetic identity: passport, family, society, mana, public release, trust layer |
| gen4 | `v4.0.0` Entelechy | LLM-runtime-native: DNA v4, MCP runtime and bridge, seats, Master ceremony, post-quantum dual signing, conformance matrix, stability soak |

## Generation 4 — Entelechy

Entelechy is the first generation written for a large language model as the runtime. Its contract is data, not
logic: a signed DNA v4 with invariants I1–I9, 14 reactive rules and budgets. Around it sit:

- a thin **MCP-shaped runtime** (10 verbs; intents with execute-once Master approval; denied fetch/exec);
- one SQLite memory index with FTS5 recall fused with a vector leg via RRF;
- a loopback **intent bridge** with scoped bearer tokens, MCP JSON/SSE transports, a replayable event stream, and
  an outbound relay;
- **Ed25519 device seats**, a **Master ceremony** with Ed25519 + ML-DSA-65 dual signing, **Master-signed passports**
  bound to gen_id + DNA sha + seat key, an append-only issuance audit, and a policy gate for remote issuance;
- a **conformance matrix** (C-beta1…C-beta24, 25 checks) and a **stability gate** (cold-run soak).

The beta line grew in public: beta 1 (runtime + recall), beta 2 (bridge + vector), beta 3 (MCP + Linux cold boot),
beta 4 (SSE + conformance), beta 5 (event stream + migration + tunnel plan), beta 6 (seats + unbounded stream),
beta 7 (ed25519 seats + Master + rollback), beta 8 (remote enrollment + passports), beta 9 (ML-DSA + policy +
stability), beta 10 (audit + dual-signed release artifacts). It was promoted to stable `v4.0.0` after a **20-run
soak** (25/25 each) and Windows + Linux cold boots.

## What was verified for v4.0.0

- **Conformance**: 25/25 checks PASS on a cold copy.
- **Stability**: 20 cold runs × 25/25 → STABLE.
- **Boot gate**: 13/13 — the 12 gen3.5 checks still pass, plus the Entelechy gate (`state/entelechy/gate.json`).
- **Linux**: WSL2 kernel 6.18, Python 3.10: Entelechy boots, 1,938-item migrated index, fused recall.
- **Migration**: live memory normalized into the Entelechy index (1,938 items, vector leg built) after a full
  timestamped backup; the source tree was verified unchanged; rollback proof recorded.
- **Tunnel E2E** (explicitly approved): a short-lived cloudflared quick tunnel (HTTP/2) reached the loopback bridge;
  `/health`, token-gated `/status`, MCP initialize/tools/status passed; ingress was closed and the token revoked.

## What it honestly is not

- The Master key is a local file, not an HSM; there is no multi-device key yet.
- No production tunnel/access policy is shipped; exposure is a Master decision and is never automatic.
- No independent third-party security audit; the license is not chosen yet.
- The beta artifacts remain online as prereleases for the record, but they are not a second stable.

## Machine appendix

```yaml
schema: agi-lineage/1
current_stable: v4.0.0
stable_gen_id: ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT
dna_canonical_sha256: 39dd5592f5f0d2573bc7529e206d679767d70c49d4bdfc0ef7aa5236117954c8
generations:
  - {id: gen3.5, tag: dna-GCACGAGGCTGT, period: "2026-10-28", status: ancestor, parent: gen3,
     delta: [dna-identity, passport-and-family, society-and-mana, public-genetic-release]}
  - {id: v4.0.0, tag: v4.0.0, period: "2026-10-30", status: released, parent: dna-GCACGAGGCTGT,
     delta: [entelechy-gen4, dna-v4, mcp-runtime, intent-bridge, mcp-transports, ed25519-seats,
             master-ceremony, mldsa-dual-signing, master-signed-passports, conformance-25,
             stability-soak-20, linux-cold-boot, tunnel-e2e-approved]}
verification:
  boot_gate: memory/scripts/boot_gate.py (13 checks)
  conformance: runtime/agi_conformance.py (C-beta1..C-beta24 = 25 checks)
  stability: runtime/agi_stability.py
  lineage_record: state/archive/evolution/lineage.json
  public_repo: https://github.com/Megasolid/AGI
evidence_rules:
  - no-claim-without-artifact
  - one-failure-reports-and-stops
  - public-projection-never-carries-private-material
  - human-authority-over-irreversible-actions
weak_spots:
  - {id: master_key, status: local-file-only, mitigation: offline backup; HSM/multi-device planned}
  - {id: ingress, status: manual-approval-only, mitigation: named tunnel + access policy planned}
  - {id: audit, status: not-independently-audited}
  - {id: license, status: not-chosen}
```

---

## Colophon

*The AGI Lineage — Anatomy of an Artificial Mind* is the public edition of the lineage record kept inside a live
AGI install. It was rewritten for the stable v4.0.0 release, with every delivered claim pointing at an artefact, a
gate, a test or a named measurement.

Published at <https://github.com/Megasolid/AGI> with the stable release `v4.0.0` (Entelechy) on 30 October 2026.
