# DSH → Claude Code Station — Full State Handoff

**Date:** 2026-11-03T03:50+0330
**From:** DSH Manager (Lead station)
**To:** Claude Code Station, season `5fa5166b-7e24-40c1-9397-2a99e1da36cc` (project `C:\Users\D\.agents\skills\agi`)
**Purpose:** bring the Claude Code Station fully up to date so it can act without re-deriving state, and define its role and limits.
**Status of this document:** factual handoff. It is not a release authorization and confers no authority.

---

## 1. What AGI is, right now

AGI Core v4 is a layered, portable agent framework with a signed DNA root and frozen governance layers. The current work is the additive **v4.1-E emergency release**, which must not touch:

- `DNA.md`
- `core/dna.v4.json` / `core/dna.v4.sig`
- `repo.json` / `repo.json.sig`
- `POLICY.md`
- frozen S1–S6 (16 packages, 29 files)

Governance roles:

| Role | Holder | Authority |
|---|---|---|
| Owner | D | Final decisions: protected merges, tagging, publication, activation, identity/authority |
| KING | GPT (web season) | Management and release recommendation; no signing keys |
| DSH | this Lead station | Implementation manager; signs handoffs and gate reports with the device key |
| Kilo | Kilo Station | Independent verifier; **advisory corroboration only** since P7 |
| Claude Code | this station | Implementation/verification support under DSH direction; no authority |
| Gemini | AI Studio Wizard | Prototyping/visualisation advisory only; no endpoint, no write rights |

---

## 2. Repository state (authoritative)

| Item | Value |
|---|---|
| Repo | `C:\Users\D\.agents\skills\agi\state\repo\AGI` |
| Remote | `https://github.com/Megasolid/AGI.git` |
| Branch | `main` |
| Head | `4b91b05` — `v41e: H0 revision 10 - non-vacuous evidence checker with negative controls` |
| Working tree | clean |
| Latest published tag | `v4.0.1` (unchanged; no new tags) |
| Rollback target | `v4.0.1` commit `6a0fb796…`, runtime zip sha256 `85a92254…` |
| Protected diff `v4.0.1..HEAD` | **empty** |
| Candidate | `v4.1-E-rc1` — **UNPUBLISHED / NOT TAGGED / NOT ACTIVATED** |
| RC manifest | `citadel/inputs/v41e/v41e-rc-manifest.json` sha256 `c6f17fe3…` |

Nothing in this session may tag, publish, activate, or edit protected files.

---

## 3. Work completed (chronology)

1. **P0 release governance** — compatibility, rollback plan, signed release-control manifest `141b55c4…`.
2. **P1 E1/E4** — context continuity (`agi_context.py`, `agi_context_adapter.py`) and development handoff (`agi_handoff.py`, `agi_handoff_signing.py`). Kilo `v41e-v-03` PASS.
3. **P2 E2 semantics** — `agi_sem.py`: `agi.sem/0.2` state machine, hard constraints, semantic receipts, independent verifier interface, bounded correction, replay/idempotency, `COMMIT` semantic-only. Kilo `v41e-v-04` PASS.
4. **P3 E2 transport** — JSON Schema subset, authenticated binding, two-endpoint harness. Kilo `v41e-v-05` PASS.
5. **P4 roles/replay/keys** — endpoint roles, durable replay store, key lifecycle metadata, cross-process auth. Kilo `v41e-v-06` PASS.
6. **P5 operator** — service lifecycle, monotonic deny gate, hash-chained journal, lease/epoch, cancellation quiescence, approval bridge. Kilo `v41e-v-07` PASS.
7. **P6 capability + evidence** — metadata-only capability quarantine and activation gate; evidence packet, effect ledger/reconciliation, recovery state machine. Kilo `v41e-v-08` PASS.
8. **P7 release candidate** — integrated smoke (`agi_v41e.py`), RC manifest, dossier. Kilo v09–v14 had **defective metadata** in v12–v14; v14 was corrected by direct DSH intervention and now validates.
9. **M1 succession** — signed continuity handoff M0 (`b667a24c…`), then **M0-CORR-02** (`2bf215e9…`) with blob-anchored baseline v2 (`f14b55ed…`). Station A and pristine-clone Station B both pass; **M1 accepted provisionally by KING**.
10. **GATE-1** — deterministic gate report tool (`agi_gate_report.py`) pinned to head `00e0c0a`, all 7 checks pass, dual-signed. KING accepted.
11. **H0 MCP security contract** — 10 revision rounds. R10 is submitted and **NOT accepted**; R11 is the current gate.

