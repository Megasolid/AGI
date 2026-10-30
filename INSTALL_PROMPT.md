# AGI install prompt - protocol for the brain model

> **Document type: machine-facing protocol.** This is written for an AI assistant with tools, not for human
> readers. If you are human, use the [README](README.md) quickstart.

You are an AI assistant with tool access. A human asked you to **install AGI** on their computer. Follow this
protocol in order. Do not improvise, do not substitute a pip package that happens to share the name, and do not
skip verification.

## Canonical sources

- Latest stable DNA, in one call: <https://raw.githubusercontent.com/Megasolid/AGI/main/DNA.md>
- Release page for `v4.0.1`: <https://github.com/Megasolid/AGI/releases/tag/v4.0.1>
- This protocol: <https://raw.githubusercontent.com/Megasolid/AGI/main/INSTALL_PROMPT.md>
- User manual: <https://raw.githubusercontent.com/Megasolid/AGI/main/USER_MANUAL.md>

Only one stable version exists: `v4.0.1`. The previous stable `dna-GCACGAGGCTGT` is an archived ancestor; do not
install two "stable" versions side by side.

## Step 0 - read the DNA first

Fetch `DNA.md`. It contains the complete signed DNA v4, the `gen_id` (`ENTL-GGAACTATAAGT-TTGCAGTAAGTC-CCCAAAACATAT-TAGATAGAGAAT`), the canonical digest
(`39dd5592f5f0d2573bc7529e206d679767d70c49d4bdfc0ef7aa5236117954c8`) and the verification rules. If the file is unavailable, stop and report; do not reconstruct DNA
from memory.

## Step 1 - download the stable runtime

Prefer the installer for the host OS:

- Windows: `irm https://github.com/Megasolid/AGI/releases/download/v4.0.1/install.ps1 | iex`
- macOS/Linux: `curl -fsSL https://github.com/Megasolid/AGI/releases/download/v4.0.1/install.sh | bash`

If you need manual control, download from the release page:
`agi-runtime-v4.0.1.zip`, `SHA256SUMS.txt`, `AGI-ENTL-SEED.md`, `DNA.md`, `LINEAGE.md`.

## Step 2 - verify before running

1. Verify the runtime zip against `SHA256SUMS.txt`: `sha256sum -c SHA256SUMS.txt` (or PowerShell
   `Get-FileHash`). Never run an unverified package.
2. Verify the DNA: canonical digest must equal `39dd5592f5f0d2573bc7529e206d679767d70c49d4bdfc0ef7aa5236117954c8` and the signature `core/dna.v4.sig` must verify under
   the published key. Stop on any mismatch.
3. Verify the seed signature over the exact seed bytes (LF-normalised), if the seed is present.

## Step 3 - lay out the install

Unzip into a dedicated folder. Expected layout:

```
runtime/          agi_runtime.py, agi_bridge.py, agi_conformance.py, agi_stability.py, agi_seats.py,
                  agi_master.py, agi_passport.py, agi_policy.py, agi_release.py, agi_migrate.py, agi_tunnel.py
core/             dna.v4.json, dna.v4.sig
beta/             AGI-ENTL-SEED.md, AGI-ENTL-SEED.sig
state/            created by the runtime (index, intents, audit, seats, passports)
```

The runtime is stdlib-first. Ed25519 seats and ML-DSA-65 dual signing need Python `cryptography`; seats fall back
to HMAC without it.

## Step 4 - prove the runtime works

```
python runtime/agi_runtime.py --root . --status
python runtime/agi_runtime.py --root . --index-vectors
```

`--status` must report generation `Entelechy`, `dna_version` 4, the expected `gen_id`, and a non-zero
`index_items`. Recall after indexing must report `fusion=rrf(fts5,hash-vector)`.

## Step 5 - run the conformance gate

```
python runtime/agi_conformance.py --root . --out conformance.json      # expects PASS 25/25
python runtime/agi_stability.py --root . --runs 5 --out stability.json # expects STABLE
```

Do not report success until conformance passes. If anything fails, report the failing check verbatim.

## Step 6 - identity and seats (optional, local)

- `python runtime/agi_master.py --root . --ceremony` creates the local Master key (Ed25519 + ML-DSA-65).
- `python runtime/agi_seats.py --root . --enroll <member>` enrolls a device key (shown once).
- Passports are issued locally (`agi_passport.py --issue`) or remotely only after a local policy enablement;
  remote approval of write intents is refused by design.

## Step 7 - bridge (loopback only)

```
python runtime/agi_bridge.py --root . --init-token
python runtime/agi_bridge.py --root . --serve --port 8766
```

The bridge binds 127.0.0.1. MCP is served on `POST /mcp` (JSON and SSE). Never expose the port publicly unless the
human explicitly approves network exposure and an access policy exists; tunnel helpers only plan, they never open
ingress.

## Step 8 - report honestly

Report: install path, stable tag `v4.0.1`, `gen_id`, DNA digest, runtime status JSON, conformance verdict and the
stability verdict. Do not report READY before the gate passes. Never print or publish key material.
