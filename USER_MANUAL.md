# AGI Entelechy v4.0.1 — User Manual

**The operational handbook for the stable release.** This manual explains how to install, run, verify, back up and
recover AGI Entelechy v4.0.1. It is a book companion to the README entry volume and the LINEAGE chronicle.

- **Stable release:** v4.0.1, generation Entelechy (gen4, DNA v4).
- **Proposed, not shipped:** the v5 Distributed Cognitive Organism architecture (awareness kernel, memory taxonomy,
  governed federation, evolution engine). Do not infer v5 capabilities from this manual.
- **Governing model:** Owner D has final authority; KING GPT directs Citadel management and documentation; DSH
  implements; Kilo independently verifies. See [CITADEL.md](CITADEL.md).

This is an engineering manual, not a claim of consciousness or general intelligence. The "organism" language is a
design and governance metaphor for persistent software identity and continuity.

## 1. Before you install

- **Supported release:** the pinned **v4.0.1** release assets. Do not install a branch, a cached copy, or an
  assistant-generated approximation.
- **Verification is mandatory:** download from the release page, compare the artifact SHA-256 against
  [SHA256SUMS.txt](https://github.com/Megasolid/AGI/releases/tag/v4.0.1), and stop on mismatch.
- **Platforms:** Windows and Linux cold boots were reported for the stable release; macOS is not claimed as verified.
- **Isolation:** install into a directory you own. Never install over a live state directory or point two releases at
  the same state tree.

## 2. Install and first boot

Use the quickstart in the [README](README.md). After installation, verify the runtime can see the install:

```text
python runtime/agi_runtime.py --root <install> --status
```

Expected evidence includes the Entelechy generation, DNA version 4 and the generation identifier. If the status does
not match, stop and use the release manifest/checksum rather than guessing.

The public install path and the exact release artifacts are recorded in `RELEASE_NOTES.md`, `DNA.md`,
`SHA256SUMS.txt` and the signed manifests. Those machine facts are authoritative; this handbook is guidance.

## 3. The runtime

v4.0.1 exposes ten typed verbs:

```text
status recall remember boot propose_intent poll_intent approve_intent fetch snapshot evolve_propose
```

```text
python runtime/agi_runtime.py --root <install> --status
python runtime/agi_runtime.py --root <install> --serve
python runtime/agi_runtime.py --root <install> --index-vectors
```

Operating rules:
- Reads (`status`, `recall`, `poll_intent`, `evolve_propose` validation) are direct.
- Writes are queued as intents; execute-once approval belongs to the **local Master**. Remote approval is refused.
- `fetch` is queued/denied rather than silently executed. `exec`/`shell` are not part of the stable runtime contract.
- Never automate `approve_intent` from an external process. It is a local Master decision.

## 4. Memory and recall

The stable runtime uses a local SQLite index with:
- FTS5 full-text recall;
- an optional 128-dimensional local **hash-vector** leg (`--index-vectors`), fused with RRF;
- per-item provenance, freshness and trust/sensitivity labels.

The hash-vector is a local hash sketch, not a learned semantic embedding. Do not claim semantic-embedding quality for
it. The reported backend is `hash-vector` (or `sqlite-vec` when available).

Memory classes, visibility enforcement and governed sharing belong to the proposed v5 work; they are not shipped in
v4.0.1. Do not place private credentials, passkeys or recovery material in the public index.

## 5. Seats, Master key and passports

```text
python runtime/agi_master.py --root <install> --ceremony
python runtime/agi_seats.py --root <install> --enroll NAME
python runtime/agi_seats.py --root <install> --challenge NAME
python runtime/agi_seats.py --root <install> --sign NAME NONCE --key <DEVICE_KEY>
python runtime/agi_passport.py --root <install> --issue NAME
python runtime/agi_passport.py --root <install> --verify NAME
python runtime/agi_passport.py --root <install> --audit
```

- Seats are Ed25519 public-key seats; only public keys are stored where supported, with an HMAC fallback when
  `cryptography` is unavailable.
- Passports are Master-signed and bind member, gen_id, DNA hash and seat public key. The signature uses Ed25519, with
  ML-DSA-65 where available.
- Remote passport issuance is disabled by default; enabling it is an explicit local policy decision in
  `state/passport_policy.json`.
- Private keys, passkeys, recovery material and live-only secrets do not belong in Git, Citadel or shared evidence.

## 6. Bridge and MCP

```text
python runtime/agi_bridge.py --root <install> --init-token
python runtime/agi_bridge.py --root <install> --serve --port 8766
```

The stable bridge is **loopback only**:
- `GET /health` reports release liveness metadata for the stable runtime;
- `/status`, intents and MCP calls require scoped bearer tokens;
- `POST /mcp` speaks JSON-RPC (`initialize`, `tools/list`, `tools/call`) over JSON or SSE, with event replay;
- `approve_intent` is always refused remotely;
- tokens are shown once; only hashes are stored.

Remote access requires an explicit Master decision: use a named tunnel with an access policy. Never expose an
unauthenticated public port. The tunnel helper plans; it does not silently open ingress.

## 7. Upgrade, migration, backup and rollback

**Upgrade from a legacy tree** with the migration tool, never by copying a new tree over live state:

```text
python runtime/agi_migrate.py --root <target> --source <legacy> --dry-run
python runtime/agi_migrate.py --root <target> --source <legacy> --snapshot-db <backup> --apply
python runtime/agi_migrate.py --root <target> --restore-db <backup>
```

Rules:
- Dry-run first; verify the source hash is unchanged; target-only writes; refuse same-tree targets.
- Take a snapshot before `--apply`; prove rollback with `--restore-db` before trusting the migration.
- Keep a full timestamped backup outside the install tree and an archived ancestor; the boot gate should verify both.
- Do not delete the previous generation to make a new release look clean.
- If any check fails, stop and restore the snapshot. Do not proceed with a partial migration.

## 8. Verification

```text
python runtime/agi_conformance.py --root <install>   # conformance matrix
python runtime/agi_stability.py --root <install> --runs 5
python runtime/agi_runtime.py --root <install> --status
```

**Project-reported evidence for v4.0.1:** conformance 25/25, a 20-run stability soak, boot gate 13/13, and Windows +
Linux cold boots. These are recorded in the release/manifest; they have **not** been independently audited by a third
party. An approved short-lived tunnel E2E passed and was closed; it is project-reported.

Do not treat a passing local test as a security audit, a license grant, or proof of general intelligence.

## 9. Troubleshooting

| Symptom | First check |
|---|---|
| Status fails or generation is unexpected | Run from the extracted release; verify `DNA.md`, manifest and `SHA256SUMS.txt` |
| Conformance fails | Check install completeness and root path; do not bypass the failing check |
| Bridge status returns 401 | Use the scoped token; health is not a substitute for authenticated status |
| Remote approval appears possible | It must not be; approval is local-only. Stop and report |
| Memory recall is poor | Confirm the index was built and the optional vector leg indexed; hash-vector is not a semantic model |
| Lost key or device | Use the recovery procedure; never copy a key into the repository or a prompt |
| Suspected compromise | Stop the bridge, preserve logs/evidence, restore from a verified backup, report to Owner/KING |

## 10. Trust, limits and support boundaries

Known limits of v4.0.1:
- the Master key is a local file; no HSM is required or shipped;
- no independent third-party audit exists;
- a named tunnel with a production access policy is not shipped;
- no license has been chosen yet;
- v5 federation/evolution are proposed, not released;
- no consciousness claim and no claim that v5 is implemented.

Support boundaries:
- Citadel issues are for governance, documentation and signed tasks; they are not a general chat support channel.
- Kilo is an independent verification station, not an integration authority.
- DSH implements and records evidence; the KING directs; Owner D retains final authority.
- Never send private keys, passkeys, recovery material, private memory or credentials to any station, issue or prompt.

## 11. Documentation map

- [README.md](README.md) — entry volume
- [LINEAGE.md](LINEAGE.md) — historical chronicle
- [CITADEL.md](CITADEL.md) — KING/Council/Hall/Divisions and release policy
- [SECURITY.md](SECURITY.md) — security model and limits
- [NOTICE.md](NOTICE.md), [POLICY.md](POLICY.md) — project notices and policy
- [RELEASE_NOTES.md](RELEASE_NOTES.md) — release history
- [DNA.md](DNA.md) — latest stable DNA in one file
- [llms.txt](llms.txt) — compact machine summary
- [docs/history](docs/history) — archived beta and earlier-phase material

---

**Owner:** D (final authority). **KING:** GPT-web. **Implementation:** DSH. **Independent verification:** Kilo.