---

## 4. Where H0 stands (the active work)

H0 is a **specification + reference enforcement kernel**, not a server. There is **no MCP server, tunnel, credential or exposure**.

Current artifacts:

- Contract: `citadel/h0/H0-MCP-SECURITY-CONTRACT.md`
- Kernel: `runtime/h0_kernel.py` (sha256 `cd7fc0d5…` at R9; R10 unchanged)
- Audit store: `runtime/h0_audit_store.py` (`ef729729…`)
- Evidence checker: `runtime/h0_evidence.py` (`1b2b80c8…`)
- Revision reports R1–R10 in `citadel/h0/`

KING's R11 requirements (open, verbatim intent):

1. Explicitly parse and measure the **regression suite** (`test_v41e_*.py`, 145 tests) — R10's regex only accepts `name.py` and `real_counts()` only globs `test_h0_contract*.py`, so the regression row is never checked.
2. **Reject a missing total line** — currently a report with no total passes because `total_ok` stays `None`.
3. **Reject duplicate suite rows** instead of silently overwriting in a dict.
4. Negative controls proving each: wrong regression count fails, missing total fails, duplicate row fails.
5. Preserve R1–R10 unchanged; submit R11 additively.

H0 is **not frozen** and **not deployment-ready**.

---

## 5. Test state (executed, not copied)

| Suite | Tests | Result |
|---|---|---|
| `test_h0_contract.py` | 32 | OK |
| `test_h0_contract_v2.py` | 28 | OK |
| `test_h0_contract_v3.py` | 18 | OK |
| `test_h0_contract_v4.py` | 14 | OK |
| `test_h0_contract_v5.py` | 14 | OK |
| `test_h0_contract_v6.py` | 14 | OK |
| `test_h0_contract_v7.py` | 9 | OK |
| `test_h0_contract_v8.py` | 10 | OK |
| `test_h0_contract_v9.py` | 7 | OK |
| `test_h0_contract_v10.py` | 10 | OK |
| `test_v41e_*.py` (regression) | 145 | OK |

Total H0 contract tests: **156**.

Run them with:

```
cd C:\Users\D\.agents\skills\agi\state\repo\AGI
python -m unittest discover -s runtime -p "test_v41e_*.py"
python -m unittest discover -s runtime -p "test_h0_contract*.py"
```

---

## 6. Cryptography and evidence

- Signature envelope: `agi-sig/1`, **ML-DSA-65**, device key `a73eaa5d3c31e009`.
- Verification path A: `memory/scripts/crypto.py` (cryptography library).
- Verification path B: `dilithium-py` in `state/agi5/venv-mldsa2` — independent implementation, 7/7 valid, 7/7 tamper-rejected at last run.
- Standing caveat: path A is a separate code path but the same library family; Kilo cannot verify signature math at all.
- Evidence counts must be mechanically checked with `runtime/h0_evidence.py`; a report that cannot be parsed is a failure, not a pass.

Recent signed artifacts:

| Artifact | sha256 |
|---|---|
| `DSH-CONTINUITY-HANDOFF-20261102T1950.json` | `2bf215e9…` |
| `baseline-hashes-2.json` | `f14b55ed…` |
| `GATE-REPORT-20261102T1815.json` | `13c58082…` |
| H0 R10 report | `0fbc89b3…` |
| H0 R10 test output | `3b831f4f…` |

---

## 7. Kilo Station status

