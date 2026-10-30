# AGI Entelechy v4.0.0 (stable)

AGI is a portable agent framework that lives in a folder you own. It carries its own identity (a signed DNA
contract), its own state, verifiable history and a small operating runtime. It is not a chat wrapper: it is the
layer that remembers, verifies, and refuses to pretend.

**One stable version: `v4.0.0`** (generation **Entelechy**, DNA v4, signed at birth on 30 October 2026).
Previous generations are recorded in the lineage; the previous stable, `dna-GCACGAGGCTGT` (gen3.5), is an
archived ancestor, not a second stable.

> **For an LLM or agent that needs the latest stable DNA in one call:**
> fetch <https://raw.githubusercontent.com/Megasolid/AGI/main/DNA.md> (raw Markdown containing the complete signed DNA v4, the gen_id, the verification rules and
> the one-line install prompt). Machine summary: <https://raw.githubusercontent.com/Megasolid/AGI/main/llms.txt>.

## Quickstart

```powershell
# Windows
irm https://github.com/Megasolid/AGI/releases/download/v4.0.0/install.ps1 | iex
```

```bash
# macOS / Linux
curl -fsSL https://github.com/Megasolid/AGI/releases/download/v4.0.0/install.sh | bash
```

Install version `v4.0.0`; verify the download's SHA-256 against `SHA256SUMS.txt` from the release page before
running it. Release page: <https://github.com/Megasolid/AGI/releases/tag/v4.0.0>.

## What is inside this repository

- `core/dna.v4.json` (+ `.sig`) — the signed DNA v4 contract (invariants, reactive rules, budgets).
- `DNA.md` — **one-call machine entrypoint**: the complete latest stable DNA + gen_id + verification rules.
- `llms.txt` — compact machine summary and raw links.
- `runtime/` — the Entelechy runtime (10 verbs, intents, recall, conformance matrix, stability gate, bridge).
- `beta/AGI-ENTL-SEED.md` (+ `.sig`) — the signed compact seed distributed with v4.0.0.
- `releases/` — released runtime packages and `SHA256SUMS`; `bundle/` and `pool/` — official bundle and update pool.
- `docs/history/` — archived beta and earlier-phase material (not current).
- Stable docs: [INSTALL_PROMPT.md](INSTALL_PROMPT.md), [USER_MANUAL.md](USER_MANUAL.md),
  [LINEAGE.md](LINEAGE.md), [RELEASE_NOTES.md](RELEASE_NOTES.md), [SECURITY.md](SECURITY.md),
  [NOTICE.md](NOTICE.md), [POLICY.md](POLICY.md).

## Verified

- Conformance matrix **C-beta1…C-beta24 (25 checks) PASS**; stability soak **20 cold runs × 25/25 → STABLE**.
- Windows and Linux (WSL2, kernel 6.18, Python 3.10) cold boots PASS; boot gate **13/13** (12 checks on the
  gen3.5 ancestor + the Entelechy gate).
- Approved tunnel E2E passed through a short-lived cloudflared quick tunnel (HTTP/2), then ingress was closed and
  the token revoked. No ingress is ever opened automatically.

## Lineage

```
gen3.5  dna-GCACGAGGCTGT  (2026-10-28)  -> archived ancestor (backup + still verified at boot)
   |
   +--> gen4  v4.0.0  AGI Entelechy  (2026-10-30)  -> current stable
```

The full story is in [LINEAGE.md](LINEAGE.md); the machine chain is in
`state/archive/evolution/lineage.json` of a live install. The beta line lives in
[docs/history/beta](docs/history/beta) as history only.

## Security and limits

No secrets are published. The runtime is loopback-only by default; the intent bridge refuses remote approvals and
`fetch`/`exec` are denied. Known limits: local Master key (no HSM), no named tunnel/access policy shipped, no
independent third-party audit, no license chosen yet. See [SECURITY.md](SECURITY.md) and [NOTICE.md](NOTICE.md).

**D** (Director), with AI collaborators under D's direction.