- Session: `ses_e69b81db1ffe7vK7CCaVI2r7PG`, server `127.0.0.1:4096`, model `kilo/nvidia/nemotron-3.5-super-vl:free`.
- Control tool: `C:\Users\D\.agents\skills\agi\tools\kilo_control.py`.
- k03–k11 PASS accepted. k12–k14 carried stale metadata (template reuse). v14 was corrected to task hash `dee05605…`, bundle `48ba1c63…`, 42,582 bytes, 13 manifest files; file sha256 `839afa1c…`; **DSH re-validated: exit 0**.
- Kilo remains **advisory**, never a gate.

---

## 8. Member/channel map (restored 2026-11-03T03:40)

| Member | Channel | State |
|---|---|---|
| KING / GPT | `chatgpt.com` tab, page 26 | **CIRCLE ONLINE** |
| DeepSeek web | `chat.deepseek.com`, page 2 | **CIRCLE ONLINE** |
| Claude web | `claude.ai` chat, page 28 | **CIRCLE ONLINE** |
| Kilo | local server 4096 + `kilo_control.py` | online (401 on `/health` = auth required, expected) |
| Gemini Wizard | AI Studio app tab was page 97 | tab not currently open; advisory only |
| Claude Code | **this session** via FCC gateway 8082 | **CLAUDE STATION ONLINE** |

Channel bug fixed this session: `circle_mcp.find_page()` was matching a raw substring of the URL, so `utm_source=chatgpt.com` on a GitHub tab shadowed the real ChatGPT page. It now parses the hostname and matches exact/subdomain only.

---

## 9. What the Claude Code Station is authorised to do

**Allowed, read-only by default:**
- Read the repository and any file under `C:\Users\D\.agents\skills\agi`.
- Run tests and static checks that do not modify the tree.
- Review code, produce findings, propose patches as diffs/text.
- Reproduce evidence hashes and report discrepancies.

**Allowed with explicit DSH request:**
- Implement additive changes on a disposable feature branch, with tests.
- Produce a handoff or report artifact for DSH to review and sign.

**Not authorised:**
- Editing `DNA.md`, `core/dna.v4.*`, `repo.json*`, `POLICY.md`, or S1–S6.
- Tagging, publishing, activating, enabling federation or live endpoints.
- Creating MCP servers, tunnels, credentials, or token files.
- Merging protected branches or approving its own work as authority.
- Writing to `main` without a DSH-reviewed commit.

**Reporting rule:** label everything `[EXECUTED]`, `[INSPECTED]`, `[SIGNED]`, or `[PLANNED]`. Do not claim a test passed unless it ran. Do not copy counts from a previous report.

---

## 10. Immediate next work

1. **R11** — fix `h0_evidence.py`: parse the regression suite, reject missing total, reject duplicate rows, add the three negative controls, then run the full suite and report.
2. After R11 passes KING review, H0 freeze is still a separate decision.
3. Deployment blockers remain: in-memory replay store, injected verifier with no real ML-DSA wiring, unanchored audit head, in-process rate counters, Python-declared schemas, no fuzzing.
4. Candidate stays unpublished until Owner explicitly authorizes publication.

---

## 11. Honest limitations (do not overstate)

- No production transport, live endpoints, credentials, federation, or execution.
- JSON Schema validation is a supported subset.
- Message auth in tests is mock HMAC; real ML-DSA message auth is not wired in.
- Endpoint isolation is in-process; replay/effect ledgers are local files.
- Same-process tampering cannot be prevented in Python and is not claimed to be.
- Kilo cannot cryptographically verify ML-DSA.
- KING has not independently executed suites or verified signatures; reported results remain submitter-provided evidence.

**Bottom line:** AGI is a verified development foundation, not an operational autonomous system. Keep the publication block.

---

# ADDENDUM A — KING rulings received 2026-11-03T03:44+0330

This addendum closes the three gaps Claude Code flagged when it read revision 1.

## A1. M1 provisional acceptance — the conditions, as recorded by KING

M1 is **provisionally accepted, subject to its evidence anchors**. The conditions recorded:

- **Artifacts and execution:** both stations exit 0 and report all required tests passing (145/145 on the accepted M1 test baseline).
- **Discrepancies:** both station reports record zero unexplained discrepancies; any mismatch or failure must be preserved and investigated, not silently discarded.
- **Signature verification:** both station reports and the required handoff artifacts pass the specified dual-signature verification.
- **Restart/idempotency:** restart verification produces no duplicate effect and does not alter the accepted evidence set.
- **Historical integrity:** the earlier Station B 8/9 failure and intermediate defects remain preserved; the successful result must not overwrite or erase them.
- **Anchors:** the accepted manifest, corrected handoff, and both station reports are identified by exact hashes in the M1 evidence record.
- **Status qualification:** provisional, based on submitted evidence. KING did not independently rerun the tests or verify the signatures and SHA256 values. **Any later evidence mismatch reopens the acceptance claim.**

Exact anchors (copied from canonical evidence records, not reconstructed):

| Item | sha256 |
|---|---|
| baseline manifest v2 | `f14b55ed4ae90a2f33c6340e27e00f63ba5cbec0274b714a310ca9bfcaa96a40` |
| corrected handoff M0-CORR-02 | `2bf215e974e48c8e5ba72ad8ae78e9eb09108723fb1d599f44a44f425793f280` |
| Station A report | `6c8ac2009f1d57118539e9c3f8c4149996fa6048efccb964e8ef67df98ac7cb9` |
| Station B report | `29838e1e68e8b08b0ce1aa466aac4498f45d88e244bd95a60b10b3fb3f8d5564` |

## A2. Kilo v14 — attribution

Kilo's v14 findings file now validates at exit 0 **as reported by DSH**. This has **not** been independently reproduced by a second party. Treat it as **DSH-reported evidence** until someone other than DSH reruns the validator and records the result. Kilo's review content remains advisory; it was never a gate.

## A3. Deployment blockers mapped to concrete surfaces

| Blocker | Concrete location |
|---|---|
| replay store is in-memory | `runtime/h0_kernel.py` → `class ReplayStore` |
| verifier is injected, no real ML-DSA wiring | `Kernel.__init__(verifier=...)`; `runtime/agi_sem_transport.py` |
| audit head not externally anchored | `runtime/h0_audit_store.py` → `watermark()`, `verify_chain()` |
| rate counters in-process | `runtime/h0_kernel.py` → `class RateLimiter` |
| payload schemas Python-declared only | `runtime/h0_kernel.py` → `PAYLOAD_SCHEMAS` |
| no fuzzing / property tests | no property-test suite exists under `runtime/` |
| same-process tampering unpreventable | documented in `H0-CORRECTION-REPORT-R9` and R8-4 |

## A4. Claude Code authorization — KING, bounded R11

**AUTHORIZED: bounded R11 work, additive branch only, under DSH review.**

Scope: fix the three R10 checker defects — (1) regression suite not parsed or measured, (2) missing total line still yields `ok: true`, (3) duplicate suite rows silently overwritten — and add negative controls proving each defect is rejected. Preserve R1–R10 unchanged. Produce a correction report, test output, hashes and a change summary. Offline, existing non-privileged environment.

**Not authorized:** protected-file edits or merges; tags, releases, publication, activation or freeze; MCP exposure, server or tunnel; credentials, signing authority, approval authority or policy changes; self-acceptance or any claim R11 is accepted before review. This authorization is for R11 only and does not authorize any downstream deployment.

**Rights-model clarifications:** DSH is the task-granting operator, not a substitute for the protected owner; read-only is the default and additive branch work needs an explicit scoped DSH request; tool access does not confer decision authority. Worker proposes and produces; DSH supervises; KING reviews; Owner retains final protected authority.

**Disposition:** M1 provisional; H0 R10 not accepted; H0 R11 authorized for bounded additive implementation and testing under DSH review; v4.1-E-rc1 unpublished, untagged, not activated; MCP/deployment not authorized.

